"""
Elasticsearch connection and utilities
"""

from elasticsearch import Elasticsearch
from typing import Optional

from app.config import settings


_es_client: Optional[Elasticsearch] = None


def get_elasticsearch_client() -> Elasticsearch:
    """
    Get Elasticsearch client instance
    Supports both local and Elastic Cloud connections
    """
    global _es_client
    
    if _es_client is None:
        # Check if using Elastic Cloud
        if settings.ELASTICSEARCH_CLOUD_ID:
            _es_client = Elasticsearch(
                cloud_id=settings.ELASTICSEARCH_CLOUD_ID,
                api_key=settings.ELASTICSEARCH_API_KEY,
            )
        elif settings.ELASTICSEARCH_API_KEY:
            # Using API key authentication
            _es_client = Elasticsearch(
                settings.ELASTICSEARCH_URL,
                api_key=settings.ELASTICSEARCH_API_KEY,
            )
        else:
            # Using basic authentication
            _es_client = Elasticsearch(
                settings.ELASTICSEARCH_URL,
                basic_auth=(
                    settings.ELASTICSEARCH_USERNAME,
                    settings.ELASTICSEARCH_PASSWORD
                ),
                verify_certs=False,  # For development only
            )
    
    return _es_client


def close_elasticsearch_connection():
    """Close Elasticsearch connection"""
    global _es_client
    if _es_client:
        _es_client.close()
        _es_client = None


def check_elasticsearch_health() -> dict:
    """
    Check Elasticsearch health
    
    Returns:
        dict: Health status with connection info
    """
    try:
        client = get_elasticsearch_client()
        
        # Test connection
        if not client.ping():
            return {
                "status": "unhealthy",
                "message": "Cannot ping Elasticsearch",
                "details": {}
            }
        
        # Get cluster info
        info = client.info()
        
        # Get index info
        index_name = settings.ELASTICSEARCH_INDEX_NAME
        try:
            index_stats = client.indices.stats(index=index_name)
            doc_count = index_stats["indices"][index_name]["total"]["docs"]["count"]
        except Exception:
            doc_count = 0
        
        return {
            "status": "healthy",
            "message": "Connected to Elasticsearch",
            "details": {
                "cluster_name": info["cluster_name"],
                "version": info["version"]["number"],
                "index_name": index_name,
                "document_count": doc_count
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Elasticsearch connection failed: {str(e)}",
            "details": {"error": str(e)}
        }


def create_index_if_not_exists():
    """
    Create Elasticsearch index with proper mappings if it doesn't exist
    """
    try:
        client = get_elasticsearch_client()
        index_name = settings.ELASTICSEARCH_INDEX_NAME
        
        # Check if index exists
        if client.indices.exists(index=index_name):
            print(f"✅ Index '{index_name}' already exists")
            return True
        
        # Create index with mappings
        mappings = {
            "mappings": {
                "properties": {
                    "question": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "answer": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "article": {
                        "type": "keyword"
                    },
                    "document": {
                        "type": "keyword"
                    },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 1536  # OpenAI text-embedding-ada-002 dimensions
                    },
                    "metadata": {
                        "type": "object",
                        "enabled": True
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "standard": {
                            "type": "standard"
                        }
                    }
                }
            }
        }
        
        # Create the index
        response = client.indices.create(
            index=index_name,
            body=mappings
        )
        
        print(f"✅ Created index '{index_name}': {response}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create index: {e}")
        return False


def delete_index():
    """
    Delete Elasticsearch index (for testing/cleanup)
    """
    try:
        client = get_elasticsearch_client()
        index_name = settings.ELASTICSEARCH_INDEX_NAME
        
        if client.indices.exists(index=index_name):
            response = client.indices.delete(index=index_name)
            print(f"✅ Deleted index '{index_name}': {response}")
            return True
        else:
            print(f"ℹ️ Index '{index_name}' does not exist")
            return True
            
    except Exception as e:
        print(f"❌ Failed to delete index: {e}")
        return False


def get_index_stats() -> dict:
    """
    Get Elasticsearch index statistics
    
    Returns:
        dict: Index statistics
    """
    try:
        client = get_elasticsearch_client()
        index_name = settings.ELASTICSEARCH_INDEX_NAME
        
        if not client.indices.exists(index=index_name):
            return {
                "exists": False,
                "document_count": 0,
                "size_in_bytes": 0
            }
        
        stats = client.indices.stats(index=index_name)
        index_stats = stats["indices"][index_name]["total"]
        
        return {
            "exists": True,
            "document_count": index_stats["docs"]["count"],
            "size_in_bytes": index_stats["store"]["size_in_bytes"],
            "segments": index_stats["segments"]["count"]
        }
        
    except Exception as e:
        return {
            "exists": False,
            "error": str(e),
            "document_count": 0,
            "size_in_bytes": 0
        }
