"""
LLM Integration Module

Provides unified interface for multiple LLM providers including
OpenAI, Anthropic, and Hugging Face.
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging
import os

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Base class for LLM providers."""

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response from messages."""
        pass

    @abstractmethod
    def generate_stream(self, messages: List[Dict[str, str]]):
        """Generate a streaming response."""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI LLM integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.\n"
                    "You can set it in your code: os.environ['OPENAI_API_KEY'] = 'your-key-here'\n"
                    "Or create a .env file with: OPENAI_API_KEY=your-key-here\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
            self.client = openai.OpenAI(api_key=api_key)
            logger.info(f"OpenAI client initialized for model: {self.model_name}")
        except ImportError as e:
            raise ImportError(
                "OpenAI package not installed.\n"
                "Install it with: pip install openai"
            ) from e

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self.kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate_stream(self, messages: List[Dict[str, str]]):
        """Generate streaming response."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                **self.kwargs
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            raise


class AnthropicLLM(BaseLLM):
    """Anthropic Claude integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.\n"
                    "You can set it in your code: os.environ['ANTHROPIC_API_KEY'] = 'your-key-here'\n"
                    "Or create a .env file with: ANTHROPIC_API_KEY=your-key-here\n"
                    "Get your API key from: https://console.anthropic.com/settings/keys"
                )
            self.client = anthropic.Anthropic(api_key=api_key)
            logger.info(f"Anthropic client initialized for model: {self.model_name}")
        except ImportError as e:
            raise ImportError(
                "Anthropic package not installed.\n"
                "Install it with: pip install anthropic"
            ) from e

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Anthropic API."""
        # Extract system message if present
        system_message = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)

        try:
            kwargs = {"model": self.model_name, "max_tokens": self.max_tokens, "messages": filtered_messages}
            if system_message:
                kwargs["system"] = system_message

            response = self.client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate_stream(self, messages: List[Dict[str, str]]):
        """Generate streaming response."""
        system_message = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)

        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": self.max_tokens,
                "messages": filtered_messages,
                "stream": True
            }
            if system_message:
                kwargs["system"] = system_message

            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            raise


class HuggingFaceLLM(BaseLLM):
    """
    Hugging Face model integration.

    Uses the tokenizer's chat template when available for proper formatting
    of chat messages. This ensures compatibility with modern open-source models
    like Llama 3, Mistral, and others that have specific chat formats.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)

            # Check if tokenizer has chat template support
            self._has_chat_template = hasattr(self.tokenizer, 'apply_chat_template')
            if self._has_chat_template:
                logger.info(f"HuggingFace model loaded with chat template support: {self.model_name}")
            else:
                logger.info(f"HuggingFace model loaded (no chat template): {self.model_name}")
            logger.info(f"Running on device: {self.device}")

        except ImportError as e:
            raise ImportError(
                "HuggingFace models require torch and transformers packages.\n"
                "Install them with: pip install torch transformers\n"
                "Or install all local model support with: pip install agent-evolve[local]\n"
                "For cloud-only usage (OpenAI/Anthropic), use those providers instead."
            ) from e

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using HuggingFace model."""
        # Format messages into prompt using chat template if available
        prompt = self._format_messages(messages)

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from response
        response = response[len(prompt):].strip()

        return response

    def generate_stream(self, messages: List[Dict[str, str]]):
        """Generate streaming response (simplified for local models)."""
        # For simplicity, return full response
        # Actual streaming would require TextIteratorStreamer
        response = self.generate(messages)
        for char in response:
            yield char

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into a prompt string.

        Uses the tokenizer's apply_chat_template when available,
        ensuring proper formatting for modern models (Llama 3, Mistral, etc.).
        Falls back to simple formatting for older models without chat templates.
        """
        if self._has_chat_template:
            return self._format_with_chat_template(messages)
        return self._format_simple(messages)

    def _format_with_chat_template(self, messages: List[Dict[str, str]]) -> str:
        """Format using tokenizer's chat template (recommended for modern models)."""
        try:
            # apply_chat_template handles model-specific formatting automatically
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            return prompt
        except Exception as e:
            logger.warning(f"Chat template failed, falling back to simple format: {e}")
            return self._format_simple(messages)

    def _format_simple(self, messages: List[Dict[str, str]]) -> str:
        """Simple fallback formatting for models without chat templates."""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


class MockLLM(BaseLLM):
    """Mock LLM for testing purposes."""

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Return a mock response."""
        last_message = messages[-1]["content"] if messages else ""
        return f"Mock response to: {last_message[:50]}..."

    def generate_stream(self, messages: List[Dict[str, str]]):
        """Return mock streaming response."""
        response = self.generate(messages)
        for char in response:
            yield char


def get_llm(
    provider: str,
    model_name: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    **kwargs
) -> BaseLLM:
    """
    Factory function to get LLM instance.

    Args:
        provider: LLM provider (openai, anthropic, huggingface, mock)
        model_name: Model identifier
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional provider-specific arguments

    Returns:
        LLM instance
    """
    providers = {
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "huggingface": HuggingFaceLLM,
        "mock": MockLLM
    }

    provider_class = providers.get(provider.lower())
    if provider_class is None:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")

    return provider_class(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
