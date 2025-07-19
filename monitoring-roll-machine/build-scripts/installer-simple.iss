; ===============================================
; Roll Machine Monitor Windows Installer v1.3.1
; Simple Installer for Executable
; ===============================================

[Setup]
AppId={{B8E8F8A0-4B4A-4B4A-8B8A-4B4A4B4A4B4A}
AppName=Roll Machine Monitor
AppVersion=1.3.1
AppVerName=Roll Machine Monitor v1.3.1
AppPublisher=Roll Machine Solutions
AppPublisherURL=https://github.com/StefanusSimandjuntak111/roll-machine-monitor
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

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\RollMachineMonitor-v1.3.1.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\monitoring\*"; DestDir: "{app}\monitoring"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\run_app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\exports"; Permissions: users-full

[Icons]
Name: "{group}\Roll Machine Monitor"; Filename: "{app}\RollMachineMonitor-v1.3.1.exe"
Name: "{autodesktop}\Roll Machine Monitor"; Filename: "{app}\RollMachineMonitor-v1.3.1.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RollMachineMonitor-v1.3.1.exe"; Description: "{cm:LaunchProgram,Roll Machine Monitor}"; Flags: nowait postinstall skipifsilent 