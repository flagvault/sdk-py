# Changelog

All notable changes to the FlagVault Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-06

### 🛡️ Graceful Error Handling

This release introduces graceful error handling, making the SDK more resilient to network issues and API errors.

### ✨ New Features

- **Graceful error handling**: SDK now returns default values instead of throwing exceptions on API errors
- **Enhanced error messages**: Detailed console warnings help with debugging while maintaining application stability
- **Default value support**: `is_enabled()` method now accepts a `default_value` parameter (defaults to `False`)

### 🛠️ Improvements

- **Network resilience**: Automatic fallback to default values on network errors
- **Authentication errors**: Graceful handling of invalid API keys (401/403 responses)
- **Missing flags**: Graceful handling of non-existent flags (404 responses)
- **API errors**: Graceful handling of server errors (5xx responses)
- **Enhanced logging**: Informative console warnings for all error conditions

### 📝 Usage

```python
# No try/catch needed - errors are handled gracefully
is_enabled = sdk.is_enabled('my-feature', default_value=False)

# On network error, you'll see:
# FlagVault: Failed to connect to API for flag 'my-feature', using default: False
```

### 🔄 Backward Compatibility

- Fully backward compatible with v1.0.0
- Existing code will continue to work without changes
- Only parameter validation errors (empty flag keys) still raise exceptions

## [1.0.0] - 2025-06-07

### 🎉 First Stable Release

This is the first stable release of the FlagVault Python SDK, featuring a simplified API design with automatic environment detection.

### 💥 Breaking Changes

- **Removed `api_secret` parameter**: SDK now uses single API key authentication
- **Made `base_url` private**: Base URL is now `_base_url` (internal parameter)
- **API endpoint change**: Updated from `/feature-flag/` to `/api/feature-flag/`

### ✨ New Features

- **Automatic environment detection**: Environment (production/test) is automatically determined from API key prefix
  - `live_` prefix → Production environment
  - `test_` prefix → Test environment
- **Simplified initialization**: Only requires a single `api_key` parameter
- **Zero configuration**: No need to specify environment or base URL

### 🛠️ Changes

- Updated all examples to use single API key pattern
- Improved error messages for better debugging
- Enhanced test coverage to 100%
- Updated documentation with environment management guide

### 📦 Dependencies

- `requests >= 2.25.0` (no changes)

### 🔄 Migration Guide

#### Before (0.1.0):
```python
sdk = FlagVaultSDK(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://api.flagvault.com",  # optional
    timeout=10  # optional
)
```

#### After (1.0.0):
```python
sdk = FlagVaultSDK(
    api_key="live_your-api-key-here",  # or 'test_' for test environment
    timeout=10  # optional, in seconds
)
```

### 📚 Documentation

- Comprehensive README with environment management section
- Updated API reference documentation
- New examples demonstrating environment-specific usage
- Clear migration guide from previous versions

---

## [0.1.0] - 2024-11-15

### 🚀 Initial Release

- Basic SDK implementation with `is_enabled()` method
- Support for API key and secret authentication
- Error handling with custom exception types
- Comprehensive test suite with 92% coverage
- Basic examples and documentation