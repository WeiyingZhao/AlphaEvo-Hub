#!/usr/bin/env python3
"""
Agent Evaluation Script (No Evolution)

Quick evaluation of an agent on a dataset without running evolution.
Useful for baseline measurements and sanity checks.

Usage:
    # Quick evaluation with mock LLM
    python experiments/evaluate_agent.py --model mock --num-samples 5

    # Full evaluation
    python experiments/evaluate_agent.py \
        --model mock \
        --num-samples 20 \
        --difficulty easy \
        --categories math factual
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_evolve import AgentCore
from agent_evolve.evaluator import QAEvaluator
from data_generation.data_loader import get_qa_pairs_for_evaluator

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def evaluate_agent(
    model: str,
    qa_pairs: List[Dict[str, str]],
    task: str = "Answer questions accurately"
) -> Dict[str, Any]:
    """
    Evaluate an agent on QA tasks.

    Args:
        model: Model name
        qa_pairs: List of QA pairs
        task: Task description

    Returns:
        Dictionary with evaluation results
    """
    logger.info(f"Creating agent with model: {model}")
    agent = AgentCore(model=model, task=task)

    logger.info(f"Creating evaluator with {len(qa_pairs)} test cases")
    evaluator = QAEvaluator(qa_pairs=qa_pairs)

    # Extract tasks
    tasks = [qa["question"] for qa in qa_pairs]

    logger.info("Running evaluation...")
    start_time = time.time()

    # Evaluate
    score = evaluator.evaluate(agent, tasks)

    elapsed_time = time.time() - start_time

    results = {
        "model": model,
        "score": score,
        "num_samples": len(qa_pairs),
        "elapsed_time": elapsed_time,
        "time_per_sample": elapsed_time / len(qa_pairs)
    }

    return results


def display_results(results: Dict[str, Any]):
    """Display evaluation results."""
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"\nModel:              {results['model']}")
    print(f"Score:              {results['score']:.4f}")
    print(f"Samples:            {results['num_samples']}")
    print(f"Total Time:         {results['elapsed_time']:.2f}s")
    print(f"Time per Sample:    {results['time_per_sample']:.3f}s")
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Evaluate agent without evolution")
    parser.add_argument("--model", type=str, default="mock", help="LLM model")
    parser.add_argument("--num-samples", type=int, default=10, help="Number of samples")
    parser.add_argument("--difficulty", type=str, default="easy", help="Difficulty level")
    parser.add_argument("--categories", type=str, nargs="+", help="Categories to include")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, help="Output JSON file")

    args = parser.parse_args()

    # Prepare dataset
    logger.info("Loading dataset...")
    dataset_path = Path("data/qa_dataset.json")
    if not dataset_path.exists():
        logger.info("Dataset not found. Generating...")
        import subprocess
        subprocess.run([
            sys.executable,
            "data_generation/generate_qa_dataset.py",
            "--output", "data/qa_dataset.json",
            "--seed", str(args.seed)
        ], check=True)

    qa_pairs = get_qa_pairs_for_evaluator(
        categories=args.categories,
        difficulty=args.difficulty,
        max_samples=args.num_samples
    )

    # Evaluate
    results = evaluate_agent(args.model, qa_pairs)

    # Display
    display_results(results)

    # Save if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
