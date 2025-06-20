"""
FlagVault SDK Caching Examples

This file demonstrates the new caching capabilities in FlagVault SDK v1.2.0
"""

import time
import asyncio
from flagvault_sdk import FlagVaultSDK


def basic_caching_example():
    """Basic usage with default caching (enabled by default)."""
    print("=== Basic Caching Example ===")
    
    sdk = FlagVaultSDK(
        api_key="your-api-key-here"
        # Caching is enabled by default with 5-minute TTL
    )

    # First call - will hit the API
    start_time = time.time()
    is_enabled1 = sdk.is_enabled("new-feature")
    first_call_time = (time.time() - start_time) * 1000
    print(f"First call: {is_enabled1} ({first_call_time:.1f}ms)")

    # Second call - will hit the cache
    start_time = time.time()
    is_enabled2 = sdk.is_enabled("new-feature")
    second_call_time = (time.time() - start_time) * 1000
    print(f"Second call: {is_enabled2} ({second_call_time:.1f}ms)")

    print(f"Performance improvement: {first_call_time / second_call_time:.1f}x faster")

    # Clean up
    sdk.destroy()


def custom_cache_example():
    """Custom cache configuration example."""
    print("\n=== Custom Cache Configuration Example ===")
    
    sdk = FlagVaultSDK(
        api_key="your-api-key-here",
        cache_enabled=True,
        cache_ttl=600,              # 10 minutes cache
        cache_max_size=500,         # Store up to 500 flags
        cache_refresh_interval=120, # Background refresh every 2 minutes
        cache_fallback_behavior='default'
    )

    is_enabled = sdk.is_enabled("long-lived-feature")
    print(f"Feature enabled: {is_enabled}")

    # Get cache statistics
    stats = sdk.get_cache_stats()
    print(f"Cache stats:")
    print(f"  Size: {stats.size}")
    print(f"  Hit rate: {stats.hit_rate * 100:.1f}%")
    print(f"  Memory usage: {stats.memory_usage} bytes")

    sdk.destroy()


def cache_debugging_example():
    """Debugging cache behavior example."""
    print("\n=== Cache Debugging Example ===")
    
    sdk = FlagVaultSDK(
        api_key="your-api-key-here",
        cache_ttl=60  # 1-minute cache for demo
    )

    # Check a flag
    sdk.is_enabled("debug-feature")

    # Debug the specific flag
    debug_info = sdk.debug_flag("debug-feature")
    print(f"Debug info:")
    print(f"  Flag key: {debug_info.flag_key}")
    print(f"  Cached: {debug_info.cached}")
    print(f"  Value: {debug_info.value}")
    if debug_info.time_until_expiry:
        print(f"  Time until expiry: {debug_info.time_until_expiry:.1f}s")

    sdk.destroy()


def high_performance_example():
    """High-performance application with multiple flags."""
    print("\n=== High Performance Example ===")
    
    sdk = FlagVaultSDK(
        api_key="your-api-key-here",
        cache_enabled=True,
        cache_ttl=300,
        cache_refresh_interval=60  # Proactive refresh
    )

    flags = [
        "new-dashboard",
        "advanced-analytics", 
        "beta-features",
        "premium-content",
        "experimental-ui"
    ]

    # First iteration - some cache misses
    start_time = time.time()
    results1 = {}
    for flag in flags:
        is_enabled = sdk.is_enabled(flag)
        results1[flag] = is_enabled
        print(f"{flag}: {is_enabled}")
    
    first_iteration_time = (time.time() - start_time) * 1000
    print(f"First iteration time: {first_iteration_time:.1f}ms")

    print("\nSecond iteration (all cached):")
    start_time = time.time()
    results2 = {}
    for flag in flags:
        is_enabled = sdk.is_enabled(flag)
        results2[flag] = is_enabled
        print(f"{flag}: {is_enabled}")
    
    second_iteration_time = (time.time() - start_time) * 1000
    print(f"Second iteration time: {second_iteration_time:.1f}ms")
    print(f"Performance improvement: {first_iteration_time / second_iteration_time:.1f}x faster")

    # Show cache performance
    stats = sdk.get_cache_stats()
    print(f"\nFinal cache stats:")
    print(f"  Size: {stats.size}")
    print(f"  Hit rate: {stats.hit_rate * 100:.1f}%")

    sdk.destroy()


def real_time_example():
    """Real-time (no cache) example."""
    print("\n=== Real-time (No Cache) Example ===")
    
    sdk = FlagVaultSDK(
        api_key="your-api-key-here",
        cache_enabled=False  # Disable caching for real-time updates
    )

    # Every call will hit the API
    is_enabled1 = sdk.is_enabled("real-time-feature")
    is_enabled2 = sdk.is_enabled("real-time-feature")
    
    print(f"First call: {is_enabled1}")
    print(f"Second call: {is_enabled2}")
    print("Both calls hit the API directly")

    sdk.destroy()


def django_integration_example():
    """Django integration example with caching."""
    return """
# Django settings.py
FLAGVAULT_SDK = FlagVaultSDK(
    api_key=os.environ.get('FLAGVAULT_API_KEY'),
    cache_enabled=True,
    cache_ttl=300,  # 5 minutes
    cache_refresh_interval=60  # Background refresh every minute
)

# Django views.py
from django.conf import settings

def my_view(request):
    # This will benefit from caching automatically
    if settings.FLAGVAULT_SDK.is_enabled('new-feature'):
        return render(request, 'new_feature.html')
    else:
        return render(request, 'old_feature.html')

# Multiple views using the same flag will benefit from caching
def another_view(request):
    is_enabled = settings.FLAGVAULT_SDK.is_enabled('new-feature')  # Cache hit!
    context = {'feature_enabled': is_enabled}
    return render(request, 'template.html', context)
"""


def flask_integration_example():
    """Flask integration example with caching."""
    return """
# Flask app.py
from flask import Flask, render_template
from flagvault_sdk import FlagVaultSDK
import os

app = Flask(__name__)

# Initialize SDK with caching (singleton pattern)
sdk = FlagVaultSDK(
    api_key=os.environ.get('FLAGVAULT_API_KEY'),
    cache_enabled=True,
    cache_ttl=300,
    cache_refresh_interval=60
)

@app.route('/dashboard')
def dashboard():
    # Multiple flag checks benefit from caching
    features = {
        'new_dashboard': sdk.is_enabled('new-dashboard'),
        'analytics': sdk.is_enabled('advanced-analytics'),
        'beta_features': sdk.is_enabled('beta-features')
    }
    
    return render_template('dashboard.html', features=features)

@app.route('/api/feature-status')
def feature_status():
    # API endpoint that benefits from caching
    return {
        'new_feature': sdk.is_enabled('new-feature'),
        'experimental': sdk.is_enabled('experimental-ui')
    }

# Optional: Add cache stats endpoint for monitoring
@app.route('/api/cache-stats')
def cache_stats():
    stats = sdk.get_cache_stats()
    return {
        'size': stats.size,
        'hit_rate': stats.hit_rate,
        'memory_usage': stats.memory_usage
    }
"""


def async_example():
    """Async/await usage pattern (conceptual)."""
    return """
import asyncio
from concurrent.futures import ThreadPoolExecutor
from flagvault_sdk import FlagVaultSDK

# Since the SDK uses synchronous requests, wrap in async for async frameworks
class AsyncFlagVaultSDK:
    def __init__(self, *args, **kwargs):
        self.sdk = FlagVaultSDK(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def is_enabled(self, flag_key: str, default_value: bool = False):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sdk.is_enabled, 
            flag_key, 
            default_value
        )

# Usage with FastAPI
from fastapi import FastAPI

app = FastAPI()
async_sdk = AsyncFlagVaultSDK(api_key="your-api-key")

@app.get("/dashboard")
async def dashboard():
    # Caching still works with async wrapper
    is_enabled = await async_sdk.is_enabled('new-feature')
    return {"feature_enabled": is_enabled}
"""


if __name__ == "__main__":
    # Run examples
    try:
        basic_caching_example()
        custom_cache_example()
        cache_debugging_example()
        high_performance_example()
        real_time_example()
        
        print("\n=== Django Integration Example ===")
        print(django_integration_example())
        
        print("\n=== Flask Integration Example ===")
        print(flask_integration_example())
        
        print("\n=== Async Framework Example ===")
        print(async_example())
        
    except Exception as error:
        print(f"Example failed: {error}")