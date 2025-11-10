"""
Risk Scorer Module
Calculates risk scores based on anomalies
"""

from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RiskScorer:
    """Calculate risk scores for queries"""
    
    def __init__(self):
        """Initialize risk scorer"""
        # Risk weights for different factors
        self.weights = {
            "malicious_keyword": 0.4,      # High weight
            "suspicious_pattern": 0.35,    # High weight
            "encoding_attack": 0.3,        # High weight
            "query_too_long": 0.15,        # Medium weight
        }
        
        # Thresholds
        self.risk_threshold_low = 0.3
        self.risk_threshold_medium = 0.6
        self.risk_threshold_high = 0.8
        
        logger.info("Risk scorer initialized")
    
    def calculate_risk(self, anomaly_results: Dict[str, Any], 
                      session_id: str = None) -> Dict[str, Any]:
        """
        Calculate risk score from anomaly detection results
        
        Args:
            anomaly_results: Results from anomaly detector
            session_id: Session ID for tracking
            
        Returns:
            Dict: Risk score and assessment
        """
        try:
            risk_score = 0.0
            factor_scores = {}
            
            # If no anomalies, risk is low
            if not anomaly_results.get("flags"):
                return {
                    "risk_score": 0.0,
                    "risk_level": "low",
                    "is_safe": True,
                    "confidence": 0.95,
                    "factors": {},
                    "recommendation": "ALLOW"
                }
            
            # Calculate risk from each flag
            flags = anomaly_results.get("flags", [])
            
            for flag in flags:
                if "KEYWORD_DETECTED" in flag:
                    factor_scores["malicious_keyword"] = self.weights["malicious_keyword"]
                elif "PATTERN_DETECTED" in flag:
                    factor_scores["suspicious_pattern"] = self.weights["suspicious_pattern"]
                elif "ENCODING_ATTACK" in flag:
                    factor_scores["encoding_attack"] = self.weights["encoding_attack"]
                elif "QUERY_TOO_LONG" in flag:
                    factor_scores["query_too_long"] = self.weights["query_too_long"]
            
            # Calculate average risk score (0-1 scale)
            if factor_scores:
                risk_score = sum(factor_scores.values()) / len(factor_scores)
                # Normalize to 0-1 range
                risk_score = min(risk_score, 1.0)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Determine if safe
            is_safe = risk_score < self.risk_threshold_medium
            
            # Calculate confidence
            confidence = 1.0 - (len(flags) * 0.05)  # Decrease confidence per flag
            confidence = max(confidence, 0.5)
            
            # Recommendation
            recommendation = self._get_recommendation(risk_level, risk_score)
            
            result = {
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "is_safe": is_safe,
                "confidence": round(confidence, 3),
                "factors": factor_scores,
                "anomaly_count": len(flags),
                "recommendation": recommendation
            }
            
            logger.info(f"[{session_id}] Risk score: {risk_score:.3f}, Level: {risk_level}, Safe: {is_safe}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate risk score: {str(e)}")
            return {
                "risk_score": 0.5,
                "risk_level": "medium",
                "is_safe": False,
                "confidence": 0.5,
                "factors": {},
                "recommendation": "REVIEW",
                "error": str(e)
            }
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """
        Determine risk level from score
        
        Args:
            risk_score: Risk score (0-1)
            
        Returns:
            str: Risk level (low, medium, high)
        """
        if risk_score < self.risk_threshold_low:
            return "low"
        elif risk_score < self.risk_threshold_medium:
            return "medium"
        elif risk_score < self.risk_threshold_high:
            return "high"
        else:
            return "critical"
    
    def _get_recommendation(self, risk_level: str, risk_score: float) -> str:
        """
        Get recommendation based on risk level
        
        Args:
            risk_level: Risk level (low, medium, high, critical)
            risk_score: Risk score (0-1)
            
        Returns:
            str: Recommendation (ALLOW, REVIEW, BLOCK)
        """
        if risk_level == "low":
            return "ALLOW"
        elif risk_level == "medium":
            return "REVIEW"
        elif risk_level == "high":
            return "REVIEW_CAREFULLY"
        else:  # critical
            return "BLOCK"
    
    def get_risk_summary(self, risk_data: Dict[str, Any]) -> str:
        """
        Get human-readable risk summary
        
        Args:
            risk_data: Risk calculation results
            
        Returns:
            str: Risk summary
        """
        risk_score = risk_data.get("risk_score", 0)
        risk_level = risk_data.get("risk_level", "unknown")
        anomaly_count = risk_data.get("anomaly_count", 0)
        recommendation = risk_data.get("recommendation", "UNKNOWN")
        
        summary = (
            f"Risk Assessment: {risk_level.upper()} "
            f"(Score: {risk_score:.1%}) | "
            f"Anomalies Detected: {anomaly_count} | "
            f"Recommendation: {recommendation}"
        )
        
        return summary


# Singleton instance
risk_scorer = RiskScorer()