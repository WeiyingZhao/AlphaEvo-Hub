# AlphaEvo-Hub Improvement Plan

This document outlines a comprehensive plan to improve the AlphaEvo-Hub project, focusing on code quality, architecture, testing, and developer experience.

## 1. Backend Improvements (`agent_evolve/`)

### 1.1. Enhance Evolution Strategies
The current implementation of evolution strategies in `strategies.py` (specifically `_rephrase_prompt`, `_modify_code`) relies on simple random string replacements. This is insufficient for genuine self-improvement.

*   **Suggestion**: Implement "LLM-based Evolution". Instead of random string manipulation, use the LLM itself to propose variations.
    *   *Example*: Ask the LLM to "Rewrite this system prompt to be more concise and accurate" or "Optimize this Python code for performance".
*   **Action**: Refactor `PromptEvolutionStrategy` and `CodeEvolutionStrategy` to use `agent.llm.generate` for mutations.

### 1.2. Robust LLM Integration
The `HuggingFaceLLM` class currently uses a hardcoded prompt format (`System: ... User: ...`), which may not work well for all models (e.g., Llama 3, Mistral).

*   **Suggestion**: Use `tokenizer.apply_chat_template` which is the standard way to handle chat formats in the `transformers` library. This ensures compatibility with any modern open-source model.
*   **Action**: Update `HuggingFaceLLM._format_messages` to use the tokenizer's chat template capabilities.

### 1.3. Asynchronous Architecture
The current `AgentCore.run` and `EvolutionaryOptimizer.evolve` methods are synchronous. LLM operations are I/O bound, and network latency will be a bottleneck, especially for population-based evolution.

*   **Suggestion**: Convert core methods to `async/await`. This allows running multiple evolution trials or parallel agent steps concurrently without threads.
*   **Action**: update `AgentCore` and `LLM` classes to support `async` methods.

### 1.4. Type Safety
While type hints are present, `Any` is used frequently (e.g., `config: Dict[str, Any]`).

*   **Suggestion**: Use `Pydantic` models for Configuration and State. This provides runtime validation and better IDE support.
    *   Replace `dataclass` with `pydantic.BaseModel`.
*   **Action**: Refactor `AgentConfig`, `AgentState`, and `EvolutionConfig` to use Pydantic.

## 2. Testing & Quality Assurance

### 2.1. Modernize Test Suite
The current `test_comprehensive.py` is a manual script that acts as a smoke test. It lacks isolation, fixtures, and proper assertions.

*   **Suggestion**: Migrate to `pytest`.
*   **Action**:
    *   Create a `tests/` directory.
    *   Split tests into `tests/unit` and `tests/integration`.
    *   Use `unittest.mock` to mock `openai`, `anthropic`, and `transformers` clients. This prevents test failures due to missing API keys (as seen in current test runs).

### 2.2. Continuous Integration (CI)
*   **Suggestion**: Add a basic CI pipeline (GitHub Actions) to run linting (`flake8`, `black`) and tests (`pytest`) on every commit.

## 3. Frontend Improvements (`frontend/`)

### 3.1. Build Tool Migration
The frontend currently uses `react-scripts` (Create React App), which is now considered legacy.

*   **Suggestion**: Migrate to **Vite**. Vite offers significantly faster development startup and build times.
*   **Action**: Re-initialize the frontend with `npm create vite@latest` or manually migrate `package.json` and `index.html`.

### 3.2. State Management
As the application grows to visualize complex evolutionary trees, local React state might become unmanageable.

*   **Suggestion**: Adopt a lightweight state management library like **Zustand** or **Jotai**.

## 4. Developer Experience & DevOps

### 4.1. Dependency Management
The project uses `requirements.txt` and `setup.py`.

*   **Suggestion**: Move to `pyproject.toml` for standardized build configuration.
*   **Suggestion**: Make heavy dependencies (like `torch` and `transformers`) optional extras if the user only wants to use API-based models (OpenAI/Anthropic).
    *   *Example*: `pip install alphaevo-hub[local]` vs `pip install alphaevo-hub[apis]`.

### 4.2. Documentation
*   **Suggestion**: detailed "Getting Started" guide that explicitly mentions API key requirements.
*   **Suggestion**: Add docstrings to the simple implementations in `strategies.py` explaining they are placeholders and pointing to where users can implement more complex logic.

## Summary of Priority Tasks

1.  **[High] COMPLETED** Refactor `strategies.py` to use LLM for mutation (actual intelligence vs random strings).
    - Added optional LLM parameter to all evolution strategies
    - `PromptEvolutionStrategy` now uses LLM for intelligent prompt rephrasing
    - `CodeEvolutionStrategy` now uses LLM for intelligent code optimization
    - Fallback to simple heuristics when no LLM is provided
    - `EvolutionaryOptimizer` automatically uses agent's LLM if available

2.  **[High] COMPLETED** Fix `test_comprehensive.py` by mocking missing credentials so tests pass locally.
    - Updated provider detection tests to use `_detect_provider` method directly
    - All 50 tests now pass without requiring API keys

3.  **[Medium] EVALUATED** Migrate Frontend to Vite.
    - Current frontend is minimal (4 JS files)
    - Uses React 18, react-router-dom, MUI, recharts
    - Migration would improve build times but is lower priority given app size
    - Recommended for future iteration when frontend grows

4.  **[Medium] COMPLETED** Update `HuggingFaceLLM` to use chat templates.
    - Now uses `tokenizer.apply_chat_template` when available
    - Automatic fallback to simple formatting for older models
    - Compatible with modern models (Llama 3, Mistral, etc.)

## Additional Improvements Made

5.  **[Medium] COMPLETED** Add GitHub Actions CI (`.github/workflows/ci.yml`)
    - Runs tests on Python 3.9, 3.10, 3.11, 3.12
    - Includes linting (black, flake8) and test coverage
    - Caches pip dependencies for faster runs

6.  **[Medium] COMPLETED** Add `pyproject.toml` for standardized build configuration
    - Modern PEP 517/518 compliant build configuration
    - Includes tool configurations for black, flake8, mypy, pytest
    - Maintains compatibility with existing setup.py
