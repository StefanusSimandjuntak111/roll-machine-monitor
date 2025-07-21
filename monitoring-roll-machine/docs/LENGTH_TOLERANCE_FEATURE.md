# 📏 Length Tolerance Feature

## Overview

Fitur **Length Tolerance** memungkinkan pengguna untuk mengatur toleransi panjang pada card **Length Print** berdasarkan pengaturan di **Page Settings**. Card Length Print akan menampilkan panjang yang sudah dikurangi dengan toleransi persentase yang ditentukan.

## 🎯 **Fitur Utama**

### ✅ **Length Print dengan Toleransi**
- **Current Length**: Data aktual dari mesin counter (misal: 100 meter)
- **Length Print**: Hasil perhitungan dengan toleransi untuk ditampilkan di card

### ✅ **Pengaturan Toleransi**
- **Length Tolerance**: Persentase toleransi (0-100%)
- **Decimal Format**: Format desimal (#, #.#, #.##)
- **Rounding Method**: Metode pembulatan (UP/DOWN)

## 📊 **Rumus Perhitungan**

```
length_display = length_input * (1 - tolerance_percent / 100)
```

### **Contoh Perhitungan:**

| Current Length | Tolerance | Rumus | Hasil | Format | Length Print |
|----------------|-----------|-------|-------|--------|--------------|
| 100.0 m | 5% | 100 × (1 - 5/100) | 95.0 | #.# | 95.0 m |
| 100.0 m | 3% | 100 × (1 - 3/100) | 97.0 | #.## | 97.00 m |
| 100.0 m | 10% | 100 × (1 - 10/100) | 90.0 | # | 90 m |
| 1.41 m | 5% | 1.41 × (1 - 5/100) | 1.3395 | #.## UP | 1.34 m |

## ⚙️ **Konfigurasi Settings**

### **Page Settings Tab**

#### **1. Length Tolerance**
- **Input**: Persentase toleransi (0-100%)
- **Default**: 3%
- **Contoh**: 5% = pengurangan 5% dari panjang aktual

#### **2. Decimal Format**
- **#**: Tanpa desimal (67 Meter)
- **#.#**: 1 desimal (67.0 Meter)  
- **#.##**: 2 desimal (66.95 Meter)

#### **3. Rounding Method**
- **UP**: Pembulatan ke atas (ceil)
- **DOWN**: Pembulatan ke bawah (floor)

### **Preview Real-time**
Settings dialog menampilkan preview hasil perhitungan dengan pengaturan saat ini.

## 🔧 **Implementasi Teknis**

### **1. Main Window (`monitoring/ui/main_window.py`)**

#### **Method `calculate_length_print()`**
```python
def calculate_length_print(self, current_length: float, unit: str) -> str:
    """Calculate length print with tolerance based on settings."""
    # Get tolerance settings from config
    tolerance_percent = self.config.get("length_tolerance", 0.0)
    decimal_points = self.config.get("decimal_points", 1)
    rounding_method = self.config.get("rounding", "UP")
    
    # Apply tolerance formula
    length_with_tolerance = current_length * (1 - tolerance_percent / 100)
    
    # Apply rounding method
    if rounding_method == "UP":
        # Ceiling function
        if decimal_points == 0:
            length_with_tolerance = math.ceil(length_with_tolerance)
        elif decimal_points == 1:
            length_with_tolerance = math.ceil(length_with_tolerance * 10) / 10
        elif decimal_points == 2:
            length_with_tolerance = math.ceil(length_with_tolerance * 100) / 100
    
    # Format and return
    format_str = f"{{:.{decimal_points}f}}"
    formatted_length = format_str.format(length_with_tolerance)
    return f"{formatted_length} {unit}"
```

#### **Method `handle_data()`**
```python
def handle_data(self, data: Dict[str, Any]):
    # Calculate length print with tolerance
    fields = data.get('fields', {})
    current_count = fields.get('current_count', 0.0)
    unit = fields.get('unit', 'meter')
    
    # Calculate length print with tolerance
    length_print_text = self.calculate_length_print(current_count, unit)
    
    # Add length print to data for monitoring view
    data['length_print_text'] = length_print_text
    data['length_print_value'] = current_count
    
    # Update monitoring view
    self.monitoring_view.update_data(data)
```

### **2. Monitoring View (`monitoring/ui/monitoring_view.py`)**

#### **Method `update_data()`**
```python
def update_data(self, data: Dict[str, Any]):
    # Display length print with tolerance (calculated in main_window)
    length_print_text = data.get('length_print_text', '0.00 m')
    self.target_value_label.setText(length_print_text)
```

### **3. Settings Dialog (`monitoring/ui/settings_dialog.py`)**

#### **Method `update_conversion_preview()`**
```python
def update_conversion_preview(self):
    """Update the length print preview based on current settings."""
    # Get current values
    tolerance = float(self.tolerance_input.text() or "3")
    decimal_format = self.decimal_combo.currentText()
    rounding = "UP" if self.round_up_radio.isChecked() else "DOWN"
    
    # Apply tolerance formula
    base_value = 100.0
    adjusted_value = base_value * (1 - tolerance / 100)
    
    # Apply rounding method
    # ... rounding logic ...
    
    # Update preview
    self.conversion_preview.setText(f"{formatted_value} Meter")
```

## 📋 **Test Cases**

### **Test Scenarios**
1. **No tolerance (0%)**: Length print = Current length
2. **5% tolerance, UP rounding**: 100m → 95.0m
3. **3% tolerance, 2 decimals**: 100m → 97.00m
4. **10% tolerance, 0 decimals**: 100m → 90m
5. **Yard unit**: 100 yard → 95.0 yard
6. **Real data**: 1.41m → 1.34m (5% tolerance, UP rounding)

### **Edge Cases**
- **Negative tolerance**: Treated as 0% tolerance
- **High tolerance (50%)**: 100m → 50m
- **Zero length**: 0m → 0m
- **Invalid settings**: Fallback to current length

## 🎨 **UI Components**

### **Card Display**
```
┌─────────────────┬─────────────────┬─────────────────┐
│ Current Length  │ Current Speed   │ Current Shift   │
│ 1.41 m          │ 0.00 m/min      │ Aktif           │
├─────────────────┼─────────────────┼─────────────────┤
│ Product Code    │ Batch Number    │ Length Print    │
│ ABC123          │ B001            │ 1.34 m          │ ← With tolerance
└─────────────────┴─────────────────┴─────────────────┘
```

### **Settings Dialog**
```
┌─────────────────────────────────────┐
│ Page Display Settings               │
├─────────────────────────────────────┤
│ Length Tolerance (%): [5]           │
│ Decimal Format: [#.## ▼]            │
│ Rounding Method: (●) UP ( ) DOWN    │
│                                     │
│ Length Print Preview:               │
│ [95.00 Meter]                       │
└─────────────────────────────────────┘
```

## 🔄 **Data Flow**

```
Machine Data → Parser → Main Window → Calculate Tolerance → Monitoring View
     ↓              ↓           ↓              ↓                    ↓
Current Length → Parsed → handle_data() → length_print → Length Print Card
     ↓              ↓           ↓              ↓                    ↓
1.41 m → 1.41 m → 1.41 m → 1.34 m → "1.34 m"
```

## 📝 **Configuration**

### **config.json**
```json
{
    "length_tolerance": 5.0,
    "decimal_points": 2,
    "rounding": "UP"
}
```

### **Default Values**
- **length_tolerance**: 3.0%
- **decimal_points**: 1 (#.# format)
- **rounding**: "UP"

## 🧪 **Testing**

### **Test Script**
```bash
python tests-integration/test_length_tolerance_simple.py
```

### **Test Results**
```
🧪 Testing Length Tolerance Calculation
==================================================
📊 Results: 7 passed, 0 failed
🎉 All tests passed!
```

## 🚀 **Usage**

### **1. Set Tolerance**
1. Buka **Settings** → **Page Settings**
2. Masukkan **Length Tolerance** (misal: 5%)
3. Pilih **Decimal Format** (misal: #.##)
4. Pilih **Rounding Method** (misal: UP)
5. Klik **Save**

### **2. Monitor Length Print**
- Card **Length Print** akan menampilkan panjang dengan toleransi
- Preview di settings menunjukkan hasil perhitungan
- Perubahan settings langsung terlihat di preview

### **3. Real-time Updates**
- Data dari mesin otomatis dihitung dengan toleransi
- Length Print card update real-time
- Settings tersimpan dan digunakan untuk semua perhitungan

## 🔮 **Future Enhancements**

### **Planned Features**
- **Dynamic tolerance**: Toleransi berbeda per product
- **Tolerance history**: Log perubahan toleransi
- **Advanced rounding**: Custom rounding rules
- **Unit conversion**: Auto-convert antara meter/yard

### **Performance Improvements**
- **Caching**: Cache hasil perhitungan
- **Batch processing**: Process multiple values
- **Async calculation**: Non-blocking calculations

## 📞 **Support**

### **Common Issues**
1. **Tolerance tidak terlihat**: Pastikan tolerance > 0%
2. **Format tidak sesuai**: Check decimal_points setting
3. **Rounding salah**: Verify rounding method
4. **Unit tidak sesuai**: Check unit detection

### **Troubleshooting**
- Restart aplikasi setelah ubah settings
- Check config.json untuk settings yang tersimpan
- Verify data parsing dari mesin
- Test dengan tolerance 0% untuk baseline 