"""
Context Manager Module

Manages conversation context, message history, and context window optimization.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a single message in the conversation."""

    role: str  # system, user, assistant, tool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None


class ContextManager:
    """
    Manages the agent's conversation context and memory.

    Features:
    - Message history tracking
    - Context window management
    - System prompt handling
    - Context summarization for long conversations
    """

    def __init__(self, max_length: int = 4096):
        """
        Initialize context manager.

        Args:
            max_length: Maximum context length (in tokens, approximate)
        """
        self.max_length = max_length
        self.messages: List[Message] = []
        self.system_prompt: Optional[str] = None
        self.context_data: Dict[str, Any] = {}

    def set_system_prompt(self, prompt: str):
        """Set the system prompt."""
        self.system_prompt = prompt
        logger.debug(f"System prompt set: {prompt[:100]}...")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the context."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)

        # Trim context if needed
        self._trim_context()

    def add_user_message(self, content: str, metadata: Optional[Dict] = None):
        """Convenience method to add user message."""
        self.add_message("user", content, metadata)

    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None):
        """Convenience method to add assistant message."""
        self.add_message("assistant", content, metadata)

    def add_tool_message(self, content: str, tool_name: str, metadata: Optional[Dict] = None):
        """Add a tool execution result."""
        metadata = metadata or {}
        metadata["tool_name"] = tool_name
        self.add_message("tool", content, metadata)

    def add_context(self, data: Dict[str, Any]):
        """Add additional context data."""
        self.context_data.update(data)

    def get_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get messages in API-compatible format.

        Args:
            include_system: Whether to include system message

        Returns:
            List of message dictionaries
        """
        result = []

        # Add system prompt if present
        if include_system and self.system_prompt:
            result.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add conversation messages
        for msg in self.messages:
            result.append({
                "role": msg.role,
                "content": msg.content
            })

        return result

    def get_last_n_messages(self, n: int) -> List[Message]:
        """Get the last N messages."""
        return self.messages[-n:] if n > 0 else []

    def get_context_string(self) -> str:
        """Get full context as a string."""
        parts = []

        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")

        for msg in self.messages:
            parts.append(f"{msg.role.capitalize()}: {msg.content}")

        return "\n\n".join(parts)

    def _trim_context(self):
        """
        Trim context to fit within max_length.

        This is a simple implementation that removes oldest messages.
        More sophisticated approaches could:
        - Use actual token counting
        - Summarize old messages instead of dropping
        - Keep important messages based on metadata
        """
        # Rough estimate: 1 token ~ 4 characters
        estimated_tokens = sum(len(msg.content) for msg in self.messages) // 4

        if self.system_prompt:
            estimated_tokens += len(self.system_prompt) // 4

        # Remove oldest messages if over limit
        while estimated_tokens > self.max_length and len(self.messages) > 1:
            removed = self.messages.pop(0)
            estimated_tokens -= len(removed.content) // 4
            logger.debug(f"Trimmed message from context (role={removed.role})")

    def summarize_context(self) -> str:
        """
        Create a summary of the conversation context.

        This is useful for memory evolution strategies.

        Returns:
            Summary string
        """
        if not self.messages:
            return "No conversation history"

        # Simple summarization - count messages by role
        role_counts = {}
        for msg in self.messages:
            role_counts[msg.role] = role_counts.get(msg.role, 0) + 1

        summary_parts = [
            f"Conversation contains {len(self.messages)} messages:",
            *[f"- {count} {role} messages" for role, count in role_counts.items()]
        ]

        # Add last user message for context
        last_user_msgs = [m for m in self.messages if m.role == "user"]
        if last_user_msgs:
            last_user = last_user_msgs[-1].content
            summary_parts.append(f"\nLast user message: {last_user[:200]}...")

        return "\n".join(summary_parts)

    def clear(self):
        """Clear all messages (keeps system prompt)."""
        self.messages = []
        self.context_data = {}
        logger.debug("Context cleared")

    def reset(self):
        """Full reset including system prompt."""
        self.messages = []
        self.system_prompt = None
        self.context_data = {}
        logger.debug("Context fully reset")

    def export_messages(self) -> List[Dict[str, Any]]:
        """Export messages for saving/analysis."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.metadata
            }
            for msg in self.messages
        ]

    def load_messages(self, messages: List[Dict[str, Any]]):
        """Load messages from exported format."""
        self.messages = []
        for msg_dict in messages:
            self.add_message(
                role=msg_dict["role"],
                content=msg_dict["content"],
                metadata=msg_dict.get("metadata")
            )

    def __len__(self) -> int:
        """Return number of messages."""
        return len(self.messages)

    def __repr__(self) -> str:
        return f"ContextManager(messages={len(self.messages)}, max_length={self.max_length})"
