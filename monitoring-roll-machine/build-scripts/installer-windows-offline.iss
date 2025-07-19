; ===============================================
; Roll Machine Monitor Windows Offline Installer v1.3.0
; Complete Self-Contained Installer - No Internet Required
; ===============================================
;
; This installer provides:
; ✅ Embedded Python 3.11 (no download needed)
; ✅ All Python packages pre-bundled
; ✅ Virtual environment pre-created
; ✅ Desktop shortcuts
; ✅ Windows service setup
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
AppVersion=1.3.0
AppVerName=Roll Machine Monitor v1.3.0
AppPublisher=Roll Machine Solutions
AppPublisherURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
AppSupportURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/issues
AppUpdatesURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/releases
DefaultDirName={autopf}\RollMachineMonitor
DefaultGroupName=Roll Machine Monitor
AllowNoIcons=yes
OutputDir=..\releases\windows
OutputBaseFilename=RollMachineMonitor-v1.3.0-Windows-Offline-Installer
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.17763

; Version information
VersionInfoVersion=1.3.0.0
VersionInfoCompany=Roll Machine Solutions
VersionInfoDescription=Industrial monitoring application for JSK3588 roll machines
VersionInfoCopyright=Copyright (C) 2025 Roll Machine Solutions
VersionInfoProductName=Roll Machine Monitor
VersionInfoProductVersion=1.3.0

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

[Icons]
; Start menu icons
Name: "{group}\Roll Machine Monitor"; Filename: "{app}\windows\start-rollmachine.bat"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Roll Machine Monitor (Kiosk)"; Filename: "{app}\windows\start-rollmachine-kiosk.bat"; WorkingDir: "{app}"; Components: startmenu
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
Root: HKLM; Subkey: "SOFTWARE\RollMachineMonitor"; ValueType: string; ValueName: "Version"; ValueData: "1.3.0"; Flags: uninsdeletekey
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
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\RollMachineMonitor"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "1.3.0"; Flags: uninsdeletekey
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

// Stop running application
procedure StopApp;
var
  ResultCode: Integer;
begin
  if IsAppRunning then begin
    Log('Stopping running application...');
    Exec('taskkill', '/F /IM python.exe /FI "WINDOWTITLE eq Roll Machine Monitor*"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(2000);
  end;
end;

// Custom messages for installation steps
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption := 
    'This will install Roll Machine Monitor v1.3.0 on your computer.' + #13#10 + #13#10 +
    'Roll Machine Monitor is an industrial monitoring application for JSK3588 roll machines.' + #13#10 + #13#10 +
    'Features:' + #13#10 +
    '• Complete offline installation (no internet required)' + #13#10 +
    '• Pre-bundled Python environment' + #13#10 +
    '• Desktop shortcuts and Start menu integration' + #13#10 +
    '• Windows service for auto-start' + #13#10 +
    '• Kiosk mode for fullscreen operation' + #13#10 +
    '• Serial port communication' + #13#10 +
    '• Data export capabilities' + #13#10 + #13#10 +
    'Click Next to continue.';
end;

// Pre-installation checks
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  // Stop any running instances
  StopApp;
  // Backup existing config if this is an update
  if IsUpdate then begin
    if FileExists(ExpandConstant('{app}\monitoring\config.json')) then begin
      FileCopy(ExpandConstant('{app}\monitoring\config.json'), 
               ExpandConstant('{tmp}\config-backup.json'), False);
      Log('Configuration backed up for update');
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
      Log('Configuration restored after update');
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
      '• Use kiosk mode for fullscreen operation' + #13#10 +
      '• Update the application via Start menu shortcut' + #13#10 + #13#10 +
      'The application will start automatically with Windows if you selected that option.' + #13#10 + #13#10 +
      'Configuration files are located in:' + #13#10 +
      ExpandConstant('{app}\monitoring\config.json') + #13#10 + #13#10 +
      'Logs and exports are saved in:' + #13#10 +
      ExpandConstant('{app}\logs\') + ' and ' + ExpandConstant('{app}\exports\') + #13#10 + #13#10 +
      'For support, visit: https://github.com/StefanusSimandjuntak111/roll-machine-monitor';
  end;
end;

// Handle silent installation
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpWelcome then begin
    if WizardSilent then begin
      // Auto-select components for silent install
      WizardSelectComponents('core,service,startmenu,firewall');
      WizardSelectTasks('autostart,firewallrule');
    end;
  end;
end; 