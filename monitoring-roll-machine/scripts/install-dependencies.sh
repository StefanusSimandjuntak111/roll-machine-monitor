#!/bin/bash

# Roll Machine Monitor v1.2.5 - Dependency Installation Script
# This script ensures all dependencies are properly installed

set -e  # Exit on any error

echo "=== Roll Machine Monitor v1.2.5 - Dependency Installation ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
print_status "Detected Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 0 ]]; then
    print_error "Python 3.9 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install system dependencies (if needed)
print_status "Checking system dependencies..."

# For Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    print_status "Detected Debian/Ubuntu system"
    sudo apt-get update
    sudo apt-get install -y python3-dev python3-pip python3-venv
    sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
fi

# For CentOS/RHEL/Fedora
if command -v yum &> /dev/null; then
    print_status "Detected CentOS/RHEL/Fedora system"
    sudo yum install -y python3-devel python3-pip
    sudo yum install -y mesa-libGL
fi

# Install Python dependencies
print_status "Installing Python dependencies..."

# Install core dependencies first
print_status "Installing core dependencies..."
pip install PySide6>=6.6.0
pip install pyqtgraph>=0.13.3
pip install pyserial>=3.5

# Install remaining dependencies
print_status "Installing remaining dependencies..."
pip install python-dotenv>=1.0.0
pip install pyyaml>=6.0.1
pip install appdirs>=1.4.4
pip install qrcode>=7.4.2
pip install Pillow>=10.0.0

# Verify installation
print_status "Verifying installation..."

# Test imports
python -c "
import sys
print('Python version:', sys.version)

try:
    import PySide6
    print('✓ PySide6 installed successfully')
except ImportError as e:
    print('✗ PySide6 import failed:', e)
    sys.exit(1)

try:
    import pyqtgraph
    print('✓ pyqtgraph installed successfully')
except ImportError as e:
    print('✗ pyqtgraph import failed:', e)
    sys.exit(1)

try:
    import serial
    print('✓ pyserial installed successfully')
except ImportError as e:
    print('✗ pyserial import failed:', e)
    sys.exit(1)

try:
    import monitoring
    print('✓ monitoring package import successful')
except ImportError as e:
    print('✗ monitoring package import failed:', e)
    sys.exit(1)

print('✓ All dependencies verified successfully!')
"

if [ $? -eq 0 ]; then
    print_status "Dependency installation completed successfully!"
    print_status "You can now run: python -m monitoring"
else
    print_error "Dependency verification failed!"
    exit 1
fi

# Set proper permissions
print_status "Setting proper permissions..."
chmod -R 755 venv
chmod +x venv/bin/activate

print_status "Installation completed successfully!"
print_status "To activate virtual environment: source venv/bin/activate"
print_status "To run application: python -m monitoring" 