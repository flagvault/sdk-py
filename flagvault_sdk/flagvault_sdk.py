import requests
from typing import Dict, Optional, Any
import json

class FlagVaultError(Exception):
    """Base exception for FlagVault SDK errors."""
    pass


class FlagVaultAuthenticationError(FlagVaultError):
    """Raised when authentication fails."""
    pass


class FlagVaultNetworkError(FlagVaultError):
    """Raised when network requests fail."""
    pass


class FlagVaultAPIError(FlagVaultError):
    """Raised when the API returns an error response."""
    pass


class FlagVaultSDK:
    """
    FlagVault SDK for feature flag management.

    This SDK allows you to easily integrate feature flags into your Python applications.
    Feature flags (also known as feature toggles) allow you to enable or disable features
    in your application without deploying new code.

    Basic Usage:
    ```python
    from flagvault_sdk import FlagVaultSDK

    sdk = FlagVaultSDK(
        api_key="live_your-api-key-here"  # Use 'test_' prefix for test environment
    )

    # Check if a feature flag is enabled
    is_enabled = sdk.is_enabled("my-feature-flag", default_value=False)
    if is_enabled:
        # Feature is enabled, run feature code
        pass
    else:
        # Feature is disabled, run fallback code
        pass
    ```

    Error Handling:
    ```python
    try:
        is_enabled = sdk.is_enabled("my-feature-flag")
        # ...
    except FlagVaultAuthenticationError:
        # Handle authentication errors
        print("Invalid API credentials")
    except FlagVaultNetworkError:
        # Handle network errors
        print("Network connection failed")
    except FlagVaultAPIError as error:
        # Handle API errors
        print(f"API error: {error}")
    except Exception as error:
        # Handle unexpected errors
        print(f"Unexpected error: {error}")
    ```
    """

    def __init__(self, api_key: str, base_url: str = "http://localhost:3001", timeout: int = 10):
        """
        Creates a new instance of the FlagVault SDK.

        Args:
            api_key: API Key for authenticating with the FlagVault service.
                    Can be obtained from your FlagVault dashboard.
                    Environment is automatically determined from the key prefix (live_ = production, test_ = test).
            base_url: Base URL for the FlagVault API. Defaults to localhost for development.
            timeout: Request timeout in seconds. Defaults to 10.

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError("API Key is required to initialize the SDK.")

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.timeout = timeout
        
        # Environment is determined by the backend from API key prefix
        # live_ = production, test_ = test
        if api_key.startswith('live_'):
            self.environment = 'production'
        elif api_key.startswith('test_'):
            self.environment = 'test'
        else:
            self.environment = 'production'  # Default fallback

    def is_enabled(self, flag_key: str, default_value: bool = False) -> bool:
        """
        Checks if a feature flag is enabled.

        Args:
            flag_key: The key for the feature flag
            default_value: Default value to return if flag cannot be retrieved or on error

        Returns:
            A boolean indicating if the feature is enabled, or default_value on error

        Raises:
            ValueError: If flag_key is not provided
        """
        if not flag_key:
            raise ValueError("flag_key is required to check if a feature is enabled.")

        url = f"{self.base_url}/api/feature-flag/{flag_key}/enabled"

        headers = {
            "X-API-Key": self.api_key,
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            # Handle authentication errors - log but return default
            if response.status_code == 401:
                print(f"FlagVault: Invalid API credentials for flag '{flag_key}', using default: {default_value}")
                return default_value
            elif response.status_code == 403:
                print(f"FlagVault: Access forbidden for flag '{flag_key}', using default: {default_value}")
                return default_value
            elif response.status_code == 404:
                print(f"FlagVault: Flag '{flag_key}' not found, using default: {default_value}")
                return default_value
            
            # Handle other HTTP errors - log but return default
            if not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"HTTP {response.status_code}")
                except (json.JSONDecodeError, ValueError):
                    error_message = f"HTTP {response.status_code}: {response.text[:100]}"
                print(f"FlagVault: API error for flag '{flag_key}': {error_message}, using default: {default_value}")
                return default_value

            # Parse response
            try:
                data = response.json()
                return data.get("enabled", default_value)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"FlagVault: Invalid JSON response for flag '{flag_key}': {e}, using default: {default_value}")
                return default_value
            
        except requests.exceptions.Timeout:
            print(f"FlagVault: Request timed out for flag '{flag_key}' after {self.timeout} seconds, using default: {default_value}")
            return default_value
        except requests.exceptions.ConnectionError:
            print(f"FlagVault: Failed to connect to API for flag '{flag_key}', using default: {default_value}")
            return default_value
        except requests.exceptions.RequestException as e:
            print(f"FlagVault: Network error for flag '{flag_key}': {e}, using default: {default_value}")
            return default_value
        except Exception as e:
            print(f"FlagVault: Unexpected error for flag '{flag_key}': {e}, using default: {default_value}")
            return default_value