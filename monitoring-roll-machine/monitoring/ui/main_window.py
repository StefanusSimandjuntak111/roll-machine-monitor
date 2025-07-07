"""
Main window for the monitoring application using Qt.
"""
import sys
import logging
import subprocess
import time
import os
import platform
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
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

class SingletonLock:
    """Cross-platform singleton lock to prevent multiple instances."""
    
    def __init__(self, lock_file: Optional[str] = None):
        if lock_file is None:
            # Use temp directory for cross-platform compatibility
            temp_dir = tempfile.gettempdir()
            self.lock_file = os.path.join(temp_dir, "rollmachine_monitor.lock")
            self.popup_shown_file = os.path.join(temp_dir, "rollmachine_popup_shown.flag")
        else:
            self.lock_file = lock_file
            self.popup_shown_file = lock_file.replace('.lock', '_popup_shown.flag')
        
        self.lock_handle = None
        
    def acquire(self):
        """Acquire exclusive lock using cross-platform method."""
        try:
            # Create lock file with PID
            pid = os.getpid()
            timestamp = datetime.now().isoformat()
            
            # Check if another instance is running
            if os.path.exists(self.lock_file):
                try:
                    with open(self.lock_file, 'r') as f:
                        existing_pid = f.readline().strip()
                        existing_timestamp = f.readline().strip()
                    
                    # Check if PID is still running
                    if self._is_pid_running(existing_pid):
                        logger.warning(f"Another instance (PID {existing_pid}) is already running")
                        return False
                    else:
                        # PID not running, remove stale lock
                        logger.info(f"Removing stale lock file from PID {existing_pid}")
                        os.remove(self.lock_file)
                except Exception as e:
                    logger.warning(f"Error reading existing lock: {e}")
                    # Remove corrupted lock file
                    if os.path.exists(self.lock_file):
                        os.remove(self.lock_file)
            
            # Create new lock file
            with open(self.lock_file, 'w') as f:
                f.write(f"{pid}\n{timestamp}\n")
            
            self.lock_handle = open(self.lock_file, 'r')
            
            # Clear the popup shown flag since we're the new primary instance
            if os.path.exists(self.popup_shown_file):
                os.remove(self.popup_shown_file)
            
            logger.info(f"Singleton lock acquired: {self.lock_file}")
            return True
            
        except (IOError, OSError) as e:
            logger.warning(f"Cannot acquire singleton lock: {e}")
            if self.lock_handle:
                self.lock_handle.close()
                self.lock_handle = None
            return False
    
    def _is_pid_running(self, pid_str: str) -> bool:
        """Check if a process ID is still running (cross-platform)."""
        try:
            pid = int(pid_str)
            if platform.system() == "Windows":
                # Windows: use tasklist
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True, shell=True)
                return str(pid) in result.stdout
            else:
                # Unix-like: use kill -0
                os.kill(pid, 0)
                return True
        except (ValueError, OSError, subprocess.SubprocessError):
            return False
    
    def should_show_popup(self):
        """Check if popup should be shown (only once per session)."""
        if os.path.exists(self.popup_shown_file):
            # Check if flag file is recent (less than 30 seconds old)
            try:
                flag_age = time.time() - os.path.getmtime(self.popup_shown_file)
                if flag_age < 30:  # Only suppress for 30 seconds
                    return False
                else:
                    # Flag is old, remove it and allow new popup
                    os.remove(self.popup_shown_file)
                    return True
            except:
                return True
        return True
    
    def mark_popup_shown(self):
        """Mark that popup has been shown."""
        try:
            with open(self.popup_shown_file, 'w') as f:
                f.write(f"{os.getpid()}\n{datetime.now().isoformat()}\n")
        except Exception as e:
            logger.warning(f"Could not create popup flag file: {e}")
    
    def release(self):
        """Release lock."""
        if self.lock_handle:
            try:
                self.lock_handle.close()
                if os.path.exists(self.lock_file):
                    os.remove(self.lock_file)
                # Also remove popup flag when releasing
                if os.path.exists(self.popup_shown_file):
                    os.remove(self.popup_shown_file)
                logger.info("Singleton lock released")
            except Exception as e:
                logger.warning(f"Error releasing lock: {e}")
            finally:
                self.lock_handle = None

class HeartbeatManager:
    """Manages application heartbeat and idle detection."""
    
    def __init__(self, heartbeat_file: Optional[str] = None):
        if heartbeat_file is None:
            # Use temp directory for cross-platform compatibility
            temp_dir = tempfile.gettempdir()
            self.heartbeat_file = os.path.join(temp_dir, "rollmachine_heartbeat")
        else:
            self.heartbeat_file = heartbeat_file
            
        self.last_activity = datetime.now()
        self.data_count = 0
        self.last_data_count = 0
        
        # Start heartbeat timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_heartbeat)
        self.timer.start(10000)  # Update every 10 seconds
    
    def record_activity(self):
        """Record user or data activity."""
        self.last_activity = datetime.now()
    
    def record_data(self):
        """Record data reception."""
        self.data_count += 1
        self.last_activity = datetime.now()
    
    def update_heartbeat(self):
        """Update heartbeat file with current status."""
        try:
            status = {
                'pid': os.getpid(),
                'timestamp': datetime.now().isoformat(),
                'last_activity': self.last_activity.isoformat(),
                'data_count': self.data_count,
                'idle_seconds': (datetime.now() - self.last_activity).total_seconds(),
                'is_processing_data': self.data_count > self.last_data_count
            }
            
            with open(self.heartbeat_file, 'w') as f:
                import json
                json.dump(status, f)
            
            self.last_data_count = self.data_count
            
        except Exception as e:
            logger.warning(f"Failed to update heartbeat: {e}")
    
    def cleanup(self):
        """Clean up heartbeat file."""
        try:
            if os.path.exists(self.heartbeat_file):
                os.remove(self.heartbeat_file)
        except Exception as e:
            logger.warning(f"Failed to cleanup heartbeat: {e}")

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
        
        # SINGLETON PROTECTION - Prevent multiple instances
        self.singleton_lock = SingletonLock()
        if not self.singleton_lock.acquire():
            logger.error("Another instance is already running. Exiting.")
            
            # Only show popup if not shown recently (prevent spam)
            if self.singleton_lock.should_show_popup():
                self.singleton_lock.mark_popup_shown()
                QMessageBox.critical(None, "Already Running", 
                                   "Roll Machine Monitor is already running.\n"
                                   "Only one instance is allowed at a time.")
            else:
                logger.info("Popup suppressed - already shown recently")
            
            sys.exit(1)
        
        # HEARTBEAT MANAGER - For idle detection and crash recovery
        self.heartbeat = HeartbeatManager()
        
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
        
        # DISABLED AUTO-RESTART MECHANISM - CAUSES MULTIPLE INSTANCES
        # self.restart_timer = QTimer(self)
        # self.restart_timer.timeout.connect(self.auto_restart)
        self.is_kiosk_mode = True  # Always in kiosk mode
        
        # DISABLED HEALTH CHECK - CAN CAUSE PERFORMANCE ISSUES
        # self.health_timer = QTimer(self)
        # self.health_timer.timeout.connect(self.health_check)
        # self.health_timer.start(5000)  # Check every 5 seconds
        
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
        self.product_form.start_monitoring.connect(self.toggle_monitoring)
        logger.info("FIXED: Connected start_monitoring signal to toggle_monitoring")
    
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
        """Toggle monitoring start/stop with FORCED real serial connection."""
        if not self.monitor or not self.monitor.is_running:
            try:
                # FORCE: Always use real port, disable auto fallback to mock
                port = self.config.get("serial_port", "/dev/ttyUSB0")
                baudrate = self.config.get("baudrate", 19200)
                use_mock = False  # FORCE: Never use mock mode
                
                # FORCE: If config says AUTO, use detected port
                if port == "AUTO" or port == "":
                    detected_port = self.auto_detect_port()
                    if detected_port:
                        port = detected_port
                        logger.info(f"Auto-detected serial port: {port}")
                    else:
                        # FORCE: Use /dev/ttyUSB0 as fallback instead of mock
                        port = "/dev/ttyUSB0"
                        logger.warning(f"No port detected, forcing: {port}")
                
                # FORCE: Always try real connection, never mock
                logger.info(f"FORCED real serial connection to: {port}")
                
                # Try real serial connection
                serial_port = JSKSerialPort(port=port, baudrate=baudrate, simulation_mode=False)
                serial_port.open()
                serial_port.enable_auto_recover()
                
                self.monitor = Monitor(
                    serial_port=serial_port,
                    on_data=self.handle_data,
                    on_error=self.handle_error,
                    on_serial_data=self.handle_serial_data,
                    auto_send_enabled=True,
                    auto_send_command="55 AA 02 00 00",
                    auto_send_interval=100
                )
                
                self.monitor.start()
                self.connection_status.setText(f"✅ REAL Connection ({port})")
                self.connection_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                logger.info(f"REAL serial monitoring started on {port}")
                
            except Exception as e:
                logger.error(f"Error starting REAL monitoring: {e}")
                # FORCE: Show error but do NOT fallback to mock mode
                self.connection_status.setText(f"❌ Connection Failed")
                self.connection_status.setStyleSheet("color: #F44336; font-weight: bold;")
                
                self.show_kiosk_dialog(
                    "critical",
                    "❌ Real Connection Failed",
                    f"Failed to connect to real device:\n\n{str(e)}\n\n"
                    f"Attempted port: {port}\n\n"
                    "Check:\n"
                    "• Device connection\n"
                    "• User permissions (dialout group)\n"
                    "• Port accessibility\n\n"
                    "DEMO MODE DISABLED - Fix connection to continue."
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
        # Record data activity for heartbeat
        self.heartbeat.record_data()
        
        self.monitoring_view.update_data(data)
        
        # Update target length input with current length
        if hasattr(self, 'product_form') and self.product_form:
            current_length = data.get('length_meters', 0.0)
            self.product_form.update_target_with_current_length(current_length)
    
    def handle_error(self, error: Exception):
        """Handle error from monitor."""
        logger.error(f"Monitor error: {error}")
        self.show_kiosk_dialog(
            "warning",
            "Monitor Error",
            str(error)
        )
    
    def handle_serial_data(self, data: str):
        """Handle real-time serial data for display."""
        # Add to monitoring view serial display
        if hasattr(self, 'monitoring_view') and self.monitoring_view:
            self.monitoring_view.add_serial_data(data)
            
            # If this is RX data, add packet analysis
            if "RX:" in data:
                # Extract hex data from RX line
                try:
                    hex_part = data.split("RX: ")[1].strip()
                    self.monitoring_view.add_packet_analysis(hex_part)
                except:
                    pass  # Ignore if parsing fails
        
        # Record data activity for heartbeat
        self.heartbeat.record_data()
    
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
    
    def keyPressEvent(self, event):
        """Override key press events to disable certain shortcuts in kiosk mode."""
        # Record user activity
        self.heartbeat.record_activity()
        
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
    
    def mousePressEvent(self, event):
        """Record user activity on mouse clicks."""
        # Record user activity
        self.heartbeat.record_activity()
        super().mousePressEvent(event)
    
    def closeEvent(self, event: QCloseEvent):
        """Handle application close - allow clean shutdown to prevent multiple instances."""
        logger.info("Application close requested")
        
        # Always allow clean shutdown to prevent multiple instances
        # Stop monitoring gracefully
        if hasattr(self, 'monitor') and self.monitor:
            try:
                self.monitor.stop()
                logger.info("Monitor stopped gracefully")
            except Exception as e:
                logger.warning(f"Error stopping monitor: {e}")
        
        # Save configuration
        try:
            save_config(self.config)
            logger.info("Configuration saved")
        except Exception as e:
            logger.warning(f"Error saving config: {e}")
        
        # Cleanup singleton lock and heartbeat
        try:
            if hasattr(self, 'heartbeat'):
                self.heartbeat.cleanup()
            if hasattr(self, 'singleton_lock'):
                self.singleton_lock.release()
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        
        # Accept close event to prevent multiple instances
            event.accept()
        logger.info("Application closed cleanly")

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
    logger.info("- Clean shutdown to prevent multiple instances")
    logger.info("- Disabled close shortcuts (Alt+F4, Ctrl+Q, etc.)")
    logger.info("- Safe session management")
    logger.info("=" * 50)
    
    # To exit kiosk mode: Create file in temp directory
    exit_flag_path = os.path.join(tempfile.gettempdir(), "exit_kiosk_mode")
    # Check for exit flag every 10 seconds
    exit_timer = QTimer()
    def check_exit_flag():
        if os.path.exists(exit_flag_path):
            logger.info("Exit flag detected - disabling kiosk mode")
            window.is_kiosk_mode = False
            os.remove(exit_flag_path)
            app.quit()
    
    exit_timer.timeout.connect(check_exit_flag)
    exit_timer.start(10000)  # Check every 10 seconds
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 