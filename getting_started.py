"""
Getting Started with Agent Evolve - No API Keys Required!

This example demonstrates the core functionality of Agent Evolve
using the built-in mock LLM, so you can explore the platform
without needing API keys or credentials.

Run this file to see agent evolution in action:
    python getting_started.py
"""

from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.evaluator import QAEvaluator


def main():
    print("=" * 60)
    print("Welcome to Agent Evolve - Getting Started Demo")
    print("=" * 60)
    print()
    print("This demo uses a mock LLM (no API keys needed!)")
    print("You'll see how agents evolve to improve their performance.")
    print()

    # Step 1: Create an agent
    print("Step 1: Creating an AI agent...")
    agent = AgentCore(
        model="mock",  # No API key needed!
        task="Answer questions accurately and concisely"
    )
    print(f"✓ Agent created: {agent}")
    print()

    # Step 2: Define evaluation criteria
    print("Step 2: Setting up evaluation criteria...")
    qa_pairs = [
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Who wrote Romeo and Juliet?", "answer": "Shakespeare"},
    ]
    evaluator = QAEvaluator(qa_pairs=qa_pairs)
    print(f"✓ Evaluator created with {len(qa_pairs)} test cases")
    print()

    # Step 3: Set up the evolutionary optimizer
    print("Step 3: Configuring evolution strategy...")
    optimizer = EvolutionaryOptimizer(
        strategy="prompt_optimization",  # Evolve the agent's prompts
        generations=5,  # Run for 5 generations
    )
    print("✓ Optimizer configured:")
    print(f"  - Strategy: prompt_optimization")
    print(f"  - Generations: 5")
    print()

    # Step 4: Run evolution!
    print("Step 4: Running evolution...")
    print("-" * 60)

    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=[qa["question"] for qa in qa_pairs]
    )

    print("-" * 60)
    print()

    # Step 5: View results
    print("Step 5: Evolution Results")
    print("=" * 60)
    print(f"Best Score: {result.best_score:.4f}")
    print(f"Total Generations: {result.total_generations}")
    print()
    print("Generation-by-Generation Scores:")
    for i, score in enumerate(result.generation_scores, 1):
        improvement = ""
        if i > 1:
            diff = score - result.generation_scores[i-2]
            improvement = f" ({diff:+.4f})"
        print(f"  Generation {i}: {score:.4f}{improvement}")

    print()
    print(f"Total Improvement: {result.generation_scores[-1] - result.generation_scores[0]:+.4f}")
    print()

    # Step 6: Export results
    print("Step 6: Exporting results...")
    result.export_report("evolution_report.md")
    print("✓ Report saved to: evolution_report.md")
    print()

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("  1. Check out 'evolution_report.md' for detailed results")
    print("  2. See 'examples/basic_usage.py' for more examples")
    print("  3. When ready, replace 'mock' with a real model:")
    print("     - 'gpt-3.5-turbo' for OpenAI")
    print("     - 'claude-3-sonnet-20240229' for Anthropic")
    print()
    print("Happy evolving!")


if __name__ == "__main__":
    main()
