"""
Agent Evolve - A Self-Evolving AI Agent Platform

This package provides a comprehensive framework for building AI agents that
continuously improve through various evolution strategies.
"""

__version__ = "0.1.0"

from agent_evolve.core.agent import AgentCore
from agent_evolve.optimizer.evolutionary import EvolutionaryOptimizer
from agent_evolve.evaluator.base import BaseEvaluator
from agent_evolve.memory.manager import MemoryManager
from agent_evolve.tools.interface import ToolInterface

__all__ = [
    "AgentCore",
    "EvolutionaryOptimizer",
    "BaseEvaluator",
    "MemoryManager",
    "ToolInterface",
]
