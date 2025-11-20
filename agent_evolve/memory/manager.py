"""
Memory Manager Module

Manages the agent's dynamic memory including:
- Short-term memory (recent interactions)
- Long-term memory (persistent knowledge)
- Memory evolution and optimization
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """Represents a single memory item."""

    content: str
    memory_type: str  # 'episodic', 'semantic', 'procedural'
    importance: float = 0.5  # 0.0 to 1.0
    timestamp: Optional[float] = None
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryManager:
    """
    Manages agent memory with support for evolution.

    Features:
    - Short-term and long-term memory separation
    - Importance-based retention
    - Memory retrieval by relevance
    - Memory evolution (learning what to remember)
    """

    def __init__(
        self,
        short_term_capacity: int = 10,
        long_term_capacity: int = 100,
        use_vector_store: bool = False
    ):
        """
        Initialize memory manager.

        Args:
            short_term_capacity: Max items in short-term memory
            long_term_capacity: Max items in long-term memory
            use_vector_store: Whether to use vector database for semantic search
        """
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self.use_vector_store = use_vector_store

        self.short_term: List[Memory] = []
        self.long_term: List[Memory] = []

        self.vector_store = None
        if use_vector_store:
            self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize vector database for semantic memory retrieval."""
        try:
            from agent_evolve.memory.store import MemoryStore
            self.vector_store = MemoryStore()
            logger.info("Vector store initialized for semantic memory")
        except Exception as e:
            logger.warning(f"Could not initialize vector store: {e}")
            self.use_vector_store = False

    def add_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        importance: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> Memory:
        """
        Add a new memory.

        Args:
            content: Memory content
            memory_type: Type of memory (episodic, semantic, procedural)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            Created Memory object
        """
        memory = Memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {}
        )

        # Add to short-term memory
        self.short_term.append(memory)

        # Trim short-term if needed
        if len(self.short_term) > self.short_term_capacity:
            self._consolidate_memory()

        # Add to vector store if available
        if self.vector_store:
            self.vector_store.add_memory(memory)

        logger.debug(f"Added memory: {content[:50]}... (importance={importance})")

        return memory

    def retrieve_relevant(
        self,
        query: str,
        k: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Memory]:
        """
        Retrieve k most relevant memories for a query.

        Args:
            query: Query string
            k: Number of memories to retrieve
            memory_type: Filter by memory type

        Returns:
            List of relevant memories
        """
        if self.vector_store:
            # Use semantic search
            results = self.vector_store.search(query, k=k)
        else:
            # Use simple keyword matching
            all_memories = self.short_term + self.long_term
            if memory_type:
                all_memories = [m for m in all_memories if m.memory_type == memory_type]

            # Simple scoring based on keyword overlap
            results = sorted(
                all_memories,
                key=lambda m: self._keyword_score(query, m.content),
                reverse=True
            )[:k]

        # Update access counts
        for memory in results:
            memory.access_count += 1

        logger.debug(f"Retrieved {len(results)} memories for query: {query[:50]}...")
        return results

    def _keyword_score(self, query: str, content: str) -> float:
        """Simple keyword-based relevance scoring."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        overlap = len(query_words & content_words)
        return overlap / max(len(query_words), 1)

    def _consolidate_memory(self):
        """
        Move memories from short-term to long-term based on importance.

        This implements a simple memory consolidation strategy.
        More sophisticated approaches could:
        - Learn importance based on feedback
        - Cluster similar memories
        - Generate summaries of episodic memories
        """
        # Sort short-term memories by importance
        sorted_memories = sorted(
            self.short_term,
            key=lambda m: m.importance * (1 + m.access_count * 0.1),
            reverse=True
        )

        # Keep top items in short-term
        self.short_term = sorted_memories[:self.short_term_capacity // 2]

        # Promote important items to long-term
        to_promote = sorted_memories[self.short_term_capacity // 2:]
        for memory in to_promote:
            if memory.importance > 0.6 or memory.access_count > 2:
                self.long_term.append(memory)

        # Trim long-term if needed
        if len(self.long_term) > self.long_term_capacity:
            self.long_term = sorted(
                self.long_term,
                key=lambda m: m.importance * (1 + m.access_count * 0.1),
                reverse=True
            )[:self.long_term_capacity]

        logger.debug(f"Memory consolidated: ST={len(self.short_term)}, LT={len(self.long_term)}")

    def summarize_memories(self) -> str:
        """
        Create a summary of important memories.

        This is useful for providing context to the agent.
        """
        if not self.long_term and not self.short_term:
            return "No memories available."

        # Get most important memories
        all_memories = self.short_term + self.long_term
        important = sorted(
            all_memories,
            key=lambda m: m.importance * (1 + m.access_count * 0.1),
            reverse=True
        )[:10]

        summary_parts = ["Important memories:"]
        for i, mem in enumerate(important, 1):
            summary_parts.append(f"{i}. {mem.content[:100]}...")

        return "\n".join(summary_parts)

    def get_all_memories(self) -> List[Memory]:
        """Get all memories (short-term + long-term)."""
        return self.short_term + self.long_term

    def clear_short_term(self):
        """Clear short-term memory."""
        self.short_term = []
        logger.debug("Short-term memory cleared")

    def clear_all(self):
        """Clear all memories."""
        self.short_term = []
        self.long_term = []
        if self.vector_store:
            self.vector_store.clear()
        logger.info("All memories cleared")

    def export_memories(self) -> Dict[str, Any]:
        """Export memories for saving."""
        return {
            "short_term": [
                {
                    "content": m.content,
                    "memory_type": m.memory_type,
                    "importance": m.importance,
                    "access_count": m.access_count,
                    "metadata": m.metadata
                }
                for m in self.short_term
            ],
            "long_term": [
                {
                    "content": m.content,
                    "memory_type": m.memory_type,
                    "importance": m.importance,
                    "access_count": m.access_count,
                    "metadata": m.metadata
                }
                for m in self.long_term
            ]
        }

    def load_memories(self, data: Dict[str, Any]):
        """Load memories from exported format."""
        self.short_term = []
        self.long_term = []

        for mem_dict in data.get("short_term", []):
            memory = Memory(**mem_dict)
            self.short_term.append(memory)

        for mem_dict in data.get("long_term", []):
            memory = Memory(**mem_dict)
            self.long_term.append(memory)

        logger.info(f"Loaded {len(self.short_term)} ST and {len(self.long_term)} LT memories")

    def evolve_memory_strategy(self, feedback: Dict[str, Any]):
        """
        Evolve memory retention strategy based on feedback.

        This placeholder method would be implemented by evolution strategies
        to optimize what the agent remembers.

        Args:
            feedback: Performance feedback to guide memory evolution
        """
        # Placeholder for memory evolution logic
        # Could adjust importance thresholds, capacity, etc.
        logger.debug("Memory evolution strategy invoked")
        pass

    def __repr__(self) -> str:
        return (
            f"MemoryManager(ST={len(self.short_term)}, "
            f"LT={len(self.long_term)}, "
            f"vector_store={self.vector_store is not None})"
        )
