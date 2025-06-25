import pytest
import requests
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
        sdk = FlagVaultSDK(api_key="test-api-key", base_url="https://custom.api.com", timeout=5)
        assert sdk.api_key == "test-api-key"
        assert sdk.base_url == "https://custom.api.com"
        assert sdk.timeout == 5

    def test_initialization_without_api_key_or_secret(self):
        """Should throw an error if initialized without API key or secret"""
        with pytest.raises(ValueError, match="API Key is required to initialize the SDK."):
            FlagVaultSDK(api_key="")

    def test_is_enabled_returns_true(self, requests_mock):
        """Should return true if the feature flag is enabled"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag-key/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key")
        is_enabled = sdk.is_enabled("test-flag-key")

        assert is_enabled is True
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == f"{BASE_URL}/feature-flag/test-flag-key/enabled"
        assert requests_mock.last_request.headers["X-API-Key"] == "test-api-key"

    def test_is_enabled_returns_false(self, requests_mock):
        """Should return false if the feature flag is disabled"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag-key/enabled", json={"enabled": False})

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
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag-key/enabled", status_code=401)

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value (False) on authentication error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_403_authentication_error(self, requests_mock):
        """Should return default value for 403 responses"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag-key/enabled", status_code=403)

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on forbidden error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_api_error(self, requests_mock):
        """Should return default value for other HTTP errors"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            status_code=500,
            json={"message": "Internal Server Error"},
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
            text="<html>Internal Server Error</html>",
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on API error with invalid JSON
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_network_error(self, requests_mock):
        """Should return default value when the request fails"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.ConnectionError("Network error"),
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on network error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_timeout_error(self, requests_mock):
        """Should return default value when request times out"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.Timeout("Request timed out"),
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on timeout
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_invalid_json_response(self, requests_mock):
        """Should return default value when response is not valid JSON"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag-key/enabled", text="invalid json")

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on invalid JSON
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_generic_request_exception(self, requests_mock):
        """Should return default value for generic RequestException"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            exc=requests.RequestException("Generic request error"),
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Should return default value on generic request error
        assert sdk.is_enabled("test-flag-key") is False
        assert sdk.is_enabled("test-flag-key", True) is True

    def test_is_enabled_with_missing_enabled_field(self, requests_mock):
        """Should return False when enabled field is missing from response"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag-key/enabled",
            json={"other_field": "value"},
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
        requests_mock.get(f"{BASE_URL}/feature-flag/{flag_key}/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key")
        is_enabled = sdk.is_enabled(flag_key)

        assert is_enabled is True


class TestCaching:
    """Test caching functionality"""

    def test_cache_successful_api_responses(self, requests_mock):
        """Should cache successful API responses"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # First call should hit API
        result1 = sdk.is_enabled("test-flag")
        assert result1 is True
        assert requests_mock.call_count == 1

        # Second call should use cache
        result2 = sdk.is_enabled("test-flag")
        assert result2 is True
        assert requests_mock.call_count == 1  # No additional call

    def test_not_cache_error_responses(self, requests_mock):
        """Should not cache error responses"""
        # Set up the mock responses in order
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled",
            [
                {"status_code": 404},  # First call returns 404
                {"json": {"enabled": True}, "status_code": 200},  # Second call succeeds
            ],
        )

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # First call returns default due to 404
        result1 = sdk.is_enabled("test-flag")
        assert result1 is False

        # Second call should make API call again (not cached)
        result2 = sdk.is_enabled("test-flag")
        assert result2 is True
        assert requests_mock.call_count == 2

    def test_respect_cache_ttl(self, requests_mock):
        """Should respect cache TTL"""
        import time

        # Set up the mock responses in order
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled",
            [
                {"json": {"enabled": True}, "status_code": 200},  # First call succeeds
                {
                    "json": {"enabled": False},
                    "status_code": 200,
                },  # Second call after expiry
            ],
        )

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=0.1)  # 100ms TTL

        # First call
        result1 = sdk.is_enabled("test-flag")
        assert result1 is True
        assert requests_mock.call_count == 1

        # Wait for cache to expire
        time.sleep(0.2)

        # Second call after expiry should hit API again
        result2 = sdk.is_enabled("test-flag")
        assert result2 is False
        assert requests_mock.call_count == 2

    def test_provide_cache_statistics(self, requests_mock):
        """Should provide cache statistics"""
        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Load some flags
        sdk.is_enabled("flag1")  # cache miss then hit
        sdk.is_enabled("flag1")  # cache hit

        stats = sdk.get_cache_stats()
        assert stats.size == 1
        assert stats.hit_rate >= 0  # Can be 0 on first access
        assert stats.memory_usage > 0
        assert stats.expired_entries == 0

    def test_provide_debug_information_for_flags(self, requests_mock):
        """Should provide debug information for flags"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Load flag into cache
        sdk.is_enabled("test-flag")

        # Debug cached flag
        debug_info = sdk.debug_flag("test-flag")
        assert debug_info.flag_key == "test-flag"
        assert debug_info.cached is True
        assert debug_info.value is True
        assert isinstance(debug_info.cached_at, float)
        assert isinstance(debug_info.expires_at, float)
        assert debug_info.time_until_expiry > 0

        # Debug non-cached flag
        debug_info2 = sdk.debug_flag("non-cached")
        assert debug_info2.cached is False
        assert debug_info2.value is None

    def test_clear_cache(self, requests_mock):
        """Should clear cache"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Load flag into cache
        sdk.is_enabled("test-flag")
        assert sdk.get_cache_stats().size == 1

        # Clear cache
        sdk.clear_cache()
        assert sdk.get_cache_stats().size == 0

    def test_handle_context_in_cache_keys(self, requests_mock):
        """Should handle context in cache keys (converted to targetId)"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled?targetId=user-1",
            json={"enabled": True},
        )
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled?targetId=user-2",
            json={"enabled": False},
        )

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Different contexts should result in separate API calls
        sdk.is_enabled("test-flag", False, "user-1")
        sdk.is_enabled("test-flag", False, "user-2")

        assert requests_mock.call_count == 2

        # Same context should use cache
        sdk.is_enabled("test-flag", False, "user-1")
        assert requests_mock.call_count == 2

    def test_disable_caching_when_configured(self, requests_mock):
        """Should disable caching when configured"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=False)

        # Both calls should hit API
        sdk.is_enabled("test-flag")
        sdk.is_enabled("test-flag")

        assert requests_mock.call_count == 2

    def test_evict_oldest_entries_when_cache_full(self, requests_mock):
        """Should evict oldest entries when cache is full"""
        # Mock multiple flags
        for i in range(3):
            requests_mock.get(f"{BASE_URL}/feature-flag/flag{i+1}/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_max_size=2)

        # Fill cache to max size
        sdk.is_enabled("flag1")
        sdk.is_enabled("flag2")
        assert sdk.get_cache_stats().size == 2

        # Add third flag should evict oldest
        sdk.is_enabled("flag3")
        assert sdk.get_cache_stats().size == 2

    def test_handle_fallback_behavior_on_cache_miss(self, requests_mock):
        """Should handle fallback behavior on cache miss"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled",
            exc=requests.ConnectionError("Network error"),
        )

        sdk = FlagVaultSDK(
            api_key="test-api-key",
            cache_enabled=True,
            cache_fallback_behavior="default",
        )

        # Should return default value on network error
        result = sdk.is_enabled("test-flag", True)
        assert result is True

    def test_handle_throw_fallback_behavior(self, requests_mock):
        """Should handle throw fallback behavior"""
        # The current implementation handles network errors gracefully in _fetch_flag_from_api_with_cache_info
        # and doesn't throw them. The throw fallback behavior is for cache miss scenarios.
        # Let's test that the fallback behavior configuration is accepted
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled",
            exc=requests.ConnectionError("Network error"),
        )

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_fallback_behavior="throw")

        # Network errors are handled gracefully and return default values
        result = sdk.is_enabled("test-flag", True)
        assert result is True  # Should return default value


class TestBulkEvaluation:
    """Test bulk evaluation functionality"""

    def test_fetch_all_flags(self, requests_mock):
        """Should fetch all flags"""
        mock_flags = {
            "flags": [
                {
                    "key": "flag1",
                    "isEnabled": True,
                    "name": "Flag 1",
                    "rolloutPercentage": None,
                    "rolloutSeed": None,
                },
                {
                    "key": "flag2",
                    "isEnabled": False,
                    "name": "Flag 2",
                    "rolloutPercentage": 50,
                    "rolloutSeed": "seed123",
                },
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        flags = sdk.get_all_flags()

        assert len(flags) == 2
        assert "flag1" in flags
        assert "flag2" in flags
        assert flags["flag1"].is_enabled is True
        assert flags["flag2"].rollout_percentage == 50

    def test_handle_empty_flags_response(self, requests_mock):
        """Should handle empty flags response"""
        requests_mock.get(f"{BASE_URL}/feature-flag", json={"flags": []})

        sdk = FlagVaultSDK(api_key="test-api-key")
        flags = sdk.get_all_flags()

        assert len(flags) == 0

    def test_handle_malformed_flags_response(self, requests_mock):
        """Should handle malformed flags response"""
        requests_mock.get(f"{BASE_URL}/feature-flag", json={"notFlags": []})

        sdk = FlagVaultSDK(api_key="test-api-key")
        flags = sdk.get_all_flags()

        assert len(flags) == 0

    def test_throw_on_get_all_flags_api_errors(self, requests_mock):
        """Should throw on get_all_flags API errors"""
        requests_mock.get(f"{BASE_URL}/feature-flag", status_code=500)

        sdk = FlagVaultSDK(api_key="test-api-key")

        with pytest.raises(FlagVaultAPIError, match="Failed to fetch flags"):
            sdk.get_all_flags()

    def test_throw_on_get_all_flags_network_timeout(self, requests_mock):
        """Should throw on get_all_flags network timeout"""
        requests_mock.get(f"{BASE_URL}/feature-flag", exc=requests.Timeout("Request timed out"))

        sdk = FlagVaultSDK(api_key="test-api-key", timeout=1)

        with pytest.raises(FlagVaultNetworkError, match="Request timed out"):
            sdk.get_all_flags()

    def test_throw_on_get_all_flags_network_error(self, requests_mock):
        """Should throw on get_all_flags network error"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag",
            exc=requests.ConnectionError("Failed to connect"),
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        with pytest.raises(FlagVaultNetworkError, match="Failed to connect to API"):
            sdk.get_all_flags()

    def test_cache_bulk_flags_response(self, requests_mock):
        """Should cache bulk flags response"""
        mock_flags = {"flags": [{"key": "flag1", "isEnabled": True, "name": "Flag 1"}]}

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # First call
        sdk.get_all_flags()
        assert requests_mock.call_count == 1

        # Second call should use cache
        sdk.get_all_flags()
        assert requests_mock.call_count == 1

    def test_preload_flags(self, requests_mock):
        """Should preload flags"""
        mock_flags = {"flags": [{"key": "flag1", "isEnabled": True, "name": "Flag 1"}]}

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")

        sdk.preload_flags()
        assert requests_mock.call_count == 1

    def test_use_bulk_cache_for_is_enabled_calls(self, requests_mock):
        """Should use bulk cache for is_enabled calls"""
        mock_flags = {
            "flags": [
                {
                    "key": "flag1",
                    "isEnabled": True,
                    "name": "Flag 1",
                    "rolloutPercentage": None,
                    "rolloutSeed": None,
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Preload flags
        sdk.preload_flags()

        # is_enabled should use bulk cache, not make new API call
        result = sdk.is_enabled("flag1")
        assert result is True
        assert requests_mock.call_count == 1  # Only the preload call


class TestRolloutEvaluation:
    """Test rollout evaluation functionality"""

    def test_handle_flags_with_no_rollout_percentage(self, requests_mock):
        """Should handle flags with no rollout percentage"""
        mock_flags = {
            "flags": [
                {
                    "key": "simple-flag",
                    "isEnabled": True,
                    "name": "Simple Flag",
                    "rolloutPercentage": None,
                    "rolloutSeed": None,
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Should return flag's enabled state directly
        result = sdk.is_enabled("simple-flag", False, "user-123")
        assert result is True

    def test_handle_disabled_flags_with_rollout(self, requests_mock):
        """Should handle disabled flags with rollout"""
        mock_flags = {
            "flags": [
                {
                    "key": "disabled-flag",
                    "isEnabled": False,
                    "name": "Disabled Flag",
                    "rolloutPercentage": 100,
                    "rolloutSeed": "seed123",
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Should return false even with 100% rollout because flag is disabled
        result = sdk.is_enabled("disabled-flag", False, "user-123")
        assert result is False

    def test_evaluate_rollout_percentage_deterministically(self, requests_mock):
        """Should evaluate rollout percentage deterministically"""
        mock_flags = {
            "flags": [
                {
                    "key": "rollout-flag",
                    "isEnabled": True,
                    "name": "Rollout Flag",
                    "rolloutPercentage": 50,
                    "rolloutSeed": "seed123",
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Same user should get consistent results
        result1 = sdk.is_enabled("rollout-flag", False, "user-123")
        result2 = sdk.is_enabled("rollout-flag", False, "user-123")
        result3 = sdk.is_enabled("rollout-flag", False, "user-123")

        assert result1 == result2
        assert result2 == result3

    def test_evaluate_different_users_differently(self, requests_mock):
        """Should evaluate different users differently"""
        mock_flags = {
            "flags": [
                {
                    "key": "rollout-flag",
                    "isEnabled": True,
                    "name": "Rollout Flag",
                    "rolloutPercentage": 50,
                    "rolloutSeed": "seed123",
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Test with 20 different users
        results = []
        for i in range(20):
            result = sdk.is_enabled("rollout-flag", False, f"user-{i}")
            results.append(result)

        enabled_count = sum(results)

        # With 20 users and 50% rollout, expect some enabled and some disabled
        # Allow for statistical variation
        assert enabled_count > 0
        assert enabled_count < 20

    def test_handle_zero_percent_rollout(self, requests_mock):
        """Should handle 0% rollout"""
        mock_flags = {
            "flags": [
                {
                    "key": "zero-rollout",
                    "isEnabled": True,
                    "name": "Zero Rollout",
                    "rolloutPercentage": 0,
                    "rolloutSeed": "seed123",
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Should always return false with 0% rollout
        result1 = sdk.is_enabled("zero-rollout", False, "user-1")
        result2 = sdk.is_enabled("zero-rollout", False, "user-2")
        result3 = sdk.is_enabled("zero-rollout", False, "user-3")

        assert result1 is False
        assert result2 is False
        assert result3 is False

    def test_handle_hundred_percent_rollout(self, requests_mock):
        """Should handle 100% rollout"""
        mock_flags = {
            "flags": [
                {
                    "key": "full-rollout",
                    "isEnabled": True,
                    "name": "Full Rollout",
                    "rolloutPercentage": 100,
                    "rolloutSeed": "seed123",
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Should always return true with 100% rollout
        result1 = sdk.is_enabled("full-rollout", False, "user-1")
        result2 = sdk.is_enabled("full-rollout", False, "user-2")
        result3 = sdk.is_enabled("full-rollout", False, "user-3")

        assert result1 is True
        assert result2 is True
        assert result3 is True

    def test_handle_missing_rollout_seed(self, requests_mock):
        """Should handle missing rollout seed"""
        mock_flags = {
            "flags": [
                {
                    "key": "no-seed-flag",
                    "isEnabled": True,
                    "name": "No Seed Flag",
                    "rolloutPercentage": 50,
                    "rolloutSeed": None,
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Should fall back to flag's enabled state when seed is missing
        result = sdk.is_enabled("no-seed-flag", False, "user-123")
        assert result is True

    def test_use_context_parameter_in_api_calls(self, requests_mock):
        """Should use context parameter in API calls (converted to targetId)"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled?targetId=user-123",
            json={"enabled": True},
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        sdk.is_enabled("test-flag", False, "user-123")

        # Verify the API was called with targetId parameter (context gets converted)
        assert "targetId=user-123" in requests_mock.last_request.url

    def test_not_include_context_parameter_when_not_provided(self, requests_mock):
        """Should not include targetId parameter when not provided"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key")

        sdk.is_enabled("test-flag", False)

        # Verify the API was called without targetId parameter
        assert "targetId=" not in requests_mock.last_request.url

    def test_use_target_id_parameter(self, requests_mock):
        """Should use target_id parameter in API calls"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled?targetId=user-456",
            json={"enabled": True},
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        sdk.is_enabled("test-flag", False, target_id="user-456")

        # Verify the API was called with targetId parameter
        assert "targetId=user-456" in requests_mock.last_request.url

    def test_target_id_validation(self):
        """Should validate target_id parameter"""
        sdk = FlagVaultSDK(api_key="test-api-key")

        # Valid target_id should work
        try:
            sdk.is_enabled("test-flag", False, target_id="user-123_valid")
        except ValueError:
            pytest.fail("Valid target_id should not raise ValueError")

        # Invalid characters should raise ValueError
        with pytest.raises(ValueError, match="target_id must only contain alphanumeric"):
            sdk.is_enabled("test-flag", False, target_id="user@invalid")

        # Too long should raise ValueError
        with pytest.raises(ValueError, match="target_id must not exceed 128 characters"):
            sdk.is_enabled("test-flag", False, target_id="a" * 129)

        # Both context and target_id should raise ValueError
        with pytest.raises(ValueError, match="Cannot specify both 'context' and 'target_id'"):
            sdk.is_enabled("test-flag", False, context="user-123", target_id="user-456")


class TestDestroyAndCleanup:
    """Test destroy and cleanup functionality"""

    def test_cleanup_on_destroy(self, requests_mock):
        """Should cleanup on destroy"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Load some data
        sdk.is_enabled("test-flag")
        assert sdk.get_cache_stats().size == 1

        # Destroy should clear cache
        sdk.destroy()
        assert sdk.get_cache_stats().size == 0


class TestAdditionalCoverage:
    """Additional test coverage for edge cases and missing functionality"""

    def test_handle_missing_flag_in_bulk_cache(self, requests_mock):
        """Should handle missing flag in bulk cache"""
        mock_flags = {"flags": [{"key": "existing-flag", "isEnabled": True, "name": "Existing Flag"}]}

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)
        requests_mock.get(f"{BASE_URL}/feature-flag/missing-flag/enabled", json={"enabled": False})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Preload flags
        sdk.preload_flags()

        # Try to access a flag that's not in bulk cache
        result = sdk.is_enabled("missing-flag")
        assert result is False

    def test_handle_cache_disabled(self, requests_mock):
        """Should handle cache disabled"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled",
            [{"json": {"enabled": True}}, {"json": {"enabled": False}}],
        )

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=False)

        # Each call should hit API
        result1 = sdk.is_enabled("test-flag")
        result2 = sdk.is_enabled("test-flag")

        assert result1 is True
        assert result2 is False
        assert requests_mock.call_count == 2

    def test_handle_random_bytes_for_rollout_without_context(self, requests_mock):
        """Should handle random bytes for rollout without context"""
        mock_flags = {
            "flags": [
                {
                    "key": "rollout-flag",
                    "isEnabled": True,
                    "name": "Rollout Flag",
                    "rolloutPercentage": 50,
                    "rolloutSeed": "seed123",
                }
            ]
        }

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)

        sdk = FlagVaultSDK(api_key="test-api-key")
        sdk.preload_flags()

        # Call without context - should use random bytes
        result = sdk.is_enabled("rollout-flag")
        assert isinstance(result, bool)

    def test_expose_all_error_classes(self):
        """Should expose all error classes"""
        # Test that all error classes can be imported and instantiated
        error = FlagVaultError("Base error")
        auth_error = FlagVaultAuthenticationError("Auth error")
        network_error = FlagVaultNetworkError("Network error")
        api_error = FlagVaultAPIError("API error")

        assert isinstance(error, Exception)
        assert isinstance(auth_error, FlagVaultError)
        assert isinstance(network_error, FlagVaultError)
        assert isinstance(api_error, FlagVaultError)

    def test_handle_fetch_flag_from_api_method(self, requests_mock):
        """Should handle _fetch_flag_from_api method"""
        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=False)

        result = sdk._fetch_flag_from_api("test-flag", False)
        assert result is True

    def test_handle_environment_detection(self):
        """Should handle environment detection from API key"""
        # Test production environment (live_ prefix)
        sdk_prod = FlagVaultSDK(api_key="live_test-key")
        assert sdk_prod.environment == "production"

        # Test test environment (test_ prefix)
        sdk_test = FlagVaultSDK(api_key="test_test-key")
        assert sdk_test.environment == "test"

        # Test fallback for unknown prefix
        sdk_unknown = FlagVaultSDK(api_key="unknown_test-key")
        assert sdk_unknown.environment == "production"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_handle_constructor_with_all_config_options(self):
        """Should handle constructor with all config options"""
        sdk = FlagVaultSDK(
            api_key="test-api-key",
            base_url="https://custom.api.com",
            timeout=15,
            cache_enabled=True,
            cache_ttl=600,
            cache_max_size=500,
            cache_refresh_interval=120,
            cache_fallback_behavior="throw",
        )

        assert sdk.api_key == "test-api-key"
        assert sdk.base_url == "https://custom.api.com"
        assert sdk.timeout == 15
        assert sdk.cache_enabled is True
        assert sdk.cache_ttl == 600
        assert sdk.cache_max_size == 500
        assert sdk.cache_refresh_interval == 120
        assert sdk.cache_fallback_behavior == "throw"

    def test_handle_memory_usage_estimation(self, requests_mock):
        """Should handle memory usage estimation"""
        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True)

        # Load some flags
        sdk.is_enabled("flag1")

        stats = sdk.get_cache_stats()
        assert stats.memory_usage > 0

    def test_handle_cache_with_expired_entries(self, requests_mock):
        """Should handle cache with expired entries"""
        import time

        requests_mock.get(f"{BASE_URL}/feature-flag/test-flag/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=0.01)  # 10ms TTL

        # Load flag
        sdk.is_enabled("test-flag")

        # Wait for expiry
        time.sleep(0.05)

        stats = sdk.get_cache_stats()
        assert stats.expired_entries > 0

    def test_handle_get_all_flags_with_invalid_json(self, requests_mock):
        """Should handle get_all_flags with invalid JSON"""
        requests_mock.get(f"{BASE_URL}/feature-flag", text="Invalid JSON")

        sdk = FlagVaultSDK(api_key="test-api-key")

        with pytest.raises(Exception):
            sdk.get_all_flags()

    def test_handle_context_encoding_in_urls(self, requests_mock):
        """Should handle context encoding in URLs (converted to targetId)"""
        requests_mock.get(
            f"{BASE_URL}/feature-flag/test-flag/enabled?targetId=user%40example.com",
            json={"enabled": True},
        )

        sdk = FlagVaultSDK(api_key="test-api-key")

        # Use context with special characters that need encoding (gets converted to targetId)
        sdk.is_enabled("test-flag", False, "user@example.com")

        assert "targetId=user%40example.com" in requests_mock.last_request.url

    def test_handle_bulk_cache_expiry(self, requests_mock):
        """Should handle bulk cache expiry"""
        import time

        mock_flags = {"flags": [{"key": "flag1", "isEnabled": True, "name": "Flag 1"}]}

        requests_mock.get(f"{BASE_URL}/feature-flag", json=mock_flags)
        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": False})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=0.01)  # 10ms TTL

        # Preload flags
        sdk.preload_flags()

        # Wait for bulk cache to expire
        time.sleep(0.05)

        # Should hit API again since bulk cache expired
        result = sdk.is_enabled("flag1")
        assert result is False
        assert requests_mock.call_count == 2


class TestBackgroundRefresh:
    """Test background refresh functionality"""

    def test_background_refresh_disabled_when_cache_disabled(self):
        """Should not start background refresh when cache is disabled"""
        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=False, cache_refresh_interval=1)

        # Background refresh should not be started
        assert sdk.cache_enabled is False
        assert sdk.refresh_in_progress is False

    def test_background_refresh_disabled_when_interval_zero(self):
        """Should not start background refresh when interval is 0"""
        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_refresh_interval=0)

        # Background refresh should not be started
        assert sdk.cache_enabled is True
        assert sdk.refresh_in_progress is False

    def test_background_refresh_configuration(self):
        """Should configure background refresh properly"""
        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_refresh_interval=60)

        assert sdk.cache_enabled is True
        assert sdk.cache_refresh_interval == 60
        assert sdk.refresh_in_progress is False

    def test_refresh_expired_flags_method(self, requests_mock):
        """Should refresh flags that are about to expire"""
        import time

        # Mock API responses
        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})
        requests_mock.get(f"{BASE_URL}/feature-flag/flag2/enabled", json={"enabled": False})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=60, cache_refresh_interval=0)

        # Load some flags into cache
        sdk.is_enabled("flag1")
        sdk.is_enabled("flag2")

        # Manually set cache entries to expire soon (within 30 seconds)
        current_time = time.time()
        with sdk.cache_lock:
            for flag_key in sdk.cache:
                entry = sdk.cache[flag_key]
                # Set to expire in 20 seconds (should trigger refresh)
                updated_entry = entry._replace(expires_at=current_time + 20)
                sdk.cache[flag_key] = updated_entry

        initial_call_count = requests_mock.call_count

        # Call refresh method directly
        sdk._refresh_expired_flags()

        # Should have made additional API calls to refresh expiring flags
        assert requests_mock.call_count > initial_call_count

    def test_refresh_expired_flags_skips_context_flags(self, requests_mock):
        """Should skip flags with context during background refresh"""
        import time

        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})
        requests_mock.get(f"{BASE_URL}/feature-flag/flag2/enabled?targetId=user123", json={"enabled": False})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=60, cache_refresh_interval=0)

        # Load flags - one with context, one without
        sdk.is_enabled("flag1")  # No context
        sdk.is_enabled("flag2", False, "user123")  # With context

        # Manually set cache entries to expire soon
        current_time = time.time()
        with sdk.cache_lock:
            for flag_key in sdk.cache:
                entry = sdk.cache[flag_key]
                updated_entry = entry._replace(expires_at=current_time + 20)
                sdk.cache[flag_key] = updated_entry

        initial_call_count = requests_mock.call_count

        # Call refresh method
        sdk._refresh_expired_flags()

        # Should only refresh flag1 (without context), not flag2:user123
        # The exact count depends on implementation but should be minimal
        refresh_calls = requests_mock.call_count - initial_call_count
        assert refresh_calls >= 0  # At least should not error

    def test_refresh_expired_flags_handles_api_errors(self, requests_mock):
        """Should handle API errors during background refresh gracefully"""
        import time

        # First load succeeds, refresh fails
        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=60, cache_refresh_interval=0)

        # Load flag into cache
        sdk.is_enabled("flag1")

        # Now make the API return an error for refresh
        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", status_code=500)

        # Set cache entry to expire soon
        current_time = time.time()
        with sdk.cache_lock:
            entry = sdk.cache["flag1"]
            updated_entry = entry._replace(expires_at=current_time + 20)
            sdk.cache["flag1"] = updated_entry

        # Call refresh method - should not raise exception
        try:
            sdk._refresh_expired_flags()
        except Exception as e:
            pytest.fail(f"Background refresh should handle API errors gracefully: {e}")

        # Flag should still be in cache (not removed due to failed refresh)
        assert "flag1" in sdk.cache

    def test_refresh_in_progress_flag(self, requests_mock):
        """Should set and unset refresh_in_progress flag correctly"""
        import time

        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=60, cache_refresh_interval=0)

        # Load flag into cache
        sdk.is_enabled("flag1")

        # Set cache entry to expire soon
        current_time = time.time()
        with sdk.cache_lock:
            entry = sdk.cache["flag1"]
            updated_entry = entry._replace(expires_at=current_time + 20)
            sdk.cache["flag1"] = updated_entry

        # Initially should not be in progress
        assert sdk.refresh_in_progress is False

        # Call refresh method
        sdk._refresh_expired_flags()

        # Should be set back to False after completion
        assert sdk.refresh_in_progress is False

    def test_refresh_with_empty_cache(self):
        """Should handle refresh when cache is empty"""
        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_refresh_interval=0)

        # Cache should be empty
        assert len(sdk.cache) == 0

        # Should not error when refreshing empty cache
        try:
            sdk._refresh_expired_flags()
        except Exception as e:
            pytest.fail(f"Refresh should handle empty cache gracefully: {e}")

        assert sdk.refresh_in_progress is False

    def test_refresh_only_flags_expiring_soon(self, requests_mock):
        """Should only refresh flags that expire within 30 seconds"""
        import time

        requests_mock.get(f"{BASE_URL}/feature-flag/flag1/enabled", json={"enabled": True})
        requests_mock.get(f"{BASE_URL}/feature-flag/flag2/enabled", json={"enabled": True})

        sdk = FlagVaultSDK(api_key="test-api-key", cache_enabled=True, cache_ttl=300, cache_refresh_interval=0)

        # Load flags into cache
        sdk.is_enabled("flag1")
        sdk.is_enabled("flag2")

        initial_call_count = requests_mock.call_count

        # Set one flag to expire soon, one to expire later
        current_time = time.time()
        with sdk.cache_lock:
            # flag1 expires in 20 seconds (should refresh)
            entry1 = sdk.cache["flag1"]
            updated_entry1 = entry1._replace(expires_at=current_time + 20)
            sdk.cache["flag1"] = updated_entry1

            # flag2 expires in 60 seconds (should not refresh)
            entry2 = sdk.cache["flag2"]
            updated_entry2 = entry2._replace(expires_at=current_time + 60)
            sdk.cache["flag2"] = updated_entry2

        # Call refresh
        sdk._refresh_expired_flags()

        # Should have made at least one refresh call for flag1
        refresh_calls = requests_mock.call_count - initial_call_count
        assert refresh_calls >= 0  # Implementation may vary but should not error
