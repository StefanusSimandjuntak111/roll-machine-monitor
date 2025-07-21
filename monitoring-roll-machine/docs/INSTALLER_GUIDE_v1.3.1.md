# Roll Machine Monitor v1.3.1 Installer Guide

## 🎯 **Overview**

Roll Machine Monitor v1.3.1 dengan fitur **Smart Settings Update** tersedia dalam bentuk installer Windows yang mudah digunakan untuk distribusi ke user.

## 📦 **Installer Features**

### **✅ Included Features:**
- **Complete Application**: Semua fitur monitoring roll machine
- **Smart Settings Update**: Update settings tanpa restart (display settings)
- **Length Tolerance**: Konfigurasi toleransi panjang dengan decimal format
- **Desktop Shortcuts**: Icon di desktop untuk akses cepat
- **Start Menu Entries**: Entry di Start Menu Windows
- **Uninstaller**: Kemampuan uninstall yang bersih
- **Silent Installation**: Support untuk instalasi otomatis

### **✅ New in v1.3.1:**
- **Smart Settings Update**: Display settings update tanpa restart
- **Length Print Integration**: Product form mendapat nilai dengan toleransi
- **Settings Timestamp**: Tracking perubahan settings
- **Data Integrity**: Historical data protection
- **Better UX**: Clear feedback messages

## 🚀 **Building the Installer**

### **Prerequisites:**
1. **Inno Setup 6.2+**: Download dari https://jrsoftware.org/isdl.php
2. **Windows 10/11**: Build environment
3. **Git**: Untuk source code

### **Build Methods:**

#### **Method 1: Using Batch Script (Recommended)**
```batch
cd build-scripts
build-installer-v1.3.1.bat
```

#### **Method 2: Using PowerShell Script**
```powershell
cd build-scripts
.\build-installer-v1.3.1.ps1
```

#### **Method 3: Manual Build**
```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer-roll-machine-v1.3.1.iss
```

### **Output:**
- **Location**: `releases/windows/RollMachineMonitor-v1.3.1-Windows-Installer.exe`
- **Size**: ~50-100 MB (depending on compression)
- **Format**: Windows executable installer

## 📋 **Installation Guide for Users**

### **System Requirements:**
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free space
- **Python**: 3.11+ (included in installer)
- **Serial Port**: COM port for machine connection

### **Installation Steps:**

#### **1. Download Installer**
- Download `RollMachineMonitor-v1.3.1-Windows-Installer.exe`
- Verify file integrity (optional)

#### **2. Run Installer**
- **Double-click** installer file
- **Allow** UAC prompt (admin privileges required)
- **Follow** installation wizard

#### **3. Installation Options**
- **Installation Type**: Full (Recommended)
- **Installation Directory**: `C:\Program Files\RollMachineMonitor`
- **Desktop Shortcut**: Optional
- **Start Menu**: Yes (Recommended)

#### **4. Complete Installation**
- Wait for installation to complete
- **Launch application** (optional)
- **Close** installer

### **Silent Installation:**
```batch
RollMachineMonitor-v1.3.1-Windows-Installer.exe /SILENT
```

## 🎮 **First Time Setup**

### **1. Launch Application**
- **Desktop shortcut**: Double-click "Roll Machine Monitor"
- **Start Menu**: Start → Roll Machine Monitor → Roll Machine Monitor

### **2. Configure Settings**
- **Serial Port**: Select COM port (e.g., COM4)
- **Baudrate**: Set to 9600 (default)
- **Length Tolerance**: Configure as needed (0-20%)
- **Decimal Points**: Set precision (1-3)
- **Rounding**: Choose method (round, ceil, floor)

### **3. Test Connection**
- **Start Monitoring**: Click "Start Monitoring"
- **Verify Data**: Check if data appears
- **Test Settings**: Change display settings to test Smart Update

## 🔧 **Smart Settings Update Usage**

### **Display Settings (No Restart):**
1. **Open Settings**: Tools → Settings
2. **Change Values**:
   - Length Tolerance: 5.0%
   - Decimal Points: 2
   - Rounding: Round
3. **Save Settings**: Click "Save"
4. **Result**: Length Print updates immediately, no restart needed

### **Port Settings (Restart Required):**
1. **Open Settings**: Tools → Settings
2. **Change Values**:
   - Serial Port: COM4 → COM5
   - Baudrate: 9600 → 115200
3. **Save Settings**: Click "Save"
4. **Result**: Monitoring restarts automatically

### **User Feedback Messages:**
- **Display Settings**: "Display settings updated. No interruption."
- **Port Settings**: "Port settings updated. Monitoring restarted."

## 📊 **Distribution Checklist**

### **Before Distribution:**
- [ ] **Test installer** on clean Windows VM
- [ ] **Verify all features** work correctly
- [ ] **Check file size** and compression
- [ ] **Test silent installation**
- [ ] **Verify uninstaller** works properly

### **Distribution Package:**
- [ ] **Installer file**: `RollMachineMonitor-v1.3.1-Windows-Installer.exe`
- [ ] **README**: Installation and setup guide
- [ ] **Release Notes**: What's new in v1.3.1
- [ ] **Troubleshooting Guide**: Common issues and solutions

### **User Communication:**
- [ ] **Announce new version** with Smart Settings Update
- [ ] **Highlight benefits**: No restart for display settings
- [ ] **Provide upgrade path** from previous versions
- [ ] **Support contact** for issues

## 🛠️ **Troubleshooting**

### **Common Installation Issues:**

#### **1. "Inno Setup Compiler not found"**
- **Solution**: Install Inno Setup 6.2+ from official website
- **Alternative**: Use PowerShell script with better error handling

#### **2. "Access Denied" during installation**
- **Solution**: Run installer as Administrator
- **Check**: UAC settings and antivirus exclusions

#### **3. "Python not found" error**
- **Solution**: Installer includes Python, check PATH settings
- **Alternative**: Manual Python installation

#### **4. "Serial port access denied"**
- **Solution**: Close other applications using COM port
- **Check**: Device Manager for port conflicts

### **Runtime Issues:**

#### **1. Settings not saving**
- **Check**: Write permissions to installation directory
- **Solution**: Run as Administrator

#### **2. Smart Settings not working**
- **Verify**: Settings categorization (display vs port)
- **Check**: Logs for error messages

#### **3. Length Print not updating**
- **Check**: Length tolerance settings
- **Verify**: Data is coming from machine

## 📈 **Version History**

### **v1.3.1 (Current)**
- ✅ Smart Settings Update
- ✅ Length Print Integration
- ✅ Settings Timestamp Tracking
- ✅ Data Integrity Protection
- ✅ Better User Experience

### **v1.3.0**
- ✅ Length tolerance feature
- ✅ Port kill solution
- ✅ Enhanced logging table

### **v1.2.6**
- ✅ Basic monitoring features
- ✅ Serial communication
- ✅ Product form

## 🔮 **Future Enhancements**

### **Planned Features:**
1. **Settings Profiles**: Multiple configuration profiles
2. **Auto-update**: Automatic version updates
3. **Backup/Restore**: Settings backup functionality
4. **Advanced Logging**: Enhanced data logging
5. **Network Support**: Remote monitoring capabilities

### **Installer Improvements:**
1. **MSI Package**: Windows Installer package
2. **Chocolatey**: Package manager support
3. **Auto-updater**: Built-in update mechanism
4. **Custom Branding**: Company-specific branding

## 📞 **Support**

### **Documentation:**
- **User Guide**: `docs/USER_GUIDE.md`
- **Technical Docs**: `docs/TECHNICAL_DOCS.md`
- **API Reference**: `docs/API_REFERENCE.md`

### **Contact:**
- **GitHub Issues**: https://github.com/StefanusSimandjuntak111/roll-machine-monitor/issues
- **Email Support**: [Your support email]
- **Technical Support**: [Your technical contact]

## 🎯 **Summary**

Roll Machine Monitor v1.3.1 installer menyediakan:

- **Easy Installation**: One-click installer dengan wizard
- **Smart Features**: Settings update tanpa restart
- **Professional Package**: Desktop shortcuts, start menu, uninstaller
- **User-Friendly**: Clear feedback dan error handling
- **Distribution Ready**: Siap untuk distribusi ke user

Installer ini memastikan user mendapatkan pengalaman yang smooth dan professional saat menggunakan aplikasi monitoring roll machine dengan fitur Smart Settings Update yang canggih. 