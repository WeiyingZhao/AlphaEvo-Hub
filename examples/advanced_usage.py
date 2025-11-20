"""
Advanced Usage Examples for Agent Evolve

Demonstrates advanced features like:
- Memory evolution
- Tool creation
- Multi-agent co-evolution
- Custom evaluators
"""

from agent_evolve import AgentCore, EvolutionaryOptimizer, MemoryManager
from agent_evolve.evaluator.base import BaseEvaluator, EvaluationResult
from agent_evolve.tools import ToolManager


class CustomDomainEvaluator(BaseEvaluator):
    """Example of a custom evaluator for a specific domain."""

    def __init__(self, domain_requirements):
        super().__init__(name="custom_domain")
        self.requirements = domain_requirements

    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        """Custom evaluation logic."""
        result = agent.run(task)
        output = result.get("solution", "")

        # Custom scoring based on domain requirements
        score = 0.0

        for req in self.requirements:
            if req.lower() in output.lower():
                score += 1.0 / len(self.requirements)

        return EvaluationResult(
            score=score,
            details={"output": output, "requirements_met": score * len(self.requirements)},
            success=score > 0.7
        )


def example_memory_evolution():
    """Example: Evolving memory management strategies."""
    print("=== Memory Evolution Example ===\n")

    # Create agent with memory
    agent = AgentCore(model="mock", task="Remember important information")

    # Add some memories
    memory_manager = MemoryManager()
    memory_manager.add_memory("User prefers concise answers", importance=0.8)
    memory_manager.add_memory("Technical domain is machine learning", importance=0.9)
    memory_manager.add_memory("Random fact", importance=0.2)

    # Create optimizer for memory evolution
    optimizer = EvolutionaryOptimizer(
        strategy="memory_evolution",
        generations=5
    )

    # Custom evaluator that checks if agent uses relevant memories
    evaluator = CustomDomainEvaluator(["concise", "machine learning"])

    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=["Explain neural networks"]
    )

    print(f"Best Score: {result.best_score:.4f}")
    print(f"Memory configuration evolved through {result.total_generations} generations")


def example_tool_evolution():
    """Example: Agent learns to create and use custom tools."""
    print("\n=== Tool Evolution Example ===\n")

    agent = AgentCore(model="mock", task="Solve problems with appropriate tools")

    # Start with basic tools
    tool_manager = ToolManager()

    # Create optimizer for tool evolution
    optimizer = EvolutionaryOptimizer(
        strategy="tool_evolution",
        generations=5
    )

    # Tasks that might benefit from specialized tools
    tasks = [
        "Calculate compound interest",
        "Convert temperature from Celsius to Fahrenheit",
        "Find prime numbers up to 100"
    ]

    evaluator = CustomDomainEvaluator(["calculate", "convert", "find"])

    result = optimizer.evolve(agent, evaluator, tasks)

    print(f"Best Score: {result.best_score:.4f}")
    print("Agent evolved tool usage capabilities")


def example_custom_evolution_config():
    """Example: Advanced evolution configuration."""
    print("\n=== Custom Evolution Configuration ===\n")

    from agent_evolve.optimizer.evolutionary import EvolutionConfig

    # Custom evolution configuration
    config = EvolutionConfig(
        strategy="prompt_optimization",
        generations=15,
        population_size=10,
        mutation_rate=0.4,
        crossover_rate=0.8,
        elitism=2,
        early_stopping=True,
        patience=5
    )

    agent = AgentCore(model="mock")

    optimizer = EvolutionaryOptimizer(config=config)

    evaluator = CustomDomainEvaluator(["accurate", "detailed"])

    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=["Explain quantum computing"]
    )

    print(f"Evolution with custom config:")
    print(f"  Population Size: {config.population_size}")
    print(f"  Mutation Rate: {config.mutation_rate}")
    print(f"  Best Score: {result.best_score:.4f}")


def example_evolution_analysis():
    """Example: Analyzing evolution history."""
    print("\n=== Evolution Analysis Example ===\n")

    agent = AgentCore(model="mock")
    evaluator = CustomDomainEvaluator(["clear", "accurate"])

    optimizer = EvolutionaryOptimizer(
        strategy="prompt_optimization",
        generations=5
    )

    result = optimizer.evolve(
        agent=agent,
        evaluator=evaluator,
        initial_tasks=["Explain photosynthesis"]
    )

    # Analyze evolution history
    print("Evolution History Analysis:")
    print(f"  Total Evaluations: {len(result.evolution_history)}")

    # Find best generation
    best_gen = result.generation_scores.index(max(result.generation_scores)) + 1
    print(f"  Best Generation: {best_gen}")
    print(f"  Best Score: {max(result.generation_scores):.4f}")

    # Calculate improvement
    improvement = result.generation_scores[-1] - result.generation_scores[0]
    print(f"  Total Improvement: {improvement:.4f}")

    # Export detailed report
    result.export_report("detailed_evolution_report.md")
    print("\nDetailed report saved to detailed_evolution_report.md")


def example_parallel_evolution():
    """Example: Running multiple evolution strategies in parallel."""
    print("\n=== Parallel Evolution Example ===\n")

    import concurrent.futures

    strategies = ["prompt_optimization", "memory_evolution", "tool_evolution"]
    results = {}

    def run_evolution(strategy):
        agent = AgentCore(model="mock")
        evaluator = CustomDomainEvaluator(["effective", "efficient"])
        optimizer = EvolutionaryOptimizer(strategy=strategy, generations=3)

        result = optimizer.evolve(
            agent=agent,
            evaluator=evaluator,
            initial_tasks=["Optimize this process"]
        )

        return strategy, result

    print("Running multiple strategies in parallel...")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_evolution, s) for s in strategies]

        for future in concurrent.futures.as_completed(futures):
            strategy, result = future.result()
            results[strategy] = result
            print(f"  {strategy}: {result.best_score:.4f}")

    # Find best strategy
    best_strategy = max(results.keys(), key=lambda s: results[s].best_score)
    print(f"\nBest Strategy: {best_strategy}")
    print(f"Score: {results[best_strategy].best_score:.4f}")


if __name__ == "__main__":
    print("Agent Evolve - Advanced Usage Examples\n")
    print("=" * 50)

    # Run examples
    example_memory_evolution()
    example_tool_evolution()
    example_custom_evolution_config()
    example_evolution_analysis()

    # Parallel execution (commented out as it may take longer)
    # example_parallel_evolution()

    print("\n" + "=" * 50)
    print("Advanced examples completed!")
