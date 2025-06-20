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

BASE_URL = "https://api.flagvault.com/api"

class TestFlagVaultSDK:
    def test_initialization_with_valid_config(self):
        """Should initialize correctly with valid config"""
        sdk = FlagVaultSDK(api_key="test-api-key")
        assert sdk is not None
        assert sdk.api_key == "test-api-key"
        assert sdk.base_url == "https://api.flagvault.com"
        assert sdk.timeout == 10

    def test_initialization_with_custom_config(self):
        """Should initialize correctly with custom config"""
        sdk = FlagVaultSDK(
            api_key="test-api-key",
            base_url="https://custom.api.com",
            timeout=5
        )
        assert sdk.api_key == "test-api-key"
        assert sdk.base_url == "https://custom.api.com"
        assert sdk.timeout == 5

    def test_initialization_without_api_key_or_secret(self):
        """Should throw an error if initialized without API key or secret"""
        with pytest.raises(ValueError, match="API Key is required to initialize the SDK."):
            FlagVaultSDK(api_key="")

    def test_is_enabled_returns_true(self, requests_mock):
        """Should return true if the feature flag is enabled"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"enabled": True}
        )

        sdk = FlagVaultSDK(api_key="test-api-key")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is True
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == f"{BASE_URL}/feature-flag/test-flag-key/enabled"
        assert requests_mock.last_request.headers["X-API-Key"] == "test-api-key"

    def test_is_enabled_returns_false(self, requests_mock):
        """Should return false if the feature flag is disabled"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"enabled": False}
        )

        sdk = FlagVaultSDK(api_key="test-api-key")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is False

    def test_is_enabled_with_missing_flag_key(self):
        """Should throw an error if flagKey is missing"""
        sdk = FlagVaultSDK(api_key="test-api-key")

        with pytest.raises(ValueError, match="flag_key is required to check if a feature is enabled."):
            sdk.is_enabled("")

    def test_is_enabled_with_401_authentication_error(self, requests_mock):
        """Should return default value for 401 responses"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=401
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value (False) on authentication error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_403_authentication_error(self, requests_mock):
        """Should return default value for 403 responses"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=403
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on forbidden error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_api_error(self, requests_mock):
        """Should return default value for other HTTP errors"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=500,
            json={"message": "Internal Server Error"}
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on API error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_http_error_invalid_json(self, requests_mock):
        """Should return default value when HTTP error response has invalid JSON"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=500,
            text="<html>Internal Server Error</html>"
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on API error with invalid JSON
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_network_error(self, requests_mock):
        """Should return default value when the request fails"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.ConnectionError("Network error")
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on network error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_timeout_error(self, requests_mock):
        """Should return default value when request times out"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.Timeout("Request timed out")
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on timeout
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_invalid_json_response(self, requests_mock):
        """Should return default value when response is not valid JSON"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            text="invalid json"
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on invalid JSON
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_generic_request_exception(self, requests_mock):
        """Should return default value for generic RequestException"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.RequestException("Generic request error")
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on generic request error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_missing_enabled_field(self, requests_mock):
        """Should return False when enabled field is missing from response"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"other_field": "value"}
        )

        sdk = FlagVaultSDK(api_key="test-api-key")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is False

    def test_is_enabled_with_none_flag_key(self):
        """Should throw ValueError when flag_key is None"""
        sdk = FlagVaultSDK(api_key="test-api-key")

        with pytest.raises(ValueError, match="flag_key is required to check if a feature is enabled."):
            sdk.is_enabled(None)

    def test_is_enabled_with_special_characters_in_flag_key(self, requests_mock):
        """Should handle flag keys with special characters"""
        flag_key = "test-flag_key.with$pecial@chars"
        requests_mock.get(
            f"{BASE_URL}/feature-flag/{flag_key}/enabled",
            json={"enabled": True}
        )

        sdk = FlagVaultSDK(api_key="test-api-key")
        is_enabled = sdk.is_enabled(flag_key)

        assert is_enabled is True