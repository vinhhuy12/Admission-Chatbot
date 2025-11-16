"""
Prompt templates for RAG chatbot
"""

from typing import List, Dict, Any


def format_context(documents: List[Dict[str, Any]], max_docs: int = 3) -> str:
    """
    Format retrieved documents into context string for LLM
    
    Args:
        documents: List of retrieved documents
        max_docs: Maximum number of documents to include
    
    Returns:
        Formatted context string
    """
    if not documents:
        return "Không có thông tin liên quan."
    
    # Limit number of documents
    max_docs = min(len(documents), max_docs)
    
    context_parts = []
    for i, doc in enumerate(documents[:max_docs], 1):
        # Extract relevant information
        question = doc.get('question', '')
        context = doc.get('context', '')
        extractive_answer = doc.get('extractive_answer', '')
        abstractive_answer = doc.get('abstractive_answer', '')
        article = doc.get('article', '')
        document = doc.get('document', '')
        
        # Format document
        doc_text = f"[Tài liệu {i}]\n"
        
        if article:
            doc_text += f"Điều khoản: {article}\n"
        if document:
            doc_text += f"Văn bản: {document}\n"
        
        doc_text += f"\nCâu hỏi tương tự: {question}\n"
        
        if context:
            doc_text += f"\nNội dung quy định:\n{context}\n"
        
        if extractive_answer:
            doc_text += f"\nTrích xuất: {extractive_answer}\n"
        
        if abstractive_answer:
            doc_text += f"\nTóm tắt: {abstractive_answer}\n"
        
        context_parts.append(doc_text)
    
    return "\n" + "="*80 + "\n".join(context_parts)


def build_user_message(query: str, context: str) -> str:
    """
    Build user message with query and context

    Args:
        query: User's question
        context: Formatted context from documents

    Returns:
        Complete user message
    """
    return f"""Câu hỏi của người dùng: {query}

CONTEXT (Thông tin từ tài liệu tuyển sinh):
{context}

Hãy trả lời câu hỏi dựa trên CONTEXT trên. Nhớ tuân thủ các nguyên tắc đã được hướng dẫn."""

