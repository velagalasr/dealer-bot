"""
Agent Orchestrator Module
Coordinates 4 intelligent agents for query processing
"""

from typing import Dict, Any, Optional
from app.llm.intent_classifier_agent import intent_classifier_agent
from app.security.anomaly_detection_agent import anomaly_detection_agent
from app.core.rag_agent import rag_agent
from app.llm.response_synthesis_agent import response_synthesis_agent
from app.utils.logger import get_logger
import uuid

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrate 4 intelligent agents for complete query processing"""
    
    def __init__(self, intent_classifier_agent=intent_classifier_agent,
                 anomaly_detection_agent=anomaly_detection_agent,
                 rag_agent=rag_agent,
                 response_synthesis_agent=response_synthesis_agent):
        """
        Initialize orchestrator with 4 agents
        
        Args:
            intent_classifier_agent: Intent classification agent
            anomaly_detection_agent: Anomaly detection agent
            rag_agent: RAG retrieval agent
            response_synthesis_agent: Response synthesis agent
        """
        self.intent_classifier_agent = intent_classifier_agent
        self.anomaly_detection_agent = anomaly_detection_agent
        self.rag_agent = rag_agent
        self.response_synthesis_agent = response_synthesis_agent
    
    def process_query(self, query: str, session_id: str = None,
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process query through all 4 agents
        
        Flow:
        1. Intent Classifier Agent - Determine intent (rules + LLM)
        2. Anomaly Detection Agent - Analyze for anomalies (with document search)
        3. RAG Agent - Retrieve relevant documents
        4. Response Synthesis Agent - Generate final response
        
        Args:
            query: User query
            session_id: Session ID for tracking
            user_id: User ID (for filtering documents)
            
        Returns:
            Dict: Complete response with all agent outputs
        """
        try:
            session_id = session_id or str(uuid.uuid4())
            logger.info(f"[{session_id}] ========== QUERY PROCESSING START ==========")
            logger.info(f"[{session_id}] Query: {query[:100]}")
            
            # ========== AGENT 1: INTENT CLASSIFIER AGENT ==========
            logger.info(f"[{session_id}] --- AGENT 1: Intent Classification ---")
            intent_result = self.intent_classifier_agent.classify(
                query=query,
                session_id=session_id
            )
            
            intent = intent_result.get("intent", "general")
            specialist = intent_result.get("specialist", "general_agent")
            intent_confidence = intent_result.get("confidence", 0.0)
            
            logger.info(f"[{session_id}] Intent: {intent} ({intent_confidence:.2f})")
            logger.info(f"[{session_id}] Specialist: {specialist}")
            logger.info(f"[{session_id}] Classification method: {intent_result.get('classification_method')}")
            
            # ========== AGENT 2: ANOMALY DETECTION AGENT ==========
            logger.info(f"[{session_id}] --- AGENT 2: Anomaly Detection ---")

            # Special handling for anomaly_concern intent
            if intent == "anomaly_concern":
                logger.info(f"[{session_id}] Query is about anomaly concern - searching for guidance documents")
                
                # Search for relevant guidance documents
                guidance_search = self.rag_agent.retrieve_and_rank(
                    query=f"fraud detection account security prevention unauthorized access {query}",
                    session_id=session_id,
                    n_results=3,
                    user_id=user_id,
                    doc_type="system"
                )
                
                guidance_documents = guidance_search.get("documents", []) if guidance_search.get("success") else []
                
                anomaly_result = {
                    "is_anomalous": True,
                    "risk_score": 0.5,
                    "confidence_score": intent_confidence,
                    "risk_level": "medium",
                    "anomaly_factors": [f"CONCERN: {intent}"],
                    "anomaly_count": 1,
                    "risk_components": {"user_concern": 0.5},
                    "decision": "REVIEW",
                    "guidance_documents": guidance_documents,
                    "session_id": session_id,
                    "timestamp": None
                }
                
                logger.info(f"[{session_id}] Found {len(guidance_documents)} guidance documents for concern")
            else:
                # Normal malicious query detection
                anomaly_result = self.anomaly_detection_agent.analyze(
                    query=query,
                    session_id=session_id
                )
            
            risk_score = anomaly_result.get("risk_score", 0.0)
            risk_level = anomaly_result.get("risk_level", "low")
            anomaly_decision = anomaly_result.get("decision", "ALLOW")
            is_anomalous = anomaly_result.get("is_anomalous", False)
            guidance_documents = anomaly_result.get("guidance_documents", [])
            
            logger.info(f"[{session_id}] Risk Score: {risk_score:.2f} ({risk_level})")
            logger.info(f"[{session_id}] Decision: {anomaly_decision}")
            logger.info(f"[{session_id}] Anomalous: {is_anomalous}")
            logger.info(f"[{session_id}] Guidance documents: {len(guidance_documents)}")
            
            # ========== DECISION: BLOCK? ==========
            if anomaly_decision == "BLOCK":
                logger.warning(f"[{session_id}] Query BLOCKED - High risk")
                return {
                    "query": query,
                    "response": "Your query has been flagged for security concerns and cannot be processed. Please contact support for assistance.",
                    "intent": intent,
                    "confidence": intent_confidence,
                    "specialist": specialist,
                    "sources": [],
                    "session_id": session_id,
                    "anomaly_info": {
                        "blocked": True,
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                        "anomalies": anomaly_result.get("anomaly_factors", [])
                    },
                    "agent_pipeline": "Intent -> Anomaly -> BLOCKED"
                }
            
            # ========== AGENT 3: RAG AGENT ==========
            logger.info(f"[{session_id}] --- AGENT 3: RAG Retrieval ---")

            # Skip RAG if anomaly_concern (already retrieved guidance docs in Agent 2)
            if intent == "anomaly_concern":
                logger.info(f"[{session_id}] Anomaly concern - using guidance documents from Agent 2")
                rag_documents = anomaly_result.get("guidance_documents", [])
                rag_result = {
                    "success": True,
                    "documents": rag_documents,
                    "confidence": intent_confidence,
                    "retrieval_stats": {
                        "retrieved": len(rag_documents),
                        "after_filtering": len(rag_documents),
                        "returned": len(rag_documents),
                        "avg_similarity": 0.85
                    }
                }
            else:
                # Normal RAG retrieval
                search_query = query
                rag_result = self.rag_agent.retrieve_and_rank(
                    query=search_query,
                    session_id=session_id,
                    n_results=5,
                    user_id=user_id,
                    doc_type="system"
                )
            
            rag_documents = rag_result.get("documents", []) if rag_result.get("success") else []
            rag_confidence = rag_result.get("confidence", 0.0)
            
            logger.info(f"[{session_id}] Retrieved: {len(rag_documents)} documents")
            logger.info(f"[{session_id}] RAG confidence: {rag_confidence:.2f}")
            
            # ========== AGENT 4: RESPONSE SYNTHESIS AGENT ==========
            logger.info(f"[{session_id}] --- AGENT 4: Response Synthesis ---")
            
            response_result = self.response_synthesis_agent.synthesize(
                query=query,
                intent=intent_result,
                anomaly_info=anomaly_result,
                rag_documents=rag_documents,
                session_id=session_id
            )
            
            response_text = response_result.get("response", "")
            response_strategy = response_result.get("response_strategy", "unknown")
            
            logger.info(f"[{session_id}] Response strategy: {response_strategy}")
            logger.info(f"[{session_id}] Response length: {len(response_text)} chars")
            
            # ========== BUILD FINAL RESULT ==========
            result = {
                "query": query,
                "response": response_text,
                "intent": intent,
                "confidence": intent_confidence,
                "specialist": specialist,
                "sources": rag_documents,
                "session_id": session_id,
                "agent_pipeline": "Intent -> Anomaly -> RAG -> Synthesis",
                
                # Intent classifier details
                "intent_details": {
                    "method": intent_result.get("classification_method"),
                    "factors": intent_result.get("factors", {})
                },
                
                # Anomaly detection details
                "anomaly_info": {
                    "is_anomalous": is_anomalous,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "decision": anomaly_decision,
                    "factors": anomaly_result.get("anomaly_factors", []),
                    "guidance_used": len(guidance_documents) > 0
                },
                
                # RAG details
                "retrieval_info": {
                    "documents_retrieved": len(rag_documents),
                    "retrieval_confidence": rag_confidence,
                    "retrieval_stats": rag_result.get("retrieval_stats", {})
                },
                
                # Response synthesis details
                "synthesis_info": {
                    "strategy": response_strategy,
                    "context_sources": response_result.get("context_used", {})
                },
                
                "timestamp": response_result.get("timestamp")
            }
            
            logger.info(f"[{session_id}] ========== QUERY PROCESSING COMPLETE ==========")
            logger.info(f"[{session_id}] Pipeline: {result['agent_pipeline']}")
            logger.info(f"[{session_id}] Final confidence: {intent_confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Query processing failed: {str(e)}", exc_info=True)
            return {
                "query": query,
                "response": "I encountered an error processing your query. Please try again.",
                "intent": "general",
                "confidence": 0.0,
                "specialist": "general_agent",
                "sources": [],
                "session_id": session_id,
                "error": str(e),
                "agent_pipeline": "ERROR"
            }


# Singleton instance
orchestrator = AgentOrchestrator()