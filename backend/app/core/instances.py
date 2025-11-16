"""
Singleton instances manager - Load all models and clients once at startup
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# SINGLETON INSTANCES - Loaded once at startup
# ============================================================================

# Database clients
_elasticsearch_client = None
_mongodb_client = None

# Models
_embedding_model = None
_reranker_model = None

# Services
_search_service = None
_answer_generator = None
_chatbot_workflow = None


# ============================================================================
# INITIALIZATION FUNCTION - Called at server startup
# ============================================================================

def initialize_all_instances():
    """
    Initialize all singleton instances at server startup
    This loads all models and clients once to avoid reloading on every request
    """
    global _elasticsearch_client, _mongodb_client
    global _embedding_model, _reranker_model
    global _search_service, _answer_generator, _chatbot_workflow
    
    logger.info("="*80)
    logger.info("🚀 INITIALIZING ALL INSTANCES")
    logger.info("="*80)
    
    # 1. Initialize database clients
    logger.info("📦 [1/6] Initializing Elasticsearch client...")
    from app.core.elasticsearch import get_elasticsearch_client
    _elasticsearch_client = get_elasticsearch_client()
    logger.info("✅ Elasticsearch client initialized")
    
    logger.info("📦 [2/6] Initializing MongoDB client...")
    from app.core.mongodb import get_mongodb_client
    _mongodb_client = get_mongodb_client()
    logger.info("✅ MongoDB client initialized")
    
    # 2. Initialize embedding model
    logger.info("📦 [3/6] Loading embedding model...")
    from sentence_transformers import SentenceTransformer
    from app.config import settings
    _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    logger.info(f"✅ Embedding model loaded: {settings.EMBEDDING_MODEL}")
    
    # 3. Initialize reranker model
    if settings.RERANKER_ENABLED:
        logger.info("📦 [4/6] Loading reranker model...")
        from sentence_transformers import CrossEncoder
        _reranker_model = CrossEncoder(settings.RERANKER_MODEL)
        logger.info(f"✅ Reranker model loaded: {settings.RERANKER_MODEL}")
    else:
        logger.info("⏭️  [4/6] Reranker disabled, skipping...")
        _reranker_model = None
    
    # 4. Initialize search service with reranker wrapper
    logger.info("📦 [5/6] Initializing search service...")
    from app.services.search import HybridSearch
    from app.services.reranker import Reranker

    # Create reranker wrapper with pre-loaded model
    reranker_wrapper = None
    if _reranker_model:
        reranker_wrapper = Reranker(model=_reranker_model)

    _search_service = HybridSearch(
        es_client=_elasticsearch_client,
        embedding_model=_embedding_model,
        reranker_model=reranker_wrapper
    )
    logger.info("✅ Search service initialized")
    
    # 5. Initialize answer generator
    logger.info("📦 [6/6] Initializing answer generator...")
    from app.services.answer_generator import AnswerGenerator
    _answer_generator = AnswerGenerator()
    logger.info("✅ Answer generator initialized")
    
    # 6. Initialize chatbot workflow
    logger.info("📦 [7/7] Initializing LangGraph workflow...")
    from app.workflows.chatbot_workflow import AdmissionsChatbotWorkflow
    _chatbot_workflow = AdmissionsChatbotWorkflow(
        search_service=_search_service,
        answer_generator=_answer_generator
    )
    logger.info("✅ LangGraph workflow initialized")
    
    logger.info("="*80)
    logger.info("🎉 ALL INSTANCES INITIALIZED SUCCESSFULLY")
    logger.info("="*80)


def shutdown_all_instances():
    """
    Cleanup all singleton instances at server shutdown
    """
    global _elasticsearch_client, _mongodb_client
    global _embedding_model, _reranker_model
    global _search_service, _answer_generator, _chatbot_workflow
    
    logger.info("🔄 Shutting down all instances...")
    
    # Close database connections
    if _mongodb_client:
        _mongodb_client.close()
        logger.info("✅ MongoDB client closed")
    
    if _elasticsearch_client:
        _elasticsearch_client.close()
        logger.info("✅ Elasticsearch client closed")
    
    # Clear references
    _elasticsearch_client = None
    _mongodb_client = None
    _embedding_model = None
    _reranker_model = None
    _search_service = None
    _answer_generator = None
    _chatbot_workflow = None
    
    logger.info("✅ All instances shut down")


# ============================================================================
# GETTER FUNCTIONS - Access pre-loaded instances
# ============================================================================

def get_elasticsearch_instance():
    """Get pre-loaded Elasticsearch client"""
    if _elasticsearch_client is None:
        raise RuntimeError("Elasticsearch client not initialized. Call initialize_all_instances() first.")
    return _elasticsearch_client


def get_mongodb_instance():
    """Get pre-loaded MongoDB client"""
    if _mongodb_client is None:
        raise RuntimeError("MongoDB client not initialized. Call initialize_all_instances() first.")
    return _mongodb_client


def get_embedding_model_instance():
    """Get pre-loaded embedding model"""
    if _embedding_model is None:
        raise RuntimeError("Embedding model not initialized. Call initialize_all_instances() first.")
    return _embedding_model


def get_reranker_model_instance() -> Optional[object]:
    """Get pre-loaded reranker model (can be None if disabled)"""
    return _reranker_model


def get_search_service_instance():
    """Get pre-loaded search service"""
    if _search_service is None:
        raise RuntimeError("Search service not initialized. Call initialize_all_instances() first.")
    return _search_service


def get_answer_generator_instance():
    """Get pre-loaded answer generator"""
    if _answer_generator is None:
        raise RuntimeError("Answer generator not initialized. Call initialize_all_instances() first.")
    return _answer_generator


def get_chatbot_workflow_instance():
    """Get pre-loaded chatbot workflow"""
    if _chatbot_workflow is None:
        raise RuntimeError("Chatbot workflow not initialized. Call initialize_all_instances() first.")
    return _chatbot_workflow


# ============================================================================
# STATUS CHECK
# ============================================================================

def check_instances_status() -> dict:
    """
    Check which instances are initialized
    
    Returns:
        Dictionary with status of each instance
    """
    return {
        "elasticsearch": _elasticsearch_client is not None,
        "mongodb": _mongodb_client is not None,
        "embedding_model": _embedding_model is not None,
        "reranker_model": _reranker_model is not None,
        "search_service": _search_service is not None,
        "answer_generator": _answer_generator is not None,
        "chatbot_workflow": _chatbot_workflow is not None
    }

