"""
Test script for ERP integration.

This script tests the ERP client connection and submission functionality
without needing to run the full GUI application.

Usage:
    python test_erp_integration.py
"""
import sys
import logging
from pathlib import Path

# Add monitoring module to path
sys.path.insert(0, str(Path(__file__).parent / "monitoring"))

from monitoring.erp_client import ERPClient
from monitoring.config import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test ERP connection."""
    print("\n" + "="*60)
    print("Testing ERP Connection")
    print("="*60 + "\n")
    
    # Load config
    config = load_config()
    
    # Check if ERP is enabled
    if not config.get('enable_erp_submission', False):
        print("❌ ERP submission is disabled in config.json")
        print("   Set 'enable_erp_submission': true to enable")
        return False
    
    # Get ERP credentials
    erp_url = config.get('erp_url', '').strip()
    erp_api_key = config.get('erp_api_key', '').strip()
    erp_api_secret = config.get('erp_api_secret', '').strip()
    
    if not all([erp_url, erp_api_key, erp_api_secret]):
        print("❌ ERP credentials not configured")
        print("\nRequired settings in config.json:")
        print("  - erp_url")
        print("  - erp_api_key")
        print("  - erp_api_secret")
        return False
    
    print(f"📡 ERP URL: {erp_url}")
    print(f"🔑 API Key: {erp_api_key[:10]}...")
    print(f"🔐 API Secret: {'*' * 20}")
    print()
    
    # Create ERP client
    try:
        client = ERPClient(
            base_url=erp_url,
            api_key=erp_api_key,
            api_secret=erp_api_secret,
            timeout=config.get('erp_timeout', 30)
        )
        
        # Test connection
        print("🔄 Testing connection...")
        success, message = client.test_connection()
        
        if success:
            print(f"✅ Connection successful!")
            print(f"   {message}")
            return True
        else:
            print(f"❌ Connection failed!")
            print(f"   {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating ERP client: {e}")
        return False


def test_stock_entry_creation():
    """Test Stock Entry document creation (dry run)."""
    print("\n" + "="*60)
    print("Testing Stock Entry Creation (Dry Run)")
    print("="*60 + "\n")
    
    # Load config
    config = load_config()
    
    # Create test batch data
    test_batch_data = {
        'batch': '999',  # Test batch number
        'product_code': 'TEST-FABRIC-001',
        'product_name': 'Test Fabric',
        'total_rolls': 2,
        'total_length': 95.5,
        'start_time': '2025-10-10T10:00:00',
        'end_time': '2025-10-10T10:30:00',
        'logs': [
            {
                'product_code': 'TEST-FABRIC-001',
                'product_name': 'Test Fabric',
                'product_length': 45.5,
                'batch': '999',
                'cycle_time': 120.0,
                'roll_time': 180.0,
                'timestamp': '2025-10-10T10:10:00'
            },
            {
                'product_code': 'TEST-FABRIC-001',
                'product_name': 'Test Fabric',
                'product_length': 50.0,
                'batch': '999',
                'cycle_time': 125.0,
                'roll_time': 185.0,
                'timestamp': '2025-10-10T10:25:00'
            }
        ]
    }
    
    print("📦 Test Batch Data:")
    print(f"   Batch: {test_batch_data['batch']}")
    print(f"   Product: {test_batch_data['product_code']} - {test_batch_data['product_name']}")
    print(f"   Rolls: {test_batch_data['total_rolls']}")
    print(f"   Total Length: {test_batch_data['total_length']:.2f} m")
    print()
    
    # Get ERP credentials
    erp_url = config.get('erp_url', '').strip()
    erp_api_key = config.get('erp_api_key', '').strip()
    erp_api_secret = config.get('erp_api_secret', '').strip()
    
    if not all([erp_url, erp_api_key, erp_api_secret]):
        print("❌ ERP credentials not configured")
        return False
    
    try:
        # Create ERP client
        client = ERPClient(
            base_url=erp_url,
            api_key=erp_api_key,
            api_secret=erp_api_secret,
            timeout=config.get('erp_timeout', 30)
        )
        
        # Prepare document (but don't submit)
        print("🔄 Preparing Stock Entry document...")
        stock_entry_doc = client._prepare_stock_entry(
            batch_data=test_batch_data,
            company=config.get('erp_company', 'Textilindo'),
            from_warehouse=config.get('erp_from_warehouse', 'Prancis - MGI'),
            to_warehouse=config.get('erp_to_warehouse', 'Prancis - MGI')
        )
        
        print("✅ Stock Entry document prepared successfully!")
        print("\n📄 Document Structure:")
        print(f"   Company: {stock_entry_doc['company']}")
        print(f"   Type: {stock_entry_doc['stock_entry_type']}")
        print(f"   From Warehouse: {stock_entry_doc['from_warehouse']}")
        print(f"   To Warehouse: {stock_entry_doc['to_warehouse']}")
        print(f"   Packing List Items: {len(stock_entry_doc['packing_list'])}")
        print(f"   Items: {len(stock_entry_doc['items'])}")
        print()
        
        # Show sample packing list item
        if stock_entry_doc['packing_list']:
            print("📋 Sample Packing List Item:")
            sample = stock_entry_doc['packing_list'][0]
            for key, value in sample.items():
                print(f"   {key}: {value}")
        
        print("\n⚠️  Note: This is a dry run. No data was submitted to ERP.")
        print("   To test actual submission, use the GUI application.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error preparing Stock Entry: {e}")
        logger.error(f"Error in test: {e}", exc_info=True)
        return False


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("ERP Integration Test")
    print("="*60)
    
    # Test connection
    connection_ok = test_connection()
    
    if not connection_ok:
        print("\n❌ Connection test failed. Fix connection issues before continuing.")
        return 1
    
    # Test Stock Entry creation (dry run)
    doc_ok = test_stock_entry_creation()
    
    if not doc_ok:
        print("\n❌ Stock Entry preparation failed.")
        return 1
    
    print("\n" + "="*60)
    print("All tests passed! ✅")
    print("="*60)
    print("\nNext steps:")
    print("1. Ensure test item code (TEST-FABRIC-001) exists in ERPNext")
    print("2. Verify warehouse names match exactly in ERPNext")
    print("3. Use the GUI application to test actual submission")
    print("4. Check created Stock Entry in ERPNext and submit if correct")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        logger.error("Unexpected error in test", exc_info=True)
        sys.exit(1)



