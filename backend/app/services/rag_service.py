"""
RAG (Retrieval-Augmented Generation) service.
Handles similarity search and retrieval from ChromaDB.
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from app.services.embedding_service import EmbeddingService
from app.db.chroma_client import ChromaClient


class RAGService:
    """
    Service for RAG retrieval operations.
    
    Design choices:
    1. Separation of concerns: RAG service handles retrieval logic
    2. Metadata filtering: Enables filtering by contract attributes
    3. Similarity scoring: Returns scores for explainability
    4. Flexible queries: Supports text queries and metadata filters
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chroma_client = ChromaClient()
    
    def retrieve_similar_contracts(
        self,
        query_text: str,
        n_results: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar contract chunks using RAG.
        
        Args:
            query_text: Natural language query
            n_results: Number of results to return
            filters: Metadata filters (e.g., {"contract_type": "employment", "location": "India"})
            
        Returns:
            List of dictionaries with:
            - text: Chunk text
            - similarity_score: Cosine similarity (1 - distance)
            - metadata: Chunk metadata
            - contract_id: Source contract ID
        """
        import time
        start_time = time.time()
        logger.info(f"Retrieving similar contracts for query: '{query_text[:50]}...'")
        
        try:
            # Step 1: Generate query embedding (with timeout protection)
            logger.info("Step 1: Generating query embedding...")
            embedding_start = time.time()
            query_embedding = self.embedding_service.generate_embedding(query_text)
            logger.info(f"Embedding generated in {time.time() - embedding_start:.2f}s")
            query_embeddings = [query_embedding.tolist()]
            
            # Step 2: Build metadata filter
            logger.info("Step 2: Building metadata filter...")
            where_clause = self._build_where_clause(filters) if filters else None
            
            # Step 3: Query ChromaDB
            logger.info("Step 3: Querying ChromaDB...")
            query_start = time.time()
            results = self.chroma_client.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where_clause,
            )
            logger.info(f"ChromaDB query completed in {time.time() - query_start:.2f}s")
            
            # Step 4: Format results
            logger.info("Step 4: Formatting results...")
            formatted_results = self._format_results(results)
            
            total_time = time.time() - start_time
            logger.info(f"Retrieved {len(formatted_results)} similar chunks in {total_time:.2f}s")
            return formatted_results
        except Exception as e:
            logger.error(f"Error in retrieve_similar_contracts: {e}", exc_info=True)
            # Return empty list instead of crashing
            logger.warning("Returning empty results due to error")
            return []
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build ChromaDB where clause from filters.
        
        ChromaDB requires filters to use $and operator when multiple conditions exist.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            ChromaDB where clause dictionary with $and operator, or None if no filters
        """
        if not filters:
            return None
        
        # If only one filter, return it directly
        if len(filters) == 1:
            key, value = next(iter(filters.items()))
            if isinstance(value, list):
                return {key: {"$in": value}}
            else:
                return {key: {"$eq": value}}
        
        # Multiple filters: use $and operator
        conditions = []
        for key, value in filters.items():
            if isinstance(value, list):
                # Multiple values: use $in
                conditions.append({key: {"$in": value}})
            elif isinstance(value, (int, float)):
                # Numeric: use $eq
                conditions.append({key: {"$eq": value}})
            else:
                # String: use $eq
                conditions.append({key: {"$eq": value}})
        
        return {"$and": conditions}
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format ChromaDB results into a clean structure.
        
        Args:
            results: Raw ChromaDB query results
            
        Returns:
            List of formatted result dictionaries
        """
        formatted = []
        
        # ChromaDB returns lists of lists (one per query)
        ids = results.get("ids", [[]])[0] if results.get("ids") else []
        documents = results.get("documents", [[]])[0] if results.get("documents") else []
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []
        
        for i in range(len(ids)):
            # Convert distance to similarity score (ChromaDB uses cosine distance)
            # Cosine distance = 1 - cosine similarity
            # So similarity = 1 - distance
            similarity_score = 1.0 - distances[i] if distances else 0.0
            
            formatted.append({
                "id": ids[i],
                "text": documents[i],
                "similarity_score": similarity_score,
                "metadata": metadatas[i] if metadatas else {},
                "contract_id": metadatas[i].get("contract_id", "unknown") if metadatas else "unknown",
                "clause_type": metadatas[i].get("clause_type", "general") if metadatas else "general",
            })
        
        # Sort by similarity (highest first)
        formatted.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return formatted
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        return self.chroma_client.get_collection_stats()

