"""
Health check API routes and schemas - Combined file for flattened structure
"""

from fastapi import APIRouter
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.services import health_service

# Setup logging
logger = logging.getLogger(__name__)

# ============================================
# PYDANTIC SCHEMAS
# ============================================

class ServiceStatus(BaseModel):
    """Schema for individual service status"""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    message: Optional[str] = Field(None, description="Status message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class HealthCheckResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="Overall system status")
    services: Dict[str, ServiceStatus] = Field(..., description="Individual service statuses")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Check timestamp")

# ============================================
# API ROUTES
# ============================================

# Create router
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthCheckResponse)
@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthCheckResponse: System health status
    """
    # Call service function
    result = health_service.check_system_health()

    # Convert services to schema
    services = {
        name: ServiceStatus(**status)
        for name, status in result["services"].items()
    }

    response = HealthCheckResponse(
        status=result["status"],
        services=services,
        version=result["version"],
        timestamp=result["timestamp"]
    )

    return response
