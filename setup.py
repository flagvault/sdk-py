from setuptools import setup, find_packages
import os

# Read the README file for the long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read version from the package
with open(os.path.join(here, "flagvault_sdk", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            __version__ = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="flagvault-sdk",
    version=__version__,
    description="Lightweight Python SDK for FlagVault with intelligent caching, enabling seamless feature flag integration and real-time flag status checks for Python applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="FlagVault",
    author_email="accounts@flagvault.com",
    url="https://github.com/flagvault/sdk-py",
    project_urls={
        "Bug Reports": "https://github.com/flagvault/sdk-py/issues",
        "Source": "https://github.com/flagvault/sdk-py",
        "Documentation": "https://flagvault.com/docs",
    },
    keywords=["feature-flag", "feature-flags", "feature-toggle", "feature-toggles", "sdk", "python", "flagvault", "remote-config", "a-b-testing", "experimentation", "caching", "performance"],
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "flake8>=3.8",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.900",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.6",
)