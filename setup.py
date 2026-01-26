#!/usr/bin/env python3
"""
Setup file for cicd-cli
This allows editable installation with pip install -e .
"""
from setuptools import setup, find_packages

setup(
    name="cicd-cli",
    version="0.1.0",
    description="Auto-detect project frameworks and generate CI/CD pipeline files",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "typer[all]>=0.9.0",
        "jinja2>=3.1.2",
        "rich>=13.7.0",
        "pydantic<2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cicd=cli.main:main",
        ],
    },
    package_data={
        "frameworks.python": ["templates/*.j2"],
        "frameworks.node": ["templates/*.j2"],
        "frameworks.maven": ["templates/*.j2"],
        "frameworks.gradle": ["templates/*.j2"],
        "frameworks.java": ["templates/*.j2"],
        "frameworks.dotnet": ["templates/*.j2"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=["ci", "cd", "jenkins", "gitlab", "github", "pipeline", "devops", "cicd"],
)
