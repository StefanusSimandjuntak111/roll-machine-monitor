# Roll Machine Monitor - Windows Installation Guide

This guide will help you install and run the Roll Machine Monitor application on Windows.

## Prerequisites

1. **Python 3.9 or higher**
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Windows 10 or higher**
   - The application is tested on Windows 10 and 11

## Quick Start

### Option 1: Simple Python Script (Recommended)

1. **Double-click the file:**
   ```
   run_app.py
   ```

2. **Or run from command line:**
   ```cmd
   python run_app.py
   ```

### Option 2: Using PowerShell (Recommended)

1. Open PowerShell as Administrator
2. Navigate to the application directory
3. Run the startup script:
   ```powershell
   .\start_windows.ps1
   ```

### Option 3: Using Command Prompt

1. Open Command Prompt as Administrator
2. Navigate to the application directory
3. Run the batch file:
   ```cmd
   start_windows.bat
   ```

### Option 4: Manual Installation

1. **Create virtual environment:**
   ```cmd
   python -m venv venv_windows
   ```

2. **Activate virtual environment:**
   ```cmd
   venv_windows\Scripts\activate
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```cmd
   python run_app.py
   ```

## Building Executable

To create a standalone Windows executable:

1. **Install PyInstaller:**
   ```cmd
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```cmd
   python build_exe.py
   ```

3. **Find the executable:**
   - Look in the `dist/` folder
   - The file will be named `MonitoringRollMachine.exe`

## Troubleshooting

### Common Issues

1. **"Python is not recognized"**
   - Make sure Python is installed and added to PATH
   - Restart your command prompt after installing Python

2. **"Permission denied"**
   - Run PowerShell/Command Prompt as Administrator
   - Check Windows Defender or antivirus settings

3. **"Module not found"**
   - Use `python run_app.py` instead of `python -m monitoring.ui.main_window`
   - Make sure you're in the correct directory

4. **Serial port access issues**
   - Install CH340 drivers if using CH340-based devices
   - Check Device Manager for COM port availability
   - Run as Administrator for better port access

### Serial Port Configuration

1. **Check available ports:**
   - Open Device Manager
   - Look under "Ports (COM & LPT)"
   - Note the COM port number

2. **Install drivers:**
   - For CH340 devices: Download from [wch.cn](http://www.wch.cn/downloads/CH341SER_EXE.html)
   - For FTDI devices: Download from [ftdichip.com](https://ftdichip.com/drivers/vcp-drivers/)

3. **Configure in application:**
   - Use the Settings dialog to set the correct COM port
   - Common ports: COM1, COM2, COM3, COM4

## Features

- **Cross-platform compatibility** - Works on Windows, Linux, and macOS
- **Kiosk mode** - Fullscreen operation for production use
- **Real-time monitoring** - Live data from JSK3588 roll machine
- **Data export** - CSV and Excel export capabilities
- **Auto-recovery** - Automatic reconnection on connection loss

## Support

For technical support or issues:
1. Check the logs in the `logs/` directory
2. Review the troubleshooting section above
3. Contact the development team

## Version Information

- **Current Version:** 1.2.5
- **Last Updated:** December 2024
- **Windows Compatibility:** Windows 10/11 