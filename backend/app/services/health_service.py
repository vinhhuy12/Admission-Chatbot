"""
Health check service - Business logic for health checks
"""

from datetime import datetime
from typing import Dict, Any
import logging

from app.core.instances import get_elasticsearch_instance, get_mongodb_instance
from app.core.elasticsearch import check_elasticsearch_health
from app.core.mongodb import check_mongodb_health
from app.config import settings

logger = logging.getLogger(__name__)


def check_system_health() -> Dict[str, Any]:
    """
    Check health of all system components
    
    Returns:
        Dictionary with overall status, services status, version, timestamp
    """
    logger.info("🏥 Performing health check")
    
    services = {}
    overall_status = "healthy"
    
    # Check Elasticsearch
    es_status = check_elasticsearch_health()
    services["elasticsearch"] = es_status
    if es_status["status"] != "healthy":
        overall_status = "unhealthy"
    
    # Check MongoDB
    mongo_status = check_mongodb_health()
    services["mongodb"] = mongo_status
    if mongo_status["status"] != "healthy":
        overall_status = "unhealthy"
    
    # Check OpenAI
    openai_status = check_openai_health()
    services["openai"] = openai_status
    if openai_status["status"] != "healthy":
        overall_status = "unhealthy"
    
    logger.info(f"✅ Health check completed: {overall_status}")
    
    return {
        "status": overall_status,
        "services": services,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }





def check_openai_health() -> Dict[str, Any]:
    """
    Check OpenAI API health
    
    Returns:
        Dictionary with status, message, details
    """
    try:
        if settings.OPENAI_API_KEY:
            return {
                "status": "healthy",
                "message": "API key configured",
                "details": {
                    "model": settings.ANSWER_GENERATION_MODEL
                }
            }
        else:
            return {
                "status": "unhealthy",
                "message": "API key not configured",
                "details": None
            }
    
    except Exception as e:
        logger.error(f"❌ OpenAI health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "details": None
        }

