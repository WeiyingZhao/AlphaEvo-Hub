"""
Code Evaluator

Evaluates agent performance on code generation tasks.
"""

from typing import Any, Dict, List, Optional
import logging

from agent_evolve.evaluator.base import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class CodeEvaluator(BaseEvaluator):
    """
    Evaluator for code generation tasks.

    Scores code based on:
    - Test case pass rate
    - Code quality metrics
    - Execution time/efficiency
    """

    def __init__(
        self,
        test_cases: Optional[List[tuple]] = None,
        timeout: int = 30,
        name: str = "code_evaluator"
    ):
        """
        Initialize code evaluator.

        Args:
            test_cases: List of (input, expected_output) tuples
            timeout: Maximum execution time per test
            name: Evaluator name
        """
        super().__init__(name)
        self.test_cases = test_cases or []
        self.timeout = timeout

        from agent_evolve.tools.sandbox import Sandbox
        self.sandbox = Sandbox(timeout=timeout)

    def evaluate_single(self, agent, task: str) -> EvaluationResult:
        """
        Evaluate agent on a code generation task.

        Args:
            agent: AgentCore instance
            task: Task description (code problem to solve)

        Returns:
            EvaluationResult with pass rate and details
        """
        # Get agent's code solution
        result = agent.run(task)
        code = self._extract_code(result.get("solution", ""))

        if not code:
            return EvaluationResult(
                score=0.0,
                details={"error": "No code generated"},
                success=False
            )

        # Test the code
        test_results = self._run_tests(code)

        # Calculate score
        pass_rate = test_results["pass_rate"]
        score = pass_rate

        # Bonus for efficiency (if applicable)
        if "execution_time" in test_results and test_results["execution_time"] < 1.0:
            score = min(1.0, score * 1.1)  # 10% bonus for fast code

        return EvaluationResult(
            score=score,
            details={
                "code": code,
                "test_results": test_results,
                "passed": test_results["passed"],
                "failed": test_results["failed"]
            },
            success=pass_rate >= 0.8,
            feedback=f"Passed {test_results['passed']}/{test_results['total']} tests"
        )

    def _extract_code(self, solution: str) -> str:
        """Extract code from solution text."""
        import re

        # Try to find code blocks
        code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", solution, re.DOTALL)

        if code_blocks:
            return code_blocks[0].strip()

        # If no code blocks, try to find def statements
        lines = solution.split("\n")
        code_lines = [line for line in lines if line.strip().startswith("def ") or "    " in line or line.strip().startswith("return")]

        if code_lines:
            return "\n".join(code_lines)

        # Return full solution as last resort
        return solution.strip()

    def _run_tests(self, code: str) -> Dict[str, Any]:
        """Run test cases against the code."""
        if not self.test_cases:
            # No test cases, just check if code runs
            result = self.sandbox.execute_code(code, language="python")
            return {
                "passed": 1 if result["success"] else 0,
                "failed": 0 if result["success"] else 1,
                "total": 1,
                "pass_rate": 1.0 if result["success"] else 0.0
            }

        # Run actual test cases
        test_result = self.sandbox.test_code(code, self.test_cases)

        return {
            "passed": test_result["passed"],
            "failed": test_result["failed"],
            "total": test_result["total"],
            "pass_rate": test_result["pass_rate"],
            "details": test_result.get("results", [])
        }

    def add_test_case(self, input_data: Any, expected: Any):
        """Add a test case."""
        self.test_cases.append((input_data, expected))

    def __repr__(self) -> str:
        return f"CodeEvaluator(test_cases={len(self.test_cases)}, timeout={self.timeout}s)"
