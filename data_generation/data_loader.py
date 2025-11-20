"""
Data Loader Utilities for Agent Evolve

Provides convenient functions to load generated datasets and convert them
to formats compatible with Agent Evolve evaluators.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_qa_dataset(filepath: str = "data/qa_dataset.json") -> Dict[str, Any]:
    """
    Load QA dataset from JSON file.

    Args:
        filepath: Path to QA dataset JSON file

    Returns:
        Dictionary with metadata and qa_pairs

    Raises:
        FileNotFoundError: If dataset file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. "
            "Generate it first:\n"
            "  python data_generation/generate_qa_dataset.py --output data/qa_dataset.json"
        )

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_code_problems(filepath: str = "data/code_problems.json") -> Dict[str, Any]:
    """
    Load code problems dataset from JSON file.

    Args:
        filepath: Path to code problems JSON file

    Returns:
        Dictionary with metadata and problems

    Raises:
        FileNotFoundError: If dataset file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. "
            "Generate it first:\n"
            "  python data_generation/generate_code_problems.py --output data/code_problems.json"
        )

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_qa_pairs_for_evaluator(
    filepath: str = "data/qa_dataset.json",
    categories: Optional[List[str]] = None,
    difficulty: Optional[str] = None,
    max_samples: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Load QA pairs filtered by criteria, ready for QAEvaluator.

    Args:
        filepath: Path to QA dataset JSON file
        categories: List of categories to include (e.g., ['math', 'factual'])
        difficulty: Difficulty level ('easy', 'medium', 'hard')
        max_samples: Maximum number of samples to return

    Returns:
        List of {"question": ..., "answer": ...} dictionaries

    Example:
        >>> from agent_evolve.evaluator import QAEvaluator
        >>> from data_generation.data_loader import get_qa_pairs_for_evaluator
        >>>
        >>> qa_pairs = get_qa_pairs_for_evaluator(
        ...     categories=['math', 'factual'],
        ...     difficulty='easy',
        ...     max_samples=10
        ... )
        >>> evaluator = QAEvaluator(qa_pairs=qa_pairs)
    """
    dataset = load_qa_dataset(filepath)
    qa_pairs = dataset["qa_pairs"]

    # Filter by category
    if categories:
        qa_pairs = [qa for qa in qa_pairs if qa.get("category") in categories]

    # Filter by difficulty
    if difficulty:
        qa_pairs = [qa for qa in qa_pairs if qa.get("difficulty") == difficulty]

    # Limit samples
    if max_samples:
        qa_pairs = qa_pairs[:max_samples]

    # Return in evaluator format
    return [{"question": qa["question"], "answer": qa["answer"]} for qa in qa_pairs]


def get_code_test_cases(
    problem_name: str,
    filepath: str = "data/code_problems.json"
) -> List[Dict[str, Any]]:
    """
    Get test cases for a specific code problem.

    Args:
        problem_name: Name of the problem (e.g., 'sum_list')
        filepath: Path to code problems JSON file

    Returns:
        List of test cases with 'input' and 'expected' fields

    Raises:
        ValueError: If problem not found

    Example:
        >>> test_cases = get_code_test_cases('sum_list')
        >>> for tc in test_cases:
        ...     input_data = tc['input']
        ...     expected = tc['expected']
        ...     result = sum_list(*input_data)
        ...     assert result == expected
    """
    dataset = load_code_problems(filepath)

    for problem in dataset["problems"]:
        if problem["name"] == problem_name:
            return problem["test_cases"]

    raise ValueError(
        f"Problem '{problem_name}' not found. "
        f"Available problems: {[p['name'] for p in dataset['problems']]}"
    )


def get_all_problem_names(filepath: str = "data/code_problems.json") -> List[str]:
    """Get list of all available problem names."""
    dataset = load_code_problems(filepath)
    return [problem["name"] for problem in dataset["problems"]]


def get_problem_description(
    problem_name: str,
    filepath: str = "data/code_problems.json"
) -> Dict[str, Any]:
    """
    Get complete problem description including signature, hints, and test cases.

    Args:
        problem_name: Name of the problem
        filepath: Path to code problems JSON file

    Returns:
        Problem dictionary with all details

    Raises:
        ValueError: If problem not found
    """
    dataset = load_code_problems(filepath)

    for problem in dataset["problems"]:
        if problem["name"] == problem_name:
            return problem

    raise ValueError(f"Problem '{problem_name}' not found")


def create_quick_qa_evaluator(
    num_samples: int = 10,
    seed: int = 42,
    difficulty: str = "easy"
):
    """
    Convenience function to quickly create a QAEvaluator with synthetic data.

    Args:
        num_samples: Number of QA pairs to use
        seed: Random seed for reproducibility
        difficulty: Difficulty level

    Returns:
        Configured QAEvaluator instance

    Example:
        >>> evaluator = create_quick_qa_evaluator(num_samples=5, difficulty='easy')
        >>> # Use with optimizer
        >>> result = optimizer.evolve(agent, evaluator)
    """
    from agent_evolve.evaluator import QAEvaluator

    try:
        qa_pairs = get_qa_pairs_for_evaluator(
            difficulty=difficulty,
            max_samples=num_samples
        )
    except FileNotFoundError:
        # Generate dataset on the fly
        print("Dataset not found. Generating synthetic data...")
        import subprocess
        subprocess.run([
            "python", "data_generation/generate_qa_dataset.py",
            "--output", "data/qa_dataset.json",
            "--seed", str(seed)
        ], check=True)

        qa_pairs = get_qa_pairs_for_evaluator(
            difficulty=difficulty,
            max_samples=num_samples
        )

    return QAEvaluator(qa_pairs=qa_pairs)


def get_dataset_statistics(qa_filepath: str = "data/qa_dataset.json") -> Dict[str, Any]:
    """
    Get statistics about the QA dataset.

    Args:
        qa_filepath: Path to QA dataset

    Returns:
        Dictionary with statistics
    """
    dataset = load_qa_dataset(qa_filepath)
    qa_pairs = dataset["qa_pairs"]

    # Count by category
    category_counts = {}
    for qa in qa_pairs:
        cat = qa.get("category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count by difficulty
    difficulty_counts = {}
    for qa in qa_pairs:
        diff = qa.get("difficulty", "unknown")
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

    return {
        "total_samples": len(qa_pairs),
        "categories": category_counts,
        "difficulties": difficulty_counts,
        "metadata": dataset["metadata"]
    }


if __name__ == "__main__":
    # Demo usage
    print("=== Data Loader Demo ===\n")

    try:
        # Load QA dataset
        print("1. Loading QA dataset...")
        qa_data = load_qa_dataset()
        print(f"   ✓ Loaded {qa_data['metadata']['total_samples']} QA pairs")

        # Get filtered QA pairs
        print("\n2. Getting easy math questions...")
        math_qa = get_qa_pairs_for_evaluator(categories=['math_arithmetic'], difficulty='easy', max_samples=3)
        print(f"   ✓ Found {len(math_qa)} questions")
        for qa in math_qa[:2]:
            print(f"     Q: {qa['question']}")
            print(f"     A: {qa['answer']}")

        # Load code problems
        print("\n3. Loading code problems...")
        code_data = load_code_problems()
        print(f"   ✓ Loaded {code_data['metadata']['total_problems']} problems")

        # Get problem names
        print("\n4. Available problems:")
        for name in get_all_problem_names()[:5]:
            print(f"     - {name}")

        # Get statistics
        print("\n5. Dataset statistics:")
        stats = get_dataset_statistics()
        print(f"   Total samples: {stats['total_samples']}")
        print(f"   Categories: {stats['categories']}")

    except FileNotFoundError as e:
        print(f"\n⚠ {e}")
        print("\nGenerate datasets first:")
        print("  python data_generation/generate_qa_dataset.py")
        print("  python data_generation/generate_code_problems.py")
