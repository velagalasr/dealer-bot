"""
Anomaly Detector Module
Detects suspicious patterns and anomalies in queries
"""

from typing import Dict, List, Any
from app.utils.logger import get_logger
import re

logger = get_logger(__name__)


class AnomalyDetector:
    """Detect suspicious patterns and anomalies"""
    
    def __init__(self):
        """Initialize anomaly detector"""
        # Define suspicious keywords
        self.malicious_keywords = [
            "drop", "delete", "exec", "execute", "sql injection",
            "hack", "crack", "breach", "exploit", "vulnerability",
            "password", "credit card", "ssn", "private key"
        ]
        
        # Define suspicious patterns (regex)
        self.suspicious_patterns = [
            r"(union|select|insert|update|delete)[\s\+]+",  # SQL injection
            r"<script|javascript:|onerror=|onclick=",  # XSS
            r"\$\{.*\}",  # Template injection
            r"\.\.[\\/]",  # Path traversal
        ]
        
        # Rate limiting: max queries per session
        self.max_queries_per_minute = 60
        self.max_chars_per_query = 5000
        
        logger.info("Anomaly detector initialized")
    
    def detect(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Detect anomalies in query
        
        Args:
            query: User query
            session_id: Session ID for tracking
            
        Returns:
            Dict: Anomaly detection results
        """
        try:
            results = {
                "is_anomaly": False,
                "risk_level": "low",  # low, medium, high
                "flags": [],
                "details": {}
            }
            
            # Check 1: Query length
            if len(query) > self.max_chars_per_query:
                results["flags"].append("QUERY_TOO_LONG")
                results["risk_level"] = "medium"
                logger.warning(f"[{session_id}] Query exceeds max length")
            
            # Check 2: Malicious keywords
            keyword_matches = self._check_malicious_keywords(query)
            if keyword_matches:
                results["flags"].extend(keyword_matches)
                results["risk_level"] = "high"
                results["details"]["malicious_keywords"] = keyword_matches
                logger.warning(f"[{session_id}] Malicious keywords detected: {keyword_matches}")
            
            # Check 3: Suspicious patterns
            pattern_matches = self._check_suspicious_patterns(query)
            if pattern_matches:
                results["flags"].extend(pattern_matches)
                results["risk_level"] = "high"
                results["details"]["suspicious_patterns"] = pattern_matches
                logger.warning(f"[{session_id}] Suspicious patterns detected: {pattern_matches}")
            
            # Check 4: Encoding attacks
            if self._check_encoding_attacks(query):
                results["flags"].append("ENCODING_ATTACK")
                results["risk_level"] = "high"
                logger.warning(f"[{session_id}] Encoding attack detected")
            
            # Determine if anomaly
            if results["flags"]:
                results["is_anomaly"] = True
            
            logger.info(f"[{session_id}] Anomaly check: risk_level={results['risk_level']}, flags={results['flags']}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {str(e)}")
            return {
                "is_anomaly": False,
                "risk_level": "low",
                "flags": [],
                "error": str(e)
            }
    
    def _check_malicious_keywords(self, query: str) -> List[str]:
        """Check for malicious keywords"""
        query_lower = query.lower()
        matches = []
        
        for keyword in self.malicious_keywords:
            if keyword in query_lower:
                matches.append(f"KEYWORD_DETECTED: {keyword}")
        
        return matches
    
    def _check_suspicious_patterns(self, query: str) -> List[str]:
        """Check for suspicious regex patterns"""
        matches = []
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matches.append(f"PATTERN_DETECTED: {pattern}")
        
        return matches
    
    def _check_encoding_attacks(self, query: str) -> bool:
        """Check for encoding attacks (URL, base64, hex)"""
        # Check for common encoding patterns
        encoding_patterns = [
            r"%[0-9a-f]{2}",  # URL encoding
            r"&#\d+;",  # HTML entities
            r"\\x[0-9a-f]{2}",  # Hex encoding
        ]
        
        for pattern in encoding_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False


# Singleton instance
anomaly_detector = AnomalyDetector()