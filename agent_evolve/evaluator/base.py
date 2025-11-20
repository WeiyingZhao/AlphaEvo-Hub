"""
Base Evaluator Module

Provides abstract base class and common evaluation utilities.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result from an evaluation."""

    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    success: bool
    feedback: str = ""


class BaseEvaluator(ABC):
    """
    Base class for all evaluators.

    Evaluators score agent performance on tasks, providing
    the fitness signal for evolution.
    """

    def __init__(self, name: str = "base_evaluator"):
        self.name = name
        self.evaluation_count = 0

    @abstractmethod
    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        """
        Evaluate agent on a single task.

        Args:
            agent: AgentCore instance
            task: Task to evaluate on

        Returns:
            EvaluationResult with score and details
        """
        pass

    def evaluate(
        self,
        agent,
        tasks: List[str],
        aggregate: str = "mean"
    ) -> float:
        """
        Evaluate agent on multiple tasks.

        Args:
            agent: AgentCore instance
            tasks: List of tasks to evaluate on
            aggregate: How to aggregate scores ('mean', 'min', 'max', 'weighted')

        Returns:
            Aggregated score (0.0 to 1.0)
        """
        self.evaluation_count += 1

        if not tasks:
            logger.warning("No tasks provided for evaluation")
            return 0.0

        results = []
        for task in tasks:
            try:
                result = self.evaluate_single(agent, task)
                results.append(result)
                logger.debug(f"Task '{task[:50]}...' score: {result.score:.4f}")
            except Exception as e:
                logger.error(f"Evaluation error on task '{task[:50]}...': {e}")
                results.append(EvaluationResult(
                    score=0.0,
                    details={"error": str(e)},
                    success=False
                ))

        # Aggregate scores
        scores = [r.score for r in results]

        if aggregate == "mean":
            final_score = sum(scores) / len(scores)
        elif aggregate == "min":
            final_score = min(scores)
        elif aggregate == "max":
            final_score = max(scores)
        elif aggregate == "weighted":
            # Weight by success
            successes = [r.success for r in results]
            final_score = sum(s * (1 if succ else 0.5) for s, succ in zip(scores, successes)) / len(scores)
        else:
            final_score = sum(scores) / len(scores)

        logger.info(f"Evaluation {self.evaluation_count}: score={final_score:.4f} on {len(tasks)} tasks")

        return final_score

    def get_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics."""
        return {
            "name": self.name,
            "evaluation_count": self.evaluation_count
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, evaluations={self.evaluation_count})"


class MetricEvaluator(BaseEvaluator):
    """
    Generic evaluator using custom metric functions.
    """

    def __init__(
        self,
        metric_fn: callable,
        name: str = "metric_evaluator"
    ):
        """
        Initialize with a metric function.

        Args:
            metric_fn: Function that takes (output, expected) and returns score 0-1
            name: Evaluator name
        """
        super().__init__(name)
        self.metric_fn = metric_fn

    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        """Evaluate using the metric function."""
        # Run task
        result = agent.run(task)
        output = result.get("solution", "")

        # For now, assume task contains expected answer
        # In practice, tasks would be more structured
        score = self.metric_fn(output, task)

        return EvaluationResult(
            score=score,
            details={"output": output},
            success=score > 0.5
        )


class JudgeLLMEvaluator(BaseEvaluator):
    """
    Evaluator that uses an LLM as a judge.

    This implements the judge agent pattern for evaluation.
    """

    def __init__(
        self,
        judge_model: str = "gpt-4",
        name: str = "judge_llm"
    ):
        """
        Initialize with a judge LLM.

        Args:
            judge_model: Model to use for judging
            name: Evaluator name
        """
        super().__init__(name)
        self.judge_model = judge_model
        self._initialize_judge()

    def _initialize_judge(self):
        """Initialize the judge LLM."""
        from agent_evolve.core.llm import get_llm
        self.judge_llm = get_llm(
            provider="openai",
            model_name=self.judge_model,
            temperature=0.0  # Deterministic for evaluation
        )

    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        """Evaluate using LLM judge."""
        # Run task
        result = agent.run(task)
        output = result.get("solution", "")

        # Ask judge to rate
        judge_prompt = f"""
Task: {task}

Agent's response:
{output}

Please rate this response on a scale of 0.0 to 1.0 based on:
- Correctness
- Completeness
- Clarity

Provide only the numeric score (e.g., 0.85).
"""

        try:
            judge_response = self.judge_llm.generate([
                {"role": "user", "content": judge_prompt}
            ])

            # Extract score
            score = self._extract_score(judge_response)

            return EvaluationResult(
                score=score,
                details={"output": output, "judge_response": judge_response},
                success=score > 0.5,
                feedback=judge_response
            )

        except Exception as e:
            logger.error(f"Judge evaluation error: {e}")
            return EvaluationResult(
                score=0.0,
                details={"error": str(e)},
                success=False
            )

    def _extract_score(self, judge_response: str) -> float:
        """Extract numeric score from judge response."""
        import re

        # Try to find a number between 0 and 1
        matches = re.findall(r"0?\.\d+|1\.0|0", judge_response)
        if matches:
            try:
                score = float(matches[0])
                return max(0.0, min(1.0, score))
            except ValueError:
                pass

        # Default if can't parse
        logger.warning("Could not parse judge score, using 0.5")
        return 0.5
