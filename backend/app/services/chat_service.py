"""
Chat service - Business logic for chat operations
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import uuid

from app.core.instances import get_chatbot_workflow_instance, get_mongodb_instance
from app.config import settings

logger = logging.getLogger(__name__)


def generate_id(prefix: str) -> str:
    """Generate unique ID with prefix"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def get_conversation_history_from_db(conversation_id: str) -> Optional[List[Dict[str, str]]]:
    """
    Get conversation history from MongoDB

    Args:
        conversation_id: Conversation ID

    Returns:
        List of messages in format [{"role": "user", "content": "..."}, ...]
        or None if not found
    """
    try:
        mongo_client = get_mongodb_instance()
        db = mongo_client[settings.MONGODB_DATABASE]
        conversations_collection = db["conversations"]

        # Get conversation with timeout
        conversation = conversations_collection.find_one(
            {"conversation_id": conversation_id},
            max_time_ms=3000  # 3 second timeout
        )

        if conversation and "messages" in conversation:
            # Convert to format expected by workflow
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation["messages"][-6:]  # Last 3 turns (6 messages)
            ]
            logger.info(f"📜 Loaded {len(conversation_history)} messages from history")
            return conversation_history

        return None

    except Exception as e:
        logger.warning(f"⚠️  Failed to load conversation history (timeout or connection error): {e}")
        return None


def process_chat_query(
    query: str,
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process chat query using LangGraph workflow
    
    Args:
        query: User's question
        conversation_id: Optional conversation ID for context
        user_id: Optional user ID
    
    Returns:
        Dictionary with answer, sources, metadata, conversation_id, message_id, timestamp
    """
    logger.info(f"💬 Processing chat query: {query[:50]}...")
    
    # Generate IDs
    conv_id = conversation_id or generate_id("conv")
    message_id = generate_id("msg")
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Get conversation history if conversation_id provided
    conversation_history = None
    if conversation_id:
        logger.info(f"Continuing conversation: {conversation_id}")
        conversation_history = get_conversation_history_from_db(conversation_id)
    else:
        logger.info(f"✨ Starting new conversation: {conv_id}")
    
    # Run workflow (use pre-loaded instance)
    workflow = get_chatbot_workflow_instance()
    result = workflow.run(
        query=query,
        conversation_history=conversation_history
    )

    # Add query, IDs and timestamp
    result["query"] = query
    result["conversation_id"] = conv_id
    result["message_id"] = message_id
    result["timestamp"] = timestamp

    # Save to MongoDB (non-blocking - don't fail if MongoDB is down)
    try:
        save_conversation_to_db(
            conversation_id=conv_id,
            user_id=user_id,
            query=query,
            answer=result["answer"],
            sources=result.get("sources", []),
            metadata=result.get("metadata", {}),
            message_id=message_id,
            timestamp=timestamp
        )
    except Exception as e:
        logger.error(f"❌ Failed to save conversation (non-blocking): {e}")
        # Add warning to metadata but don't fail the request
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"]["save_warning"] = "Conversation not saved to database"

    logger.info(f"✅ Chat query completed: {message_id}")
    return result


def save_conversation_to_db(
    conversation_id: str,
    user_id: Optional[str],
    query: str,
    answer: str,
    sources: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    message_id: str,
    timestamp: str
) -> None:
    """
    Save conversation to MongoDB
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID
        query: User's question
        answer: Generated answer
        sources: Source documents
        metadata: Response metadata
        message_id: Message ID
        timestamp: Timestamp
    """
    try:
        mongo_client = get_mongodb_instance()
        db = mongo_client[settings.MONGODB_DATABASE]
        conversations_collection = db["conversations"]
        
        # Prepare messages
        user_message = {
            "message_id": message_id + "_user",
            "role": "user",
            "content": query,
            "timestamp": timestamp
        }
        
        assistant_message = {
            "message_id": message_id,
            "role": "assistant",
            "content": answer,
            "timestamp": timestamp,
            "sources": sources,
            "metadata": metadata
        }
        
        # Update or create conversation
        conversations_collection.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "user_id": user_id,
                    "updated_at": timestamp
                },
                "$setOnInsert": {
                    "created_at": timestamp
                },
                "$push": {
                    "messages": {
                        "$each": [user_message, assistant_message]
                    }
                }
            },
            upsert=True
        )
        
        logger.info(f"💾 Conversation saved: {conversation_id}")
    
    except Exception as e:
        logger.error(f"❌ Failed to save conversation: {e}")
        # Don't raise - continue even if save fails


def get_conversation_history(conversation_id: str) -> Dict[str, Any]:
    """
    Get full conversation history from MongoDB
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        Dictionary with conversation_id, messages, total_messages
    
    Raises:
        ValueError: If conversation not found
    """
    logger.info(f"📜 Getting conversation history: {conversation_id}")

    mongo_client = get_mongodb_instance()
    db = mongo_client[settings.MONGODB_DATABASE]
    conversations_collection = db["conversations"]
    
    # Get conversation
    conversation = conversations_collection.find_one(
        {"conversation_id": conversation_id}
    )
    
    if not conversation:
        raise ValueError(f"Conversation not found: {conversation_id}")
    
    messages = conversation.get("messages", [])
    
    logger.info(f"✅ Retrieved {len(messages)} messages")
    
    return {
        "conversation_id": conversation_id,
        "messages": messages,
        "total_messages": len(messages)
    }


def get_user_conversations(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of conversations for a user

    Args:
        user_id: Optional user ID filter

    Returns:
        List of conversation summaries
    """
    logger.info(f"📋 Getting conversations for user: {user_id or 'all'}")

    mongo_client = get_mongodb_instance()
    db = mongo_client[settings.MONGODB_DATABASE]
    conversations_collection = db["conversations"]

    # Build query
    query = {}
    if user_id:
        query["user_id"] = user_id

    # Get conversations sorted by updated_at desc
    conversations = conversations_collection.find(query).sort("updated_at", -1).limit(50)

    result = []
    for conv in conversations:
        messages = conv.get("messages", [])
        if not messages:
            continue

        # Get first user message for title
        first_user_msg = next((msg for msg in messages if msg["role"] == "user"), None)
        last_message = messages[-1] if messages else None

        summary = {
            "id": conv["conversation_id"],
            "title": (first_user_msg["content"][:50] + "..." if first_user_msg and len(first_user_msg["content"]) > 50 else first_user_msg["content"]) if first_user_msg else "Cuộc trò chuyện mới",
            "lastMessage": (last_message["content"][:100] + "..." if last_message and len(last_message["content"]) > 100 else last_message["content"]) if last_message else "",
            "timestamp": conv.get("updated_at", conv.get("created_at", "")),
            "messageCount": len(messages),
            "userId": conv.get("user_id")
        }
        result.append(summary)

    logger.info(f"✅ Retrieved {len(result)} conversations")
    return result


def submit_feedback(
    conversation_id: str,
    message_id: str,
    rating: int,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Submit feedback for a message
    
    Args:
        conversation_id: Conversation ID
        message_id: Message ID
        rating: Rating (1-5)
        comment: Optional comment
    
    Returns:
        Dictionary with feedback_id
    """
    logger.info(f"⭐ Submitting feedback: {rating}/5 for {message_id}")

    mongo_client = get_mongodb_instance()
    db = mongo_client[settings.MONGODB_DATABASE]
    feedback_collection = db["feedback"]
    
    # Generate feedback ID
    feedback_id = generate_id("feedback")
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Save feedback
    feedback_doc = {
        "feedback_id": feedback_id,
        "conversation_id": conversation_id,
        "message_id": message_id,
        "rating": rating,
        "comment": comment,
        "timestamp": timestamp
    }
    
    feedback_collection.insert_one(feedback_doc)
    
    logger.info(f"✅ Feedback saved: {feedback_id}")
    
    return {
        "feedback_id": feedback_id,
        "message": "Feedback saved successfully"
    }

