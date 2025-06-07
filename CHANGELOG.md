# Changelog

All notable changes to the FlagVault Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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