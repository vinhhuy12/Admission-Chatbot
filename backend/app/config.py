"""
Configuration settings for the application
Loads environment variables from .env file using os.getenv()
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables using os.getenv()"""

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Admissions Counseling Chatbot")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Backend API
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    VITE_API_URL: str = os.getenv("VITE_API_URL", "http://localhost:8000")

    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "admissions_chatbot")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "admissions_chatbot")  # Alias for compatibility
    MONGODB_USERS_COLLECTION: str = os.getenv("MONGODB_USERS_COLLECTION", "users")
    MONGODB_CONVERSATIONS_COLLECTION: str = os.getenv("MONGODB_CONVERSATIONS_COLLECTION", "conversations")
    MONGODB_FEEDBACK_COLLECTION: str = os.getenv("MONGODB_FEEDBACK_COLLECTION", "feedback")

    # Elasticsearch
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    ELASTICSEARCH_CLOUD_ID: str = os.getenv("ELASTICSEARCH_CLOUD_ID", "")
    ELASTICSEARCH_API_KEY: str = os.getenv("ELASTICSEARCH_API_KEY", "")
    ELASTICSEARCH_INDEX_NAME: str = os.getenv("ELASTICSEARCH_INDEX_NAME", "admissions_qa")
    ELASTICSEARCH_USERNAME: str = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
    ELASTICSEARCH_PASSWORD: str = os.getenv("ELASTICSEARCH_PASSWORD", "changeme")

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-gpt-5-nano-2025-08-07")  # Changed from gpt-3.5-turbo
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))

    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))

    # Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

    # Retrieval
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    RETRIEVAL_MIN_SCORE: float = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.5"))
    RETRIEVAL_BM25_WEIGHT: float = float(os.getenv("RETRIEVAL_BM25_WEIGHT", "0.3"))
    RETRIEVAL_VECTOR_WEIGHT: float = float(os.getenv("RETRIEVAL_VECTOR_WEIGHT", "0.7"))

    # Reranking
    RERANKER_ENABLED: bool = os.getenv("RERANKER_ENABLED", "True").lower() == "true"
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-12-v2")
    RERANKER_TOP_K: int = int(os.getenv("RERANKER_TOP_K", "20"))
    RERANKER_TOP_N: int = int(os.getenv("RERANKER_TOP_N", "5"))

    # Answer Generation
    ANSWER_GENERATION_ENABLED: bool = os.getenv("ANSWER_GENERATION_ENABLED", "True").lower() == "true"
    ANSWER_GENERATION_MODEL: str = os.getenv("ANSWER_GENERATION_MODEL", "gpt-gpt-5-nano-2025-08-07")  # Changed from gpt-3.5-turbo
    ANSWER_MAX_TOKENS: int = int(os.getenv("ANSWER_MAX_TOKENS", "500"))
    ANSWER_TEMPERATURE: float = float(os.getenv("ANSWER_TEMPERATURE", "0.7"))
    ANSWER_MAX_CONTEXT_DOCS: int = int(os.getenv("ANSWER_MAX_CONTEXT_DOCS", "5"))

    # LangGraph Workflow
    LANGGRAPH_ENABLED: bool = os.getenv("LANGGRAPH_ENABLED", "True").lower() == "true"
    LANGGRAPH_MAX_ITERATIONS: int = int(os.getenv("LANGGRAPH_MAX_ITERATIONS", "10"))
    LANGGRAPH_TIMEOUT: int = int(os.getenv("LANGGRAPH_TIMEOUT", "60"))

    # LangGraph
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "5"))
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "True").lower() == "true"

    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # Redis (Optional)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "False").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))

    # Data Ingestion
    DATA_FILE_PATH: str = os.getenv("DATA_FILE_PATH", "train.csv")
    BATCH_SIZE_INGESTION: int = int(os.getenv("BATCH_SIZE_INGESTION", "100"))
    SKIP_EXISTING_DOCS: bool = os.getenv("SKIP_EXISTING_DOCS", "True").lower() == "true"

    # Monitoring
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "False").lower() == "true"
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "admissions-chatbot")

    # Development
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    SHOW_ERROR_DETAILS: bool = os.getenv("SHOW_ERROR_DETAILS", "True").lower() == "true"


# Create global settings instance
settings = Settings()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

