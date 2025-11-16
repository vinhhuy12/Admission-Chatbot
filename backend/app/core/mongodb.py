"""
MongoDB connection and utilities
"""

from pymongo import MongoClient
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from app.config import settings


# Synchronous MongoDB client (for data ingestion scripts)
_sync_client: Optional[MongoClient] = None

# Asynchronous MongoDB client (for FastAPI)
_async_client: Optional[AsyncIOMotorClient] = None


def get_mongodb_client() -> MongoClient:
    """Get synchronous MongoDB client"""
    global _sync_client
    if _sync_client is None:
                _sync_client = MongoClient(
            settings.MONGODB_URL, serverSelectionTimeoutMS=5000
        )
    return _sync_client


def get_async_mongodb_client() -> AsyncIOMotorClient:
    """Get asynchronous MongoDB client for FastAPI"""
    global _async_client
    if _async_client is None:
        _async_client = AsyncIOMotorClient(
            settings.MONGODB_URL, serverSelectionTimeoutMS=5000
        )
    return _async_client


def get_database() -> Database:
    """Get MongoDB database instance"""
    client = get_mongodb_client()
    return client[settings.MONGODB_DB_NAME]


async def get_async_database():
    """Get async MongoDB database instance"""
    client = get_async_mongodb_client()
    return client[settings.MONGODB_DB_NAME]


def close_mongodb_connection():
    """Close MongoDB connection"""
    global _sync_client, _async_client
    if _sync_client:
        _sync_client.close()
        _sync_client = None
    if _async_client:
        _async_client.close()
        _async_client = None


# Collections helper functions
def get_users_collection():
    """Get users collection"""
    db = get_database()
    return db[settings.MONGODB_USERS_COLLECTION]


def get_conversations_collection():
    """Get conversations collection"""
    db = get_database()
    return db[settings.MONGODB_CONVERSATIONS_COLLECTION]


def get_feedback_collection():
    """Get feedback collection"""
    db = get_database()
    return db[settings.MONGODB_FEEDBACK_COLLECTION]


async def get_async_users_collection():
    """Get async users collection"""
    db = await get_async_database()
    return db[settings.MONGODB_USERS_COLLECTION]


async def get_async_conversations_collection():
    """Get async conversations collection"""
    db = await get_async_database()
    return db[settings.MONGODB_CONVERSATIONS_COLLECTION]


async def get_async_feedback_collection():
    """Get async feedback collection"""
    db = await get_async_database()
    return db[settings.MONGODB_FEEDBACK_COLLECTION]


def init_mongodb_indexes():
    """Initialize MongoDB indexes for better performance"""
    db = get_database()
    
    # Users collection indexes
    users = db[settings.MONGODB_USERS_COLLECTION]
    users.create_index("email", unique=True)
    users.create_index("created_at")
    
    # Conversations collection indexes
    conversations = db[settings.MONGODB_CONVERSATIONS_COLLECTION]
    conversations.create_index("user_id")
    conversations.create_index("created_at")
    conversations.create_index([("user_id", 1), ("created_at", -1)])
    
    # Feedback collection indexes
    feedback = db[settings.MONGODB_FEEDBACK_COLLECTION]
    feedback.create_index("conversation_id")
    feedback.create_index("created_at")
    
    print("✅ MongoDB indexes created successfully")


def check_mongodb_health() -> dict:
    """
    Check MongoDB health
    
    Returns:
        dict: Health status with connection info
    """
    try:
        client = get_mongodb_client()
        
        # Test connection
        client.admin.command('ping')
        
        # Get server info
        server_info = client.server_info()
        
        # Get database info
        db = get_database()
        collections = db.list_collection_names()
        
        return {
            "status": "healthy",
            "message": "Connected to MongoDB",
            "details": {
                "version": server_info["version"],
                "database": settings.MONGODB_DB_NAME,
                "collections": collections
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"MongoDB connection failed: {str(e)}",
            "details": {"error": str(e)}
        }
