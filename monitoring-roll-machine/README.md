# Roll Machine Monitoring Application

A modern Qt-based application for monitoring fabric roll machines. This application provides real-time monitoring of machine status, product information management, and data export capabilities.

## Project Structure

```
monitoring-roll-machine/
├── build-scripts/         # Build scripts and installer files
│   ├── installer-windows.iss
│   ├── build-windows-complete.bat
│   ├── create-offline-windows-bundle.py
│   └── ...
│
├── docs/                  # Documentation files
│   ├── RELEASE_NOTES_v1.2.6.md
│   ├── JSK3588.md
│   ├── SERIAL_TOOL_GUIDE.md
│   └── ...
│
├── scripts/               # Utility scripts (batch, shell)
│   ├── start_app.bat
│   ├── start_kiosk.sh
│   ├── exit_kiosk.sh
│   └── ...
│
├── tools/                 # Python utility tools
│   ├── serial_tool.py
│   ├── checksum_calculator.py
│   └── ...
│
├── tests-integration/     # Integration and UI tests
│   ├── test_ui.py
│   ├── test_kiosk.py
│   ├── test_ports.py
│   └── ...
│
├── tests/                 # Unit tests
│
├── monitoring/            # Main application code
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── monitor.py
│   └── ...
│
├── windows/               # Windows-specific files
├── releases/              # Release packages
├── logs/                  # Log files
├── exports/               # Exported data
├── requirements.txt       # Python dependencies
├── setup.py               # Package setup
├── pyproject.toml         # Project configuration
└── run_app.py             # Application entry point
```

## Features

- Modern dark theme UI optimized for 24/7 operation
- Real-time monitoring of machine speed and length
- Product information management
- Serial communication with JSK3588 machines
- Data export capabilities
- Touch-screen friendly interface
- Automatic connection recovery
- Cross-platform support (Windows/Linux)

## Requirements

- Python 3.9 or higher
- PySide6 (Qt for Python)
- PyQtGraph for real-time plotting
- PySerial for machine communication
- Other dependencies as listed in setup.py

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/monitoring-roll-machine.git
   cd monitoring-roll-machine
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

1. Start the application:
   ```bash
   python run_app.py
   ```
   
   Or use the provided scripts:
   ```bash
   # Windows
   scripts\start_app.bat
   
   # Linux/AntiX (Kiosk mode)
   ./scripts/start_kiosk.sh
   ```

2. Configure serial connection:
   - Click the "Settings" button
   - Select the appropriate COM port
   - Set the baudrate (default: 19200)
   - Click "Save Settings"

3. Enter product information:
   - Fill in the product code
   - Enter batch number
   - Set target length
   - Click "Save Product Info"

4. Start monitoring:
   - Click "Start Monitoring"
   - The application will display real-time data
   - Graphs will update automatically

## Development

### Running Tests
```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests-integration/
```

### Building Executable
```bash
# Windows
python build-scripts/build_exe.py

# Full Windows installer
build-scripts\build-windows-complete.bat
```

## Configuration

The application uses a JSON configuration file located at:
- Default: `monitoring/config.json`
- Windows: `%APPDATA%/monitoring-roll-machine/config.json`
- Linux: `~/.config/monitoring-roll-machine/config.json`

## Logging

Log files are stored in:
- Default: `logs/`
- Windows: `%APPDATA%/monitoring-roll-machine/logs/`
- Linux: `~/.local/share/monitoring-roll-machine/logs/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request