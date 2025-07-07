# Windows Troubleshooting Guide

## Masalah Umum dan Solusi

### 1. Permission Error (Access Denied)

**Gejala:**
```
Error opening port COM6: could not open port 'COM6': PermissionError(13, 'Access is denied.', None, 5)
```

**Solusi:**
1. **Jalankan sebagai Administrator:**
   ```cmd
   # Buka PowerShell sebagai Administrator, lalu:
   cd "D:\Apps\monitoring-roll-machine\monitoring-roll-machine"
   python -m monitoring.ui.main_window
   ```

2. **Atau gunakan script yang sudah disediakan:**
   ```cmd
   .\run_as_admin.bat
   ```

3. **Tutup aplikasi lain yang menggunakan port serial:**
   - Arduino IDE
   - PuTTY
   - Terminal/Serial Monitor
   - Aplikasi monitoring lain

### 2. Port Tidak Terdeteksi

**Gejala:**
```
Found ports: []
No serial ports detected
```

**Solusi:**
1. **Cek Device Manager:**
   - Win+R → `devmgmt.msc`
   - Cari di "Ports (COM & LPT)"
   - Pastikan status "This device is working properly"

2. **Install/Update Driver CH340:**
   - Download dari: [wch.cn/downloads/CH341SER_EXE.html](https://www.wch.cn/downloads/CH341SER_EXE.html)
   - Install sebagai Administrator
   - Restart komputer

3. **Test port dengan script:**
   ```cmd
   python test_ports.py
   ```

### 3. Driver CH340 Bermasalah

**Gejala:**
```
Status: Unknown (di Device Manager)
PermissionError(13, 'A device attached to the system is not functioning.')
```

**Solusi:**
1. **Uninstall driver lama:**
   - Device Manager → Ports → USB-SERIAL CH340
   - Klik kanan → Uninstall device
   - Restart komputer

2. **Install driver baru:**
   - Download driver terbaru dari wch.cn
   - Install sebagai Administrator
   - Restart komputer

3. **Cek status di Device Manager:**
   - Status harus "This device is working properly"
   - Tidak ada warning/error

### 4. Multiple Instance Error

**Gejala:**
```
Another instance (PID XXXX) is already running
Another instance is already running. Exiting.
```

**Solusi:**
1. **Hapus file lock:**
   - Buka `%TEMP%` (biasanya `C:\Users\<USER>\AppData\Local\Temp`)
   - Cari file `rollmachine_monitor.lock`
   - Hapus file tersebut

2. **Atau restart komputer**

### 5. Aplikasi Tidak Bisa Connect ke Device

**Solusi Sementara:**
1. **Gunakan mode Mock/Simulation:**
   - Edit `monitoring/config.json`
   - Set `"use_mock_data": true`
   - Restart aplikasi

2. **Test dengan port lain:**
   - Cek Device Manager untuk port yang tersedia
   - Edit config, ganti port ke COM lain
   - Test satu per satu

## Cara Menjalankan Aplikasi

### Opsi 1: PowerShell (Recommended)
```powershell
# Buka PowerShell sebagai Administrator
cd "D:\Apps\monitoring-roll-machine\monitoring-roll-machine"
python -m monitoring.ui.main_window
```

### Opsi 2: Batch File
```cmd
# Double-click file
run_as_admin.bat
```

### Opsi 3: Manual Setup
```cmd
# 1. Buat virtual environment
python -m venv venv_windows

# 2. Aktifkan virtual environment
venv_windows\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan aplikasi
python -m monitoring.ui.main_window
```

## Konfigurasi Port Serial

### Auto-Detect (Recommended)
```json
{
    "serial_port": "AUTO",
    "baudrate": 19200
}
```

### Manual Port Selection
```json
{
    "serial_port": "COM6",
    "baudrate": 19200
}
```

### Mock Mode (untuk testing)
```json
{
    "serial_port": "AUTO",
    "use_mock_data": true
}
```

## Testing dan Debugging

### 1. Test Port Availability
```cmd
python test_ports.py
```

### 2. Test Windows Compatibility
```cmd
python test_windows.py
```

### 3. Check Logs
- Lihat file di folder `logs/`
- File terbaru: `monitor_YYYYMMDD.log`

### 4. Device Manager Check
```powershell
Get-PnpDevice -Class "Ports" | Format-Table -AutoSize
```

## Tips Penting

1. **Selalu jalankan sebagai Administrator** untuk akses port serial
2. **Restart komputer** setelah install/update driver
3. **Tutup aplikasi lain** yang menggunakan port serial
4. **Gunakan mode mock** untuk testing tanpa device
5. **Cek Device Manager** untuk status port

## Support

Jika masih ada masalah:
1. Jalankan `python test_windows.py` dan kirim hasilnya
2. Screenshot Device Manager (Ports section)
3. Isi log error dari folder `logs/`
4. Sebutkan versi Windows dan Python yang digunakan 