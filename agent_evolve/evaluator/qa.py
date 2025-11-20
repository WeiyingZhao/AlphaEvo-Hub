"""
QA Evaluator

Evaluates agent performance on question-answering tasks.
"""

from typing import Any, Dict, List, Optional
import logging

from agent_evolve.evaluator.base import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class QAEvaluator(BaseEvaluator):
    """
    Evaluator for question-answering tasks.

    Scores answers based on:
    - Accuracy (compared to reference answer)
    - Completeness
    - Relevance
    """

    def __init__(
        self,
        qa_pairs: Optional[List[Dict[str, str]]] = None,
        use_llm_judge: bool = False,
        name: str = "qa_evaluator"
    ):
        """
        Initialize QA evaluator.

        Args:
            qa_pairs: List of {"question": ..., "answer": ...} dictionaries
            use_llm_judge: Whether to use LLM for judging
            name: Evaluator name
        """
        super().__init__(name)
        self.qa_pairs = qa_pairs or []
        self.use_llm_judge = use_llm_judge

        if use_llm_judge:
            from agent_evolve.evaluator.base import JudgeLLMEvaluator
            self.judge = JudgeLLMEvaluator()

    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        """
        Evaluate agent on a QA task.

        Args:
            agent: AgentCore instance
            task: Question to answer

        Returns:
            EvaluationResult with accuracy score
        """
        # Get agent's answer
        result = agent.run(task)
        answer = result.get("solution", "")

        # Find reference answer if available
        reference = self._find_reference_answer(task)

        if reference and not self.use_llm_judge:
            # Use exact/fuzzy matching
            score = self._compute_similarity(answer, reference)
        elif self.use_llm_judge:
            # Use LLM judge
            judge_result = self.judge.evaluate_single(agent, task)
            score = judge_result.score
        else:
            # No reference, assume moderate score
            score = 0.5

        return EvaluationResult(
            score=score,
            details={
                "answer": answer,
                "reference": reference
            },
            success=score >= 0.6
        )

    def _find_reference_answer(self, question: str) -> Optional[str]:
        """Find reference answer for a question."""
        for qa in self.qa_pairs:
            if qa["question"].strip().lower() == question.strip().lower():
                return qa["answer"]

        # Try partial match
        for qa in self.qa_pairs:
            if question.strip().lower() in qa["question"].strip().lower():
                return qa["answer"]

        return None

    def _compute_similarity(self, answer: str, reference: str) -> float:
        """Compute similarity between answer and reference."""
        # Simple word overlap-based similarity
        answer_words = set(answer.lower().split())
        ref_words = set(reference.lower().split())

        if not ref_words:
            return 0.0

        overlap = len(answer_words & ref_words)
        similarity = overlap / len(ref_words)

        return min(1.0, similarity)

    def add_qa_pair(self, question: str, answer: str):
        """Add a QA pair."""
        self.qa_pairs.append({
            "question": question,
            "answer": answer
        })

    def __repr__(self) -> str:
        return f"QAEvaluator(qa_pairs={len(self.qa_pairs)}, llm_judge={self.use_llm_judge})"
