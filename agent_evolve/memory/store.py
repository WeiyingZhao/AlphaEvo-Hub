"""
Vector Memory Store

Provides semantic memory storage and retrieval using embeddings.
"""

from typing import List, Optional, Any, Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Vector-based memory store for semantic retrieval.

    Uses sentence embeddings and vector similarity search.
    """

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store.

        Args:
            embedding_model: Model name for sentence embeddings
        """
        self.embedding_model_name = embedding_model
        self.embeddings_cache = []
        self.memories = []

        self._initialize_embedding_model()

    def _initialize_embedding_model(self):
        """Initialize embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Embedding model initialized: {self.embedding_model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed, using fallback")
            self.embedding_model = None

    def add_memory(self, memory):
        """
        Add a memory to the store.

        Args:
            memory: Memory object to add
        """
        self.memories.append(memory)

        if self.embedding_model:
            # Generate embedding
            embedding = self.embedding_model.encode(memory.content)
            self.embeddings_cache.append(embedding)
        else:
            # Fallback: store None
            self.embeddings_cache.append(None)

        logger.debug(f"Memory added to vector store: {memory.content[:50]}...")

    def search(self, query: str, k: int = 5) -> List:
        """
        Search for k most relevant memories.

        Args:
            query: Query string
            k: Number of results to return

        Returns:
            List of Memory objects
        """
        if not self.memories:
            return []

        if self.embedding_model and self.embeddings_cache[0] is not None:
            # Semantic search using embeddings
            query_embedding = self.embedding_model.encode(query)
            scores = [
                self._cosine_similarity(query_embedding, mem_emb)
                if mem_emb is not None else 0.0
                for mem_emb in self.embeddings_cache
            ]

            # Get top k indices
            top_k_indices = np.argsort(scores)[::-1][:k]
            results = [self.memories[i] for i in top_k_indices]

        else:
            # Fallback to keyword matching
            scores = [
                self._keyword_overlap(query, mem.content)
                for mem in self.memories
            ]
            top_k_indices = np.argsort(scores)[::-1][:k]
            results = [self.memories[i] for i in top_k_indices]

        logger.debug(f"Vector search returned {len(results)} results")
        return results

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _keyword_overlap(self, query: str, text: str) -> float:
        """Simple keyword overlap score."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        overlap = len(query_words & text_words)
        return overlap / max(len(query_words), 1)

    def clear(self):
        """Clear all memories from store."""
        self.memories = []
        self.embeddings_cache = []
        logger.debug("Vector store cleared")

    def __len__(self) -> int:
        return len(self.memories)

    def __repr__(self) -> str:
        return f"MemoryStore(size={len(self.memories)}, model={self.embedding_model_name})"
