# New Cycle Time Logic - Logika Cycle Time yang Baru

## 🔧 Masalah yang Diperbaiki

**Masalah:** Logika cycle time sebelumnya salah. Cycle time muncul saat print, padahal seharusnya update record produk sebelumnya saat produk berikutnya di-print.

**Logika yang Benar:**
1. **Produk 1**: Cycle time kosong, disimpan `start_time`
2. **Produk 2**: Update cycle time Produk 1 = `start_time_produk_2 - start_time_produk_1`, Produk 2 cycle time kosong
3. **Produk 3**: Update cycle time Produk 2 = `start_time_produk_3 - start_time_produk_2`, Produk 3 cycle time kosong
4. **Close Cycle**: Update cycle time Produk 3 = `close_time - start_time_produk_3`

## 📋 Perubahan yang Dilakukan

### 1. Perbaikan Variable Tracking

**Variable Baru:**
- `product_start_times`: List untuk menyimpan start time setiap produk
- `is_new_product_started`: Flag untuk track apakah produk baru sudah dimulai
- `update_last_entry_cycle_time()`: Method untuk update cycle time di logging table

**Inisialisasi:**
```python
if not hasattr(self, 'cycle_start_time'):
    self.cycle_start_time = None
    self.roll_start_time = None
    self.last_length = 0.0
    self.current_product_info = {}
    self.cycle_count = 0
    self.product_start_times = []  # Store start times for each product
    self.pending_cycle_time = None
    self.is_new_product_started = False  # Track if new product has started
```

### 2. Perbaikan Deteksi Awal Produk

**Deteksi Length Counter == 1:**
```python
# Detect when length counter == 1 (start of new product cycle)
if length >= 0.9 and length <= 1.1 and not self.is_new_product_started:
    # New product cycle started - length counter is at 1
    self.cycle_start_time = current_time
    self.roll_start_time = current_time
    self.cycle_count += 1
    self.is_new_product_started = True
    logger.info(f"New product cycle started - length counter at {length:.2f}m (cycle {self.cycle_count})")
```

**Deteksi Reset Counter:**
```python
# Detect roll length reset to 0 (cycle end - after Reset Counter)
elif self.last_length > 0.1 and length <= 0.1:
    # Roll length reset to 0 - cycle ended, prepare for next product
    self.is_new_product_started = False
    logger.info(f"Cycle ended - roll length reset to {length:.2f}m")
```

### 3. Perbaikan `handle_print_logging()` Method

**Logika Print:**
```python
# For Print button: cycle_time is always None initially
# Cycle time will be calculated when next product starts or Close Cycle is pressed
cycle_time = None

# Store start time for this product (when length == 1)
start_time = self.cycle_start_time if self.cycle_start_time else current_time
self.product_start_times.append(start_time)

# Log the production data with cycle_time = None initially
self.logging_table_widget.add_production_entry(
    product_name=product_name,
    product_code=product_code,
    product_length=product_length,
    batch=batch,
    cycle_time=cycle_time,  # Always None for Print
    roll_time=roll_time
)
```

**Update Cycle Time Produk Sebelumnya:**
```python
# Update previous product's cycle time if this is not the first product
if len(self.product_start_times) > 1:
    previous_product_start = self.product_start_times[-2]  # Previous product start time
    current_product_start = self.product_start_times[-1]   # Current product start time
    previous_cycle_time = (current_product_start - previous_product_start).total_seconds()
    
    # Update the previous product's cycle time in the logging table
    self.logging_table_widget.update_last_entry_cycle_time(previous_cycle_time)
    logger.info(f"Updated previous product cycle time: {previous_cycle_time:.1f}s")
```

### 4. Perbaikan `close_cycle()` Method

**Perhitungan Cycle Time Terakhir:**
```python
# Calculate final cycle time for the last product
cycle_time = None
if hasattr(self, 'product_start_times') and len(self.product_start_times) > 0:
    last_product_start = self.product_start_times[-1]  # Last product start time
    cycle_time = (current_time - last_product_start).total_seconds()
    logger.info(f"Close cycle: Last product started at {last_product_start.strftime('%H:%M:%S')}, current time {current_time.strftime('%H:%M:%S')}")
```

### 5. Perbaikan `reset_counter()` Method

**Reset Semua Variable:**
```python
# Reset cycle time variables
self.cycle_start_time = None
self.roll_start_time = None
self.pending_cycle_time = None
self.current_cycle_start = None
self.last_length = 0.0
self.cycle_count = 0
self.current_product_info = {}  # Reset current product info
self.product_start_times = []  # Reset product start times
self.is_new_product_started = False  # Reset new product flag
logger.info("Cycle time variables reset - ready for new product cycle")
```

## 🔄 Alur Kerja yang Benar

### Skenario 1: Produk Pertama
1. **Length Counter == 1**: 
   - Deteksi `length >= 0.9 and length <= 1.1`
   - Set `cycle_start_time = current_time`
   - Set `is_new_product_started = True`
2. **Print**: 
   - Cycle time = `None` (kosong)
   - `start_time` disimpan di `product_start_times[0]`
   - Record ditambahkan ke logging table dengan cycle time kosong
3. **Hasil**: Produk 1 cycle time kosong

### Skenario 2: Produk Kedua
1. **Reset Counter**: 
   - Length counter reset ke 0
   - Set `is_new_product_started = False`
2. **Length Counter == 1**: 
   - Deteksi produk baru dimulai
   - Set `cycle_start_time = current_time`
   - Set `is_new_product_started = True`
3. **Print**: 
   - `start_time` disimpan di `product_start_times[1]`
   - Update cycle time Produk 1 = `product_start_times[1] - product_start_times[0]`
   - Record Produk 2 ditambahkan dengan cycle time kosong
4. **Hasil**: Produk 1 cycle time ter-update, Produk 2 cycle time kosong

### Skenario 3: Produk Terakhir
1. **Reset Counter**: 
   - Length counter reset ke 0
   - Set `is_new_product_started = False`
2. **Length Counter == 1**: 
   - Deteksi produk baru dimulai
   - Set `cycle_start_time = current_time`
   - Set `is_new_product_started = True`
3. **Print**: 
   - `start_time` disimpan di `product_start_times[2]`
   - Update cycle time Produk 2 = `product_start_times[2] - product_start_times[1]`
   - Record Produk 3 ditambahkan dengan cycle time kosong
4. **Close Cycle**: 
   - Update cycle time Produk 3 = `close_time - product_start_times[2]`
   - Record Produk 3 di-update dengan cycle time final
5. **Hasil**: Produk 2 cycle time ter-update, Produk 3 cycle time ter-update

## 🧪 Testing

**Test Script:** `test_new_cycle_time_logic.py`
- ✅ Simulasi Product 1: Empty cycle time initially
- ✅ Simulasi Product 2: Updates Product 1 cycle time to 60.0s
- ✅ Simulasi Product 3: Updates Product 2 cycle time to 60.0s
- ✅ Simulasi Close Cycle: Updates Product 3 cycle time to 60.0s
- ✅ Test logging table update functionality

**Hasil Test:**
```
🧪 Testing New Cycle Time Logic
📦 Product 1: Length=1 + Print
   Cycle time: Empty (first product)
📦 Product 2: Reset + Length=1 + Print
   Product 1 cycle time updated: 60.0s
   Product 2 cycle time: Empty
📦 Product 3: Reset + Length=1 + Print
   Product 2 cycle time updated: 60.0s
   Product 3 cycle time: Empty
📦 Product 3: Close Cycle (Final Product)
   Product 3 cycle time updated: 60.0s
```

## 📝 Catatan Penting

1. **Cycle time = end_time_produk_sebelumnya - start_time_produk_sebelumnya**
2. **Produk pertama** selalu cycle time kosong sampai produk kedua di-print
3. **Update cycle time** dilakukan saat produk berikutnya di-print
4. **Close Cycle** mengupdate cycle time produk terakhir
5. **Reset counter** mereset semua variable termasuk `product_start_times`
6. **Deteksi produk baru** berdasarkan `length >= 0.9 and length <= 1.1`
7. **Deteksi reset** berdasarkan `length <= 0.1` setelah sebelumnya `> 0.1`

## 🎯 Hasil Akhir

- ✅ **Produk 1 length=1 + print**: Cycle time kosong
- ✅ **Produk 2 reset + length=1 + print**: Update cycle time Produk 1, Produk 2 kosong
- ✅ **Produk 3 reset + length=1 + print**: Update cycle time Produk 2, Produk 3 kosong
- ✅ **Produk 3 close cycle**: Update cycle time Produk 3
- ✅ **Reset counter**: Semua variable di-reset
- ✅ **Logging table update**: Cycle time ter-update di table dan file
- ✅ **Deteksi length counter**: Otomatis deteksi saat length = 1
- ✅ **Deteksi reset**: Otomatis deteksi saat length reset ke 0 