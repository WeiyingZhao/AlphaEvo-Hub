#!/usr/bin/env python3
"""
Evolution Experiment Harness for Agent Evolve

Unified script for running agent evolution experiments with comprehensive metrics.
Supports multiple evolution strategies, evaluators, and reproducible experiments.

Usage:
    # Quick test (mock LLM, 3 generations)
    python experiments/run_evolution_experiment.py --quick

    # Full evolution experiment
    python experiments/run_evolution_experiment.py \
        --model mock \
        --strategy prompt_optimization \
        --generations 10 \
        --population 5 \
        --seed 42

    # With real LLM (requires API key)
    python experiments/run_evolution_experiment.py \
        --model gpt-3.5-turbo \
        --strategy prompt_optimization \
        --generations 5
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator
from agent_evolve.optimizer.evolutionary import EvolutionConfig

# Ensure data generation is available
try:
    from data_generation.data_loader import (
        get_qa_pairs_for_evaluator,
        get_dataset_statistics
    )
except ImportError:
    print("Warning: data_generation module not in path. Using direct import.")
    sys.path.insert(0, str(Path(__file__).parent.parent / "data_generation"))
    from data_loader import get_qa_pairs_for_evaluator, get_dataset_statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_reproducibility(seed: int = 42):
    """Set all random seeds for reproducibility."""
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)

    # Set for PyTorch if available
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

    logger.info(f"Random seed set to {seed} for reproducibility")


def prepare_dataset(
    categories: List[str] = None,
    difficulty: str = "easy",
    max_samples: int = 10,
    seed: int = 42
) -> List[Dict[str, str]]:
    """
    Prepare QA dataset for evaluation.

    Args:
        categories: List of categories to include
        difficulty: Difficulty level
        max_samples: Maximum number of samples
        seed: Random seed

    Returns:
        List of QA pairs
    """
    logger.info("Preparing dataset...")

    # Check if dataset exists, generate if not
    dataset_path = Path("data/qa_dataset.json")
    if not dataset_path.exists():
        logger.warning("Dataset not found. Generating synthetic data...")
        import subprocess
        subprocess.run([
            sys.executable,
            "data_generation/generate_qa_dataset.py",
            "--output", "data/qa_dataset.json",
            "--seed", str(seed)
        ], check=True)
        logger.info("✓ Dataset generated")

    # Load and filter
    qa_pairs = get_qa_pairs_for_evaluator(
        categories=categories,
        difficulty=difficulty,
        max_samples=max_samples
    )

    logger.info(f"✓ Loaded {len(qa_pairs)} QA pairs")
    if categories:
        logger.info(f"  Categories: {', '.join(categories)}")
    if difficulty:
        logger.info(f"  Difficulty: {difficulty}")

    return qa_pairs


def create_agent(model: str, task: str, seed: int = 42) -> AgentCore:
    """
    Create and configure agent.

    Args:
        model: Model name (e.g., 'mock', 'gpt-3.5-turbo')
        task: Task description
        seed: Random seed

    Returns:
        Configured AgentCore instance
    """
    logger.info(f"Creating agent with model: {model}")

    agent = AgentCore(
        model=model,
        task=task
    )

    logger.info(f"✓ Agent created (provider: {agent.config.model_provider})")
    return agent


def create_evaluator(qa_pairs: List[Dict[str, str]]) -> QAEvaluator:
    """
    Create evaluator from QA pairs.

    Args:
        qa_pairs: List of question-answer pairs

    Returns:
        Configured QAEvaluator
    """
    logger.info("Creating evaluator...")
    evaluator = QAEvaluator(qa_pairs=qa_pairs)
    logger.info(f"✓ Evaluator created with {len(qa_pairs)} test cases")
    return evaluator


def create_optimizer(
    strategy: str,
    generations: int,
    population_size: int,
    mutation_rate: float,
    crossover_rate: float,
    early_stopping: bool,
    patience: int
) -> EvolutionaryOptimizer:
    """
    Create evolution optimizer with configuration.

    Args:
        strategy: Evolution strategy name
        generations: Number of generations
        population_size: Population size
        mutation_rate: Mutation probability
        crossover_rate: Crossover probability
        early_stopping: Enable early stopping
        patience: Generations without improvement before stopping

    Returns:
        Configured EvolutionaryOptimizer
    """
    logger.info("Creating optimizer...")

    config = EvolutionConfig(
        strategy=strategy,
        generations=generations,
        population_size=population_size,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        early_stopping=early_stopping,
        patience=patience
    )

    optimizer = EvolutionaryOptimizer(config=config)

    logger.info(f"✓ Optimizer configured:")
    logger.info(f"  Strategy: {strategy}")
    logger.info(f"  Generations: {generations}")
    logger.info(f"  Population: {population_size}")
    logger.info(f"  Mutation rate: {mutation_rate}")
    logger.info(f"  Crossover rate: {crossover_rate}")

    return optimizer


def run_evolution(
    agent: AgentCore,
    evaluator: QAEvaluator,
    optimizer: EvolutionaryOptimizer,
    qa_pairs: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Run evolution and collect metrics.

    Args:
        agent: Agent to evolve
        evaluator: Evaluator for fitness
        optimizer: Evolution optimizer
        qa_pairs: QA pairs for evaluation tasks

    Returns:
        Dictionary with results and metrics
    """
    logger.info("\n" + "=" * 70)
    logger.info("Starting Evolution")
    logger.info("=" * 70 + "\n")

    # Extract questions for evolution
    tasks = [qa["question"] for qa in qa_pairs]

    # Run evolution
    start_time = time.time()
    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=tasks,
        show_progress=True
    )
    elapsed_time = time.time() - start_time

    logger.info("\n" + "=" * 70)
    logger.info("Evolution Complete")
    logger.info("=" * 70)

    # Calculate metrics
    metrics = calculate_metrics(result, elapsed_time)

    return {
        "result": result,
        "metrics": metrics
    }


def calculate_metrics(result, elapsed_time: float) -> Dict[str, Any]:
    """
    Calculate comprehensive metrics from evolution result.

    Args:
        result: EvolutionResult object
        elapsed_time: Total time in seconds

    Returns:
        Dictionary of metrics
    """
    metrics = {
        "best_score": result.best_score,
        "initial_score": result.generation_scores[0],
        "final_score": result.generation_scores[-1],
        "total_improvement": result.generation_scores[-1] - result.generation_scores[0],
        "percent_improvement": (
            (result.generation_scores[-1] - result.generation_scores[0]) /
            max(result.generation_scores[0], 1e-6) * 100
        ),
        "generations_run": result.total_generations,
        "total_evaluations": len(result.evolution_history),
        "elapsed_time_seconds": elapsed_time,
        "time_per_generation": elapsed_time / result.total_generations,
        "convergence": {
            "converged": result.generation_scores[-1] >= result.best_score * 0.99,
            "stagnation_count": count_stagnation(result.generation_scores)
        },
        "score_statistics": {
            "mean": sum(result.generation_scores) / len(result.generation_scores),
            "min": min(result.generation_scores),
            "max": max(result.generation_scores),
            "std": calculate_std(result.generation_scores)
        }
    }

    return metrics


def count_stagnation(scores: List[float], threshold: float = 0.001) -> int:
    """Count number of generations without significant improvement."""
    stagnation = 0
    for i in range(1, len(scores)):
        if abs(scores[i] - scores[i-1]) < threshold:
            stagnation += 1
    return stagnation


def calculate_std(values: List[float]) -> float:
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def display_results(metrics: Dict[str, Any], result):
    """Display results in a formatted table."""
    print("\n" + "=" * 70)
    print("EVOLUTION RESULTS")
    print("=" * 70)

    print(f"\n📊 Performance Metrics:")
    print(f"  Initial Score:       {metrics['initial_score']:.4f}")
    print(f"  Final Score:         {metrics['final_score']:.4f}")
    print(f"  Best Score:          {metrics['best_score']:.4f}")
    print(f"  Total Improvement:   {metrics['total_improvement']:+.4f}")
    print(f"  % Improvement:       {metrics['percent_improvement']:+.2f}%")

    print(f"\n⏱️  Execution Metrics:")
    print(f"  Generations Run:     {metrics['generations_run']}")
    print(f"  Total Evaluations:   {metrics['total_evaluations']}")
    print(f"  Elapsed Time:        {metrics['elapsed_time_seconds']:.2f}s")
    print(f"  Time per Gen:        {metrics['time_per_generation']:.2f}s")

    print(f"\n📈 Score Statistics:")
    print(f"  Mean:                {metrics['score_statistics']['mean']:.4f}")
    print(f"  Std Dev:             {metrics['score_statistics']['std']:.4f}")
    print(f"  Min:                 {metrics['score_statistics']['min']:.4f}")
    print(f"  Max:                 {metrics['score_statistics']['max']:.4f}")

    print(f"\n🎯 Convergence:")
    print(f"  Converged:           {metrics['convergence']['converged']}")
    print(f"  Stagnation Count:    {metrics['convergence']['stagnation_count']}")

    print(f"\n📜 Generation History:")
    for i, score in enumerate(result.generation_scores, 1):
        improvement = ""
        if i > 1:
            diff = score - result.generation_scores[i-2]
            improvement = f" ({diff:+.4f})"
        marker = "🏆" if score == metrics['best_score'] else "  "
        print(f"  {marker} Gen {i:2d}: {score:.4f}{improvement}")

    print("\n" + "=" * 70)


def save_results(
    metrics: Dict[str, Any],
    result,
    output_dir: Path,
    experiment_name: str
):
    """
    Save experiment results to disk.

    Args:
        metrics: Metrics dictionary
        result: EvolutionResult object
        output_dir: Output directory
        experiment_name: Name for this experiment
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save metrics as JSON
    metrics_file = output_dir / f"{experiment_name}_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"✓ Metrics saved to {metrics_file}")

    # Save evolution report
    report_file = output_dir / f"{experiment_name}_report.md"
    result.export_report(str(report_file))
    logger.info(f"✓ Report saved to {report_file}")

    # Save best config
    config_file = output_dir / f"{experiment_name}_best_config.json"
    with open(config_file, 'w') as f:
        json.dump(result.best_agent_config, f, indent=2)
    logger.info(f"✓ Best config saved to {config_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run evolution experiments for Agent Evolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Experiment configuration
    parser.add_argument("--quick", action="store_true", help="Quick test mode (mock LLM, 3 generations)")
    parser.add_argument("--model", type=str, default="mock", help="LLM model to use")
    parser.add_argument("--strategy", type=str, default="prompt_optimization",
                        choices=["prompt_optimization", "memory_evolution", "tool_evolution", "code_evolution"],
                        help="Evolution strategy")
    parser.add_argument("--generations", type=int, default=5, help="Number of generations")
    parser.add_argument("--population", type=int, default=5, help="Population size")
    parser.add_argument("--mutation-rate", type=float, default=0.3, help="Mutation rate")
    parser.add_argument("--crossover-rate", type=float, default=0.7, help="Crossover rate")
    parser.add_argument("--no-early-stopping", action="store_true", help="Disable early stopping")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")

    # Dataset configuration
    parser.add_argument("--num-samples", type=int, default=10, help="Number of QA samples")
    parser.add_argument("--difficulty", type=str, default="easy",
                        choices=["easy", "medium", "hard"],
                        help="Question difficulty")
    parser.add_argument("--categories", type=str, nargs="+",
                        help="QA categories to include (e.g., math factual)")

    # Reproducibility
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    # Output
    parser.add_argument("--output-dir", type=str, default="results/experiments",
                        help="Output directory for results")
    parser.add_argument("--experiment-name", type=str, default=None,
                        help="Name for this experiment")

    args = parser.parse_args()

    # Quick mode overrides
    if args.quick:
        args.model = "mock"
        args.generations = 3
        args.population = 3
        args.num_samples = 5
        logger.info("🚀 Quick test mode enabled")

    # Set reproducibility
    setup_reproducibility(args.seed)

    # Generate experiment name
    if args.experiment_name is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        args.experiment_name = f"{args.strategy}_{args.model}_{timestamp}"

    try:
        # Step 1: Prepare dataset
        qa_pairs = prepare_dataset(
            categories=args.categories,
            difficulty=args.difficulty,
            max_samples=args.num_samples,
            seed=args.seed
        )

        # Step 2: Create agent
        agent = create_agent(
            model=args.model,
            task="Answer questions accurately and concisely",
            seed=args.seed
        )

        # Step 3: Create evaluator
        evaluator = create_evaluator(qa_pairs)

        # Step 4: Create optimizer
        optimizer = create_optimizer(
            strategy=args.strategy,
            generations=args.generations,
            population_size=args.population,
            mutation_rate=args.mutation_rate,
            crossover_rate=args.crossover_rate,
            early_stopping=not args.no_early_stopping,
            patience=args.patience
        )

        # Step 5: Run evolution
        results = run_evolution(agent, evaluator, optimizer, qa_pairs)

        # Step 6: Display results
        display_results(results["metrics"], results["result"])

        # Step 7: Save results
        output_dir = Path(args.output_dir)
        save_results(
            results["metrics"],
            results["result"],
            output_dir,
            args.experiment_name
        )

        print(f"\n✅ Experiment complete! Results saved to {output_dir}/{args.experiment_name}_*")
        return 0

    except Exception as e:
        logger.error(f"Experiment failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
