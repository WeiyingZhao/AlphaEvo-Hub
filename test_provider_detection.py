#!/usr/bin/env python3
"""
Test provider auto-detection bug fix
"""
import sys
sys.path.insert(0, '/home/user/AlphaEvo-Hub')

from agent_evolve.core.agent import AgentCore

def test_provider_detection():
    """Test that model names correctly detect providers"""
    print("Testing Provider Auto-Detection Fix\n")
    print("=" * 60)

    test_cases = [
        ("mock", "mock"),
        ("gpt-3.5-turbo", "openai"),
        ("gpt-4", "openai"),
        ("claude-3-sonnet-20240229", "anthropic"),
        ("meta-llama/Llama-2-7b-hf", "huggingface"),
        ("mistralai/Mistral-7B-v0.1", "huggingface"),
    ]

    all_passed = True

    for model_name, expected_provider in test_cases:
        try:
            # Create agent with just model name
            agent = AgentCore(model=model_name)
            detected_provider = agent.config.model_provider

            if detected_provider == expected_provider:
                print(f"✓ {model_name:40} -> {detected_provider}")
            else:
                print(f"✗ {model_name:40} -> {detected_provider} (expected: {expected_provider})")
                all_passed = False

        except Exception as e:
            print(f"✗ {model_name:40} -> ERROR: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("All provider detection tests PASSED!")
    else:
        print("Some tests FAILED!")

    return all_passed

if __name__ == "__main__":
    success = test_provider_detection()
    sys.exit(0 if success else 1)
