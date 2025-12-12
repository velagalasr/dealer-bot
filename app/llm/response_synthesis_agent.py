"""
Response Synthesis Agent
Synthesizes intelligent responses using query context, intent, anomalies, and documents
Includes real-time quality metrics for every response
"""

from typing import Dict, List, Optional, Any
from app.llm.openai_client import openai_client
from app.utils.logger import get_logger
from datetime import datetime
import re

logger = get_logger(__name__)

# Import semantic similarity model for real-time metrics
try:
    from sentence_transformers import SentenceTransformer, util
    SEMANTIC_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_MODEL = None
    SEMANTIC_AVAILABLE = False
    logger.warning("SentenceTransformers not available - semantic metrics disabled")


class ResponseSynthesisAgent:
    """Intelligent response synthesis with context awareness"""
    
    def __init__(self, openai_client=openai_client):
        """
        Initialize response synthesis agent
        
        Args:
            openai_client: OpenAI client instance
        """
        self.openai_client = openai_client
        logger.info("Response synthesis agent initialized")
    
    def synthesize(self, query: str, intent: Dict[str, Any],
                  anomaly_info: Optional[Dict[str, Any]] = None,
                  rag_documents: Optional[List[Dict[str, Any]]] = None,
                  session_id: str = None) -> Dict[str, Any]:
        """
        Synthesize response using all available context
        
        Args:
            query: User query
            intent: Intent classification result
            anomaly_info: Anomaly detection result (optional)
            rag_documents: Retrieved documents (optional)
            session_id: Session ID for tracking
            
        Returns:
            Dict: Synthesized response with metadata
        """
        try:
            logger.info(f"[{session_id}] Starting response synthesis")
            
            # ========== STEP 1: Determine Response Strategy ==========
            logger.info(f"[{session_id}] Step 1: Determining response strategy")
            
            strategy = self._determine_strategy(
                intent, anomaly_info, rag_documents, session_id
            )
            
            logger.info(f"[{session_id}] Strategy: {strategy['type']}")
            
            # ========== STEP 2: Prepare Context ==========
            logger.info(f"[{session_id}] Step 2: Preparing context documents")
            
            context_docs = self._prepare_context_documents(
                anomaly_info, rag_documents, strategy, session_id
            )
            
            logger.info(f"[{session_id}] Using {len(context_docs)} context documents")
            
            # ========== STEP 3: Generate Response ==========
            logger.info(f"[{session_id}] Step 3: Generating response with LLM")
            
            response_text = self._generate_response(
                query, intent, strategy, context_docs, session_id
            )
            
            # ========== STEP 4: Calculate Real-Time Quality Metrics ==========
            logger.info(f"[{session_id}] Step 4: Calculating real-time quality metrics")
            
            quality_metrics = self._calculate_realtime_quality(
                query, response_text, context_docs, session_id
            )
            
            logger.info(f"[{session_id}] Quality Score: {quality_metrics.get('overall_quality', 0):.2f}")
            
            # ========== STEP 5: Build Result ==========
            result = {
                "query": query,
                "response": response_text,
                "intent": intent.get("intent", "unknown"),
                "confidence": intent.get("confidence", 0.0),
                "specialist": intent.get("specialist", "general_agent"),
                "response_strategy": strategy["type"],
                "quality_metrics": quality_metrics,  # Add real-time quality metrics
                "context_used": {
                    "anomaly_detection": anomaly_info is not None and anomaly_info.get("is_anomalous", False),
                    "rag_documents": len(context_docs),
                    "includes_guidance": strategy["includes_guidance"]
                },
                "documents": context_docs,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[{session_id}] Response synthesis complete")
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] Response synthesis failed: {str(e)}")
            return {
                "query": query,
                "response": "I apologize, but I encountered an error generating a response. Please try again.",
                "intent": intent.get("intent", "unknown") if intent else "unknown",
                "confidence": 0.0,
                "error": str(e),
                "session_id": session_id
            }
    
    def _determine_strategy(self, intent: Dict[str, Any],
                           anomaly_info: Optional[Dict[str, Any]],
                           rag_documents: Optional[List[Dict[str, Any]]],
                           session_id: str) -> Dict[str, Any]:
        """
        Determine response strategy based on context
        
        Strategies:
        - NORMAL: Regular Q&A from documents
        - ANOMALY_REVIEW: Anomaly detected, use guidance docs
        - ESCALATION: High risk, recommend escalation
        - GUIDANCE_ONLY: Use guidance docs without RAG docs
        
        Args:
            intent: Intent classification
            anomaly_info: Anomaly detection result
            rag_documents: Retrieved documents
            session_id: Session ID
            
        Returns:
            Dict: Strategy details
        """
        try:
            # Check anomaly level
            is_anomalous = anomaly_info and anomaly_info.get("is_anomalous", False)
            anomaly_decision = anomaly_info.get("decision", "ALLOW") if anomaly_info else "ALLOW"
            risk_level = anomaly_info.get("risk_level", "low") if anomaly_info else "low"
            
            # Determine strategy
            if anomaly_decision == "BLOCK":
                strategy_type = "ESCALATION"
                includes_guidance = True
            elif is_anomalous and anomaly_decision in ["REVIEW", "REVIEW_CAREFULLY"]:
                strategy_type = "ANOMALY_REVIEW"
                includes_guidance = True
            elif rag_documents and len(rag_documents) > 0:
                strategy_type = "NORMAL"
                includes_guidance = False
            else:
                strategy_type = "GENERAL"
                includes_guidance = False
            
            return {
                "type": strategy_type,
                "is_anomalous": is_anomalous,
                "anomaly_decision": anomaly_decision,
                "risk_level": risk_level,
                "includes_guidance": includes_guidance,
                "has_documents": rag_documents is not None and len(rag_documents) > 0
            }
            
        except Exception as e:
            logger.error(f"[{session_id}] Failed to determine strategy: {str(e)}")
            return {
                "type": "GENERAL",
                "is_anomalous": False,
                "includes_guidance": False,
                "has_documents": False
            }
    
    def _prepare_context_documents(self, anomaly_info: Optional[Dict[str, Any]],
                                   rag_documents: Optional[List[Dict[str, Any]]],
                                   strategy: Dict[str, Any],
                                   session_id: str) -> List[Dict[str, Any]]:
        """
        Prepare context documents for LLM
        
        Priority:
        1. Guidance documents from anomaly detection (if anomalous)
        2. RAG retrieved documents (if available)
        
        Args:
            anomaly_info: Anomaly detection result
            rag_documents: Retrieved documents
            strategy: Response strategy
            session_id: Session ID
            
        Returns:
            List: Prepared context documents
        """
        try:
            context_docs = []
            
            # Add guidance documents if anomaly detected
            if strategy["includes_guidance"] and anomaly_info:
                guidance_docs = anomaly_info.get("guidance_documents", [])
                if guidance_docs:
                    logger.info(f"[{session_id}] Adding {len(guidance_docs)} guidance documents")
                    for doc in guidance_docs:
                        context_docs.append({
                            "source": "guidance",
                            "rank": doc.get("rank", 0),
                            "content": doc.get("document", ""),
                            "score": doc.get("similarity_score", 0),
                            "type": "guidance"
                        })
            
            # Add RAG documents
            if rag_documents:
                logger.info(f"[{session_id}] Adding {len(rag_documents)} RAG documents")
                for doc in rag_documents:
                    context_docs.append({
                        "source": "rag",
                        "rank": doc.get("rank", 0),
                        "content": doc.get("document", ""),
                        "score": doc.get("similarity_score", 0) or doc.get("combined_score", 0),
                        "type": "retrieved"
                    })
            
            return context_docs
            
        except Exception as e:
            logger.error(f"[{session_id}] Failed to prepare context: {str(e)}")
            return []
    
    def _generate_response(self, query: str, intent: Dict[str, Any],
                          strategy: Dict[str, Any],
                          context_docs: List[Dict[str, Any]],
                          session_id: str) -> str:
        """
        Generate response using LLM with context
        
        Args:
            query: User query
            intent: Intent classification
            strategy: Response strategy
            context_docs: Context documents
            session_id: Session ID
            
        Returns:
            str: Generated response
        """
        try:
            # Prepare context text
            context_text = self._format_context_documents(context_docs)
            
            # Build system prompt based on strategy
            system_prompt = self._build_system_prompt(
                strategy, intent, session_id
            )
            
            # Build user prompt
            user_prompt = f"""User Query: {query}

{context_text}

Please provide a helpful and accurate response based on the query and context above. Do not include RAG scores"""
            
            # Generate response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.openai_client.generate_response(
                messages, temperature=0.3, max_tokens=1000
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"[{session_id}] Failed to generate response: {str(e)}")
            return "I apologize, but I was unable to generate a response at this time."
    
    def _calculate_realtime_quality(self, query: str, response: str,
                                    context_docs: List[Dict[str, Any]],
                                    session_id: str) -> Dict[str, float]:
        """
        Calculate real-time quality metrics for response
        
        Metrics calculated:
        - Groundedness: Response based on context
        - Answer Relevance: Response addresses query
        - Context Relevance: Context relevant to query
        - Faithfulness: No hallucinations
        - Formatting: Structure quality
        - Overall Quality: Weighted average
        
        Args:
            query: User query
            response: Generated response
            context_docs: Context documents used
            session_id: Session ID
            
        Returns:
            Dict: Quality metrics (0-1 scale)
        """
        try:
            metrics = {}
            
            # Extract context text
            context_text = " ".join([doc.get('content', '') for doc in context_docs])
            
            # 1. Groundedness (0-1)
            metrics['groundedness'] = self._metric_groundedness(response, context_text)
            
            # 2. Answer Relevance (0-1)
            metrics['answer_relevance'] = self._metric_answer_relevance(query, response)
            
            # 3. Context Relevance (0-1)
            metrics['context_relevance'] = self._metric_context_relevance(query, context_text)
            
            # 4. Faithfulness (0-1)
            metrics['faithfulness'] = self._metric_faithfulness(response, context_text)
            
            # 5. Formatting (0-1)
            metrics['formatting'] = self._metric_formatting(response)
            
            # 6. Overall Quality (weighted average)
            weights = {
                'groundedness': 0.25,
                'answer_relevance': 0.25,
                'context_relevance': 0.15,
                'faithfulness': 0.25,
                'formatting': 0.10
            }
            
            total_weight = sum(weights.values())
            weighted_sum = sum(metrics[k] * weights[k] for k in weights if k in metrics)
            metrics['overall_quality'] = round(weighted_sum / total_weight, 3)
            
            # Log if quality is low
            if metrics['overall_quality'] < 0.5:
                logger.warning(f"[{session_id}] Low quality response: {metrics['overall_quality']:.2f}")
            
            if metrics['groundedness'] < 0.3:
                logger.warning(f"[{session_id}] Low groundedness - possible hallucination")
            
            return metrics
            
        except Exception as e:
            logger.error(f"[{session_id}] Failed to calculate quality metrics: {str(e)}")
            return {
                'groundedness': 0.0,
                'answer_relevance': 0.0,
                'context_relevance': 0.0,
                'faithfulness': 0.0,
                'formatting': 0.0,
                'overall_quality': 0.0,
                'error': str(e)
            }
    
    def _metric_groundedness(self, response: str, context: str) -> float:
        """Calculate if response is grounded in context"""
        if not response or not context:
            return 0.0
        
        response_lower = response.lower()
        context_lower = context.lower()
        
        # Count overlapping content words (4+ chars)
        response_words = set(re.findall(r'\b\w{4,}\b', response_lower))
        context_words = set(re.findall(r'\b\w{4,}\b', context_lower))
        
        if not response_words:
            return 0.0
        
        overlap = len(response_words & context_words)
        overlap_ratio = overlap / len(response_words)
        
        # Boost score if high overlap
        return round(min(overlap_ratio * 1.3, 1.0), 3)
    
    def _metric_answer_relevance(self, query: str, response: str) -> float:
        """Calculate if response is relevant to query"""
        if not query or not response:
            return 0.0
        
        # Use semantic similarity if available
        if SEMANTIC_AVAILABLE and SEMANTIC_MODEL:
            try:
                query_emb = SEMANTIC_MODEL.encode(query, convert_to_tensor=True)
                response_emb = SEMANTIC_MODEL.encode(response, convert_to_tensor=True)
                similarity = util.cos_sim(query_emb, response_emb).item()
                return round(similarity, 3)
            except:
                pass
        
        # Fallback: word overlap
        query_words = set(re.findall(r'\b\w{4,}\b', query.lower()))
        response_words = set(re.findall(r'\b\w{4,}\b', response.lower()))
        
        if not query_words:
            return 0.5
        
        overlap = len(query_words & response_words) / len(query_words)
        return round(min(overlap * 1.5, 1.0), 3)
    
    def _metric_context_relevance(self, query: str, context: str) -> float:
        """Calculate if context is relevant to query"""
        if not query or not context:
            return 0.0
        
        # Use semantic similarity if available
        if SEMANTIC_AVAILABLE and SEMANTIC_MODEL:
            try:
                query_emb = SEMANTIC_MODEL.encode(query, convert_to_tensor=True)
                context_emb = SEMANTIC_MODEL.encode(context[:1000], convert_to_tensor=True)  # Limit context length
                similarity = util.cos_sim(query_emb, context_emb).item()
                return round(similarity, 3)
            except:
                pass
        
        # Fallback: word overlap
        query_words = set(re.findall(r'\b\w{4,}\b', query.lower()))
        context_words = set(re.findall(r'\b\w{4,}\b', context.lower()))
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words & context_words) / len(query_words)
        return round(min(overlap * 1.5, 1.0), 3)
    
    def _metric_faithfulness(self, response: str, context: str) -> float:
        """Calculate faithfulness (no hallucinations)"""
        if not context or not response:
            return 0.5  # Neutral if no context
        
        # Split response into sentences
        sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 10]
        
        if not sentences:
            return 1.0
        
        supported = 0
        context_lower = context.lower()
        
        for sentence in sentences:
            # Extract key words from sentence
            key_words = set(re.findall(r'\b\w{4,}\b', sentence.lower()))
            context_words = set(re.findall(r'\b\w{4,}\b', context_lower))
            
            if key_words:
                overlap_ratio = len(key_words & context_words) / len(key_words)
                if overlap_ratio > 0.3:  # At least 30% overlap
                    supported += 1
        
        faithfulness = supported / len(sentences) if sentences else 0.0
        return round(faithfulness, 3)
    
    def _metric_formatting(self, response: str) -> float:
        """Calculate response formatting quality"""
        if not response:
            return 0.0
        
        score = 0.0
        
        # Proper capitalization
        if response[0].isupper():
            score += 0.2
        
        # Proper punctuation
        if response.rstrip()[-1] in '.!?':
            score += 0.2
        
        # Reasonable length
        if 30 < len(response) < 2000:
            score += 0.2
        elif len(response) >= 30:
            score += 0.1
        
        # Has spaces (not garbled)
        if response.count(' ') > 3:
            score += 0.2
        
        # Not all caps
        if not response.isupper():
            score += 0.2
        
        return round(score, 3)
    
    def _build_system_prompt(self, strategy: Dict[str, Any],
                            intent: Dict[str, Any],
                            session_id: str) -> str:
        """Build system prompt based on strategy"""
        
        base_prompt = "You are a helpful dealer support assistant."
        
        # Add strategy-specific instructions
        if strategy["type"] == "ANOMALY_REVIEW":
            return f"""{base_prompt}

The user's query contains a security or fraud concern that has been flagged for review.
Please:
1. Acknowledge the concern seriously
2. Provide guidance from the available documentation
3. Recommend contacting support for further assistance if needed
4. Be empathetic and professional"""
        
        elif strategy["type"] == "ESCALATION":
            return f"""{base_prompt}

IMPORTANT: This query contains a high-risk security concern and requires careful handling.
Please:
1. Express concern appropriately
2. Recommend immediate escalation to the support team
3. Provide temporary guidance if available
4. DO NOT provide sensitive technical details"""
        
        elif strategy["type"] == "GUIDANCE_ONLY":
            return f"""{base_prompt}

Provide guidance based on the available documentation.
Be clear, helpful, and thorough."""
        
        else:  # NORMAL
            return f"""{base_prompt}

Use the provided context documents to answer the user's question.
Be accurate, helpful, and cite relevant information from the documents.
If unsure or did not find any info in the provided documents, admit it rather than guessing or searching elsewhere."""
    
    def _format_context_documents(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format context documents for LLM"""
        if not context_docs:
            return "No context documents available."
        
        formatted = "Context Documents:\n"
        
        for doc in context_docs:
            formatted += f"\n[{doc['source'].upper()} - Score: {doc['score']:.2f}]\n"
            formatted += f"{doc['content'][:500]}...\n" if len(doc['content']) > 500 else f"{doc['content']}\n"
        
        return formatted


# Singleton instance
response_synthesis_agent = ResponseSynthesisAgent()