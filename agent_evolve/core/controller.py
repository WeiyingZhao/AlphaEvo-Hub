"""
Agent Controller Module

Orchestrates the agent's action loop, deciding when to reason,
when to invoke tools, and when to return results.
"""

from typing import Any, Dict, List, Optional
import logging
import json
import re

logger = logging.getLogger(__name__)


class AgentController:
    """
    Controls the agent's decision-making and action execution loop.

    The controller implements a ReAct-style reasoning loop where the agent:
    1. Thinks about the task
    2. Decides on an action (tool use or final answer)
    3. Observes the result
    4. Repeats until task is complete
    """

    def __init__(self, agent, use_tools: bool = True):
        """
        Initialize the controller.

        Args:
            agent: Reference to the AgentCore instance
            use_tools: Whether to enable tool usage
        """
        self.agent = agent
        self.use_tools = use_tools
        self.tool_manager = None

        if use_tools:
            self._initialize_tools()

    def _initialize_tools(self):
        """Initialize tool management system."""
        from agent_evolve.tools.interface import ToolManager
        self.tool_manager = ToolManager()
        logger.debug("Tool manager initialized")

    def execute_task(
        self,
        task: str,
        max_iterations: int = 10,
        return_trace: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a task using a reasoning loop.

        Args:
            task: Task description
            max_iterations: Maximum reasoning iterations
            return_trace: Whether to return full reasoning trace

        Returns:
            Dictionary containing:
            - solution: Final answer/result
            - reasoning_trace: List of reasoning steps (if return_trace=True)
            - iterations: Number of iterations used
            - success: Whether task completed successfully
        """
        reasoning_trace = []
        iteration = 0
        final_answer = None

        logger.info(f"Executing task: {task[:100]}...")

        # Initial prompt for reasoning
        prompt = self._create_initial_prompt(task)

        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Iteration {iteration}/{max_iterations}")

            # Generate reasoning step
            response = self.agent.generate_response(prompt)

            # Parse response for actions
            parsed = self._parse_response(response)

            reasoning_trace.append({
                "iteration": iteration,
                "thought": parsed.get("thought", ""),
                "action": parsed.get("action"),
                "observation": None,
                "raw_response": response
            })

            # Check if final answer is reached
            if parsed["action_type"] == "answer":
                final_answer = parsed["action_content"]
                reasoning_trace[-1]["final_answer"] = final_answer
                logger.info("Final answer reached")
                break

            # Execute tool action if present
            if parsed["action_type"] == "tool" and self.use_tools:
                observation = self._execute_tool(
                    tool_name=parsed["tool_name"],
                    tool_input=parsed["action_content"]
                )
                reasoning_trace[-1]["observation"] = observation

                # Add observation to prompt for next iteration
                prompt = f"Observation: {observation}\n\nWhat should we do next?"
            else:
                # Continue reasoning
                prompt = "Continue reasoning about the task."

        # If no final answer after max iterations, use last response
        if final_answer is None:
            final_answer = response
            logger.warning("Max iterations reached without explicit final answer")

        result = {
            "solution": final_answer,
            "iterations": iteration,
            "success": final_answer is not None,
            "metadata": {
                "task": task,
                "max_iterations": max_iterations,
                "tools_used": self._get_tools_used(reasoning_trace)
            }
        }

        if return_trace:
            result["reasoning_trace"] = reasoning_trace

        return result

    def _create_initial_prompt(self, task: str) -> str:
        """Create the initial reasoning prompt."""
        if self.use_tools and self.tool_manager:
            tool_descriptions = self.tool_manager.get_tool_descriptions()
            tools_section = f"\n\nAvailable tools:\n{tool_descriptions}\n"
        else:
            tools_section = ""

        prompt = f"""Task: {task}

Please solve this task step by step. Use the following format:

Thought: [Your reasoning about what to do next]
Action: [Either use a tool or provide the final answer]
{tools_section}
When you have the final answer, use:
Answer: [Your final answer]

Let's begin:"""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the agent's response to extract thoughts and actions.

        Returns:
            Dictionary with:
            - thought: Reasoning text
            - action_type: 'tool', 'answer', or 'none'
            - tool_name: Name of tool to use (if action_type='tool')
            - action_content: Tool input or final answer
        """
        result = {
            "thought": "",
            "action_type": "none",
            "tool_name": None,
            "action_content": None
        }

        # Extract thought
        thought_match = re.search(r"Thought:\s*(.+?)(?:\n|$)", response, re.IGNORECASE | re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        # Check for final answer
        answer_match = re.search(r"Answer:\s*(.+)", response, re.IGNORECASE | re.DOTALL)
        if answer_match:
            result["action_type"] = "answer"
            result["action_content"] = answer_match.group(1).strip()
            return result

        # Check for tool action
        action_match = re.search(r"Action:\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
        if action_match:
            action_text = action_match.group(1).strip()

            # Try to parse tool call: ToolName(input)
            tool_call_match = re.match(r"(\w+)\((.*?)\)", action_text)
            if tool_call_match:
                result["action_type"] = "tool"
                result["tool_name"] = tool_call_match.group(1)
                result["action_content"] = tool_call_match.group(2).strip('"\'')

        return result

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """
        Execute a tool and return the observation.

        Args:
            tool_name: Name of the tool
            tool_input: Input for the tool

        Returns:
            Tool execution result as string
        """
        if not self.tool_manager:
            return "Error: Tool manager not initialized"

        try:
            logger.debug(f"Executing tool: {tool_name}({tool_input})")
            result = self.tool_manager.execute_tool(tool_name, tool_input)

            # Update agent state
            if tool_name not in self.agent.state.tools_used:
                self.agent.state.tools_used.append(tool_name)

            return str(result)
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _get_tools_used(self, reasoning_trace: List[Dict]) -> List[str]:
        """Extract list of unique tools used from reasoning trace."""
        tools = set()
        for step in reasoning_trace:
            if step.get("action") and "tool" in step.get("action", "").lower():
                # Extract tool name from action
                action = step["action"]
                tool_match = re.match(r"(\w+)\(", action)
                if tool_match:
                    tools.add(tool_match.group(1))
        return list(tools)

    def set_tool_manager(self, tool_manager):
        """Set a custom tool manager."""
        self.tool_manager = tool_manager
        logger.info("Custom tool manager set")

    def add_tool(self, tool):
        """Add a tool to the tool manager."""
        if self.tool_manager:
            self.tool_manager.register_tool(tool)
        else:
            logger.warning("Tool manager not initialized")

    def __repr__(self) -> str:
        return f"AgentController(use_tools={self.use_tools})"
