"""
Main FastAPI application.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routes import health, interview, kpi, cv_upload, rag  # langgraph_interview disabled for now

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Interview Agent API...")
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Gemini Model: {settings.gemini_model}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Interview Agent API...")


# Create FastAPI app
app = FastAPI(
    title="Interview Agent API",
    description="AI-powered interview system using Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import research router
try:
    from .routes import research
    app.include_router(research.router)
    logger.info("Research router loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load research router: {e}")

# Include routers
app.include_router(health.router)
app.include_router(interview.router)
app.include_router(kpi.router)
app.include_router(cv_upload.router)
app.include_router(rag.router)
# app.include_router(langgraph_interview.router)  # Disabled - needs checkpoint fix


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
