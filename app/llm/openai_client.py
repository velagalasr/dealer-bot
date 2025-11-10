"""
OpenAI Client Module
This file is a wrapper around OpenAI's API - makes it easier to use OpenAI in our project. 
It handles text generation, classification, and summarization.
"""

from typing import List, Dict, Optional
from openai import OpenAI
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API"""
    
    def __init__(self, api_key: str = settings.OPENAI_API_KEY,
                 model: str = settings.OPENAI_MODEL):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default from config)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        
        logger.info(f"OpenAI client initialized with model: {model}")
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         temperature: Optional[float] = None,
                         max_tokens: Optional[int] = None) -> str:
        """
        Generate response using GPT
        
        Args:
            messages: Chat messages (with roles and content)
            temperature: Temperature for sampling
            max_tokens: Maximum tokens in response
            
        Returns:
            str: Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise
    
    def classify_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """
        Classify text into categories
        
        Args:
            text: Text to classify
            categories: List of possible categories
            
        Returns:
            Dict: Category scores
        """
        try:
            prompt = f"""Classify the following text into one of these categories: {', '.join(categories)}
            
Text: {text}

Respond with ONLY the category name, nothing else."""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.generate_response(messages, temperature=0.1, max_tokens=50)
            
            return {"classified_as": response.strip()}
            
        except Exception as e:
            logger.error(f"Failed to classify text: {str(e)}")
            raise
    
    def summarize(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            str: Summary
        """
        try:
            prompt = f"""Summarize the following text in maximum {max_length} characters:

{text}

Provide only the summary, no additional text."""
            
            messages = [{"role": "user", "content": prompt}]
            return self.generate_response(messages, temperature=0.7, max_tokens=100)
            
        except Exception as e:
            logger.error(f"Failed to summarize text: {str(e)}")
            raise


# Singleton instance
openai_client = OpenAIClient()