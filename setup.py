from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-evolve",
    version="0.1.0",
    author="AlphaEvo Team",
    description="A general-purpose AI agent platform that continuously self-improves over time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WeiyingZhao/AlphaEvo-Hub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies (minimal install)
        "openai>=1.0.0",
        "anthropic>=0.3.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "langchain>=0.0.300",
        "deap>=1.4.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "faiss-cpu>=1.7.4",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "websockets>=11.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "tinydb>=4.8.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.0.0",
        "tqdm>=4.65.0",  # For progress bars
    ],
    extras_require={
        "local": [
            # For running local HuggingFace models
            "torch>=2.0.0",
            "transformers>=4.30.0",
        ],
        "full": [
            # All features including local models
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "ray[rllib]>=2.5.0",
            "docker>=6.1.0",
            "pyodide-build>=0.23.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-evolve=agent_evolve.cli:main",
        ],
    },
)
