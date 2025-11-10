"""
RAG Pipeline Module
Orchestrates the complete RAG system
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import uuid
from app.core.document_manager import document_manager
from app.core.text_processor import text_processor
from app.core.embeddings import embeddings_manager
from app.core.vector_db import vector_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Orchestrate complete RAG pipeline"""
    
    def __init__(self, document_manager=document_manager,
                 text_processor=text_processor,
                 embeddings_manager=embeddings_manager,
                 vector_db=vector_db):
        """
        Initialize RAG pipeline
        
        Args:
            document_manager: Document manager instance
            text_processor: Text processor instance
            embeddings_manager: Embeddings manager instance
            vector_db: Vector database instance
        """
        self.document_manager = document_manager
        self.text_processor = text_processor
        self.embeddings_manager = embeddings_manager
        self.vector_db = vector_db
        
        # Track ingested documents
        self.ingested_documents = {}
        
        logger.info("RAG pipeline initialized")
    
    def ingest_document_from_url(self, url: str, doc_type: str = "system",
                                user_id: Optional[str] = None,
                                chunk_size: int = 500,
                                chunk_overlap: int = 100) -> Dict[str, Any]:
        """
        Complete pipeline: download → extract → embed → store
        
        Args:
            url: Document URL
            doc_type: "system" (admin) or "user" (dealer)
            user_id: Owner user ID (required for user docs)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dict: Ingestion result
        """
        try:
            session_id = str(uuid.uuid4())
            logger.info(f"[{session_id}] Starting document ingestion from URL: {url}")
            
            # Validate document type
            if doc_type not in ["system", "user"]:
                raise ValueError("doc_type must be 'system' or 'user'")
            
            if doc_type == "user" and not user_id:
                raise ValueError("user_id required for user documents")
            
            # Step 1: Download document
            logger.info(f"[{session_id}] Step 1: Downloading document")
            doc_info = self.document_manager.download_document(
                url=url,
                document_type=doc_type
            )
            
            document_id = doc_info["document_id"]
            filename = doc_info["filename"]
            file_path = self.document_manager.documents_path / filename
            
            # Step 2: Extract and process text
            logger.info(f"[{session_id}] Step 2: Extracting and processing text")
            chunks = self.text_processor.process_pdf(
                file_path,
                chunk_size=chunk_size,
                overlap=chunk_overlap
            )
            
            chunk_count = len(chunks)
            logger.info(f"[{session_id}] Created {chunk_count} chunks")
            
            # Step 3: Generate embeddings
            logger.info(f"[{session_id}] Step 3: Generating embeddings")
            embeddings = self.embeddings_manager.get_embeddings_batch(chunks)
            logger.info(f"[{session_id}] Generated {len(embeddings)} embeddings")
            
            # Step 4: Store in vector database
            logger.info(f"[{session_id}] Step 4: Storing in vector database")
            
            # Create chunk IDs with document reference
            chunk_ids = [f"{document_id}_{i}" for i in range(chunk_count)]
            
            # Create metadata with document and user info
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": i,
                    "doc_type": doc_type,
                    "user_id": user_id or "system",
                    "url": url,
                    "filename": filename,
                    "ingested_at": datetime.now().isoformat()
                }
                for i in range(chunk_count)
            ]
            
            # Add to vector database
            self.vector_db.add_documents(
                texts=chunks,
                ids=chunk_ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            # Step 5: Track document
            self.ingested_documents[document_id] = {
                "url": url,
                "filename": filename,
                "doc_type": doc_type,
                "user_id": user_id,
                "chunks": chunk_count,
                "ingested_at": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            result = {
                "success": True,
                "document_id": document_id,
                "filename": filename,
                "chunks_created": chunk_count,
                "doc_type": doc_type,
                "user_id": user_id,
                "session_id": session_id,
                "message": f"Successfully ingested {chunk_count} chunks from {filename}"
            }
            
            logger.info(f"[{session_id}] Document ingestion complete: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Document ingestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def ingest_document_from_file(self, file_path: Path, doc_type: str = "system",
                                 user_id: Optional[str] = None,
                                 chunk_size: int = 500,
                                 chunk_overlap: int = 100) -> Dict[str, Any]:
        """
        Ingest document from local file
        
        Args:
            file_path: Path to document file
            doc_type: "system" or "user"
            user_id: Owner user ID
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dict: Ingestion result
        """
        try:
            session_id = str(uuid.uuid4())
            logger.info(f"[{session_id}] Starting document ingestion from file: {file_path}")
            
            # Validate
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if doc_type not in ["system", "user"]:
                raise ValueError("doc_type must be 'system' or 'user'")
            
            if doc_type == "user" and not user_id:
                raise ValueError("user_id required for user documents")
            
            # Generate document ID
            import hashlib
            document_id = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
            
            # Step 1: Extract and process text
            logger.info(f"[{session_id}] Step 1: Extracting and processing text")
            chunks = self.text_processor.process_pdf(
                file_path,
                chunk_size=chunk_size,
                overlap=chunk_overlap
            )
            
            chunk_count = len(chunks)
            logger.info(f"[{session_id}] Created {chunk_count} chunks")
            
            # Step 2: Generate embeddings
            logger.info(f"[{session_id}] Step 2: Generating embeddings")
            embeddings = self.embeddings_manager.get_embeddings_batch(chunks)
            logger.info(f"[{session_id}] Generated {len(embeddings)} embeddings")
            
            # Step 3: Store in vector database
            logger.info(f"[{session_id}] Step 3: Storing in vector database")
            
            chunk_ids = [f"{document_id}_{i}" for i in range(chunk_count)]
            
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": i,
                    "doc_type": doc_type,
                    "user_id": user_id or "system",
                    "filename": file_path.name,
                    "ingested_at": datetime.now().isoformat()
                }
                for i in range(chunk_count)
            ]
            
            self.vector_db.add_documents(
                texts=chunks,
                ids=chunk_ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            # Track document
            self.ingested_documents[document_id] = {
                "filename": file_path.name,
                "doc_type": doc_type,
                "user_id": user_id,
                "chunks": chunk_count,
                "ingested_at": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            result = {
                "success": True,
                "document_id": document_id,
                "filename": file_path.name,
                "chunks_created": chunk_count,
                "doc_type": doc_type,
                "user_id": user_id,
                "session_id": session_id,
                "message": f"Successfully ingested {chunk_count} chunks from {file_path.name}"
            }
            
            logger.info(f"[{session_id}] Document ingestion complete: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Document ingestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def get_ingested_documents(self) -> Dict[str, Any]:
        """
        Get list of all ingested documents
        
        Returns:
            Dict: Ingested documents info
        """
        try:
            collection_info = self.vector_db.get_collection_info()
            
            return {
                "total_documents": len(self.ingested_documents),
                "total_chunks": collection_info.get("document_count", 0),
                "documents": self.ingested_documents
            }
            
        except Exception as e:
            logger.error(f"Failed to get ingested documents: {str(e)}")
            return {"error": str(e)}
    
    def clear_all_data(self) -> Dict[str, Any]:
        """
        Clear all documents and embeddings (for testing)
        
        Returns:
            Dict: Clear result
        """
        try:
            logger.warning("Clearing all RAG data")
            
            self.vector_db.clear_collection()
            self.ingested_documents.clear()
            
            return {
                "success": True,
                "message": "All RAG data cleared"
            }
            
        except Exception as e:
            logger.error(f"Failed to clear RAG data: {str(e)}")
            return {"success": False, "error": str(e)}


# Singleton instance
rag_pipeline = RAGPipeline()