#!/usr/bin/env python3
"""
Test script to verify batch saving functionality.
"""
import sys
import os
import logging
from datetime import datetime

# Add the monitoring directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitoring-roll-machine'))

from monitoring.batch_manager import get_batch_manager
from monitoring.supabase_client import get_supabase_client
from monitoring.config import load_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_batch_manager():
    """Test batch manager functionality."""
    print("=" * 50)
    print("TESTING BATCH MANAGER")
    print("=" * 50)

    # Initialize batch manager
    batch_manager = get_batch_manager()

    # Test 1: Get batch for new product (should return "1")
    print("\nTest 1: Get batch for new product")
    batch1 = batch_manager.get_batch_for_product("TEST-PRODUCT-001")
    print(f"Batch for TEST-PRODUCT-001: {batch1}")
    assert batch1 == "1", f"Expected '1', got '{batch1}'"

    # Test 2: Get batch for same product (should return same batch)
    print("\nTest 2: Get batch for same product")
    batch2 = batch_manager.get_batch_for_product("TEST-PRODUCT-001")
    print(f"Batch for TEST-PRODUCT-001 (again): {batch2}")
    assert batch2 == "1", f"Expected '1', got '{batch2}'"

    # Test 3: Get batch for different product (should increment)
    print("\nTest 3: Get batch for different product")
    batch3 = batch_manager.get_batch_for_product("TEST-PRODUCT-002")
    print(f"Batch for TEST-PRODUCT-002: {batch3}")
    assert batch3 == "2", f"Expected '2', got '{batch3}'"

    print("\n✅ Batch manager tests passed!")

def test_supabase_connection():
    """Test Supabase connection."""
    print("=" * 50)
    print("TESTING SUPABASE CONNECTION")
    print("=" * 50)

    # Load config
    config = load_config()
    print(f"Supabase URL: {config.get('supabase_url', 'Not configured')}")
    print(f"Supabase Key: {'*' * len(config.get('supabase_key', '')) if config.get('supabase_key') else 'Not configured'}")
    print(f"Enable Supabase: {config.get('enable_supabase', False)}")

    # Initialize Supabase client
    supabase_client = get_supabase_client()

    if supabase_client.is_connected:
        print("\n✅ Supabase client connected successfully!")

        # Test saving batch metadata
        print("\nTest: Saving batch metadata")
        batch_metadata = {
            'batch': 'TEST-001',
            'product_code': 'TEST-PRODUCT-001',
            'product_name': 'Test Product 001',
            'color_code': 'RED',
            'target_length': 100,
            'units': 'Meter',
            'created_at': datetime.now().isoformat(),
            'status': 'test'
        }

        result = supabase_client.insert_batch_metadata(batch_metadata)
        if result:
            print("✅ Batch metadata saved successfully!")
        else:
            print("❌ Failed to save batch metadata")

        # Test saving production log
        print("\nTest: Saving production log")
        production_log = {
            'batch': 'TEST-001',
            'product_code': 'TEST-PRODUCT-001',
            'product_name': 'Test Product 001',
            'color_code': 'RED',
            'product_length': 95.0,
            'target_length': 100,
            'units': 'Meter',
            'timestamp': datetime.now().isoformat(),
            'status': 'test'
        }

        result = supabase_client.insert_production_log(production_log)
        if result:
            print("✅ Production log saved successfully!")
        else:
            print("❌ Failed to save production log")

    else:
        print("\n❌ Supabase client not connected")
        print("Please configure your Supabase credentials in settings")

def main():
    """Run all tests."""
    print("BATCH SAVING FUNCTIONALITY TEST")
    print("=" * 50)

    try:
        test_batch_manager()
        test_supabase_connection()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 50)
        print("\nTo use the batch saving functionality:")
        print("1. Open the application")
        print("2. Go to Settings > Supabase Settings")
        print("3. Enter your Supabase URL and API key")
        print("4. Enable Supabase integration")
        print("5. Click 'Save Settings'")
        print("6. Use the 'Save' button in the product form to save batches")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()