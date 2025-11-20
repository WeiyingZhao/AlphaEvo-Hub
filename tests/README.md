# Test Suite

Comprehensive test suite for Agent Evolve platform.

## Quick Start

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_comprehensive_v2.py -v

# Run with coverage
pytest tests/ --cov=agent_evolve --cov-report=html
```

## Test Files

### `test_comprehensive_v2.py` (NEW - Recommended)
**Complete test suite** with:
- ✅ Unit tests (LLM, Context, Agent, Evaluators, Strategies)
- ✅ Integration tests (End-to-end evolution)
- ✅ Negative tests (Error handling, edge cases)
- ✅ Performance tests (Speed checks)
- ✅ All tests use mock LLM (no API keys)
- ✅ Fast execution (< 30 seconds total)
- ✅ CPU-only (no GPU required)

**Run:** `pytest tests/test_comprehensive_v2.py -v`

### `test_comprehensive.py` (Legacy)
Original test suite with basic import and agent creation tests.

### `test_llm_basic.py` (Legacy)
Basic LLM provider tests.

### `test_provider_detection.py` (Legacy)
Tests for automatic provider detection from model names.

## Test Categories

### Unit Tests (`TestLLMProviders`, `TestContextManager`, `TestAgentCore`, etc.)
Test individual components in isolation:
- LLM provider integration (mock, OpenAI, Anthropic, HuggingFace)
- Context management (messages, trimming, export/load)
- Agent core (creation, configuration, response generation)
- Evaluators (QA, metrics, similarity)
- Evolution strategies (prompt, memory, tool, code)
- Configuration validation

**Run:** `pytest tests/test_comprehensive_v2.py::TestAgentCore -v`

### Integration Tests (`TestEndToEndEvolution`)
Test complete workflows:
- Minimal evolution (1 generation)
- Multi-generation evolution
- Early stopping mechanism
- All evolution strategies
- Result export (reports, configs)

**Run:** `pytest tests/test_comprehensive_v2.py::TestEndToEndEvolution -v`

### Robustness Tests (`TestRobustness`)
Test error handling and edge cases:
- Empty inputs
- Malformed data
- Invalid configurations
- Resource limits
- Timeout handling

**Run:** `pytest tests/test_comprehensive_v2.py::TestRobustness -v`

### Performance Tests (`TestPerformance`)
Verify fast execution:
- Agent creation speed (< 1s for 10 agents)
- Evaluation speed (< 5s for 10 samples)

**Run:** `pytest tests/test_comprehensive_v2.py::TestPerformance -v`

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Class

```bash
pytest tests/test_comprehensive_v2.py::TestAgentCore -v
```

### Run Specific Test Method

```bash
pytest tests/test_comprehensive_v2.py::TestAgentCore::test_agent_creation_default -v
```

### Run with Pattern Matching

```bash
# Run all tests with "agent" in the name
pytest tests/ -k agent -v

# Run all tests with "evolution" in the name
pytest tests/ -k evolution -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=agent_evolve --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run with Different Verbosity

```bash
# Minimal output
pytest tests/ -q

# Standard output
pytest tests/ -v

# Very verbose with print statements
pytest tests/ -vv -s
```

## Test Fixtures

The test suite includes useful fixtures:

```python
@pytest.fixture
def mock_agent():
    """Pre-configured mock agent."""
    return AgentCore(model="mock", task="Test task")

@pytest.fixture
def simple_evaluator():
    """Simple QA evaluator with 2 questions."""
    qa_pairs = [
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "What is the capital of France?", "answer": "Paris"}
    ]
    return QAEvaluator(qa_pairs=qa_pairs)

@pytest.fixture
def simple_optimizer():
    """Simple optimizer with 2 generations."""
    return EvolutionaryOptimizer(
        strategy="prompt_optimization",
        generations=2
    )
```

Use in tests:

```python
def test_my_feature(mock_agent, simple_evaluator):
    result = simple_evaluator.evaluate(mock_agent, ["Test question"])
    assert result >= 0
```

## Expected Output

### Successful Run

```
============================= test session starts ==============================
platform linux -- Python 3.10.0, pytest-7.4.0, pluggy-1.0.0 -- /usr/bin/python3
collected 45 items

tests/test_comprehensive_v2.py::TestLLMProviders::test_mock_llm_basic PASSED [  2%]
tests/test_comprehensive_v2.py::TestLLMProviders::test_mock_llm_streaming PASSED [  4%]
tests/test_comprehensive_v2.py::TestLLMProviders::test_get_llm_factory_mock PASSED [  6%]
...
tests/test_comprehensive_v2.py::TestEndToEndEvolution::test_minimal_evolution_mock PASSED [ 84%]
tests/test_comprehensive_v2.py::TestEndToEndEvolution::test_multi_generation_evolution PASSED [ 88%]
...
tests/test_comprehensive_v2.py::TestRobustness::test_agent_with_empty_task PASSED [ 95%]
tests/test_comprehensive_v2.py::TestRobustness::test_evaluator_with_empty_tasks PASSED [ 97%]
...

============================== 45 passed in 12.34s ==============================
```

### Failed Test Example

```
FAILED tests/test_comprehensive_v2.py::TestAgentCore::test_agent_creation_default

def test_agent_creation_default():
    agent = AgentCore(model="mock")
>   assert agent.config.model_name == "mock"
E   AssertionError: assert 'invalid' == 'mock'

tests/test_comprehensive_v2.py:123: AssertionError
```

## Writing New Tests

### Unit Test Template

```python
class TestMyFeature:
    """Test my new feature."""

    def test_basic_functionality(self):
        """Test basic functionality works."""
        # Arrange
        component = MyComponent()

        # Act
        result = component.do_something()

        # Assert
        assert result is not None
        assert isinstance(result, expected_type)

    def test_error_handling(self):
        """Test error handling."""
        component = MyComponent()
        with pytest.raises(ValueError, match="expected error message"):
            component.do_invalid_thing()
```

### Integration Test Template

```python
def test_end_to_end_workflow():
    """Test complete workflow."""
    # Setup
    agent = AgentCore(model="mock")
    evaluator = QAEvaluator(qa_pairs=[...])
    optimizer = EvolutionaryOptimizer(generations=2)

    # Execute
    result = optimizer.evolve(agent, evaluator, show_progress=False)

    # Verify
    assert result.best_score >= 0
    assert len(result.generation_scores) > 0
```

## Continuous Integration

For CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest tests/ -v --cov=agent_evolve
```

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'agent_evolve'
```

**Solution**: Install the package in development mode:
```bash
pip install -e .
```

### Slow Tests

If tests are slow (> 30 seconds), check:
1. Are you using mock LLM? (Real LLMs are slow)
2. Are you running too many generations?
3. Is there network I/O happening?

**Solution**: Use `--durations=10` to find slow tests:
```bash
pytest tests/ --durations=10
```

### Flaky Tests

If tests fail intermittently:
1. Check for proper random seed setting
2. Ensure no network dependencies
3. Verify no race conditions

**Solution**: Run multiple times to reproduce:
```bash
for i in {1..10}; do pytest tests/test_comprehensive_v2.py; done
```

## Test Coverage

Current coverage targets:
- **Core modules**: > 80%
- **Critical paths (evolution, evaluation)**: > 90%
- **Overall**: > 75%

Check coverage:
```bash
pytest tests/ --cov=agent_evolve --cov-report=term-missing
```

## Best Practices

1. ✅ **Fast tests**: All tests should run in < 30 seconds total
2. ✅ **Isolated**: Tests should not depend on external services
3. ✅ **Deterministic**: Use fixed random seeds, no flaky tests
4. ✅ **Mock LLM**: Use mock provider for unit/integration tests
5. ✅ **Clear names**: Test names should describe what they test
6. ✅ **One assertion per test**: Focus on single behavior
7. ✅ **Arrange-Act-Assert**: Follow AAA pattern
8. ✅ **Test both happy path and errors**: Cover success and failure cases

## Next Steps

1. Run the test suite: `pytest tests/test_comprehensive_v2.py -v`
2. Check coverage: `pytest tests/ --cov=agent_evolve`
3. Add tests for new features
4. Run tests before committing code
5. Integrate with CI/CD pipeline
