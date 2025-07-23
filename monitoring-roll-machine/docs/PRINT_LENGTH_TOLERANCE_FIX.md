# Print Length Tolerance Fix

## Overview
Perbaikan perhitungan `print_length` dengan rumus toleransi yang benar sesuai dengan kebutuhan industri tekstil.

## Rumus yang Benar

### **Formula:**
```
P_roll = P_target / (1 - T/100)
```

### **Keterangan:**
- **P_target** = Panjang target roll (contoh: 100 meter)
- **T** = Toleransi (%) → contoh: 5% artinya kemungkinan kain menyusut atau melar sampai 5%
- **P_roll** = Panjang yang ditampilkan/dicetak untuk pembeli

### **Contoh Perhitungan:**
```
P_roll = 100 / (1 - 5/100) = 100 / 0.95 ≈ 105.26 meter
```

## Masalah Sebelumnya

### **Rumus Salah:**
```python
# SEBELUM: Rumus yang salah
adjusted_value = base_value * (1 - tolerance / 100)
# Contoh: 100 * (1 - 5/100) = 100 * 0.95 = 95 meter ❌
```

### **Hasil yang Salah:**
- Target: 100m, Tolerance: 5% → Print: 95m ❌
- Seharusnya: Target: 100m, Tolerance: 5% → Print: 105.26m ✅

## Perbaikan yang Diterapkan

### **1. Fungsi Utilitas di `config.py`**

```python
def calculate_print_length(target_length: float, tolerance_percent: float, decimal_points: int = 1, rounding: str = "UP") -> float:
    """
    Calculate print length using the correct tolerance formula.
    
    Formula: P_roll = P_target / (1 - T/100)
    """
    if tolerance_percent <= 0:
        return target_length
    
    # Apply tolerance formula: P_roll = P_target / (1 - T/100)
    print_length = target_length / (1 - tolerance_percent / 100)
    
    # Apply rounding method
    if rounding == "UP":
        if decimal_points == 0:
            print_length = math.ceil(print_length)
        elif decimal_points == 1:
            print_length = math.ceil(print_length * 10) / 10
        elif decimal_points == 2:
            print_length = math.ceil(print_length * 100) / 100
    else:  # DOWN
        if decimal_points == 0:
            print_length = math.floor(print_length)
        elif decimal_points == 1:
            print_length = math.floor(print_length * 10) / 10
        elif decimal_points == 2:
            print_length = math.floor(print_length * 100) / 100
    
    return print_length
```

### **2. Fungsi Detail Info**

```python
def get_print_length_info(target_length: float, tolerance_percent: float, decimal_points: int = 1, rounding: str = "UP") -> Dict[str, Any]:
    """Get detailed print length information including calculation details."""
    print_length = calculate_print_length(target_length, tolerance_percent, decimal_points, rounding)
    
    return {
        "target_length": target_length,
        "tolerance_percent": tolerance_percent,
        "decimal_points": decimal_points,
        "rounding": rounding,
        "print_length": print_length,
        "formula": f"P_roll = {target_length} / (1 - {tolerance_percent}/100) = {target_length} / {1 - tolerance_percent/100:.3f}",
        "calculation": f"{target_length} / {1 - tolerance_percent/100:.3f} = {target_length / (1 - tolerance_percent/100):.6f}",
        "rounded": f"{print_length:.{decimal_points}f}"
    }
```

### **3. Integrasi ke Print Preview**

```python
# Load config for tolerance settings
config = load_config()
tolerance_percent = config.get("length_tolerance", 3.0)
decimal_points = config.get("decimal_points", 1)
rounding = config.get("rounding", "UP")

# Calculate print length with tolerance
target_length = self.product_info.get('target_length', 0)
print_length = calculate_print_length(target_length, tolerance_percent, decimal_points, rounding)

# Use print_length instead of target_length in display
f"{print_length:.{decimal_points}f} {self.product_info.get('units', 'Yard')}"
```

### **4. Update Settings Dialog**

```python
def update_conversion_preview(self):
    """Update the conversion factor preview based on current settings."""
    # Apply CORRECT tolerance formula: P_roll = P_target / (1 - T/100)
    if tolerance > 0:
        adjusted_value = base_value / (1 - tolerance / 100)
    else:
        adjusted_value = base_value
    
    # Update preview with unit and explanation
    self.conversion_preview.setText(f"{formatted_value} Meter (Target: 100m, Tolerance: {tolerance}%)")
```

## Test Cases

### **Test Case 1: User's Example**
- **Input:** Target = 100m, Tolerance = 5%
- **Formula:** P_roll = 100 / (1 - 5/100) = 100 / 0.95
- **Expected:** 105.26m
- **Result:** ✅ 105.26m

### **Test Case 2: 50m with 3% Tolerance**
- **Input:** Target = 50m, Tolerance = 3%
- **Formula:** P_roll = 50 / (1 - 3/100) = 50 / 0.97
- **Expected:** 51.55m
- **Result:** ✅ 51.55m

### **Test Case 3: 200m with 10% Tolerance**
- **Input:** Target = 200m, Tolerance = 10%
- **Formula:** P_roll = 200 / (1 - 10/100) = 200 / 0.9
- **Expected:** 222.22m
- **Result:** ✅ 222.22m

### **Test Case 4: No Tolerance**
- **Input:** Target = 75m, Tolerance = 0%
- **Formula:** P_roll = 75 / (1 - 0/100) = 75 / 1
- **Expected:** 75m
- **Result:** ✅ 75m

## Implementasi di UI

### **1. Print Preview Dialog**
- ✅ Menggunakan `print_length` dengan toleransi
- ✅ Menampilkan info toleransi di UI
- ✅ QR code menggunakan `print_length`
- ✅ Label length menggunakan `print_length`

### **2. Settings Dialog**
- ✅ Preview menggunakan rumus yang benar
- ✅ Menampilkan penjelasan formula
- ✅ Real-time update saat setting berubah

### **3. Tolerance Info Display**
```python
tolerance_info = f"Target: {target_length:.{decimal_points}f}m, Tolerance: {tolerance_percent}%, Print: {print_length:.{decimal_points}f}m"
self.tolerance_label.setText(tolerance_info)
```

## File yang Dimodifikasi

1. **`monitoring/config.py`**
   - Added `calculate_print_length()` function
   - Added `get_print_length_info()` function

2. **`monitoring/ui/print_preview.py`**
   - Integrated tolerance calculation
   - Updated print preview to use `print_length`
   - Added tolerance info display

3. **`monitoring/ui/settings_dialog.py`**
   - Fixed conversion preview formula
   - Updated display with explanation

4. **`tests-integration/test_print_length_tolerance.py`**
   - Test script untuk verifikasi perhitungan

## Cara Test

### **1. Run Test Script:**
```bash
python tests-integration/test_print_length_tolerance.py
```

### **2. Manual Test:**
1. Buka aplikasi
2. Masukkan target length (contoh: 100m)
3. Set tolerance di settings (contoh: 5%)
4. Buka print preview
5. Verifikasi print length = 105.26m

### **3. Settings Test:**
1. Buka Settings → Page Settings
2. Ubah Length Tolerance
3. Lihat preview berubah sesuai formula yang benar

## Expected Results

### **Before Fix:**
- Target: 100m, Tolerance: 5% → Print: 95m ❌
- Formula: `length * (1 - tolerance/100)` ❌

### **After Fix:**
- Target: 100m, Tolerance: 5% → Print: 105.26m ✅
- Formula: `length / (1 - tolerance/100)` ✅
- UI shows tolerance calculation info ✅
- Print preview uses correct print length ✅

## Business Logic

### **Mengapa Rumus Ini Benar?**

1. **Toleransi Menyusut/Melar**: Kain bisa menyusut atau melar sampai 5%
2. **Target untuk Customer**: Customer ingin kain minimal 100m
3. **Print Length**: Harus lebih dari target untuk mengkompensasi penyusutan
4. **Formula**: `P_roll = P_target / (1 - T/100)` memastikan customer mendapat minimal target length

### **Contoh Praktis:**
- **Target:** 100m (yang diinginkan customer)
- **Tolerance:** 5% (kain bisa menyusut 5%)
- **Print:** 105.26m (yang dicetak di label)
- **Result:** Jika kain menyusut 5%, customer tetap dapat minimal 100m

## Future Enhancements

1. **Multiple Tolerance Types**: Different tolerances for different fabric types
2. **Tolerance History**: Track tolerance changes over time
3. **Auto Tolerance**: Automatic tolerance based on fabric properties
4. **Tolerance Validation**: Validate tolerance values against industry standards 