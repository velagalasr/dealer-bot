"""
Intent Classifier Module
Classify user queries into intents
"""

from typing import Dict, Tuple
from app.llm.openai_client import openai_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Define intents and specialists
INTENTS = {
    "product_inquiry": {"description": "Questions about products", "specialist": "product_agent"},
    "technical_support": {"description": "Technical issues and troubleshooting", "specialist": "tech_agent"},
    "maintenance": {"description": "Maintenance and service procedures", "specialist": "maintenance_agent"},
    "warranty": {"description": "Warranty and service terms", "specialist": "warranty_agent"},
    "general": {"description": "General questions", "specialist": "general_agent"}
}


class IntentClassifier:
    """Classify user queries into predefined intents"""
    
    def __init__(self, openai_client=openai_client):
        """
        Initialize classifier
        
        Args:
            openai_client: OpenAI client instance
        """
        self.openai_client = openai_client
        self.intents = INTENTS
    
    def classify(self, query: str) -> Tuple[str, float]:
        """
        Classify query into an intent
        
        Args:
            query: User query
            
        Returns:
            Tuple: (intent, confidence score)
        """
        try:
            intent_names = list(self.intents.keys())
            intent_descriptions = "\n".join([
                f"- {name}: {self.intents[name]['description']}"
                for name in intent_names
            ])
            
            prompt = f"""Classify the following user query into ONE of these intents:

{intent_descriptions}

User Query: "{query}"

Respond with ONLY the intent name (one word), nothing else."""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.openai_client.generate_response(
                messages, temperature=0.1, max_tokens=10
            )
            
            intent = response.strip().lower()
            
            # Validate intent
            if intent not in intent_names:
                logger.warning(f"Unrecognized intent: {intent}, defaulting to 'general'")
                intent = "general"
            
            confidence = 0.85  # Placeholder
            logger.info(f"Classified query as: {intent} (confidence: {confidence})")
            
            return intent, confidence
            
        except Exception as e:
            logger.error(f"Failed to classify intent: {str(e)}")
            return "general", 0.0
    
    def get_specialist(self, intent: str) -> str:
        """
        Get specialist agent for intent
        
        Args:
            intent: Intent name
            
        Returns:
            str: Specialist agent name
        """
        return self.intents.get(intent, {}).get("specialist", "general_agent")


# Singleton instance
intent_classifier = IntentClassifier()