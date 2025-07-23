; ===============================================
; Roll Machine Monitor Windows Installer v1.3.2
; Roll Time Fix & Restart Button Edition
; ===============================================
;
; This installer provides:
; ✅ Complete application with all features
; ✅ Roll time fix for first product
; ✅ Restart button functionality
; ✅ Logging table descending order
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
OutputBaseFilename=RollMachineMonitor-v1.3.2-Windows-Installer
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
Name: "{group}\Roll Machine Monitor"; Filename: "{app}\run_app.py"; WorkingDir: "{app}"; IconFilename: "{app}\monitoring\ui\icons\app_icon.ico"; IconIndex: 0; Components: startmenu
Name: "{group}\Serial Tool"; Filename: "{app}\tools\serial_tool.py"; WorkingDir: "{app}"; Components: startmenu
Name: "{group}\Uninstall Roll Machine Monitor"; Filename: "{uninstallexe}"; Components: startmenu

; Desktop Icons
Name: "{autodesktop}\Roll Machine Monitor"; Filename: "{app}\run_app.py"; WorkingDir: "{app}"; IconFilename: "{app}\monitoring\ui\icons\app_icon.ico"; IconIndex: 0; Tasks: desktopicon; Components: shortcuts

[Registry]
; Application registry entries
Root: HKLM; Subkey: "SOFTWARE\Roll Machine Monitor"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Roll Machine Monitor"; ValueType: string; ValueName: "Version"; ValueData: "1.3.2"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Roll Machine Monitor"; ValueType: string; ValueName: "Publisher"; ValueData: "Roll Machine Solutions"; Flags: uninsdeletekey

[Run]
; Post-installation tasks
Filename: "{app}\run_app.py"; Description: "{cm:LaunchProgram,Roll Machine Monitor}"; Flags: nowait postinstall skipifsilent; WorkingDir: "{app}"

[Code]
; Custom installation code
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

[UninstallDelete]
; Clean up additional files
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\logs\*.log"
Type: dirifempty; Name: "{app}\logs"
Type: dirifempty; Name: "{app}" 