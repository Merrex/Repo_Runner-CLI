"""
Setup script for repo_runner.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="repo_runner",
    version="1.0.0",
    author="repo_runner",
    author_email="info@repo_runner.dev",
    description="Modular Python CLI tool for automatic repository detection and execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/repo_runner/repo_runner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Installation/Setup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "PyYAML>=6.0",
        "python-dotenv>=0.19.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "accelerate>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "repo_runner=repo_runner.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)