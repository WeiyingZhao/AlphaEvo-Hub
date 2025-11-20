# Agent Evolve - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/WeiyingZhao/AlphaEvo-Hub.git
cd AlphaEvo-Hub

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

## Basic Usage

### 1. Create an Agent

```python
from agent_evolve import AgentCore

# Create an agent with a specific task
agent = AgentCore(
    model="gpt-3.5-turbo",
    task="Solve coding problems"
)
```

### 2. Set Up Evolution

```python
from agent_evolve import EvolutionaryOptimizer
from agent_evolve.evaluator import CodeEvaluator

# Create an evaluator with test cases
evaluator = CodeEvaluator(test_cases=[
    ([1, 2, 3], 6),
    ([10, 20], 30),
])

# Create optimizer
optimizer = EvolutionaryOptimizer(
    strategy="prompt_optimization",
    generations=10
)
```

### 3. Run Evolution

```python
# Evolve the agent
result = optimizer.evolve(
    agent=agent,
    evaluator=evaluator
)

print(f"Best Score: {result.best_score}")
result.export_report("report.md")
```

## Using the API

### Start the Backend Server

```bash
python -m agent_evolve.api.server
```

### Start the Frontend

```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` to access the dashboard.

## API Examples

### Create an Agent

```bash
curl -X POST http://localhost:8000/agent/create \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "gpt-3.5-turbo",
    "task": "Answer questions"
  }'
```

### Start Evolution

```bash
curl -X POST http://localhost:8000/evolution/start \
  -H "Content-Type: application/json" \
  -d '{
    "agent_config": {
      "model_name": "gpt-3.5-turbo",
      "task": "Solve problems"
    },
    "strategy": "prompt_optimization",
    "generations": 10
  }'
```

## Evolution Strategies

### Available Strategies

1. **prompt_optimization**: Evolves the agent's system prompt
2. **memory_evolution**: Optimizes memory management
3. **tool_evolution**: Creates and refines tools
4. **code_evolution**: Evolves code solutions

### Example with Different Strategies

```python
strategies = [
    "prompt_optimization",
    "memory_evolution",
    "tool_evolution"
]

for strategy in strategies:
    optimizer = EvolutionaryOptimizer(
        strategy=strategy,
        generations=5
    )
    result = optimizer.evolve(agent, evaluator)
    print(f"{strategy}: {result.best_score:.4f}")
```

## Evaluators

### Code Evaluator

For code generation tasks:

```python
from agent_evolve.evaluator import CodeEvaluator

evaluator = CodeEvaluator(
    test_cases=[
        (input1, expected1),
        (input2, expected2),
    ]
)
```

### QA Evaluator

For question-answering tasks:

```python
from agent_evolve.evaluator import QAEvaluator

evaluator = QAEvaluator(
    qa_pairs=[
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "Capital of France?", "answer": "Paris"},
    ]
)
```

### Custom Evaluator

Create your own evaluator:

```python
from agent_evolve.evaluator.base import BaseEvaluator, EvaluationResult

class MyEvaluator(BaseEvaluator):
    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        result = agent.run(task)
        score = self.compute_score(result)

        return EvaluationResult(
            score=score,
            details={},
            success=score > 0.7
        )
```

## Configuration

### Evolution Configuration

```python
from agent_evolve.optimizer.evolutionary import EvolutionConfig

config = EvolutionConfig(
    strategy="prompt_optimization",
    generations=20,
    population_size=10,
    mutation_rate=0.3,
    crossover_rate=0.7,
    elitism=2,
    early_stopping=True,
    patience=5
)

optimizer = EvolutionaryOptimizer(config=config)
```

### Agent Configuration

```python
from agent_evolve.core.agent import AgentConfig

config = AgentConfig(
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=2048,
    system_prompt="You are an expert problem solver.",
    use_tools=True,
    enable_memory=True
)

agent = AgentCore(config=config)
```

## Next Steps

- Check out [examples/](../examples/) for more detailed examples
- Read the [API Documentation](API.md) for complete API reference
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture details
- Join our community and contribute!

## Troubleshooting

### API Key Issues

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

### Model Access

If using mock models for testing:

```python
agent = AgentCore(model="mock")
```

### Common Errors

1. **Import Error**: Make sure to install all dependencies
2. **API Connection**: Ensure the backend server is running
3. **Frontend**: Check that port 3000 is not in use

## Support

For questions or issues:
- GitHub Issues: https://github.com/WeiyingZhao/AlphaEvo-Hub/issues
- Documentation: See `docs/` folder

Happy evolving! 🚀
