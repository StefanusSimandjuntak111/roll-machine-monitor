@echo off
REM ===============================================
REM GitHub Release Creator for Roll Machine Monitor
REM ===============================================

set VERSION=1.3.1
set REPOSITORY=StefanusSimandjuntak111/roll-machine-monitor
set INSTALLER_PATH=..\releases\windows\RollMachineMonitor-v1.3.1-Windows-Installer.exe

echo.
echo ===============================================
echo Creating GitHub Release for v%VERSION%
echo ===============================================
echo.

REM Check if GitHub CLI is installed
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI (gh) not found!
    echo Please install GitHub CLI from: https://cli.github.com/
    echo.
    echo Alternative: Create release manually on GitHub website
    echo 1. Go to: https://github.com/%REPOSITORY%/releases
    echo 2. Click 'Create a new release'
    echo 3. Tag: v%VERSION%
    echo 4. Title: Roll Machine Monitor v%VERSION% - Smart Settings Update
    echo 5. Copy content from: docs/GITHUB_RELEASE_v%VERSION%.md
    echo 6. Upload installer: %INSTALLER_PATH%
    echo.
    pause
    exit /b 1
)

REM Check if installer exists
if not exist "%INSTALLER_PATH%" (
    echo Installer not found: %INSTALLER_PATH%
    echo Please build the installer first using:
    echo   build-installer-v%VERSION%.bat
    echo.
    pause
    exit /b 1
)

REM Check if release notes exist
set RELEASE_NOTES_PATH=..\docs\GITHUB_RELEASE_v%VERSION%.md
if not exist "%RELEASE_NOTES_PATH%" (
    echo Release notes not found: %RELEASE_NOTES_PATH%
    echo.
    pause
    exit /b 1
)

echo Repository: %REPOSITORY%
echo Version: v%VERSION%
echo Installer: %INSTALLER_PATH%
echo Release Notes: %RELEASE_NOTES_PATH%
echo.

REM Confirm release creation
set /p CONFIRM="Create GitHub release for v%VERSION%? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Release creation cancelled.
    exit /b 0
)

echo.
echo Creating GitHub release...

REM Create release with GitHub CLI
set RELEASE_TITLE=Roll Machine Monitor v%VERSION% - Smart Settings Update

REM Create the release
gh release create v%VERSION% --title "%RELEASE_TITLE%" --notes-file "%RELEASE_NOTES_PATH%" --repo %REPOSITORY%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===============================================
    echo SUCCESS: GitHub release created!
    echo ===============================================
    echo.
    
    REM Upload installer asset
    echo Uploading installer asset...
    gh release upload v%VERSION% "%INSTALLER_PATH%" --repo %REPOSITORY%
    
    if %ERRORLEVEL% EQU 0 (
        echo Installer uploaded successfully!
    ) else (
        echo Warning: Failed to upload installer
    )
    
    echo.
    echo Release URL: https://github.com/%REPOSITORY%/releases/tag/v%VERSION%
    echo.
    echo Release created successfully!
    echo Users can now download the installer from GitHub.
    echo.
    
    REM Open release URL
    set /p OPEN_BROWSER="Open release page in browser? (y/n): "
    if /i "%OPEN_BROWSER%"=="y" (
        start https://github.com/%REPOSITORY%/releases/tag/v%VERSION%
    )
    
) else (
    echo.
    echo ===============================================
    echo ERROR: Failed to create GitHub release!
    echo ===============================================
    echo.
    echo Please check:
    echo 1. GitHub CLI authentication (gh auth login)
    echo 2. Repository access permissions
    echo 3. Tag already exists (delete if needed)
    echo.
)

pause 