"""
Embedding service for generating vector embeddings.
Uses Google's text-embedding-004 model for high-quality embeddings.
"""
from typing import List, Optional, Union
import numpy as np
import time
from loguru import logger

from app.config import settings


class EmbeddingService:
    """
    Service for generating text embeddings using Google's embedding models.
    
    Design choices:
    1. Google embeddings: High quality, cost-effective
    2. Batch processing: Efficient for multiple texts
    3. Caching: Could be added later for cost optimization
    4. Type safety: Returns numpy arrays for compatibility
    """
    
    def __init__(self):
        self.provider = settings.embedding_provider
        self.model = settings.embedding_model
        
        # Initialize Google Generative AI client
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                if not settings.google_api_key:
                    raise ValueError("GOOGLE_API_KEY not set for embeddings")
                genai.configure(api_key=settings.google_api_key)
                self.client = genai
                logger.info(f"Initialized Google embeddings with model {self.model}")
            except ImportError:
                raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        else:
            raise ValueError(f"Unknown embedding provider: {self.provider}. Expected 'gemini'")
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process per API call
            
        Returns:
            numpy array of shape (num_texts, embedding_dim)
        """
        if not texts:
            return np.array([])
        
        logger.info(f"Generating embeddings for {len(texts)} texts using {self.provider}")
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)
            logger.debug(f"Processed batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")
        
        embeddings_array = np.array(all_embeddings)
        logger.info(f"Generated embeddings with shape {embeddings_array.shape}")
        
        return embeddings_array
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        Optimized for single embeddings (no batch overhead, no delays).
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        # Reuse batch logic for consistency, but optimized for single item
        embeddings = self._embed_batch([text], task_type="retrieval_query")
        if embeddings and len(embeddings) > 0:
            return np.array(embeddings[0])
        raise ValueError("Failed to generate embedding")
    
    def _embed_batch(self, texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Uses serial embedding for reliability (batch API can return single embedding 
        for list input on some SDK versions).
        """
        # Always use serial for reliability - batch mode has issues
        return self._embed_batch_serial(texts, task_type)

    def _embed_batch_optimized(self, texts: List[str], task_type: str) -> List[List[float]]:
        """Use genai.embed_content with list input (if supported) or batch_embed_contents."""
        # Using Google's batch embedding if possible
        # Note: The SDK method name varies by version, we try the most common ones
        
        max_retries = 5
        base_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Prepare content
                model = self.model
                if "models/" not in model:
                    model = f"models/{model}"
                
                # Check directly for embed_content support with list
                # This is supported in newer google-generativeai versions
                result = self.client.embed_content(
                    model=model,
                    content=texts,
                    task_type=task_type,
                )
                
                # Parse result
                if isinstance(result, dict) and 'embedding' in result:
                    # Single result wrapped? unlikely if we sent list
                    return [result['embedding']]
                elif hasattr(result, 'embeddings'):
                     # stored in result.embeddings list
                     return [e for e in result.embeddings]
                elif isinstance(result, dict) and 'embeddings' in result:
                     return result['embeddings']
                else:
                    # If it returned a single embedding for a list, it failed batching
                    # Fallback to serial
                    raise ValueError("API returned single embedding for batch input")

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower() or "503" in error_str:
                    delay = base_delay * (2 ** attempt) # 5, 10, 20, 40, 80
                    # Add jitter
                    import random
                    delay += random.uniform(0, 2)
                    
                    logger.warning(f"Rate limit during batch embedding. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    raise e
        
        raise ValueError("Failed to embed batch after retries")

    def _embed_batch_serial(self, texts: List[str], task_type: str) -> List[List[float]]:
        """Fallback to serial embedding with smart rate limiting."""
        embeddings = []
        
        for i, text in enumerate(texts):
            max_retries = 3
            base_delay = 1
            
            for attempt in range(max_retries):
                try:
                    result = self.client.embed_content(
                        model=self.model,
                        content=text,
                        task_type=task_type
                    )
                    
                    if isinstance(result, dict):
                        embedding = result.get('embedding', result.get('values', []))
                    else:
                        embedding = result
                        
                    if not embedding:
                        raise ValueError("Empty embedding returned")
                        
                    embeddings.append(embedding)
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.warning(f"Rate limit. Retrying {i+1}/{len(texts)} in {delay}s...")
                            time.sleep(delay)
                            continue
                    
                    logger.error(f"Failed to embed text {i}: {e}")
                    # On final failure, maybe append zero vector or raise? 
                    # Raising ensures data integrity.
                    raise e
                    
        return embeddings

