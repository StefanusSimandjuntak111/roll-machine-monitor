# Popup Spam Prevention Fix v1.2.5

## 🐛 **PROBLEM**

User melaporkan: **"pengecekan instance nya terbuka / pop up already running hanya sekali saja jangan terus terusan menambahkan pop up baru"**

### Issue
- Popup "Already Running" muncul berulang-ulang saat ada multiple restart attempts
- Watchdog atau script lain mencoba restart aplikasi berkali-kali
- User terganggu dengan popup spam yang tidak berhenti
- Popup blocking UI saat aplikasi dalam kiosk mode

### Root Cause
1. **Tidak ada debouncing mechanism** - Setiap restart attempt menampilkan popup
2. **Watchdog aggressive restart** - Mencoba restart terlalu sering
3. **No popup suppression** - Tidak ada pembatasan frekuensi popup
4. **Race condition** - Multiple watchdog instances bisa start bersamaan

## 🔧 **SOLUTION IMPLEMENTED**

### 1. **Popup Suppression Mechanism**

#### Flag File System
```python
class SingletonLock:
    def __init__(self, lock_file="/tmp/rollmachine_monitor.lock"):
        self.popup_shown_file = "/tmp/rollmachine_popup_shown.flag"
        
    def should_show_popup(self):
        """Check if popup should be shown (only once per 30-second window)."""
        if os.path.exists(self.popup_shown_file):
            flag_age = time.time() - os.path.getmtime(self.popup_shown_file)
            if flag_age < 30:  # Suppress for 30 seconds
                return False
        return True
```

#### Smart Popup Control
```python
if not self.singleton_lock.acquire():
    # Only show popup if not shown recently (prevent spam)
    if self.singleton_lock.should_show_popup():
        self.singleton_lock.mark_popup_shown()
        QMessageBox.critical(None, "Already Running", 
                           "Roll Machine Monitor is already running.\n"
                           "Only one instance is allowed at a time.")
    else:
        logger.info("Popup suppressed - already shown recently")
    sys.exit(1)
```

### 2. **Restart Attempt Debouncing**

#### Watchdog Debouncing
```bash
start_application() {
    # Check for recent restart attempts to prevent popup spam
    RESTART_FLAG="/tmp/rollmachine_restart_attempt"
    if [ -f "$RESTART_FLAG" ]; then
        restart_age=$(( $(date +%s) - $(stat -c %Y "$RESTART_FLAG" 2>/dev/null || echo "0") ))
        if [ "$restart_age" -lt 30 ]; then
            log_message "Recent restart attempt detected (${restart_age}s ago), skipping to prevent popup spam"
            return 1
        fi
    fi
    
    # Mark restart attempt
    date +%s > "$RESTART_FLAG"
}
```

### 3. **Automatic Cleanup**

#### Flag File Cleanup
```python
def release(self):
    """Release lock and cleanup flag files."""
    if self.lock_handle:
        # Remove popup flag when releasing
        if os.path.exists(self.popup_shown_file):
            os.remove(self.popup_shown_file)
        # Also clear popup shown flag since we're the new primary instance
        if os.path.exists(self.popup_shown_file):
            os.remove(self.popup_shown_file)
```

## ⏱️ **TIMING CONFIGURATION**

### Popup Suppression Window
- **Duration**: 30 seconds
- **Logic**: Popup hanya muncul maksimal 1 kali per 30 detik
- **Reset**: Flag dihapus otomatis saat primary instance start

### Restart Debouncing  
- **Duration**: 30 seconds
- **Logic**: Watchdog tidak akan mencoba restart lagi dalam 30 detik
- **Tracking**: Menggunakan timestamp file di `/tmp/rollmachine_restart_attempt`

## 📁 **FILES AFFECTED**

### Core Application
- `monitoring/ui/main_window.py`
  - Added `popup_shown_file` tracking
  - Added `should_show_popup()` method
  - Added `mark_popup_shown()` method
  - Enhanced `acquire()` and `release()` methods

### Watchdog Scripts
- `smart-watchdog.sh`
- `smart-watchdog-sysv.sh`
- `deploy-packages/rollmachine-monitor-fix-v1.2.3/smart-watchdog.sh`
- `deploy-packages/rollmachine-monitor-fix-v1.2.3/smart-watchdog-sysv.sh`

## 🎯 **BEHAVIOR CHANGES**

### Before Fix
```
Time 0s:  Instance 1 tries to start → Popup shown
Time 5s:  Instance 2 tries to start → Popup shown  
Time 10s: Instance 3 tries to start → Popup shown
Time 15s: Instance 4 tries to start → Popup shown
...
```

### After Fix
```
Time 0s:  Instance 1 tries to start → Popup shown, flag created
Time 5s:  Instance 2 tries to start → Popup suppressed (< 30s)
Time 10s: Instance 3 tries to start → Popup suppressed (< 30s)
Time 15s: Watchdog restart attempt → Skipped (debounced)
Time 35s: Instance 4 tries to start → Popup allowed (> 30s)
```

## ✅ **VERIFICATION**

### Test Scenario 1: Multiple Quick Starts
```bash
# Start multiple instances quickly
python -m monitoring &
python -m monitoring &  # Should be suppressed
python -m monitoring &  # Should be suppressed
```
**Expected**: Only 1 popup shown

### Test Scenario 2: Watchdog Restart Loop
```bash
# Force watchdog restart repeatedly
./smart-watchdog-sysv.sh start
sleep 5
./smart-watchdog-sysv.sh start  # Should be debounced
```
**Expected**: Second restart skipped

### Test Scenario 3: Flag File Cleanup
```bash
# Check flag files are cleaned up
ls -la /tmp/rollmachine_*
# After application shutdown, should be clean
```

## 🚀 **BENEFITS**

1. **No More Popup Spam** - Maksimal 1 popup per 30 detik
2. **Better User Experience** - Tidak terganggu popup berulang
3. **Kiosk Mode Friendly** - Popup tidak blocking interface
4. **Automatic Cleanup** - Flag files dibersihkan otomatis
5. **Smart Debouncing** - Watchdog tidak restart terlalu agresif
6. **Resource Efficient** - Mengurangi unnecessary restart attempts

## 📊 **IMPACT METRICS**

| Metric | Before | After |
|--------|--------|-------|
| Popup frequency | Unlimited | Max 1 per 30s |
| Restart attempts | Unlimited | Max 1 per 30s |
| User interruption | High | Minimal |
| Resource usage | High | Optimized |
| Flag file cleanup | Manual | Automatic |

## 📦 **DEPLOYMENT**

**Package**: `rollmachine-monitor-fix-v1.2.3.tar.gz` (148KB)  
**Checksum**: `fc23b8afa6134070f671606e7821945624143e216ca7ca53949f224c95ff38c1`  
**Commit**: `5dd54c8`

### Installation
```bash
# Extract package
tar -xzf rollmachine-monitor-fix-v1.2.3.tar.gz
cd rollmachine-monitor-fix-v1.2.3

# Install with popup fix
sudo bash fix-multiple-instance-offline.sh
```

### Verification Commands
```bash
# Check if flag files exist
ls -la /tmp/rollmachine_*

# Test popup suppression
python -m monitoring &
python -m monitoring &  # Should be silent

# Check logs for suppression
tail -f /var/log/rollmachine-smart-watchdog.log
```

---

## 📋 **COMMIT INFO**

```
commit 5dd54c8
fix: prevent repeated 'already running' popup spam

- Add popup suppression mechanism using flag file
- Popup only shows once per 30-second window  
- Add restart attempt debouncing in watchdog scripts
- Prevent excessive restart attempts that cause popup spam
- Implement should_show_popup() and mark_popup_shown() methods
- Add restart attempt tracking with RESTART_FLAG file
- Clean up flag files when singleton lock is released

Resolves issue where multiple restart attempts would show
repeated 'already running' popups annoying users.
```

**Result**: Popup "already running" sekarang **hanya muncul sekali saja**, tidak berulang-ulang lagi! ✅ 