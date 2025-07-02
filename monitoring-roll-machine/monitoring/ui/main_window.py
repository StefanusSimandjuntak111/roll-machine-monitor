"""
Main window for the monitoring application using Qt.
"""
import sys
import logging
import subprocess
import time
import os
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
from .connection_settings import ConnectionSettings

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
        
        # KIOSK MODE CONFIGURATION
        self.setWindowTitle("Roll Machine Monitor - Kiosk Mode")
        
        # Force fullscreen and disable window controls
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Disable close button and ALT+F4
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        # Set up the theme (True for dark, False for light)
        self.setup_theme(is_dark=False)  # Set to light theme
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # AUTO-RESTART MECHANISM
        self.restart_timer = QTimer(self)
        self.restart_timer.timeout.connect(self.auto_restart)
        self.is_kiosk_mode = True  # Always in kiosk mode
        
        # Health check timer to ensure application stays running
        self.health_timer = QTimer(self)
        self.health_timer.timeout.connect(self.health_check)
        self.health_timer.start(5000)  # Check every 5 seconds
        
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
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                color: white;
                font-size: 12px;
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
    
    def show_kiosk_dialog(self, dialog_type: str, title: str, message: str) -> int:
        """Show a dialog that stays on top in kiosk mode."""
        dialog = QMessageBox(self)
        
        # Set dialog type
        if dialog_type == "critical":
            dialog.setIcon(QMessageBox.Icon.Critical)
        elif dialog_type == "warning":
            dialog.setIcon(QMessageBox.Icon.Warning)
        elif dialog_type == "question":
            dialog.setIcon(QMessageBox.Icon.Question)
        else:
            dialog.setIcon(QMessageBox.Icon.Information)
        
        dialog.setWindowTitle(title)
        dialog.setText(message)
        
        # Force dialog to stay on top and be modal
        dialog.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint
        )
        
        # Set standard buttons
        if dialog_type == "question":
            dialog.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            dialog.setDefaultButton(QMessageBox.StandardButton.No)
        else:
            dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Ensure dialog appears in front
        dialog.raise_()
        dialog.activateWindow()
        
        return dialog.exec()
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config)
        
        # Force settings dialog to stay on top too
        dialog.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint
        )
        
        dialog.settings_updated.connect(self.handle_settings_update)
        dialog.raise_()
        dialog.activateWindow()
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
        """Toggle monitoring start/stop with auto-detection and mock mode."""
        if not self.monitor or not self.monitor.is_running:
            try:
                port = self.config.get("serial_port", "AUTO")
                baudrate = self.config.get("baudrate", 19200)
                use_mock = self.config.get("use_mock_data", False)
                
                # Auto-detect serial port
                if port == "AUTO" or port == "":
                    detected_port = self.auto_detect_port()
                    if detected_port:
                        port = detected_port
                        logger.info(f"Auto-detected serial port: {port}")
                    else:
                        if not use_mock:
                            logger.warning("No serial port found - enabling mock mode")
                            self.config["use_mock_data"] = True
                            use_mock = True
                
                # Use mock data if enabled or no port available
                if use_mock or not port or port == "AUTO":
                    logger.info("Starting in MOCK mode (no real serial connection)")
                    self.start_mock_monitoring()
                    return
                
                # Try real serial connection
                serial_port = JSKSerialPort(port=port, baudrate=baudrate)
                serial_port.open()
                serial_port.enable_auto_recover()
                
                self.monitor = Monitor(
                    serial_port=serial_port,
                    on_data=self.handle_data,
                    on_error=self.handle_error
                )
                
                self.monitor.start()
                self.connection_status.setText(f"Connected ({port})")
                self.connection_status.setStyleSheet("color: #4CAF50;")
                logger.info(f"Real serial monitoring started on {port}")
                
            except Exception as e:
                logger.error(f"Error starting monitoring: {e}")
                # Fallback to mock mode in kiosk mode
                if self.is_kiosk_mode:
                    logger.info("Kiosk mode: Falling back to mock data")
                    self.start_mock_monitoring()
                else:
                    self.show_kiosk_dialog(
                        "critical",
                        "Error",
                        f"Failed to start monitoring: {str(e)}\n\nTip: Check serial port configuration or enable mock mode."
                    )
        else:
            try:
                self.monitor.stop()
                self.monitor.serial_port.disable_auto_recover()
                self.connection_status.setText("Not Connected")
                self.connection_status.setStyleSheet("color: #ff4444;")
                
            except Exception as e:
                logger.error(f"Error stopping monitoring: {e}")
                self.show_kiosk_dialog(
                    "critical",
                    "Error",
                    f"Failed to stop monitoring: {str(e)}"
                )
    
    def handle_data(self, data: Dict[str, Any]):
        """Handle data from monitor."""
        self.monitoring_view.update_data(data)
    
    def handle_error(self, error: Exception):
        """Handle error from monitor."""
        logger.error(f"Monitor error: {error}")
        self.show_kiosk_dialog(
            "warning",
            "Monitor Error", 
            str(error)
        )
    
    def auto_detect_port(self):
        """Auto-detect available serial ports."""
        import serial.tools.list_ports
        
        # Common port patterns for JSK3588
        preferred_patterns = ['ttyUSB', 'ttyACM', 'COM']
        
        ports = serial.tools.list_ports.comports()
        
        # First try to find ports with preferred patterns
        for pattern in preferred_patterns:
            for port in ports:
                if pattern in port.device:
                    logger.info(f"Found preferred serial port: {port.device}")
                    return port.device
        
        # If no preferred pattern found, return first available port
        if ports:
            logger.info(f"Found serial port: {ports[0].device}")
            return ports[0].device
        
        logger.warning("No serial ports detected")
        return None
    
    def start_mock_monitoring(self):
        """Start monitoring with mock data for demo/testing."""
        try:
            # Use JSKSerialPort in simulation mode
            mock_port = JSKSerialPort(
                port="MOCK",
                baudrate=19200,
                simulation_mode=True,
                simulate_errors=False
            )
            mock_port.open()
            mock_port.enable_auto_recover()
            
            self.monitor = Monitor(
                serial_port=mock_port,
                on_data=self.handle_data,
                on_error=self.handle_error
            )
            
            self.monitor.start()
            self.connection_status.setText("Mock Mode (Demo Data)")
            self.connection_status.setStyleSheet("color: #FF9800;")  # Orange color
            logger.info("Mock monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start mock monitoring: {e}")
            self.connection_status.setText("Failed to Start")
            self.connection_status.setStyleSheet("color: #F44336;")  # Red color
    
    def health_check(self):
        """Health check to ensure application stays responsive."""
        # Force window to stay on top and fullscreen
        if not self.isFullScreen():
            self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # Ensure window stays on top
        self.raise_()
        self.activateWindow()
    
    def auto_restart(self):
        """Auto-restart the application after a delay."""
        logger.info("Auto-restarting application in kiosk mode...")
        
        # Get current executable path
        current_dir = Path(__file__).parent.parent
        python_exec = sys.executable
        
        # Restart application
        try:
            subprocess.Popen([python_exec, "-m", "monitoring"], 
                           cwd=current_dir.parent,
                           start_new_session=True)
            logger.info("New application instance started")
            QApplication.quit()
        except Exception as e:
            logger.error(f"Failed to restart application: {e}")
            # If restart fails, try to show the window again
            self.show()
            self.setWindowState(Qt.WindowState.WindowFullScreen)
    
    def keyPressEvent(self, event):
        """Override key press events to disable certain shortcuts in kiosk mode."""
        if self.is_kiosk_mode:
            # Disable ALT+F4, CTRL+Q, CTRL+W, ESC, etc.
            if (event.key() == Qt.Key.Key_F4 and event.modifiers() == Qt.KeyboardModifier.AltModifier) or \
               (event.key() == Qt.Key.Key_Q and event.modifiers() == Qt.KeyboardModifier.ControlModifier) or \
               (event.key() == Qt.Key.Key_W and event.modifiers() == Qt.KeyboardModifier.ControlModifier) or \
               (event.key() == Qt.Key.Key_Escape):
                logger.info("Close shortcut disabled in kiosk mode")
                event.ignore()
                return
        
        # Allow other keys
        super().keyPressEvent(event)
    
    def closeEvent(self, event: QCloseEvent):
        """Handle application close - prevent close in kiosk mode or auto-restart."""
        if self.is_kiosk_mode:
            logger.info("Close event blocked in kiosk mode - scheduling auto-restart")
            event.ignore()  # Prevent close
            
            # Hide window temporarily and restart after 3 seconds
            self.hide()
            self.restart_timer.start(3000)  # 3 second delay
        else:
            # Normal close
            if self.monitor:
                self.monitor.stop()
            save_config(self.config)
            event.accept()

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window in kiosk mode
    window = ModernMainWindow()
    
    # Force fullscreen kiosk mode
    window.show()
    window.setWindowState(Qt.WindowState.WindowFullScreen)
    window.raise_()
    window.activateWindow()
    
    # Auto-start monitoring if possible
    try:
        window.toggle_monitoring()
        logger.info("Auto-started monitoring in kiosk mode")
    except Exception as e:
        logger.warning(f"Could not auto-start monitoring: {e}")
    
    # Log kiosk mode info
    logger.info("=" * 50)
    logger.info("ROLL MACHINE MONITOR - KIOSK MODE ACTIVE")
    logger.info("Features:")
    logger.info("- Fullscreen mode (cannot be minimized)")
    logger.info("- Auto-restart on close (3 second delay)")
    logger.info("- Disabled close shortcuts (Alt+F4, Ctrl+Q, etc.)")
    logger.info("- Health monitoring every 5 seconds")
    logger.info("=" * 50)
    
    # To exit kiosk mode: Create file /tmp/exit_kiosk_mode
    # Check for exit flag every 10 seconds
    exit_timer = QTimer()
    def check_exit_flag():
        if os.path.exists("/tmp/exit_kiosk_mode"):
            logger.info("Exit flag detected - disabling kiosk mode")
            window.is_kiosk_mode = False
            os.remove("/tmp/exit_kiosk_mode")
            app.quit()
    
    exit_timer.timeout.connect(check_exit_flag)
    exit_timer.start(10000)  # Check every 10 seconds
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 