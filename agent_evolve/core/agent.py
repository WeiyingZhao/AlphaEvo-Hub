"""
Agent Core Module

This module implements the core agent system with LLM integration,
context management, and action orchestration.
"""

from typing import Any, Dict, List, Optional, Union
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the AI agent."""

    model_name: str = "gpt-3.5-turbo"
    model_provider: str = "openai"  # openai, anthropic, huggingface
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    system_prompt: Optional[str] = None
    use_tools: bool = True
    enable_memory: bool = True
    max_context_length: int = 4096
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Current state of the agent."""

    generation: int = 0
    task_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_scores: List[float] = field(default_factory=list)
    best_score: float = 0.0
    current_prompt: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCore:
    """
    Core agent system that drives reasoning and behavior.

    The Agent Core includes:
    - LLM integration for reasoning
    - Context management for multi-turn interactions
    - Tool orchestration for external action execution
    - State management across evolution iterations

    Attributes:
        config: Agent configuration
        state: Current agent state
        context_manager: Manages conversation context
        controller: Orchestrates agent actions
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        model: Optional[str] = None,
        task: Optional[str] = None,
        _skip_init: bool = False
    ):
        """
        Initialize the Agent Core.

        Args:
            config: Agent configuration object
            model: Model name (if config not provided)
            task: Task description for the agent
            _skip_init: Internal flag to skip initialization (for loading from config)
        """
        # Set up configuration
        if config is None:
            config = AgentConfig()
        if model:
            config.model_name = model
            # Auto-detect provider from model name
            config.model_provider = self._detect_provider(model)
        if task:
            config.metadata["task"] = task

        self.config = config
        self.state = AgentState()

        # Initialize components (unless skipped for loading)
        if not _skip_init:
            self._initialize_model()
            self._initialize_context_manager()
            self._initialize_controller()

            logger.info(f"AgentCore initialized with model: {config.model_name}")

    def _detect_provider(self, model_name: str) -> str:
        """
        Auto-detect LLM provider from model name.

        Args:
            model_name: The name of the model

        Returns:
            Provider name (openai, anthropic, huggingface, or mock)
        """
        model_lower = model_name.lower()

        # Check for mock
        if model_lower == "mock" or "mock" in model_lower:
            return "mock"

        # Check for Anthropic/Claude models
        if "claude" in model_lower or "anthropic" in model_lower:
            return "anthropic"

        # Check for common HuggingFace model patterns
        if any(pattern in model_lower for pattern in [
            "llama", "mistral", "falcon", "gpt-j", "gpt-neo",
            "opt-", "bloom", "pythia", "dolly", "vicuna"
        ]):
            return "huggingface"

        # Check for OpenAI models (gpt-3.5, gpt-4, etc.)
        if "gpt" in model_lower or "davinci" in model_lower or "turbo" in model_lower:
            return "openai"

        # Default to OpenAI if can't detect
        logger.warning(f"Could not auto-detect provider for model '{model_name}', defaulting to 'openai'")
        return "openai"

    def _initialize_model(self):
        """Initialize the LLM based on configuration."""
        from agent_evolve.core.llm import get_llm
        self.llm = get_llm(
            provider=self.config.model_provider,
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        logger.debug("LLM initialized")

    def _initialize_context_manager(self):
        """Initialize context management system."""
        from agent_evolve.core.context import ContextManager
        self.context_manager = ContextManager(
            max_length=self.config.max_context_length
        )
        if self.config.system_prompt:
            self.context_manager.set_system_prompt(self.config.system_prompt)
        logger.debug("Context manager initialized")

    def _initialize_controller(self):
        """Initialize the action controller."""
        from agent_evolve.core.controller import AgentController
        self.controller = AgentController(
            agent=self,
            use_tools=self.config.use_tools
        )
        logger.debug("Controller initialized")

    def run(
        self,
        task: str,
        max_iterations: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using the agent.

        Args:
            task: Task description or query
            max_iterations: Maximum reasoning iterations
            context: Additional context for the task

        Returns:
            Result dictionary with solution, reasoning trace, and metadata
        """
        logger.info(f"Running task: {task[:100]}...")

        # Add task to context
        self.context_manager.add_user_message(task)
        if context:
            self.context_manager.add_context(context)

        # Execute reasoning loop
        result = self.controller.execute_task(
            task=task,
            max_iterations=max_iterations
        )

        # Update state
        self.state.task_history.append({
            "task": task,
            "result": result,
            "generation": self.state.generation
        })

        return result

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: Input prompt

        Returns:
            Generated text response
        """
        messages = self.context_manager.get_messages()
        messages.append({"role": "user", "content": prompt})

        response = self.llm.generate(messages)

        # Add to context
        self.context_manager.add_assistant_message(response)

        return response

    def update_config(self, **kwargs):
        """
        Update agent configuration.

        This allows evolution strategies to modify the agent's parameters.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug(f"Updated config: {key}={value}")

    def update_prompt(self, new_prompt: str):
        """
        Update the system prompt.

        Used by prompt evolution strategies.
        """
        self.config.system_prompt = new_prompt
        self.state.current_prompt = new_prompt
        self.context_manager.set_system_prompt(new_prompt)
        logger.info("System prompt updated")

    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state

    def set_state(self, state: AgentState):
        """Set agent state (for loading evolved agents)."""
        self.state = state

    def export_config(self) -> Dict[str, Any]:
        """Export current configuration for saving."""
        return {
            "config": {
                "model_name": self.config.model_name,
                "model_provider": self.config.model_provider,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "system_prompt": self.config.system_prompt,
                "use_tools": self.config.use_tools,
                "metadata": self.config.metadata
            },
            "state": {
                "generation": self.state.generation,
                "best_score": self.state.best_score,
                "current_prompt": self.state.current_prompt,
                "tools_used": self.state.tools_used
            }
        }

    def load_config(self, config_dict: Dict[str, Any]):
        """Load configuration from dictionary."""
        if "config" in config_dict:
            for key, value in config_dict["config"].items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

        if "state" in config_dict:
            for key, value in config_dict["state"].items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)

        # Reinitialize all components with new config
        self._initialize_model()

        # Initialize context manager if it doesn't exist
        if not hasattr(self, 'context_manager'):
            self._initialize_context_manager()

        if self.config.system_prompt:
            self.context_manager.set_system_prompt(self.config.system_prompt)

        # Initialize controller if it doesn't exist
        if not hasattr(self, 'controller'):
            self._initialize_controller()

    def reset(self):
        """Reset agent state for new task."""
        self.context_manager.clear()
        if self.config.system_prompt:
            self.context_manager.set_system_prompt(self.config.system_prompt)
        logger.info("Agent reset")

    def __repr__(self) -> str:
        return (
            f"AgentCore(model={self.config.model_name}, "
            f"generation={self.state.generation}, "
            f"best_score={self.state.best_score:.4f})"
        )
