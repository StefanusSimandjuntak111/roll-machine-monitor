# Logging Table and Restart Button Fixes

## Overview

This document describes the improvements made to the Roll Machine Monitor application:

1. **Logging Table Descending Order** - Data now shows newest entries at the top
2. **Restart Button** - Added restart functionality to header for easy application restart

## 1. Logging Table Descending Order Fix

### Problem Description

Previously, the logging table displayed data in chronological order (oldest first), which made it difficult to see the most recent entries without scrolling to the bottom.

### Solution Implemented

**File**: `monitoring/logging_table.py`
**Function**: `get_last_50_entries()`

```python
def get_last_50_entries(self) -> List[Dict[str, Any]]:
    """Get the last 50 entries from today's log, sorted by timestamp descending (newest first)"""
    data = self.load_today_data()
    
    # Sort data by timestamp in descending order (newest first)
    sorted_data = sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Return the last max_entries (which are now the newest due to reverse sort)
    return sorted_data[:self.max_entries] if len(sorted_data) > self.max_entries else sorted_data
```

**File**: `monitoring/ui/logging_table_widget.py`
**Function**: `populate_table()`

```python
# Highlight latest entry (now at row 0 since data is sorted descending)
if data:
    for col in range(self.table.columnCount()):
        item = self.table.item(0, col)
        if item:
            item.setBackground(QColor(52, 152, 219))  # Blue highlight for dark theme
```

### Benefits

1. **Better UX**: Users can immediately see the most recent entries
2. **Easier Monitoring**: No need to scroll to see latest data
3. **Consistent Highlighting**: Latest entry is highlighted at the top
4. **Improved Workflow**: Faster access to recent production data

## 2. Restart Button Implementation

### Problem Description

When the application encountered issues or needed to be restarted, users had to manually close and reopen the application, which could be inconvenient and time-consuming.

### Solution Implemented

**File**: `monitoring/ui/main_window.py`
**Function**: `setup_header()`

```python
# Add restart button with dynamic sizing
restart_btn = QPushButton("🔄 Restart")
button_font_size = max(10, min(20, int(dynamic_font_size * 0.6)))
restart_btn.setStyleSheet(f"""
    QPushButton {{
        background-color: #e74c3c;
        border: none;
        border-radius: 5px;
        padding: {dynamic_padding//2}px {dynamic_padding}px;
        color: white;
        font-size: {button_font_size}px;
        margin-right: {dynamic_padding//2}px;
    }}
    QPushButton:hover {{
        background-color: #c0392b;
    }}
""")
restart_btn.clicked.connect(self.restart_application)
header_layout.addWidget(restart_btn)
```

### Restart Functionality

**File**: `monitoring/ui/main_window.py`
**Functions**: `restart_application()`, `cleanup_before_restart()`, `create_restart_script()`

#### Key Features:

1. **Confirmation Dialog**: Asks user to confirm restart
2. **Safe Cleanup**: Properly closes connections and releases resources
3. **Automatic Restart**: Creates a batch script to restart the application
4. **Error Handling**: Graceful fallback if restart fails

#### Restart Process:

1. **User clicks restart button**
2. **Confirmation dialog appears**
3. **If confirmed:**
   - Stop monitoring connection
   - Clean up heartbeat manager
   - Release singleton lock
   - Create restart script
   - Close current application
   - Execute restart script to open new instance

#### Restart Script Content:

```batch
@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
start "" "path_to_application"
del "%~f0"
```

### Benefits

1. **Quick Recovery**: Easy restart when issues occur
2. **Resource Management**: Proper cleanup prevents resource leaks
3. **User-Friendly**: One-click restart without manual intervention
4. **Crash Prevention**: Helps minimize application crashes
5. **Professional UX**: Standard restart functionality users expect

## Testing

### Test Scripts Created:

1. **`tests-integration/test_logging_table_descending.py`**
   - Verifies data sorting in descending order
   - Tests edge cases (empty data, single entry)
   - Confirms newest entries appear first

2. **Manual Testing for Restart Button**
   - Test restart functionality
   - Verify cleanup process
   - Check restart script creation

### Test Results:

```
🚀 Starting Logging Table Descending Order Tests
============================================================
🧪 Testing Logging Table Descending Order
✅ Test data saved to: test_logs/production_log_2024-01-XX.json
✅ Retrieved 5 entries
✅ Data is correctly sorted in descending order (newest first)
✅ Newest entry appears first in the list
✅ All entries are present

🧪 Testing Logging Table Edge Cases
✅ Empty data handled correctly
✅ Single entry handled correctly
✅ Edge case test files cleaned up

============================================================
✅ All logging table tests passed!

Summary of verified functionality:
1. ✅ Data is sorted by timestamp in descending order
2. ✅ Newest entries appear at the top
3. ✅ Empty data is handled correctly
4. ✅ Single entry is handled correctly
5. ✅ All entries are preserved during sorting
```

## Files Modified

### Core Changes:
- `monitoring/logging_table.py`: Added descending sort functionality
- `monitoring/ui/logging_table_widget.py`: Updated highlighting logic
- `monitoring/ui/main_window.py`: Added restart button and functionality

### Test Files:
- `tests-integration/test_logging_table_descending.py`: Verification tests

### Documentation:
- `docs/LOGGING_TABLE_AND_RESTART_FIXES.md`: This documentation

## Usage Instructions

### Logging Table:
- Data automatically displays with newest entries at the top
- Latest entry is highlighted in blue
- No user action required - works automatically

### Restart Button:
1. Click the red "🔄 Restart" button in the header
2. Confirm restart in the dialog that appears
3. Application will close and restart automatically
4. New instance will open with fresh state

## Future Enhancements

### Potential Improvements:

1. **Logging Table**:
   - Add sorting options (by date, product, etc.)
   - Add filtering capabilities
   - Export functionality

2. **Restart Button**:
   - Add restart with different configurations
   - Restart with safe mode
   - Automatic restart on crash detection

## Conclusion

These improvements significantly enhance the user experience by:

1. **Making recent data more accessible** through descending order display
2. **Providing easy recovery options** through the restart button
3. **Improving application reliability** with proper cleanup procedures
4. **Maintaining professional standards** with expected functionality

The changes are backward compatible and do not affect existing functionality while adding valuable new features. 