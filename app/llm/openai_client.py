"""
OpenAI Client Module
Using LangChain for better error handling and retries
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from app.config import settings
from app.utils.logger import get_logger
import os

logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI client using LangChain"""
    
    def __init__(self):
        """Initialize OpenAI client with LangChain"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("OPENAI_API_KEY not set")
        
        # LangChain ChatOpenAI with built-in retries!
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-4",
            temperature=0.7,
            max_retries=3,  # Built-in retry logic!
            timeout=30
        )
        
        logger.info("OpenAI client initialized with LangChain")
    
    def generate_response(self, messages: List[Dict], temperature: float = 0.7,
                         max_tokens: int = 1000) -> str:
        """
        Generate response using LangChain
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation
            max_tokens: Max tokens to generate
            
        Returns:
            str: Generated response text
        """
        try:
            logger.info(f"Generating response with {len(messages)} messages")
            
            # Convert to LangChain message format
            langchain_messages = []
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
            
            # Create LLM with custom temperature and max_tokens
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=3  # Retry on failure!
            )
            
            # Generate response
            response = llm.invoke(langchain_messages)
            
            logger.info(f"Response generated: {len(response.content)} chars")
            return response.content
            
        except Exception as e:
            logger.error(f"OpenAI Error: {type(e).__name__}: {str(e)}")
            raise


# Singleton instance
openai_client = OpenAIClient()