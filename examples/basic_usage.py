"""
Basic Usage Example for Agent Evolve

This example demonstrates how to create an agent and evolve it
to improve performance on a specific task.
"""

import os
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import CodeEvaluator, QAEvaluator

# Set API keys (if using OpenAI or Anthropic)
# os.environ["OPENAI_API_KEY"] = "your-key-here"
# os.environ["ANTHROPIC_API_KEY"] = "your-key-here"


def example_prompt_evolution():
    """Example: Evolving a prompt for better question answering."""
    print("=== Prompt Evolution Example ===\n")

    # Create an agent
    agent = AgentCore(
        model="mock",  # Use "gpt-3.5-turbo" for real usage
        task="Answer questions accurately and concisely"
    )

    # Define Q&A pairs for evaluation
    qa_pairs = [
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare"},
    ]

    # Create evaluator
    evaluator = QAEvaluator(qa_pairs=qa_pairs)

    # Create optimizer
    optimizer = EvolutionaryOptimizer(
        strategy="prompt_optimization",
        generations=5
    )

    # Run evolution
    print("Starting evolution...")
    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=[qa["question"] for qa in qa_pairs]
    )

    print(f"\nEvolution Complete!")
    print(f"Best Score: {result.best_score:.4f}")
    print(f"Total Generations: {result.total_generations}")
    print(f"\nGeneration Scores:")
    for i, score in enumerate(result.generation_scores, 1):
        print(f"  Generation {i}: {score:.4f}")

    # Export results
    result.export_report("evolution_report.md")
    print("\nReport exported to evolution_report.md")


def example_code_evolution():
    """Example: Evolving code solutions."""
    print("\n=== Code Evolution Example ===\n")

    # Create an agent for code generation
    agent = AgentCore(
        model="mock",
        task="Write efficient Python code"
    )

    # Define test cases
    test_cases = [
        ([1, 2, 3], 6),  # sum([1,2,3]) = 6
        ([10, 20], 30),  # sum([10,20]) = 30
        ([], 0),         # sum([]) = 0
    ]

    # Create code evaluator
    evaluator = CodeEvaluator(test_cases=test_cases)

    # Create optimizer for code evolution
    optimizer = EvolutionaryOptimizer(
        strategy="code_evolution",
        generations=5
    )

    # Run evolution
    print("Starting code evolution...")
    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=["Write a function to sum a list of numbers"]
    )

    print(f"\nEvolution Complete!")
    print(f"Best Score: {result.best_score:.4f}")

    # Export best code
    if "code" in result.best_agent_config:
        result.export_code("best_solution.py")
        print("\nBest solution exported to best_solution.py")


def example_multi_strategy():
    """Example: Using multiple evolution strategies."""
    print("\n=== Multi-Strategy Example ===\n")

    agent = AgentCore(
        model="mock",
        task="Solve problems efficiently"
    )

    evaluator = QAEvaluator(qa_pairs=[
        {"question": "What is 10 * 5?", "answer": "50"},
        {"question": "What is 100 / 4?", "answer": "25"},
    ])

    # Try different strategies
    strategies = ["prompt_optimization", "memory_evolution", "tool_evolution"]

    for strategy in strategies:
        print(f"\nTesting strategy: {strategy}")

        optimizer = EvolutionaryOptimizer(
            strategy=strategy,
            generations=3
        )

        result = optimizer.evolve(agent, evaluator, ["What is 10 * 5?"])

        print(f"  Best Score: {result.best_score:.4f}")


def example_with_custom_tasks():
    """Example: Evolution with custom task generation."""
    print("\n=== Custom Tasks Example ===\n")

    agent = AgentCore(
        model="mock",
        task="Mathematical reasoning"
    )

    # Custom tasks
    tasks = [
        "Calculate 15 + 27",
        "What is 8 squared?",
        "Find the average of 10, 20, and 30"
    ]

    evaluator = QAEvaluator()

    optimizer = EvolutionaryOptimizer(
        strategy="prompt_optimization",
        generations=5
    )

    result = optimizer.evolve(agent, evaluator, tasks)

    print(f"Best Score: {result.best_score:.4f}")
    print(f"Evolved through {result.total_generations} generations")


if __name__ == "__main__":
    print("Agent Evolve - Basic Usage Examples\n")
    print("=" * 50)

    # Run examples
    # Note: Using mock LLM for demonstration
    # Replace with real models for actual usage

    example_prompt_evolution()

    # Uncomment to run other examples:
    # example_code_evolution()
    # example_multi_strategy()
    # example_with_custom_tasks()

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo use with real LLMs, set your API keys and change model to:")
    print("  - 'gpt-3.5-turbo' or 'gpt-4' for OpenAI")
    print("  - 'claude-3-sonnet-20240229' for Anthropic")
