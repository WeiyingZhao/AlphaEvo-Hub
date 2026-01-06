#!/usr/bin/env python3
"""
Synthetic Code Problem Generator for Agent Evolve

Generates Python coding problems with test cases for code evolution.
Includes: algorithms, data structures, string manipulation, math, and edge cases.

Usage:
    python data_generation/generate_code_problems.py --output data/code_problems.json --seed 42
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple


def set_seed(seed: int = 42):
    """Set random seed for reproducibility."""
    random.seed(seed)


def generate_algorithm_problems() -> List[Dict[str, Any]]:
    """Generate algorithmic problems."""
    problems = [
        {
            "name": "sum_list",
            "description": "Write a function that takes a list of numbers and returns their sum.",
            "function_signature": "def sum_list(numbers: list) -> int:",
            "test_cases": [
                {"input": [[1, 2, 3]], "expected": 6},
                {"input": [[10, 20, 30]], "expected": 60},
                {"input": [[-5, 5]], "expected": 0},
                {"input": [[]], "expected": 0},
                {"input": [[100]], "expected": 100},
            ],
            "difficulty": "easy",
            "category": "algorithms",
            "hints": ["Use a loop or built-in sum() function"]
        },
        {
            "name": "reverse_string",
            "description": "Write a function that reverses a string.",
            "function_signature": "def reverse_string(s: str) -> str:",
            "test_cases": [
                {"input": ["hello"], "expected": "olleh"},
                {"input": ["world"], "expected": "dlrow"},
                {"input": [""], "expected": ""},
                {"input": ["a"], "expected": "a"},
                {"input": ["python"], "expected": "nohtyp"},
            ],
            "difficulty": "easy",
            "category": "strings",
            "hints": ["Use string slicing [::-1]"]
        },
        {
            "name": "is_palindrome",
            "description": "Write a function that checks if a string is a palindrome (reads the same forwards and backwards).",
            "function_signature": "def is_palindrome(s: str) -> bool:",
            "test_cases": [
                {"input": ["racecar"], "expected": True},
                {"input": ["hello"], "expected": False},
                {"input": [""], "expected": True},
                {"input": ["a"], "expected": True},
                {"input": ["noon"], "expected": True},
            ],
            "difficulty": "easy",
            "category": "strings",
            "hints": ["Compare string with its reverse"]
        },
        {
            "name": "find_max",
            "description": "Write a function that finds the maximum value in a list.",
            "function_signature": "def find_max(numbers: list) -> int:",
            "test_cases": [
                {"input": [[1, 5, 3, 9, 2]], "expected": 9},
                {"input": [[-10, -5, -20]], "expected": -5},
                {"input": [[42]], "expected": 42},
                {"input": [[0, 0, 0]], "expected": 0},
                {"input": [[100, 200, 150]], "expected": 200},
            ],
            "difficulty": "easy",
            "category": "algorithms",
            "hints": ["Use built-in max() or iterate through list"]
        },
        {
            "name": "count_vowels",
            "description": "Write a function that counts the number of vowels (a, e, i, o, u) in a string.",
            "function_signature": "def count_vowels(s: str) -> int:",
            "test_cases": [
                {"input": ["hello"], "expected": 2},
                {"input": ["python"], "expected": 1},
                {"input": ["aeiou"], "expected": 5},
                {"input": ["xyz"], "expected": 0},
                {"input": [""], "expected": 0},
            ],
            "difficulty": "easy",
            "category": "strings",
            "hints": ["Iterate and check if character is in 'aeiou'"]
        },
        {
            "name": "fibonacci",
            "description": "Write a function that returns the nth Fibonacci number (0-indexed).",
            "function_signature": "def fibonacci(n: int) -> int:",
            "test_cases": [
                {"input": [0], "expected": 0},
                {"input": [1], "expected": 1},
                {"input": [2], "expected": 1},
                {"input": [5], "expected": 5},
                {"input": [10], "expected": 55},
            ],
            "difficulty": "medium",
            "category": "algorithms",
            "hints": ["Use recursion or iteration. F(n) = F(n-1) + F(n-2)"]
        },
        {
            "name": "is_prime",
            "description": "Write a function that checks if a number is prime.",
            "function_signature": "def is_prime(n: int) -> bool:",
            "test_cases": [
                {"input": [2], "expected": True},
                {"input": [3], "expected": True},
                {"input": [4], "expected": False},
                {"input": [17], "expected": True},
                {"input": [1], "expected": False},
            ],
            "difficulty": "medium",
            "category": "mathematics",
            "hints": ["Check divisibility from 2 to sqrt(n)"]
        },
        {
            "name": "remove_duplicates",
            "description": "Write a function that removes duplicates from a list while preserving order.",
            "function_signature": "def remove_duplicates(lst: list) -> list:",
            "test_cases": [
                {"input": [[1, 2, 2, 3, 4, 4, 5]], "expected": [1, 2, 3, 4, 5]},
                {"input": [[1, 1, 1]], "expected": [1]},
                {"input": [[]], "expected": []},
                {"input": [[1, 2, 3]], "expected": [1, 2, 3]},
                {"input": [["a", "b", "a", "c"]], "expected": ["a", "b", "c"]},
            ],
            "difficulty": "easy",
            "category": "data_structures",
            "hints": ["Use a set to track seen elements"]
        },
        {
            "name": "binary_search",
            "description": "Write a function that performs binary search on a sorted list. Return the index of the target, or -1 if not found.",
            "function_signature": "def binary_search(arr: list, target: int) -> int:",
            "test_cases": [
                {"input": [[1, 2, 3, 4, 5], 3], "expected": 2},
                {"input": [[1, 2, 3, 4, 5], 1], "expected": 0},
                {"input": [[1, 2, 3, 4, 5], 5], "expected": 4},
                {"input": [[1, 2, 3, 4, 5], 6], "expected": -1},
                {"input": [[], 1], "expected": -1},
            ],
            "difficulty": "medium",
            "category": "algorithms",
            "hints": ["Compare middle element, narrow search range"]
        },
        {
            "name": "merge_sorted_lists",
            "description": "Write a function that merges two sorted lists into one sorted list.",
            "function_signature": "def merge_sorted_lists(list1: list, list2: list) -> list:",
            "test_cases": [
                {"input": [[1, 3, 5], [2, 4, 6]], "expected": [1, 2, 3, 4, 5, 6]},
                {"input": [[1, 2, 3], []], "expected": [1, 2, 3]},
                {"input": [[], [4, 5, 6]], "expected": [4, 5, 6]},
                {"input": [[1], [2]], "expected": [1, 2]},
                {"input": [[], []], "expected": []},
            ],
            "difficulty": "medium",
            "category": "algorithms",
            "hints": ["Use two pointers to compare elements"]
        }
    ]

    return problems


def generate_string_problems() -> List[Dict[str, Any]]:
    """Generate string manipulation problems."""
    problems = [
        {
            "name": "capitalize_words",
            "description": "Write a function that capitalizes the first letter of each word in a string.",
            "function_signature": "def capitalize_words(s: str) -> str:",
            "test_cases": [
                {"input": ["hello world"], "expected": "Hello World"},
                {"input": ["python programming"], "expected": "Python Programming"},
                {"input": [""], "expected": ""},
                {"input": ["a"], "expected": "A"},
                {"input": ["one two three"], "expected": "One Two Three"},
            ],
            "difficulty": "easy",
            "category": "strings",
            "hints": ["Split by spaces, capitalize each word"]
        },
        {
            "name": "count_words",
            "description": "Write a function that counts the number of words in a string.",
            "function_signature": "def count_words(s: str) -> int:",
            "test_cases": [
                {"input": ["hello world"], "expected": 2},
                {"input": ["one two three four"], "expected": 4},
                {"input": [""], "expected": 0},
                {"input": ["single"], "expected": 1},
                {"input": ["  spaces  everywhere  "], "expected": 2},
            ],
            "difficulty": "easy",
            "category": "strings",
            "hints": ["Split by whitespace and count"]
        },
        {
            "name": "longest_word",
            "description": "Write a function that finds the longest word in a string.",
            "function_signature": "def longest_word(s: str) -> str:",
            "test_cases": [
                {"input": ["the quick brown fox"], "expected": "quick"},
                {"input": ["python is awesome"], "expected": "awesome"},
                {"input": ["a"], "expected": "a"},
                {"input": ["one two three"], "expected": "three"},
                {"input": [""], "expected": ""},
            ],
            "difficulty": "easy",
            "category": "strings",
            "hints": ["Split and compare lengths"]
        }
    ]

    return problems


def generate_data_structure_problems() -> List[Dict[str, Any]]:
    """Generate data structure problems."""
    problems = [
        {
            "name": "flatten_list",
            "description": "Write a function that flattens a nested list.",
            "function_signature": "def flatten_list(nested: list) -> list:",
            "test_cases": [
                {"input": [[[1, 2], [3, 4]]], "expected": [1, 2, 3, 4]},
                {"input": [[[1], [2], [3]]], "expected": [1, 2, 3]},
                {"input": [[[1, [2, [3]]]]], "expected": [1, 2, 3]},
                {"input": [[[]]], "expected": []},
                {"input": [[[1, 2, 3]]], "expected": [1, 2, 3]},
            ],
            "difficulty": "medium",
            "category": "data_structures",
            "hints": ["Use recursion or itertools.chain"]
        },
        {
            "name": "group_by_key",
            "description": "Write a function that groups a list of dictionaries by a specific key.",
            "function_signature": "def group_by_key(items: list, key: str) -> dict:",
            "test_cases": [
                {
                    "input": [[{"type": "fruit", "name": "apple"}, {"type": "fruit", "name": "banana"}], "type"],
                    "expected": {"fruit": [{"type": "fruit", "name": "apple"}, {"type": "fruit", "name": "banana"}]}
                },
                {
                    "input": [[{"age": 20, "name": "Alice"}, {"age": 20, "name": "Bob"}], "age"],
                    "expected": {20: [{"age": 20, "name": "Alice"}, {"age": 20, "name": "Bob"}]}
                },
                {"input": [[], "key"], "expected": {}},
            ],
            "difficulty": "medium",
            "category": "data_structures",
            "hints": ["Use a dictionary to collect items by key value"]
        }
    ]

    return problems


def generate_edge_case_problems() -> List[Dict[str, Any]]:
    """Generate problems with important edge cases."""
    problems = [
        {
            "name": "safe_divide",
            "description": "Write a function that divides two numbers, returning None if division by zero.",
            "function_signature": "def safe_divide(a: float, b: float) -> float:",
            "test_cases": [
                {"input": [10, 2], "expected": 5.0},
                {"input": [10, 0], "expected": None},
                {"input": [0, 5], "expected": 0.0},
                {"input": [-10, 2], "expected": -5.0},
                {"input": [7, 2], "expected": 3.5},
            ],
            "difficulty": "easy",
            "category": "edge_cases",
            "hints": ["Check for b == 0 before dividing"]
        },
        {
            "name": "get_nth_element",
            "description": "Write a function that safely gets the nth element from a list, returning None if index is out of bounds.",
            "function_signature": "def get_nth_element(lst: list, n: int):",
            "test_cases": [
                {"input": [[1, 2, 3], 0], "expected": 1},
                {"input": [[1, 2, 3], 2], "expected": 3},
                {"input": [[1, 2, 3], 5], "expected": None},
                {"input": [[1, 2, 3], -1], "expected": 3},
                {"input": [[], 0], "expected": None},
            ],
            "difficulty": "easy",
            "category": "edge_cases",
            "hints": ["Check if index is valid before accessing"]
        }
    ]

    return problems


def generate_full_dataset(seed: int = 42) -> Dict[str, Any]:
    """Generate complete code problems dataset."""
    set_seed(seed)

    dataset = {
        "metadata": {
            "version": "1.0",
            "seed": seed,
            "language": "python",
            "categories": ["algorithms", "strings", "data_structures", "mathematics", "edge_cases"]
        },
        "problems": []
    }

    # Generate all categories
    dataset["problems"].extend(generate_algorithm_problems())
    dataset["problems"].extend(generate_string_problems())
    dataset["problems"].extend(generate_data_structure_problems())
    dataset["problems"].extend(generate_edge_case_problems())

    # Add metadata
    dataset["metadata"]["total_problems"] = len(dataset["problems"])

    return dataset


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic code problems")
    parser.add_argument("--output", type=str, default="data/code_problems.json", help="Output file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")

    args = parser.parse_args()

    # Generate dataset
    print(f"Generating code problems with seed={args.seed}...")
    dataset = generate_full_dataset(seed=args.seed)

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save dataset
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"✓ Dataset saved to {output_path}")
    print(f"  Total problems: {dataset['metadata']['total_problems']}")
    print(f"  Categories: {', '.join(dataset['metadata']['categories'])}")

    # Print sample
    print("\nSample problems:")
    for i, problem in enumerate(dataset["problems"][:2], 1):
        print(f"\n  {i}. {problem['name']} ({problem['difficulty']})")
        print(f"     {problem['description']}")
        print(f"     Test cases: {len(problem['test_cases'])}")


if __name__ == "__main__":
    main()
