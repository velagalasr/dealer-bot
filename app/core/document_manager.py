"""
Document Manager Module
Manages document file operations (download, store, delete, list)
Note: Document ingestion (chunking, embedding, Chroma storage) is handled by rag_pipeline
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import requests
import hashlib
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentManager:
    """Manage document files - download, store, delete, list"""
    
    def __init__(self, documents_path: Path = settings.DOCUMENTS_PATH):
        """
        Initialize document manager
        
        Args:
            documents_path: Path to store documents
        """
        self.documents_path = Path(documents_path)
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Document manager initialized at {self.documents_path}")
    
    def download_document(self, url: str, document_type: str = "manual",
                         filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Download document from URL and save to disk
        
        NOTE: After downloading, document must be ingested through rag_pipeline
              to be indexed in Chroma and searchable by RAG
        
        Args:
            url: Document URL
            document_type: Type of document (manual, guide, spec, etc.)
            filename: Custom filename (optional)
            
        Returns:
            Dict: Document info including ID and path
        """
        try:
            logger.info(f"Downloading document from: {url}")
            
            # Download file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Generate filename if not provided
            if not filename:
                filename = url.split('/')[-1]
                if not filename or '.' not in filename:
                    filename = f"document_{datetime.now().timestamp()}.pdf"
            
            # Generate document ID
            doc_id = hashlib.md5(url.encode()).hexdigest()[:12]
            
            # Save file to disk
            file_path = self.documents_path / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Create metadata
            doc_info = {
                "document_id": doc_id,
                "filename": filename,
                "url": url,
                "document_type": document_type,
                "file_size": len(response.content),
                "downloaded_at": datetime.now().isoformat(),
                "status": "downloaded",
                "file_path": str(file_path),
                "note": "Document saved to disk. Must be ingested via rag_pipeline for RAG search."
            }
            
            logger.info(f"✅ Document saved: {doc_id} -> {filename}")
            return doc_info
            
        except Exception as e:
            logger.error(f"Failed to download document: {str(e)}")
            raise
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Save uploaded file to disk
        
        NOTE: After saving, document must be ingested through rag_pipeline
              to be indexed in Chroma and searchable by RAG
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Dict: File info
        """
        try:
            logger.info(f"Saving uploaded file: {filename}")
            
            # Generate document ID
            doc_id = hashlib.md5(filename.encode()).hexdigest()[:12]
            
            # Save file
            file_path = self.documents_path / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            doc_info = {
                "document_id": doc_id,
                "filename": filename,
                "file_size": len(file_content),
                "saved_at": datetime.now().isoformat(),
                "file_path": str(file_path),
                "status": "saved",
                "note": "Document saved to disk. Must be ingested via rag_pipeline for RAG search."
            }
            
            logger.info(f"✅ File saved: {doc_id} -> {filename}")
            return doc_info
            
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise
    
    def get_document_path(self, filename: str) -> Optional[Path]:
        """
        Get full path to document file
        
        Args:
            filename: Document filename
            
        Returns:
            Path: Path to document file or None
        """
        try:
            file_path = self.documents_path / filename
            if file_path.exists() and file_path.is_file():
                return file_path
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document path: {str(e)}")
            return None
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all stored document files
        
        Returns:
            List: List of file information
        """
        try:
            documents = []
            
            for file in self.documents_path.glob("*"):
                if file.is_file():
                    doc_info = {
                        "filename": file.name,
                        "file_size": file.stat().st_size,
                        "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                        "path": str(file)
                    }
                    documents.append(doc_info)
            
            logger.info(f"✅ Listed {len(documents)} files on disk")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    def delete_document(self, filename: str) -> bool:
        """
        Delete document file
        
        Args:
            filename: Document filename
            
        Returns:
            bool: Success status
        """
        try:
            file_path = self.documents_path / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"✅ Deleted file: {filename}")
                return True
            else:
                logger.warning(f"File not found: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    def get_document_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed file information
        
        Args:
            filename: Document filename
            
        Returns:
            Dict: File information
        """
        try:
            file_path = self.documents_path / filename
            
            if file_path.exists():
                return {
                    "filename": filename,
                    "file_size": file_path.stat().st_size,
                    "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "path": str(file_path)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document info: {str(e)}")
            return None


# Singleton instance
document_manager = DocumentManager()