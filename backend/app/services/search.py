"""
Search module with hybrid search (BM25 + Vector) and reranking
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.core.elasticsearch import get_elasticsearch_client
from app.services.reranker import get_reranker
from app.services.answer_generator import get_answer_generator


class HybridSearch:
    """
    Hybrid search combining BM25 (keyword) and Vector (semantic) search
    with optional reranking
    """

    def __init__(self, es_client=None, embedding_model=None, reranker_model=None):
        """
        Initialize HybridSearch

        Args:
            es_client: Pre-loaded Elasticsearch client (optional)
            embedding_model: Pre-loaded embedding model (optional)
            reranker_model: Pre-loaded Reranker object (optional)
        """
        # Use provided instances or create new ones
        self.es_client = es_client if es_client else get_elasticsearch_client()
        self.index_name = settings.ELASTICSEARCH_INDEX_NAME

        # Use provided embedding model or load new one
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            print(f"📦 Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print(f"✅ Embedding model loaded")

        # Use provided reranker (Reranker object) or create new one
        if reranker_model:
            self.reranker = reranker_model
        else:
            self.reranker = get_reranker()

        # Load answer generator (not used in search, can be removed)
        # self.answer_generator = get_answer_generator()
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query"""
        embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None,
        use_reranker: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with BM25 + Vector search
        
        Args:
            query: User query
            top_k: Number of results to return (default: from settings)
            filters: Optional metadata filters
            use_reranker: Whether to use reranker (default: True)
        
        Returns:
            List of search results with scores
        """
        # Determine retrieval size
        if use_reranker and settings.RERANKER_ENABLED:
            # Retrieve more candidates for reranking
            retrieval_size = settings.RERANKER_TOP_K
            final_size = top_k or settings.RERANKER_TOP_N
        else:
            retrieval_size = top_k or settings.RETRIEVAL_TOP_K
            final_size = retrieval_size
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Build Elasticsearch query
        es_query = {
            "size": retrieval_size,
            "query": {
                "bool": {
                    "should": [
                        # BM25 keyword search on question
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["question^2", "context", "extractive_answer", "abstractive_answer"],
                                "type": "best_fields",
                                "boost": settings.RETRIEVAL_BM25_WEIGHT
                            }
                        },
                        # Vector semantic search on question embedding
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'question_embedding') + 1.0",
                                    "params": {"query_vector": query_embedding}
                                },
                                "boost": settings.RETRIEVAL_VECTOR_WEIGHT
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "_source": [
                "index", "question", "context", "article", "document",
                "extractive_answer", "abstractive_answer", "yes_no", "metadata"
            ]
        }
        
        # Add filters if provided
        if filters:
            es_query["query"]["bool"]["filter"] = []
            for key, value in filters.items():
                es_query["query"]["bool"]["filter"].append({
                    "term": {f"metadata.{key}": value}
                })
        
        # Execute search
        response = self.es_client.search(index=self.index_name, body=es_query)
        
        # Parse results
        results = []
        for hit in response["hits"]["hits"]:
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"]
            }
            results.append(result)
        
        # Apply reranking if enabled
        if use_reranker and settings.RERANKER_ENABLED and results:
            results = self.reranker.rerank(query, results, top_n=final_size)
        else:
            results = results[:final_size]
        
        return results
    
    def search_with_comparison(
        self,
        query: str,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Search with and without reranking for comparison
        
        Args:
            query: User query
            top_k: Number of results to return
        
        Returns:
            Dictionary with both results and comparison metrics
        """
        # Search without reranking
        results_no_rerank = self.hybrid_search(query, top_k=top_k, use_reranker=False)
        
        # Search with reranking
        if settings.RERANKER_ENABLED:
            # Get more candidates
            candidates = self.hybrid_search(
                query,
                top_k=settings.RERANKER_TOP_K,
                use_reranker=False
            )
            
            # Rerank with comparison
            results_with_rerank, metrics = self.reranker.rerank_with_comparison(
                query,
                candidates,
                top_n=top_k or settings.RERANKER_TOP_N
            )
        else:
            results_with_rerank = results_no_rerank
            metrics = {"reranker_enabled": False}
        
        return {
            "query": query,
            "results_without_reranking": results_no_rerank,
            "results_with_reranking": results_with_rerank,
            "reranking_metrics": metrics
        }

    def search_and_generate(
        self,
        query: str,
        top_k: int = None,
        include_generation: bool = True,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: Search + Rerank + Generate Answer

        Args:
            query: User query
            top_k: Number of documents to retrieve
            include_generation: Whether to generate answer (default: True)
            conversation_history: Optional conversation history for context

        Returns:
            Dictionary with generated answer and retrieved documents
        """
        # Step 1: Hybrid search with reranking
        retrieved_documents = self.hybrid_search(
            query,
            top_k=top_k,
            use_reranker=True
        )

        # Step 2: Generate answer if enabled
        if include_generation and settings.ANSWER_GENERATION_ENABLED:
            generation_result = self.answer_generator.generate_answer(
                query,
                retrieved_documents,
                conversation_history=conversation_history
            )

            generated_answer = generation_result["answer"]
            generation_metadata = {
                "model": generation_result["model"],
                "tokens_used": generation_result["tokens_used"],
                "finish_reason": generation_result["finish_reason"],
                "generation_successful": generation_result["generation_successful"],
                "fallback_used": generation_result["fallback_used"]
            }

            if "error" in generation_result:
                generation_metadata["error"] = generation_result["error"]
        else:
            # Fallback to extractive answer
            if retrieved_documents:
                generated_answer = retrieved_documents[0].get('abstractive_answer') or \
                                 retrieved_documents[0].get('extractive_answer') or \
                                 "Không tìm thấy câu trả lời phù hợp."
            else:
                generated_answer = "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn."

            generation_metadata = {
                "model": "none",
                "tokens_used": {"prompt": 0, "completion": 0, "total": 0},
                "generation_successful": False,
                "fallback_used": True
            }

        # Step 3: Format response
        return {
            "query": query,
            "generated_answer": generated_answer,
            "retrieved_documents": retrieved_documents,
            "metadata": {
                "retrieval_method": "hybrid_search_with_reranking",
                "num_documents_retrieved": len(retrieved_documents),
                "num_documents_used": generation_metadata.get("num_contexts_used", len(retrieved_documents)),
                "generation_model": generation_metadata["model"],
                "reranker_enabled": settings.RERANKER_ENABLED,
                "answer_generation_enabled": settings.ANSWER_GENERATION_ENABLED,
                **generation_metadata
            }
        }


# Global search instance
_search_instance = None


def get_search_engine() -> HybridSearch:
    """Get or create global search engine instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = HybridSearch()
    return _search_instance
