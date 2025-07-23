# Installer Build Guide for Roll Machine Monitor v1.3.2

## 🎯 Overview

This guide provides step-by-step instructions for building the Windows installer for Roll Machine Monitor v1.3.2.

## 📋 Prerequisites

### 1. **Inno Setup Compiler 6.2+**
- **Download:** https://jrsoftware.org/isdl.php
- **Installation:** Run the installer and follow the setup wizard
- **PATH Setup:** Make sure `iscc.exe` is added to your system PATH
- **Verification:** Open Command Prompt and run `iscc --version`

### 2. **Python Environment**
- **Python 3.9+** installed and working
- **All dependencies** installed via `pip install -r requirements.txt`
- **Application tested** and working correctly

### 3. **Git Repository**
- **Latest v1.3.2 code** pulled from repository
- **All files committed** and up to date

## 🚀 Build Methods

### Method 1: PowerShell Script (Recommended)

1. **Navigate to build-scripts directory:**
   ```powershell
   cd build-scripts
   ```

2. **Run PowerShell script:**
   ```powershell
   .\build-installer-v1.3.2.ps1
   ```

3. **Expected output:**
   ```
   🚀 Starting Roll Machine Monitor v1.3.2 Installer Build
   ===============================================
   
   📋 Build Information:
      Version: v1.3.2
      Project Root: ..
      Build Directory: ..\releases\windows
      Installer Script: installer-roll-machine-v1.3.2.iss
      Output: RollMachineMonitor-v1.3.2-Windows-Installer.exe
   
   🔍 Checking Inno Setup Compiler...
   ✅ Inno Setup Compiler found at: C:\Program Files (x86)\Inno Setup 6\ISCC.exe
   
   🔍 Checking project files...
   ✅ Project files found
   
   📁 Creating build directory...
   ✅ Build directory ready
   
   🔄 Updating version information...
      Version updated to v1.3.2
   
   🔨 Building installer...
      Using script: installer-roll-machine-v1.3.2.iss
   
   🔍 Verifying installer...
   ✅ Installer created successfully
      Location: ..\releases\windows\RollMachineMonitor-v1.3.2-Windows-Installer.exe
      Size: 45.2 MB
   
   📝 Creating build log...
   ✅ Build log created: ..\releases\windows\build-log-v1.3.2-20250115_143022.txt
   
   ===============================================
   🎉 Installer Build Completed Successfully!
   ===============================================
   ```

### Method 2: Batch Script

1. **Navigate to build-scripts directory:**
   ```cmd
   cd build-scripts
   ```

2. **Run batch script:**
   ```cmd
   .\build-installer-v1.3.2.bat
   ```

### Method 3: Manual Build

1. **Navigate to build-scripts directory:**
   ```cmd
   cd build-scripts
   ```

2. **Run Inno Setup Compiler directly:**
   ```cmd
   iscc installer-roll-machine-v1.3.2.iss
   ```

## 📁 Output Files

### Installer File
- **Name:** `RollMachineMonitor-v1.3.2-Windows-Installer.exe`
- **Location:** `releases/windows/`
- **Size:** ~45-50 MB (depending on content)
- **Type:** Windows executable installer

### Build Log
- **Name:** `build-log-v1.3.2-YYYYMMDD_HHMMSS.txt`
- **Location:** `releases/windows/`
- **Content:** Build information, timestamps, file details

## 🔧 Troubleshooting

### Issue 1: "Inno Setup Compiler not found"
**Symptoms:**
```
❌ Inno Setup Compiler (iscc) not found in PATH
```

**Solutions:**
1. **Install Inno Setup:**
   - Download from https://jrsoftware.org/isdl.php
   - Install with default settings
   - Restart Command Prompt/PowerShell

2. **Check PATH:**
   ```cmd
   echo %PATH%
   ```
   Should include: `C:\Program Files (x86)\Inno Setup 6\`

3. **Manual PATH addition:**
   - Open System Properties → Environment Variables
   - Add `C:\Program Files (x86)\Inno Setup 6\` to PATH
   - Restart terminal

### Issue 2: "Project files not found"
**Symptoms:**
```
❌ Monitoring directory not found
❌ run_app.py not found
❌ requirements.txt not found
```

**Solutions:**
1. **Check current directory:**
   ```cmd
   dir
   ```
   Should show build-scripts folder

2. **Verify project structure:**
   ```cmd
   dir ..
   ```
   Should show monitoring folder, run_app.py, requirements.txt

3. **Navigate to correct location:**
   ```cmd
   cd D:\Apps\monitoring-roll-machine\monitoring-roll-machine\build-scripts
   ```

### Issue 3: "Installer build failed"
**Symptoms:**
```
❌ Installer build failed with exit code: 1
```

**Solutions:**
1. **Check Inno Setup script:**
   - Verify `installer-roll-machine-v1.3.2.iss` exists
   - Check for syntax errors in the script

2. **Check file permissions:**
   - Ensure write access to `releases/windows/` directory
   - Run as Administrator if needed

3. **Check disk space:**
   - Ensure sufficient free space (at least 100 MB)

4. **Manual build with verbose output:**
   ```cmd
   iscc /V+ installer-roll-machine-v1.3.2.iss
   ```

### Issue 4: "Installer not found after build"
**Symptoms:**
```
❌ Installer not found
   Expected: ..\releases\windows\RollMachineMonitor-v1.3.2-Windows-Installer.exe
```

**Solutions:**
1. **Check build directory:**
   ```cmd
   dir ..\releases\windows\
   ```

2. **Check for errors in build process:**
   - Look for error messages during build
   - Check build log file

3. **Verify Inno Setup output:**
   - Check if `iscc` command completed successfully
   - Look for any error messages

## 🧪 Testing the Installer

### Pre-Installation Test
1. **Check installer file:**
   - Verify file size (~45-50 MB)
   - Check file properties for version info
   - Ensure file is not corrupted

2. **Test on clean system:**
   - Use virtual machine or clean Windows installation
   - Install with default settings
   - Verify all components installed

### Installation Verification
1. **Check installed files:**
   - `C:\Program Files\RollMachineMonitor\`
   - Desktop shortcuts
   - Start menu entries

2. **Test application:**
   - Launch application
   - Verify version display shows v1.3.2
   - Test all features (roll time, restart button, etc.)

3. **Test uninstaller:**
   - Uninstall application
   - Verify clean removal

## 📦 Distribution

### GitHub Release
1. **Create new release:**
   - Go to GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag: `v1.3.2`
   - Title: `Roll Machine Monitor v1.3.2`

2. **Upload files:**
   - Upload installer: `RollMachineMonitor-v1.3.2-Windows-Installer.exe`
   - Upload release notes: `docs/RELEASE_NOTES_v1.3.2.md`

3. **Publish release:**
   - Add release description
   - Mark as latest release
   - Publish

### Alternative Distribution
1. **Direct file sharing:**
   - Share installer file directly
   - Include installation instructions
   - Provide support contact

2. **Internal distribution:**
   - Network share
   - Company intranet
   - Email distribution

## 📞 Support

### Build Issues
- **Check this guide** for common solutions
- **Review build logs** for specific errors
- **Verify prerequisites** are met

### Installation Issues
- **Test on clean system** first
- **Check system requirements** (Windows 10+)
- **Run as Administrator** if needed

### Application Issues
- **Verify version** shows v1.3.2
- **Check all features** work correctly
- **Review documentation** in `docs/` folder

---

**Roll Machine Monitor v1.3.2** - Professional installer build guide! 🚀 