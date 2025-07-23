# Roll Time Fix Summary

## Problem Description

When the first product was rolled and printed, the roll time did not appear in the print output. This was because:

1. `roll_start_time` was only initialized when length reached 0.01 (indicating a new product cycle)
2. For the first product, if the user printed immediately without length reaching 0.01 first, `roll_start_time` remained `None`
3. This resulted in roll time being 0.0 during print

## Root Cause Analysis

The issue was in the roll time logic in `monitoring/ui/main_window.py`:

### Before Fix:
```python
# roll_start_time was only set when length = 0.01
if length >= 0.005 and length <= 0.015 and not self.is_new_product_started:
    self.roll_start_time = current_time  # Only set here

# During print, roll time calculation:
roll_time = 0.0
if hasattr(self, 'roll_start_time') and self.roll_start_time:
    roll_time = (current_time - self.roll_start_time).total_seconds()

# roll_start_time was NOT reset after print
# This caused roll time to accumulate for subsequent prints
```

### Problems:
1. **First Product Issue**: `roll_start_time` was `None` for first product if length never reached 0.01
2. **Accumulating Roll Time**: `roll_start_time` was not reset after print, causing roll time to accumulate
3. **Incorrect Logic**: Roll time should stop and restart for each print, not continue accumulating

## Solution Implemented

### 1. Initialize roll_start_time on First Data

**File**: `monitoring/ui/main_window.py`
**Function**: `handle_data()`

```python
# Initialize roll_start_time on first data if not set
if hasattr(self, 'roll_start_time') and self.roll_start_time is None:
    from datetime import datetime
    self.roll_start_time = datetime.now()
    logger.info(f"Initialized roll_start_time on first data: {self.roll_start_time}")
```

**Purpose**: Ensures `roll_start_time` is set as soon as monitoring starts, not just when length reaches 0.01.

### 2. Reset roll_start_time After Print

**File**: `monitoring/ui/main_window.py`
**Function**: `handle_print_logging()`

```python
# Reset roll_start_time after print - roll time should stop and restart for next print
# This ensures each print has its own roll time from the last roll start
if hasattr(self, 'roll_start_time') and self.roll_start_time:
    self.roll_start_time = None
    logger.info(f"Print logged - roll time: {roll_time:.1f}s, roll_start_time reset to None")
else:
    logger.info(f"Print logged - roll time: {roll_time:.1f}s, roll_start_time was already None")
```

**Purpose**: Stops the current roll time and prepares for the next roll cycle.

## Roll Time Logic Flow

### Corrected Flow:

1. **Monitoring Starts**: `roll_start_time` is initialized with current time
2. **Rolling Begins**: User starts rolling the product
3. **Print Occurs**: 
   - Roll time is calculated: `(print_time - roll_start_time)`
   - `roll_start_time` is reset to `None`
4. **Next Roll**: When length reaches 0.01, new `roll_start_time` is set
5. **Next Print**: New roll time is calculated from the new start time

### Key Changes:

1. **Initialization**: `roll_start_time` is set on first data arrival, not just on length = 0.01
2. **Reset After Print**: `roll_start_time` is reset to `None` after each print
3. **Independent Roll Times**: Each print gets its own roll time calculation

## Testing

### Test Script: `tests-integration/test_roll_time_logic_simple.py`

The test verifies:
- ✅ `roll_start_time` initialization works correctly
- ✅ Roll time calculation: `(print_time - roll_start_time)`
- ✅ `roll_start_time` reset after print
- ✅ New `roll_start_time` can be set for subsequent prints
- ✅ Roll time is 0.0 when `roll_start_time` is `None`
- ✅ Roll time calculation works for very short durations

## Benefits

1. **First Product Fix**: Roll time now appears correctly for the first product
2. **Accurate Timing**: Each print shows the correct roll time from the last roll start
3. **Independent Cycles**: Roll time doesn't accumulate across multiple prints
4. **Consistent Behavior**: Roll time logic is now consistent for all products

## Files Modified

- `monitoring/ui/main_window.py`: Main logic fixes
- `tests-integration/test_roll_time_logic_simple.py`: Test verification
- `docs/ROLL_TIME_FIX_SUMMARY.md`: This documentation

## Verification

To verify the fix works:

1. Start the application
2. Connect to the roll machine
3. Print the first product - roll time should now appear
4. Print subsequent products - each should have its own roll time
5. Check the logging table - roll time should be accurate for all entries

The fix ensures that roll time is properly calculated and displayed for all products, including the first one. 