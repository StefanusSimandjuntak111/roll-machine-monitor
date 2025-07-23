; ===============================================
; Roll Machine Monitor Windows Offline Installer v1.3.2
; Complete Self-Contained Installer - No Internet Required
; ===============================================
;
; This installer provides:
; ✅ Complete application with all dependencies
; ✅ Roll time fix for first product
; ✅ Restart button functionality
; ✅ Logging table descending order
; ✅ Version display in UI
; ✅ Smart Settings Update functionality
; ✅ Desktop shortcuts
; ✅ Start menu entries
; ✅ Offline installation (no internet required)
; ✅ Uninstaller
;
; Build with: Inno Setup Compiler 6.2+
; Requirements: Inno Setup 6.2+

[Setup]
; Basic application information
AppId={{B8E8F8A0-4B4A-4B4A-8B8A-4B4A4B4A4B4A}
AppName=Roll Machine Monitor
AppVersion=1.3.2
AppVerName=Roll Machine Monitor v1.3.2
AppPublisher=Roll Machine Solutions
AppPublisherURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
AppSupportURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/issues
AppUpdatesURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/releases
DefaultDirName={autopf}\RollMachineMonitor
DefaultGroupName=Roll Machine Monitor
AllowNoIcons=yes
OutputDir=..\releases\windows
OutputBaseFilename=RollMachineMonitor-v1.3.2-Windows-Offline-Installer
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.17763

; Version information
VersionInfoVersion=1.3.2.0
VersionInfoCompany=Roll Machine Solutions
VersionInfoDescription=Industrial monitoring application for JSK3588 roll machines with Roll Time Fix and Restart Button
VersionInfoCopyright=Copyright (C) 2025 Roll Machine Solutions
VersionInfoProductName=Roll Machine Monitor
VersionInfoProductVersion=1.3.2

; Uninstall information
UninstallDisplayName=Roll Machine Monitor
CreateUninstallRegKey=yes

; Installation options
DisableProgramGroupPage=no
DisableReadyPage=no
DisableFinishedPage=no
DisableWelcomePage=no
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage

; Progress and UI
ShowTasksTreeLines=yes
AllowCancelDuringInstall=no
RestartIfNeededByRun=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full Installation (Recommended)"; Flags: iscustom
Name: "minimal"; Description: "Minimal Installation"
Name: "custom"; Description: "Custom Installation"

[Components]
Name: "core"; Description: "Core Application"; Types: full minimal custom; Flags: fixed
Name: "service"; Description: "Windows Service (Auto-start)"; Types: full custom
Name: "shortcuts"; Description: "Desktop Shortcuts"; Types: full custom
Name: "startmenu"; Description: "Start Menu Entries"; Types: full minimal custom
Name: "firewall"; Description: "Windows Firewall Exception"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; Components: shortcuts
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Components: shortcuts
Name: "autostart"; Description: "Start automatically with Windows"; GroupDescription: "Auto-start Options"; Components: service
Name: "firewallrule"; Description: "Add Windows Firewall exception"; GroupDescription: "Network Options"; Components: firewall

[Files]
; Core application files
Source: "..\monitoring\*"; DestDir: "{app}\monitoring"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\run_app.py"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Windows-specific files
Source: "..\windows\start-rollmachine.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: core
Source: "..\windows\start-rollmachine-kiosk.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: core
Source: "..\windows\install-service.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: service
Source: "..\windows\uninstall-service.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: service
Source: "..\windows\setup-environment.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: core

; Scripts and tools
Source: "..\scripts\start_windows.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "..\scripts\start_windows.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "..\scripts\start_serial_tool.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "..\tools\serial_tool.py"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: core

[Icons]
; Start menu icons
Name: "{group}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Roll Machine Monitor (Kiosk)"; Filename: "{app}\windows\start-rollmachine-kiosk.bat"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Serial Tool"; Filename: "{app}\tools\serial_tool.py"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Configuration"; Filename: "{app}\monitoring\config.json"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Logs Folder"; Filename: "{app}\logs"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Exports Folder"; Filename: "{app}\exports"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\{cm:UninstallProgram,Roll Machine Monitor}"; Filename: "{uninstallexe}"; Components: startmenu

; Desktop icons
Name: "{autoprograms}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autodesktop}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autodesktop}\Roll Machine Monitor (Kiosk)"; Filename: "{app}\windows\start-rollmachine-kiosk.bat"; WorkingDir: "{app}"; Tasks: desktopicon

; Quick launch icons
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Dirs]
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\exports"; Permissions: users-full
Name: "{app}\monitoring\logs"; Permissions: users-full
Name: "{app}\monitoring\exports"; Permissions: users-full

[Registry]
; Application registration
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: string; ValueName: "Version"; ValueData: "1.3.2"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: dword; ValueName: "Installed"; ValueData: 1; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetInstallDate}"; Flags: uninsdeletekey

; URL protocol registration (for updates)
Root: HKLM; Subkey: "SOFTWARE\Classes\rollmachine"; ValueType: string; ValueName: ""; ValueData: "Roll Machine Monitor Protocol"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Classes\rollmachine"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Classes\rollmachine\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\windows\start-rollmachine.bat"" ""%1"""; Flags: uninsdeletekey

; Auto-start registry entry
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "RollMachineMonitor"; ValueData: """{app}\windows\start-rollmachine.bat"""; Tasks: autostart; Flags: uninsdeletevalue

; Uninstall information
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: string; ValueName: "DisplayName"; ValueData: "Roll Machine Monitor"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "1.3.2"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: string; ValueName: "Publisher"; ValueData: "Roll Machine Solutions"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: string; ValueName: "UninstallString"; ValueData: """{uninstallexe}"""; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: dword; ValueName: "NoModify"; ValueData: 1; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: dword; ValueName: "NoRepair"; ValueData: 1; Flags: uninsdeletekey

[Run]
; Setup Python environment and install requirements
Filename: "{app}\windows\setup-environment.bat"; StatusMsg: "Setting up Python environment and installing requirements..."; Flags: waituntilterminated shellexec; Components: core

; Install Windows service (simple batch file call)
Filename: "{app}\windows\install-service.bat"; StatusMsg: "Installing Windows service..."; Flags: waituntilterminated shellexec; Components: service

; Add firewall exception
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=RollMachineMonitor dir=in action=allow program={app}\venv\Scripts\python.exe enable=yes"; StatusMsg: "Adding firewall exception..."; Flags: waituntilterminated runhidden; Tasks: firewallrule

[UninstallRun]
; Stop and remove Windows service
Filename: "{app}\windows\uninstall-service.bat"; Flags: waituntilterminated runhidden; Components: service

; Remove firewall rule
Filename: "netsh"; Parameters: "advfirewall firewall delete rule name=RollMachineMonitor"; Flags: waituntilterminated runhidden; Tasks: firewallrule

; Remove auto-start entry
Filename: "reg"; Parameters: "delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v RollMachineMonitor /f"; Flags: waituntilterminated runhidden

[UninstallDelete]
; Clean up logs and temporary files
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\monitoring\__pycache__"

[Code]
// Check if this is an update installation
function IsUpdate: Boolean;
var
  InstalledVersion: String;
begin
  Result := RegQueryStringValue(HKLM, 'SOFTWARE\RollMachineMonitor', 'Version', InstalledVersion) and (InstalledVersion <> '');
  if Result then
    Log('Update installation detected. Current version: ' + InstalledVersion);
end;

// Get installation date
function GetInstallDate(Param: string): string;
begin
  Result := GetDateTimeString('yyyy-mm-dd', '-', ':');
end;

// Check if application is running
function IsAppRunning: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('tasklist', '/FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Roll Machine Monitor*"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
  if Result then
    Log('Application is currently running');
end; 