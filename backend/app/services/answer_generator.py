"""
Answer Generator using OpenAI API
Generates natural language answers based on retrieved contexts
"""

from typing import List, Dict, Any, Optional
import logging
import time
from openai import OpenAI

from app.config import settings
from app.prompts.system_prompts import SYSTEM_PROMPT
from app.prompts.prompt_templates import format_context, build_user_message
from app.core.openai_logger import get_openai_logger, rag_context_logger

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    Generate natural language answers using OpenAI API
    based on retrieved contexts from RAG pipeline
    """

    def __init__(self):
        """Initialize OpenAI client"""
        self.enabled = settings.ANSWER_GENERATION_ENABLED

        if self.enabled:
            if not settings.OPENAI_API_KEY:
                logger.warning("⚠️  OpenAI API key not found. Answer generation disabled.")
                self.enabled = False
                self.client = None
            else:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"✅ Answer Generator initialized with model: {settings.ANSWER_GENERATION_MODEL}")
        else:
            self.client = None
            logger.info("⚠️  Answer generation disabled in settings")

    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string for LLM

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        return format_context(documents, max_docs=settings.ANSWER_MAX_CONTEXT_DOCS)

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format conversation history for OpenAI API

        Args:
            history: List of conversation turns with 'role' and 'content'

        Returns:
            Formatted history for OpenAI messages
        """
        if not history:
            return []

        # Limit history to avoid token overflow
        max_history = min(len(history), settings.MAX_CONVERSATION_HISTORY * 2)  # *2 for user+assistant pairs
        return history[-max_history:]

    def generate_answer(
        self,
        query: str,
        retrieved_contexts: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate natural language answer based on query and retrieved contexts

        Args:
            query: User's question
            retrieved_contexts: List of retrieved documents from RAG
            conversation_history: Optional conversation history for context
            conversation_id: Optional conversation ID for logging

        Returns:
            Dictionary with generated answer and metadata
        """
        # Check if generation is enabled
        if not self.enabled or not self.client:
            logger.warning("Answer generation disabled, falling back to extractive answer")
            return self._fallback_answer(retrieved_contexts)

        # Get OpenAI logger
        openai_logger = get_openai_logger()
        conversation_id = conversation_id or f"conv_{int(time.time())}"

        try:
            # Format context from retrieved documents
            context = self._format_context(retrieved_contexts)
            # Log the formatted RAG context to its dedicated log file
            rag_context_logger.info(context)

            # Build messages for OpenAI API
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            # Add conversation history if provided
            if conversation_history:
                formatted_history = self._format_conversation_history(conversation_history)
                messages.extend(formatted_history)

            # Add current query with context
            user_message = build_user_message(query, context)
            messages.append({"role": "user", "content": user_message})

            # Log API call with FULL details
            logger.info("="*80)
            logger.info("🤖 OPENAI API CALL - FULL PARAMETERS")
            logger.info("="*80)
            logger.info(f"📝 Query: {query}")
            logger.info(f"📊 Model: {settings.ANSWER_GENERATION_MODEL}")
            logger.info(f"🌡️  Temperature: {settings.ANSWER_TEMPERATURE}")
            logger.info(f"📏 Max Tokens: {settings.ANSWER_MAX_TOKENS}")
            logger.info(f"📚 Number of Documents: {len(retrieved_contexts)}")
            logger.info(f"📄 Context Length: {len(context)} characters")
            logger.info(f"\n💬 MESSAGES SENT TO OPENAI:")
            for i, msg in enumerate(messages, 1):
                logger.info(f"\n--- Message {i} ({msg['role']}) ---")
                logger.info(msg['content'][:500] + "..." if len(msg['content']) > 500 else msg['content'])
            logger.info("\n" + "="*80)

            # Prepare context for logging - INCLUDE ALL FIELDS
            context_docs = [
                {
                    "question": doc.get("question", ""),
                    "context": doc.get("context", ""),  # Full context from document
                    "extractive_answer": doc.get("extractive_answer", ""),
                    "abstractive_answer": doc.get("abstractive_answer", ""),
                    "answer": doc.get("answer", ""),  # Generic answer field
                    "score": doc.get("score", 0.0),
                    "reranker_score": doc.get("reranker_score", 0.0),
                    "article": doc.get("article", ""),
                    "document": doc.get("document", "")
                }
                for doc in retrieved_contexts
            ]

            # Log request to OpenAI logger
            request_id = openai_logger.log_request(
                conversation_id=conversation_id,
                user_query=query,
                system_prompt=SYSTEM_PROMPT,
                context=context_docs,
                model=settings.ANSWER_GENERATION_MODEL,
                temperature=settings.ANSWER_TEMPERATURE,
                max_tokens=settings.ANSWER_MAX_TOKENS
            )

            # Start timer
            start_time = time.time()

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.ANSWER_GENERATION_MODEL,
                messages=messages,
                temperature=settings.ANSWER_TEMPERATURE,
                max_tokens=settings.ANSWER_MAX_TOKENS,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            # Calculate response time
            response_time = time.time() - start_time

            # Extract answer
            generated_answer = response.choices[0].message.content.strip()

            # Log success
            logger.info(f"✅ Generated answer: {generated_answer[:100]}...")

            # Prepare usage data
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            # Log response to OpenAI logger
            openai_logger.log_response(
                request_id=request_id,
                conversation_id=conversation_id,
                response_text=generated_answer,
                usage=usage,
                response_time=response_time,
                success=True
            )

            # Return result with metadata
            return {
                "answer": generated_answer,
                "model": settings.ANSWER_GENERATION_MODEL,
                "tokens_used": usage,
                "finish_reason": response.choices[0].finish_reason,
                "num_contexts_used": len(retrieved_contexts),
                "generation_successful": True,
                "fallback_used": False,
                "response_time": response_time
            }

        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}")
            logger.exception(e)

            # Log error to OpenAI logger
            import traceback
            openai_logger.log_error(
                conversation_id=conversation_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )

            # Fallback to extractive answer
            return self._fallback_answer(retrieved_contexts, error=str(e))

    def _fallback_answer(
        self,
        retrieved_contexts: List[Dict[str, Any]],
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fallback to extractive/abstractive answer when generation fails

        Args:
            retrieved_contexts: Retrieved documents
            error: Optional error message

        Returns:
            Fallback answer with metadata
        """
        if not retrieved_contexts:
            return {
                "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn trong cơ sở dữ liệu.",
                "model": "fallback",
                "tokens_used": {"prompt": 0, "completion": 0, "total": 0},
                "finish_reason": "no_context",
                "num_contexts_used": 0,
                "generation_successful": False,
                "fallback_used": True,
                "error": error
            }

        # Use abstractive answer if available, otherwise extractive
        top_doc = retrieved_contexts[0]
        answer = (
            top_doc.get('abstractive_answer') or
            top_doc.get('extractive_answer') or
            "Xin lỗi, tôi không thể tạo câu trả lời cho câu hỏi này."
        )

        # Add source information
        article = top_doc.get('article', '')
        document = top_doc.get('document', '')

        if article or document:
            source_info = "\n\n📚 Nguồn: "
            if article:
                source_info += f"{article}"
            if document:
                source_info += f" - {document}"
            answer += source_info

        return {
            "answer": answer,
            "model": "fallback",
            "tokens_used": {"prompt": 0, "completion": 0, "total": 0},
            "finish_reason": "fallback",
            "num_contexts_used": len(retrieved_contexts),
            "generation_successful": False,
            "fallback_used": True,
            "error": error
        }


# Global answer generator instance
_generator_instance = None


def get_answer_generator() -> AnswerGenerator:
    """Get or create global answer generator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = AnswerGenerator()
    return _generator_instance
