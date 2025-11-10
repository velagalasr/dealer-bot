"""
Agent Router Module
Routes queries to appropriate specialist agents
"""

from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AgentRouter:
    """Route queries to specialist agents"""
    
    def __init__(self):
        """Initialize router"""
        self.routes = {
            "product_agent": self._product_specialist,
            "tech_agent": self._tech_specialist,
            "maintenance_agent": self._maintenance_specialist,
            "warranty_agent": self._warranty_specialist,
            "general_agent": self._general_specialist
        }
    
    def route_query(self, query: str, specialist: str) -> Dict[str, Any]:
        """
        Route query to specialist
        
        Args:
            query: User query
            specialist: Target specialist agent
            
        Returns:
            Dict: Routing result
        """
        try:
            if specialist not in self.routes:
                logger.warning(f"Unknown specialist: {specialist}, using general_agent")
                specialist = "general_agent"
            
            handler = self.routes[specialist]
            return handler(query)
            
        except Exception as e:
            logger.error(f"Routing failed: {str(e)}")
            return {"error": str(e), "specialist": specialist}
    
    def _product_specialist(self, query: str) -> Dict[str, Any]:
        """Handle product-related queries"""
        logger.info("Routing to product specialist")
        return {"specialist": "product_agent", "handler": "product_specialist"}
    
    def _tech_specialist(self, query: str) -> Dict[str, Any]:
        """Handle technical support queries"""
        logger.info("Routing to tech specialist")
        return {"specialist": "tech_agent", "handler": "tech_specialist"}
    
    def _maintenance_specialist(self, query: str) -> Dict[str, Any]:
        """Handle maintenance-related queries"""
        logger.info("Routing to maintenance specialist")
        return {"specialist": "maintenance_agent", "handler": "maintenance_specialist"}
    
    def _warranty_specialist(self, query: str) -> Dict[str, Any]:
        """Handle warranty-related queries"""
        logger.info("Routing to warranty specialist")
        return {"specialist": "warranty_agent", "handler": "warranty_specialist"}
    
    def _general_specialist(self, query: str) -> Dict[str, Any]:
        """Handle general queries"""
        logger.info("Routing to general specialist")
        return {"specialist": "general_agent", "handler": "general_specialist"}


# Singleton instance
router = AgentRouter()