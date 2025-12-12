"""
Text Processor Module
Extract, clean, and chunk text for embedding
"""

from typing import List, Dict, Any
from pathlib import Path
import re
from pypdf import PdfReader
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TextProcessor:
    """Process text - extract, clean, chunk"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize text processor
        
        Args:
            chunk_size: Size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(f"Text processor initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            logger.info(f"Extracting text from PDF: {file_path}")
            
            reader = PdfReader(file_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                # Add page marker
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            
            char_count = len(text)
            logger.info(f"Extracted {char_count} characters from {len(reader.pages)} pages")
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            str: Cleaned text
        """
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\[\]\{\}]', '', text)
            
            # Remove extra spaces around punctuation
            text = re.sub(r'\s+([.,;:])', r'\1', text)
            text = re.sub(r'([.,;:])\s+', r'\1 ', text)
            
            # Normalize newlines
            text = text.strip()
            
            logger.debug(f"Cleaned text: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Failed to clean text: {str(e)}")
            return text
    
    def chunk_text(self, text: str, chunk_size: int = None, 
                   overlap: int = None) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Full text to chunk
            chunk_size: Size of each chunk (uses default if None)
            overlap: Overlap between chunks (uses default if None)
            
        Returns:
            List[str]: List of text chunks
        """
        try:
            chunk_size = chunk_size or self.chunk_size
            overlap = overlap or self.chunk_overlap
            
            if chunk_size <= overlap:
                logger.warning("Chunk size <= overlap, adjusting overlap")
                overlap = chunk_size // 2
            
            chunks = []
            step = chunk_size - overlap
            
            # Create chunks with overlap
            for i in range(0, len(text), step):
                chunk = text[i:i + chunk_size]
                
                if chunk.strip():  # Only add non-empty chunks
                    chunks.append(chunk)
            
            logger.info(f"Created {len(chunks)} chunks from text "
                       f"(size: {chunk_size}, overlap: {overlap})")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text: {str(e)}")
            raise
    
    def process_pdf(self, file_path: Path, chunk_size: int = None,
                   overlap: int = None) -> List[str]:
        """
        Complete pipeline: extract → clean → chunk
        
        Args:
            file_path: Path to PDF file
            chunk_size: Custom chunk size (optional)
            overlap: Custom overlap (optional)
            
        Returns:
            List[str]: List of processed chunks
        """
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Step 1: Extract text
            text = self.extract_text_from_pdf(file_path)
            
            # Step 2: Clean text
            text = self.clean_text(text)
            
            # Step 3: Chunk text
            chunks = self.chunk_text(text, chunk_size, overlap)
            
            logger.info(f"PDF processing complete: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process PDF: {str(e)}")
            raise
    
    def process_text(self, text: str, chunk_size: int = None,
                    overlap: int = None) -> List[str]:
        """
        Process plain text (no PDF extraction)
        
        Args:
            text: Plain text to process
            chunk_size: Custom chunk size (optional)
            overlap: Custom overlap (optional)
            
        Returns:
            List[str]: List of processed chunks
        """
        try:
            logger.info(f"Processing plain text ({len(text)} chars)")
            
            # Step 1: Clean text
            text = self.clean_text(text)
            
            # Step 2: Chunk text
            chunks = self.chunk_text(text, chunk_size, overlap)
            
            logger.info(f"Text processing complete: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process text: {str(e)}")
            raise
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)
        
        Args:
            text: Text to estimate
            
        Returns:
            int: Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        # Or 1 token ≈ 0.75 words
        words = len(text.split())
        estimated_tokens = int(words / 0.75)
        return estimated_tokens


# Singleton instance
text_processor = TextProcessor()