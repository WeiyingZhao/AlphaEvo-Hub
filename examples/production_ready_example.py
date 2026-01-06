"""
Production-Ready Example for Agent Evolve

This example demonstrates all the production improvements:
1. Input validation for evolution parameters
2. Progress bars for long-running evolution
3. Better error messages
4. Optional dependencies handling
5. Mock mode for testing without API costs

Run this to see all improvements in action:
    python examples/production_ready_example.py
"""

import os
from agent_evolve import AgentCore, EvolutionaryOptimizer
from agent_evolve.optimizer.evolutionary import EvolutionConfig
from agent_evolve.evaluator import QAEvaluator


def demo_input_validation():
    """Demonstrate input validation with helpful error messages."""
    print("=" * 70)
    print("Demo 1: Input Validation")
    print("=" * 70)
    print()

    print("Testing invalid configuration...")
    print()

    # Example 1: Invalid generations
    try:
        config = EvolutionConfig(generations=0)
        print("✗ Should have caught invalid generations!")
    except ValueError as e:
        print("✓ Caught invalid generations:")
        print(f"  Error: {e}")
        print()

    # Example 2: Invalid mutation rate
    try:
        config = EvolutionConfig(mutation_rate=1.5)
        print("✗ Should have caught invalid mutation_rate!")
    except ValueError as e:
        print("✓ Caught invalid mutation_rate:")
        print(f"  Error: {e}")
        print()

    # Example 3: Invalid strategy
    try:
        config = EvolutionConfig(strategy="invalid_strategy")
        print("✗ Should have caught invalid strategy!")
    except ValueError as e:
        print("✓ Caught invalid strategy:")
        print(f"  Error: {e}")
        print()

    # Example 4: Valid configuration
    config = EvolutionConfig(
        strategy="prompt_optimization",
        generations=10,
        population_size=5,
        mutation_rate=0.3,
        early_stopping=True
    )
    print("✓ Valid configuration created successfully:")
    print(f"  Strategy: {config.strategy}")
    print(f"  Generations: {config.generations}")
    print(f"  Population: {config.population_size}")
    print()


def demo_progress_bars():
    """Demonstrate evolution with progress bars."""
    print("=" * 70)
    print("Demo 2: Progress Bars During Evolution")
    print("=" * 70)
    print()

    print("Running evolution with progress tracking...")
    print("(Watch the progress bars show real-time status)")
    print()

    # Create agent
    agent = AgentCore(
        model="mock",
        task="Answer questions accurately"
    )

    # Create evaluator
    qa_pairs = [
        {"question": "What is 2+2?", "answer": "4"},
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Who wrote Hamlet?", "answer": "Shakespeare"},
    ]
    evaluator = QAEvaluator(qa_pairs=qa_pairs)

    # Create optimizer with validated config
    config = EvolutionConfig(
        strategy="prompt_optimization",
        generations=5,
        population_size=4,
        mutation_rate=0.3,
        early_stopping=True,
        patience=3
    )
    optimizer = EvolutionaryOptimizer(config=config)

    # Run evolution with progress bars
    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=[qa["question"] for qa in qa_pairs],
        show_progress=True  # Enable progress bars
    )

    print()
    print(f"✓ Evolution completed!")
    print(f"  Best Score: {result.best_score:.4f}")
    print(f"  Generations Run: {result.total_generations}")
    print()


def demo_error_handling():
    """Demonstrate improved error messages."""
    print("=" * 70)
    print("Demo 3: Improved Error Messages")
    print("=" * 70)
    print()

    print("Simulating common user errors with helpful messages...")
    print()

    # Example 1: Missing API key (commented out to avoid actual error)
    print("Example: Missing API Key")
    print("If you try to use OpenAI without setting OPENAI_API_KEY:")
    print("  Error: OpenAI API key not found. Please set the OPENAI_API_KEY")
    print("  environment variable.")
    print("  Get your API key from: https://platform.openai.com/api-keys")
    print()

    # Example 2: Missing optional dependencies
    print("Example: Missing Optional Dependencies")
    print("If you try to use HuggingFace models without torch/transformers:")
    print("  Error: HuggingFace models require torch and transformers packages.")
    print("  Install them with: pip install torch transformers")
    print("  Or: pip install agent-evolve[local]")
    print()

    print("✓ All error messages are now clear and actionable!")
    print()


def demo_minimal_dependencies():
    """Demonstrate working with minimal dependencies."""
    print("=" * 70)
    print("Demo 4: Minimal Dependencies (OpenAI/Anthropic Only)")
    print("=" * 70)
    print()

    print("You can now install Agent Evolve with minimal dependencies:")
    print()
    print("  # Minimal install (no torch/transformers)")
    print("  pip install openai anthropic fastapi uvicorn langchain deap \\")
    print("      numpy scipy faiss-cpu chromadb sentence-transformers \\")
    print("      websockets pydantic sqlalchemy python-dotenv tqdm")
    print()
    print("  # Or use extras:")
    print("  pip install agent-evolve            # Minimal")
    print("  pip install agent-evolve[local]     # + local models")
    print("  pip install agent-evolve[full]      # Everything")
    print()
    print("✓ This reduces install size and avoids large dependencies")
    print("  if you only use OpenAI or Anthropic APIs!")
    print()


def demo_complete_workflow():
    """Demonstrate a complete production workflow."""
    print("=" * 70)
    print("Demo 5: Complete Production Workflow")
    print("=" * 70)
    print()

    print("Step 1: Validate configuration...")
    config = EvolutionConfig(
        strategy="prompt_optimization",
        generations=8,
        population_size=5,
        mutation_rate=0.25,
        crossover_rate=0.75,
        elitism=1,
        early_stopping=True,
        patience=3
    )
    print("✓ Configuration validated")
    print()

    print("Step 2: Create agent (using mock for demo)...")
    agent = AgentCore(
        model="mock",
        task="Solve mathematical problems accurately"
    )
    print("✓ Agent created")
    print()

    print("Step 3: Set up evaluation criteria...")
    qa_pairs = [
        {"question": "What is 10 + 15?", "answer": "25"},
        {"question": "What is 8 * 7?", "answer": "56"},
        {"question": "What is 100 / 4?", "answer": "25"},
        {"question": "What is 12 - 5?", "answer": "7"},
    ]
    evaluator = QAEvaluator(qa_pairs=qa_pairs)
    print("✓ Evaluator configured with 4 test cases")
    print()

    print("Step 4: Run evolution with progress tracking...")
    optimizer = EvolutionaryOptimizer(config=config)
    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=[qa["question"] for qa in qa_pairs],
        show_progress=True
    )
    print()

    print("Step 5: Analyze results...")
    print(f"✓ Best Score: {result.best_score:.4f}")
    print(f"✓ Total Generations: {result.total_generations}")
    print(f"✓ Total Evaluations: {len(result.evolution_history)}")
    print()
    print("  Generation-by-Generation Progress:")
    for i, score in enumerate(result.generation_scores, 1):
        marker = " ⭐" if i > 1 and score > result.generation_scores[i-2] else ""
        print(f"    Gen {i}: {score:.4f}{marker}")
    print()

    print("Step 6: Export results...")
    result.export_report("production_evolution_report.md")
    print("✓ Report saved to: production_evolution_report.md")
    print()

    print("✓ Complete workflow finished successfully!")
    print()


def main():
    """Run all production-ready demos."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Agent Evolve - Production Ready Demo" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("This demo showcases all production improvements:")
    print("  ✓ Input validation with helpful error messages")
    print("  ✓ Progress bars for real-time tracking")
    print("  ✓ Optional dependencies (torch/transformers)")
    print("  ✓ Improved error handling throughout")
    print("  ✓ Mock mode for testing without API costs")
    print()
    input("Press Enter to start the demos...\n")

    # Run all demos
    demo_input_validation()
    input("Press Enter to continue to next demo...\n")

    demo_progress_bars()
    input("Press Enter to continue to next demo...\n")

    demo_error_handling()
    input("Press Enter to continue to next demo...\n")

    demo_minimal_dependencies()
    input("Press Enter to continue to final demo...\n")

    demo_complete_workflow()

    print("=" * 70)
    print("All Demos Complete!")
    print("=" * 70)
    print()
    print("Summary of Production Improvements:")
    print("  ✓ Comprehensive input validation catches errors early")
    print("  ✓ Progress bars show real-time evolution status")
    print("  ✓ Torch/transformers are now optional dependencies")
    print("  ✓ Error messages guide users to solutions")
    print("  ✓ Mock mode enables testing without API costs")
    print()
    print("Next Steps:")
    print("  1. Check out 'getting_started.py' for a quick intro")
    print("  2. See 'production_evolution_report.md' for detailed results")
    print("  3. Ready to use real models? Set your API keys and go!")
    print()
    print("Happy evolving! 🚀")
    print()


if __name__ == "__main__":
    main()
