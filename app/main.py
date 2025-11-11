# FastAPI = Web framework
# Depends = Used for dependency injection (like API key checking)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth import verify_api_key
from app.api.models import (
    QueryRequest, QueryResponse, HealthCheckResponse,
    IntentRequest, IntentResponse, DocumentUploadRequest
)
from app.agents.orchestrator import orchestrator
from app.utils.logger import get_logger
from datetime import datetime
import uuid
import os
from app.api.document_endpoints import router as document_router

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Bot API - RAG-based Q&A system"
)

# Add CORS middleware CORS = Cross-Origin Resource Sharing
# It's a security feature that controls which websites can call API.
# CORS Configuration
if os.getenv("ENVIRONMENT") == "production":
    origins = [
        "https://huggingface.co",
        "https://velagalasr-dealer-bot.hf.space",
    ]
else:  # Development
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= INCLUDE ROUTERS =============
app.include_router(document_router)
logger = get_logger(__name__)

# ============ HEALTH CHECK ENDPOINT ============

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check API health and connectivity"""
    try:
        # Try to connect to OpenAI (simple validation)
        openai_connected = bool(settings.OPENAI_API_KEY)
        vector_db_connected = True  # Will be updated after vector DB setup
        
        return HealthCheckResponse(
            status="healthy",
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            openai_connected=openai_connected,
            vector_db_connected=vector_db_connected
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


# ============ MAIN QUERY ENDPOINT ============

@app.post(f"{settings.API_PREFIX}/query")
async def process_query(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Process user query and return bot response
    
    Args:
        request: User query request
        api_key: Validated API key
        
    Returns:
        dict: Bot's response with security info
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"Processing query [Session: {session_id}]: {request.query[:100]}")
        
        # Use orchestrator to process query with security
        from app.agents.orchestrator import orchestrator
        result = orchestrator.process_query(request.query, session_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ROOT ENDPOINT ============

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "query": f"{settings.API_PREFIX}/query",
            "intent": f"{settings.API_PREFIX}/intent",
            "upload_document": f"{settings.API_PREFIX}/documents/upload"
        },
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )