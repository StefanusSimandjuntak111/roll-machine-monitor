
; Monitoring Roll Machine v1.4.4 Installer
; NSIS Script with Install/Update Support
; Includes Batch Tracking, Supabase Integration, and ERP Integration

!define APP_NAME "Monitoring Roll Machine"
!define APP_VERSION "1.4.4"
!define APP_PUBLISHER "Textilindo"
!define APP_URL "https://github.com/StefanusSimandjuntak111/roll-machine-monitor"
!define APP_EXECUTABLE "MonitoringRollMachine.exe"
!define APP_ICON "monitoring\ui\assets\icon.ico"
!define APP_UNINSTALLER "Uninstall.exe"

; Installer Information
Name "${APP_NAME} v${APP_VERSION}"
OutFile "Monitoring-Roll-Machine-v1.4.4-Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma

; Modern UI
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

; Modern UI Configuration
!define MUI_ICON "${APP_ICON}"
!define MUI_UNICON "${APP_ICON}"
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2025 ${APP_PUBLISHER}"

; Installer Sections
Section "Main Application" SecMain
    SectionIn RO
    
    ; Stop running application and services
    Call StopApplication
    Call StopServices
    
    ; Install main executable
    SetOutPath "$INSTDIR"
    File "dist\${APP_EXECUTABLE}"
    
    ; Install main application files
    File "run_app.py"
    File "requirements.txt"
    File "README.md"
    File "LICENSE.txt"
    File "SUPABASE_SCHEMA.sql"
    
    ; Install monitoring package
    SetOutPath "$INSTDIR\monitoring"
    File /r "monitoring\*"
    
    ; Install Windows scripts
    SetOutPath "$INSTDIR\windows"
    File "windows\*.bat"
    
    ; Install documentation if exists
    IfFileExists "docs\*" 0 +3
        SetOutPath "$INSTDIR\docs"
        File /r "docs\*"
    
    ; Install scripts if exists
    IfFileExists "scripts\*" 0 +3
        SetOutPath "$INSTDIR\scripts"
        File /r "scripts\*"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\${APP_NAME}"
    CreateDirectory "$APPDATA\${APP_NAME}\logs"
    CreateDirectory "$APPDATA\${APP_NAME}\exports"
    
    ; Create Program Files config directory
    CreateDirectory "$INSTDIR\config"
    
    ; Copy config if it doesn't exist
    IfFileExists "$INSTDIR\config\config.json" +2 0
        CopyFiles "$INSTDIR\monitoring\config.json" "$INSTDIR\config\config.json"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\${APP_UNINSTALLER}"
    
    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\${APP_UNINSTALLER}"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXECUTABLE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}" "" "$INSTDIR\${APP_EXECUTABLE}" 0
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\${APP_UNINSTALLER}" "" "$INSTDIR\${APP_UNINSTALLER}" 0
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXECUTABLE}" "" "$INSTDIR\${APP_EXECUTABLE}" 0
    
SectionEnd

Section "Python Environment (Optional)" SecPython
    ; This section installs Python dependencies if Python is available
    Call CheckPython
    Pop $0
    ${If} $0 == "1"
        DetailPrint "Python found, setting up virtual environment..."
        Call CreateVirtualEnv
        Call InstallRequirements
    ${Else}
        DetailPrint "Python not found, skipping virtual environment setup"
        MessageBox MB_OK|MB_ICONINFORMATION "Python was not detected. The application will run using the bundled executable.$\n$\nIf you need Python integration, please install Python 3.9+ and re-run the installer."
    ${EndIf}
SectionEnd

Section "Windows Service (Optional)" SecService
    Call InstallWindowsService
SectionEnd

Section "Database Setup (Optional)" SecDatabase
    ; Create database setup batch file
    SetOutPath "$INSTDIR"
    FileOpen $0 "$INSTDIR\setup_database.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 "echo Setting up Supabase database...$\r$\n"
    FileWrite $0 "echo Please run this script after installation to set up your database.$\r$\n"
    FileWrite $0 "echo See README.md for detailed instructions.$\r$\n"
    FileWrite $0 "pause$\r$\n"
    FileClose $0
    
    MessageBox MB_YESNO "Would you like to open the database setup instructions now?" IDYES ShowDBInstructions
    Goto EndDBInstructions
    ShowDBInstructions:
        ExecShell "open" "$INSTDIR\README.md"
    EndDBInstructions:
SectionEnd

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Install the main application and required files"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} "Set up Python virtual environment (requires Python 3.9+)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecService} "Install as Windows service for automatic startup"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDatabase} "Database setup instructions and batch tracking documentation"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Stop application and services
    Call un.StopApplication
    Call un.StopServices
    
    ; Remove files
    RMDir /r "$INSTDIR\monitoring"
    RMDir /r "$INSTDIR\windows"
    RMDir /r "$INSTDIR\docs"
    RMDir /r "$INSTDIR\scripts"
    RMDir /r "$INSTDIR\config"
    RMDir /r "$INSTDIR\venv"
    Delete "$INSTDIR\${APP_EXECUTABLE}"
    Delete "$INSTDIR\run_app.py"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\SUPABASE_SCHEMA.sql"
    Delete "$INSTDIR\setup_database.bat"
    Delete "$INSTDIR\${APP_UNINSTALLER}"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    ; Remove directories
    RMDir "$INSTDIR"
    
    ; Optional: Remove AppData (ask user)
    MessageBox MB_YESNO "Do you want to remove all application data including logs and exports?" IDYES RemoveAppData IDNO SkipAppData
    RemoveAppData:
        RMDir /r "$APPDATA\${APP_NAME}"
    SkipAppData:
    
SectionEnd

; Helper Functions
Function StopApplication
    DetailPrint "Stopping running application..."
    nsExec::ExecToStack 'taskkill /f /im "${APP_EXECUTABLE}" /t'
    Pop $0
    Sleep 2000
FunctionEnd

Function un.StopApplication
    DetailPrint "Stopping running application..."
    nsExec::ExecToStack 'taskkill /f /im "${APP_EXECUTABLE}" /t'
    Pop $0
    Sleep 2000
FunctionEnd

Function StopServices
    DetailPrint "Stopping Windows services..."
    ExecWait 'sc stop "RollMachineMonitor"' $0
    ExecWait 'sc stop "RollMachineKiosk"' $0
    Sleep 2000
FunctionEnd

Function un.StopServices
    DetailPrint "Stopping and removing Windows services..."
    ExecWait 'sc stop "RollMachineMonitor"' $0
    ExecWait 'sc delete "RollMachineMonitor"' $0
    ExecWait 'sc stop "RollMachineKiosk"' $0
    ExecWait 'sc delete "RollMachineKiosk"' $0
    Sleep 2000
FunctionEnd

Function CheckPython
    nsExec::ExecToStack 'python --version'
    Pop $0
    Pop $1
    ${If} $0 == 0
        Push "1"
    ${Else}
        Push "0"
    ${EndIf}
FunctionEnd

Function CreateVirtualEnv
    DetailPrint "Creating virtual environment..."
    SetOutPath "$INSTDIR"
    nsExec::ExecToLog 'python -m venv venv'
    Pop $0
FunctionEnd

Function InstallRequirements
    DetailPrint "Installing Python requirements..."
    SetOutPath "$INSTDIR"
    nsExec::ExecToLog '"$INSTDIR\venv\Scripts\pip.exe" install --upgrade pip'
    nsExec::ExecToLog '"$INSTDIR\venv\Scripts\pip.exe" install -r requirements.txt'
    Pop $0
FunctionEnd

Function InstallWindowsService
    DetailPrint "Installing Windows service..."
    SetOutPath "$INSTDIR\windows"
    nsExec::ExecToLog 'cmd /c install-service.bat'
    Pop $0
FunctionEnd

; Installer initialization
Function .onInit
    ; Check Windows version
    ${IfNot} ${AtLeastWin7}
        MessageBox MB_OK|MB_ICONSTOP "This application requires Windows 7 or later."
        Abort
    ${EndIf}
    
    ; Check if already installed
    ReadRegStr $0 HKLM "Software\${APP_NAME}" "Install_Dir"
    ${If} $0 != ""
        ReadRegStr $1 HKLM "Software\${APP_NAME}" "Version"
        MessageBox MB_YESNO|MB_ICONQUESTION "Monitoring Roll Machine v$1 is already installed.$\n$\nDo you want to update to version ${APP_VERSION}?$\n$\nNew in v${APP_VERSION}:$\n• ERP integration for stock entry submission$\n• Enhanced batch tracking and management$\n• Supabase cloud database integration$\n• Batch summary/recap feature$\n• Improved offline queue handling$\n• Bug fixes and performance improvements" IDYES UpdateInstall
        Abort
        UpdateInstall:
            DetailPrint "Updating from version $1 to ${APP_VERSION}..."
    ${EndIf}
FunctionEnd
