# Setup build environment for Monitoring Roll Machine v1.3.5
# This script installs required tools and dependencies

param(
    [switch]$Force,
    [switch]$SkipNSIS
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    
    if ($Level -eq "ERROR") {
        Write-Host $logMessage -ForegroundColor Red
    } elseif ($Level -eq "WARNING") {
        Write-Host $logMessage -ForegroundColor Yellow
    } elseif ($Level -eq "SUCCESS") {
        Write-Host $logMessage -ForegroundColor Green
    }
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-NSIS {
    Write-Log "Installing NSIS..."
    
    # Check if NSIS is already installed
    try {
        $null = Get-Command makensis -ErrorAction Stop
        Write-Log "NSIS is already installed" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "NSIS not found, installing..."
    }
    
    # Download NSIS
    $nsisUrl = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.09/nsis-3.09-setup.exe/download"
    $nsisInstaller = "$env:TEMP\nsis-3.09-setup.exe"
    
    try {
        Write-Log "Downloading NSIS installer..."
        Invoke-WebRequest -Uri $nsisUrl -OutFile $nsisInstaller -UseBasicParsing
        Write-Log "NSIS installer downloaded successfully"
        
        # Install NSIS silently
        Write-Log "Installing NSIS (this may take a few minutes)..."
        $installArgs = @(
            "/S"  # Silent install
            "/D=C:\Program Files (x86)\NSIS"  # Install directory
        )
        
        $process = Start-Process -FilePath $nsisInstaller -ArgumentList $installArgs -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Log "NSIS installed successfully" "SUCCESS"
            
            # Add NSIS to PATH
            $nsisPath = "C:\Program Files (x86)\NSIS"
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
            if ($currentPath -notlike "*$nsisPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$nsisPath", "Machine")
                Write-Log "Added NSIS to system PATH"
            }
            
            # Refresh current session PATH
            $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine")
            
            # Verify installation
            try {
                $null = Get-Command makensis -ErrorAction Stop
                Write-Log "NSIS verification successful" "SUCCESS"
                return $true
            }
            catch {
                Write-Log "NSIS installation verification failed" "ERROR"
                return $false
            }
        }
        else {
            Write-Log "NSIS installation failed with exit code $($process.ExitCode)" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error installing NSIS: $($_.Exception.Message)" "ERROR"
        return $false
    }
    finally {
        # Clean up installer
        if (Test-Path $nsisInstaller) {
            Remove-Item $nsisInstaller -Force
        }
    }
}

function Install-PythonPackages {
    Write-Log "Installing Python packages..."
    
    $packages = @(
        "PyInstaller>=5.0.0",
        "PySide6>=6.6.0",
        "pyqtgraph>=0.13.3",
        "pyserial>=3.5",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "appdirs>=1.4.4",
        "qrcode>=7.4.2",
        "Pillow>=10.0.0",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "requests>=2.28.0"
    )
    
    foreach ($package in $packages) {
        try {
            Write-Log "Installing $package..."
            pip install $package --quiet
            Write-Log "Installed $package successfully" "SUCCESS"
        }
        catch {
            Write-Log "Failed to install $package: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }
    
    return $true
}

function Test-BuildEnvironment {
    Write-Log "Testing build environment..."
    
    # Test Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python: $pythonVersion" "SUCCESS"
    }
    catch {
        Write-Log "Python not found" "ERROR"
        return $false
    }
    
    # Test PyInstaller
    try {
        $pyinstallerVersion = python -c "import PyInstaller; print(PyInstaller.__version__)" 2>&1
        Write-Log "PyInstaller: $pyinstallerVersion" "SUCCESS"
    }
    catch {
        Write-Log "PyInstaller not found" "ERROR"
        return $false
    }
    
    # Test NSIS
    if (-not $SkipNSIS) {
        try {
            $nsisVersion = makensis /VERSION 2>&1
            Write-Log "NSIS: $nsisVersion" "SUCCESS"
        }
        catch {
            Write-Log "NSIS not found" "ERROR"
            return $false
        }
    }
    
    return $true
}

# Main execution
Write-Log "Setting up build environment for Monitoring Roll Machine v1.3.5"
Write-Log "=" * 60

# Check if running as administrator
if (-not (Test-Administrator)) {
    Write-Log "This script requires administrator privileges to install NSIS" "ERROR"
    Write-Log "Please run PowerShell as Administrator and try again" "ERROR"
    exit 1
}

try {
    # Install Python packages
    if (-not (Install-PythonPackages)) {
        Write-Log "Failed to install Python packages" "ERROR"
        exit 1
    }
    
    # Install NSIS if not skipped
    if (-not $SkipNSIS) {
        if (-not (Install-NSIS)) {
            Write-Log "Failed to install NSIS" "ERROR"
            exit 1
        }
    }
    
    # Test build environment
    if (Test-BuildEnvironment) {
        Write-Log "Build environment setup completed successfully!" "SUCCESS"
        Write-Log "You can now run the build scripts to create the installer" "SUCCESS"
    }
    else {
        Write-Log "Build environment test failed" "ERROR"
        exit 1
    }
}
catch {
    Write-Log "Setup failed: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log "=" * 60
Write-Log "Setup completed!"
Write-Log "Next steps:"
Write-Log "1. Run: .\build_all_v1.3.5.bat"
Write-Log "2. Or run: python build_complete_v1.3.5.py"
Write-Log "3. The installer will be created in the releases directory"

