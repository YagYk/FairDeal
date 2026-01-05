"""
ChromaDB client for vector storage and retrieval.
Handles collection management and querying.
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from loguru import logger
import uuid

from app.config import settings


class ChromaClient:
    """
    Client for interacting with ChromaDB vector database.
    
    Design choices:
    1. Persistent storage: ChromaDB stores data on disk
    2. Metadata filtering: Enables filtering by contract_type, industry, etc.
    3. Collection-based: One collection per project for isolation
    4. ID management: Uses UUIDs for unique document identification
    """
    
    def __init__(self):
        self.db_path = str(settings.get_chroma_db_path())
        self.collection_name = settings.chroma_collection_name
        
        # Initialize ChromaDB client (persistent mode)
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Contract chunks for RAG retrieval"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        contract_metadata: Dict[str, Any],
    ) -> None:
        """
        Add contract chunks to ChromaDB.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'clause_type'
            embeddings: List of embedding vectors (one per chunk)
            contract_metadata: Contract-level metadata to attach to all chunks
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        logger.info(f"Adding {len(chunks)} chunks to ChromaDB")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        embedding_list = []
        
        for i, chunk in enumerate(chunks):
            # Generate unique ID
            chunk_id = f"{contract_metadata.get('contract_id', 'unknown')}_chunk_{chunk.get('chunk_index', i)}"
            ids.append(chunk_id)
            
            # Document text
            documents.append(chunk["text"])
            
            # Combine chunk-level and contract-level metadata
            metadata = {
                **contract_metadata,  # Contract-level metadata
                "clause_type": chunk.get("clause_type", "general"),
                "chunk_index": chunk.get("chunk_index", i),
            }
            metadatas.append(metadata)
            
            # Embedding
            embedding_list.append(embeddings[i].tolist() if hasattr(embeddings[i], 'tolist') else embeddings[i])
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embedding_list,
            )
            logger.info(f"Successfully added {len(chunks)} chunks to collection")
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {e}")
            raise
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 20,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query ChromaDB for similar chunks.
        
        Args:
            query_embeddings: Query embedding vectors
            n_results: Number of results to return
            where: Metadata filter (e.g., {"contract_type": "employment"})
            where_document: Document content filter (e.g., {"$contains": "notice period"})
            
        Returns:
            Dictionary with 'ids', 'documents', 'metadatas', 'distances'
        """
        logger.info(f"Querying ChromaDB with n_results={n_results}")
        
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )
            
            logger.info(f"Retrieved {len(results.get('ids', [])[0] if results.get('ids') else [])} results")
            return results
            
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def delete_collection(self) -> None:
        """
        Delete the entire collection (use with caution!).
        """
        logger.warning(f"Deleting collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)
        # Recreate empty collection
        self.collection = self.client.create_collection(name=self.collection_name)

