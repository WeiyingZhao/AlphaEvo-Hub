"""
Evolutionary Optimizer Module

Orchestrates the self-improvement loop using various evolution strategies.
Implements genetic algorithms, reinforcement learning, and other search methods.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import logging
import random
import copy
import json

logger = logging.getLogger(__name__)


@dataclass
class EvolutionConfig:
    """Configuration for evolutionary optimization."""

    strategy: str = "prompt_optimization"  # Evolution strategy to use
    generations: int = 10  # Number of evolution generations
    population_size: int = 5  # Population size for population-based methods
    mutation_rate: float = 0.3  # Mutation probability
    crossover_rate: float = 0.7  # Crossover probability
    elitism: int = 1  # Number of elite individuals to preserve
    parallel_trials: bool = False  # Run trials in parallel
    early_stopping: bool = True  # Stop if no improvement
    patience: int = 3  # Generations without improvement before stopping
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionResult:
    """Results from evolution run."""

    best_agent_config: Dict[str, Any]
    best_score: float
    generation_scores: List[float]
    total_generations: int
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def export_code(self, filepath: str):
        """Export evolved solution as code."""
        with open(filepath, 'w') as f:
            if "code" in self.best_agent_config:
                f.write(self.best_agent_config["code"])
            else:
                f.write(f"# Evolved agent configuration\n{json.dumps(self.best_agent_config, indent=2)}")
        logger.info(f"Exported code to {filepath}")

    def export_report(self, filepath: str):
        """Export evolution report."""
        report = f"""# Evolution Report

## Summary
- Best Score: {self.best_score:.4f}
- Total Generations: {self.total_generations}
- Final Improvement: {self.generation_scores[-1] - self.generation_scores[0]:.4f}

## Generation Scores
{chr(10).join(f"Generation {i+1}: {score:.4f}" for i, score in enumerate(self.generation_scores))}

## Best Configuration
```json
{json.dumps(self.best_agent_config, indent=2)}
```

## Evolution History
Total evaluations: {len(self.evolution_history)}
"""
        with open(filepath, 'w') as f:
            f.write(report)
        logger.info(f"Exported report to {filepath}")


class EvolutionaryOptimizer:
    """
    Evolutionary Optimizer for agent self-improvement.

    Implements various evolution strategies:
    - Prompt optimization (iterative refinement)
    - Memory evolution (optimize what to remember)
    - Tool evolution (create and refine tools)
    - Policy evolution (RL-based updates)
    - Multi-agent co-evolution

    The optimizer runs the evolution loop, generates variants,
    evaluates them, and selects the best performers.
    """

    def __init__(
        self,
        strategy: str = "prompt_optimization",
        generations: int = 10,
        config: Optional[EvolutionConfig] = None
    ):
        """
        Initialize evolutionary optimizer.

        Args:
            strategy: Evolution strategy name
            generations: Number of generations to run
            config: Full evolution configuration
        """
        if config is None:
            config = EvolutionConfig(strategy=strategy, generations=generations)

        self.config = config
        self.evolution_history = []
        self.best_score = float('-inf')
        self.best_config = None
        self.generation_scores = []

        # Initialize strategy
        self.strategy = self._get_strategy(config.strategy)

    def _get_strategy(self, strategy_name: str):
        """Get evolution strategy by name."""
        from agent_evolve.optimizer.strategies import (
            PromptEvolutionStrategy,
            MemoryEvolutionStrategy,
            ToolEvolutionStrategy,
            CodeEvolutionStrategy
        )

        strategies = {
            "prompt_optimization": PromptEvolutionStrategy(),
            "memory_evolution": MemoryEvolutionStrategy(),
            "tool_evolution": ToolEvolutionStrategy(),
            "code_evolution": CodeEvolutionStrategy(),
        }

        if strategy_name not in strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return strategies[strategy_name]

    def evolve(
        self,
        agent,
        evaluator,
        initial_tasks: Optional[List[str]] = None
    ) -> EvolutionResult:
        """
        Run the evolution loop.

        Args:
            agent: AgentCore instance to evolve
            evaluator: Evaluator for scoring agent performance
            initial_tasks: Initial set of tasks for evaluation

        Returns:
            EvolutionResult with best configuration and history
        """
        logger.info(f"Starting evolution with strategy: {self.config.strategy}")
        logger.info(f"Generations: {self.config.generations}, Population: {self.config.population_size}")

        # Initialize population
        population = self._initialize_population(agent)

        # Track generations without improvement
        generations_without_improvement = 0

        for generation in range(self.config.generations):
            logger.info(f"\n=== Generation {generation + 1}/{self.config.generations} ===")

            # Evaluate population
            scores = []
            for individual in population:
                score = self._evaluate_individual(individual, evaluator, initial_tasks)
                scores.append(score)

                # Record in history
                self.evolution_history.append({
                    "generation": generation + 1,
                    "config": individual,
                    "score": score
                })

            # Track best score this generation
            gen_best_score = max(scores)
            self.generation_scores.append(gen_best_score)

            logger.info(f"Generation {generation + 1} best score: {gen_best_score:.4f}")

            # Update global best
            if gen_best_score > self.best_score:
                self.best_score = gen_best_score
                best_idx = scores.index(gen_best_score)
                self.best_config = copy.deepcopy(population[best_idx])
                generations_without_improvement = 0
                logger.info(f"New best score: {self.best_score:.4f}")
            else:
                generations_without_improvement += 1

            # Early stopping
            if self.config.early_stopping and generations_without_improvement >= self.config.patience:
                logger.info(f"Early stopping: no improvement for {self.config.patience} generations")
                break

            # Generate next generation
            if generation < self.config.generations - 1:
                population = self._generate_next_generation(population, scores)

        # Create result
        result = EvolutionResult(
            best_agent_config=self.best_config,
            best_score=self.best_score,
            generation_scores=self.generation_scores,
            total_generations=len(self.generation_scores),
            evolution_history=self.evolution_history,
            metadata={
                "strategy": self.config.strategy,
                "population_size": self.config.population_size
            }
        )

        logger.info(f"\nEvolution complete! Best score: {self.best_score:.4f}")

        return result

    def _initialize_population(self, agent) -> List[Dict[str, Any]]:
        """Initialize the population of agent configurations."""
        population = []

        # Add original agent as first individual
        population.append(agent.export_config())

        # Generate variants using strategy
        for i in range(self.config.population_size - 1):
            variant = self.strategy.generate_variant(agent.export_config())
            population.append(variant)

        logger.debug(f"Initialized population of size {len(population)}")
        return population

    def _evaluate_individual(
        self,
        individual_config: Dict[str, Any],
        evaluator,
        tasks: Optional[List[str]] = None
    ) -> float:
        """Evaluate a single individual configuration."""
        from agent_evolve.core.agent import AgentCore

        # Create agent with this configuration
        temp_agent = AgentCore()
        temp_agent.load_config(individual_config)

        # Evaluate on tasks
        if tasks is None:
            # Generate tasks using self-questioning
            tasks = self._generate_tasks(temp_agent)

        score = evaluator.evaluate(temp_agent, tasks)

        return score

    def _generate_tasks(self, agent) -> List[str]:
        """Generate tasks for evaluation (self-questioning)."""
        # Simple implementation - in practice, this would be more sophisticated
        return ["Solve a coding problem", "Answer a question", "Analyze data"]

    def _generate_next_generation(
        self,
        population: List[Dict[str, Any]],
        scores: List[float]
    ) -> List[Dict[str, Any]]:
        """Generate next generation using selection, crossover, and mutation."""
        next_generation = []

        # Elitism: keep best individuals
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        for i in range(self.config.elitism):
            next_generation.append(copy.deepcopy(population[sorted_indices[i]]))

        # Generate rest through selection, crossover, and mutation
        while len(next_generation) < self.config.population_size:
            # Selection (tournament)
            parent1 = self._tournament_selection(population, scores)
            parent2 = self._tournament_selection(population, scores)

            # Crossover
            if random.random() < self.config.crossover_rate:
                child = self.strategy.crossover(parent1, parent2)
            else:
                child = copy.deepcopy(parent1)

            # Mutation
            if random.random() < self.config.mutation_rate:
                child = self.strategy.mutate(child)

            next_generation.append(child)

        return next_generation

    def _tournament_selection(
        self,
        population: List[Dict[str, Any]],
        scores: List[float],
        tournament_size: int = 3
    ) -> Dict[str, Any]:
        """Select an individual using tournament selection."""
        indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        best_idx = max(indices, key=lambda i: scores[i])
        return copy.deepcopy(population[best_idx])

    def get_history(self) -> List[Dict[str, Any]]:
        """Get evolution history."""
        return self.evolution_history

    def get_best_config(self) -> Dict[str, Any]:
        """Get best configuration found."""
        return self.best_config

    def __repr__(self) -> str:
        return (
            f"EvolutionaryOptimizer(strategy={self.config.strategy}, "
            f"generations={self.config.generations}, "
            f"best_score={self.best_score:.4f})"
        )
