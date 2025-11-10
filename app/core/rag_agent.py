"""
RAG Agent Module
Intelligent document retrieval, ranking, and filtering
"""

from typing import List, Dict, Optional, Any
from app.core.embeddings import embeddings_manager
from app.core.vector_db import vector_db
from app.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class RAGAgent:
    """Intelligent RAG with retrieval, re-ranking, filtering"""
    
    def __init__(self, embeddings_manager=embeddings_manager,
                 vector_db=vector_db):
        """
        Initialize RAG agent
        
        Args:
            embeddings_manager: Embeddings manager instance
            vector_db: Vector database instance
        """
        self.embeddings_manager = embeddings_manager
        self.vector_db = vector_db
        
        # Ranking and filtering parameters
        self.min_similarity_threshold = 0.5  # Minimum relevance score
        self.max_results = 10  # Max docs to consider
        self.rerank_window = 5  # Number of top results to consider
        
        logger.info("RAG agent initialized")
    
    def retrieve_and_rank(self, query: str, session_id: str = None,
                         n_results: int = 5, user_id: Optional[str] = None,
                         doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve → re-rank → filter → return
        
        Steps:
        1. Generate embedding for query
        2. Retrieve candidates from vector DB
        3. Calculate semantic similarity scores
        4. Re-rank by multiple factors
        5. Filter by criteria (user, doc_type)
        6. Return best results with confidence
        
        Args:
            query: User query
            session_id: Session ID for tracking
            n_results: Number of results to return
            user_id: Filter by user (optional)
            doc_type: Filter by document type (optional)
            
        Returns:
            Dict: Ranked and filtered documents with scores
        """
        try:
            logger.info(f"[{session_id}] RAG retrieval started: {query[:100]}")
            
            # ========== STEP 1: Generate Query Embedding ==========
            logger.info(f"[{session_id}] Step 1: Generating query embedding")
            try:
                query_embedding = self.embeddings_manager.get_embedding(query)
            except Exception as e:
                logger.error(f"[{session_id}] Failed to generate embedding: {str(e)}")
                return {
                    "success": False,
                    "documents": [],
                    "error": f"Embedding generation failed: {str(e)}"
                }
            
            # ========== STEP 2: Retrieve Candidates ==========
            logger.info(f"[{session_id}] Step 2: Retrieving candidates from vector DB")
            try:
                # Retrieve more than needed for re-ranking
                retrieve_count = min(self.max_results, n_results * 2)
                raw_results = self.vector_db.query(query_embedding, n_results=retrieve_count)
            except Exception as e:
                logger.error(f"[{session_id}] Failed to retrieve from vector DB: {str(e)}")
                return {
                    "success": False,
                    "documents": [],
                    "error": f"Vector DB retrieval failed: {str(e)}"
                }
            
            # ========== STEP 3: Process and Score Results ==========
            logger.info(f"[{session_id}] Step 3: Processing and scoring results")
            
            scored_documents = []
            
            if raw_results.get("documents") and raw_results["documents"][0]:
                for i, (doc, distance, metadata) in enumerate(
                    zip(raw_results["documents"][0],
                        raw_results["distances"][0],
                        raw_results["metadatas"][0])
                ):
                    # Convert distance to similarity (0-1 scale)
                    # Distance ranges from 0 to 2 for cosine, convert to similarity
                    similarity_score = 1 - distance
                    
                    # Skip if below threshold
                    if similarity_score < self.min_similarity_threshold:
                        logger.debug(f"[{session_id}] Skipping doc {i}: similarity too low ({similarity_score:.2f})")
                        continue
                    
                    # ========== STEP 4: Calculate Ranking Factors ==========
                    ranking_factors = self._calculate_ranking_factors(
                        doc, metadata, similarity_score, i
                    )
                    
                    # Combined score considering multiple factors
                    combined_score = self._calculate_combined_score(ranking_factors)
                    
                    scored_documents.append({
                        "rank": None,  # Will be set after filtering
                        "document": doc,
                        "similarity_score": round(similarity_score, 3),
                        "combined_score": round(combined_score, 3),
                        "metadata": metadata,
                        "ranking_factors": ranking_factors
                    })
            
            logger.info(f"[{session_id}] Retrieved {len(scored_documents)} scored documents")
            
            # ========== STEP 5: Filter by Criteria ==========
            logger.info(f"[{session_id}] Step 5: Filtering by criteria")
            
            filtered_documents = self._filter_documents(
                scored_documents, user_id, doc_type, session_id
            )
            
            logger.info(f"[{session_id}] After filtering: {len(filtered_documents)} documents")
            
            # ========== STEP 6: Re-rank by Combined Score ==========
            logger.info(f"[{session_id}] Step 6: Re-ranking by combined score")
            
            sorted_documents = sorted(
                filtered_documents,
                key=lambda x: x["combined_score"],
                reverse=True
            )
            
            # Limit to requested number
            final_documents = sorted_documents[:n_results]
            
            # Assign final ranks
            for rank, doc in enumerate(final_documents, 1):
                doc["rank"] = rank
            
            # ========== CALCULATE CONFIDENCE ==========
            # Confidence based on similarity scores and document count
            if final_documents:
                avg_similarity = sum(d["similarity_score"] for d in final_documents) / len(final_documents)
                confidence = min(avg_similarity, 1.0)
            else:
                confidence = 0.0
            
            result = {
                "success": True,
                "query": query,
                "documents": final_documents,
                "document_count": len(final_documents),
                "confidence": round(confidence, 3),
                "retrieval_stats": {
                    "retrieved": len(scored_documents),
                    "after_filtering": len(filtered_documents),
                    "returned": len(final_documents),
                    "avg_similarity": round(avg_similarity, 3) if final_documents else 0.0
                },
                "filters_applied": {
                    "user_id": user_id,
                    "doc_type": doc_type
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[{session_id}] RAG retrieval complete: "
                       f"returned {len(final_documents)} docs, confidence: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"[{session_id}] RAG retrieval failed: {str(e)}")
            return {
                "success": False,
                "documents": [],
                "error": str(e),
                "session_id": session_id
            }
    
    def _calculate_ranking_factors(self, doc: str, metadata: Dict,
                                   similarity_score: float, rank: int) -> Dict[str, float]:
        """
        Calculate multiple ranking factors
        
        Factors:
        - Semantic similarity (from embedding)
        - Document type relevance
        - Recency (newer docs ranked higher)
        - Position bonus (top results from vector DB)
        
        Args:
            doc: Document text
            metadata: Document metadata
            similarity_score: Semantic similarity (0-1)
            rank: Original rank from vector DB
            
        Returns:
            Dict: Ranking factors and scores
        """
        factors = {
            "semantic_similarity": similarity_score
        }
        
        # Factor: Position bonus (top results get boost)
        position_boost = 1.0 - (rank * 0.05)  # Decreases with rank
        factors["position_bonus"] = max(position_boost, 0.0)
        
        # Factor: Document length (longer docs may be more relevant)
        doc_length = len(doc)
        length_factor = min(doc_length / 1000, 1.0)  # Normalize to 0-1
        factors["length_factor"] = length_factor
        
        # Factor: Document type bias
        doc_type = metadata.get("doc_type", "unknown")
        doc_type_score = 1.0 if doc_type == "system" else 0.8
        factors["doc_type_score"] = doc_type_score
        
        # Factor: Recency
        try:
            from datetime import datetime
            ingested_at = metadata.get("ingested_at")
            if ingested_at:
                ingested_time = datetime.fromisoformat(ingested_at)
                days_old = (datetime.now() - ingested_time).days
                recency = max(1.0 - (days_old * 0.01), 0.5)  # Don't go below 0.5
                factors["recency"] = recency
        except:
            factors["recency"] = 1.0  # Default if parsing fails
        
        return factors
    
    def _calculate_combined_score(self, ranking_factors: Dict[str, float]) -> float:
        """
        Calculate combined ranking score from multiple factors
        
        Weighted formula:
        - Semantic similarity: 50% (most important)
        - Position bonus: 20%
        - Recency: 15%
        - Doc type: 10%
        - Length: 5%
        
        Args:
            ranking_factors: Dict of individual factors
            
        Returns:
            float: Combined score (0-1)
        """
        weights = {
            "semantic_similarity": 0.50,
            "position_bonus": 0.20,
            "recency": 0.15,
            "doc_type_score": 0.10,
            "length_factor": 0.05
        }
        
        combined = 0.0
        for factor, weight in weights.items():
            value = ranking_factors.get(factor, 0.0)
            combined += value * weight
        
        return combined
    
    def _filter_documents(self, documents: List[Dict], user_id: Optional[str],
                         doc_type: Optional[str], session_id: str) -> List[Dict]:
        """
        Filter documents by criteria
        
        Filters:
        - User access (if user_id provided)
        - Document type (if doc_type provided)
        
        Args:
            documents: List of scored documents
            user_id: Filter by user ID (optional)
            doc_type: Filter by document type (optional)
            session_id: Session ID for logging
            
        Returns:
            List: Filtered documents
        """
        filtered = documents.copy()
        
        # Filter by user access
        if user_id:
            logger.debug(f"[{session_id}] Filtering by user_id: {user_id}")
            filtered = [
                d for d in filtered
                if d["metadata"].get("doc_type") == "system" or d["metadata"].get("user_id") == user_id
            ]
            logger.debug(f"[{session_id}] After user filter: {len(filtered)} docs")
        
        # Filter by document type
        if doc_type:
            logger.debug(f"[{session_id}] Filtering by doc_type: {doc_type}")
            filtered = [
                d for d in filtered
                if d["metadata"].get("doc_type") == doc_type
            ]
            logger.debug(f"[{session_id}] After doc_type filter: {len(filtered)} docs")
        
        return filtered


# Singleton instance
rag_agent = RAGAgent()