# Roll Machine Monitor - Kiosk Mode 🎯

## Fitur Kiosk Mode

✅ **Fullscreen Mode** - Aplikasi selalu fullscreen, tidak bisa di-minimize  
✅ **Cannot Close** - Semua shortcut close disabled (Alt+F4, Ctrl+Q, ESC, dll)  
✅ **Auto-Restart** - Jika aplikasi tertutup, otomatis restart dalam 3 detik  
✅ **Auto-Start Monitoring** - Otomatis connect ke serial port saat startup  
✅ **Health Monitoring** - Self-check every 5 seconds  
✅ **Stay On Top** - Window selalu di atas aplikasi lain  

## Cara Menjalankan

### 1. Manual Start (Recommended)
```bash
# Start kiosk mode dengan monitoring
./start_kiosk.sh

# Atau langsung jalankan aplikasi
cd /opt/rollmachine-monitor/monitoring-roll-machine
/opt/rollmachine-monitor/venv/bin/python -m monitoring
```

### 2. Via System Service (jika terinstall)
```bash
# SystemD
sudo systemctl start rollmachine-kiosk

# Init Script (AntiX)  
sudo /etc/init.d/rollmachine-monitor start
```

## Cara Keluar dari Kiosk Mode

### 1. Via Script (Recommended)
```bash
./exit_kiosk.sh
```

### 2. Manual Exit Flag
```bash
# Create exit flag
touch /tmp/exit_kiosk_mode

# Application akan exit dalam 10 detik
```

### 3. Force Kill
```bash
sudo pkill -f "python.*monitoring"
```

## Monitoring & Logs

```bash
# Real-time logs
tail -f /var/log/rollmachine-kiosk.log

# Check apakah running
ps aux | grep python | grep monitoring

# Check display
echo $DISPLAY
xset q
```

## Troubleshooting

### Aplikasi tidak muncul?
```bash
# Check display
export DISPLAY=:0
xset q

# Test manual
cd /opt/rollmachine-monitor/monitoring-roll-machine
/opt/rollmachine-monitor/venv/bin/python -m monitoring
```

### Aplikasi crash terus?
```bash
# Check dependencies
/opt/rollmachine-monitor/venv/bin/python -c "import PySide6; print('OK')"

# Check logs
tail -20 /var/log/rollmachine-kiosk.log
```

### Tidak bisa connect ke serial?
```bash
# Check serial ports
ls /dev/ttyUSB* /dev/ttyACM*

# Check permissions
sudo usermod -a -G dialout $USER
```

---

## 🎯 Perfect untuk:
- **Production kiosk** di lantai pabrik
- **24/7 monitoring** tanpa intervensi user
- **Industrial environment** yang robust
- **Anti-tamper** protection

**Aplikasi akan selalu running dan restart otomatis!** 🚀 