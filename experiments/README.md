# Experiments Directory

This directory contains experiment harnesses and evaluation scripts for Agent Evolve.

## Quick Start

### Run a Quick Test (No API Keys)

```bash
# Quick 3-generation evolution test with mock LLM
python experiments/run_evolution_experiment.py --quick
```

### Run Full Evolution Experiment

```bash
# 10 generations with prompt optimization
python experiments/run_evolution_experiment.py \
    --model mock \
    --strategy prompt_optimization \
    --generations 10 \
    --population 5 \
    --num-samples 20 \
    --seed 42
```

### Evaluate Agent (No Evolution)

```bash
# Quick baseline evaluation
python experiments/evaluate_agent.py \
    --model mock \
    --num-samples 10 \
    --difficulty easy
```

## Scripts

### `run_evolution_experiment.py`
**Complete evolution experiment harness** with:
- Dataset preparation (auto-generates if missing)
- Agent creation and configuration
- Evolution with configurable parameters
- Comprehensive metrics (improvement, convergence, timing)
- Result visualization and export

**Key Features:**
- ✅ Reproducible (fixed random seeds)
- ✅ CPU-only (no GPU required)
- ✅ Progress bars with tqdm
- ✅ Early stopping support
- ✅ Saves metrics, reports, and best configs
- ✅ Works with mock LLM (no API keys needed)

**Example Usage:**

```bash
# Quick test (mock LLM, 3 gens, 5 samples)
python experiments/run_evolution_experiment.py --quick

# Custom configuration
python experiments/run_evolution_experiment.py \
    --model mock \
    --strategy prompt_optimization \
    --generations 10 \
    --population 5 \
    --mutation-rate 0.3 \
    --crossover-rate 0.7 \
    --num-samples 20 \
    --difficulty easy \
    --categories math factual \
    --seed 42 \
    --output-dir results/my_experiment

# With real LLM (set API key first)
export OPENAI_API_KEY="your-key"
python experiments/run_evolution_experiment.py \
    --model gpt-3.5-turbo \
    --strategy prompt_optimization \
    --generations 5 \
    --num-samples 10
```

**Arguments:**
- `--quick`: Quick test mode (overrides other settings)
- `--model`: LLM model (`mock`, `gpt-3.5-turbo`, `claude-3-sonnet-20240229`)
- `--strategy`: Evolution strategy (`prompt_optimization`, `memory_evolution`, `tool_evolution`, `code_evolution`)
- `--generations`: Number of evolution generations (default: 5)
- `--population`: Population size (default: 5)
- `--mutation-rate`: Mutation probability 0.0-1.0 (default: 0.3)
- `--crossover-rate`: Crossover probability 0.0-1.0 (default: 0.7)
- `--no-early-stopping`: Disable early stopping
- `--patience`: Generations without improvement before stopping (default: 3)
- `--num-samples`: Number of QA samples (default: 10)
- `--difficulty`: Question difficulty (`easy`, `medium`, `hard`)
- `--categories`: QA categories (e.g., `math factual reasoning`)
- `--seed`: Random seed for reproducibility (default: 42)
- `--output-dir`: Output directory (default: `results/experiments`)
- `--experiment-name`: Custom experiment name

**Output Files:**
```
results/experiments/
├── {experiment_name}_metrics.json      # Comprehensive metrics
├── {experiment_name}_report.md         # Evolution report
└── {experiment_name}_best_config.json  # Best agent configuration
```

**Metrics Computed:**
- **Performance**: Initial/final/best score, improvement, % improvement
- **Execution**: Generations run, total evaluations, elapsed time
- **Statistics**: Mean, std dev, min, max of scores
- **Convergence**: Stagnation count, convergence status

### `evaluate_agent.py`
**Simple agent evaluation** without evolution:
- Quick baseline measurements
- Sanity checks before evolution
- Faster than full evolution

**Example Usage:**

```bash
# Basic evaluation
python experiments/evaluate_agent.py --model mock --num-samples 10

# With filtering
python experiments/evaluate_agent.py \
    --model mock \
    --num-samples 20 \
    --difficulty easy \
    --categories math factual \
    --output results/baseline_eval.json
```

**Arguments:**
- `--model`: LLM model (default: `mock`)
- `--num-samples`: Number of samples (default: 10)
- `--difficulty`: Difficulty level (default: `easy`)
- `--categories`: Categories to include
- `--seed`: Random seed (default: 42)
- `--output`: Save results to JSON file

## Example Workflows

### 1. Quick Sanity Check

```bash
# Test that everything works (< 1 minute)
python experiments/run_evolution_experiment.py --quick
```

### 2. Baseline Evaluation

```bash
# Evaluate agent before evolution
python experiments/evaluate_agent.py \
    --model mock \
    --num-samples 20 \
    --output results/baseline.json
```

### 3. Compare Evolution Strategies

```bash
# Try different strategies
for strategy in prompt_optimization memory_evolution tool_evolution; do
    python experiments/run_evolution_experiment.py \
        --model mock \
        --strategy $strategy \
        --generations 10 \
        --output-dir results/$strategy
done
```

### 4. Reproduce Published Results

```bash
# Use same seed for reproducibility
python experiments/run_evolution_experiment.py \
    --seed 42 \
    --model mock \
    --strategy prompt_optimization \
    --generations 10 \
    --population 5
```

### 5. Grid Search Over Hyperparameters

```bash
# Search mutation rates
for rate in 0.1 0.3 0.5; do
    python experiments/run_evolution_experiment.py \
        --model mock \
        --mutation-rate $rate \
        --experiment-name "mutation_${rate}"
done
```

## Expected Output

### Console Output

```
INFO: Random seed set to 42 for reproducibility
INFO: Preparing dataset...
INFO: ✓ Loaded 10 QA pairs
INFO: Creating agent with model: mock
INFO: ✓ Agent created (provider: mock)
INFO: Creating evaluator...
INFO: ✓ Evaluator created with 10 test cases
INFO: Creating optimizer...
INFO: ✓ Optimizer configured:
  Strategy: prompt_optimization
  Generations: 5
  Population: 5

======================================================================
Starting Evolution
======================================================================

Evolution Progress: 100%|████████████| 5/5 [00:02<00:00, 2.31gen/s]

======================================================================
Evolution Complete
======================================================================

======================================================================
EVOLUTION RESULTS
======================================================================

📊 Performance Metrics:
  Initial Score:       0.5000
  Final Score:         0.7500
  Best Score:          0.7500
  Total Improvement:   +0.2500
  % Improvement:       +50.00%

⏱️  Execution Metrics:
  Generations Run:     5
  Total Evaluations:   25
  Elapsed Time:        2.16s
  Time per Gen:        0.43s

📈 Score Statistics:
  Mean:                0.6500
  Std Dev:             0.1118
  Min:                 0.5000
  Max:                 0.7500

🎯 Convergence:
  Converged:           True
  Stagnation Count:    2

📜 Generation History:
     Gen  1: 0.5000
     Gen  2: 0.6000 (+0.1000)
     Gen  3: 0.7000 (+0.1000)
  🏆  Gen  4: 0.7500 (+0.0500)
     Gen  5: 0.7500 (+0.0000)

======================================================================

✓ Metrics saved to results/experiments/prompt_optimization_mock_20240115_143022_metrics.json
✓ Report saved to results/experiments/prompt_optimization_mock_20240115_143022_report.md
✓ Best config saved to results/experiments/prompt_optimization_mock_20240115_143022_best_config.json

✅ Experiment complete! Results saved to results/experiments/prompt_optimization_mock_20240115_143022_*
```

## Troubleshooting

### Error: Dataset not found
```
FileNotFoundError: Dataset not found at data/qa_dataset.json
```
**Solution**: The script auto-generates datasets. If this fails, generate manually:
```bash
python data_generation/generate_qa_dataset.py
```

### Error: Module not found
```
ModuleNotFoundError: No module named 'agent_evolve'
```
**Solution**: Install the package or set PYTHONPATH:
```bash
pip install -e .
# OR
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: API key not found
```
ValueError: OpenAI API key not found
```
**Solution**: Use mock model or set API key:
```bash
# Use mock (no API key needed)
python experiments/run_evolution_experiment.py --model mock

# OR set API key
export OPENAI_API_KEY="your-key-here"
```

### Slow execution
**Solution**: Reduce generations or samples:
```bash
python experiments/run_evolution_experiment.py \
    --quick \
    --generations 3 \
    --num-samples 5
```

## Tips

1. **Start with `--quick`** to verify everything works
2. **Use `mock` model** for development (fast, free, no API keys)
3. **Set `--seed`** for reproducible experiments
4. **Enable early stopping** (default) to save time
5. **Use `--categories`** to focus on specific problem types
6. **Save results** with `--output-dir` for later analysis
7. **Compare strategies** by running multiple experiments
8. **Monitor progress** with the progress bars (requires tqdm)

## Next Steps

After running experiments:
1. Check `results/experiments/` for outputs
2. Compare metrics across different strategies
3. Analyze best configurations
4. Try with real LLMs (gpt-3.5-turbo, claude-3-sonnet)
5. Increase generations for longer evolution runs
6. Experiment with different hyperparameters
