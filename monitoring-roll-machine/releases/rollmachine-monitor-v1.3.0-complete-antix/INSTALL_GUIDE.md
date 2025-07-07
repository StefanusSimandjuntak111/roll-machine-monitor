# Installation Guide - Roll Machine Monitor v1.3.0 
 
## Quick Start 
 
1. Extract the package: 
   ```bash 
   tar -xzf rollmachine-monitor-v1.3.0-complete-antix.tar.gz 
   cd rollmachine-monitor-v1.3.0-complete-antix 
   ``` 
 
2. Install everything automatically: 
   ```bash 
   sudo ./install-complete-antix.sh 
   ``` 
 
3. For updates (preserves settings): 
   ```bash 
   sudo ./install-complete-antix.sh --update 
   ``` 
 
## Features 
 
- Desktop shortcuts for regular and kiosk modes 
- Automatic service setup with SysV init scripts 
- Kiosk user (username: kiosk, password: kiosk123) 
- Watchdog process monitoring 
- Complete offline installation support 
- Logs in /opt/rollmachine-monitor/logs/ 
