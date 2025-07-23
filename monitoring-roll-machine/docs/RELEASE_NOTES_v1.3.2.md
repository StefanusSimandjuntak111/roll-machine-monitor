# Roll Machine Monitor v1.3.2 Release Notes

## 🎉 Release Overview

**Version:** 1.3.2  
**Release Date:** January 2025  
**Codename:** "Roll Time Fix & Restart Button Edition"

This release focuses on improving user experience and fixing critical issues with roll time calculation and application restart functionality.

## 🚀 New Features

### 1. **Restart Button** 🔄
- **Location:** Header (next to Settings button)
- **Functionality:** One-click application restart
- **Features:**
  - Safe cleanup of resources before restart
  - Automatic restart script generation
  - Works with all execution modes (`python -m monitoring`, direct executable)
  - Confirmation dialog for safety
  - Proper resource management (monitoring, heartbeat, singleton lock)

### 2. **Version Display** 📋
- **Location:** Status bar (right side, next to clock)
- **Display:** Shows current application version (v1.3.2)
- **Style:** Gray color, smaller font than clock
- **Purpose:** Easy identification of installed version

### 3. **Logging Table Improvements** 📊
- **Descending Order:** Newest entries now appear at the top
- **Better UX:** No need to scroll to see recent data
- **Highlighting:** Latest entry highlighted in blue at the top
- **Consistent Behavior:** Works with all data types

## 🔧 Bug Fixes

### 1. **Roll Time Fix for First Product** ⏱️
- **Problem:** Roll time was 0.0 for the first product when printed immediately
- **Root Cause:** `roll_start_time` was only initialized when length reached 0.01
- **Solution:** 
  - Initialize `roll_start_time` on first data arrival
  - Reset `roll_start_time` after each print
  - Independent roll time calculation for each print
- **Result:** Roll time now appears correctly for all products, including the first

### 2. **Restart Script Compatibility** 🔄
- **Problem:** Restart button didn't work with `python -m monitoring`
- **Root Cause:** Script didn't detect Python module mode correctly
- **Solution:**
  - Proper detection of execution mode
  - Different script generation for Python module vs direct executable
  - Correct working directory handling
- **Result:** Restart works with all execution methods

## 📋 Technical Improvements

### 1. **Version Management**
- **Centralized Version:** `monitoring/version.py` for version information
- **Consistent Versioning:** All files updated to v1.3.2
- **Easy Updates:** Single source for version changes

### 2. **Code Quality**
- **Better Error Handling:** Graceful fallbacks for restart functionality
- **Improved Logging:** Detailed logs for debugging
- **Resource Management:** Proper cleanup procedures

### 3. **Testing**
- **Comprehensive Tests:** Added tests for roll time logic
- **Restart Script Tests:** Verification of script generation
- **Logging Table Tests:** Validation of descending order functionality

## 📦 Installation

### Windows Installer
- **File:** `RollMachineMonitor-v1.3.2-Windows-Installer.exe`
- **Size:** ~XX MB
- **Features:** Complete installation with all components
- **Requirements:** Windows 10+ (x64)

### Manual Installation
```bash
# Clone repository
git clone https://github.com/StefanusSimandjuntak111/roll-machine-monitor.git
cd roll-machine-monitor

# Install dependencies
pip install -r requirements.txt

# Run application
python -m monitoring
```

## 🔄 Upgrade Instructions

### From v1.3.1
1. **Backup:** Export any important configuration
2. **Uninstall:** Remove previous version
3. **Install:** Run v1.3.2 installer
4. **Verify:** Check version display shows v1.3.2

### From Earlier Versions
1. **Full Backup:** Export all data and configurations
2. **Clean Install:** Remove old version completely
3. **New Install:** Install v1.3.2
4. **Migration:** Import backed up data if needed

## 🧪 Testing

### Verified Features
- ✅ Roll time calculation for first product
- ✅ Restart button functionality
- ✅ Logging table descending order
- ✅ Version display
- ✅ All existing features from v1.3.1

### Test Scenarios
- ✅ Fresh installation
- ✅ Upgrade from v1.3.1
- ✅ Python module mode (`python -m monitoring`)
- ✅ Direct executable mode
- ✅ Restart functionality
- ✅ Roll time accuracy

## 📁 Files Modified

### Core Application
- `monitoring/ui/main_window.py` - Added restart button and version display
- `monitoring/logging_table.py` - Fixed descending order sorting
- `monitoring/ui/logging_table_widget.py` - Updated highlighting logic
- `monitoring/version.py` - New version management file

### Configuration
- `setup.py` - Updated to v1.3.2
- `pyproject.toml` - Build configuration

### Documentation
- `docs/ROLL_TIME_FIX_SUMMARY.md` - Roll time fix documentation
- `docs/LOGGING_TABLE_AND_RESTART_FIXES.md` - UI improvements documentation
- `docs/RESTART_SCRIPT_FIX.md` - Restart functionality documentation

### Testing
- `tests-integration/test_roll_time_logic_simple.py` - Roll time tests
- `tests-integration/test_logging_table_descending.py` - Logging table tests
- `tests-integration/test_restart_script.py` - Restart script tests

### Build Scripts
- `build-scripts/installer-roll-machine-v1.3.2.iss` - Installer script
- `build-scripts/build-installer-v1.3.2.bat` - Build script

## 🐛 Known Issues

None reported in this release.

## 🔮 Future Plans

### v1.4.0 (Planned)
- Enhanced data export functionality
- Advanced filtering options
- Performance optimizations
- Additional language support

### v1.3.3 (Minor Updates)
- Bug fixes and minor improvements
- Additional testing scenarios
- Documentation updates

## 📞 Support

### Documentation
- **User Guide:** See `docs/` directory
- **API Reference:** Inline code documentation
- **Troubleshooting:** `docs/WINDOWS_TROUBLESHOOTING.md`

### Issues and Feedback
- **GitHub Issues:** https://github.com/StefanusSimandjuntak111/roll-machine-monitor/issues
- **Email Support:** Contact development team

### Community
- **GitHub Discussions:** For questions and feature requests
- **Wiki:** Additional documentation and guides

## 🙏 Acknowledgments

- **Development Team:** For continuous improvements
- **Testing Team:** For comprehensive testing
- **Users:** For valuable feedback and bug reports

---

**Roll Machine Monitor v1.3.2** - Making industrial monitoring more reliable and user-friendly! 🚀 