"""
This file handles document processing - downloading PDFs and extracting text from them. 
It's the first step of our RAG system.
Document Loader Module
Handles downloading and processing documents
"""

import os
import requests
from pathlib import Path
from typing import List, Optional
from app.config import settings
from app.utils.logger import get_logger
from pypdf import PdfReader
import io

logger = get_logger(__name__)


class DocumentLoader:
    """Load and process documents from URLs"""
    
    def __init__(self, documents_path: Path = settings.DOCUMENTS_PATH):
        self.documents_path = documents_path
        self.documents_path.mkdir(parents=True, exist_ok=True)
    
    def download_document(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download document from URL
        
        Args:
            url: Document URL
            filename: Custom filename (optional)
            
        Returns:
            Path: Local file path
        """
        try:
            logger.info(f"Downloading document from: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract filename from URL if not provided
            if not filename:
                filename = url.split('/')[-1]
                if not filename or '.' not in filename:
                    filename = f"document_{len(os.listdir(self.documents_path))}.pdf"
            
            file_path = self.documents_path / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Document saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download document: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            logger.info(f"Extracting text from: {file_path}")
            
            reader = PdfReader(file_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            
            logger.info(f"Extracted {len(text)} characters from {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 500, 
                   overlap: int = 100) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Full text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(text), step):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks


# Singleton instance
document_loader = DocumentLoader()