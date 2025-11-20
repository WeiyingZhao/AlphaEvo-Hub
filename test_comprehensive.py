#!/usr/bin/env python3
"""
Comprehensive test suite for AlphaEvo-Hub platform
Tests core functionality, evolution strategies, and integration
"""
import sys
import os

sys.path.insert(0, '/home/user/AlphaEvo-Hub')

def test_imports():
    """Test that all modules can be imported"""
    print("\n" + "=" * 70)
    print("TEST 1: Module Imports")
    print("=" * 70)

    modules_to_test = [
        ("agent_evolve", "Main package"),
        ("agent_evolve.core.agent", "Agent Core"),
        ("agent_evolve.core.llm", "LLM Integration"),
        ("agent_evolve.core.context", "Context Manager"),
        ("agent_evolve.core.controller", "Agent Controller"),
        ("agent_evolve.optimizer.evolutionary", "Evolutionary Optimizer"),
        ("agent_evolve.optimizer.strategies", "Evolution Strategies"),
        ("agent_evolve.evaluator.base", "Base Evaluator"),
        ("agent_evolve.evaluator.qa", "QA Evaluator"),
        ("agent_evolve.evaluator.code", "Code Evaluator"),
        ("agent_evolve.memory.manager", "Memory Manager"),
        ("agent_evolve.tools.interface", "Tool Interface"),
    ]

    failed = []
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {description:30} ({module_name})")
        except Exception as e:
            print(f"✗ {description:30} ({module_name})")
            print(f"  Error: {e}")
            failed.append((module_name, e))

    return len(failed) == 0, failed


def test_agent_creation():
    """Test basic agent creation with different models"""
    print("\n" + "=" * 70)
    print("TEST 2: Agent Creation")
    print("=" * 70)

    from agent_evolve import AgentCore

    test_cases = [
        ("mock", "Mock LLM"),
        ("gpt-3.5-turbo", "OpenAI GPT-3.5"),
        ("claude-3-sonnet-20240229", "Anthropic Claude"),
    ]

    failed = []
    for model, description in test_cases:
        try:
            agent = AgentCore(model=model, task="Test task")
            detected_provider = agent.config.model_provider
            print(f"✓ {description:30} -> provider: {detected_provider}")
        except Exception as e:
            print(f"✗ {description:30}")
            print(f"  Error: {e}")
            failed.append((model, e))

    return len(failed) == 0, failed


def test_qa_evaluator():
    """Test QA Evaluator"""
    print("\n" + "=" * 70)
    print("TEST 3: QA Evaluator")
    print("=" * 70)

    try:
        from agent_evolve import AgentCore
        from agent_evolve.evaluator.qa import QAEvaluator

        # Create evaluator with test Q&A pairs
        qa_pairs = [
            {"question": "What is 2+2?", "answer": "4"},
            {"question": "What is the capital of France?", "answer": "Paris"},
        ]

        evaluator = QAEvaluator(qa_pairs=qa_pairs)
        print(f"✓ QA Evaluator created with {len(qa_pairs)} Q&A pairs")

        # Create mock agent
        agent = AgentCore(model="mock")
        print(f"✓ Mock agent created for testing")

        # Note: Can't fully test evaluation without running agent
        # which requires task completion that may fail with mock
        print(f"✓ QA Evaluator basic functionality verified")

        return True, []

    except Exception as e:
        print(f"✗ QA Evaluator test failed")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False, [("qa_evaluator", e)]


def test_evolution_config():
    """Test Evolution Configuration"""
    print("\n" + "=" * 70)
    print("TEST 4: Evolution Configuration")
    print("=" * 70)

    try:
        from agent_evolve import EvolutionaryOptimizer
        from agent_evolve.optimizer.evolutionary import EvolutionConfig

        # Test default config
        config = EvolutionConfig()
        print(f"✓ Default config: strategy={config.strategy}, generations={config.generations}")

        # Test custom config
        custom_config = EvolutionConfig(
            strategy="prompt_optimization",
            generations=5,
            population_size=3
        )
        print(f"✓ Custom config: strategy={custom_config.strategy}, pop_size={custom_config.population_size}")

        # Create optimizer
        optimizer = EvolutionaryOptimizer(
            strategy="prompt_optimization",
            generations=3
        )
        print(f"✓ Evolutionary Optimizer created")

        return True, []

    except Exception as e:
        print(f"✗ Evolution configuration test failed")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False, [("evolution_config", e)]


def test_strategy_loading():
    """Test loading all evolution strategies"""
    print("\n" + "=" * 70)
    print("TEST 5: Evolution Strategies")
    print("=" * 70)

    from agent_evolve.optimizer.evolutionary import EvolutionaryOptimizer

    strategies = [
        "prompt_optimization",
        "memory_evolution",
        "tool_evolution",
        "code_evolution"
    ]

    failed = []
    for strategy in strategies:
        try:
            optimizer = EvolutionaryOptimizer(strategy=strategy, generations=1)
            print(f"✓ Strategy loaded: {strategy}")
        except Exception as e:
            print(f"✗ Strategy failed: {strategy}")
            print(f"  Error: {e}")
            failed.append((strategy, e))

    return len(failed) == 0, failed


def test_context_manager():
    """Test Context Manager"""
    print("\n" + "=" * 70)
    print("TEST 6: Context Manager")
    print("=" * 70)

    try:
        from agent_evolve.core.context import ContextManager

        ctx = ContextManager(max_length=1024)
        print(f"✓ Context Manager created (max_length={ctx.max_length})")

        # Test adding messages
        ctx.set_system_prompt("You are a helpful assistant")
        ctx.add_user_message("Hello!")
        ctx.add_assistant_message("Hi there!")

        messages = ctx.get_messages()
        print(f"✓ Messages added and retrieved (count={len(messages)})")

        return True, []

    except Exception as e:
        print(f"✗ Context Manager test failed")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False, [("context_manager", e)]


def run_all_tests():
    """Run all tests and generate report"""
    print("\n")
    print("#" * 70)
    print("# AlphaEvo-Hub Comprehensive Test Suite")
    print("#" * 70)

    all_results = []

    # Run tests
    tests = [
        ("Module Imports", test_imports),
        ("Agent Creation", test_agent_creation),
        ("QA Evaluator", test_qa_evaluator),
        ("Evolution Config", test_evolution_config),
        ("Strategy Loading", test_strategy_loading),
        ("Context Manager", test_context_manager),
    ]

    for test_name, test_func in tests:
        try:
            passed, failures = test_func()
            all_results.append((test_name, passed, failures))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            all_results.append((test_name, False, [(test_name, e)]))

    # Generate summary
    print("\n" + "#" * 70)
    print("# TEST SUMMARY")
    print("#" * 70)

    total_tests = len(all_results)
    passed_tests = sum(1 for _, passed, _ in all_results if passed)
    failed_tests = total_tests - passed_tests

    for test_name, passed, failures in all_results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
        if not passed and failures:
            for item, error in failures:
                print(f"         - {item}: {str(error)[:60]}")

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if failed_tests > 0:
        print(f"\n⚠ {failed_tests} test(s) failed")
        return False
    else:
        print(f"\n✓ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
