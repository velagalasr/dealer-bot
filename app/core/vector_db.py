"""
Vector Database Module
Manages embeddings storage and retrieval using Chroma
"""

from typing import List, Optional, Dict, Any
import chromadb
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorDatabase:
    """Manage vector embeddings with Chroma"""
    
    def __init__(self, persist_directory: str = settings.CHROMA_DB_PATH):
        """
        Initialize Chroma vector database
        
        Args:
            persist_directory: Path to persist Chroma database
        """
        try:
            self.persist_directory = persist_directory
            
            # Initialize Chroma client with new API (PersistentClient)
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="dealer_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Vector database initialized at {persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            raise
    
    def add_documents(self, texts: List[str], ids: List[str], 
                     embeddings: List[List[float]], 
                     metadatas: Optional[List[Dict]] = None) -> None:
        """
        Add documents and embeddings to collection
        
        Args:
            texts: List of text chunks
            ids: Unique IDs for each chunk
            embeddings: Pre-computed embeddings
            metadatas: Optional metadata for each chunk
        """
        try:
            if metadatas is None:
                metadatas = [{"source": "document"} for _ in texts]
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(texts)} documents to vector database")
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector database: {str(e)}")
            raise
    
    def query(self, embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        """
        Query similar documents
        
        Args:
            embedding: Query embedding vector
            n_results: Number of results to return
            
        Returns:
            Dict: Query results with documents and distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                include=["documents", "distances", "metadatas"]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query vector database: {str(e)}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                "name": self.collection.name,
                "document_count": count,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {}
    
    def clear_collection(self) -> None:
        """Clear all documents from collection (for testing)"""
        try:
            self.client.delete_collection(name="dealer_documents")
            self.collection = self.client.get_or_create_collection(
                name="dealer_documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            raise


# Singleton instance
vector_db = VectorDatabase()