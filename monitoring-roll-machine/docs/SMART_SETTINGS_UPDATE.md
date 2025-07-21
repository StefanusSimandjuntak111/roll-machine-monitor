# Smart Settings Update Feature

## Overview

Smart Settings Update adalah fitur yang memungkinkan aplikasi untuk mengupdate settings dengan cara yang cerdas, dimana:

1. **Display settings** (length tolerance, decimal format, rounding) diupdate **tanpa restart**
2. **Port settings** (serial_port, baudrate) memerlukan **restart monitoring**
3. **Settings baru hanya berpengaruh pada data saat ini dan masa depan**, tidak mengubah data historis

## 🎯 **Tujuan**

- **Minimal interruption**: Display settings update tanpa putus koneksi
- **Data integrity**: Data historis tidak terpengaruh settings baru
- **User experience**: Feedback yang jelas tentang jenis update yang dilakukan
- **Performance**: Hanya restart jika benar-benar diperlukan

## 🔧 **Implementasi**

### **1. Kategorisasi Settings**

#### **Settings yang TIDAK PERLU Restart (Display Settings):**
- `length_tolerance`: Persentase toleransi panjang
- `decimal_points`: Jumlah desimal
- `rounding`: Metode pembulatan (round, ceil, floor)

#### **Settings yang PERLU Restart (Port Settings):**
- `serial_port`: Port COM
- `baudrate`: Kecepatan komunikasi

### **2. Smart Update Logic**

```python
def _needs_monitoring_restart(self, settings: Dict[str, Any]) -> bool:
    """Check if settings require monitoring restart."""
    restart_settings = ['serial_port', 'baudrate']
    return any(key in settings for key in restart_settings)
```

### **3. Settings Timestamp Tracking**

Setiap perubahan settings disimpan timestamp-nya untuk tracking:

```python
def _update_display_settings(self):
    """Update display settings without restart - only affects current and future data."""
    # Store settings change timestamp
    self.settings_changed_at = datetime.now()
    
    # Update Length Print card immediately with new settings for current data
    if hasattr(self, 'last_data'):
        self.handle_data(self.last_data)
```

### **4. Data Logging dengan Settings Timestamp**

Setiap entry di logging table menyimpan timestamp settings yang aktif saat data disimpan:

```python
def log_production_data(self, 
                      product_name: str,
                      product_code: str,
                      product_length: float,
                      batch: str,
                      cycle_time: float | None,
                      roll_time: float,
                      settings_timestamp: str | None = None):
    """Log production data with settings timestamp"""
    data = {
        # ... other fields ...
        'settings_timestamp': settings_timestamp  # When settings were last changed
    }
```

## 📊 **Flow Diagram**

```
User Changes Settings
         ↓
Settings Categorized
         ↓
    ┌─────────────┐
    │ Port Settings │ → Kill Port → Restart Monitoring
    └─────────────┘
         ↓
    ┌─────────────┐
    │Display Settings│ → Update Immediately → No Restart
    └─────────────┘
         ↓
Store Settings Timestamp
         ↓
Update Length Print Card
         ↓
Show Success Message
```

## 🎮 **User Experience**

### **Display Settings Update:**
```
✅ Settings Updated

Display settings have been updated successfully!

Length tolerance and formatting are now active.

New settings apply to current and future products only.

No connection interruption.
```

### **Port Settings Update:**
```
✅ Settings Updated

Port settings have been updated.

Monitoring has been restarted with new configuration.

New settings will apply to current and future products only.
```

## 🔄 **Data Flow**

### **1. Current Data Update**
- Length Print card diupdate langsung dengan settings baru
- Product form mendapat nilai Length Print (dengan toleransi)
- Tidak ada gap data atau interruption

### **2. Historical Data Protection**
- Data lama tetap menggunakan settings lama
- Settings timestamp disimpan untuk setiap entry
- Tidak ada retroactive update

### **3. Future Data Consistency**
- Semua data baru menggunakan settings terbaru
- Konsistensi dijamin melalui settings timestamp

## 🧪 **Testing**

### **Test Cases:**

1. **Display Settings Update:**
   - Length tolerance berubah → Length Print update langsung
   - Decimal format berubah → Format update langsung
   - Rounding method berubah → Pembulatan update langsung

2. **Port Settings Update:**
   - Serial port berubah → Monitoring restart
   - Baudrate berubah → Monitoring restart

3. **Mixed Settings Update:**
   - Port + Display settings → Restart required
   - Multiple display settings → No restart

4. **Data Integrity:**
   - Historical data tidak terpengaruh
   - Current data update dengan settings baru
   - Future data konsisten dengan settings baru

## 📝 **Code Examples**

### **Smart Settings Update:**
```python
@Slot(dict)
def handle_settings_update(self, settings: Dict[str, Any]):
    """Handle settings updates with smart restart logic."""
    self.config.update(settings)
    save_config(self.config)
    
    needs_restart = self._needs_monitoring_restart(settings)
    
    if needs_restart:
        # Port settings changed - need restart
        self.kill_port_connection()
        self.toggle_monitoring()
        self.show_kiosk_dialog("information", "Settings Updated", 
                              "Port settings updated. Monitoring restarted.")
    else:
        # Display settings changed - no restart needed
        self._update_display_settings()
        self.show_kiosk_dialog("information", "Settings Updated",
                              "Display settings updated. No interruption.")
```

### **Length Print with Tolerance:**
```python
def calculate_length_print(self, current_length: float, unit: str) -> str:
    """Calculate length print with tolerance and formatting."""
    tolerance = self.config.get('length_tolerance', 0.0)
    decimal_points = self.config.get('decimal_points', 2)
    rounding = self.config.get('rounding', 'round')
    
    # Apply tolerance: length_display = length_input * (1 - tolerance_percent / 100)
    adjusted_length = current_length * (1 - tolerance / 100)
    
    # Apply rounding
    if rounding == 'ceil':
        adjusted_length = math.ceil(adjusted_length * 10**decimal_points) / 10**decimal_points
    elif rounding == 'floor':
        adjusted_length = math.floor(adjusted_length * 10**decimal_points) / 10**decimal_points
    else:  # round
        adjusted_length = round(adjusted_length, decimal_points)
    
    # Format with unit
    unit_symbol = 'm' if unit.lower() == 'meter' else 'yd'
    return f"{adjusted_length:.{decimal_points}f} {unit_symbol}"
```

## 🚀 **Benefits**

### **✅ Keuntungan:**
1. **No interruption**: Display settings update tanpa putus koneksi
2. **Data integrity**: Historical data tidak terpengaruh
3. **Better UX**: Feedback yang jelas dan tepat
4. **Performance**: Hanya restart jika diperlukan
5. **Consistency**: Future data konsisten dengan settings baru

### **❌ Kekurangan Sebelumnya:**
1. **Always restart**: Setiap save settings = restart
2. **Connection loss**: User kehilangan koneksi sementara
3. **Data gap**: Ada gap waktu tanpa data
4. **Poor UX**: Tidak ada feedback yang jelas

## 🔮 **Future Enhancements**

1. **Settings History**: Track semua perubahan settings
2. **Rollback Settings**: Kemampuan untuk rollback ke settings sebelumnya
3. **Settings Profiles**: Multiple settings profiles untuk different scenarios
4. **Auto-save**: Auto-save settings changes
5. **Settings Validation**: Validate settings sebelum apply

## 📋 **Configuration**

### **Settings Categories:**
```json
{
  "display_settings": {
    "length_tolerance": 5.0,
    "decimal_points": 2,
    "rounding": "round"
  },
  "port_settings": {
    "serial_port": "COM4",
    "baudrate": 9600
  }
}
```

### **Settings Timestamp Format:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "settings_timestamp": "2024-01-15T10:25:30.987654"
}
```

## 🎯 **Summary**

Smart Settings Update memberikan pengalaman yang jauh lebih baik dengan:

- **Intelligent categorization** of settings
- **Minimal interruption** for display settings
- **Data integrity** protection for historical data
- **Clear user feedback** for different update types
- **Performance optimization** by avoiding unnecessary restarts

Fitur ini memastikan bahwa aplikasi tetap responsif dan user-friendly sambil mempertahankan integritas data dan konsistensi settings. 