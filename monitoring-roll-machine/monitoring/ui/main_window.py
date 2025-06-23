"""
Main window for the monitoring application using Qt.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QSpinBox,
    QLineEdit, QFormLayout, QGroupBox, QScrollArea,
    QSizePolicy, QApplication, QMessageBox, QFrame,
    QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, Slot, Signal
from PySide6.QtGui import QIcon, QFont, QCloseEvent, QPalette, QColor
import pyqtgraph as pg

from ..monitor import Monitor
from ..serial_handler import JSKSerialPort
from ..config import load_config, save_config
from ..logging_utils import setup_logging
from .monitoring_view import MonitoringView
from .product_form import ProductForm
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)

class MachineStatus(QGroupBox):
    """Panel for displaying machine status."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Machine Status", parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the machine status UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Connection status
        self.conn_status = QLabel("Disconnected")
        self.conn_status.setStyleSheet("color: red;")
        layout.addWidget(self.conn_status)
        
        # Create status labels with large fonts
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        
        # Rolled length
        self.rolled_length = QLabel("0.0")
        self.rolled_length.setFont(font)
        self.rolled_length.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.rolled_length)
        
        length_unit = QLabel("meters rolled")
        length_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(length_unit)
        
        # Speed
        self.speed = QLabel("0.0")
        self.speed.setFont(font)
        self.speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.speed)
        
        speed_unit = QLabel("meters/minute")
        speed_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(speed_unit)
        
        # Shift and time info
        info_layout = QHBoxLayout()
        
        # Shift info
        shift_box = QVBoxLayout()
        self.shift = QLabel("1")
        self.shift.setFont(font)
        self.shift.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shift_label = QLabel("Current Shift")
        shift_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shift_box.addWidget(self.shift)
        shift_box.addWidget(shift_label)
        
        # Time info
        time_box = QVBoxLayout()
        self.current_time = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.current_time.setFont(font)
        self.current_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label = QLabel("Time")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_box.addWidget(self.current_time)
        time_box.addWidget(time_label)
        
        info_layout.addLayout(shift_box)
        info_layout.addLayout(time_box)
        layout.addLayout(info_layout)
        
        # Start clock update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
    def update_time(self):
        """Update current time display."""
        self.current_time.setText(datetime.now().strftime("%H:%M:%S"))
        
    def update_connection_status(self, connected: bool):
        """Update connection status display."""
        if connected:
            self.conn_status.setText("Connected")
            self.conn_status.setStyleSheet("color: green;")
        else:
            self.conn_status.setText("Disconnected")
            self.conn_status.setStyleSheet("color: red;")
            
    def update_status(self, length: float, speed: float, shift: int):
        """Update machine status display."""
        self.rolled_length.setText(f"{length:.1f}")
        self.speed.setText(f"{speed:.1f}")
        self.shift.setText(str(shift))

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
        import serial.tools.list_ports
        self.port_combo.clear()
        
        try:
            ports = list(serial.tools.list_ports.comports())
            for port in ports:
                self.port_combo.addItem(port.device)
            
            if not ports:
                self.port_combo.addItem("No ports available")
                
        except Exception as e:
            logger.error(f"Error refreshing ports: {e}")
            self.port_combo.addItem("Error getting ports")
            
    def get_selected_port(self) -> str:
        """Get the currently selected port."""
        return self.port_combo.currentText()

class Statistics(QGroupBox):
    """Panel for statistics and data visualization."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Statistics", parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the statistics UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create graphs
        graphs_layout = QHBoxLayout()
        
        # Length graph
        self.length_plot = pg.PlotWidget(title="Length over Time")
        self.length_plot.setLabel('left', 'Length', units='m')
        self.length_plot.setLabel('bottom', 'Time', units='s')
        self.length_curve = self.length_plot.plot(pen='g')
        
        # Speed graph
        self.speed_plot = pg.PlotWidget(title="Speed over Time")
        self.speed_plot.setLabel('left', 'Speed', units='m/s')
        self.speed_plot.setLabel('bottom', 'Time', units='s')
        self.speed_curve = self.speed_plot.plot(pen='b')
        
        graphs_layout.addWidget(self.length_plot)
        graphs_layout.addWidget(self.speed_plot)
        layout.addLayout(graphs_layout)
        
        # Initialize data
        self.length_data = []
        self.speed_data = []
        self.time_data = []
        self.max_points = 100
        
    def update_plots(self, length: float, speed: float):
        """Update plot data."""
        current_time = len(self.time_data)
        
        self.length_data.append(length)
        self.speed_data.append(speed)
        self.time_data.append(current_time)
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.length_data = self.length_data[-self.max_points:]
            self.speed_data = self.speed_data[-self.max_points:]
            
        self.length_curve.setData(self.time_data, self.length_data)
        self.speed_curve.setData(self.time_data, self.speed_data)

class ModernMainWindow(QMainWindow):
    """Main window for the monitoring application with modern industrial design."""
    
    def __init__(self):
        super().__init__()
        self.monitor: Optional[Monitor] = None
        self.config = load_config()
        
        self.setWindowTitle("Roll Machine Monitor")
        self.setWindowState(Qt.WindowState.WindowFullScreen)  # Start in fullscreen for kiosk mode
        
        # Set up the theme (True for dark, False for light)
        self.setup_theme(is_dark=False)  # Set to light theme
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Create header
        self.setup_header()
        
        # Create content area
        self.setup_content()
        
        # Create status bar
        self.setup_status_bar()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
        
        # Connect signals
        self.product_form.product_updated.connect(self.handle_product_update)
    
    def setup_theme(self, is_dark: bool = True):
        """Set up theme colors and styling."""
        palette = QPalette()
        if is_dark:
            # Dark theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d2d"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#353535"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#353535"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
        else:
            # Light theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#f0f0f0"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#e0e0e0"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
        
        self.setPalette(palette)
        
        # Set application-wide font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
    
        # Update frame styles
        frame_style = f"""
            QFrame {{ 
                background-color: {palette.color(QPalette.ColorRole.Base).name()}; 
                border-radius: 10px; 
            }}
        """
        for widget in self.findChildren(QFrame):
            widget.setStyleSheet(frame_style)
            
        # Update button styles
        button_style = f"""
            QPushButton {{
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
            QPushButton:pressed {{
                background-color: #006cbd;
            }}
        """
        for widget in self.findChildren(QPushButton):
            widget.setStyleSheet(button_style)
    
    def setup_header(self):
        """Set up the header with title and main controls."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 10px; }")
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("Roll Machine Monitor")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        self.main_layout.addWidget(header_frame)
    
    def setup_content(self):
        """Set up the main content area with monitoring view and product form."""
        content_layout = QHBoxLayout()
        
        # Create and add monitoring view
        self.monitoring_view = MonitoringView()
        content_layout.addWidget(self.monitoring_view, stretch=2)
        
        # Create and add product form
        self.product_form = ProductForm()
        content_layout.addWidget(self.product_form, stretch=1)
        
        self.main_layout.addLayout(content_layout, stretch=1)
    
    def setup_status_bar(self):
        """Set up the status bar with connection status and other info."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_frame.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 10px; }")
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setStyleSheet("color: #ff4444;")
        status_layout.addWidget(self.connection_status)
        
        status_layout.addStretch()
        
        self.clock_label = QLabel()
        status_layout.addWidget(self.clock_label)
        
        self.main_layout.addWidget(status_frame)
    
    def update_display(self):
        """Update dynamic display elements."""
        self.clock_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config)
        dialog.settings_updated.connect(self.handle_settings_update)
        dialog.exec()
    
    @Slot(dict)
    def handle_settings_update(self, settings: Dict[str, Any]):
        """Handle settings updates."""
        logger.info(f"Settings updated: {settings}")
        self.config.update(settings)
        save_config(self.config)
        
        # Restart monitoring if active
        if self.monitor and self.monitor.is_running:
            self.toggle_monitoring()  # Stop
            self.toggle_monitoring()  # Start with new settings
    
    @Slot(dict)
    def handle_product_update(self, product_info: Dict[str, Any]):
        """Handle product information updates."""
        logger.info(f"Product info updated: {product_info}")
        if self.monitor:
            self.monitor.update_product_info(product_info)
    
    def toggle_monitoring(self):
        """Toggle monitoring start/stop."""
        if not self.monitor or not self.monitor.is_running:
            try:
                port = self.config.get("serial_port", "COM1")
                baudrate = self.config.get("baudrate", 19200)
                
                serial_port = JSKSerialPort(port=port, baudrate=baudrate)
                serial_port.open()
                serial_port.enable_auto_recover()
                
                self.monitor = Monitor(
                    serial_port=serial_port,
                    on_data=self.handle_data,
                    on_error=self.handle_error
                )
                
                self.monitor.start()
                self.connection_status.setText("Connected")
                self.connection_status.setStyleSheet("color: #4CAF50;")
                
            except Exception as e:
                logger.error(f"Error starting monitoring: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to start monitoring: {str(e)}"
                )
        else:
            try:
                self.monitor.stop()
                self.monitor.serial_port.disable_auto_recover()
                self.connection_status.setText("Not Connected")
                self.connection_status.setStyleSheet("color: #ff4444;")
                
            except Exception as e:
                logger.error(f"Error stopping monitoring: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to stop monitoring: {str(e)}"
                )
    
    def handle_data(self, data: Dict[str, Any]):
        """Handle data from monitor."""
        self.monitoring_view.update_data(data)
    
    def handle_error(self, error: Exception):
        """Handle error from monitor."""
        logger.error(f"Monitor error: {error}")
        QMessageBox.warning(
            self,
            "Monitor Error",
            str(error)
        )
    
    def closeEvent(self, event: QCloseEvent):
        """Handle application close."""
        if self.monitor:
            self.monitor.stop()
        save_config(self.config)
        event.accept()

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = ModernMainWindow()
    window.showMaximized()  # Start maximized
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 