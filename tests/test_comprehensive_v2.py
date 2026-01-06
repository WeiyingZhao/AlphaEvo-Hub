#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agent Evolve

Tests core functionality, evolution strategies, integration, and robustness.
Designed to be fast (< 30 seconds total), CPU-only, and deterministic.

Run with:
    pytest tests/test_comprehensive_v2.py -v
    pytest tests/test_comprehensive_v2.py -v --tb=short  # Short traceback
    pytest tests/test_comprehensive_v2.py -k test_agent  # Run specific tests
"""

import pytest
import sys
import tempfile
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.core.llm import get_llm, MockLLM, BaseLLM
from agent_evolve.core.context import ContextManager, Message
from agent_evolve.core.controller import AgentController
from agent_evolve.evaluator import QAEvaluator
from agent_evolve.evaluator.base import BaseEvaluator, EvaluationResult, MetricEvaluator
from agent_evolve.optimizer.evolutionary import EvolutionConfig, EvolutionResult
from agent_evolve.optimizer.strategies import (
    PromptEvolutionStrategy,
    MemoryEvolutionStrategy,
    ToolEvolutionStrategy,
    CodeEvolutionStrategy
)


# ============================================================================
# UNIT TESTS: Core Components
# ============================================================================

class TestLLMProviders:
    """Test LLM provider integration."""

    def test_mock_llm_basic(self):
        """Test mock LLM basic functionality."""
        llm = MockLLM(model_name="mock")
        response = llm.generate([{"role": "user", "content": "Hello"}])
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Mock response" in response

    def test_mock_llm_streaming(self):
        """Test mock LLM streaming."""
        llm = MockLLM(model_name="mock")
        chunks = list(llm.generate_stream([{"role": "user", "content": "Hi"}]))
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_get_llm_factory_mock(self):
        """Test LLM factory with mock provider."""
        llm = get_llm("mock", "mock-model")
        assert isinstance(llm, MockLLM)
        assert isinstance(llm, BaseLLM)

    def test_get_llm_factory_invalid(self):
        """Test LLM factory with invalid provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_llm("invalid_provider", "model")

    def test_llm_temperature_config(self):
        """Test LLM configuration parameters."""
        llm = get_llm("mock", "mock", temperature=0.8, max_tokens=1024)
        assert llm.temperature == 0.8
        assert llm.max_tokens == 1024


class TestContextManager:
    """Test context management."""

    def test_context_creation(self):
        """Test basic context manager creation."""
        ctx = ContextManager(max_length=100)
        assert len(ctx) == 0
        assert ctx.max_length == 100

    def test_add_messages(self):
        """Test adding messages."""
        ctx = ContextManager()
        ctx.set_system_prompt("You are helpful")
        ctx.add_user_message("Hello")
        ctx.add_assistant_message("Hi there")

        messages = ctx.get_messages()
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"

    def test_context_trim(self):
        """Test context trimming."""
        ctx = ContextManager(max_length=100)
        # Add many messages to exceed limit
        for i in range(50):
            ctx.add_user_message("x" * 20)  # 20 chars each
        # Should have trimmed old messages
        assert len(ctx) < 50

    def test_context_clear(self):
        """Test context clearing."""
        ctx = ContextManager()
        ctx.add_user_message("Test")
        assert len(ctx) == 1
        ctx.clear()
        assert len(ctx) == 0

    def test_context_export_load(self):
        """Test exporting and loading messages."""
        ctx = ContextManager()
        ctx.add_user_message("Hello")
        ctx.add_assistant_message("Hi")

        exported = ctx.export_messages()
        assert len(exported) == 2

        ctx2 = ContextManager()
        ctx2.load_messages(exported)
        assert len(ctx2) == 2


class TestAgentCore:
    """Test agent core functionality."""

    def test_agent_creation_default(self):
        """Test agent creation with defaults."""
        agent = AgentCore(model="mock")
        assert agent.config.model_name == "mock"
        assert agent.config.model_provider == "mock"
        assert hasattr(agent, 'llm')
        assert hasattr(agent, 'context_manager')
        assert hasattr(agent, 'controller')

    def test_agent_creation_with_task(self):
        """Test agent creation with task."""
        agent = AgentCore(model="mock", task="Answer questions")
        assert agent.config.metadata.get("task") == "Answer questions"

    def test_agent_provider_detection_openai(self):
        """Test provider auto-detection for OpenAI."""
        # Test detection method directly to avoid API key requirements
        agent = AgentCore(model="mock", _skip_init=True)
        assert agent._detect_provider("gpt-3.5-turbo") == "openai"
        assert agent._detect_provider("gpt-4") == "openai"
        assert agent._detect_provider("gpt-4-turbo") == "openai"

    def test_agent_provider_detection_anthropic(self):
        """Test provider auto-detection for Anthropic."""
        # Test detection method directly to avoid API key requirements
        agent = AgentCore(model="mock", _skip_init=True)
        assert agent._detect_provider("claude-3-sonnet-20240229") == "anthropic"
        assert agent._detect_provider("claude-3-opus") == "anthropic"
        assert agent._detect_provider("anthropic-model") == "anthropic"

    def test_agent_provider_detection_huggingface(self):
        """Test provider auto-detection for HuggingFace."""
        # Test detection method directly to avoid API key requirements
        agent = AgentCore(model="mock", _skip_init=True)
        assert agent._detect_provider("llama-7b") == "huggingface"
        assert agent._detect_provider("mistral-7b") == "huggingface"
        assert agent._detect_provider("falcon-40b") == "huggingface"

    def test_agent_generate_response(self):
        """Test agent response generation."""
        agent = AgentCore(model="mock")
        response = agent.generate_response("What is 2+2?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_agent_config_export_load(self):
        """Test exporting and loading agent config."""
        agent = AgentCore(model="mock", task="Test task")
        agent.update_prompt("Custom prompt")

        config = agent.export_config()
        assert "config" in config
        assert "state" in config

        agent2 = AgentCore(_skip_init=True)
        agent2.load_config(config)
        assert agent2.config.system_prompt == "Custom prompt"

    def test_agent_reset(self):
        """Test agent reset functionality."""
        agent = AgentCore(model="mock")
        agent.generate_response("Test")
        assert len(agent.context_manager) > 0
        agent.reset()
        assert len(agent.context_manager) == 0


class TestEvaluators:
    """Test evaluator functionality."""

    def test_qa_evaluator_creation(self):
        """Test QA evaluator creation."""
        qa_pairs = [
            {"question": "What is 2+2?", "answer": "4"},
            {"question": "Capital of France?", "answer": "Paris"}
        ]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)
        assert len(evaluator.qa_pairs) == 2

    def test_qa_evaluator_find_reference(self):
        """Test finding reference answers."""
        qa_pairs = [{"question": "What is 2+2?", "answer": "4"}]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)
        ref = evaluator._find_reference_answer("What is 2+2?")
        assert ref == "4"

    def test_qa_evaluator_similarity(self):
        """Test answer similarity computation."""
        evaluator = QAEvaluator()
        # Exact match
        sim = evaluator._compute_similarity("Paris", "Paris")
        assert sim == 1.0
        # Partial match
        sim = evaluator._compute_similarity("The capital is Paris", "Paris")
        assert sim > 0
        # No match
        sim = evaluator._compute_similarity("London", "Paris")
        assert sim == 0.0

    def test_metric_evaluator(self):
        """Test custom metric evaluator."""
        def simple_metric(output, expected):
            return 1.0 if output == expected else 0.0

        evaluator = MetricEvaluator(metric_fn=simple_metric)
        assert evaluator.metric_fn("test", "test") == 1.0


class TestEvolutionStrategies:
    """Test evolution strategy implementations."""

    def test_prompt_strategy_generate_variant(self):
        """Test prompt strategy variant generation."""
        strategy = PromptEvolutionStrategy()
        config = {"config": {"system_prompt": "You are helpful"}}
        variant = strategy.generate_variant(config)
        assert "config" in variant
        assert "system_prompt" in variant["config"]

    def test_prompt_strategy_mutate(self):
        """Test prompt strategy mutation."""
        strategy = PromptEvolutionStrategy()
        config = {"config": {"system_prompt": "You are helpful"}}
        mutated = strategy.mutate(config)
        assert "system_prompt" in mutated["config"]

    def test_memory_strategy_generate_variant(self):
        """Test memory strategy variant generation."""
        strategy = MemoryEvolutionStrategy()
        config = {"config": {}}
        variant = strategy.generate_variant(config)
        assert "memory" in variant

    def test_tool_strategy_generate_variant(self):
        """Test tool strategy variant generation."""
        strategy = ToolEvolutionStrategy()
        config = {"config": {}}
        variant = strategy.generate_variant(config)
        assert "tools" in variant

    def test_code_strategy_generate_variant(self):
        """Test code strategy variant generation."""
        strategy = CodeEvolutionStrategy()
        config = {}
        variant = strategy.generate_variant(config)
        assert "code" in variant


class TestEvolutionConfig:
    """Test evolution configuration validation."""

    def test_config_valid_defaults(self):
        """Test valid default configuration."""
        config = EvolutionConfig()
        assert config.generations >= 1
        assert config.population_size >= 1
        assert 0 <= config.mutation_rate <= 1
        assert 0 <= config.crossover_rate <= 1

    def test_config_invalid_generations(self):
        """Test invalid generations raises error."""
        with pytest.raises(ValueError, match="generations must be at least 1"):
            EvolutionConfig(generations=0)

    def test_config_invalid_population(self):
        """Test invalid population size raises error."""
        with pytest.raises(ValueError, match="population_size must be at least 1"):
            EvolutionConfig(population_size=0)

    def test_config_invalid_mutation_rate(self):
        """Test invalid mutation rate raises error."""
        with pytest.raises(ValueError, match="mutation_rate must be between"):
            EvolutionConfig(mutation_rate=1.5)

    def test_config_invalid_crossover_rate(self):
        """Test invalid crossover rate raises error."""
        with pytest.raises(ValueError, match="crossover_rate must be between"):
            EvolutionConfig(crossover_rate=-0.1)

    def test_config_invalid_elitism(self):
        """Test invalid elitism raises error."""
        with pytest.raises(ValueError, match="elitism.*must be less than population_size"):
            EvolutionConfig(population_size=5, elitism=5)

    def test_config_invalid_patience(self):
        """Test invalid patience raises error."""
        with pytest.raises(ValueError, match="patience must be at least 1"):
            EvolutionConfig(patience=0)

    def test_config_invalid_strategy(self):
        """Test invalid strategy raises error."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            EvolutionConfig(strategy="invalid_strategy")


# ============================================================================
# INTEGRATION TESTS: End-to-End Workflows
# ============================================================================

class TestEndToEndEvolution:
    """Test complete evolution workflows."""

    def test_minimal_evolution_mock(self):
        """Test minimal evolution with mock LLM (1 generation, small population)."""
        # Create agent
        agent = AgentCore(model="mock", task="Answer questions")

        # Create evaluator
        qa_pairs = [
            {"question": "What is 2+2?", "answer": "4"},
            {"question": "Capital?", "answer": "Paris"}
        ]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)

        # Create optimizer
        optimizer = EvolutionaryOptimizer(
            strategy="prompt_optimization",
            generations=1
        )

        # Run evolution
        result = optimizer.evolve(agent, evaluator, show_progress=False)

        # Verify result
        assert isinstance(result, EvolutionResult)
        assert result.best_score >= 0
        assert result.total_generations == 1
        assert len(result.generation_scores) == 1

    def test_multi_generation_evolution(self):
        """Test multi-generation evolution."""
        agent = AgentCore(model="mock")
        qa_pairs = [{"question": "Test?", "answer": "Answer"}]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)

        optimizer = EvolutionaryOptimizer(
            strategy="prompt_optimization",
            generations=3
        )

        result = optimizer.evolve(agent, evaluator, show_progress=False)

        assert result.total_generations <= 3  # May stop early
        assert len(result.generation_scores) == result.total_generations

    def test_early_stopping(self):
        """Test early stopping mechanism."""
        agent = AgentCore(model="mock")
        qa_pairs = [{"question": "Q", "answer": "A"}]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)

        config = EvolutionConfig(
            strategy="prompt_optimization",
            generations=10,
            early_stopping=True,
            patience=2
        )
        optimizer = EvolutionaryOptimizer(config=config)

        result = optimizer.evolve(agent, evaluator, show_progress=False)

        # Should stop before 10 generations due to no improvement
        assert result.total_generations < 10

    def test_all_strategies(self):
        """Test that all evolution strategies can run."""
        strategies = ["prompt_optimization", "memory_evolution", "tool_evolution", "code_evolution"]

        agent = AgentCore(model="mock")
        qa_pairs = [{"question": "Test", "answer": "Answer"}]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)

        for strategy in strategies:
            optimizer = EvolutionaryOptimizer(strategy=strategy, generations=1)
            result = optimizer.evolve(agent, evaluator, show_progress=False)
            assert isinstance(result, EvolutionResult)

    def test_evolution_result_export(self):
        """Test exporting evolution results."""
        agent = AgentCore(model="mock")
        qa_pairs = [{"question": "Q", "answer": "A"}]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)
        optimizer = EvolutionaryOptimizer(generations=1)

        result = optimizer.evolve(agent, evaluator, show_progress=False)

        # Test report export
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            report_path = f.name
        try:
            result.export_report(report_path)
            assert Path(report_path).exists()
            content = Path(report_path).read_text()
            assert "Evolution Report" in content
            assert "Best Score" in content
        finally:
            Path(report_path).unlink(missing_ok=True)


# ============================================================================
# NEGATIVE TESTS: Error Handling & Robustness
# ============================================================================

class TestRobustness:
    """Test error handling and edge cases."""

    def test_agent_with_empty_task(self):
        """Test agent handles empty task."""
        agent = AgentCore(model="mock")
        # Should not crash
        result = agent.run("", max_iterations=1)
        assert isinstance(result, dict)

    def test_evaluator_with_empty_tasks(self):
        """Test evaluator handles empty task list."""
        agent = AgentCore(model="mock")
        evaluator = QAEvaluator()
        score = evaluator.evaluate(agent, [])
        assert score == 0.0

    def test_evaluator_with_malformed_qa(self):
        """Test evaluator handles malformed QA pairs gracefully."""
        qa_pairs = [{"question": "Q", "answer": "A"}]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)
        # Missing reference
        ref = evaluator._find_reference_answer("Unknown question")
        assert ref is None

    def test_evolution_with_zero_population(self):
        """Test that zero population raises error."""
        with pytest.raises(ValueError):
            EvolutionConfig(population_size=0)

    def test_context_overflow_handling(self):
        """Test context handles extremely long content."""
        ctx = ContextManager(max_length=100)
        # Add message longer than limit
        ctx.add_user_message("x" * 1000)
        # Should trim automatically
        assert len(ctx) >= 0  # Should not crash

    def test_agent_run_max_iterations(self):
        """Test agent respects max_iterations."""
        agent = AgentCore(model="mock")
        result = agent.run("Complex task", max_iterations=1)
        # Should stop after 1 iteration
        assert result["iterations"] == 1

    def test_invalid_model_provider(self):
        """Test handling of invalid model provider."""
        # Test detection defaults to openai for unknown models
        agent = AgentCore(model="mock", _skip_init=True)
        # Unknown model should default to openai
        detected = agent._detect_provider("unknown-model-xyz")
        assert detected == "openai"  # Defaults to openai when unknown


# ============================================================================
# PERFORMANCE TESTS: Speed & Resource Usage
# ============================================================================

class TestPerformance:
    """Test performance characteristics (should be fast)."""

    def test_agent_creation_speed(self):
        """Test agent creation is fast (< 1 second)."""
        import time
        start = time.time()
        for _ in range(10):
            agent = AgentCore(model="mock")
        elapsed = time.time() - start
        assert elapsed < 1.0  # 10 agents in < 1 second

    def test_evaluation_speed(self):
        """Test evaluation is fast (< 5 seconds for 10 samples)."""
        import time
        agent = AgentCore(model="mock")
        qa_pairs = [{"question": f"Q{i}", "answer": f"A{i}"} for i in range(10)]
        evaluator = QAEvaluator(qa_pairs=qa_pairs)

        start = time.time()
        tasks = [qa["question"] for qa in qa_pairs]
        score = evaluator.evaluate(agent, tasks)
        elapsed = time.time() - start

        assert elapsed < 5.0  # Should be fast with mock


# ============================================================================
# FIXTURE UTILITIES
# ============================================================================

@pytest.fixture
def mock_agent():
    """Fixture for creating a mock agent."""
    return AgentCore(model="mock", task="Test task")


@pytest.fixture
def simple_evaluator():
    """Fixture for creating a simple evaluator."""
    qa_pairs = [
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "What is the capital of France?", "answer": "Paris"}
    ]
    return QAEvaluator(qa_pairs=qa_pairs)


@pytest.fixture
def simple_optimizer():
    """Fixture for creating a simple optimizer."""
    return EvolutionaryOptimizer(
        strategy="prompt_optimization",
        generations=2
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def test_quick_smoke_test(mock_agent, simple_evaluator, simple_optimizer):
    """Quick smoke test using fixtures."""
    result = simple_optimizer.evolve(mock_agent, simple_evaluator, show_progress=False)
    assert result.best_score >= 0
    assert result.total_generations <= 2


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
