#!/usr/bin/env python3
"""
Serial Tool for JSK3588 Protocol Testing
Similar to SerialTool but specifically designed for JSK3588 roll machine
"""
import sys
import os
import time
import threading
from datetime import datetime
from typing import Optional, List

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import serial
    import serial.tools.list_ports
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QTextEdit, QLineEdit, QCheckBox,
        QGroupBox, QGridLayout, QSpinBox, QMessageBox, QTabWidget
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QThread
    from PySide6.QtGui import QFont, QTextCursor
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install: pip install PySide6 pyserial")
    sys.exit(1)

class SerialReader(QThread):
    """Thread untuk membaca data serial secara kontinu."""
    data_received = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = False
        
    def run(self):
        """Run the serial reading loop."""
        self.running = True
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        hex_data = ' '.join([f'{b:02X}' for b in data])
                        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                        self.data_received.emit(f"[{timestamp}] RX: {hex_data}")
                time.sleep(0.01)  # Small delay to prevent high CPU usage
            except Exception as e:
                self.error_occurred.emit(f"Read error: {e}")
                break
                
    def stop(self):
        """Stop the reading thread."""
        self.running = False

class JSK3588SerialTool(QMainWindow):
    """Main window for JSK3588 Serial Tool."""
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.reader_thread = None
        self.auto_send_timer = QTimer()
        self.auto_send_timer.timeout.connect(self.auto_send_data)
        
        self.setup_ui()
        self.refresh_ports()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("JSK3588 Serial Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Connection group
        self.setup_connection_group(layout)
        
        # Tabs for different functions
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Manual send tab
        tabs.addTab(self.setup_manual_tab(), "Manual Send")
        
        # Auto send tab
        tabs.addTab(self.setup_auto_tab(), "Auto Send")
        
        # Protocol commands tab
        tabs.addTab(self.setup_protocol_tab(), "Protocol Commands")
        
        # Data display
        self.setup_data_display(layout)
        
    def setup_connection_group(self, parent_layout):
        """Setup connection controls."""
        group = QGroupBox("Connection Settings")
        layout = QGridLayout(group)
        
        # Port selection
        layout.addWidget(QLabel("Port:"), 0, 0)
        self.port_combo = QComboBox()
        layout.addWidget(self.port_combo, 0, 1)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(refresh_btn, 0, 2)
        
        # Baudrate
        layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baudrate_combo.setCurrentText('19200')  # Default for JSK3588
        layout.addWidget(self.baudrate_combo, 1, 1)
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn, 1, 2)
        
        # Status label
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label, 2, 0, 1, 3)
        
        parent_layout.addWidget(group)
        
    def setup_manual_tab(self):
        """Setup manual send tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Data input
        input_group = QGroupBox("Send Data")
        input_layout = QVBoxLayout(input_group)
        
        # Hex data input
        input_layout.addWidget(QLabel("Hex Data (space separated):"))
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("55 AA 02 00 00 (without checksum)")
        input_layout.addWidget(self.hex_input)
        
        # Buttons layout
        btn_layout = QHBoxLayout()
        
        # Send button
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_manual_data)
        btn_layout.addWidget(send_btn)
        
        # Add checksum button
        checksum_btn = QPushButton("Add Checksum")
        checksum_btn.clicked.connect(self.add_checksum_to_input)
        btn_layout.addWidget(checksum_btn)
        
        # Verify checksum button
        verify_btn = QPushButton("Verify")
        verify_btn.clicked.connect(self.verify_input_checksum)
        btn_layout.addWidget(verify_btn)
        
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_group)
        
        # Quick commands
        quick_group = QGroupBox("Quick Commands")
        quick_layout = QGridLayout(quick_group)
        
        commands = [
            ("Query Status", "55 AA 02 00 00"),
            ("Clear Current", "55 AA 01 00 00"),
            ("Query Data", "55 AA 03 00 00"),
            ("Clear Accumulated", "55 AA 04 00 00"),
        ]
        
        for i, (name, cmd) in enumerate(commands):
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, cmd=cmd: self.hex_input.setText(cmd))
            quick_layout.addWidget(btn, i // 2, i % 2)
            
        layout.addWidget(quick_group)
        layout.addStretch()
        
        return widget
        
    def setup_auto_tab(self):
        """Setup auto send tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Auto send settings
        settings_group = QGroupBox("Auto Send Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Command input
        settings_layout.addWidget(QLabel("Command:"), 0, 0)
        self.auto_command = QLineEdit("55 AA 02 00 00")
        settings_layout.addWidget(self.auto_command, 0, 1)
        
        # Interval
        settings_layout.addWidget(QLabel("Interval (ms):"), 1, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)
        self.interval_spin.setValue(1000)
        settings_layout.addWidget(self.interval_spin, 1, 1)
        
        # Start/Stop button
        self.auto_btn = QPushButton("Start Auto Send")
        self.auto_btn.clicked.connect(self.toggle_auto_send)
        settings_layout.addWidget(self.auto_btn, 2, 0, 1, 2)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        return widget
        
    def setup_protocol_tab(self):
        """Setup protocol commands tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Protocol info
        info_group = QGroupBox("JSK3588 Protocol Info")
        info_layout = QVBoxLayout(info_group)
        
        info_text = """
        <b>JSK3588 Protocol:</b><br>
        • Baudrate: 19200<br>
        • Data bits: 8<br>
        • Stop bits: 1<br>
        • Parity: None<br><br>
        
        <b>Send Format:</b> 55 AA COM D1 D0 Checksum<br>
        <b>Receive Format:</b> 55 AA COM LEN D6 D5 D4 D3 D2 D1 D0 Checksum<br><br>
        
        <b>Common Commands:</b><br>
        • 02: Query Status<br>
        • 01: Clear Current Data<br>
        • 03: Query Data<br>
        • 04: Clear Accumulated Data<br>
        • 10/11: Set Length<br>
        • 12/13: Set Coefficient<br>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        return widget
        
    def setup_data_display(self, parent_layout):
        """Setup data display area."""
        group = QGroupBox("Received Data")
        layout = QVBoxLayout(group)
        
        # Data display
        self.data_display = QTextEdit()
        self.data_display.setFont(QFont("Consolas", 10))
        self.data_display.setMaximumHeight(200)
        layout.addWidget(self.data_display)
        
        # Clear button
        clear_btn = QPushButton("Clear Display")
        clear_btn.clicked.connect(self.data_display.clear)
        layout.addWidget(clear_btn)
        
        parent_layout.addWidget(group)
        
    def refresh_ports(self):
        """Refresh available serial ports."""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
            
        if not ports:
            self.port_combo.addItem("No ports found")
            
    def toggle_connection(self):
        """Connect or disconnect from serial port."""
        if self.serial_port is None or not self.serial_port.is_open:
            self.connect_to_port()
        else:
            self.disconnect_from_port()
            
    def connect_to_port(self):
        """Connect to selected serial port."""
        try:
            port_text = self.port_combo.currentText()
            if "No ports found" in port_text:
                QMessageBox.warning(self, "Error", "No serial ports available")
                return
                
            port_name = port_text.split(' - ')[0]
            baudrate = int(self.baudrate_combo.currentText())
            
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                timeout=1
            )
            
            # Start reading thread
            self.reader_thread = SerialReader(self.serial_port)
            self.reader_thread.data_received.connect(self.on_data_received)
            self.reader_thread.error_occurred.connect(self.on_error)
            self.reader_thread.start()
            
            # Update UI
            self.connect_btn.setText("Disconnect")
            self.status_label.setText(f"Connected to {port_name}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            self.log_message(f"Connected to {port_name} at {baudrate} baud")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {e}")
            
    def disconnect_from_port(self):
        """Disconnect from serial port."""
        try:
            # Stop auto send
            self.auto_send_timer.stop()
            self.auto_btn.setText("Start Auto Send")
            
            # Stop reading thread
            if self.reader_thread:
                self.reader_thread.stop()
                self.reader_thread.wait()
                
            # Close serial port
            if self.serial_port:
                self.serial_port.close()
                self.serial_port = None
                
            # Update UI
            self.connect_btn.setText("Connect")
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
            self.log_message("Disconnected")
            
        except Exception as e:
            QMessageBox.critical(self, "Disconnect Error", f"Error disconnecting: {e}")
            
    def send_manual_data(self):
        """Send manual data."""
        if not self.serial_port or not self.serial_port.is_open:
            QMessageBox.warning(self, "Error", "Not connected to any port")
            return
            
        try:
            hex_data = self.hex_input.text().strip()
            if not hex_data:
                QMessageBox.warning(self, "Error", "Please enter hex data")
                return
                
            # Convert hex string to bytes
            hex_bytes = hex_data.replace(' ', '')
            if len(hex_bytes) % 2 != 0:
                QMessageBox.warning(self, "Error", "Invalid hex data length")
                return
                
            data = bytes.fromhex(hex_bytes)
            self.serial_port.write(data)
            
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.log_message(f"[{timestamp}] TX: {hex_data}")
            
        except Exception as e:
            QMessageBox.critical(self, "Send Error", f"Failed to send data: {e}")
            
    def toggle_auto_send(self):
        """Start or stop auto send."""
        if self.auto_send_timer.isActive():
            self.auto_send_timer.stop()
            self.auto_btn.setText("Start Auto Send")
            self.log_message("Auto send stopped")
        else:
            if not self.serial_port or not self.serial_port.is_open:
                QMessageBox.warning(self, "Error", "Not connected to any port")
                return
                
            interval = self.interval_spin.value()
            self.auto_send_timer.start(interval)
            self.auto_btn.setText("Stop Auto Send")
            self.log_message(f"Auto send started (interval: {interval}ms)")
            
    def auto_send_data(self):
        """Send data automatically."""
        try:
            hex_data = self.auto_command.text().strip()
            if not hex_data:
                return
                
            # Convert hex string to bytes
            hex_bytes = hex_data.replace(' ', '')
            if len(hex_bytes) % 2 != 0:
                return
                
            data = bytes.fromhex(hex_bytes)
            if self.serial_port:
                self.serial_port.write(data)
            
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.log_message(f"[{timestamp}] AUTO TX: {hex_data}")
            
        except Exception as e:
            self.log_message(f"Auto send error: {e}")
            
    def on_data_received(self, data):
        """Handle received data."""
        self.data_display.append(data)
        
        # Auto-scroll to bottom
        cursor = self.data_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.data_display.setTextCursor(cursor)
        
    def on_error(self, error):
        """Handle error from reader thread."""
        self.log_message(f"ERROR: {error}")
        
    def log_message(self, message):
        """Log a message to the display."""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.data_display.append(f"[{timestamp}] {message}")
        
    def calculate_checksum(self, hex_data: str) -> int:
        """Calculate checksum for JSK3588 protocol."""
        hex_clean = hex_data.replace(' ', '').upper()
        
        if len(hex_clean) % 2 != 0:
            raise ValueError("Invalid hex data length")
        
        bytes_data = []
        for i in range(0, len(hex_clean), 2):
            byte_val = int(hex_clean[i:i+2], 16)
            bytes_data.append(byte_val)
        
        checksum = sum(bytes_data) % 256
        return checksum
    
    def add_checksum_to_input(self):
        """Add checksum to current input."""
        try:
            hex_data = self.hex_input.text().strip()
            if not hex_data:
                QMessageBox.warning(self, "Error", "Please enter hex data")
                return
            
            checksum = self.calculate_checksum(hex_data)
            hex_clean = hex_data.replace(' ', '').upper()
            
            # Add checksum
            result = hex_clean + f"{checksum:02X}"
            
            # Format with spaces
            formatted = ' '.join([result[i:i+2] for i in range(0, len(result), 2)])
            self.hex_input.setText(formatted)
            
            self.log_message(f"Added checksum: {checksum:02X}")
            
        except Exception as e:
            QMessageBox.critical(self, "Checksum Error", f"Failed to calculate checksum: {e}")
    
    def verify_input_checksum(self):
        """Verify checksum of current input."""
        try:
            hex_data = self.hex_input.text().strip()
            if not hex_data:
                QMessageBox.warning(self, "Error", "Please enter hex data")
                return
            
            hex_clean = hex_data.replace(' ', '').upper()
            
            if len(hex_clean) < 4:
                QMessageBox.warning(self, "Error", "Data too short for checksum verification")
                return
            
            # Split data and checksum
            data_part = hex_clean[:-2]
            checksum_part = hex_clean[-2:]
            
            # Calculate expected checksum
            expected = self.calculate_checksum(data_part)
            actual = int(checksum_part, 16)
            
            if expected == actual:
                QMessageBox.information(self, "Checksum Valid", 
                                      f"Checksum is correct: {actual:02X}")
                self.log_message(f"Checksum verified: {actual:02X} (correct)")
            else:
                QMessageBox.warning(self, "Checksum Invalid", 
                                  f"Checksum mismatch!\nExpected: {expected:02X}\nActual: {actual:02X}")
                self.log_message(f"Checksum error: expected {expected:02X}, got {actual:02X}")
                
        except Exception as e:
            QMessageBox.critical(self, "Verify Error", f"Failed to verify checksum: {e}")

    def closeEvent(self, event):
        """Handle application close."""
        self.disconnect_from_port()
        event.accept()

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = JSK3588SerialTool()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 