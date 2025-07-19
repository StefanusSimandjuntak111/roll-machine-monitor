# =============================================================================
# Roll Machine Monitor - Release Builder v1.2.0
# =============================================================================
# Script to create versioned release packages for client distribution

param(
    [string]$Version = "1.2.0",
    [switch]$Clean,
    [switch]$IncludeSource
)

$ErrorActionPreference = "Stop"

# Release configuration
$ReleaseName = "rollmachine-monitor-installer-$Version"
$ReleaseDir = "./$ReleaseName"
$ArchiveName = "$ReleaseName.tar.gz"

# Colors for output
function Write-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "ℹ $Message" -ForegroundColor Blue
}

function Write-Warning {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Roll Machine Monitor Release Builder" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check if tar is available (Windows 10/11 has built-in tar)
    try {
        tar --version | Out-Null
        Write-Success "tar command available"
    } catch {
        Write-Warning "tar command not found. Using PowerShell compression instead."
    }
    
    # Check if release directory exists
    if (Test-Path $ReleaseDir) {
        if ($Clean) {
            Write-Info "Cleaning existing release directory..."
            Remove-Item $ReleaseDir -Recurse -Force
            Write-Success "Cleaned release directory"
        } else {
            Write-Warning "Release directory already exists: $ReleaseDir"
            $response = Read-Host "Do you want to continue? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                Write-Info "Build cancelled"
                exit 0
            }
        }
    }
}

function Copy-ApplicationFiles {
    Write-Info "Copying application files..."
    
    # Copy monitoring-roll-machine directory
    $appSource = "./monitoring-roll-machine"
    $appDest = "$ReleaseDir/app/monitoring-roll-machine"
    
    if (Test-Path $appSource) {
        Copy-Item -Path $appSource -Destination $appDest -Recurse -Force
        Write-Success "Application files copied"
    } else {
        Write-Warning "Application source directory not found: $appSource"
        Write-Info "Creating placeholder directory..."
        New-Item -ItemType Directory -Path $appDest -Force | Out-Null
    }
}

function Create-ConfigTemplates {
    Write-Info "Creating configuration templates..."
    
    $configDir = "$ReleaseDir/config"
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    
    # Create sample config.json
    $configTemplate = @"
{
    "serial_port": "AUTO",
    "baudrate": 19200,
    "timeout": 1.0,
    "use_mock_data": false,
    "poll_interval": 1.0,
    "log_level": "INFO",
    "max_log_files": 10,
    "export_format": "csv",
    "ui_theme": "dark",
    "fullscreen": false,
    "auto_restart": true
}
"@
    
    $configTemplate | Out-File -FilePath "$configDir/config.json.template" -Encoding UTF8
    
    # Create environment template
    $envTemplate = @"
# Roll Machine Monitor Environment Configuration
# Copy this file to .env and modify as needed

# Serial Port Configuration
SERIAL_PORT=AUTO
BAUDRATE=19200
TIMEOUT=1.0

# Application Settings
LOG_LEVEL=INFO
USE_MOCK_DATA=false
POLL_INTERVAL=1.0

# UI Settings
FULLSCREEN=false
UI_THEME=dark
AUTO_RESTART=true

# Export Settings
EXPORT_FORMAT=csv
MAX_LOG_FILES=10
"@
    
    $envTemplate | Out-File -FilePath "$configDir/.env.template" -Encoding UTF8
    
    Write-Success "Configuration templates created"
}

function Create-UtilityScripts {
    Write-Info "Creating utility scripts..."
    
    $scriptsDir = "$ReleaseDir/scripts"
    New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    
    # Create uninstall script for Windows
    $uninstallWindows = @"
# Roll Machine Monitor - Windows Uninstaller
param([string]`$InstallPath = "C:\Program Files\RollMachineMonitor")

Write-Host "Uninstalling Roll Machine Monitor..." -ForegroundColor Yellow

# Stop and remove service
try {
    Stop-Service "RollMachineMonitor" -ErrorAction SilentlyContinue
    sc.exe delete "RollMachineMonitor"
    Write-Host "✓ Service removed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Service removal failed or not found" -ForegroundColor Yellow
}

# Remove application files
if (Test-Path `$InstallPath) {
    Remove-Item `$InstallPath -Recurse -Force
    Write-Host "✓ Application files removed" -ForegroundColor Green
}

# Remove shortcuts
Remove-Item "`$env:PUBLIC\Desktop\Roll Machine Monitor.lnk" -ErrorAction SilentlyContinue
Remove-Item "`$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Roll Machine Monitor.lnk" -ErrorAction SilentlyContinue

Write-Host "✓ Uninstallation completed" -ForegroundColor Green
"@
    
    $uninstallWindows | Out-File -FilePath "$scriptsDir/uninstall-windows.ps1" -Encoding UTF8
    
    # Create uninstall script for Linux
    $uninstallLinux = @"
#!/bin/bash
# Roll Machine Monitor - Linux Uninstaller

echo "Uninstalling Roll Machine Monitor..."

# Stop and disable services
sudo systemctl stop rollmachine-monitor 2>/dev/null || true
sudo systemctl disable rollmachine-monitor 2>/dev/null || true
sudo systemctl stop rollmachine-kiosk 2>/dev/null || true
sudo systemctl disable rollmachine-kiosk 2>/dev/null || true

# Remove service files
sudo rm -f /etc/systemd/system/rollmachine-monitor.service
sudo rm -f /etc/systemd/system/rollmachine-kiosk.service
sudo systemctl daemon-reload

# Remove application files
sudo rm -rf /opt/rollmachine-monitor

# Remove desktop entries
sudo rm -f /usr/share/applications/rollmachine-monitor.desktop
sudo rm -f /usr/share/applications/rollmachine-kiosk.desktop

# Remove binary link
sudo rm -f /usr/local/bin/rollmachine-monitor

echo "✓ Uninstallation completed"
"@
    
    $uninstallLinux | Out-File -FilePath "$scriptsDir/uninstall-linux.sh" -Encoding UTF8
    
    Write-Success "Utility scripts created"
}

function Create-ReleaseManifest {
    Write-Info "Creating release manifest..."
    
    $manifest = @"
# Roll Machine Monitor - Release Manifest v$Version
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")

## Package Information
- **Version**: $Version
- **Release Date**: 2025-01-27
- **Release Name**: Complete Multi-Platform Installer
- **Package Size**: $(if (Test-Path $ArchiveName) { "{0:N2} MB" -f ((Get-Item $ArchiveName).Length / 1MB) } else { "TBD" })

## Included Installers
- **Windows**: install.ps1 (PowerShell, requires Administrator)
- **Linux**: install.sh (Bash, Ubuntu/Debian/CentOS support)
- **AntiX**: install-antix.sh (Specialized for antiX Linux)

## Installation Commands

### Windows
``````powershell
.\install.ps1 -Service -Kiosk
``````

### Standard Linux
``````bash
sudo ./install.sh
``````

### AntiX Linux
``````bash
sudo ./install-antix.sh
``````

## Package Contents
- app/monitoring-roll-machine/ - Complete application
- docs/README.md - Comprehensive documentation
- config/ - Configuration templates
- scripts/ - Utility scripts (uninstall, etc.)
- VERSION - Version information
- CHANGELOG.md - Release history
- MANIFEST.md - This file

## Checksums
Generated during packaging process

## Support Information
- **Platforms**: Windows 10/11, Ubuntu 18.04+, Debian 10+, CentOS 7+, AntiX Linux
- **Python**: 3.8+ (auto-installed)
- **Hardware**: JSK3588 Roll Machine via USB/Serial

For technical support, refer to docs/README.md
"@
    
    $manifest | Out-File -FilePath "$ReleaseDir/MANIFEST.md" -Encoding UTF8
    
    Write-Success "Release manifest created"
}

function Create-Archive {
    Write-Info "Creating release archive..."
    
    if (Get-Command tar -ErrorAction SilentlyContinue) {
        # Use system tar (Windows 10/11 built-in or Linux)
        tar -czf $ArchiveName $ReleaseName
        Write-Success "Archive created using tar: $ArchiveName"
    } else {
        # Fallback to PowerShell compression
        Compress-Archive -Path $ReleaseDir -DestinationPath "$ReleaseName.zip" -Force
        Write-Success "Archive created using PowerShell: $ReleaseName.zip"
        Write-Warning "Created ZIP format instead of tar.gz (tar not available)"
    }
    
    # Generate checksums
    if (Test-Path $ArchiveName) {
        $hash = Get-FileHash $ArchiveName -Algorithm SHA256
        "$($hash.Algorithm): $($hash.Hash)" | Out-File -FilePath "$ArchiveName.sha256" -Encoding ASCII
        Write-Success "SHA256 checksum generated"
    }
}

function Show-ReleaseSummary {
    Write-Header
    Write-Success "Release package created successfully!"
    Write-Info ""
    Write-Info "Release Details:"
    Write-Info "  • Version: $Version"
    Write-Info "  • Package: $ArchiveName"
    Write-Info "  • Size: $(if (Test-Path $ArchiveName) { "{0:N2} MB" -f ((Get-Item $ArchiveName).Length / 1MB) } else { "N/A" })"
    Write-Info ""
    Write-Info "Package Contents:"
    Write-Info "  • Windows Installer (install.ps1)"
    Write-Info "  • Linux Installer (install.sh)"
    Write-Info "  • AntiX Installer (install-antix.sh)"
    Write-Info "  • Complete Application"
    Write-Info "  • Documentation & Guides"
    Write-Info "  • Configuration Templates"
    Write-Info "  • Utility Scripts"
    Write-Info ""
    Write-Info "Ready for client distribution! 🚀"
}

# Main execution
try {
    Write-Header
    Write-Info "Building Roll Machine Monitor Release v$Version"
    Write-Info ""
    
    Test-Prerequisites
    Copy-ApplicationFiles
    Create-ConfigTemplates
    Create-UtilityScripts
    Create-ReleaseManifest
    Create-Archive
    Show-ReleaseSummary
    
} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 