from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-evolve",
    version="0.1.0",
    author="AlphaEvo Team",
    author_email="contact@alphaevo.ai",
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
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "langchain>=0.0.300",
        "deap>=1.4.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agent-evolve=agent_evolve.cli:main",
        ],
    },
)
