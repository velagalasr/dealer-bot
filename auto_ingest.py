#!/usr/bin/env python3
"""
Auto-ingest sample documents on startup (HuggingFace only)
"""
import os
from pathlib import Path
from app.core.rag_pipeline import rag_pipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)

def ingest_sample_documents():
    """Ingest any PDF files from data/documents/ if vector DB is empty (HuggingFace only)"""
    # Only run on HuggingFace Spaces (ephemeral storage)
    if not os.getenv("SPACE_ID"):
        logger.info("Not running on HuggingFace Spaces - skipping auto-ingest (local storage persists)")
        return
    
    logger.info("Running on HuggingFace Spaces - checking if auto-ingest needed")
    
    try:
        from app.core.vector_db import vector_db
        
        # Check if vector DB already has documents
        count = vector_db.get_collection_info()["document_count"]
        if count > 0:
            logger.info(f"Vector DB already has {count} documents, skipping auto-ingest")
            return
        
        logger.info("Vector DB is empty, checking for sample documents to ingest...")
        
        # Look for PDFs in data/documents/
        docs_dir = Path("data/documents")
        if not docs_dir.exists():
            logger.info("No documents directory found")
            return
            
        pdf_files = list(docs_dir.glob("*.pdf"))
        if not pdf_files:
            logger.info("No PDF files found in data/documents/")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to ingest")
        
        for pdf_file in pdf_files:
            logger.info(f"Ingesting: {pdf_file.name}")
            result = rag_pipeline.ingest_document_from_file(
                file_path=pdf_file,
                doc_type="user",  # Use "user" to match orchestrator searches (doc_type=None)
                user_id="auto-ingest",
                chunk_size=500,
                chunk_overlap=100
            )
            
            if result.get("success"):
                logger.info(f"✅ Successfully ingested {pdf_file.name}: {result.get('chunks_created')} chunks")
            else:
                logger.error(f"❌ Failed to ingest {pdf_file.name}: {result.get('error')}")
                
    except Exception as e:
        logger.error(f"Error during auto-ingest: {str(e)}")

if __name__ == "__main__":
    ingest_sample_documents()
