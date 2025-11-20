"""
Tool Interface Module

Provides standardized interface for tool usage and management.
Supports Model Context Protocol (MCP) for tool interoperability.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ToolSchema:
    """Schema definition for a tool."""

    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str = "string"
    examples: List[str] = None


class Tool(ABC):
    """
    Base class for all tools.

    Tools are external capabilities the agent can invoke
    (e.g., calculator, web search, code executor).
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.usage_count = 0

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the tool with given input.

        Args:
            input_data: Tool input

        Returns:
            Tool execution result
        """
        pass

    def get_schema(self) -> ToolSchema:
        """Get tool schema for documentation."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters={}
        )

    def __call__(self, input_data: Any) -> Any:
        """Allow tool to be called directly."""
        self.usage_count += 1
        return self.execute(input_data)


class CalculatorTool(Tool):
    """Simple calculator tool."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic mathematical calculations. Input should be a math expression."
        )

    def execute(self, input_data: str) -> Any:
        """Evaluate mathematical expression."""
        try:
            # Safe eval with limited scope
            result = eval(input_data, {"__builtins__": {}}, {})
            logger.debug(f"Calculator: {input_data} = {result}")
            return result
        except Exception as e:
            error_msg = f"Calculation error: {e}"
            logger.error(error_msg)
            return error_msg


class PythonExecutorTool(Tool):
    """Executes Python code in a sandbox."""

    def __init__(self):
        super().__init__(
            name="python",
            description="Executes Python code and returns the output."
        )
        from agent_evolve.tools.sandbox import Sandbox
        self.sandbox = Sandbox()

    def execute(self, input_data: str) -> Any:
        """Execute Python code safely."""
        try:
            result = self.sandbox.execute_code(input_data, language="python")
            logger.debug(f"Python execution completed")
            return result
        except Exception as e:
            error_msg = f"Execution error: {e}"
            logger.error(error_msg)
            return error_msg


class WebSearchTool(Tool):
    """Web search tool (mock implementation)."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Searches the web for information. Input should be a search query."
        )

    def execute(self, input_data: str) -> Any:
        """Perform web search (mock)."""
        # In a real implementation, this would use an actual search API
        logger.debug(f"Web search: {input_data}")
        return f"[Mock] Search results for: {input_data}"


class ToolInterface:
    """
    Standardized interface for tool interaction.

    Provides a consistent API for tool registration, discovery, and execution.
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a new tool."""
        self.tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List available tool names."""
        return list(self.tools.keys())

    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all tools."""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)

    def execute(self, tool_name: str, input_data: Any) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if tool is None:
            raise ValueError(f"Tool not found: {tool_name}")

        return tool(input_data)


class ToolManager:
    """
    Manages tools for an agent, including tool evolution capabilities.

    Features:
    - Tool registration and discovery
    - Tool usage tracking
    - Tool creation and evolution (MCP support)
    """

    def __init__(self):
        self.interface = ToolInterface()
        self.tool_library: Dict[str, Tool] = {}

        # Register default tools
        self._register_default_tools()

    def _register_default_tools(self):
        """Register commonly used default tools."""
        default_tools = [
            CalculatorTool(),
            PythonExecutorTool(),
            WebSearchTool()
        ]

        for tool in default_tools:
            self.register_tool(tool)
            self.tool_library[tool.name] = tool

    def register_tool(self, tool: Tool):
        """Register a new tool."""
        self.interface.register(tool)
        logger.info(f"Tool registered: {tool.name}")

    def execute_tool(self, tool_name: str, input_data: Any) -> Any:
        """Execute a tool."""
        return self.interface.execute(tool_name, input_data)

    def get_tool_descriptions(self) -> str:
        """Get descriptions of available tools."""
        return self.interface.get_tool_descriptions()

    def list_tools(self) -> List[str]:
        """List available tools."""
        return self.interface.list_tools()

    def create_tool_from_code(
        self,
        name: str,
        description: str,
        code: str
    ) -> Tool:
        """
        Create a new tool from code (tool evolution).

        This enables the agent to create new tools during evolution.

        Args:
            name: Tool name
            description: Tool description
            code: Python code implementing the tool

        Returns:
            Created Tool instance
        """
        # Create a dynamic tool class
        class DynamicTool(Tool):
            def __init__(self, name, description, code):
                super().__init__(name, description)
                self.code = code

            def execute(self, input_data: Any) -> Any:
                # Execute the code with input
                from agent_evolve.tools.sandbox import Sandbox
                sandbox = Sandbox()
                result = sandbox.execute_code(
                    f"{self.code}\n\nresult = execute({repr(input_data)})",
                    language="python"
                )
                return result

        tool = DynamicTool(name, description, code)
        self.register_tool(tool)
        self.tool_library[name] = tool

        logger.info(f"Dynamic tool created: {name}")
        return tool

    def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for all tools."""
        stats = {}
        for name, tool in self.tool_library.items():
            stats[name] = tool.usage_count
        return stats

    def export_tools(self) -> Dict[str, Any]:
        """Export tool configurations."""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "usage_count": tool.usage_count
                }
                for tool in self.tool_library.values()
            ]
        }

    def __repr__(self) -> str:
        return f"ToolManager(tools={len(self.tool_library)})"
