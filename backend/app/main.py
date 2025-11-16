"""
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
from datetime import datetime

from app.config import settings
from app.api import chat_router, health_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Admissions Counseling Chatbot API",
    description="RAG-based chatbot for Vietnamese university admissions counseling using LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "ValidationError",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("="*80)
    logger.info("🚀 Starting Admissions Counseling Chatbot API")
    logger.info("="*80)
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔍 Elasticsearch: {settings.ELASTICSEARCH_CLOUD_ID[:20] if settings.ELASTICSEARCH_CLOUD_ID else 'Local'}...")
    logger.info(f"🗄️  MongoDB: {settings.MONGODB_URL}")
    logger.info(f"🤖 LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"🔄 Reranker: {'Enabled' if settings.RERANKER_ENABLED else 'Disabled'}")
    logger.info(f"🧠 LangGraph: {'Enabled' if settings.LANGGRAPH_ENABLED else 'Disabled'}")
    logger.info("="*80)

    # Initialize all models and clients
    logger.info("\n🔧 Initializing all instances (models, clients, services)...")
    from app.core.instances import initialize_all_instances
    initialize_all_instances()
    logger.info("✅ Server ready to accept requests!\n")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("="*80)
    logger.info("🛑 Shutting down Admissions Counseling Chatbot API")

    # Cleanup all instances
    from app.core.instances import shutdown_all_instances
    shutdown_all_instances()
    logger.info("="*80)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "Admissions Counseling Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc)
        }
    )


# Register routers
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


# Run with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

