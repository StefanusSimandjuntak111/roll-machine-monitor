# Roll Machine Monitor

A comprehensive monitoring system for roll machine production with real-time data tracking, cycle time calculation, and production logging.

## 🎯 Features

### ✅ **Core Monitoring**
- Real-time length counter monitoring
- Speed and shift tracking
- Serial communication with JSK3588 protocol
- Auto-detection of serial ports
- Mock data simulation for testing

### ✅ **Cycle Time Logic** (NEW)
- **Automatic length counter detection** when reaching 1.0m
- **Precise cycle time calculation** based on product start times
- **Print button**: Saves product data with cycle_time = null initially
- **Reset Counter**: Resets length counter and prepares for new product
- **Close Cycle**: Calculates final cycle time for last product
- **Automatic updates**: Previous product cycle time updated when next product starts

### ✅ **Production Logging**
- Comprehensive production data logging
- Cycle time and roll time tracking
- Batch and product information management
- Export functionality to CSV
- Real-time logging table display

### ✅ **User Interface**
- Modern industrial design
- Kiosk mode for production environments
- Real-time data visualization
- Product search and management
- Settings configuration

### ✅ **Advanced Features**
- Heartbeat monitoring for system health
- Singleton protection (single instance)
- Auto-recovery for serial connections
- Comprehensive error handling
- Logging and debugging support

### ✅ **Length Tolerance Feature** (NEW)
- **Length Print with tolerance**: Card Length Print menampilkan panjang dengan toleransi persentase
- **Configurable settings**: Length tolerance, decimal format, dan rounding method
- **Real-time preview**: Settings dialog menampilkan preview hasil perhitungan
- **Formula**: `length_display = length_input * (1 - tolerance_percent / 100)`
- **Rounding options**: UP (ceil) atau DOWN (floor) dengan format desimal yang dapat disesuaikan

## 🔧 Cycle Time Logic Implementation

### 📌 **How It Works:**

1. **Product Start Detection**
   - System automatically detects when length counter reaches 1.0m
   - Range tolerance: 0.9m - 1.1m for accuracy
   - Records start time for the new product

2. **Print Button Logic**
   - Saves product data with `cycle_time = null` initially
   - Updates previous product's cycle time if available
   - Formula: `cycle_time_previous = start_time_current - start_time_previous`

3. **Reset Counter Logic**
   - Resets length counter to 0
   - Clears all cycle time tracking variables
   - Prepares system for next product

4. **Close Cycle Logic**
   - Calculates final cycle time for last product
   - Formula: `cycle_time_final = current_time - start_time_last_product`
   - Updates logging table with final cycle time

### 📊 **Example Workflow:**

| Step | Action | Product | Cycle Time | Notes |
|------|--------|---------|------------|-------|
| 1 | Length = 1 | Product 1 | Empty | New product started |
| 2 | Print | Product 1 | Empty | Stored with cycle_time = null |
| 3 | Reset Counter | - | - | Length reset to 0 |
| 4 | Length = 1 | Product 2 | Empty | New product started |
| 5 | Print | Product 2 | Empty | Product 1 cycle time updated |
| 6 | Close Cycle | Product 2 | Calculated | Product 2 cycle time updated |

## 🚀 Installation

### Prerequisites
- Python 3.8+
- PySide6
- pyserial
- matplotlib
- numpy

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd monitoring-roll-machine

# Install dependencies
pip install -r requirements.txt

# Run the application
python run_app.py
```

### Windows Installation
```bash
# Use the provided batch file
start_windows.bat
```

## 🧪 Testing

### Cycle Time Logic Test
```bash
cd tests-integration
python test_cycle_time_logic.py
```

This test verifies:
- Length counter detection at 1.0m
- Print button functionality
- Reset counter functionality
- Close cycle functionality
- Cycle time calculations

## 📁 Project Structure

```
monitoring-roll-machine/
├── monitoring/                 # Core monitoring system
│   ├── ui/                    # User interface components
│   ├── parser.py              # JSK3588 protocol parser
│   ├── serial_handler.py      # Serial communication
│   └── logging_table.py       # Production logging
├── tests-integration/         # Integration tests
├── docs/                      # Documentation
├── build-scripts/             # Build and deployment scripts
└── releases/                  # Release packages
```

## 🔧 Configuration

### Serial Settings
- **Port**: Auto-detection or manual selection
- **Baudrate**: 19200 (default for JSK3588)
- **Protocol**: JSK3588 with checksum validation

### Cycle Time Settings
- **Detection Range**: 0.9m - 1.1m for length counter = 1
- **Reset Detection**: Length <= 0.1m after previous > 0.1m
- **Auto-update**: Previous product cycle time updated automatically

## 📝 Usage

### 1. **Start Monitoring**
- Launch the application
- Ensure serial connection is established
- Monitor will automatically detect length counter changes

### 2. **Product Production**
- Fill in product information
- Wait for length counter to reach 1.0m
- Click **Print** to save product data
- Click **Reset Counter** to prepare for next product

### 3. **Cycle Management**
- System automatically tracks cycle times
- Previous product cycle time updated when new product starts
- Use **Close Cycle** for final product to calculate last cycle time

### 4. **Data Export**
- Production data automatically logged to JSON files
- Export to CSV format available
- Real-time logging table display

## 🐛 Troubleshooting

### Common Issues

1. **Serial Connection Failed**
   - Check device connection
   - Verify port permissions
   - Ensure correct baudrate

2. **Cycle Time Not Calculating**
   - Verify length counter reaches 1.0m
   - Check that Reset Counter is clicked between products
   - Ensure Close Cycle is clicked for final product

3. **Application Won't Start**
   - Check if another instance is running
   - Verify Python dependencies
   - Check log files for errors

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the documentation in the `docs/` folder
- Review the troubleshooting section
- Create an issue in the repository

---

**Version**: 1.3.1  
**Last Updated**: December 2024  
**Status**: Production Ready ✅