
; Monitoring Roll Machine v1.4.5 Installer
; NSIS Script with Install/Update Support
; Fix BrokenPipeError and Enhanced Error Handling

!define APP_NAME "Monitoring Roll Machine"
!define APP_VERSION "1.4.5"
!define APP_PUBLISHER "Textilindo"
!define APP_URL "https://github.com/StefanusSimandjuntak111/roll-machine-monitor"
!define APP_EXECUTABLE "MonitoringRollMachine.exe"
!define APP_ICON "monitoring\ui\assets\icon.ico"
!define APP_UNINSTALLER "Uninstall.exe"

; Installer Information
Name "${APP_NAME} v${APP_VERSION}"
OutFile "Monitoring-Roll-Machine-v1.4.5-Setup.exe"
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
VIAddVersionKey "LegalCopyright" "Copyright (C) 2026 ${APP_PUBLISHER}"

; Installer Sections
Section "Main Application" SecMain
    SectionIn RO
    
    ; Stop running application
    Call StopApplication
    
    ; Install main executable
    SetOutPath "$INSTDIR"
    File "dist\${APP_EXECUTABLE}"
    
    ; Install application files
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
    File /nonfatal "windows\*.bat"
    
    ; Create application data directory
    CreateDirectory "$APPDATA\${APP_NAME}"
    CreateDirectory "$APPDATA\${APP_NAME}\logs"
    CreateDirectory "$APPDATA\${APP_NAME}\exports"
    
    ; Create config directory
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

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Install the main application and required files (includes BrokenPipeError fix)"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Stop application
    Call un.StopApplication
    
    ; Remove files
    RMDir /r "$INSTDIR\monitoring"
    RMDir /r "$INSTDIR\windows"
    RMDir /r "$INSTDIR\config"
    Delete "$INSTDIR\${APP_EXECUTABLE}"
    Delete "$INSTDIR\run_app.py"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\SUPABASE_SCHEMA.sql"
    Delete "$INSTDIR\${APP_UNINSTALLER}"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    ; Remove directories
    RMDir "$INSTDIR"
    
    ; Optional: Remove AppData
    MessageBox MB_YESNO "Remove all application data?" IDYES RemoveAppData IDNO SkipAppData
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
        MessageBox MB_YESNO|MB_ICONQUESTION "Monitoring Roll Machine v$1 is already installed.$\n$\nDo you want to update to version ${APP_VERSION}?$\n$\nNew in v${APP_VERSION}:$\n• Fix BrokenPipeError on ERP submission$\n• Enhanced error handling with HTML parsing$\n• Multi-layer validation for stock_entry_type$\n• Improved BOM settings management$\n• Custom batch name format support$\n• Cycle time detection fix (0.01 yard)$\n• User-friendly Indonesian error messages" IDYES UpdateInstall
        Abort
        UpdateInstall:
            DetailPrint "Updating from version $1 to ${APP_VERSION}..."
    ${EndIf}
FunctionEnd
