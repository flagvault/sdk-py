import requests
from typing import Dict, Optional, Any, NamedTuple, Tuple
import json
import time
import threading
from collections import OrderedDict
import hashlib
import os


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


class CacheEntry(NamedTuple):
    """Cache entry for storing flag data."""

    value: bool
    cached_at: float
    expires_at: float
    last_accessed: float


class CacheStats(NamedTuple):
    """Cache statistics for monitoring and debugging."""

    size: int
    hit_rate: float
    expired_entries: int
    memory_usage: int


class FlagDebugInfo(NamedTuple):
    """Debug information for a specific flag."""

    flag_key: str
    cached: bool
    value: Optional[bool] = None
    cached_at: Optional[float] = None
    expires_at: Optional[float] = None
    time_until_expiry: Optional[float] = None
    last_accessed: Optional[float] = None


class FeatureFlagMetadata(NamedTuple):
    """Feature flag metadata returned from the API."""

    key: str
    is_enabled: bool
    name: str
    rollout_percentage: Optional[int] = None
    rollout_seed: Optional[str] = None


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

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.flagvault.com",
        timeout: int = 10,
        cache_enabled: bool = True,
        cache_ttl: int = 300,
        cache_max_size: int = 1000,
        cache_refresh_interval: int = 60,
        cache_fallback_behavior: str = "default",
    ):
        """
        Creates a new instance of the FlagVault SDK.

        Args:
            api_key: API Key for authenticating with the FlagVault service.
                    Can be obtained from your FlagVault dashboard.
                    Environment is automatically determined from the key prefix (live_ = production, test_ = test).
            base_url: Base URL for the FlagVault API. Defaults to production URL.
            timeout: Request timeout in seconds. Defaults to 10.
            cache_enabled: Enable or disable caching. Defaults to True.
            cache_ttl: Cache time-to-live in seconds. Defaults to 300 (5 minutes).
            cache_max_size: Maximum number of flags to cache. Defaults to 1000.
            cache_refresh_interval: Background refresh interval in seconds. Defaults to 60.
            cache_fallback_behavior: Fallback behavior when cache fails ('default', 'api', 'throw').
                                     Defaults to 'default'.

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError("API Key is required to initialize the SDK.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")  # Remove trailing slash
        self.timeout = timeout

        # Cache configuration
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.cache_max_size = cache_max_size
        self.cache_refresh_interval = cache_refresh_interval
        self.cache_fallback_behavior = cache_fallback_behavior

        # Initialize cache (using OrderedDict for LRU behavior)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.cache_lock = threading.RLock()
        self.refresh_in_progress = False
        self.bulk_flags_cache: Optional[Dict[str, Any]] = None

        # Environment is determined by the backend from API key prefix
        # live_ = production, test_ = test
        if api_key.startswith("live_"):
            self.environment = "production"
        elif api_key.startswith("test_"):
            self.environment = "test"
        else:
            self.environment = "production"  # Default fallback

        # Start background refresh if enabled
        if self.cache_enabled and self.cache_refresh_interval > 0:
            self._start_background_refresh()

    def is_enabled(self, flag_key: str, default_value: bool = False, context: Optional[str] = None) -> bool:
        """
        Checks if a feature flag is enabled.

        Args:
            flag_key: The key for the feature flag
            default_value: Default value to return if flag cannot be retrieved or on error
            context: Optional context ID for percentage rollouts (e.g., user_id, session_id)

        Returns:
            A boolean indicating if the feature is enabled, or default_value on error

        Raises:
            ValueError: If flag_key is not provided
        """
        if not flag_key:
            raise ValueError("flag_key is required to check if a feature is enabled.")

        # Check bulk cache first if available
        if self.cache_enabled and self.bulk_flags_cache:
            current_time = time.time()
            if current_time < self.bulk_flags_cache.get("expires_at", 0):
                flag = self.bulk_flags_cache["flags"].get(flag_key)
                if flag:
                    return self._evaluate_flag(flag, context)

        # Check individual cache if enabled (include context in cache key)
        cache_key = f"{flag_key}:{context}" if context else flag_key
        if self.cache_enabled:
            cached_value = self._get_cached_value(cache_key)
            if cached_value is not None:
                return cached_value

        # Cache miss - fetch from API
        try:
            value, should_cache = self._fetch_flag_from_api_with_cache_info(flag_key, default_value, context)

            # Store in cache if enabled and the response was successful
            if self.cache_enabled and should_cache:
                self._set_cached_value(cache_key, value)

            return value
        except Exception as error:
            return self._handle_cache_miss(flag_key, default_value, error)

    def _fetch_flag_from_api_with_cache_info(
        self, flag_key: str, default_value: bool, context: Optional[str] = None
    ) -> Tuple[bool, bool]:
        """Fetches a flag value from the API with cache information."""
        url = f"{self.base_url}/api/feature-flag/{flag_key}/enabled"
        if context:
            # URL encode the context parameter
            import urllib.parse

            url += f"?context={urllib.parse.quote(context)}"

        headers = {
            "X-API-Key": self.api_key,
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)

            # Handle authentication errors - log but return default (don't cache)
            if response.status_code == 401:
                print(f"FlagVault: Invalid API credentials for flag '{flag_key}', using default: {default_value}")
                return default_value, False
            elif response.status_code == 403:
                print(f"FlagVault: Access forbidden for flag '{flag_key}', using default: {default_value}")
                return default_value, False
            elif response.status_code == 404:
                print(f"FlagVault: Flag '{flag_key}' not found, using default: {default_value}")
                return default_value, False

            # Handle other HTTP errors - log but return default (don't cache)
            if not response.ok:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"HTTP {response.status_code}")
                except (json.JSONDecodeError, ValueError):
                    error_message = f"HTTP {response.status_code}: {response.text[:100]}"
                print(f"FlagVault: API error for flag '{flag_key}': {error_message}, using default: {default_value}")
                return default_value, False

            # Parse response
            try:
                data = response.json()
                return data.get("enabled", default_value), True
            except (json.JSONDecodeError, ValueError) as e:
                print(f"FlagVault: Invalid JSON response for flag '{flag_key}': {e}, using default: {default_value}")
                return default_value, False

        except requests.Timeout:
            print(
                f"FlagVault: Request timed out for flag '{flag_key}' after {self.timeout}s, "
                f"using default: {default_value}"
            )
            return default_value, False
        except requests.ConnectionError:
            print(f"FlagVault: Failed to connect to API for flag '{flag_key}', using default: {default_value}")
            return default_value, False
        except requests.RequestException as e:
            print(f"FlagVault: Network error for flag '{flag_key}': {e}, using default: {default_value}")
            return default_value, False

    def _fetch_flag_from_api(self, flag_key: str, default_value: bool, context: Optional[str] = None) -> bool:
        """Fetches a flag value from the API."""
        value, _ = self._fetch_flag_from_api_with_cache_info(flag_key, default_value, context)
        return value

    def _get_cached_value(self, flag_key: str) -> Optional[bool]:
        """Gets a cached flag value if it exists and is not expired."""
        with self.cache_lock:
            entry = self.cache.get(flag_key)
            if not entry:
                return None

            current_time = time.time()
            if current_time > entry.expires_at:
                del self.cache[flag_key]
                return None

            # Update last accessed time and move to end for LRU
            updated_entry = entry._replace(last_accessed=current_time)
            self.cache[flag_key] = updated_entry
            self.cache.move_to_end(flag_key)
            return entry.value

    def _set_cached_value(self, flag_key: str, value: bool) -> None:
        """Sets a flag value in the cache."""
        with self.cache_lock:
            # Check if cache is full and evict oldest entry
            if len(self.cache) >= self.cache_max_size:
                self.cache.popitem(last=False)  # Remove oldest (first) item

            current_time = time.time()
            entry = CacheEntry(
                value=value,
                cached_at=current_time,
                expires_at=current_time + self.cache_ttl,
                last_accessed=current_time,
            )
            self.cache[flag_key] = entry

    def _handle_cache_miss(self, flag_key: str, default_value: bool, error: Exception) -> bool:
        """Handles cache miss scenarios based on configured fallback behavior."""
        if self.cache_fallback_behavior == "default":
            print(f"FlagVault: Cache miss for '{flag_key}', using default: {default_value}")
            return default_value
        elif self.cache_fallback_behavior == "throw":
            raise error
        elif self.cache_fallback_behavior == "api":
            # For now, just return default - could implement retry logic
            print(f"FlagVault: Cache miss for '{flag_key}', using default: {default_value}")
            return default_value
        else:
            return default_value

    def _start_background_refresh(self) -> None:
        """Starts the background refresh timer."""

        def refresh_worker():
            while True:
                try:
                    time.sleep(self.cache_refresh_interval)
                    if not self.refresh_in_progress:
                        self._refresh_expired_flags()
                except Exception as e:
                    print(f"FlagVault: Background refresh thread error: {e}")

        refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        refresh_thread.start()

    def _refresh_expired_flags(self) -> None:
        """Refreshes flags that are about to expire."""
        self.refresh_in_progress = True

        try:
            current_time = time.time()
            flags_to_refresh = []

            # Find flags that will expire in the next 30 seconds
            # Only refresh flags without context (basic flag keys)
            with self.cache_lock:
                for flag_key, entry in list(self.cache.items()):
                    time_until_expiry = entry.expires_at - current_time
                    if time_until_expiry <= 30 and ":" not in flag_key:  # 30 seconds, no context
                        flags_to_refresh.append(flag_key)

            # Refresh flags in the background
            for flag_key in flags_to_refresh:
                try:
                    value, should_cache = self._fetch_flag_from_api_with_cache_info(flag_key, False)
                    if should_cache:
                        self._set_cached_value(flag_key, value)
                except Exception as error:
                    # Background refresh failed, but don't remove from cache
                    print(f"FlagVault: Background refresh failed for '{flag_key}': {error}")

        except Exception as error:
            print(f"FlagVault: Background refresh failed: {error}")
        finally:
            self.refresh_in_progress = False

    def get_cache_stats(self) -> CacheStats:
        """Gets cache statistics for monitoring and debugging."""
        with self.cache_lock:
            hit_count = 0
            expired_count = 0
            current_time = time.time()

            for entry in self.cache.values():
                if entry.last_accessed > entry.cached_at:
                    hit_count += 1
                if current_time > entry.expires_at:
                    expired_count += 1

            hit_rate = hit_count / len(self.cache) if len(self.cache) > 0 else 0

            return CacheStats(
                size=len(self.cache),
                hit_rate=hit_rate,
                expired_entries=expired_count,
                memory_usage=self._estimate_memory_usage(),
            )

    def debug_flag(self, flag_key: str) -> FlagDebugInfo:
        """Gets debug information for a specific flag."""
        with self.cache_lock:
            entry = self.cache.get(flag_key)
            current_time = time.time()

            if entry:
                return FlagDebugInfo(
                    flag_key=flag_key,
                    cached=True,
                    value=entry.value,
                    cached_at=entry.cached_at,
                    expires_at=entry.expires_at,
                    time_until_expiry=entry.expires_at - current_time,
                    last_accessed=entry.last_accessed,
                )
            else:
                return FlagDebugInfo(flag_key=flag_key, cached=False)

    def clear_cache(self) -> None:
        """Clears the entire cache."""
        with self.cache_lock:
            self.cache.clear()

    def destroy(self) -> None:
        """Cleans up resources. Call this when done with the SDK instance."""
        self.clear_cache()
        # Note: Background thread is daemon and will automatically stop

    def _estimate_memory_usage(self) -> int:
        """Estimates memory usage of the cache."""
        # Rough estimation: each entry has a key (string) + CacheEntry object
        # String: ~1 byte per character, CacheEntry: ~32 bytes for floats/bool
        total = 0
        for key in self.cache.keys():
            total += len(key) + 40  # Rough estimate
        return total

    def get_all_flags(self) -> Dict[str, FeatureFlagMetadata]:
        """
        Fetches all feature flags for the organization.

        Returns:
            A dictionary mapping flag keys to flag metadata

        Raises:
            FlagVaultNetworkError: If network request fails
            FlagVaultAPIError: If API returns an error
        """
        # Check bulk cache first
        if self.cache_enabled and self.bulk_flags_cache:
            current_time = time.time()
            if current_time < self.bulk_flags_cache.get("expires_at", 0):
                return self.bulk_flags_cache["flags"].copy()

        url = f"{self.base_url}/api/feature-flag"
        headers = {
            "X-API-Key": self.api_key,
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)

            if not response.ok:
                raise FlagVaultAPIError(f"Failed to fetch flags: {response.status_code} {response.text[:100]}")

            data = response.json()
            flags = {}

            if "flags" in data and isinstance(data["flags"], list):
                for flag_data in data["flags"]:
                    flag = FeatureFlagMetadata(
                        key=flag_data["key"],
                        is_enabled=flag_data["isEnabled"],
                        name=flag_data["name"],
                        rollout_percentage=flag_data.get("rolloutPercentage"),
                        rollout_seed=flag_data.get("rolloutSeed"),
                    )
                    flags[flag.key] = flag

            # Cache the bulk response
            if self.cache_enabled:
                current_time = time.time()
                self.bulk_flags_cache = {
                    "flags": flags.copy(),
                    "cached_at": current_time,
                    "expires_at": current_time + self.cache_ttl,
                }

            return flags

        except requests.Timeout:
            raise FlagVaultNetworkError(f"Request timed out after {self.timeout}s")
        except requests.ConnectionError:
            raise FlagVaultNetworkError("Failed to connect to API")
        except requests.RequestException as e:
            raise FlagVaultNetworkError(f"Network error: {e}")

    def _evaluate_flag(self, flag: FeatureFlagMetadata, context: Optional[str] = None) -> bool:
        """
        Evaluates a feature flag for a specific context using local rollout logic.
        Internal method - not part of public API.
        """
        # If flag is disabled, always return false
        if not flag.is_enabled:
            return False

        # If no rollout percentage set, return the flag's enabled state
        if flag.rollout_percentage is None or flag.rollout_seed is None:
            return flag.is_enabled

        # Use provided context or generate a random one
        rollout_context = context or os.urandom(16).hex()

        # Calculate consistent hash for this context + flag combination
        hash_input = f"{rollout_context}-{flag.key}-{flag.rollout_seed}".encode("utf-8")
        hash_bytes = hashlib.sha256(hash_input).digest()

        # Convert first 2 bytes to a number between 0-9999 (for 0.01% precision)
        bucket = (hash_bytes[0] * 256 + hash_bytes[1]) % 10000

        # Check if this context is in the rollout percentage
        threshold = flag.rollout_percentage * 100  # Convert percentage to 0-10000 scale

        return bucket < threshold

    def preload_flags(self) -> None:
        """
        Preloads all feature flags into cache.
        Useful for applications that need to evaluate many flags quickly.
        """
        self.get_all_flags()
