#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan race condition pada product search.
Menguji scenario rapid typing dan multiple API calls.
"""

import time
import threading
import logging
from typing import List, Dict, Any
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RaceConditionTest:
    """Test class untuk menguji race condition fix."""
    
    def __init__(self):
        self.results = []
        self.current_input = ""
        self.last_searched = ""
        self.current_request_id = None
        self.last_user_input = ""
        
    def simulate_rapid_typing(self, product_codes: List[str], delay_ms: int = 50):
        """Simulate rapid typing of product codes."""
        logger.info(f"Starting rapid typing test with {len(product_codes)} codes")
        
        for i, code in enumerate(product_codes):
            logger.info(f"Typing: {code} (step {i+1}/{len(product_codes)})")
            
            # Simulate user typing
            self.current_input = code
            self.last_user_input = code
            
            # Simulate search trigger
            self._trigger_search(code)
            
            # Small delay to simulate typing speed
            time.sleep(delay_ms / 1000.0)
        
        logger.info("Rapid typing test completed")
    
    def _trigger_search(self, product_code: str):
        """Simulate search trigger with thread safety."""
        import uuid
        
        # Update tracking variables
        self.last_searched = product_code
        self.last_user_input = product_code
        
        # Generate new request ID
        request_id = str(uuid.uuid4())
        self.current_request_id = request_id
        
        logger.info(f"Search triggered for '{product_code}' with request ID: {request_id[:8]}...")
        
        # Simulate API call in background thread
        thread = threading.Thread(
            target=self._simulate_api_call,
            args=(product_code, request_id)
        )
        thread.daemon = True
        thread.start()
    
    def _simulate_api_call(self, product_code: str, request_id: str):
        """Simulate API call with variable response time."""
        import random
        
        # Simulate network delay (50-200ms)
        delay = random.uniform(0.05, 0.2)
        time.sleep(delay)
        
        # Simulate API response
        product_info = {
            "product_code": product_code,
            "product_name": f"Product {product_code}",
            "color_code": "RED",
            "barcode": ["123456789"],
            "attachment": None,
            "_request_id": request_id
        }
        
        # Process result
        self._process_search_result(product_info)
    
    def _process_search_result(self, product_info: Dict[str, Any]):
        """Process search result with thread safety checks."""
        request_id = product_info.get("_request_id")
        current_input = self.current_input
        
        logger.info(f"Processing result for request {request_id[:8]}... (current input: '{current_input}')")
        
        # Thread safety check - only process if this is the current request
        if request_id != self.current_request_id:
            logger.warning(f"Ignoring stale result for request {request_id[:8]}... (current: {self.current_request_id[:8] if self.current_request_id else 'None'}...)")
            return
        
        # Check if user input has changed since this search started
        if current_input != self.last_user_input:
            logger.warning(f"Ignoring result - user input changed from '{self.last_user_input}' to '{current_input}'")
            return
        
        # Process the result
        logger.info(f"✅ Processing valid result for '{product_info['product_code']}'")
        self.results.append({
            "product_code": product_info["product_code"],
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "status": "processed"
        })
    
    def test_scenario_1(self):
        """Test scenario: BD-1 -> BD-2 -> BD-5 -> BD-1 (rapid typing)"""
        logger.info("\n" + "="*60)
        logger.info("SCENARIO 1: Rapid typing with repeated codes")
        logger.info("="*60)
        
        self.results = []
        product_codes = ["BD-1", "BD-2", "BD-5", "BD-1"]
        
        self.simulate_rapid_typing(product_codes, delay_ms=30)
        
        # Wait for all threads to complete
        time.sleep(1.0)
        
        # Analyze results
        self._analyze_results("Scenario 1")
    
    def test_scenario_2(self):
        """Test scenario: Very rapid typing with many codes"""
        logger.info("\n" + "="*60)
        logger.info("SCENARIO 2: Very rapid typing with many codes")
        logger.info("="*60)
        
        self.results = []
        product_codes = ["BD-1", "BD-2", "BD-3", "BD-4", "BD-5", "BD-1", "BD-2", "BD-3"]
        
        self.simulate_rapid_typing(product_codes, delay_ms=20)
        
        # Wait for all threads to complete
        time.sleep(1.5)
        
        # Analyze results
        self._analyze_results("Scenario 2")
    
    def test_scenario_3(self):
        """Test scenario: Slow typing then rapid changes"""
        logger.info("\n" + "="*60)
        logger.info("SCENARIO 3: Slow typing then rapid changes")
        logger.info("="*60)
        
        self.results = []
        
        # Slow typing first
        logger.info("Phase 1: Slow typing")
        self.simulate_rapid_typing(["BD-1"], delay_ms=500)
        time.sleep(0.5)
        
        # Then rapid changes
        logger.info("Phase 2: Rapid changes")
        self.simulate_rapid_typing(["BD-2", "BD-3", "BD-4", "BD-1"], delay_ms=25)
        
        # Wait for all threads to complete
        time.sleep(1.0)
        
        # Analyze results
        self._analyze_results("Scenario 3")
    
    def _analyze_results(self, scenario_name: str):
        """Analyze test results."""
        logger.info(f"\n--- {scenario_name} Results ---")
        
        if not self.results:
            logger.warning("No results processed!")
            return
        
        # Count processed results
        processed_count = len(self.results)
        logger.info(f"Processed results: {processed_count}")
        
        # Show final result
        if self.results:
            final_result = self.results[-1]
            logger.info(f"Final processed result: {final_result['product_code']}")
            logger.info(f"Expected final input: {self.current_input}")
            
            if final_result['product_code'] == self.current_input:
                logger.info("✅ SUCCESS: Final result matches current input")
            else:
                logger.error(f"❌ FAILURE: Final result '{final_result['product_code']}' doesn't match current input '{self.current_input}'")
        
        # Show all results
        logger.info("All processed results:")
        for i, result in enumerate(self.results):
            logger.info(f"  {i+1}. {result['product_code']} (request: {result['request_id'][:8]}...)")
        
        return processed_count

def main():
    """Main test function."""
    logger.info("Starting Race Condition Fix Test")
    logger.info(f"Timestamp: {datetime.now()}")
    
    # Create test instance
    tester = RaceConditionTest()
    
    # Run test scenarios
    tester.test_scenario_1()
    time.sleep(1)
    
    tester.test_scenario_2()
    time.sleep(1)
    
    tester.test_scenario_3()
    
    logger.info("\n" + "="*60)
    logger.info("RACE CONDITION FIX TEST COMPLETED")
    logger.info("="*60)
    
    # Summary
    logger.info("\nTest Summary:")
    logger.info("- Scenario 1: Rapid typing with repeated codes")
    logger.info("- Scenario 2: Very rapid typing with many codes") 
    logger.info("- Scenario 3: Slow typing then rapid changes")
    logger.info("\nExpected behavior:")
    logger.info("- Only the most recent search should be processed")
    logger.info("- Stale results should be ignored")
    logger.info("- Final result should match the last user input")

if __name__ == "__main__":
    main() 