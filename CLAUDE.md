# FlagVault Python SDK Guidelines

## Setup Commands
- **Create Virtual Environment**: `python -m venv venv && source venv/bin/activate`
- **Install Dependencies**: `pip install -r requirements-dev.txt`
- **Install in Development Mode**: `pip install -e .`

## Build Commands
- **Build Package**: `python setup.py build`
- **Build Distribution**: `python -m build`

## Test Commands
- **Run All Tests**: `pytest`
- **Run Tests with Coverage**: `pytest --cov=flagvault_sdk`
- **Run Specific Test**: `pytest tests/test_specific_file.py -k "test_name"`

## Lint Commands
- **Run Flake8**: `flake8 flagvault_sdk tests`
- **Run Black**: `black flagvault_sdk tests`
- **Run isort**: `isort flagvault_sdk tests`
- **Run All Linters**: `flake8 flagvault_sdk tests && black flagvault_sdk tests && isort flagvault_sdk tests`

## Packaging Commands
- **Create Source Distribution**: `python setup.py sdist`
- **Create Wheel Distribution**: `python setup.py bdist_wheel`

## Type Checking
- **Run MyPy**: `mypy flagvault_sdk`