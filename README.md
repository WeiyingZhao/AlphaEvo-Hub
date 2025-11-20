# Agent Evolve - Self-Evolving AI Agent Platform

Agent Evolve is a general-purpose AI agent platform that continuously self-improves over time, bridging the gap between powerful but static AI models and dynamic, adaptive agents.

## Overview

Agent Evolve enables AI agents to adaptively reason, act, and evolve in real time. The platform democratizes advanced self-evolving AI techniques, making them accessible for non-experts to harness AI that improves itself across diverse domains including coding, mathematics, education, and personal productivity.

## Key Features

- **Multiple Self-Evolution Strategies**: Prompt optimization, memory enhancement, tool use adaptation, workflow refinement, and multi-agent co-evolution
- **Self-Questioning Task Generation**: Automatic task generation for continuous improvement
- **Feedback-Driven Learning Loops**: Experience-guided feedback loops for policy improvement
- **Fine-Grained Trajectory Analysis**: Attribution-based credit assignment for debugging reasoning
- **Evolutionary Code Solver**: AlphaEvolve-inspired algorithmic problem solving
- **Multi-Agent Co-Evolution**: Proposer-Solver-Judge triad for collective improvement
- **Domain Specialization**: Tool evolution via Model Context Protocols (MCP)
- **Intuitive UI**: Interactive visualizations and real-time progress tracking

## Architecture

The platform consists of several core modules:

- **Agent Core**: LLM-powered reasoning and behavior engine
- **Memory Module**: Dynamic memory management with evolution support
- **Tool Interface**: Standardized tool usage and creation framework
- **Evolutionary Optimizer**: Multiple evolution algorithms (genetic, RL, etc.)
- **Evaluator**: Flexible scoring and probing mechanisms
- **Orchestration**: Distributed execution and dataflow management

## Technology Stack

- **Backend**: Python, PyTorch, Hugging Face Transformers, DEAP, RLlib
- **Frontend**: React, TypeScript, D3.js for visualizations
- **API**: FastAPI with WebSocket support
- **Storage**: Vector databases (FAISS/Chroma), SQLite
- **Sandboxing**: Docker containers for safe code execution

## Installation

### Quick Install (Minimal Setup)

For basic usage with OpenAI or Anthropic APIs only (no local models):

```bash
# Clone the repository
git clone https://github.com/WeiyingZhao/AlphaEvo-Hub.git
cd AlphaEvo-Hub

# Install minimal dependencies (without torch/transformers)
pip install openai anthropic fastapi uvicorn langchain deap numpy scipy \
    faiss-cpu chromadb sentence-transformers websockets pydantic \
    sqlalchemy python-dotenv aiofiles python-multipart tinydb
```

### Full Install (All Features)

For complete functionality including local models and all evolution strategies:

```bash
# Clone the repository
git clone https://github.com/WeiyingZhao/AlphaEvo-Hub.git
cd AlphaEvo-Hub

# Install all dependencies
pip install -r requirements.txt

# (Optional) Install frontend dependencies
cd frontend
npm install
cd ..
```

### Install from Source

```bash
# Install in development mode
pip install -e .

# Or install specific dependency groups
pip install -e ".[dev]"  # Includes testing and dev tools
```

### Environment Setup

Create a `.env` file for your API keys (optional for demo mode):

```bash
# For OpenAI
OPENAI_API_KEY=your-openai-key-here

# For Anthropic
ANTHROPIC_API_KEY=your-anthropic-key-here
```

## Quick Start

### Demo Mode (No API Keys Required!)

Try Agent Evolve immediately without any API keys:

```bash
python examples/basic_usage.py
```

This runs in **mock mode** for demonstration and testing purposes.

### With Real LLMs

```python
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator

# Set your API key
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"

# Create an agent
agent = AgentCore(
    model="gpt-3.5-turbo",  # or "claude-3-sonnet-20240229"
    task="Answer questions accurately"
)

# Set up evolution
optimizer = EvolutionaryOptimizer(
    strategy="prompt_optimization",
    generations=5
)

# Define evaluation criteria
evaluator = QAEvaluator(qa_pairs=[
    {"question": "What is 2+2?", "answer": "4"},
    {"question": "Capital of France?", "answer": "Paris"}
])

# Run evolution
result = optimizer.evolve(agent, evaluator)

# View results
print(f"Best Score: {result.best_score:.4f}")
result.export_report("evolution_report.md")
```

### Using the Web Interface (Optional)

```bash
# Start the backend server
python -m agent_evolve.server

# In another terminal, start the frontend
cd frontend
npm start
```

Visit `http://localhost:3000` to access the Agent Evolve dashboard.

## Usage Examples

### 1. Getting Started - No API Keys

```python
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator

# Use mock LLM for testing (no API key needed)
agent = AgentCore(model="mock", task="Answer questions")

evaluator = QAEvaluator(qa_pairs=[
    {"question": "What is 2+2?", "answer": "4"}
])

optimizer = EvolutionaryOptimizer(strategy="prompt_optimization", generations=3)
result = optimizer.evolve(agent, evaluator)
print(f"Evolution complete! Best score: {result.best_score:.4f}")
```

### 2. Code Evolution with OpenAI

```python
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import CodeEvaluator

# Create a code-generating agent
agent = AgentCore(
    model="gpt-3.5-turbo",
    task="Write efficient Python code"
)

# Define test cases
evaluator = CodeEvaluator(test_cases=[
    ([1, 2, 3], 6),  # sum([1,2,3]) = 6
    ([10, 20], 30),   # sum([10,20]) = 30
])

# Evolve the solution
optimizer = EvolutionaryOptimizer(
    strategy="code_evolution",
    generations=10
)

result = optimizer.evolve(agent, evaluator)

# Export the best solution
result.export_code("best_solution.py")
result.export_report("evolution_report.md")
```

### 3. Multi-Strategy Evolution

```python
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator

agent = AgentCore(model="claude-3-sonnet-20240229")
evaluator = QAEvaluator(qa_pairs=[...])

# Try different evolution strategies
strategies = ["prompt_optimization", "memory_evolution", "tool_evolution"]

best_results = {}
for strategy in strategies:
    optimizer = EvolutionaryOptimizer(strategy=strategy, generations=5)
    result = optimizer.evolve(agent, evaluator)
    best_results[strategy] = result.best_score
    print(f"{strategy}: {result.best_score:.4f}")
```

## Supported Models

- **OpenAI**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **Anthropic**: claude-3-sonnet-20240229, claude-3-opus-20240229, claude-3-haiku-20240307
- **HuggingFace**: llama, mistral, falcon, and other open-source models
- **Mock**: For testing without API costs

## Roadmap

- **Phase 1 (Q1 2026)**: MVP - Single-Agent Evolution
- **Phase 2 (Q2-Q3 2026)**: Expanded Evolution Techniques & Domain Specialization
- **Phase 3 (Q4 2026)**: Multi-Agent Co-Evolution & Collaboration
- **Phase 4 (2027)**: Refinement, Safety, and Scale
- **Phase 5 (Beyond 2027)**: Personal AI Ecosystems and Continuous Learning

## Research References

This project is inspired by cutting-edge research including:

- DeepMind's [AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)
- Alibaba's [AgentEvolver](https://github.com/modelscope/AgentEvolver)
- UIUC's [Multi-Agent Evolve](https://github.com/ulab-uiuc/Multi-agent-Evolve)
- Princeton's [ALITA-G](https://arxiv.org/abs/2510.23601)
- [A Comprehensive Survey of Self-Evolving AI Agents](https://arxiv.org/abs/2508.07407)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use Agent Evolve in your research, please cite:

```bibtex
@software{agent_evolve_2025,
  title={Agent Evolve: A General-Purpose Self-Evolving AI Agent Platform},
  author={AlphaEvo Team},
  year={2025},
  url={https://github.com/WeiyingZhao/AlphaEvo-Hub}
}
```

## Contact

For questions and feedback, please open an issue on GitHub.
