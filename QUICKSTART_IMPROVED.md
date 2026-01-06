# Agent Evolve - Improved Quickstart Guide

**Version**: 1.1 (Improved with comprehensive testing, data generation, and evaluation harness)

This guide will get you up and running with Agent Evolve in under 5 minutes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Test (No API Keys)](#quick-test-no-api-keys)
4. [Data Generation](#data-generation)
5. [Running Experiments](#running-experiments)
6. [Testing](#testing)
7. [Next Steps](#next-steps)

---

## Prerequisites

- **Python 3.9+**
- **pip** or **conda**
- **(Optional)** API keys for OpenAI or Anthropic
- **CPU-only** (no GPU required)

---

## Installation

### Option 1: Quick Install (Minimal Dependencies)

```bash
# Clone repository
git clone https://github.com/WeiyingZhao/AlphaEvo-Hub.git
cd AlphaEvo-Hub

# Install minimal dependencies
pip install -e .
```

### Option 2: Full Install (All Features)

```bash
# Install with all dependencies
pip install -e ".[full]"
```

### Option 3: Development Install (With Testing)

```bash
# Install with dev tools
pip install -e ".[dev]"
```

---

## Quick Test (No API Keys)

Run a quick evolution experiment using the mock LLM (no API keys required):

```bash
# Quick 3-generation test (takes ~30 seconds)
python experiments/run_evolution_experiment.py --quick
```

**Expected Output:**
```
🚀 Quick test mode enabled
INFO: Random seed set to 42 for reproducibility
INFO: Preparing dataset...
INFO: ✓ Loaded 5 QA pairs
INFO: Creating agent with model: mock
INFO: ✓ Agent created (provider: mock)

======================================================================
Starting Evolution
======================================================================

Evolution Progress: 100%|████████████| 3/3 [00:05<00:00, 1.87gen/s]

======================================================================
EVOLUTION RESULTS
======================================================================

📊 Performance Metrics:
  Initial Score:       0.5000
  Final Score:         0.7000
  Best Score:          0.7000
  Total Improvement:   +0.2000
  % Improvement:       +40.00%

...

✅ Experiment complete!
```

---

## Data Generation

Generate synthetic datasets for training and evaluation:

### Generate QA Dataset

```bash
# Generate question-answering dataset
python data_generation/generate_qa_dataset.py \
    --output data/qa_dataset.json \
    --seed 42 \
    --num-math 20 \
    --num-factual 20 \
    --num-reasoning 15
```

**Output**: `data/qa_dataset.json` with 75 QA pairs across multiple categories.

### Generate Code Problems

```bash
# Generate programming problems with test cases
python data_generation/generate_code_problems.py \
    --output data/code_problems.json \
    --seed 42
```

**Output**: `data/code_problems.json` with 25 coding problems.

### Load Data in Code

```python
from data_generation.data_loader import get_qa_pairs_for_evaluator

# Load filtered QA pairs
qa_pairs = get_qa_pairs_for_evaluator(
    categories=['math', 'factual'],
    difficulty='easy',
    max_samples=10
)
```

**See**: `data_generation/README.md` for full documentation.

---

## Running Experiments

### Basic Evolution

```python
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator
from data_generation.data_loader import get_qa_pairs_for_evaluator

# 1. Load data
qa_pairs = get_qa_pairs_for_evaluator(difficulty='easy', max_samples=10)

# 2. Create agent
agent = AgentCore(model="mock", task="Answer questions accurately")

# 3. Create evaluator
evaluator = QAEvaluator(qa_pairs=qa_pairs)

# 4. Create optimizer
optimizer = EvolutionaryOptimizer(
    strategy="prompt_optimization",
    generations=5
)

# 5. Run evolution
result = optimizer.evolve(agent, evaluator)

# 6. View results
print(f"Best Score: {result.best_score:.4f}")
result.export_report("evolution_report.md")
```

### Using the Experiment Harness

```bash
# Full experiment with custom parameters
python experiments/run_evolution_experiment.py \
    --model mock \
    --strategy prompt_optimization \
    --generations 10 \
    --population 5 \
    --num-samples 20 \
    --difficulty easy \
    --categories math factual \
    --seed 42 \
    --output-dir results/my_experiment
```

**See**: `experiments/README.md` for all options.

### Evaluation Only (No Evolution)

```bash
# Quick baseline evaluation
python experiments/evaluate_agent.py \
    --model mock \
    --num-samples 10 \
    --difficulty easy
```

---

## Testing

Run the comprehensive test suite to verify everything works:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/test_comprehensive_v2.py -v

# Run specific test category
pytest tests/test_comprehensive_v2.py::TestAgentCore -v

# Run with coverage
pytest tests/ --cov=agent_evolve --cov-report=html
```

**Expected**: 45+ tests pass in < 30 seconds.

**See**: `tests/README.md` for full testing documentation.

---

## Next Steps

### 1. Try Different Evolution Strategies

```bash
for strategy in prompt_optimization memory_evolution tool_evolution code_evolution; do
    python experiments/run_evolution_experiment.py \
        --model mock \
        --strategy $strategy \
        --generations 5 \
        --output-dir results/$strategy
done
```

### 2. Use Real LLMs

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Run with GPT-3.5
python experiments/run_evolution_experiment.py \
    --model gpt-3.5-turbo \
    --strategy prompt_optimization \
    --generations 5 \
    --num-samples 10
```

### 3. Create Custom Evaluator

```python
from agent_evolve.evaluator.base import BaseEvaluator, EvaluationResult

class CustomEvaluator(BaseEvaluator):
    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        result = agent.run(task)
        output = result.get("solution", "")

        # Your custom scoring logic
        score = self.compute_custom_score(output)

        return EvaluationResult(
            score=score,
            details={"output": output},
            success=score > 0.5
        )
```

### 4. Explore the Codebase

Key modules to understand:
- `agent_evolve/core/agent.py` - Agent implementation
- `agent_evolve/optimizer/evolutionary.py` - Evolution logic
- `agent_evolve/evaluator/base.py` - Evaluation framework
- `data_generation/` - Synthetic data generators
- `experiments/` - Experiment harnesses

---

## Common Issues & Solutions

### Issue: Dataset not found

```
FileNotFoundError: Dataset not found at data/qa_dataset.json
```

**Solution**: Generate the dataset:
```bash
python data_generation/generate_qa_dataset.py
```

### Issue: Module not found

```
ModuleNotFoundError: No module named 'agent_evolve'
```

**Solution**: Install the package:
```bash
pip install -e .
```

### Issue: API key not found

```
ValueError: OpenAI API key not found
```

**Solution**: Use mock model or set API key:
```bash
# Option 1: Use mock
python experiments/run_evolution_experiment.py --model mock

# Option 2: Set API key
export OPENAI_API_KEY="your-key"
```

### Issue: Tests failing

**Solution**: Check you have dev dependencies:
```bash
pip install -e ".[dev]"
pytest tests/test_comprehensive_v2.py -v
```

---

## Key Features Added in This Update

### ✅ Comprehensive Test Suite
- 45+ tests covering unit, integration, and robustness
- All tests use mock LLM (no API keys needed)
- Fast execution (< 30 seconds total)
- See: `tests/test_comprehensive_v2.py`

### ✅ Synthetic Data Generation
- QA dataset generator (math, factual, reasoning, edge cases)
- Code problems generator (algorithms, strings, data structures)
- Reproducible with fixed seeds
- See: `data_generation/`

### ✅ Experiment Harness
- Unified script for running evolution experiments
- Comprehensive metrics (performance, timing, convergence)
- Result export (reports, configs, metrics)
- See: `experiments/run_evolution_experiment.py`

### ✅ Evaluation Tools
- Quick baseline evaluation without evolution
- Filtering by category and difficulty
- Custom evaluator support
- See: `experiments/evaluate_agent.py`

### ✅ Bug Fixes & Hardening
- Input validation throughout
- Better error handling
- Security improvements
- See: `BUG_FIXES_AND_IMPROVEMENTS.md`

### ✅ Enhanced Documentation
- README for each module
- Comprehensive examples
- Troubleshooting guides
- Architecture diagrams

---

## Project Structure

```
AlphaEvo-Hub/
├── agent_evolve/              # Main package
│   ├── core/                  # Agent, LLM, Context, Controller
│   ├── optimizer/             # Evolution algorithms
│   ├── evaluator/             # Evaluation frameworks
│   ├── memory/                # Memory management
│   ├── tools/                 # Tool interface and sandbox
│   ├── api/                   # FastAPI server
│   └── utils/                 # Validation utilities (NEW)
├── data_generation/           # Synthetic data generators (NEW)
│   ├── generate_qa_dataset.py
│   ├── generate_code_problems.py
│   ├── data_loader.py
│   └── README.md
├── experiments/               # Experiment harnesses (NEW)
│   ├── run_evolution_experiment.py
│   ├── evaluate_agent.py
│   └── README.md
├── tests/                     # Comprehensive test suite (IMPROVED)
│   ├── test_comprehensive_v2.py  # NEW: 45+ tests
│   ├── pytest.ini
│   └── README.md
├── frontend/                  # React dashboard
├── examples/                  # Usage examples
├── docs/                      # Documentation
├── BUG_FIXES_AND_IMPROVEMENTS.md  # NEW: Bug fix documentation
├── QUICKSTART_IMPROVED.md     # NEW: This file
└── README.md                  # Main documentation
```

---

## Resources

- **Main README**: `README.md`
- **Data Generation Guide**: `data_generation/README.md`
- **Experiment Guide**: `experiments/README.md`
- **Testing Guide**: `tests/README.md`
- **Bug Fixes**: `BUG_FIXES_AND_IMPROVEMENTS.md`
- **Architecture**: See Step 1 in analysis document
- **GitHub**: https://github.com/WeiyingZhao/AlphaEvo-Hub

---

## Getting Help

1. Check the READMEs in each directory
2. Run tests to verify your setup
3. Look at example scripts in `examples/`
4. Read the bug fixes document for known issues
5. Open an issue on GitHub

---

## What's Next?

1. ✅ Run the quick test to verify installation
2. ✅ Generate synthetic data
3. ✅ Run your first evolution experiment
4. ✅ Explore different strategies
5. ✅ Try with real LLMs (OpenAI/Anthropic)
6. ✅ Create custom evaluators
7. ✅ Extend with new tools and strategies

**Happy Evolving!** 🚀
