# Roll Machine Monitoring Application

A modern Qt-based application for monitoring fabric roll machines. This application provides real-time monitoring of machine status, product information management, and data export capabilities.

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
   monitoring-roll-machine
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
pytest
```

### Building Executable
```bash
# Windows
pyinstaller monitoring-roll-machine/build_exe.py

# Linux
pyinstaller --onefile monitoring-roll-machine/build_exe.py
```

## Configuration

The application uses a YAML configuration file located at:
- Windows: `%APPDATA%/monitoring-roll-machine/config.yaml`
- Linux: `~/.config/monitoring-roll-machine/config.yaml`

## Logging

Log files are stored in:
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