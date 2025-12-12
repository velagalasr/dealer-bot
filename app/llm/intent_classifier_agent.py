"""
Intent Classifier Agent
Rules + LLM hybrid with confidence-based decision making
"""

from typing import Dict, Tuple, List, Optional
from app.llm.openai_client import openai_client
from app.utils.logger import get_logger
import re

logger = get_logger(__name__)


class IntentClassifierAgent:
    """Intelligent intent classification with confidence scoring"""
    
    def __init__(self, openai_client=openai_client):
        """Initialize intent classifier agent"""
        self.openai_client = openai_client
        
        # Define intents and specialists
        self.intents = {
            "product_inquiry": {"description": "Questions about products", "specialist": "product_agent"},
            "technical_support": {"description": "Technical issues and troubleshooting", "specialist": "tech_agent"},
            "maintenance": {"description": "Maintenance and service procedures", "specialist": "maintenance_agent"},
            "warranty": {"description": "Warranty and service terms", "specialist": "warranty_agent"},
            "anomaly_concern": {"description": "Fraud, security, suspicious activity", "specialist": "anomaly_detection_agent"},
            "general": {"description": "General questions", "specialist": "general_agent"}
        }
        
        # Define keywords for rules-based classification
        self.keyword_rules = {
            "product_inquiry": [
                "product", "features", "specifications", "model", "version",
                "compare", "difference", "which", "best", "available"
            ],
            "technical_support": [
                "error", "issue", "problem", "broken", "crash", "fail",
                "bug", "fix", "troubleshoot", "debug", "not working"
            ],
            "maintenance": [
                "maintenance", "service", "schedule", "routine", "preventive",
                "check", "inspection", "calibration", "replace", "change"
            ],
            "warranty": [
                "warranty", "guarantee", "coverage", "claim", "protection",
                "covered", "expired", "term", "condition", "valid"
            ],
            "anomaly_concern": [
                "fraud", "flagged", "suspicious", "hacked", "compromised",
                "unauthorized", "breach", "security", "attack", "malicious",
                "unusual", "strange", "weird activity", "account locked"
            ],
            "general": []
        }
        
        # Confidence thresholds
        self.confidence_high = 0.8      # Use rule result
        self.confidence_medium = 0.5   # Verify with LLM
        self.confidence_low = 0.5      # Call LLM for decision
        
        logger.info("Intent classifier agent initialized")
    
    def classify(self, query: str, session_id: str = None,
                 user_history: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Classify query intent with confidence scoring
        
        Uses rules first, then LLM based on confidence
        
        Args:
            query: User query
            session_id: Session ID for tracking
            user_history: Previous queries for context
            
        Returns:
            Dict: Intent classification with confidence and factors
        """
        try:
            logger.info(f"[{session_id}] Classifying intent for: {query[:100]}")
            
            # Step 1: Rules-based classification
            rules_result = self._rules_based_classify(query)
            rules_intent = rules_result["intent"]
            rules_confidence = rules_result["confidence"]
            rules_factors = rules_result["factors"]
            
            logger.info(f"[{session_id}] Rules confidence: {rules_confidence:.2f}")
            
            # Step 2: Decide if we need LLM verification
            llm_result = None
            final_confidence = rules_confidence
            final_factors = rules_factors
            
            if rules_confidence < self.confidence_high:
                logger.info(f"[{session_id}] Confidence below {self.confidence_high}, calling LLM")
                
                llm_result = self._llm_classify(query, rules_intent)
                llm_intent = llm_result["intent"]
                llm_confidence = llm_result["confidence"]
                
                # Combine results
                if llm_confidence > rules_confidence:
                    final_intent = llm_intent
                    final_confidence = llm_confidence
                    final_factors = {**rules_factors, **llm_result["factors"]}
                    logger.info(f"[{session_id}] LLM confidence higher: {llm_confidence:.2f}")
                else:
                    final_intent = rules_intent
                    final_confidence = rules_confidence
                    logger.info(f"[{session_id}] Keeping rules confidence: {rules_confidence:.2f}")
            else:
                final_intent = rules_intent
                logger.info(f"[{session_id}] Confidence sufficient, using rules: {rules_confidence:.2f}")
            
            # Step 3: Get specialist
            specialist = self.intents.get(final_intent, {}).get("specialist", "general_agent")
            
            result = {
                "intent": final_intent,
                "confidence": final_confidence,
                "specialist": specialist,
                "classification_method": "rules" if llm_result is None else "hybrid",
                "factors": final_factors,
                "session_id": session_id
            }
            
            logger.info(f"[{session_id}] Classification complete: intent={final_intent}, confidence={final_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Classification failed: {str(e)}")
            return {
                "intent": "general",
                "confidence": 0.0,
                "specialist": "general_agent",
                "classification_method": "error",
                "factors": {"error": str(e)},
                "session_id": session_id
            }
    
    def _rules_based_classify(self, query: str) -> Dict[str, any]:
        """
        Classify using rules and keywords
        
        Factors considered:
        - Keywords matching
        - Domain detection
        - Message length
        - Query structure
        
        Args:
            query: User query
            
        Returns:
            Dict: Intent, confidence, factors
        """
        try:
            query_lower = query.lower()
            intent_scores = {}
            factors = {}
            
            # Factor 0: Keyword matching
            for intent, keywords in self.keyword_rules.items():
                matches = sum(1 for keyword in keywords if keyword in query_lower)
                intent_scores[intent] = matches / len(keywords) if keywords else 0
            

            # Factor 1: Check for anomaly keywords FIRST (highest priority)
            anomaly_keywords = self.keyword_rules.get("anomaly_concern", [])
            anomaly_matches = sum(1 for keyword in anomaly_keywords if keyword in query_lower)
            anomaly_score = anomaly_matches / len(anomaly_keywords) if anomaly_keywords else 0

            # If anomaly detected, return immediately with high confidence
            if anomaly_score > 0.2:  # Even one anomaly keyword detected
                logger.info(f"Anomaly keywords detected: {anomaly_score:.2f}")
                return {
                    "intent": "anomaly_concern",
                    "confidence": 0.9 + (anomaly_score * 0.1),  # High confidence
                    "factors": {
                        "anomaly_keywords_found": [kw for kw in anomaly_keywords if kw in query_lower],
                        "anomaly_score": anomaly_score,
                        "query_length": len(query),
                        "reason": "Security/fraud-related query detected"
                    }
                }

            # Factor 2: Message length
            query_length = len(query)
            length_factor = min(query_length / 100, 1.0)  # Normalize to 0-1
            
            # Factor 3: Query structure
            has_question = "?" in query
            has_imperative = any(query.startswith(w) for w in ["how", "what", "why", "when", "where", "who"])
            
            # Calculate confidence for each intent
            best_intent = "general"
            best_confidence = 0.0
            
            for intent, keyword_score in intent_scores.items():
                structure_bonus = 0.1 if (has_question or has_imperative) else 0
                combined_score = (keyword_score * 0.7) + (length_factor * 0.2) + structure_bonus
                
                if combined_score > best_confidence:
                    best_confidence = combined_score
                    best_intent = intent
            
            # If no strong match, default to general
            if best_confidence < 0.3:
                best_intent = "general"
                best_confidence = 0.5
            
            factors = {
                "keyword_match": intent_scores,
                "query_length": query_length,
                "has_question": has_question,
                "has_imperative": has_imperative
            }
            
            logger.debug(f"Rules classification: {best_intent} ({best_confidence:.2f})")
            
            return {
                "intent": best_intent,
                "confidence": best_confidence,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"Rules classification failed: {str(e)}")
            return {
                "intent": "general",
                "confidence": 0.5,
                "factors": {"error": str(e)}
            }
    
    def _llm_classify(self, query: str, rules_intent: str) -> Dict[str, any]:
        """
        Classify using LLM for verification/refinement
        
        Args:
            query: User query
            rules_intent: Intent from rules classifier
            
        Returns:
            Dict: Intent, confidence, factors
        """
        try:
            intent_descriptions = "\n".join([
                f"- {name}: {info['description']}"
                for name, info in self.intents.items()
            ])
            
            prompt = f"""Analyze the user query and classify it into ONE of these intents:

{intent_descriptions}

The rules-based classifier suggested: {rules_intent}

User Query: "{query}"

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "intent": "[intent_name]",
  "confidence": [0.0-1.0],
  "reasoning": "[brief reason]"
}}"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.openai_client.generate_response(
                messages, temperature=0.3, max_tokens=100
            )
            
            # Parse JSON response
            import json
            response_data = json.loads(response)
            
            intent = response_data.get("intent", "general")
            confidence = response_data.get("confidence", 0.5)
            reasoning = response_data.get("reasoning", "")
            
            # Validate intent
            if intent not in self.intents:
                intent = "general"
            
            factors = {
                "llm_reasoning": reasoning,
                "rules_suggestion": rules_intent
            }
            
            logger.debug(f"LLM classification: {intent} ({confidence:.2f})")
            
            return {
                "intent": intent,
                "confidence": confidence,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"LLM classification failed: {str(e)}")
            return {
                "intent": "general",
                "confidence": 0.5,
                "factors": {"error": str(e)}
            }
    
    def get_specialist(self, intent: str) -> str:
        """Get specialist for intent"""
        return self.intents.get(intent, {}).get("specialist", "general_agent")


# Singleton instance
intent_classifier_agent = IntentClassifierAgent()