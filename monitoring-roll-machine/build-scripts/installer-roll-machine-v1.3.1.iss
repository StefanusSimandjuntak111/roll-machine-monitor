; ===============================================
; Roll Machine Monitor Windows Installer v1.3.1
; Smart Settings Update Edition
; ===============================================
;
; This installer provides:
; ✅ Complete application with all features
; ✅ Smart Settings Update functionality
; ✅ Length tolerance and formatting
; ✅ Desktop shortcuts
; ✅ Start menu entries
; ✅ Uninstaller
; ✅ Silent installation support
;
; Build with: Inno Setup Compiler 6.2+
; Requirements: Inno Setup 6.2+

[Setup]
; Basic application information
AppId={{B8E8F8A0-4B4A-4B4A-8B8A-4B4A4B4A4B4A}
AppName=Roll Machine Monitor
AppVersion=1.3.1
AppVerName=Roll Machine Monitor v1.3.1
AppPublisher=Roll Machine Solutions
AppPublisherURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
AppSupportURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/issues
AppUpdatesURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor/releases
DefaultDirName={autopf}\RollMachineMonitor
DefaultGroupName=Roll Machine Monitor
AllowNoIcons=yes
OutputDir=..\releases\windows
OutputBaseFilename=RollMachineMonitor-v1.3.1-Windows-Installer
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.17763

; Version information
VersionInfoVersion=1.3.1.0
VersionInfoCompany=Roll Machine Solutions
VersionInfoDescription=Industrial monitoring application for JSK3588 roll machines with Smart Settings Update
VersionInfoCopyright=Copyright (C) 2025 Roll Machine Solutions
VersionInfoProductName=Roll Machine Monitor
VersionInfoProductVersion=1.3.1

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
Name: "shortcuts"; Description: "Desktop Shortcuts"; Types: full custom
Name: "startmenu"; Description: "Start Menu Entries"; Types: full minimal custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; Components: shortcuts
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Components: shortcuts

[Files]
; Core application files
Source: "..\monitoring\*"; DestDir: "{app}\monitoring"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\run_app.py"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

; Scripts and tools
Source: "..\scripts\start_windows.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "..\scripts\start_windows.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "..\scripts\start_serial_tool.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core
Source: "..\tools\serial_tool.py"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: core

; Windows specific files
Source: "..\windows\*"; DestDir: "{app}\windows"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

[Icons]
; Start Menu Icons
Name: "{group}\Roll Machine Monitor"; Filename: "{app}\run_app.py"; WorkingDir: "{app}"; IconFilename: "{app}\monitoring\ui\assets\icon.ico"; IconIndex: 0; Components: startmenu
Name: "{group}\Serial Tool"; Filename: "{app}\tools\serial_tool.py"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Uninstall Roll Machine Monitor"; Filename: "{uninstallexe}"; Components: startmenu

; Desktop Icons
Name: "{autodesktop}\Roll Machine Monitor"; Filename: "{app}\run_app.py"; WorkingDir: "{app}"; IconFilename: "{app}\monitoring\ui\assets\icon.ico"; IconIndex: 0; Tasks: desktopicon; Components: shortcuts

[Registry]
; Register application for uninstall
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#SetupSetting("AppName")}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "UninstallString"; ValueData: "{uninstallexe}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\monitoring\ui\assets\icon.ico"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#SetupSetting("AppPublisher")}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#SetupSetting("AppPublisherURL")}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "URLUpdateInfo"; ValueData: "{#SetupSetting("AppUpdatesURL")}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "HelpLink"; ValueData: "{#SetupSetting("AppSupportURL")}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: dword; ValueName: "NoModify"; ValueData: 1; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: dword; ValueName: "NoRepair"; ValueData: 1; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#SetupSetting("AppVersion")}"; Flags: uninsdeletekey

[Run]
; Run application after installation
Filename: "{app}\run_app.py"; Description: "Launch Roll Machine Monitor"; Flags: postinstall nowait skipifsilent; WorkingDir: "{app}"

[Code]
// Custom code for installation
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create logs directory if it doesn't exist
    if not DirExists(ExpandConstant('{app}\logs')) then
      CreateDir(ExpandConstant('{app}\logs'));
      
    // Create exports directory if it doesn't exist
    if not DirExists(ExpandConstant('{app}\exports')) then
      CreateDir(ExpandConstant('{app}\exports'));
  end;
end; 