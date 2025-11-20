# Data Generation for Agent Evolve

This directory contains synthetic data generators for testing and evaluating AI agents.

## Overview

The data generation scripts create **reproducible, synthetic datasets** for:
- **QA Evaluation**: Question-answering pairs across multiple domains
- **Code Evolution**: Programming problems with test cases
- **Robustness Testing**: Edge cases and adversarial examples

All generators use **fixed random seeds** for reproducibility and run on **CPU-only** (no GPU required).

## Quick Start

### Generate All Datasets

```bash
# From repository root
python data_generation/generate_qa_dataset.py --output data/qa_dataset.json --seed 42
python data_generation/generate_code_problems.py --output data/code_problems.json --seed 42
```

### Use with Agent Evolve

```python
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator
from data_generation.data_loader import get_qa_pairs_for_evaluator

# Load synthetic QA data
qa_pairs = get_qa_pairs_for_evaluator(
    categories=['math', 'factual'],
    difficulty='easy',
    max_samples=10
)

# Create evaluator
evaluator = QAEvaluator(qa_pairs=qa_pairs)

# Run evolution
agent = AgentCore(model="mock", task="Answer questions")
optimizer = EvolutionaryOptimizer(strategy="prompt_optimization", generations=5)
result = optimizer.evolve(agent, evaluator)
```

## Files

### `generate_qa_dataset.py`
Generates question-answering datasets with:
- **Math**: Arithmetic, word problems, sequences, percentages
- **Factual**: Geography, history, science, general knowledge
- **Reasoning**: Logic puzzles, pattern recognition, deduction
- **Edge Cases**: Empty inputs, ambiguous questions, paradoxes
- **Adversarial**: Prompt injection, misleading hints, social pressure

**Usage:**
```bash
python data_generation/generate_qa_dataset.py \
    --output data/qa_dataset.json \
    --seed 42 \
    --num-math 20 \
    --num-factual 20 \
    --num-reasoning 15 \
    --num-edge 10 \
    --num-adversarial 10
```

**Output Format:**
```json
{
  "metadata": {
    "version": "1.0",
    "seed": 42,
    "total_samples": 75
  },
  "qa_pairs": [
    {
      "question": "What is 2 + 2?",
      "answer": "4",
      "category": "math_arithmetic",
      "difficulty": "easy"
    }
  ]
}
```

### `generate_code_problems.py`
Generates programming problems with test cases:
- **Algorithms**: Sorting, searching, recursion
- **Strings**: Manipulation, parsing, pattern matching
- **Data Structures**: Lists, dictionaries, trees
- **Math**: Prime numbers, Fibonacci, combinatorics
- **Edge Cases**: Empty inputs, null handling, boundary conditions

**Usage:**
```bash
python data_generation/generate_code_problems.py \
    --output data/code_problems.json \
    --seed 42
```

**Output Format:**
```json
{
  "metadata": {
    "version": "1.0",
    "seed": 42,
    "language": "python",
    "total_problems": 25
  },
  "problems": [
    {
      "name": "sum_list",
      "description": "Write a function that sums a list",
      "function_signature": "def sum_list(numbers: list) -> int:",
      "test_cases": [
        {"input": [[1, 2, 3]], "expected": 6}
      ],
      "difficulty": "easy",
      "category": "algorithms"
    }
  ]
}
```

### `data_loader.py`
Utility functions for loading and filtering datasets:

```python
from data_generation.data_loader import (
    load_qa_dataset,
    load_code_problems,
    get_qa_pairs_for_evaluator,
    get_code_test_cases,
    create_quick_qa_evaluator
)

# Load full datasets
qa_dataset = load_qa_dataset("data/qa_dataset.json")
code_dataset = load_code_problems("data/code_problems.json")

# Filter QA pairs
easy_math = get_qa_pairs_for_evaluator(
    categories=['math_arithmetic'],
    difficulty='easy',
    max_samples=10
)

# Get test cases for a problem
test_cases = get_code_test_cases('sum_list')

# Quick evaluator creation
evaluator = create_quick_qa_evaluator(num_samples=10, difficulty='easy')
```

## Data Categories

### QA Dataset Categories
- `math_arithmetic`: Basic arithmetic (addition, subtraction, multiplication)
- `math_word_problem`: Word problems requiring reasoning
- `math_percentage`: Percentage calculations
- `math_sequence`: Number sequences and patterns
- `geography`: Country capitals, landmarks, continents
- `history`: Historical events and dates
- `science`: Physics, chemistry, biology
- `literature`: Books, authors, poetry
- `logic`: Logical reasoning and deduction
- `logic_puzzle`: Brain teasers and puzzles
- `edge_case`: Edge cases for robustness testing
- `adversarial`: Adversarial examples (prompt injection, etc.)

### Code Problem Categories
- `algorithms`: Sorting, searching, graph algorithms
- `strings`: String manipulation and processing
- `data_structures`: Lists, stacks, queues, trees
- `mathematics`: Mathematical computations
- `edge_cases`: Null handling, boundary conditions

## Reproducibility

All generators accept a `--seed` parameter for reproducibility:

```bash
# Same seed = same output
python data_generation/generate_qa_dataset.py --seed 42 --output data1.json
python data_generation/generate_qa_dataset.py --seed 42 --output data2.json
# data1.json == data2.json

# Different seed = different output
python data_generation/generate_qa_dataset.py --seed 123 --output data3.json
# data3.json != data1.json
```

## Resource Requirements

- **CPU-only**: No GPU required
- **Memory**: < 100 MB
- **Disk**: < 1 MB per dataset
- **Time**: < 1 second per dataset

## Extending

To add new problem types:

1. Add generator function in `generate_qa_dataset.py` or `generate_code_problems.py`
2. Follow existing format (question/answer or problem/test_cases)
3. Include metadata (category, difficulty)
4. Update `generate_full_dataset()` to include new problems

Example:
```python
def generate_custom_problems() -> List[Dict[str, Any]]:
    return [
        {
            "question": "Your custom question?",
            "answer": "Your answer",
            "category": "custom_category",
            "difficulty": "medium"
        }
    ]

# In generate_full_dataset():
dataset["qa_pairs"].extend(generate_custom_problems())
```

## Testing

Run data loaders to verify datasets:
```bash
python data_generation/data_loader.py
```

Expected output:
```
=== Data Loader Demo ===

1. Loading QA dataset...
   ✓ Loaded 75 QA pairs

2. Getting easy math questions...
   ✓ Found 3 questions
     Q: What is 47 + 82?
     A: 129

3. Loading code problems...
   ✓ Loaded 25 problems

4. Available problems:
     - sum_list
     - reverse_string
     - is_palindrome
     ...

5. Dataset statistics:
   Total samples: 75
   Categories: {'math_arithmetic': 5, 'factual': 20, ...}
```

## Troubleshooting

**Error: Dataset not found**
```
FileNotFoundError: Dataset not found at data/qa_dataset.json
```
**Solution**: Generate the dataset first:
```bash
python data_generation/generate_qa_dataset.py
```

**Error: Module not found**
```
ModuleNotFoundError: No module named 'agent_evolve'
```
**Solution**: Install the package or add to PYTHONPATH:
```bash
pip install -e .
# OR
export PYTHONPATH="${PYTHONPATH}:/path/to/AlphaEvo-Hub"
```
