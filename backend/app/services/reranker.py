"""
Reranking module using Cross-Encoder models from Hugging Face
Improves retrieval quality by reranking initial candidates
"""

from typing import List, Dict, Any, Tuple
from sentence_transformers import CrossEncoder
import numpy as np

from app.config import settings


class Reranker:
    """
    Reranker using Cross-Encoder models for better relevance scoring
    """

    def __init__(self, model=None, model_name: str = None):
        """
        Initialize reranker with cross-encoder model

        Args:
            model: Pre-loaded CrossEncoder model (optional)
            model_name: Hugging Face model name (default: from settings)
        """
        self.model_name = model_name or settings.RERANKER_MODEL
        self.enabled = settings.RERANKER_ENABLED

        if model:
            # Use pre-loaded model
            self.model = model
        elif self.enabled:
            print(f"📦 Loading reranker model: {self.model_name}")
            self.model = CrossEncoder(self.model_name, max_length=512)
            print(f"✅ Reranker model loaded")
        else:
            self.model = None
            print("⚠️  Reranker disabled")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on query relevance using cross-encoder
        
        Args:
            query: User query
            documents: List of documents from initial retrieval
            top_n: Number of top documents to return (default: from settings)
        
        Returns:
            Reranked list of documents with updated scores
        """
        if not self.enabled or not documents:
            return documents[:top_n] if top_n else documents
        
        top_n = top_n or settings.RERANKER_TOP_N
        
        # Prepare query-document pairs for cross-encoder
        pairs = []
        for doc in documents:
            # Combine question and context for better matching
            doc_text = f"{doc.get('question', '')} {doc.get('context', '')}"
            pairs.append([query, doc_text])
        
        # Get relevance scores from cross-encoder
        scores = self.model.predict(pairs)
        
        # Add reranker scores to documents
        for i, doc in enumerate(documents):
            doc['reranker_score'] = float(scores[i])
            doc['original_rank'] = i + 1
        
        # Sort by reranker score (descending)
        reranked_docs = sorted(
            documents,
            key=lambda x: x['reranker_score'],
            reverse=True
        )
        
        # Return top N
        return reranked_docs[:top_n]
    
    def rerank_with_comparison(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Rerank documents and return comparison metrics
        
        Args:
            query: User query
            documents: List of documents from initial retrieval
            top_n: Number of top documents to return
        
        Returns:
            Tuple of (reranked_documents, comparison_metrics)
        """
        if not self.enabled or not documents:
            return documents[:top_n] if top_n else documents, {}
        
        top_n = top_n or settings.RERANKER_TOP_N
        
        # Store original order
        original_docs = documents.copy()
        
        # Rerank
        reranked_docs = self.rerank(query, documents, top_n)
        
        # Calculate metrics
        metrics = {
            "total_candidates": len(original_docs),
            "top_n_returned": len(reranked_docs),
            "reranker_enabled": True,
            "reranker_model": self.model_name,
            "score_range": {
                "min": min(doc['reranker_score'] for doc in reranked_docs) if reranked_docs else 0,
                "max": max(doc['reranker_score'] for doc in reranked_docs) if reranked_docs else 0,
                "mean": np.mean([doc['reranker_score'] for doc in reranked_docs]) if reranked_docs else 0,
            },
            "rank_changes": []
        }
        
        # Track rank changes
        for new_rank, doc in enumerate(reranked_docs, 1):
            original_rank = doc.get('original_rank', 0)
            if original_rank > 0:
                rank_change = original_rank - new_rank
                metrics["rank_changes"].append({
                    "doc_id": doc.get('id', 'unknown'),
                    "original_rank": original_rank,
                    "new_rank": new_rank,
                    "rank_change": rank_change,
                    "reranker_score": doc['reranker_score']
                })
        
        return reranked_docs, metrics


# Global reranker instance
_reranker_instance = None


def get_reranker() -> Reranker:
    """Get or create global reranker instance"""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = Reranker()
    return _reranker_instance
