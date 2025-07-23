#!/usr/bin/env python3
"""
Test script untuk memverifikasi optimasi product search.
Mengukur performa sebelum dan sesudah optimasi.
"""

import time
import requests
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductSearchPerformanceTest:
    """Test class untuk mengukur performa product search."""
    
    def __init__(self, api_url: str, api_key: str = ""):
        self.api_url = api_url
        self.api_key = api_key
        self.session = requests.Session()
        
        # Setup headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"token {api_key}"
        
        # Optimize session
        from requests.adapters import HTTPAdapter
        self.session.mount('http://', HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=1
        ))
        self.session.mount('https://', HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=1
        ))
        
        # Test product codes
        self.test_products = [
            "BD-RED",
            "BD-BLUE", 
            "BD-GREEN",
            "BD-YELLOW",
            "BD-BLACK"
        ]
        
        # Cache untuk testing
        self._cache = {}
        self._cache_max_size = 100
    
    def _get_cached_product(self, product_code: str) -> Dict[str, Any]:
        """Get product from cache if available."""
        return self._cache.get(product_code)
    
    def _cache_product(self, product_code: str, product_info: Dict[str, Any]):
        """Cache product information."""
        if len(self._cache) >= self._cache_max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[product_code] = product_info
    
    def search_product_with_cache(self, product_code: str, timeout: int = 5) -> Dict[str, Any]:
        """Search product with caching."""
        # Check cache first
        cached_result = self._get_cached_product(product_code)
        if cached_result:
            logger.info(f"Cache HIT for {product_code}")
            return cached_result
        
        logger.info(f"Cache MISS for {product_code}")
        
        # Make API call
        json_data = {"product_code": product_code}
        
        start_time = time.time()
        try:
            response = self.session.post(
                self.api_url,
                json=json_data,
                headers=self.headers,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Check response structure
            if (data.get("message") and 
                isinstance(data["message"], dict) and 
                data["message"].get("success") and 
                data["message"].get("data", {}).get("products")):
                
                products = data["message"]["data"]["products"]
                if products:
                    product_info = products[0]
                    # Cache the result
                    self._cache_product(product_code, product_info)
                    return product_info
            
            return {"error": "Product not found"}
            
        except requests.exceptions.Timeout:
            return {"error": "Timeout"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error"}
        except Exception as e:
            return {"error": f"Search error: {str(e)}"}
        finally:
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"API call for {product_code}: {elapsed:.2f}ms")
    
    def test_single_search(self, product_code: str) -> Dict[str, Any]:
        """Test single product search."""
        logger.info(f"Testing search for: {product_code}")
        
        # First search (should hit API)
        start_time = time.time()
        result1 = self.search_product_with_cache(product_code)
        first_search_time = (time.time() - start_time) * 1000
        
        # Second search (should hit cache)
        start_time = time.time()
        result2 = self.search_product_with_cache(product_code)
        second_search_time = (time.time() - start_time) * 1000
        
        return {
            "product_code": product_code,
            "first_search_ms": first_search_time,
            "second_search_ms": second_search_time,
            "cache_improvement": first_search_time / second_search_time if second_search_time > 0 else float('inf'),
            "result1": result1,
            "result2": result2
        }
    
    def test_multiple_searches(self, iterations: int = 3) -> List[Dict[str, Any]]:
        """Test multiple product searches."""
        results = []
        
        for i in range(iterations):
            logger.info(f"\n=== Iteration {i+1}/{iterations} ===")
            
            for product_code in self.test_products:
                result = self.test_single_search(product_code)
                results.append(result)
                
                # Small delay between searches
                time.sleep(0.1)
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]):
        """Analyze test results."""
        logger.info("\n" + "="*60)
        logger.info("PERFORMANCE ANALYSIS")
        logger.info("="*60)
        
        # Calculate averages
        first_search_times = [r["first_search_ms"] for r in results]
        second_search_times = [r["second_search_ms"] for r in results]
        cache_improvements = [r["cache_improvement"] for r in results if r["cache_improvement"] != float('inf')]
        
        avg_first = sum(first_search_times) / len(first_search_times)
        avg_second = sum(second_search_times) / len(second_search_times)
        avg_improvement = sum(cache_improvements) / len(cache_improvements) if cache_improvements else 0
        
        logger.info(f"Average First Search Time: {avg_first:.2f}ms")
        logger.info(f"Average Cached Search Time: {avg_second:.2f}ms")
        logger.info(f"Average Cache Improvement: {avg_improvement:.2f}x faster")
        
        # Performance comparison with Postman
        logger.info(f"\nPostman Performance: 80-125ms")
        logger.info(f"Optimized First Search: {avg_first:.2f}ms")
        logger.info(f"Optimized Cached Search: {avg_second:.2f}ms")
        
        if avg_first <= 300:
            logger.info("✅ First search performance is good (≤300ms)")
        else:
            logger.info("⚠️ First search performance needs improvement (>300ms)")
        
        if avg_second <= 50:
            logger.info("✅ Cached search performance is excellent (≤50ms)")
        else:
            logger.info("⚠️ Cached search performance needs improvement (>50ms)")
        
        # Cache hit analysis
        cache_hits = len([r for r in results if "Cache HIT" in str(r)])
        cache_misses = len([r for r in results if "Cache MISS" in str(r)])
        
        logger.info(f"\nCache Statistics:")
        logger.info(f"Cache Hits: {cache_hits}")
        logger.info(f"Cache Misses: {cache_misses}")
        logger.info(f"Cache Hit Rate: {cache_hits/(cache_hits+cache_misses)*100:.1f}%")
        
        return {
            "avg_first_search": avg_first,
            "avg_cached_search": avg_second,
            "avg_improvement": avg_improvement,
            "cache_hit_rate": cache_hits/(cache_hits+cache_misses)*100
        }

def main():
    """Main test function."""
    # Configuration
    API_URL = "http://192.168.68.111:8000/api/method/textile_plus.overrides.api.product.search_product"
    API_KEY = ""  # Add your API key if needed
    
    logger.info("Starting Product Search Performance Test")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Timestamp: {datetime.now()}")
    
    # Create test instance
    tester = ProductSearchPerformanceTest(API_URL, API_KEY)
    
    # Run tests
    results = tester.test_multiple_searches(iterations=2)
    
    # Analyze results
    analysis = tester.analyze_results(results)
    
    # Save results to file
    output_file = f"product_search_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_url": API_URL,
            "results": results,
            "analysis": analysis
        }, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Test completed!")

if __name__ == "__main__":
    main() 