"""
Embeddings Module
Generate embeddings using OpenAI API
This file manages generating embeddings using OpenAI's API. Embeddings convert text into vectors (numbers) that represent meaning.
"""

from typing import List
from openai import OpenAI
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingsManager:
    """Manage text embeddings using OpenAI"""
    
    def __init__(self, api_key: str = settings.OPENAI_API_KEY,
                 model: str = settings.EMBEDDING_MODEL):
        """
        Initialize OpenAI embeddings client
        
        Args:
            api_key: OpenAI API key
            model: Embedding model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Embeddings manager initialized with model: {model}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            # Split into batches of 100 (OpenAI limit)
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                
                # Sort by index to maintain order
                embeddings = sorted(response.data, key=lambda x: x.index)
                all_embeddings.extend([e.embedding for e in embeddings])
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise


# Singleton instance
embeddings_manager = EmbeddingsManager()