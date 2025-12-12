"""
Document API Endpoints
Handle document upload, ingestion, listing, deletion
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from app.auth import verify_api_key
from app.core.rag_pipeline import rag_pipeline
from app.core.document_manager import document_manager
from app.utils.logger import get_logger
from pathlib import Path
import os

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
    
    Steps:
    1. Download from URL
    2. Extract text and create chunks
    3. Generate embeddings
    4. Store in Chroma (persistent)
    
    Args:
        request: Document ingest request
        api_key: Validated API key
        
    Returns:
        DocumentIngestResponse: Ingestion result
    """
    try:
        logger.info(f"Document ingest from URL: {request.url}")
        
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
        
        # Ingest through RAG pipeline
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
        
        logger.info(f"✅ Document ingested: {result.get('document_id')}")
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
    api_key: str = Depends(verify_api_key),
    doc_type: str = "user",
    user_id: Optional[str] = "gradio-user"
):
    """
    Upload and ingest document through RAG pipeline
    
    Steps:
    1. Save uploaded file to disk
    2. Extract text and create chunks
    3. Generate embeddings
    4. Store in Chroma (persistent)
    
    Args:
        file: Uploaded file
        api_key: Validated API key
        doc_type: Document type (system/user)
        user_id: Owner user ID
        
    Returns:
        DocumentIngestResponse: Ingestion result
    """
    temp_path = None
    
    try:
        logger.info(f"Ingesting uploaded file: {file.filename}")
        
        # Create temp path in documents directory
        temp_path = Path(document_manager.documents_path) / file.filename
        
        # Save uploaded file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File saved temporarily: {temp_path}")
        
        # Ingest through RAG pipeline
        result = rag_pipeline.ingest_document_from_file(
            file_path=temp_path,
            doc_type=doc_type,
            user_id=user_id,
            chunk_size=500,
            chunk_overlap=100
        )
        
        if not result.get("success"):
            logger.error(f"File ingestion failed: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest file: {result.get('error')}"
            )
        
        logger.info(f"✅ File ingested: {result.get('document_id')}")
        return DocumentIngestResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File ingest error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest file: {str(e)}"
        )
    finally:
        # Clean up temp file if it still exists
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
                logger.debug(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")


@router.get("/list", response_model=DocumentListResponse)
async def list_documents(
    api_key: str = Depends(verify_api_key)
):
    """
    List all ingested documents from Chroma
    
    Returns documents that have been ingested and indexed
    (these are searchable by RAG)
    
    Args:
        api_key: Validated API key
        
    Returns:
        DocumentListResponse: List of ingested documents
    """
    try:
        logger.info("Listing ingested documents")
        
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
    
    WARNING: This will delete all ingested documents and embeddings!
    
    Args:
        api_key: Validated API key
        
    Returns:
        dict: Clear result
    """
    try:
        logger.warning("⚠️ Clear all documents request")
        
        result = rag_pipeline.clear_all_data()
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to clear documents")
            )
        
        logger.warning("✅ All documents cleared")
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
    
    Returns:
        dict: RAG system health and document count
    """
    try:
        logger.info("Getting RAG status")
        
        docs_info = rag_pipeline.get_ingested_documents()
        total_docs = docs_info.get("total_documents", 0)
        total_chunks = docs_info.get("total_chunks", 0)
        
        return {
            "status": "healthy" if total_docs > 0 else "empty",
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "rag_ready": total_docs > 0,
            "message": f"RAG system has {total_docs} documents with {total_chunks} chunks"
        }
        
    except Exception as e:
        logger.error(f"Failed to get RAG status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get RAG status: {str(e)}"
        )