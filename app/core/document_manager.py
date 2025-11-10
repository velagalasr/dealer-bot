"""
Document Manager Module
Manages document lifecycle - download, store, delete, list
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
    """Manage documents - download, store, delete, list"""
    
    def __init__(self, documents_path: Path = settings.DOCUMENTS_PATH):
        """
        Initialize document manager
        
        Args:
            documents_path: Path to store documents
        """
        self.documents_path = documents_path
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.documents_path / "documents_metadata.json"
        
        logger.info(f"Document manager initialized at {documents_path}")
    
    def download_document(self, url: str, document_type: str = "manual",
                         filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Download document from URL
        
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
            
            # Save file
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
                "status": "downloaded"
            }
            
            logger.info(f"Document saved: {doc_id} -> {filename}")
            return doc_info
            
        except Exception as e:
            logger.error(f"Failed to download document: {str(e)}")
            raise
    
    def get_document_path(self, document_id: str) -> Optional[Path]:
        """
        Get path to document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Path: Path to document file
        """
        try:
            # Search for document with this ID
            for file in self.documents_path.glob("*"):
                if file.is_file() and file.name != "documents_metadata.json":
                    return file
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document path: {str(e)}")
            return None
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all downloaded documents
        
        Returns:
            List: List of document info
        """
        try:
            documents = []
            
            for file in self.documents_path.glob("*"):
                if file.is_file() and file.name != "documents_metadata.json":
                    doc_info = {
                        "filename": file.name,
                        "file_size": file.stat().st_size,
                        "modified_at": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    }
                    documents.append(doc_info)
            
            logger.info(f"Listed {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    def delete_document(self, filename: str) -> bool:
        """
        Delete document
        
        Args:
            filename: Document filename
            
        Returns:
            bool: Success status
        """
        try:
            file_path = self.documents_path / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted document: {filename}")
                return True
            else:
                logger.warning(f"Document not found: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    def get_document_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get document information
        
        Args:
            filename: Document filename
            
        Returns:
            Dict: Document info
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