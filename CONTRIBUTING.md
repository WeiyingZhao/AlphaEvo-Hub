# Contributing to Agent Evolve

We welcome contributions to Agent Evolve! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/AlphaEvo-Hub.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Style

We follow PEP 8 style guidelines. Use these tools:

```bash
# Format code
black agent_evolve/

# Check style
flake8 agent_evolve/

# Type checking
mypy agent_evolve/
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_evolve

# Run specific test file
pytest tests/test_agent.py
```

## Adding New Features

### Evolution Strategies

To add a new evolution strategy:

1. Create a new class in `agent_evolve/optimizer/strategies.py`
2. Inherit from `EvolutionStrategy`
3. Implement required methods
4. Add tests in `tests/test_strategies.py`
5. Update documentation

Example:

```python
class MyCustomStrategy(EvolutionStrategy):
    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass

    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

### Evaluators

To add a new evaluator:

1. Create a new file in `agent_evolve/evaluator/`
2. Inherit from `BaseEvaluator`
3. Implement `evaluate_single` method
4. Add tests
5. Update documentation

### Tools

To add a new tool:

1. Create a new class in `agent_evolve/tools/`
2. Inherit from `Tool`
3. Implement `execute` method
4. Register in `ToolManager`
5. Add tests

## Documentation

- Update README.md if needed
- Add docstrings to all public functions
- Update docs/ if adding major features
- Include examples in examples/ directory

## Pull Request Guidelines

- **Title**: Use descriptive titles (e.g., "Add genetic programming strategy")
- **Description**: Explain what and why
- **Tests**: Include tests for new features
- **Documentation**: Update relevant documentation
- **Code Quality**: Ensure all checks pass

## Issue Guidelines

When creating issues:

- **Bug Reports**: Include steps to reproduce, expected vs actual behavior
- **Feature Requests**: Explain the use case and proposed solution
- **Questions**: Check existing docs and issues first

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

## Architecture Decisions

For significant architectural changes:

1. Open an issue for discussion first
2. Explain the motivation and alternatives considered
3. Get feedback from maintainers
4. Implement after consensus

## Research Integration

Agent Evolve is research-driven. When proposing new features based on papers:

1. Cite the paper in your PR
2. Explain the core concept
3. Show how it fits into the platform
4. Provide references in code comments

## Questions?

- Open an issue for questions
- Check existing documentation
- Look at examples in examples/ directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Agent Evolve! 🚀
