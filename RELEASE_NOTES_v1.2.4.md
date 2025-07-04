# Roll Machine Monitor v1.2.4 - Auto-Detection Release

## ✨ New Features

### Automatic Serial Port Detection
- **AUTO mode**: Aplikasi sekarang dapat mendeteksi port serial secara otomatis
- **Smart detection**: Prioritas untuk device CH340 (JSK3588)
- **Platform support**: Windows (COM1-COM6) dan Linux (/dev/ttyUSB0, /dev/ttyACM0)
- **Fallback options**: Jika tidak ada port yang terdeteksi, akan menggunakan port default

### Enhanced Connection Settings
- **Auto-detect option**: Pilihan "AUTO (Auto-detect)" sebagai default
- **Real-time port detection**: Refresh button untuk mendeteksi port yang baru tersambung
- **Smart validation**: Tidak lagi memblokir monitoring jika menggunakan AUTO mode

## 🔧 Improvements

### UI/UX Enhancements
- Default port selection ke "AUTO (Auto-detect)"
- Pesan error yang lebih informatif
- Validasi port yang lebih smart

### Technical Improvements
- Integrasi dengan `serial.tools.list_ports` untuk deteksi port yang lebih akurat
- Logging yang lebih detail untuk debugging
- Better error handling untuk port yang tidak tersedia

## 📋 Configuration Changes

### Default Config (config.json)
```json
{
    "serial_port": "AUTO",
    "baudrate": 19200,
    "auto_connect": true
}
```

### Port Detection Priority
1. **CH340 devices** (JSK3588 hardware)
2. **USB-SERIAL adapters** 
3. **Standard COM/ttyUSB ports**
4. **Fallback to common ports**

## 🚀 Installation

### For Linux
```bash
tar -xzf rollmachine-monitor-v1.2.4.tar.gz
cd rollmachine-monitor-v1.2.4
./install.sh
```

### For Windows
```bash
# Extract rollmachine-monitor-v1.2.4.zip
# Run install.bat
```

## 🔍 Usage

### Auto-Detection Mode
1. Pilih "AUTO (Auto-detect)" di Connection Settings
2. Aplikasi akan otomatis mendeteksi JSK3588 device
3. Klik "Start Monitoring" - tidak perlu pilih port manual

### Manual Mode
1. Klik "Refresh" untuk lihat port tersedia
2. Pilih port specific (COM4, /dev/ttyUSB0, etc.)
3. Start monitoring seperti biasa

## 🐛 Bug Fixes

### Fixed Issues
- **Port validation**: Fixed "Please select a serial port" warning untuk AUTO mode
- **Serial connection**: Improved connection stability
- **Error handling**: Better error messages untuk troubleshooting

### Known Issues
- Port detection requires proper USB driver installation
- Some CH340 clones may not be detected automatically

## 📊 Compatibility

### Operating Systems
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, CentOS, antiX)
- ✅ WSL (Windows Subsystem for Linux)

### Hardware
- ✅ JSK3588 Roll Machine
- ✅ CH340 USB-Serial adapters
- ✅ FTDI USB-Serial adapters
- ✅ Standard COM ports

## 🔄 Migration Notes

### From v1.2.3
- Auto-detection diaktifkan secara default
- Tidak perlu ubah konfigurasi existing
- Port manual masih tetap bisa digunakan

### Configuration Migration
- Existing `"serial_port": "COM4"` tetap berfungsi
- Recommended: ganti ke `"serial_port": "AUTO"`
- Backup config lama jika perlu rollback

## 📞 Support

### Troubleshooting
1. **Port not detected**: Pastikan driver CH340 sudah terinstall
2. **Connection failed**: Coba refresh port atau restart aplikasi
3. **Permission denied**: Jalankan sebagai administrator (Windows) atau tambahkan user ke group `dialout` (Linux)

### Contact
- GitHub Issues: [Link to issues]
- Email: [Support email]

---

**Roll Machine Monitor v1.2.4**  
*Build Date: 2024-12-XX*  
*Compatible with JSK3588 Roll Machine* 