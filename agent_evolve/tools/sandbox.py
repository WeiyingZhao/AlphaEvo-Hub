"""
Sandbox Module

Provides safe code execution environment for tools and evolved solutions.
"""

from typing import Any, Dict, Optional
import logging
import sys
import io
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)


class Sandbox:
    """
    Safe code execution sandbox.

    Executes code in an isolated environment to prevent security issues.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize sandbox.

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout

    def execute_code(
        self,
        code: str,
        language: str = "python",
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code safely.

        Args:
            code: Code to execute
            language: Programming language (python, javascript, etc.)
            input_data: Optional input for the code

        Returns:
            Dictionary with:
            - output: stdout output
            - error: stderr output
            - return_code: execution return code
            - success: whether execution succeeded
        """
        if language.lower() == "python":
            return self._execute_python(code, input_data)
        elif language.lower() in ["javascript", "js"]:
            return self._execute_javascript(code, input_data)
        else:
            return {
                "output": "",
                "error": f"Unsupported language: {language}",
                "return_code": 1,
                "success": False
            }

    def _execute_python(self, code: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """Execute Python code with restrictions."""
        # Create a restricted environment
        restricted_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "abs": abs,
                "max": max,
                "min": min,
                "sum": sum,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
            }
        }

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute code
            exec(code, restricted_globals, {})

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            result = {
                "output": stdout_capture.getvalue(),
                "error": stderr_capture.getvalue(),
                "return_code": 0,
                "success": True
            }

        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            result = {
                "output": stdout_capture.getvalue(),
                "error": f"{type(e).__name__}: {str(e)}",
                "return_code": 1,
                "success": False
            }

        logger.debug(f"Python execution completed: success={result['success']}")
        return result

    def _execute_javascript(self, code: str, input_data: Optional[str] = None) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js."""
        try:
            # Write code to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # Execute with node
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Clean up
            os.unlink(temp_file)

            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            return {
                "output": "",
                "error": f"Execution timeout ({self.timeout}s)",
                "return_code": -1,
                "success": False
            }
        except FileNotFoundError:
            return {
                "output": "",
                "error": "Node.js not found. Please install Node.js to execute JavaScript.",
                "return_code": -1,
                "success": False
            }
        except Exception as e:
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.unlink(temp_file)
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "return_code": -1,
                "success": False
            }

    def test_code(self, code: str, test_cases: list) -> Dict[str, Any]:
        """
        Test code against multiple test cases.

        Args:
            code: Code to test
            test_cases: List of (input, expected_output) tuples

        Returns:
            Test results summary
        """
        passed = 0
        failed = 0
        results = []

        for i, (test_input, expected) in enumerate(test_cases):
            # Prepare code with test input
            test_code = f"{code}\n\nprint(main({repr(test_input)}))"

            result = self.execute_code(test_code, language="python")

            actual = result["output"].strip()
            test_passed = actual == str(expected).strip()

            if test_passed:
                passed += 1
            else:
                failed += 1

            results.append({
                "test_case": i + 1,
                "input": test_input,
                "expected": expected,
                "actual": actual,
                "passed": test_passed
            })

        return {
            "total": len(test_cases),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(test_cases) if test_cases else 0.0,
            "results": results
        }

    def __repr__(self) -> str:
        return f"Sandbox(timeout={self.timeout}s)"
