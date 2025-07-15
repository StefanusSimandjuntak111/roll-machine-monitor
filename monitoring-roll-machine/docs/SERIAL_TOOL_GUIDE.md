# JSK3588 Serial Tool - User Guide

## Overview

JSK3588 Serial Tool adalah aplikasi untuk testing komunikasi serial dengan mesin JSK3588 roll machine. Aplikasi ini mirip dengan SerialTool tapi dirancang khusus untuk protokol JSK3588.

## Features

✅ **Connect/Disconnect** ke port COM  
✅ **Manual Send** - kirim data hex manual  
✅ **Auto Send** - kirim data otomatis setiap detik  
✅ **Protocol Commands** - quick buttons untuk command JSK3588  
✅ **Real-time Display** - lihat data TX/RX dengan timestamp  
✅ **JSK3588 Protocol Support** - sesuai dokumentasi protokol  

## Cara Menjalankan

### Option 1: Double-click
```
start_serial_tool.bat
```

### Option 2: Command Line
```cmd
python serial_tool.py
```

## Cara Menggunakan

### 1. **Connection Settings**
- **Port**: Pilih port COM (contoh: COM6)
- **Baudrate**: Set ke 19200 (default JSK3588)
- **Click "Connect"** untuk mulai koneksi

### 2. **Manual Send Tab**
- **Hex Data**: Masukkan data hex (contoh: `55 AA 02 00 00 01`)
- **Send**: Click untuk kirim data
- **Quick Commands**: Button cepat untuk command umum

### 3. **Auto Send Tab**
- **Command**: Set command yang akan dikirim berulang
- **Interval**: Set interval dalam ms (default: 1000ms = 1 detik)
- **Start Auto Send**: Mulai kirim otomatis

### 4. **Protocol Commands Tab**
- Informasi lengkap protokol JSK3588
- Format data send/receive
- List command yang tersedia

## JSK3588 Protocol Commands

### Command Utama:
| Command | Hex Data | Fungsi |
|---------|----------|--------|
| Query Status | `55 AA 02 00 00 01` | Ambil status current |
| Clear Current | `55 AA 01 00 00 00` | Clear data current |
| Query Data | `55 AA 03 00 00 02` | Ambil data |
| Clear Accumulated | `55 AA 04 00 00 03` | Clear data accumulated |

### Format Protocol:
- **Send**: `55 AA COM D1 D0 Checksum`
- **Receive**: `55 AA COM LEN D6 D5 D4 D3 D2 D1 D0 Checksum`

### Parameter JSK3588:
- **Baudrate**: 19200
- **Data bits**: 8
- **Stop bits**: 1
- **Parity**: None

## Testing dengan Device Real

### 1. **Connect ke COM6**
```
Port: COM6 - USB-SERIAL CH340 (COM6)
Baudrate: 19200
Click "Connect"
```

### 2. **Test Query Status**
```
Manual Send Tab:
Hex Data: 55 AA 02 00 00 01
Click "Send"
```

**Expected Response:**
```
[12:34:56.789] TX: 55 AA 02 00 00 01
[12:34:56.790] RX: 55 AA 20 0C 01 00 00 23 00 00 01 50
```

### 3. **Auto Send Test**
```
Auto Send Tab:
Command: 55 AA 02 00 00 01
Interval: 1000
Click "Start Auto Send"
```

## Troubleshooting

### Connection Issues
1. **Port not found**: Refresh ports, check device connection
2. **Permission denied**: Run as Administrator
3. **Driver issues**: Install CH340 driver

### Data Issues
1. **No response**: Check baudrate (19200), check device power
2. **Invalid hex**: Make sure format is correct (space separated)
3. **Timeout**: Increase timeout, check cable connection

### Auto Send Issues
1. **Not sending**: Check connection status
2. **Wrong interval**: Min 100ms, max 10000ms
3. **Stop not working**: Click "Stop Auto Send" button

## Data Interpretation

### Query Status Response Example:
```
RX: 55 AA 20 0C 01 00 00 23 00 00 01 50
```

**Breakdown:**
- `55 AA`: Header
- `20`: Command response (02 + address)
- `0C`: Data length (12 bytes)
- `01`: Coefficient & unit flags
- `00 00 23`: Current length (35 units)
- `00 00`: Current speed (0 units/min)
- `01`: Current shift (1)
- `50`: Checksum

## Tips

1. **Selalu check connection** sebelum send data
2. **Gunakan Auto Send** untuk monitoring kontinyu
3. **Save log data** dengan copy dari display area
4. **Test dengan Query Status** untuk verifikasi koneksi
5. **Check checksum** jika ada error response

## Support

Jika ada masalah:
1. Check dokumentasi JSK3588.md
2. Verify port dan baudrate settings
3. Test dengan device lain untuk isolasi masalah
4. Check driver CH340 di Device Manager 