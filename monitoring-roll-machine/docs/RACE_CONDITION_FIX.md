# Race Condition Fix untuk Product Search

## Overview
Perbaikan race condition yang menyebabkan product code berubah secara otomatis saat rapid typing dan multiple API calls.

## Masalah yang Ditemukan

### **Race Condition Scenario:**
1. User mengetik "BD-1" → Search worker 1 dimulai
2. User mengetik "BD-2" → Search worker 2 dimulai  
3. User mengetik "BD-5" → Search worker 3 dimulai
4. User mengetik "BD-1" → Search worker 4 dimulai
5. **Masalah**: Worker yang selesai terakhir akan meng-override product code

### **Gejala:**
- Product code berubah otomatis dari "BD-1" ke "BD-5"
- UI tidak konsisten dengan input user
- Multiple API calls berjalan bersamaan
- Memory leaks dari worker threads yang tidak di-cleanup

## Root Cause Analysis

### 1. **No Thread Safety**
```python
# SEBELUM: Tidak ada tracking request
self._search_worker = ProductSearchWorker(product_code, api_url, headers)
```

### 2. **No Request Tracking**
```python
# SEBELUM: Tidak ada ID untuk membedakan request
def _on_search_completed(self, product_info):
    self._populate_form_from_api(product_info)  # Bisa dari thread lama
```

### 3. **No User Input Validation**
```python
# SEBELUM: Tidak cek apakah user masih mengetik
def _populate_form_from_api(self, product_info):
    self.product_code.setText(product_info.get("product_code", ""))  # Overwrite user input
```

## Solusi yang Diterapkan

### 1. **Request ID Tracking**
```python
class ProductSearchWorker(QThread):
    def __init__(self, product_code: str, api_url: str, headers: Dict[str, str], request_id: str):
        self.request_id = request_id  # Unique ID untuk setiap request
        
    def run(self):
        # Add request_id to product_info for thread safety
        product_info["_request_id"] = self.request_id
        self.search_completed.emit(product_info)
```

### 2. **Thread Safety Checks**
```python
def _on_search_completed(self, product_info: Dict[str, Any]):
    # Thread safety check - only process if this is the current request
    request_id = product_info.get("_request_id")
    current_user_input = self.product_code.text().strip()
    
    # Check if this result is still relevant
    if (request_id != self._current_request_id and 
        request_id != "cache" and 
        current_user_input != self._last_user_input):
        logger.info(f"Ignoring stale search result for request {request_id}")
        return
    
    # Check if user input has changed since this search started
    if current_user_input != self._last_user_input:
        logger.info(f"Ignoring search result - user input changed")
        return
```

### 3. **Proper Worker Management**
```python
def _cancel_current_search(self):
    """Cancel current search worker and cleanup."""
    if self._search_worker and self._search_worker.isRunning():
        logger.info("Cancelling current search worker")
        self._search_worker.terminate()
        self._search_worker.wait(1000)  # Wait up to 1 second
        if self._search_worker.isRunning():
            logger.warning("Force killing search worker")
            self._search_worker.terminate()
            self._search_worker.wait()
    
    # Reset current request ID
    self._current_request_id = None
```

### 4. **User Input Protection**
```python
def _populate_form_from_api(self, product_info: Dict[str, Any]):
    # Thread safety check - don't update if user is currently typing
    current_user_input = self.product_code.text().strip()
    if current_user_input != self._last_user_input:
        logger.info(f"Skipping form population - user input changed")
        return
    
    # Don't overwrite product_code if user is still typing
    if not self.product_code.hasFocus() or current_user_input == self._last_user_input:
        self.product_code.setText(product_info.get("product_code", ""))
```

### 5. **Request ID Generation**
```python
def _perform_product_search(self):
    # Generate a unique request ID
    import uuid
    request_id = str(uuid.uuid4())
    self._current_request_id = request_id
    
    # Start new search in background thread with new format
    self._search_worker = ProductSearchWorker(product_code, api_url, headers, request_id)
```

## Workflow Perbaikan

### **Sebelum Fix:**
```
User: BD-1 → Worker1 (100ms) → UI: BD-1 ✅
User: BD-2 → Worker2 (80ms)  → UI: BD-2 ✅  
User: BD-5 → Worker3 (120ms) → UI: BD-5 ✅
User: BD-1 → Worker4 (90ms)  → UI: BD-5 ❌ (Worker3 selesai terakhir)
```

### **Sesudah Fix:**
```
User: BD-1 → Worker1 (ID:abc123) (100ms) → UI: BD-1 ✅
User: BD-2 → Worker2 (ID:def456) (80ms)  → UI: BD-2 ✅
User: BD-5 → Worker3 (ID:ghi789) (120ms) → UI: BD-5 ✅
User: BD-1 → Worker4 (ID:jkl012) (90ms)  → UI: BD-1 ✅ (Worker4 adalah current request)
```

## Implementasi Detail

### **1. Request Tracking Variables**
```python
# Thread safety for preventing race conditions
self._current_request_id = None
self._last_user_input = ""
```

### **2. Input Change Detection**
```python
def _on_product_code_changed(self):
    # Track current user input
    self._last_user_input = self.product_code.text().strip()
    self._search_timer.start(100)
```

### **3. Stale Result Detection**
```python
# Check if this result is still relevant
if (request_id != self._current_request_id and 
    request_id != "cache" and 
    current_user_input != self._last_user_input):
    logger.info(f"Ignoring stale search result")
    return
```

### **4. Cache Integration**
```python
# Cache the result (only for API results, not cache hits)
if request_id != "cache":
    # Remove request_id before caching
    cache_product_info = product_info.copy()
    cache_product_info.pop("_request_id", None)
    self._cache_product(product_code, cache_product_info)
```

## Testing

### **Test Scenarios:**
1. **Rapid Typing**: BD-1 → BD-2 → BD-5 → BD-1
2. **Very Rapid**: Multiple codes dengan delay 20ms
3. **Slow then Fast**: Slow typing lalu rapid changes

### **Expected Results:**
- ✅ Final result selalu match dengan input terakhir
- ✅ Stale results di-ignore
- ✅ No memory leaks
- ✅ UI konsisten dengan user input

### **Test Script:**
```bash
python tests-integration/test_race_condition_fix.py
```

## Performance Impact

### **Memory Usage:**
- Minimal overhead dari request ID tracking
- Proper cleanup mencegah memory leaks
- Cache tetap berfungsi optimal

### **Response Time:**
- Tidak ada impact pada response time
- Thread safety checks sangat cepat
- Cache hits tetap instant

### **User Experience:**
- ✅ No more automatic product code changes
- ✅ UI selalu konsisten dengan input
- ✅ Smooth typing experience
- ✅ Reliable search results

## Monitoring dan Debugging

### **Log Messages:**
```python
logger.info(f"Ignoring stale search result for request {request_id}")
logger.info(f"Ignoring search result - user input changed")
logger.info(f"Processing valid result for '{product_code}'")
```

### **Debug Information:**
- Request ID tracking
- User input change detection
- Worker thread management
- Cache hit/miss statistics

## Future Enhancements

### **1. Advanced Threading**
- Thread pool untuk multiple searches
- Priority-based request handling
- Automatic retry mechanism

### **2. Enhanced Caching**
- Request deduplication
- Cache warming
- Cache invalidation strategies

### **3. UI Improvements**
- Visual feedback untuk active searches
- Progress indicators
- Search cancellation UI

## Troubleshooting

### **Jika Masih Ada Race Condition:**
1. Check log messages untuk stale results
2. Verify request ID generation
3. Monitor user input tracking
4. Check worker cleanup

### **Performance Issues:**
1. Monitor memory usage
2. Check thread cleanup
3. Verify cache efficiency
4. Analyze API response times 