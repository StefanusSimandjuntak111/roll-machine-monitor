# Release Notes v1.2.6 - Enhanced Settings & Port Management

## 🎉 Major Features Added

### ✨ **Enhanced Settings Dialog with Tabbed Interface**

#### **1. Port Settings Tab**
- **Serial Port Selection**: Dropdown dengan auto-refresh
- **Baudrate Selection**: 9600, 19200, 38400, 57600, 115200
- **Refresh Ports Button**: Update daftar port secara real-time
- **Save/Cancel Buttons**: Fungsi lengkap dengan error handling

#### **2. Page Settings Tab**
- **Length Tolerance**: Input persentase (default: 3%)
- **Decimal Format**: Select options (#, #.#, #.##)
- **Rounding Method**: Radio buttons (UP/DOWN)
- **Conversion Factor Preview**: Real-time preview dengan format yang dipilih

#### **3. Port Management Tab** 🆕
- **Connection Status**: Real-time status dengan color coding
- **Kill/Close Port**: Force close koneksi yang stuck
- **Auto Connect**: Otomatis connect ke port yang tersedia
- **Disconnect**: Putus koneksi dengan aman
- **Auto Reconnect**: Reconnect otomatis saat disconnect (1 detik delay)

### 🔧 **Technical Improvements**

#### **Settings Management**
- **Default Config**: Length tolerance 3%, decimal points 1 (#.#), rounding UP
- **Config Persistence**: Settings tersimpan di config.json
- **Error Validation**: Validasi input dengan pesan error yang jelas
- **Backward Compatibility**: Support konfigurasi lama

#### **UI/UX Enhancements**
- **Dark Theme**: Konsisten dengan aplikasi utama
- **Modal Dialog**: Dialog tidak bisa diakses background
- **Smart Button States**: Enable/disable berdasarkan status
- **Visual Feedback**: Status label dengan warna yang sesuai

### 🧪 **Testing & Quality**

#### **Test Scripts**
- `test_settings_dialog.py`: Test basic settings functionality
- `test_settings_buttons.py`: Test semua tombol berfungsi
- `test_port_management.py`: Test fitur port management

#### **Error Handling**
- **Input Validation**: Tolerance 0-100%, valid decimal format
- **Port Detection**: Handle kasus tidak ada port tersedia
- **Connection Errors**: Graceful error handling dengan user feedback

## 📋 **Detailed Feature Breakdown**

### **Settings Dialog Tabs**

#### **Port Settings Tab**
```
┌─────────────────────────────────────┐
│ Port Settings                       │
├─────────────────────────────────────┤
│ Serial Port: [COM6 ▼] [Refresh]     │
│ Baudrate:   [19200 ▼]               │
└─────────────────────────────────────┘
```

#### **Page Settings Tab**
```
┌─────────────────────────────────────┐
│ Page Display Settings               │
├─────────────────────────────────────┤
│ Length Tolerance (%): [3]           │
│ Decimal Format: [#.# ▼]             │
│ Rounding Method: (●) UP ( ) DOWN    │
│                                     │
│ Conversion Factor Preview:          │
│ [66.95 Yard / Meter]                │
└─────────────────────────────────────┘
```

#### **Port Management Tab** 🆕
```
┌─────────────────────────────────────┐
│ Port Management                     │
├─────────────────────────────────────┤
│ Connection Status:                  │
│ [Connected to COM6]                 │
│                                     │
│ Port Control:                       │
│ [🔌 Kill/Close Port Connection]     │
│ [🔗 Auto Connect to Available Port] │
│ [❌ Disconnect]                     │
│                                     │
│ Auto Reconnect Settings:            │
│ [✓] Enable Auto Reconnect           │
└─────────────────────────────────────┘
```

### **Workflow Examples**

#### **Auto Connect Process**
1. **Kill Connection** → Tutup koneksi yang ada
2. **Scan Ports** → Cari port yang tersedia
3. **Select Port** → Pilih port pertama
4. **Connect** → Buat koneksi baru
5. **Update UI** → Update status dan button states

#### **Disconnect + Auto Reconnect**
1. **Disconnect** → Putus koneksi
2. **Check Setting** → Cek auto reconnect enabled
3. **Delay 1s** → Tunggu stabilitas
4. **Auto Connect** → Connect otomatis

## 🚀 **Installation & Usage**

### **For antiX Users**

#### **1. Download & Extract**
```bash
# Download release package
wget https://github.com/hokgt/textilindo_roll_printer/releases/download/v1.2.6/rollmachine-monitor-v1.2.6-antix.tar.gz

# Extract
tar -xzf rollmachine-monitor-v1.2.6-antix.tar.gz
cd rollmachine-monitor-v1.2.6-antix
```

#### **2. Install Dependencies**
```bash
# Run installer
sudo ./install-rollmachine.sh
```

#### **3. Start Application**
```bash
# Start in kiosk mode
./start_kiosk.sh

# Or start normally
python3 monitoring-roll-machine/monitoring/__main__.py
```

### **Settings Configuration**

#### **Access Settings**
- Klik **Settings** button di main window
- Pilih tab yang sesuai:
  - **Port Settings**: Konfigurasi koneksi serial
  - **Page Settings**: Konfigurasi tampilan
  - **Port Management**: Kontrol koneksi port

#### **Port Management Usage**
1. **Auto Connect**: Klik untuk connect otomatis
2. **Kill Port**: Jika port stuck, klik untuk force close
3. **Disconnect**: Putus koneksi dengan aman
4. **Auto Reconnect**: Enable untuk reconnect otomatis

## 🔧 **Configuration Files**

### **config.json**
```json
{
    "serial_port": "COM6",
    "baudrate": 19200,
    "length_tolerance": 3.0,
    "decimal_points": 1,
    "rounding": "UP"
}
```

### **Default Values**
- **serial_port**: "" (auto-detect)
- **baudrate**: 19200
- **length_tolerance**: 3.0%
- **decimal_points**: 1 (#.# format)
- **rounding**: "UP"

## 🐛 **Bug Fixes**

### **Settings Dialog**
- ✅ **Fixed**: Tombol refresh ports tidak berfungsi
- ✅ **Fixed**: Tombol save settings tidak berfungsi
- ✅ **Fixed**: Tombol cancel tidak berfungsi
- ✅ **Fixed**: Tombol close (X) tidak berfungsi
- ✅ **Fixed**: Error handling untuk input invalid

### **UI/UX**
- ✅ **Fixed**: Dialog tidak modal
- ✅ **Fixed**: Window flags tidak proper
- ✅ **Fixed**: Error messages tidak muncul

## 📊 **Performance & Stability**

### **Connection Management**
- **Auto Recovery**: Reconnect otomatis saat disconnect
- **Port Detection**: Auto-detect port yang tersedia
- **Error Recovery**: Graceful handling connection errors
- **Resource Cleanup**: Proper cleanup saat close

### **Memory Management**
- **UI Cleanup**: Proper cleanup saat dialog close
- **Event Handling**: Thread-safe event handling
- **Resource Leaks**: Fixed potential memory leaks

## 🔮 **Future Enhancements**

### **Planned Features**
- **Port Monitoring**: Real-time port health monitoring
- **Connection Logging**: Detailed connection logs
- **Advanced Settings**: More granular configuration options
- **Profile Management**: Save/load configuration profiles

### **Performance Improvements**
- **Async Operations**: Non-blocking port operations
- **Connection Pooling**: Multiple port support
- **Smart Detection**: Intelligent port selection

## 📞 **Support & Troubleshooting**

### **Common Issues**

#### **Port Not Found**
```bash
# Check available ports
ls /dev/tty*

# Check user permissions
sudo usermod -a -G dialout $USER
```

#### **Permission Denied**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Reboot or logout/login
sudo reboot
```

#### **Settings Not Saved**
- Pastikan aplikasi memiliki write permission ke directory
- Cek disk space tersedia
- Restart aplikasi jika perlu

### **Log Files**
```bash
# View application logs
tail -f logs/monitoring.log

# View system logs
dmesg | grep tty
```

## 📝 **Changelog**

### **v1.2.6 (Current)**
- ✨ Added Port Management tab with kill/close, auto connect, disconnect features
- ✨ Enhanced settings dialog with tabbed interface
- ✨ Added decimal format selection (#, #.#, #.##)
- ✨ Added length tolerance and rounding settings
- ✨ Added conversion factor preview
- 🔧 Fixed all settings dialog buttons functionality
- 🔧 Improved error handling and validation
- 🧪 Added comprehensive test scripts
- 📚 Updated documentation and release notes

### **v1.2.5**
- 🔧 Fixed popup spam issues
- 🔧 Improved kiosk mode stability

### **v1.2.4**
- ✨ Added unit detection and auto-switch
- 🔧 Fixed meter count display
- 🔧 Improved data polling interval

---

## 🎯 **Summary**

**v1.2.6** adalah release major yang menambahkan fitur **Port Management** yang powerful dan **Enhanced Settings Dialog** dengan interface yang modern. Semua fitur telah di-test secara menyeluruh dan siap untuk production use di environment antiX.

**Key Highlights:**
- 🆕 **Port Management Tab** dengan kontrol penuh atas koneksi
- 🎨 **Tabbed Settings Interface** yang modern dan user-friendly
- 🔧 **Robust Error Handling** dengan user feedback yang jelas
- 🧪 **Comprehensive Testing** dengan multiple test scripts
- 📚 **Complete Documentation** untuk deployment dan troubleshooting

**Ready for Production Use! 🚀** 