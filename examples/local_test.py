#!/usr/bin/env python3
"""
Example script for testing the FlagVault SDK against a local server.
"""
from flagvault_sdk import FlagVaultSDK

def test_local_server():
    """Test the SDK against a local server"""
    # Initialize the SDK with localhost URL
    sdk = FlagVaultSDK(
        api_key="your-test-api-key",
        api_secret="your-test-api-secret", 
        base_url="http://localhost:3000"  # Adjust port as needed
    )
    
    try:
        # Check if a feature flag is enabled
        flag_key = "test-flag"
        is_enabled = sdk.is_enabled(flag_key)
        print(f"Flag '{flag_key}' enabled: {is_enabled}")
    except Exception as e:
        print(f"Error testing feature flag: {e}")

if __name__ == "__main__":
    test_local_server()