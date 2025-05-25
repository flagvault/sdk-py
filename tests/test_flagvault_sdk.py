import pytest
import requests
import requests_mock
from flagvault_sdk import (
    FlagVaultSDK,
    FlagVaultError,
    FlagVaultAuthenticationError,
    FlagVaultNetworkError,
    FlagVaultAPIError,
)

BASE_URL = "https://api.flagvault.com"

class TestFlagVaultSDK:
    def test_initialization_with_valid_config(self):
        """Should initialize correctly with valid config"""
        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")
        assert sdk is not None
        assert sdk.api_key == "test-api-key"
        assert sdk.api_secret == "test-api-secret"
        assert sdk.base_url == BASE_URL
        assert sdk.timeout == 10

    def test_initialization_with_custom_config(self):
        """Should initialize correctly with custom config"""
        sdk = FlagVaultSDK(
            api_key="test-api-key",
            api_secret="test-api-secret",
            base_url="https://custom.api.com",
            timeout=5
        )
        assert sdk.api_key == "test-api-key"
        assert sdk.api_secret == "test-api-secret"
        assert sdk.base_url == "https://custom.api.com"
        assert sdk.timeout == 5

    def test_initialization_without_api_key_or_secret(self):
        """Should throw an error if initialized without API key or secret"""
        with pytest.raises(ValueError, match="API Key and Secret are required to initialize the SDK."):
            FlagVaultSDK(api_key="", api_secret="")

    def test_is_enabled_returns_true(self, requests_mock):
        """Should return true if the feature flag is enabled"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"enabled": True}
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is True
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == f"{BASE_URL}/feature-flag/test-flag-key/enabled"
        assert requests_mock.last_request.headers["X-API-Key"] == "test-api-key"
        assert requests_mock.last_request.headers["X-API-Secret"] == "test-api-secret"

    def test_is_enabled_returns_false(self, requests_mock):
        """Should return false if the feature flag is disabled"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"enabled": False}
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is False

    def test_is_enabled_with_missing_flag_key(self):
        """Should throw an error if flagKey is missing"""
        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(ValueError, match="flag_key is required to check if a feature is enabled."):
            sdk.is_enabled("")

    def test_is_enabled_with_401_authentication_error(self, requests_mock):
        """Should throw FlagVaultAuthenticationError for 401 responses"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=401
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultAuthenticationError, match="Invalid API credentials"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_403_authentication_error(self, requests_mock):
        """Should throw FlagVaultAuthenticationError for 403 responses"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=403
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultAuthenticationError, match="Access forbidden - check your API credentials"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_api_error(self, requests_mock):
        """Should throw FlagVaultAPIError for other HTTP errors"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=500,
            json={"message": "Internal Server Error"}
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultAPIError, match="API request failed: Internal Server Error"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_http_error_invalid_json(self, requests_mock):
        """Should throw FlagVaultAPIError when HTTP error response has invalid JSON"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=500,
            text="<html>Internal Server Error</html>"
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultAPIError, match="API request failed: HTTP 500: <html>Internal Server Error</html>"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_network_error(self, requests_mock):
        """Should throw FlagVaultNetworkError when the request fails"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.ConnectionError("Network error")
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultNetworkError, match="Failed to connect to FlagVault API"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_timeout_error(self, requests_mock):
        """Should throw FlagVaultNetworkError when request times out"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.Timeout("Request timed out")
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultNetworkError, match="Request timed out after 10 seconds"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_invalid_json_response(self, requests_mock):
        """Should throw FlagVaultAPIError when response is not valid JSON"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            text="invalid json"
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultAPIError, match="Invalid JSON response"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_generic_request_exception(self, requests_mock):
        """Should throw FlagVaultNetworkError for generic RequestException"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.RequestException("Generic request error")
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(FlagVaultNetworkError, match="Network error: Generic request error"):
            sdk.is_enabled("test-flag-key")

    def test_is_enabled_with_missing_enabled_field(self, requests_mock):
        """Should return False when enabled field is missing from response"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"other_field": "value"}
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is False

    def test_is_enabled_with_none_flag_key(self):
        """Should throw ValueError when flag_key is None"""
        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")

        with pytest.raises(ValueError, match="flag_key is required to check if a feature is enabled."):
            sdk.is_enabled(None)

    def test_is_enabled_with_special_characters_in_flag_key(self, requests_mock):
        """Should handle flag keys with special characters"""
        flag_key = "test-flag_key.with$pecial@chars"
        requests_mock.get(
            f"{BASE_URL}/feature-flag/{flag_key}/enabled",
            json={"enabled": True}
        )

        sdk = FlagVaultSDK(api_key="test-api-key", api_secret="test-api-secret")
        is_enabled = sdk.is_enabled(flag_key)

        assert is_enabled is True