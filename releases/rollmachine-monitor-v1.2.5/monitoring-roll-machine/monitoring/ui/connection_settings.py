"""
Connection settings panel for serial port configuration.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QGroupBox
)
from PySide6.QtCore import Qt
import serial.tools.list_ports
import logging
from typing import Optional
from ..serial_handler import auto_detect_serial_ports

logger = logging.getLogger(__name__)

class ConnectionSettings(QGroupBox):
    """Panel for serial connection settings."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Connection Settings", parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the connection settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Port selection
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setMinimumHeight(40)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMinimumHeight(40)
        port_layout.addWidget(self.port_combo, stretch=2)
        port_layout.addWidget(self.refresh_btn, stretch=1)
        layout.addLayout(port_layout)
        
        # Connection info
        self.conn_info = QLabel("Baudrate: 19200, Data: 8bit, Parity: None, Stop: 1bit")
        self.last_connected = QLabel("Last Connected: Never")
        layout.addWidget(self.conn_info)
        layout.addWidget(self.last_connected)
        
        # Connect signals
        self.refresh_btn.clicked.connect(self.refresh_ports)
        
        # Initial port refresh
        self.refresh_ports()
        
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        try:
            self.port_combo.clear()
            
            # Add AUTO option first (default)
            self.port_combo.addItem("AUTO (Auto-detect)")
            
            # Get available ports using our auto-detection
            ports = auto_detect_serial_ports()
            for port in ports:
                self.port_combo.addItem(port)
            
            if not ports:
                self.port_combo.addItem("No additional ports found")
                
        except Exception as e:
            logger.error(f"Error refreshing ports: {e}")
            self.port_combo.addItem("Error getting ports")
            
    def get_selected_port(self) -> str:
        """Get the currently selected port."""
        port = self.port_combo.currentText()
        
        # Handle AUTO option
        if port.startswith("AUTO"):
            return "AUTO"
        
        # Handle error cases
        if port in ["No additional ports found", "Error getting ports"]:
            return "AUTO"  # Fallback to AUTO
        
        return port 