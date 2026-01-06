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

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    logger.warning("tqdm not available. Install with 'pip install tqdm' for progress bars.")


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

    def __post_init__(self):
        """Validate configuration parameters."""
        # Validate generations
        if self.generations < 1:
            raise ValueError(
                f"generations must be at least 1, got {self.generations}. "
                "Set to a positive integer (e.g., 10 for quick tests, 50+ for serious evolution)."
            )
        if self.generations > 1000:
            logger.warning(
                f"generations={self.generations} is very high. "
                "Consider using early_stopping=True to avoid long run times."
            )

        # Validate population_size
        if self.population_size < 1:
            raise ValueError(
                f"population_size must be at least 1, got {self.population_size}. "
                "Typical values: 5-20 for most use cases."
            )
        if self.population_size > 100:
            logger.warning(
                f"population_size={self.population_size} is very large. "
                "This may slow down evolution significantly."
            )

        # Validate mutation_rate
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError(
                f"mutation_rate must be between 0.0 and 1.0, got {self.mutation_rate}. "
                "0.0 = no mutation, 1.0 = always mutate. Typical: 0.1-0.5"
            )

        # Validate crossover_rate
        if not 0.0 <= self.crossover_rate <= 1.0:
            raise ValueError(
                f"crossover_rate must be between 0.0 and 1.0, got {self.crossover_rate}. "
                "0.0 = no crossover, 1.0 = always crossover. Typical: 0.5-0.9"
            )

        # Validate elitism
        if self.elitism < 0:
            raise ValueError(
                f"elitism must be non-negative, got {self.elitism}. "
                "Set to 0 for no elitism, or 1-2 to preserve best individuals."
            )
        if self.elitism >= self.population_size:
            raise ValueError(
                f"elitism ({self.elitism}) must be less than population_size ({self.population_size}). "
                "Typically elitism should be 1-2 individuals."
            )

        # Validate patience
        if self.patience < 1:
            raise ValueError(
                f"patience must be at least 1, got {self.patience}. "
                "This is the number of generations without improvement before early stopping."
            )

        # Validate strategy
        valid_strategies = [
            "prompt_optimization", "memory_evolution",
            "tool_evolution", "code_evolution"
        ]
        if self.strategy not in valid_strategies:
            raise ValueError(
                f"Unknown strategy: {self.strategy}. "
                f"Valid strategies are: {', '.join(valid_strategies)}"
            )


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
        initial_tasks: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> EvolutionResult:
        """
        Run the evolution loop.

        Args:
            agent: AgentCore instance to evolve
            evaluator: Evaluator for scoring agent performance
            initial_tasks: Initial set of tasks for evaluation
            show_progress: Whether to show progress bars (default: True)

        Returns:
            EvolutionResult with best configuration and history
        """
        logger.info(f"Starting evolution with strategy: {self.config.strategy}")
        logger.info(f"Generations: {self.config.generations}, Population: {self.config.population_size}")

        # Initialize population
        population = self._initialize_population(agent)

        # Track generations without improvement
        generations_without_improvement = 0

        # Create progress bar for generations
        use_progress = show_progress and TQDM_AVAILABLE
        generation_pbar = tqdm(
            range(self.config.generations),
            desc="Evolution Progress",
            disable=not use_progress,
            unit="gen"
        )

        for generation in generation_pbar:
            if not use_progress:
                logger.info(f"\n=== Generation {generation + 1}/{self.config.generations} ===")

            # Evaluate population with progress bar
            scores = []
            population_pbar = tqdm(
                population,
                desc=f"Gen {generation + 1} Evaluation",
                disable=not use_progress,
                leave=False,
                unit="ind"
            )

            for individual in population_pbar:
                score = self._evaluate_individual(individual, evaluator, initial_tasks)
                scores.append(score)

                # Record in history
                self.evolution_history.append({
                    "generation": generation + 1,
                    "config": individual,
                    "score": score
                })

                # Update inner progress bar with current score
                if use_progress:
                    population_pbar.set_postfix({"score": f"{score:.4f}"})

            # Track best score this generation
            gen_best_score = max(scores)
            self.generation_scores.append(gen_best_score)

            # Update global best
            improvement = ""
            if gen_best_score > self.best_score:
                self.best_score = gen_best_score
                best_idx = scores.index(gen_best_score)
                self.best_config = copy.deepcopy(population[best_idx])
                generations_without_improvement = 0
                improvement = " (NEW BEST!)"
                if not use_progress:
                    logger.info(f"New best score: {self.best_score:.4f}")
            else:
                generations_without_improvement += 1

            # Update generation progress bar
            if use_progress:
                generation_pbar.set_postfix({
                    "best": f"{self.best_score:.4f}",
                    "current": f"{gen_best_score:.4f}",
                    "no_improve": generations_without_improvement
                })
            else:
                logger.info(f"Generation {generation + 1} best score: {gen_best_score:.4f}{improvement}")

            # Early stopping
            if self.config.early_stopping and generations_without_improvement >= self.config.patience:
                if use_progress:
                    generation_pbar.set_description("Early stopping")
                    generation_pbar.close()
                logger.info(f"Early stopping: no improvement for {self.config.patience} generations")
                break

            # Generate next generation
            if generation < self.config.generations - 1:
                population = self._generate_next_generation(population, scores)

        if use_progress:
            generation_pbar.close()

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

        # Create agent with this configuration (skip init, will be done in load_config)
        temp_agent = AgentCore(_skip_init=True)
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
