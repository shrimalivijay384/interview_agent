"""
Health check and utility routes.
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "interview-agent-api"
    }


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Interview Agent API",
        "version": "1.0.0",
        "description": "AI-powered interview system using FastAPI, React, and Google Gemini",
        "endpoints": {
            "health": "/health",
            "interview": "/api/interview/*",
            "docs": "/docs"
        }
    }
