"""
Retriever Module
This file handles semantic search - finding relevant documents based on meaning.
It uses embeddings and the vector database to retrieve information.
"""

from typing import List, Dict, Any
from app.core.embeddings import embeddings_manager
from app.core.vector_db import vector_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SemanticRetriever:
    """Retrieve relevant documents using semantic search"""
    
    def __init__(self, embeddings_manager=embeddings_manager, 
                 vector_db=vector_db):
        """
        Initialize retriever
        
        Args:
            embeddings_manager: EmbeddingsManager instance
            vector_db: VectorDatabase instance
        """
        self.embeddings_manager = embeddings_manager
        self.vector_db = vector_db
    
    def retrieve(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query text
            n_results: Number of documents to return
            
        Returns:
            List[Dict]: Retrieved documents with scores
        """
        try:
            logger.info(f"Retrieving documents for query: {query[:100]}")
            
            # Generate embedding for query
            query_embedding = self.embeddings_manager.get_embedding(query)
            
            # Query vector database
            results = self.vector_db.query(query_embedding, n_results=n_results)
            
            # Format results
            retrieved_docs = []
            
            if results["documents"] and results["documents"][0]:
                for i, (doc, distance, metadata) in enumerate(
                    zip(results["documents"][0], 
                        results["distances"][0],
                        results["metadatas"][0])
                ):
                    # Convert distance to similarity score (cosine similarity)
                    similarity = 1 - distance
                    
                    retrieved_docs.append({
                        "rank": i + 1,
                        "document": doc,
                        "score": similarity,
                        "metadata": metadata
                    })
            
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            raise
    
    def retrieve_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        Retrieve specific documents by ID
        
        Args:
            ids: Document IDs to retrieve
            
        Returns:
            Dict: Retrieved documents
        """
        try:
            results = self.vector_db.collection.get(ids=ids)
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents by IDs: {str(e)}")
            raise


# Singleton instance
retriever = SemanticRetriever()