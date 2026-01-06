"""
Validation Utilities

Provides common input validation functions for the Agent Evolve platform.
Centralized validation improves consistency and reduces code duplication.
"""

from typing import Any, List, Dict, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)


def validate_not_none(value: Any, name: str) -> None:
    """
    Validate that a value is not None.

    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)

    Raises:
        ValueError: If value is None
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")


def validate_positive(value: Union[int, float], name: str, allow_zero: bool = False) -> None:
    """
    Validate that a numeric value is positive.

    Args:
        value: Value to validate
        name: Name of the parameter
        allow_zero: Whether to allow zero

    Raises:
        ValueError: If value is not positive (or not non-negative if allow_zero=True)
    """
    if allow_zero:
        if value < 0:
            raise ValueError(f"{name} must be non-negative, got {value}")
    else:
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")


def validate_range(value: Union[int, float], name: str, min_val: float, max_val: float) -> None:
    """
    Validate that a value is within a range.

    Args:
        value: Value to validate
        name: Name of the parameter
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Raises:
        ValueError: If value is outside the range
    """
    if not min_val <= value <= max_val:
        raise ValueError(
            f"{name} must be between {min_val} and {max_val}, got {value}"
        )


def validate_probability(value: float, name: str) -> None:
    """
    Validate that a value is a valid probability (0.0 to 1.0).

    Args:
        value: Value to validate
        name: Name of the parameter

    Raises:
        ValueError: If value is not in [0.0, 1.0]
    """
    validate_range(value, name, 0.0, 1.0)


def validate_list_not_empty(value: List, name: str) -> None:
    """
    Validate that a list is not empty.

    Args:
        value: List to validate
        name: Name of the parameter

    Raises:
        ValueError: If list is empty
    """
    if not value:
        raise ValueError(f"{name} cannot be empty")


def validate_dict_has_keys(value: Dict, required_keys: List[str], name: str) -> None:
    """
    Validate that a dictionary has required keys.

    Args:
        value: Dictionary to validate
        required_keys: List of required keys
        name: Name of the parameter

    Raises:
        ValueError: If any required key is missing
    """
    missing = [key for key in required_keys if key not in value]
    if missing:
        raise ValueError(
            f"{name} missing required keys: {missing}"
        )


def validate_string_not_empty(value: str, name: str) -> None:
    """
    Validate that a string is not empty or whitespace-only.

    Args:
        value: String to validate
        name: Name of the parameter

    Raises:
        ValueError: If string is empty or whitespace-only
    """
    if not value or not value.strip():
        raise ValueError(f"{name} cannot be empty or whitespace-only")


def validate_choice(value: Any, choices: List[Any], name: str) -> None:
    """
    Validate that a value is one of the allowed choices.

    Args:
        value: Value to validate
        choices: List of allowed values
        name: Name of the parameter

    Raises:
        ValueError: If value is not in choices
    """
    if value not in choices:
        raise ValueError(
            f"{name} must be one of {choices}, got '{value}'"
        )


def validate_file_path_safe(path: str, name: str = "path") -> None:
    """
    Validate that a file path is safe (no directory traversal).

    Args:
        path: Path to validate
        name: Name of the parameter

    Raises:
        ValueError: If path contains dangerous patterns

    Warning:
        This is a basic check. For production, use pathlib.Path().resolve()
        and check if the resolved path is within allowed directories.
    """
    dangerous_patterns = ["../", "..\\", "/etc/", "C:\\Windows"]

    for pattern in dangerous_patterns:
        if pattern in path:
            raise ValueError(
                f"{name} contains potentially dangerous pattern: {pattern}"
            )


def validate_model_name(model_name: str) -> None:
    """
    Validate that a model name is reasonable.

    Args:
        model_name: Model name to validate

    Raises:
        ValueError: If model name is invalid
    """
    validate_string_not_empty(model_name, "model_name")

    # Check length
    if len(model_name) > 200:
        raise ValueError(
            f"model_name is too long ({len(model_name)} chars). "
            "Maximum is 200 characters."
        )

    # Check for suspicious characters
    if any(char in model_name for char in ["\n", "\r", "\0"]):
        raise ValueError(
            "model_name contains invalid characters (newlines, null bytes)"
        )


def validate_messages_format(messages: List[Dict[str, str]]) -> None:
    """
    Validate that messages are in the correct format for LLM APIs.

    Args:
        messages: List of message dictionaries

    Raises:
        ValueError: If messages are malformed
    """
    if not isinstance(messages, list):
        raise ValueError(f"messages must be a list, got {type(messages)}")

    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            raise ValueError(f"messages[{i}] must be a dict, got {type(msg)}")

        if "role" not in msg:
            raise ValueError(f"messages[{i}] missing 'role' key")

        if "content" not in msg:
            raise ValueError(f"messages[{i}] missing 'content' key")

        if not isinstance(msg["content"], str):
            raise ValueError(
                f"messages[{i}]['content'] must be a string, got {type(msg['content'])}"
            )


def sanitize_code_input(code: str, max_length: int = 10000) -> str:
    """
    Sanitize code input for safe execution.

    Args:
        code: Code string to sanitize
        max_length: Maximum allowed code length

    Returns:
        Sanitized code string

    Raises:
        ValueError: If code is too long or contains dangerous patterns

    Warning:
        This does NOT make code execution safe. It only provides basic checks.
        Always use proper sandboxing (Docker, WebAssembly, etc.) for code execution.
    """
    if not code:
        raise ValueError("code cannot be empty")

    if len(code) > max_length:
        raise ValueError(
            f"code is too long ({len(code)} chars). Maximum is {max_length}."
        )

    # Check for dangerous patterns (basic check only)
    dangerous_patterns = [
        "import os",
        "import sys",
        "import subprocess",
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "open(",
        "file(",
    ]

    found_dangerous = []
    for pattern in dangerous_patterns:
        if pattern in code:
            found_dangerous.append(pattern)

    if found_dangerous:
        logger.warning(
            f"Code contains potentially dangerous patterns: {found_dangerous}. "
            "Ensure proper sandboxing is enabled."
        )

    return code


def validate_config_dict(config: Dict[str, Any], required_keys: Optional[List[str]] = None) -> None:
    """
    Validate a configuration dictionary.

    Args:
        config: Configuration dictionary
        required_keys: Optional list of required keys

    Raises:
        ValueError: If config is invalid
    """
    if not isinstance(config, dict):
        raise ValueError(f"config must be a dict, got {type(config)}")

    if required_keys:
        validate_dict_has_keys(config, required_keys, "config")


def validate_qa_pair(qa_pair: Dict[str, str]) -> None:
    """
    Validate a QA pair dictionary.

    Args:
        qa_pair: QA pair to validate

    Raises:
        ValueError: If QA pair is malformed
    """
    if not isinstance(qa_pair, dict):
        raise ValueError(f"qa_pair must be a dict, got {type(qa_pair)}")

    if "question" not in qa_pair:
        raise ValueError("qa_pair missing 'question' key")

    if "answer" not in qa_pair:
        raise ValueError("qa_pair missing 'answer' key")

    if not isinstance(qa_pair["question"], str):
        raise ValueError("qa_pair['question'] must be a string")

    if not isinstance(qa_pair["answer"], str):
        raise ValueError("qa_pair['answer'] must be a string")


# Utility function for logging validation warnings
def log_validation_warning(message: str):
    """Log a validation warning."""
    logger.warning(f"Validation warning: {message}")


# Utility function for logging validation errors
def log_validation_error(message: str):
    """Log a validation error."""
    logger.error(f"Validation error: {message}")
