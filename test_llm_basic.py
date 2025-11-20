#!/usr/bin/env python3
"""
Basic test script for LLM integration
"""
import os
from agent_evolve.core.llm import get_llm

def test_openai_llm():
    """Test OpenAI LLM integration"""
    print("=" * 60)
    print("Testing OpenAI LLM Integration")
    print("=" * 60)

    try:
        # Create OpenAI LLM instance
        llm = get_llm(
            provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100
        )
        print(f"✓ LLM instance created: {llm}")

        # Test simple generation
        messages = [{"role": "user", "content": "Say 'Hello, I am working!' in exactly those words."}]
        print(f"\nSending message: {messages[0]['content']}")

        response = llm.generate(messages)
        print(f"✓ Response received: {response}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_llm():
    """Test Mock LLM (no API key required)"""
    print("\n" + "=" * 60)
    print("Testing Mock LLM")
    print("=" * 60)

    try:
        # Create Mock LLM instance
        llm = get_llm(
            provider="mock",
            model_name="mock-model"
        )
        print(f"✓ Mock LLM instance created: {llm}")

        # Test simple generation
        messages = [{"role": "user", "content": "Test message"}]
        response = llm.generate(messages)
        print(f"✓ Mock response received: {response}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting LLM Integration Tests\n")

    # Test 1: Mock LLM (should always work)
    mock_success = test_mock_llm()

    # Test 2: OpenAI LLM (requires API key)
    if os.getenv("OPENAI_API_KEY"):
        openai_success = test_openai_llm()
    else:
        print("\n⚠ Skipping OpenAI test: OPENAI_API_KEY not set")
        openai_success = None

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Mock LLM: {'✓ PASS' if mock_success else '✗ FAIL'}")
    if openai_success is not None:
        print(f"OpenAI LLM: {'✓ PASS' if openai_success else '✗ FAIL'}")
    else:
        print(f"OpenAI LLM: ⊘ SKIPPED")
