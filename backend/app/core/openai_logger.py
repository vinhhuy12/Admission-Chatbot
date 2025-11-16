"""
OpenAI Request/Response Logger
Logs full context of all OpenAI API calls with detailed information
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

# Create logs directory if not exists
LOGS_DIR = Path(__file__).parent.parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure OpenAI logger
openai_logger = logging.getLogger("openai_chatbot")
openai_logger.setLevel(logging.INFO)

# Create file handler for OpenAI logs
openai_log_file = LOGS_DIR / "openai_chatbot.log"
file_handler = logging.FileHandler(openai_log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create detailed JSON log file handler
json_log_file = LOGS_DIR / "openai_chatbot_detailed.jsonl"
json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
json_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Add handlers
openai_logger.addHandler(file_handler)
openai_logger.addHandler(json_handler)


# Configure RAG context logger
rag_context_logger = logging.getLogger("rag_context")
rag_context_logger.setLevel(logging.INFO)
rag_context_logger.propagate = False # Prevent logs from going to the root logger

# Create file handler for RAG context log
rag_context_log_file = LOGS_DIR / "rag_context.log"
rag_context_handler = logging.FileHandler(rag_context_log_file, encoding='utf-8')
rag_context_handler.setLevel(logging.INFO)

# Create a simple formatter for the RAG context log
rag_formatter = logging.Formatter('%(asctime)s - CONTEXT:\n%(message)s\n' + '-'*80, datefmt='%Y-%m-%d %H:%M:%S')
rag_context_handler.setFormatter(rag_formatter)

# Add handler to the RAG context logger
rag_context_logger.addHandler(rag_context_handler)


class OpenAILogger:
    """Logger for OpenAI API interactions"""

    def __init__(self):
        self.logger = openai_logger
        self.request_count = 0

    def log_request(
        self,
        conversation_id: str,
        user_query: str,
        system_prompt: str,
        context: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log OpenAI request with full context

        Args:
            conversation_id: Unique conversation ID
            user_query: User's question
            system_prompt: System prompt used
            context: Retrieved context documents
            model: OpenAI model name
            temperature: Temperature parameter
            max_tokens: Max tokens parameter
            metadata: Additional metadata

        Returns:
            request_id: Unique request ID
        """
        self.request_count += 1
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.request_count}"

        # Prepare log data
        log_data = {
            "type": "REQUEST",
            "request_id": request_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            "user_query": user_query,
            "system_prompt": system_prompt,
            "context": context,
            "context_count": len(context),
            "metadata": metadata or {}
        }

        # Log to text file
        self.logger.info(f"[REQUEST] {request_id} | Conversation: {conversation_id}")
        self.logger.info(f"  Model: {model}")
        self.logger.info(f"  User Query: {user_query}")
        self.logger.info(f"  System Prompt Length: {len(system_prompt)} chars")
        self.logger.info(f"  Context Documents: {len(context)}")
        self.logger.info(f"  Parameters: temp={temperature}, max_tokens={max_tokens}")

        # Detailed context is no longer logged here. It is now in logs/rag_context.log

        # Log to JSON file
        json_handler.stream.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        json_handler.flush()

        return request_id

    def log_response(
        self,
        request_id: str,
        conversation_id: str,
        response_text: str,
        usage: Dict[str, int],
        response_time: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log OpenAI response with full details

        Args:
            request_id: Request ID from log_request
            conversation_id: Conversation ID
            response_text: Generated response
            usage: Token usage statistics
            response_time: Response time in seconds
            success: Whether request was successful
            error: Error message if failed
            metadata: Additional metadata
        """
        # Prepare log data
        log_data = {
            "type": "RESPONSE",
            "request_id": request_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "response_time_seconds": response_time,
            "response_text": response_text,
            "usage": usage,
            "error": error,
            "metadata": metadata or {}
        }

        # Log to text file
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[RESPONSE] {request_id} | Status: {status}")
        self.logger.info(f"  Response Time: {response_time:.2f}s")

        if success:
            self.logger.info(f"  Response Length: {len(response_text)} chars")
            self.logger.info(f"  Response Preview: {response_text[:200]}...")
            self.logger.info(f"  Token Usage:")
            self.logger.info(f"    - Prompt Tokens: {usage.get('prompt_tokens', 0)}")
            self.logger.info(f"    - Completion Tokens: {usage.get('completion_tokens', 0)}")
            self.logger.info(f"    - Total Tokens: {usage.get('total_tokens', 0)}")
        else:
            self.logger.error(f"  Error: {error}")

        # Log to JSON file
        json_handler.stream.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        json_handler.flush()

    def log_conversation_summary(
        self,
        conversation_id: str,
        total_requests: int,
        total_tokens: int,
        total_cost: float,
        avg_response_time: float
    ):
        """
        Log conversation summary statistics

        Args:
            conversation_id: Conversation ID
            total_requests: Total number of requests
            total_tokens: Total tokens used
            total_cost: Total cost in USD
            avg_response_time: Average response time
        """
        log_data = {
            "type": "CONVERSATION_SUMMARY",
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "total_cost_usd": total_cost,
                "avg_response_time_seconds": avg_response_time
            }
        }

        self.logger.info(f"[SUMMARY] Conversation: {conversation_id}")
        self.logger.info(f"  Total Requests: {total_requests}")
        self.logger.info(f"  Total Tokens: {total_tokens}")
        self.logger.info(f"  Total Cost: ${total_cost:.4f}")
        self.logger.info(f"  Avg Response Time: {avg_response_time:.2f}s")

        # Log to JSON file
        json_handler.stream.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        json_handler.flush()

    def log_error(
        self,
        conversation_id: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log errors during OpenAI interaction

        Args:
            conversation_id: Conversation ID
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace if available
            metadata: Additional metadata
        """
        log_data = {
            "type": "ERROR",
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "metadata": metadata or {}
        }

        self.logger.error(f"[ERROR] Conversation: {conversation_id}")
        self.logger.error(f"  Type: {error_type}")
        self.logger.error(f"  Message: {error_message}")
        if stack_trace:
            self.logger.error(f"  Stack Trace: {stack_trace}")

        # Log to JSON file
        json_handler.stream.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        json_handler.flush()


# Global logger instance
_openai_logger = None

def get_openai_logger() -> OpenAILogger:
    """Get global OpenAI logger instance"""
    global _openai_logger
    if _openai_logger is None:
        _openai_logger = OpenAILogger()
    return _openai_logger


def log_openai_interaction(
    conversation_id: str,
    user_query: str,
    system_prompt: str,
    context: List[Dict[str, Any]],
    model: str,
    temperature: float,
    max_tokens: int,
    response_text: str,
    usage: Dict[str, int],
    response_time: float,
    success: bool = True,
    error: Optional[str] = None
):
    """
    Convenience function to log complete OpenAI interaction

    Args:
        conversation_id: Conversation ID
        user_query: User's question
        system_prompt: System prompt
        context: Retrieved context
        model: Model name
        temperature: Temperature
        max_tokens: Max tokens
        response_text: Response
        usage: Token usage
        response_time: Response time
        success: Success status
        error: Error message
    """
    logger = get_openai_logger()

    # Log request
    request_id = logger.log_request(
        conversation_id=conversation_id,
        user_query=user_query,
        system_prompt=system_prompt,
        context=context,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Log response
    logger.log_response(
        request_id=request_id,
        conversation_id=conversation_id,
        response_text=response_text,
        usage=usage,
        response_time=response_time,
        success=success,
        error=error
    )

