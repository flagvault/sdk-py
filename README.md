# FlagVault Python SDK

A lightweight Python SDK that allows developers to integrate FlagVault's feature flag service into their Python applications. Feature flags let you enable/disable features remotely without deploying new code.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Use Cases](#use-cases)
- [Project Structure](#project-structure)
- [Development](#development)
- [Requirements](#requirements)

## Installation

```bash
pip install flagvault-sdk
# or
poetry add flagvault-sdk
```

## Quick Start

```python
from flagvault_sdk import FlagVaultSDK, FlagVaultAuthenticationError, FlagVaultNetworkError

# Initialize the SDK with your API credentials
sdk = FlagVaultSDK(
    api_key="your-api-key",
    api_secret="your-api-secret",
    # Optional: custom base URL and timeout
    # base_url="https://custom-api.flagvault.com",
    # timeout=10
)

# Check if a feature flag is enabled
def check_feature():
    try:
        is_enabled = sdk.is_enabled("my-feature-flag")
        
        if is_enabled:
            # Feature is enabled, run feature code
            print("Feature is enabled!")
        else:
            # Feature is disabled, run fallback code
            print("Feature is disabled.")
    except FlagVaultAuthenticationError:
        print("Invalid API credentials")
    except FlagVaultNetworkError:
        print("Network connection failed")
    except Exception as error:
        print(f"Unexpected error: {error}")

check_feature()
```

## Project Overview

### What It Is

FlagVault Python SDK provides a simple, reliable way to integrate feature flags into your Python applications. Feature flags (also known as feature toggles) allow you to:

- Enable/disable features without deploying new code
- Perform A/B testing and gradual rollouts
- Create kill switches for problematic features
- Manage environment-specific features

### Core Functionality

The SDK centers around one main class and method:

```python
# Initialize once
sdk = FlagVaultSDK(api_key="key", api_secret="secret")

# Use throughout your application
if sdk.is_enabled("new-checkout-flow"):
    show_new_checkout()
else:
    show_old_checkout()
```

### How It Works

1. **Initialize**: Create SDK instance with API credentials from your FlagVault dashboard
2. **Check Flag**: Call `is_enabled("flag-key")` anywhere in your code
3. **HTTP Request**: SDK makes secure GET request to FlagVault API
4. **Parse Response**: Returns boolean from API response
5. **Handle Errors**: Specific exceptions for different failure scenarios

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from flagvault_sdk import (
    FlagVaultSDK,
    FlagVaultError,
    FlagVaultAuthenticationError,
    FlagVaultNetworkError,
    FlagVaultAPIError,
)

try:
    is_enabled = sdk.is_enabled("my-feature-flag")
except FlagVaultAuthenticationError:
    # Handle authentication errors (401, 403)
    print("Check your API credentials")
except FlagVaultNetworkError:
    # Handle network errors (timeouts, connection issues)
    print("Network connection problem")
except FlagVaultAPIError:
    # Handle API errors (500, malformed responses, etc.)
    print("API error occurred")
except ValueError:
    # Handle invalid input (empty flag_key, etc.)
    print("Invalid input provided")
```

### Exception Types

- **`FlagVaultAuthenticationError`**: Invalid API credentials (401/403 responses)
- **`FlagVaultNetworkError`**: Connection timeouts, network failures
- **`FlagVaultAPIError`**: Server errors, malformed responses
- **`ValueError`**: Invalid input parameters (empty flag keys, etc.)
- **`FlagVaultError`**: Base exception class for all SDK errors

## Configuration

### SDK Parameters

- **`api_key`** (required): Your FlagVault API key
- **`api_secret`** (required): Your FlagVault API secret  
- **`base_url`** (optional): Custom API endpoint. Defaults to `https://api.flagvault.com`
- **`timeout`** (optional): Request timeout in seconds. Defaults to 10

### Getting API Credentials

1. Sign up at [FlagVault](https://flagvault.com)
2. Create a new project
3. Go to Settings > API Credentials
4. Generate new API credentials

## API Reference

### `FlagVaultSDK(api_key, api_secret, base_url=None, timeout=10)`

Creates a new FlagVault SDK instance.

**Parameters:**
- `api_key` (str): Your FlagVault API key
- `api_secret` (str): Your FlagVault API secret
- `base_url` (str, optional): Custom API endpoint
- `timeout` (int, optional): Request timeout in seconds

**Raises:**
- `ValueError`: If api_key or api_secret is empty

### `is_enabled(flag_key: str) -> bool`

Checks if a feature flag is enabled.

**Parameters:**
- `flag_key` (str): The key/name of the feature flag

**Returns:** 
- `bool`: True if the flag is enabled, False otherwise

**Raises:**
- `ValueError`: If flag_key is empty or None
- `FlagVaultAuthenticationError`: If API credentials are invalid
- `FlagVaultNetworkError`: If network request fails
- `FlagVaultAPIError`: If API returns an error

## Use Cases

### 1. A/B Testing
```python
if sdk.is_enabled("new-ui-design"):
    render_new_design()
else:
    render_current_design()
```

### 2. Gradual Rollouts
```python
if sdk.is_enabled("premium-feature"):
    show_premium_features()
else:
    show_basic_features()
```

### 3. Kill Switches
```python
if sdk.is_enabled("external-api-integration"):
    call_external_api()
else:
    use_cached_data()  # Fallback if external service has issues
```

### 4. Environment-Specific Features
```python
if sdk.is_enabled("debug-mode"):
    enable_verbose_logging()
    show_debug_info()
```

## Project Structure

```
sdk-py/
├── flagvault_sdk/           # Main package
│   ├── __init__.py         # Package exports & version
│   └── flagvault_sdk.py    # Core SDK implementation
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_flagvault_sdk.py
├── examples/               # Usage examples
├── LICENSE                 # MIT license
├── README.md              # This file
├── setup.py               # Package configuration
├── pyproject.toml         # Build configuration
└── requirements-dev.txt   # Development dependencies
```

### Key Features

- **🚀 Simple**: One method, clear API
- **🛡️ Reliable**: Comprehensive error handling with custom exceptions
- **🔧 Compatible**: Works with Python 3.6+
- **✅ Well-Tested**: 92% test coverage, handles edge cases
- **⚡ Production-Ready**: Configurable timeouts, proper error types
- **📦 Lightweight**: Only requires `requests` library

### Testing Strategy

The SDK includes 14 comprehensive tests covering:
- ✅ Initialization (valid/invalid credentials)
- ✅ Successful flag checks (enabled/disabled responses)
- ✅ Error scenarios (authentication, network, API errors)
- ✅ Edge cases (invalid JSON, missing fields, special characters)
- ✅ Timeout and connection handling

## Requirements

- Python 3.6 or later
- requests >= 2.25.0

## Development

### Setting up for development

```bash
# Clone the repository
git clone https://github.com/flagvault/sdk-py.git
cd sdk-py

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
pip install -r requirements-dev.txt
```

### Running tests

```bash
pytest
# With coverage
pytest --cov=flagvault_sdk
```

### Code Quality

```bash
# Linting
flake8 flagvault_sdk tests

# Code formatting
black flagvault_sdk tests

# Import sorting
isort flagvault_sdk tests

# Type checking
mypy flagvault_sdk
```

### Building the package

```bash
python -m build
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

- 📚 [Documentation](https://flagvault.com/docs)
- 🐛 [Bug Reports](https://github.com/flagvault/sdk-py/issues)
- 💬 [Community Support](https://flagvault.com/community)

---

Made with ❤️ by the FlagVault team