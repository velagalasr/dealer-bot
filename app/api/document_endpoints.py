"""
Document API Endpoints
Handle document upload, ingestion, listing, deletion
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import verify_api_key
from app.core.rag_pipeline import rag_pipeline
from app.utils.logger import get_logger
from fastapi import File, UploadFile
from pathlib import Path
import shutil

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


# ============= REQUEST/RESPONSE MODELS =============

class DocumentIngestRequest(BaseModel):
    """Request to ingest document from URL"""
    url: str
    doc_type: str = "system"  # "system" or "user"
    user_id: Optional[str] = None
    chunk_size: int = 500
    chunk_overlap: int = 100


class DocumentListResponse(BaseModel):
    """Response with list of documents"""
    total_documents: int
    total_chunks: int
    documents: dict


class DocumentIngestResponse(BaseModel):
    """Response from document ingestion"""
    success: bool
    document_id: Optional[str] = None
    filename: Optional[str] = None
    chunks_created: Optional[int] = None
    doc_type: Optional[str] = None
    user_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ============= ENDPOINTS =============

@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    request: DocumentIngestRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest document from URL into RAG system
    
    Args:
        request: Document ingest request
        api_key: Validated API key
        
    Returns:
        DocumentIngestResponse: Ingestion result
    """
    try:
        logger.info(f"Document ingest request: {request.url}, type: {request.doc_type}")
        
        # Validate document type
        if request.doc_type not in ["system", "user"]:
            raise HTTPException(
                status_code=400,
                detail="doc_type must be 'system' or 'user'"
            )
        
        # Validate user_id for user documents
        if request.doc_type == "user" and not request.user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id required for user documents"
            )
        
        # Ingest document
        result = rag_pipeline.ingest_document_from_url(
            url=request.url,
            doc_type=request.doc_type,
            user_id=request.user_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        if not result.get("success"):
            logger.error(f"Document ingestion failed: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest document: {result.get('error')}"
            )
        
        logger.info(f"Document ingested successfully: {result.get('document_id')}")
        return DocumentIngestResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document ingest error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest document: {str(e)}"
        )

@router.post("/ingest-file", response_model=DocumentIngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    doc_type: str = "system",
    user_id: Optional[str] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest document from uploaded file into RAG system
    
    Args:
        file: Uploaded PDF file
        doc_type: "system" or "user"
        user_id: Owner user ID (required for user docs)
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        api_key: Validated API key
        
    Returns:
        DocumentIngestResponse: Ingestion result
    """
    try:
        logger.info(f"File ingestion request: {file.filename}, type: {doc_type}")
        
        # Validate document type
        if doc_type not in ["system", "user"]:
            raise HTTPException(
                status_code=400,
                detail="doc_type must be 'system' or 'user'"
            )
        
        # Validate user_id for user documents
        if doc_type == "user" and not user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id required for user documents"
            )
        
        # Save uploaded file temporarily
        temp_path = Path("temp") / file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Ingest from file
        result = rag_pipeline.ingest_document_from_file(
            file_path=temp_path,
            doc_type=doc_type,
            user_id=user_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()
        
        if not result.get("success"):
            logger.error(f"Document ingestion failed: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest document: {result.get('error')}"
            )
        
        logger.info(f"Document ingested successfully: {result.get('document_id')}")
        return DocumentIngestResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File ingest error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest file: {str(e)}"
        )

@router.get("/list", response_model=DocumentListResponse)
async def list_documents(
    api_key: str = Depends(verify_api_key)
):
    """
    List all ingested documents
    
    Args:
        api_key: Validated API key
        
    Returns:
        DocumentListResponse: List of documents
    """
    try:
        logger.info("Listing documents")
        
        result = rag_pipeline.get_ingested_documents()
        
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        return DocumentListResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/clear")
async def clear_all_documents(
    api_key: str = Depends(verify_api_key)
):
    """
    Clear all documents from RAG system (for testing only)
    
    Args:
        api_key: Validated API key
        
    Returns:
        dict: Clear result
    """
    try:
        logger.warning("Clear all documents request")
        
        result = rag_pipeline.clear_all_data()
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to clear documents")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear documents: {str(e)}"
        )


@router.get("/status")
async def get_rag_status(
    api_key: str = Depends(verify_api_key)
):
    """
    Get RAG system status
    
    Args:
        api_key: Validated API key
        
    Returns:
        dict: RAG system status
    """
    try:
        logger.info("Getting RAG status")
        
        docs_info = rag_pipeline.get_ingested_documents()
        
        return {
            "status": "healthy",
            "total_documents": docs_info.get("total_documents", 0),
            "total_chunks": docs_info.get("total_chunks", 0),
            "rag_ready": docs_info.get("total_documents", 0) > 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get RAG status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get RAG status: {str(e)}"
        )