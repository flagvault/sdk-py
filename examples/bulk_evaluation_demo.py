from flagvault_sdk import FlagVaultSDK
import time

def demonstrate_bulk_evaluation():
    # Initialize SDK
    sdk = FlagVaultSDK(
        api_key='test_your-api-key',  # Replace with your actual API key
        base_url='http://localhost:3001',  # For local testing
    )
    
    print('=== FlagVault Bulk Evaluation Demo ===\n')
    
    try:
        # Method 1: Preload all flags
        print('1. Preloading all flags...')
        sdk.preload_flags()
        print('✓ Flags preloaded into cache\n')
        
        # Method 2: Get all flags and evaluate locally
        print('2. Fetching all flags...')
        all_flags = sdk.get_all_flags()
        print(f'✓ Fetched {len(all_flags)} flags\n')
        
        # Display flag metadata
        print('Flag Metadata:')
        for key, flag in all_flags.items():
            print(f'- {key}:')
            print(f'  Enabled: {flag.is_enabled}')
            print(f'  Rollout: {flag.rollout_percentage if flag.rollout_percentage is not None else "None"}%')
            print(f'  Seed: {flag.rollout_seed or "None"}')
        print()
        
        # Method 3: Evaluate flags for different users using is_enabled
        print('3. Evaluating flags for different users:')
        users = ['user-123', 'user-456', 'user-789', 'user-abc', 'user-def']
        
        # Pick a flag with rollout (if any)
        rollout_flag = None
        for flag in all_flags.values():
            if flag.rollout_percentage is not None:
                rollout_flag = flag
                break
        
        if rollout_flag:
            print(f'\nRollout evaluation for "{rollout_flag.key}" ({rollout_flag.rollout_percentage}%):')
            
            for user_id in users:
                enabled = sdk.is_enabled(rollout_flag.key, False, user_id)
                status = '✓ Enabled' if enabled else '✗ Disabled'
                print(f'- {user_id}: {status}')
            
            # Demonstrate consistency
            print('\nConsistency check - evaluating same user multiple times:')
            test_user = 'user-999'
            for i in range(3):
                enabled = sdk.is_enabled(rollout_flag.key, False, test_user)
                status = '✓ Enabled' if enabled else '✗ Disabled'
                print(f'- Attempt {i + 1}: {status}')
        else:
            print('No flags with rollout percentage found.')
        
        # Method 4: Using cached data with is_enabled
        print('\n4. Using is_enabled with bulk cache:')
        start_time = time.time()
        
        # These calls will use the bulk cache instead of making API calls
        for key in all_flags.keys():
            sdk.is_enabled(key, False, 'user-123')
        
        elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds
        print(f'✓ Evaluated {len(all_flags)} flags in {elapsed:.0f}ms (using cache)')
        
    except Exception as e:
        print(f'Error: {e}')
    finally:
        # Clean up
        sdk.destroy()

if __name__ == '__main__':
    demonstrate_bulk_evaluation()