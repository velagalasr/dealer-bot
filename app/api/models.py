#Pydantic models - data structures that validate incoming requests and outgoing responses. Think of them as blueprints for data.

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ============ REQUEST MODELS ============

class QueryRequest(BaseModel):
    """User query request"""
    query: str
    session_id: Optional[str] = None
    context: Optional[str] = None

class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    url: str
    document_type: Optional[str] = "manual"

class IntentRequest(BaseModel):
    """Intent classification request"""
    text: str


# ============ RESPONSE MODELS ============

class IntentResponse(BaseModel):
    """Intent classification response"""
    intent: str
    confidence: float
    specialist: str

class SourceDocument(BaseModel):
    """Source document reference"""
    title: str
    page: Optional[int] = None
    chunk_id: str
    relevance_score: float

class QueryResponse(BaseModel):
    """Bot response to user query"""
    answer: str
    intent: str
    confidence: float
    sources: List[SourceDocument]
    timestamp: datetime
    session_id: str

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str
    code: int

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    openai_connected: bool
    vector_db_connected: bool