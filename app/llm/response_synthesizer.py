"""
Response Synthesizer Module
Generate final responses using LLM and retrieved documents
"""

from typing import List, Dict, Any
from app.llm.openai_client import openai_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseSynthesizer:
    """Synthesize responses using LLM and context documents"""
    
    def __init__(self, openai_client=openai_client):
        """
        Initialize synthesizer
        
        Args:
            openai_client: OpenAI client instance
        """
        self.openai_client = openai_client
    
    def synthesize(self, query: str, context_documents: List[Dict[str, Any]], 
                   intent: str = "general") -> str:
        """
        Synthesize response from query and context documents
        
        Args:
            query: User query
            context_documents: Retrieved context documents
            intent: User intent (for context)
            
        Returns:
            str: Generated response
        """
        try:
            # Prepare context
            context_text = self._prepare_context(context_documents)
            
            # Build prompt
            prompt = self._build_prompt(query, context_text, intent)
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.openai_client.generate_response(
                messages, temperature=0.7, max_tokens=1000
            )
            
            logger.info("Response synthesized successfully")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to synthesize response: {str(e)}")
            return "I apologize, but I encountered an error while processing your query."
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Prepare context from retrieved documents
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            str: Formatted context text
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            score = doc.get("score", 0)
            content = doc.get("document", "")
            
            context_parts.append(f"Document {i} (relevance: {score:.2f}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str, intent: str) -> str:
        """
        Build prompt for response generation
        
        Args:
            query: User query
            context: Context documents
            intent: User intent
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"""You are a helpful and knowledgeable assistant.

Based on the following context documents, please answer the user's question comprehensively and accurately.

CONTEXT DOCUMENTS:
{context}

USER QUESTION: {query}

Please provide:
1. A clear and helpful answer based on the context
2. Specific details and examples if available
3. Any important warnings or precautions if relevant
4. Next steps or recommendations if applicable

If the answer is not fully covered in the context, you may supplement with general knowledge, but clearly indicate what is from the provided documents and what is general knowledge."""
        
        return prompt


# Singleton instance
response_synthesizer = ResponseSynthesizer()