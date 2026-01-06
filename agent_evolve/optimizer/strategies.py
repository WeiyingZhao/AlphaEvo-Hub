"""
Evolution Strategies

Implements specific evolution methods for different aspects of agent intelligence:
- Prompt optimization
- Memory evolution
- Tool evolution
- Code evolution

Supports LLM-based evolution for intelligent mutations when an LLM instance is provided,
with fallback to simple heuristic-based mutations otherwise.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
import logging
import random
import copy

if TYPE_CHECKING:
    from agent_evolve.core.llm import BaseLLM

logger = logging.getLogger(__name__)


class EvolutionStrategy(ABC):
    """
    Base class for evolution strategies.

    Supports optional LLM integration for intelligent mutations.
    When an LLM is provided, strategies can use it for more sophisticated
    evolutionary operations instead of simple heuristics.
    """

    def __init__(self, llm: Optional["BaseLLM"] = None):
        """
        Initialize evolution strategy.

        Args:
            llm: Optional LLM instance for intelligent mutations.
                 If not provided, falls back to heuristic-based mutations.
        """
        self.llm = llm

    @abstractmethod
    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a variant of the given configuration."""
        pass

    @abstractmethod
    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mutation to a configuration."""
        pass

    def crossover(
        self,
        config1: Dict[str, Any],
        config2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform crossover between two configurations.

        Default implementation: random selection from parents.
        """
        child = copy.deepcopy(config1)

        # Mix configurations
        for key in config1.get("config", {}):
            if key in config2.get("config", {}) and random.random() < 0.5:
                child["config"][key] = config2["config"][key]

        return child

    def _llm_generate(self, prompt: str, fallback: str) -> str:
        """
        Generate text using LLM with fallback.

        Args:
            prompt: The prompt to send to the LLM
            fallback: Value to return if LLM is unavailable or fails

        Returns:
            LLM response or fallback value
        """
        if self.llm is None:
            return fallback

        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.generate(messages)
            return response.strip() if response else fallback
        except Exception as e:
            logger.warning(f"LLM generation failed, using fallback: {e}")
            return fallback


class PromptEvolutionStrategy(EvolutionStrategy):
    """
    Prompt Evolution Strategy

    Evolves the agent's system prompt to improve performance.
    Uses techniques like:
    - Adding/removing instructions
    - Rephrasing for clarity (LLM-based when available)
    - Adding examples

    When an LLM is provided, uses intelligent rephrasing instead of
    simple string replacements.
    """

    def __init__(self, llm: Optional["BaseLLM"] = None):
        super().__init__(llm=llm)

        self.prompt_templates = [
            "You are an AI assistant that {objective}. {instructions}",
            "Your task is to {objective}. Follow these guidelines: {instructions}",
            "As an expert AI, {objective}. {instructions}",
        ]

        self.instruction_modifiers = [
            "Think step by step.",
            "Provide detailed explanations.",
            "Be concise and accurate.",
            "Consider multiple approaches.",
            "Verify your reasoning.",
        ]

    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a prompt variant."""
        variant = copy.deepcopy(config)

        current_prompt = variant.get("config", {}).get("system_prompt", "")

        if not current_prompt:
            # Generate initial prompt
            template = random.choice(self.prompt_templates)
            modifier = random.choice(self.instruction_modifiers)
            new_prompt = template.format(
                objective="solve problems effectively",
                instructions=modifier
            )
        else:
            # Modify existing prompt
            new_prompt = self._modify_prompt(current_prompt)

        variant["config"]["system_prompt"] = new_prompt
        logger.debug(f"Generated prompt variant: {new_prompt[:100]}...")

        return variant

    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate prompt by adding/removing instructions."""
        mutated = copy.deepcopy(config)

        current_prompt = mutated.get("config", {}).get("system_prompt", "")

        if current_prompt:
            # Add an instruction modifier
            if random.random() < 0.5:
                modifier = random.choice(self.instruction_modifiers)
                new_prompt = f"{current_prompt}\n{modifier}"
            else:
                # Rephrase
                new_prompt = self._rephrase_prompt(current_prompt)

            mutated["config"]["system_prompt"] = new_prompt
            logger.debug("Mutated prompt")

        return mutated

    def _modify_prompt(self, prompt: str) -> str:
        """Modify an existing prompt."""
        modifications = [
            f"{prompt}\nAlways verify your answer.",
            f"{prompt}\nProvide step-by-step reasoning.",
            f"{prompt}\nConsider edge cases.",
            prompt.replace("You are", "You are an expert"),
            prompt.replace("should", "must"),
        ]
        return random.choice(modifications)

    def _rephrase_prompt(self, prompt: str) -> str:
        """
        Rephrase a prompt using LLM when available.

        Uses intelligent LLM-based rephrasing for meaningful improvements,
        with fallback to simple string replacements when no LLM is available.
        """
        if self.llm is not None:
            return self._llm_rephrase_prompt(prompt)
        return self._simple_rephrase_prompt(prompt)

    def _llm_rephrase_prompt(self, prompt: str) -> str:
        """Use LLM to intelligently rephrase the prompt."""
        rephrase_instructions = random.choice([
            "Rewrite this system prompt to be more concise while keeping the same meaning",
            "Improve this system prompt by making instructions clearer and more specific",
            "Rephrase this system prompt to encourage step-by-step reasoning",
            "Optimize this system prompt for accuracy and precision",
            "Enhance this system prompt with better structure and organization",
        ])

        llm_prompt = f"""{rephrase_instructions}:

Original prompt:
{prompt}

Provide ONLY the rephrased prompt, nothing else."""

        fallback = self._simple_rephrase_prompt(prompt)
        result = self._llm_generate(llm_prompt, fallback)

        # Validate the result is reasonable (not empty, not too different in length)
        if len(result) < 10 or len(result) > len(prompt) * 3:
            logger.debug("LLM rephrase result out of bounds, using fallback")
            return fallback

        logger.debug(f"LLM rephrased prompt: {result[:100]}...")
        return result

    def _simple_rephrase_prompt(self, prompt: str) -> str:
        """Simple heuristic-based prompt rephrasing (fallback)."""
        replacements = [
            ("You are", "Act as"),
            ("should", "need to"),
            ("Think", "Reason"),
            ("Provide", "Give"),
        ]

        new_prompt = prompt
        for old, new in replacements:
            if old in new_prompt and random.random() < 0.3:
                new_prompt = new_prompt.replace(old, new, 1)

        return new_prompt


class MemoryEvolutionStrategy(EvolutionStrategy):
    """
    Memory Evolution Strategy

    Evolves the agent's memory management:
    - Memory capacity
    - Retention thresholds
    - Retrieval strategies
    """

    def __init__(self, llm: Optional["BaseLLM"] = None):
        super().__init__(llm=llm)

    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a memory configuration variant."""
        variant = copy.deepcopy(config)

        # Add memory configuration if not present
        if "memory" not in variant:
            variant["memory"] = {}

        # Randomize memory parameters
        variant["memory"]["short_term_capacity"] = random.randint(5, 20)
        variant["memory"]["long_term_capacity"] = random.randint(50, 200)
        variant["memory"]["importance_threshold"] = random.uniform(0.3, 0.8)

        logger.debug("Generated memory configuration variant")
        return variant

    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate memory parameters."""
        mutated = copy.deepcopy(config)

        if "memory" not in mutated:
            mutated["memory"] = {}

        # Mutate one parameter
        param = random.choice(["short_term_capacity", "long_term_capacity", "importance_threshold"])

        if param == "short_term_capacity":
            current = mutated["memory"].get("short_term_capacity", 10)
            mutated["memory"]["short_term_capacity"] = max(1, current + random.randint(-3, 3))
        elif param == "long_term_capacity":
            current = mutated["memory"].get("long_term_capacity", 100)
            mutated["memory"]["long_term_capacity"] = max(10, current + random.randint(-20, 20))
        else:
            current = mutated["memory"].get("importance_threshold", 0.5)
            mutated["memory"]["importance_threshold"] = max(0.0, min(1.0, current + random.uniform(-0.2, 0.2)))

        logger.debug(f"Mutated memory parameter: {param}")
        return mutated


class ToolEvolutionStrategy(EvolutionStrategy):
    """
    Tool Evolution Strategy

    Evolves the agent's tool usage:
    - Creating new tools
    - Refining existing tools
    - Tool selection strategies
    """

    def __init__(self, llm: Optional["BaseLLM"] = None):
        super().__init__(llm=llm)

    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a tool configuration variant."""
        variant = copy.deepcopy(config)

        if "tools" not in variant:
            variant["tools"] = []

        # Add a new tool concept
        new_tool = {
            "name": f"custom_tool_{random.randint(1, 100)}",
            "description": "A custom tool for specific tasks",
            "enabled": True
        }

        variant["tools"].append(new_tool)
        logger.debug("Generated tool variant with new tool")

        return variant

    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate tool configuration."""
        mutated = copy.deepcopy(config)

        if "tools" in mutated and mutated["tools"]:
            # Toggle a random tool
            tool = random.choice(mutated["tools"])
            tool["enabled"] = not tool.get("enabled", True)
            logger.debug(f"Toggled tool: {tool.get('name')}")

        return mutated


class CodeEvolutionStrategy(EvolutionStrategy):
    """
    Code Evolution Strategy

    Evolves code solutions using genetic programming:
    - Mutating code structure
    - Combining code from successful solutions
    - Optimizing algorithms (LLM-based when available)

    When an LLM is provided, uses intelligent code optimization
    instead of naive string modifications.
    """

    def __init__(self, llm: Optional["BaseLLM"] = None):
        super().__init__(llm=llm)

        self.code_templates = {
            "sorting": """
def sort_algorithm(arr):
    # Sorting implementation
    return sorted(arr)
""",
            "search": """
def search_algorithm(arr, target):
    # Search implementation
    return target in arr
""",
        }

    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a code variant."""
        variant = copy.deepcopy(config)

        # Get current code or start with template
        current_code = variant.get("code", "")

        if not current_code:
            # Use a template
            template_name = random.choice(list(self.code_templates.keys()))
            new_code = self.code_templates[template_name]
        else:
            # Modify existing code
            new_code = self._modify_code(current_code)

        variant["code"] = new_code
        logger.debug("Generated code variant")

        return variant

    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate code."""
        mutated = copy.deepcopy(config)

        code = mutated.get("code", "")
        if code:
            # Simple mutations: add comments, change variable names, etc.
            mutations = [
                f"# Optimized version\n{code}",
                code.replace("arr", "data"),
                code.replace("target", "value"),
            ]
            mutated["code"] = random.choice(mutations)
            logger.debug("Mutated code")

        return mutated

    def _modify_code(self, code: str) -> str:
        """
        Modify existing code using LLM when available.

        Uses intelligent LLM-based code optimization for meaningful improvements,
        with fallback to simple modifications when no LLM is available.
        """
        if self.llm is not None:
            return self._llm_modify_code(code)
        return self._simple_modify_code(code)

    def _llm_modify_code(self, code: str) -> str:
        """Use LLM to intelligently modify/optimize code."""
        modification_instructions = random.choice([
            "Optimize this Python code for better performance while maintaining correctness",
            "Refactor this code to be more readable and maintainable",
            "Add appropriate error handling to this code",
            "Improve this code by using more Pythonic idioms",
            "Optimize this algorithm for better time complexity if possible",
        ])

        llm_prompt = f"""{modification_instructions}:

```python
{code}
```

Provide ONLY the modified Python code, no explanations. Keep the same function signatures."""

        fallback = self._simple_modify_code(code)
        result = self._llm_generate(llm_prompt, fallback)

        # Clean up result - extract code from markdown if present
        if "```python" in result:
            start = result.find("```python") + 9
            end = result.find("```", start)
            if end > start:
                result = result[start:end].strip()
        elif "```" in result:
            start = result.find("```") + 3
            end = result.find("```", start)
            if end > start:
                result = result[start:end].strip()

        # Validate result
        if len(result) < 10 or "def " not in result:
            logger.debug("LLM code modification invalid, using fallback")
            return fallback

        logger.debug(f"LLM modified code: {result[:100]}...")
        return result

    def _simple_modify_code(self, code: str) -> str:
        """Simple heuristic-based code modification (fallback)."""
        modifications = [
            f"{code}\n# Added optimization",
            code.replace("for", "# for"),  # Comment out loops
            code.replace("return", "# return"),
        ]
        return random.choice(modifications)

    def crossover(
        self,
        config1: Dict[str, Any],
        config2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crossover two code solutions."""
        child = copy.deepcopy(config1)

        code1 = config1.get("code", "")
        code2 = config2.get("code", "")

        if code1 and code2:
            # Simple crossover: combine parts of both codes
            lines1 = code1.split("\n")
            lines2 = code2.split("\n")

            # Take first half from parent1, second half from parent2
            midpoint = len(lines1) // 2
            child_code = "\n".join(lines1[:midpoint] + lines2[midpoint:])

            child["code"] = child_code
            logger.debug("Performed code crossover")

        return child


class MultiAgentEvolutionStrategy(EvolutionStrategy):
    """
    Multi-Agent Evolution Strategy

    Evolves multiple agents that interact:
    - Proposer-Solver-Judge triad
    - Cooperative agents
    - Competitive agents
    """

    def __init__(self, llm: Optional["BaseLLM"] = None):
        super().__init__(llm=llm)

    def generate_variant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a multi-agent configuration variant."""
        variant = copy.deepcopy(config)

        if "agents" not in variant:
            variant["agents"] = []

        # Add agent roles
        roles = ["proposer", "solver", "judge"]
        for role in roles:
            if role not in [a.get("role") for a in variant["agents"]]:
                variant["agents"].append({
                    "role": role,
                    "enabled": True,
                    "config": {}
                })

        logger.debug("Generated multi-agent variant")
        return variant

    def mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate multi-agent configuration."""
        mutated = copy.deepcopy(config)

        if "agents" in mutated and mutated["agents"]:
            # Modify an agent's configuration
            agent = random.choice(mutated["agents"])
            agent["enabled"] = random.random() < 0.7

            logger.debug(f"Mutated agent: {agent.get('role')}")

        return mutated
