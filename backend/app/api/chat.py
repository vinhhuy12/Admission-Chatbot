"""
Chat API routes and schemas - Combined file for flattened structure
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.services import chat_service

# Setup logging
logger = logging.getLogger(__name__)

# ============================================
# PYDANTIC SCHEMAS
# ============================================

class ChatQueryRequest(BaseModel):
    """Request schema for chat query"""
    query: str = Field(..., min_length=1, max_length=1000, description="User's question")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field(None, description="User ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Điều kiện xét tuyển vào đại học là gì?",
                "conversation_id": "conv_123456",
                "user_id": "user_789"
            }
        }


class FeedbackRequest(BaseModel):
    """Request schema for feedback"""
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=500, description="Optional feedback comment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456",
                "message_id": "msg_789",
                "rating": 5,
                "comment": "Câu trả lời rất hữu ích!"
            }
        }


class SourceDocument(BaseModel):
    """Schema for source document"""
    question: str = Field(..., description="Question from source")
    article: Optional[str] = Field(None, description="Article reference")
    document: Optional[str] = Field(None, description="Document name")
    score: float = Field(..., description="Relevance score")
    reranker_score: Optional[float] = Field(None, description="Reranker score if available")


class ChatMetadata(BaseModel):
    """Schema for chat metadata"""
    num_documents_retrieved: int = Field(..., description="Number of documents retrieved")
    retrieval_method: str = Field(..., description="Retrieval method used")
    reranker_enabled: bool = Field(..., description="Whether reranker was used")
    generation_model: Optional[str] = Field(None, description="LLM model used")
    generation_successful: Optional[bool] = Field(None, description="Whether generation succeeded")
    fallback_used: Optional[bool] = Field(None, description="Whether fallback was used")
    tokens_used: Optional[Dict[str, int]] = Field(None, description="Token usage")
    workflow: str = Field(..., description="Workflow type")


class ChatQueryResponse(BaseModel):
    """Response schema for chat query"""
    success: bool = Field(..., description="Whether request was successful")
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents")
    metadata: ChatMetadata = Field(..., description="Response metadata")
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    timestamp: str = Field(..., description="Response timestamp")


class FeedbackResponse(BaseModel):
    """Response schema for feedback"""
    success: bool = Field(..., description="Whether feedback was saved")
    message: str = Field(..., description="Response message")
    feedback_id: str = Field(..., description="Feedback ID")


class ConversationMessage(BaseModel):
    """Schema for conversation message"""
    message_id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    sources: Optional[List[SourceDocument]] = Field(None, description="Source documents if assistant message")


class ConversationHistoryResponse(BaseModel):
    """Response schema for conversation history"""
    success: bool = Field(..., description="Whether request was successful")
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ConversationMessage] = Field(..., description="Conversation messages")
    total_messages: int = Field(..., description="Total number of messages")


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

# ============================================
# API ROUTES
# ============================================

# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatQueryResponse, status_code=status.HTTP_200_OK)
async def chat_query(request: ChatQueryRequest):
    """
    Process chat query using LangGraph workflow

    Args:
        request: ChatQueryRequest with query and optional conversation_id

    Returns:
        ChatQueryResponse: Generated answer with sources and metadata
    """
    try:
        # Call service function
        result = chat_service.process_chat_query(
            query=request.query,
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )

        # Convert sources to schema
        sources = [
            SourceDocument(
                question=src.get("question", ""),
                article=src.get("article"),
                document=src.get("document"),
                score=src.get("score", 0.0),
                reranker_score=src.get("reranker_score")
            )
            for src in result.get("sources", [])
        ]

        # Convert metadata to schema
        metadata_dict = result.get("metadata", {})
        metadata = ChatMetadata(
            num_documents_retrieved=metadata_dict.get("num_documents_retrieved", 0),
            retrieval_method=metadata_dict.get("retrieval_method", "unknown"),
            reranker_enabled=metadata_dict.get("reranker_enabled", False),
            generation_model=metadata_dict.get("generation_model"),
            generation_successful=metadata_dict.get("generation_successful"),
            fallback_used=metadata_dict.get("fallback_used"),
            tokens_used=metadata_dict.get("tokens_used"),
            workflow=metadata_dict.get("workflow", "langgraph")
        )

        # Build response
        response = ChatQueryResponse(
            success=True,
            query=result["query"],
            answer=result["answer"],
            sources=sources,
            metadata=metadata,
            conversation_id=result["conversation_id"],
            message_id=result["message_id"],
            timestamp=result["timestamp"]
        )

        return response

    except Exception as e:
        logger.error(f"❌ Chat query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/conversations", response_model=dict)
async def get_user_conversations(user_id: str = None):
    """
    Get list of conversations for a user

    Args:
        user_id: Optional user ID filter

    Returns:
        List of conversation summaries
    """
    try:
        # Call service function
        result = chat_service.get_user_conversations(user_id)
        return {"success": True, "conversations": result}

    except Exception as e:
        logger.error(f"❌ Failed to get conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history

    Args:
        conversation_id: Conversation ID

    Returns:
        ConversationHistoryResponse: Conversation messages
    """
    try:
        # Call service function
        result = chat_service.get_conversation_history(conversation_id)

        # Convert messages to schema
        messages = []
        for msg in result["messages"]:
            message = ConversationMessage(
                message_id=msg["message_id"],
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"],
                sources=[SourceDocument(**src) for src in msg.get("sources", [])] if msg["role"] == "assistant" else None
            )
            messages.append(message)

        response = ConversationHistoryResponse(
            success=True,
            conversation_id=result["conversation_id"],
            messages=messages,
            total_messages=result["total_messages"]
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to get conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a message

    Args:
        request: FeedbackRequest with rating and optional comment

    Returns:
        FeedbackResponse: Feedback submission result
    """
    try:
        # Call service function
        result = chat_service.submit_feedback(
            conversation_id=request.conversation_id,
            message_id=request.message_id,
            rating=request.rating,
            comment=request.comment
        )

        response = FeedbackResponse(
            success=True,
            message=result["message"],
            feedback_id=result["feedback_id"]
        )

        return response

    except Exception as e:
        logger.error(f"❌ Failed to save feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save feedback: {str(e)}"
        )
