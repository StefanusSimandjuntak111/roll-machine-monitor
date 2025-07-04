from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QFrame, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    # Signal emitted when settings are saved
    settings_updated = Signal(dict)
    
    def __init__(self, current_settings: Dict[str, Any]):
        super().__init__()
        self.current_settings = current_settings
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the settings dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Create settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #888888;
                font-size: 12px;
            }
            QComboBox {
                background-color: #353535;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        
        settings_layout = QFormLayout(settings_frame)
        settings_layout.setSpacing(15)
        
        # Title
        title = QLabel("Serial Connection Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        settings_layout.addRow(title)
        
        # Port selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        settings_layout.addRow("Serial Port:", self.port_combo)
        
        # Baudrate selection
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems([
            "9600", "19200", "38400", "57600", "115200"
        ])
        self.baudrate_combo.setCurrentText(
            str(self.current_settings.get("baudrate", 19200))
        )
        settings_layout.addRow("Baudrate:", self.baudrate_combo)
        
        layout.addWidget(settings_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #d83b01;
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ea4a1f;
            }
            QPushButton:pressed {
                background-color: #ca3801;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        try:
            self.port_combo.clear()
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.port_combo.addItem(port.device)
                
            # Set current port if available
            current_port = self.current_settings.get("serial_port")
            if current_port:
                index = self.port_combo.findText(current_port)
                if index >= 0:
                    self.port_combo.setCurrentIndex(index)
                    
        except Exception as e:
            logger.error(f"Error refreshing ports: {e}")
    
    def save_settings(self):
        """Save the current settings."""
        settings = {
            "serial_port": self.port_combo.currentText(),
            "baudrate": int(self.baudrate_combo.currentText())
        }
        
        self.settings_updated.emit(settings)
        self.accept() 