; ===============================================
; Roll Machine Monitor Windows Installer v1.3.0
; Complete All-in-One Installer using Inno Setup
; ===============================================
;
; This installer provides:
; ✅ Python installation (if needed)
; ✅ Virtual environment creation
; ✅ All Python requirements installation
; ✅ Desktop shortcuts
; ✅ Windows service setup
; ✅ Start menu entries
; ✅ Automatic updates support
; ✅ Uninstaller
;
; Build with: Inno Setup Compiler
; Requirements: Inno Setup 6.0+

[Setup]
; Basic application information
AppId={{B8E8F8A0-4B4A-4B4A-8B8A-4B4A4B4A4B4A}
AppName=Roll Machine Monitor
AppVersion=1.3.0
AppPublisher=Roll Machine Solutions
AppPublisherURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
AppSupportURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/issues
AppUpdatesURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/releases
DefaultDirName={autopf}\RollMachineMonitor
DefaultGroupName=Roll Machine Monitor
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=INSTALL_INFO_WINDOWS.txt
InfoAfterFile=POST_INSTALL_INFO_WINDOWS.txt
OutputDir=releases\windows
OutputBaseFilename=RollMachineMonitor-v1.3.0-Windows-Installer
SetupIconFile=assets\rollmachine-icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Version information
VersionInfoVersion=1.3.0.0
VersionInfoCompany=Roll Machine Solutions
VersionInfoDescription=Industrial monitoring application for JSK3588 roll machines
VersionInfoCopyright=Copyright (C) 2025 Roll Machine Solutions
VersionInfoProductName=Roll Machine Monitor
VersionInfoProductVersion=1.3.0

; Uninstall information
UninstallDisplayName=Roll Machine Monitor
UninstallDisplayIcon={app}\assets\rollmachine-icon.ico
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
Name: "full"; Description: "Full Installation (Recommended)"
Name: "minimal"; Description: "Minimal Installation"
Name: "custom"; Description: "Custom Installation"; Flags: iscustom

[Components]
Name: "core"; Description: "Core Application"; Types: full minimal custom; Flags: fixed
Name: "python"; Description: "Python 3.11 (if not installed)"; Types: full minimal custom; Check: not IsPythonInstalled
Name: "service"; Description: "Windows Service (Auto-start)"; Types: full custom
Name: "shortcuts"; Description: "Desktop Shortcuts"; Types: full custom
Name: "startmenu"; Description: "Start Menu Entries"; Types: full minimal custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; Components: shortcuts
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Components: shortcuts
Name: "autostart"; Description: "Start automatically with Windows"; GroupDescription: "Auto-start Options"; Components: service
Name: "firewall"; Description: "Add Windows Firewall exception"; GroupDescription: "Network Options"

[Files]
; Core application files
Source: "monitoring\*"; DestDir: "{app}\monitoring"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "run_app.py"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Windows-specific files
Source: "windows\*"; DestDir: "{app}\windows"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Python installer (embedded)
Source: "python-installer\python-3.11.7-amd64.exe"; DestDir: "{tmp}"; Flags: external deleteafterinstall; Components: python; Check: not IsPythonInstalled

; Service files
Source: "windows\rollmachine-service.py"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: service
Source: "windows\install-service.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: service
Source: "windows\uninstall-service.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: service

; Batch scripts
Source: "windows\setup-environment.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: core
Source: "windows\start-rollmachine.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: core
Source: "windows\start-rollmachine-kiosk.bat"; DestDir: "{app}\windows"; Flags: ignoreversion; Components: core

[Icons]
; Start menu icons
Name: "{group}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\rollmachine-icon.ico"; Components: startmenu
Name: "{group}\Roll Machine Monitor (Kiosk)"; Filename: "{app}\windows\start-rollmachine-kiosk.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\rollmachine-icon.ico"; Components: startmenu
Name: "{group}\Configuration"; Filename: "{app}\monitoring\config.json"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Logs Folder"; Filename: "{app}\logs"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Exports Folder"; Filename: "{app}\exports"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\{cm:UninstallProgram,Roll Machine Monitor}"; Filename: "{uninstallexe}"; Components: startmenu

; Desktop icons
Name: "{autoprograms}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\rollmachine-icon.ico"; Tasks: desktopicon
Name: "{autodesktop}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\rollmachine-icon.ico"; Tasks: desktopicon
Name: "{autodesktop}\Roll Machine Monitor (Kiosk)"; Filename: "{app}\windows\start-rollmachine-kiosk.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\rollmachine-icon.ico"; Tasks: desktopicon

; Quick launch icons
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\rollmachine-icon.ico"; Tasks: quicklaunchicon

[Dirs]
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\exports"; Permissions: users-full
Name: "{app}\monitoring\logs"; Permissions: users-full
Name: "{app}\monitoring\exports"; Permissions: users-full
Name: "{app}\venv"; Permissions: users-full

[Registry]
; Application registration
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: string; ValueName: "Version"; ValueData: "1.3.0"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: dword; ValueName: "Installed"; ValueData: 1; Flags: uninsdeletekey

; URL protocol registration (for updates)
Root: HKLM; Subkey: "SOFTWARE\Classes\rollmachine"; ValueType: string; ValueName: ""; ValueData: "Roll Machine Monitor Protocol"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Classes\rollmachine"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Classes\rollmachine\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\windows\start-rollmachine.bat"" ""%1"""; Flags: uninsdeletekey

; Auto-start registry entry
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "RollMachineMonitor"; ValueData: """{app}\windows\start-rollmachine.bat"""; Tasks: autostart; Flags: uninsdeletevalue

[Run]
; Install Python if needed
Filename: "{tmp}\python-3.11.7-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"; StatusMsg: "Installing Python 3.11..."; Flags: waituntilterminated; Components: python; Check: not IsPythonInstalled

; Setup Python environment and install requirements
Filename: "{app}\windows\setup-environment.bat"; StatusMsg: "Setting up Python environment and installing requirements..."; Flags: waituntilterminated; Components: core

; Install Windows service
Filename: "{app}\windows\install-service.bat"; StatusMsg: "Installing Windows service..."; Flags: waituntilterminated; Components: service

; Add firewall exception
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""Roll Machine Monitor"" dir=in action=allow program=""{app}\venv\Scripts\python.exe"""; StatusMsg: "Adding firewall exception..."; Flags: waituntilterminated runhidden; Tasks: firewall

[UninstallRun]
; Stop and remove Windows service
Filename: "{app}\windows\uninstall-service.bat"; Flags: waituntilterminated runhidden; Components: service

; Remove firewall rule
Filename: "netsh"; Parameters: "advfirewall firewall delete rule name=""Roll Machine Monitor"""; Flags: waituntilterminated runhidden; Tasks: firewall

[UninstallDelete]
; Clean up logs and temporary files
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\monitoring\__pycache__"

[Code]
// Check if Python is installed
function IsPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
  if not Result then
    Result := Exec('py', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// Check if this is an update installation
function IsUpdate: Boolean;
var
  InstalledVersion: String;
begin
  Result := RegQueryStringValue(HKLM, 'SOFTWARE\RollMachineMonitor', 'Version', InstalledVersion) and (InstalledVersion <> '');
end;

// Custom messages for installation steps
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption := 
    'This will install Roll Machine Monitor v1.3.0 on your computer.' + #13#10 + #13#10 +
    'Roll Machine Monitor is an industrial monitoring application for JSK3588 roll machines.' + #13#10 + #13#10 +
    'Features:' + #13#10 +
    '• Complete Python environment setup' + #13#10 +
    '• Desktop shortcuts and Start menu integration' + #13#10 +
    '• Windows service for auto-start' + #13#10 +
    '• Kiosk mode for fullscreen operation' + #13#10 +
    '• Serial port communication' + #13#10 +
    '• Data export capabilities' + #13#10 + #13#10 +
    'Click Next to continue.';
end;

// Pre-installation checks
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  
  // Check if we need to stop any running instances
  if Exec('taskkill', '/F /IM python.exe /FI "WINDOWTITLE eq Roll Machine Monitor*"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    Sleep(2000);
    
  // Backup existing config if this is an update
  if IsUpdate then begin
    if FileExists(ExpandConstant('{app}\monitoring\config.json')) then begin
      FileCopy(ExpandConstant('{app}\monitoring\config.json'), 
               ExpandConstant('{tmp}\config-backup.json'), False);
    end;
  end;
end;

// Post-installation tasks
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    // Restore backed up config
    if IsUpdate and FileExists(ExpandConstant('{tmp}\config-backup.json')) then begin
      FileCopy(ExpandConstant('{tmp}\config-backup.json'), 
               ExpandConstant('{app}\monitoring\config.json'), False);
    end;
  end;
end;

// Custom finish page message
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then begin
    WizardForm.FinishedLabel.Caption := 
      'Roll Machine Monitor v1.3.0 has been successfully installed!' + #13#10 + #13#10 +
      'You can now:' + #13#10 +
      '• Start the application from the desktop shortcut' + #13#10 +
      '• Access it from the Start menu' + #13#10 +
      '• Use kiosk mode for fullscreen operation' + #13#10 + #13#10 +
      'The application will start automatically with Windows if you selected that option.' + #13#10 + #13#10 +
      'Configuration files are located in:' + #13#10 +
      ExpandConstant('{app}\monitoring\config.json') + #13#10 + #13#10 +
      'Logs and exports are saved in:' + #13#10 +
      ExpandConstant('{app}\logs\') + ' and ' + ExpandConstant('{app}\exports\');
  end;
end; 