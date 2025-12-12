"""
Anomaly Detection Agent
Analyzes queries for suspicious patterns, calculates risk/confidence scores
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from app.utils.logger import get_logger
from app.core.rag_agent import rag_agent

logger = get_logger(__name__)


class AnomalyDetectionAgent:
    """Intelligent anomaly detection with comprehensive scoring"""
    
    def __init__(self):
        """Initialize anomaly detection agent"""
        
        # Malicious keywords and patterns
        self.malicious_keywords = {
            "injection_keywords": [
                "drop", "delete", "exec", "execute", "sql injection",
                "union", "select", "insert", "update"
            ],
            "hacking_keywords": [
                "hack", "crack", "breach", "exploit", "vulnerability",
                "backdoor", "payload", "shellcode"
            ],
            "fraud_keywords": [
                "fraud", "money laundering", "stolen", "credit card",
                "SSN", "password", "private key"
            ],
            "xss_keywords": [
                "script", "javascript", "onerror", "onclick", "alert"
            ]
        }
        
        # Suspicious patterns (regex)
        self.suspicious_patterns = {
            "sql_injection": r"(union|select|insert|update|delete)[\s\+]+",
            "xss_attack": r"<script|javascript:|onerror=|onclick=",
            "template_injection": r"\$\{.*\}",
            "path_traversal": r"\.\.[\\/]",
            "command_injection": r"[;&|`\$\(\)]"
        }
        
        # Limits
        self.max_query_length = 5000
        self.max_words = 500
        
        logger.info("Anomaly detection agent initialized")
    
    def analyze(self, query: str, session_id: str = None,
               user_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive anomaly analysis
        
        Calculates:
        - Risk score (0-1)
        - Confidence score (0-1)
        - Anomaly factors
        - Final decision
        
        Args:
            query: User query
            session_id: Session ID for tracking
            user_history: Previous queries from user
            
        Returns:
            Dict: Anomaly analysis with scores and decision
        """
        try:
            logger.info(f"[{session_id}] Analyzing query for anomalies")
            
            # Initialize results
            anomaly_factors = []
            risk_components = {}
            
            # ========== FACTOR 1: Malicious Keywords ==========
            keyword_result = self._check_malicious_keywords(query)
            if keyword_result["found"]:
                anomaly_factors.extend(keyword_result["keywords"])
                risk_components["malicious_keywords"] = 0.4
                logger.warning(f"[{session_id}] Malicious keywords found: {keyword_result['keywords']}")
            
            # ========== FACTOR 2: Suspicious Patterns ==========
            pattern_result = self._check_suspicious_patterns(query)
            if pattern_result["found"]:
                anomaly_factors.extend(pattern_result["patterns"])
                risk_components["suspicious_patterns"] = 0.35
                logger.warning(f"[{session_id}] Suspicious patterns found: {pattern_result['patterns']}")
            
            # ========== FACTOR 3: Encoding Attacks ==========
            encoding_result = self._check_encoding_attacks(query)
            if encoding_result["found"]:
                anomaly_factors.append(f"ENCODING_ATTACK: {encoding_result['type']}")
                risk_components["encoding_attack"] = 0.3
                logger.warning(f"[{session_id}] Encoding attack detected: {encoding_result['type']}")
            
            # ========== FACTOR 4: Query Length Anomaly ==========
            length_result = self._check_query_length(query)
            if length_result["anomalous"]:
                anomaly_factors.append(length_result["factor"])
                risk_components["query_length"] = 0.15
                logger.warning(f"[{session_id}] Query length anomaly: {length_result['factor']}")
            
            # ========== FACTOR 5: User Behavior Anomaly ==========
            if user_history:
                behavior_result = self._check_behavior_anomaly(query, user_history)
                if behavior_result["anomalous"]:
                    anomaly_factors.append(behavior_result["factor"])
                    risk_components["behavior_anomaly"] = 0.25
                    logger.warning(f"[{session_id}] Behavior anomaly: {behavior_result['factor']}")
            
            # ========== CALCULATE SCORES ==========
            
            # Risk Score: Average of detected components
            if risk_components:
                risk_score = sum(risk_components.values()) / len(risk_components)
            else:
                risk_score = 0.0
            
            # Confidence Score: Based on number of factors detected
            factor_count = len(anomaly_factors)
            confidence_score = min(0.5 + (factor_count * 0.15), 1.0)  # 0.5 baseline + 0.15 per factor
            
            # ========== DETERMINE RISK LEVEL ==========
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.6:
                risk_level = "medium"
            elif risk_score < 0.8:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # ========== MAKE DECISION ==========
            decision = self._make_decision(risk_level, risk_score, factor_count)
            
            # ========== BUILD RESULT ==========
            # ========== SEARCH FOR RELEVANT DOCUMENTS ==========
            relevant_documents = []
            if decision == "REVIEW":  # Only search if flagged for review
                logger.info(f"[{session_id}] Searching for relevant guidance documents")
                relevant_documents = self._search_relevant_documents(
                    query, anomaly_factors, session_id
                )

            # ========== BUILD RESULT ==========
            result = {
                "is_anomalous": len(anomaly_factors) > 0,
                "risk_score": round(risk_score, 3),
                "confidence_score": round(confidence_score, 3),
                "risk_level": risk_level,
                "anomaly_factors": anomaly_factors,
                "anomaly_count": factor_count,
                "risk_components": risk_components,
                "decision": decision,
                "guidance_documents": relevant_documents,  
                "document_count": len(relevant_documents), 
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[{session_id}] Anomaly analysis complete: "
                       f"risk={risk_score:.2f}, confidence={confidence_score:.2f}, "
                       f"decision={decision}")
            
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Anomaly analysis failed: {str(e)}")
            return {
                "is_anomalous": False,
                "risk_score": 0.0,
                "confidence_score": 0.0,
                "risk_level": "unknown",
                "anomaly_factors": [],
                "anomaly_count": 0,
                "decision": "REVIEW",
                "error": str(e),
                "session_id": session_id
            }
    
    def _check_malicious_keywords(self, query: str) -> Dict[str, Any]:
        """Check for malicious keywords"""
        query_lower = query.lower()
        found_keywords = []
        
        for category, keywords in self.malicious_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_keywords.append(f"{category.upper()}: {keyword}")
        
        return {
            "found": len(found_keywords) > 0,
            "keywords": found_keywords,
            "count": len(found_keywords)
        }
    
    def _check_suspicious_patterns(self, query: str) -> Dict[str, Any]:
        """Check for suspicious regex patterns"""
        found_patterns = []
        
        for pattern_name, pattern in self.suspicious_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                found_patterns.append(f"{pattern_name.upper()}")
        
        return {
            "found": len(found_patterns) > 0,
            "patterns": found_patterns,
            "count": len(found_patterns)
        }
    
    def _check_encoding_attacks(self, query: str) -> Dict[str, Any]:
        """Check for encoding attacks"""
        encoding_patterns = {
            "url_encoding": r"%[0-9a-f]{2}",
            "html_entities": r"&#\d+;",
            "hex_encoding": r"\\x[0-9a-f]{2}",
            "unicode_encoding": r"\\u[0-9a-f]{4}"
        }
        
        for encoding_type, pattern in encoding_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return {
                    "found": True,
                    "type": encoding_type
                }
        
        return {"found": False, "type": None}
    
    def _check_query_length(self, query: str) -> Dict[str, Any]:
        """Check for query length anomalies"""
        query_length = len(query)
        word_count = len(query.split())
        
        if query_length > self.max_query_length:
            return {
                "anomalous": True,
                "factor": f"QUERY_TOO_LONG: {query_length} chars (max: {self.max_query_length})"
            }
        
        if word_count > self.max_words:
            return {
                "anomalous": True,
                "factor": f"TOO_MANY_WORDS: {word_count} words (max: {self.max_words})"
            }
        
        return {"anomalous": False, "factor": None}
    
    def _check_behavior_anomaly(self, query: str, user_history: List[str]) -> Dict[str, Any]:
        """Check for unusual user behavior patterns"""
        
        # If user has history, analyze for sudden changes
        if not user_history:
            return {"anomalous": False, "factor": None}
        
        avg_history_length = sum(len(q) for q in user_history) / len(user_history)
        current_length = len(query)
        
        # Anomaly if current query is significantly different
        if current_length > avg_history_length * 3:
            return {
                "anomalous": True,
                "factor": f"BEHAVIOR_CHANGE: Query significantly longer than history average"
            }
        
        return {"anomalous": False, "factor": None}
    
    def _make_decision(self, risk_level: str, risk_score: float, factor_count: int) -> str:
        """Make decision based on risk analysis"""
        
        if risk_level == "critical":
            return "BLOCK"
        elif risk_level == "high":
            return "BLOCK" if factor_count > 2 else "REVIEW_CAREFULLY"
        elif risk_level == "medium":
            return "REVIEW"
        else:
            return "ALLOW"

def _search_relevant_documents(self, query: str, anomaly_factors: List[str],
                               session_id: str) -> List[Dict[str, Any]]:
    """
    Search RAG for documents related to detected anomalies
    
    Args:
        query: Original user query
        anomaly_factors: Detected anomaly factors
        session_id: Session ID for tracking
        
    Returns:
        List: Relevant documents from RAG
    """
    try:
        # Determine search query based on anomaly type
        search_query = query
        
        # If fraud detected, search for fraud docs
        if any("fraud" in factor.lower() for factor in anomaly_factors):
            search_query = f"fraud detection account security prevention unauthorized access"
            logger.info(f"[{session_id}] Searching for fraud-related documents")
        
        # If hacking detected, search for security docs
        elif any("hack" in factor.lower() or "breach" in factor.lower() for factor in anomaly_factors):
            search_query = f"security breach hacking attack prevention recovery"
            logger.info(f"[{session_id}] Searching for security-related documents")
        
        # Retrieve relevant documents
        rag_result = rag_agent.retrieve_and_rank(
            query=search_query,
            session_id=session_id,
            n_results=3,  # Get top 3 relevant documents
            doc_type="system"  # Only system docs for guidance
        )
        
        if rag_result.get("success"):
            documents = rag_result.get("documents", [])
            logger.info(f"[{session_id}] Found {len(documents)} relevant documents")
            return documents
        else:
            logger.warning(f"[{session_id}] RAG search failed: {rag_result.get('error')}")
            return []
            
    except Exception as e:
        logger.error(f"[{session_id}] Failed to search documents: {str(e)}")
        return []
    
# Singleton instance
anomaly_detection_agent = AnomalyDetectionAgent()