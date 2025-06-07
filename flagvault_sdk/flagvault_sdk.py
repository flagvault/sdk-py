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
    is_enabled = sdk.is_enabled("my-feature-flag")
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

    def __init__(self, api_key: str, timeout: int = 10, _base_url: str = "https://api.flagvault.com"):
        """
        Creates a new instance of the FlagVault SDK.

        Args:
            api_key: API Key for authenticating with the FlagVault service.
                    Can be obtained from your FlagVault dashboard.
                    Environment is automatically determined from the key prefix (live_ = production, test_ = test).
            timeout: Request timeout in seconds. Defaults to 10.

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError("API Key is required to initialize the SDK.")

        self.api_key = api_key
        self._base_url = _base_url
        self.timeout = timeout

    def is_enabled(self, flag_key: str) -> bool:
        """
        Checks if a feature flag is enabled.

        Args:
            flag_key: The key for the feature flag

        Returns:
            A boolean indicating if the feature is enabled

        Raises:
            ValueError: If flag_key is not provided
            FlagVaultAuthenticationError: If authentication fails
            FlagVaultNetworkError: If the network request fails
            FlagVaultAPIError: If the API returns an error
        """
        if not flag_key:
            raise ValueError("flag_key is required to check if a feature is enabled.")

        url = f"{self._base_url}/api/feature-flag/{flag_key}/enabled"

        headers = {
            "X-API-Key": self.api_key,
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            # Handle authentication errors
            if response.status_code == 401:
                raise FlagVaultAuthenticationError("Invalid API credentials")
            elif response.status_code == 403:
                raise FlagVaultAuthenticationError("Access forbidden - check your API credentials")
            
            # Handle other HTTP errors
            if not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"HTTP {response.status_code}")
                except (json.JSONDecodeError, ValueError):
                    error_message = f"HTTP {response.status_code}: {response.text[:100]}"
                raise FlagVaultAPIError(f"API request failed: {error_message}")

            # Parse response
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError) as e:
                raise FlagVaultAPIError(f"Invalid JSON response: {e}")
            
            return data.get("enabled", False)
            
        except requests.exceptions.Timeout:
            raise FlagVaultNetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise FlagVaultNetworkError("Failed to connect to FlagVault API")
        except requests.exceptions.RequestException as e:
            raise FlagVaultNetworkError(f"Network error: {e}")