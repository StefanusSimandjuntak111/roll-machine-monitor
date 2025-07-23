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
from .logging_table_widget import LoggingTableWidget

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
        
        # Initialize state variables
        self.cycle_is_closed = False  # Track if current cycle is closed
        self.cycle_start_time = None
        self.roll_start_time = None
        self.last_length = 0.0
        self.current_product_info = {}
        self.product_start_times = []  # List to store product start times
        self.last_product_start_time = None  # Last product start time for cycle time calculation
        self.is_new_product_started = False  # Flag to track if new product started
        
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logging()
        
        # Initialize heartbeat manager
        self.heartbeat = HeartbeatManager()
        
        # Initialize singleton lock
        self.singleton_lock = SingletonLock()
        
        # Try to acquire singleton lock
        if not self.singleton_lock.acquire():
            # Another instance is running
            if self.singleton_lock.should_show_popup():
                QMessageBox.warning(
                    self,
                    "Application Already Running",
                    "Another instance of Roll Machine Monitor is already running.\n\nOnly one instance can run at a time.",
                    QMessageBox.StandardButton.Ok
                )
                self.singleton_lock.mark_popup_shown()
            sys.exit(1)
        
        # Initialize UI components
        self.monitor = None
        self.monitoring_view = None
        self.product_form = None
        self.logging_table_widget = None
        
        # Get screen dimensions for dynamic sizing (must be before setup_header)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Setup UI
        self.setup_theme()
        self.setup_header()
        self.setup_content()
        self.setup_status_bar()
        
        # Connect signals
        self.product_form.close_cycle.connect(self.close_cycle)
        self.product_form.reset_counter.connect(self.reset_counter)
        self.product_form.print_logged.connect(self.handle_print_logging)
        
        # Setup timer for display updates
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(100)  # Update every 100ms
        
        # Setup timer for heartbeat
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.heartbeat.update_heartbeat)
        self.heartbeat_timer.start(30000)  # Update every 30 seconds
        
        # Set window properties
        self.setWindowTitle("Roll Machine Monitor")
        self.setMinimumSize(1200, 800)
        
        # Center window on screen
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Show window
        self.show()
        
        # Record startup activity
        self.heartbeat.record_activity()
        
        logger.info("Main window initialized successfully")
    
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
        
        # Calculate dynamic padding based on screen size
        padding_percentage = 0.015  # 1.5% of screen size
        dynamic_padding = max(10, min(30, int(min(self.screen_width, self.screen_height) * padding_percentage)))
        header_layout.setContentsMargins(dynamic_padding, dynamic_padding, dynamic_padding, dynamic_padding)
        
        # Calculate dynamic font size based on screen size
        font_percentage = 0.025  # 2.5% of screen height
        dynamic_font_size = max(14, min(32, int(self.screen_height * font_percentage)))
        
        title_label = QLabel("Roll Machine Monitor")
        title_font = QFont("Segoe UI", dynamic_font_size, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add settings button with dynamic sizing
        settings_btn = QPushButton("⚙️ Settings")
        button_font_size = max(10, min(20, int(dynamic_font_size * 0.6)))
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                padding: {dynamic_padding//2}px {dynamic_padding}px;
                color: white;
                font-size: {button_font_size}px;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
        """)
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        self.main_layout.addWidget(header_frame)
    
    def setup_content(self):
        """Set up the main content area with monitoring view and product form."""
        content_layout = QHBoxLayout()
        
        # Create and add monitoring view with logging table
        self.logging_table_widget = LoggingTableWidget()
        self.monitoring_view = MonitoringView(logging_table_widget=self.logging_table_widget)
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
        
        # Calculate dynamic padding based on screen size
        padding_percentage = 0.012  # 1.2% of screen size
        dynamic_padding = max(8, min(25, int(min(self.screen_width, self.screen_height) * padding_percentage)))
        status_layout.setContentsMargins(dynamic_padding, dynamic_padding//2, dynamic_padding, dynamic_padding//2)
        
        # Calculate dynamic font size for status text
        status_font_percentage = 0.018  # 1.8% of screen height
        dynamic_status_font_size = max(10, min(24, int(self.screen_height * status_font_percentage)))
        
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setStyleSheet(f"color: #ff4444; font-size: {dynamic_status_font_size}px;")
        status_layout.addWidget(self.connection_status)
        
        status_layout.addStretch()
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"color: white; font-size: {dynamic_status_font_size}px;")
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
    
    def force_kill_com_port(self, port_name: str):
        """Force kill COM port on Windows using command line tools."""
        try:
            import platform
            if platform.system() != "Windows":
                logger.info("Force kill COM port only available on Windows")
                return
            
            logger.info(f"Force killing COM port: {port_name}")
            
            # Extract COM number (e.g., "COM4" -> "4")
            if port_name.upper().startswith("COM"):
                com_number = port_name[3:]
            else:
                logger.warning(f"Invalid COM port name: {port_name}")
                return
            
            # Use mode command to check if port is in use
            check_cmd = f'mode {port_name}'
            try:
                result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=5)
                if "Error" in result.stderr or "Error" in result.stdout:
                    logger.info(f"Port {port_name} is not in use or already available")
                    return
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout checking port {port_name}")
            
            # Try to kill processes using the port
            # Method 1: Use netstat to find processes using the port
            netstat_cmd = f'netstat -ano | findstr {port_name}'
            try:
                result = subprocess.run(netstat_cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if port_name.upper() in line.upper():
                            # Extract PID from the last column
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                try:
                                    # Kill the process
                                    kill_cmd = f'taskkill /PID {pid} /F'
                                    logger.info(f"Killing process {pid} using {port_name}")
                                    subprocess.run(kill_cmd, shell=True, capture_output=True, timeout=5)
                                except Exception as e:
                                    logger.warning(f"Failed to kill process {pid}: {e}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout finding processes using {port_name}")
            
            # Method 2: Use devcon to disable/enable the port (if available)
            try:
                # Try to disable and re-enable the port
                disable_cmd = f'devcon disable "USB\\VID_*&PID_*"'
                enable_cmd = f'devcon enable "USB\\VID_*&PID_*"'
                
                logger.info("Attempting to disable/enable USB devices...")
                subprocess.run(disable_cmd, shell=True, capture_output=True, timeout=5)
                import time
                time.sleep(2)
                subprocess.run(enable_cmd, shell=True, capture_output=True, timeout=5)
                logger.info("USB devices disabled and re-enabled")
            except Exception as e:
                logger.debug(f"Devcon method not available: {e}")
            
            logger.info(f"Force kill completed for {port_name}")
            
        except Exception as e:
            logger.error(f"Error force killing COM port {port_name}: {e}")

    def kill_port_connection(self):
        """Kill/close any existing port connection to avoid permission errors."""
        try:
            logger.info("Killing port connection before restart...")
            
            # Get current port name for force kill
            current_port = self.config.get("serial_port", "")
            
            # Stop monitoring if running
            if self.monitor and self.monitor.is_running:
                logger.info("Stopping monitor...")
                self.monitor.stop()
                
                # Wait a bit for cleanup
                import time
                time.sleep(1)
                
                # Close serial port if exists
                if hasattr(self.monitor, 'serial_port') and self.monitor.serial_port:
                    logger.info("Closing serial port...")
                    try:
                        self.monitor.serial_port.close()
                        logger.info("Serial port closed successfully")
                    except Exception as e:
                        logger.warning(f"Error closing serial port: {e}")
                
                # Clear monitor reference
                self.monitor = None
                logger.info("Port connection killed successfully")
            else:
                logger.info("No active monitor to kill")
            
            # Force kill COM port on Windows if needed
            if current_port and current_port.upper().startswith("COM"):
                self.force_kill_com_port(current_port)
                
        except Exception as e:
            logger.error(f"Error killing port connection: {e}")
    
    def _needs_monitoring_restart(self, settings: Dict[str, Any]) -> bool:
        """Check if settings require monitoring restart."""
        restart_settings = ['serial_port', 'baudrate']
        return any(key in settings for key in restart_settings)
    
    def _update_display_settings(self):
        """Update display settings without restart - only affects current and future data."""
        # Store settings change timestamp
        self.settings_changed_at = datetime.now()
        logger.info(f"Display settings updated at: {self.settings_changed_at}")
        
        # Update Length Print card immediately with new settings for current data
        if hasattr(self, 'last_data'):
            self.handle_data(self.last_data)
        logger.info("Display settings updated without restart - affects current and future data only")

    @Slot(dict)
    def handle_settings_update(self, settings: Dict[str, Any]):
        """Handle settings updates with smart restart logic - only affects current and future data."""
        logger.info(f"Settings updated: {settings}")
        self.config.update(settings)
        save_config(self.config)
        
        # Check if settings require monitoring restart
        needs_restart = self._needs_monitoring_restart(settings)
        
        if needs_restart:
            # Port settings changed - need restart
            logger.info("Port settings changed, restarting monitoring...")
            self.kill_port_connection()
            
            # Store settings change timestamp for port settings
            self.settings_changed_at = datetime.now()
            
            # Restart monitoring with new settings
            try:
                logger.info("Restarting monitoring with new settings...")
                self.toggle_monitoring()  # Start with new settings
                
                # Show success message
                self.show_kiosk_dialog(
                    "information",
                    "Settings Updated",
                    "Port settings have been updated.\n\nMonitoring has been restarted with new configuration.\n\nNew settings will apply to current and future products only."
                )
                
            except Exception as e:
                logger.error(f"Error restarting monitoring: {e}")
                self.show_kiosk_dialog(
                    "warning",
                    "Restart Failed",
                    f"Settings saved but failed to restart monitoring:\n\n{str(e)}\n\nPlease try starting monitoring manually."
                )
        else:
            # Only display settings changed - no restart needed
            logger.info("Display settings updated, no restart needed")
            
            # Update Length Print immediately for current data
            self._update_display_settings()
            
            # Show success message
            self.show_kiosk_dialog(
                "information",
                "Settings Updated",
                "Display settings have been updated successfully!\n\nLength tolerance and formatting are now active.\n\nNew settings apply to current and future products only.\n\nNo connection interruption."
            )
    
    @Slot(dict)
    def handle_product_update(self, product_info: Dict[str, Any]):
        """Handle product information updates."""
        logger.info(f"Product info updated: {product_info}")
        if self.monitor:
            self.monitor.update_product_info(product_info)
    
    @Slot()
    def reset_counter(self):
        """Reset counter by sending command 55 AA 01 00 00 00 to device."""
        try:
            if self.monitor and self.monitor.is_running:
                # Send reset command: 55 AA 01 00 00 00
                reset_command = "55 AA 01 00 00 00"
                logger.info(f"Sending reset counter command: {reset_command}")
                
                # Send command through serial port
                if hasattr(self.monitor, 'serial_port') and self.monitor.serial_port:
                    self.monitor.serial_port.send_hex(reset_command)
                    logger.info("Reset counter command sent successfully")
                    
                    # Reset cycle time variables
                    self.cycle_start_time = None
                    self.roll_start_time = None  # Will be set when new product starts (length = 0.01)
                    self.last_length = 0.0
                    self.current_product_info = {}  # Reset current product info
                    # DON'T reset product_start_times - we need this for cycle time calculation
                    self.is_new_product_started = False  # Reset new product flag
                    # DON'T reset last_product_start_time - we need this for cycle time calculation
                    logger.info("Cycle time variables reset - ready for new product cycle")
                    
                    # Show success message
                    self.show_kiosk_dialog(
                        "information",
                        "Reset Counter",
                        "Reset counter command sent successfully!\n\nDevice will reset current collection data to zero and return current data.\n\nCycle time tracking has been reset.\n\nNext product will start when length counter reaches 0.01."
                    )
                else:
                    logger.error("Serial port not available for reset command")
                    self.show_kiosk_dialog(
                        "warning",
                        "Reset Failed",
                        "Cannot send reset command: Serial port not available."
                    )
            else:
                logger.warning("Monitor not running, cannot send reset command")
                self.show_kiosk_dialog(
                    "warning",
                    "Reset Failed",
                    "Cannot send reset command: Monitor not running.\n\nPlease ensure device is connected and monitoring is active."
                )
        except Exception as e:
            logger.error(f"Error sending reset command: {e}")
            self.show_kiosk_dialog(
                "critical",
                "Reset Error",
                f"Error sending reset command:\n\n{str(e)}"
            )
    
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
        
        # Store last data for immediate settings updates
        self.last_data = data.copy()
        
        # Initialize roll_start_time on first data if not set
        if hasattr(self, 'roll_start_time') and self.roll_start_time is None:
            from datetime import datetime
            self.roll_start_time = datetime.now()
            logger.info(f"Initialized roll_start_time on first data: {self.roll_start_time}")
        
        # Check if cycle is closed and enable close cycle button if new data arrives
        if self.cycle_is_closed:
            # New data arrived, enable close cycle button for new cycle
            if hasattr(self, 'product_form') and self.product_form:
                self.product_form.close_cycle_button.setEnabled(True)
                self.product_form.close_cycle_button.setText("Close Cycle")
                self.product_form.close_cycle_button.setStyleSheet(
                    "QPushButton { background-color: #6c757d; color: #ffffff; border: none; padding: 10px; border-radius: 5px; font-weight: bold; }\n"
                    "QPushButton:hover { background-color: #5a6268; }\n"
                    "QPushButton:pressed { background-color: #495057; }"
                )
                logger.info("Close cycle button enabled - new data received")
            
            # Reset cycle closed flag
            self.cycle_is_closed = False
        
        # Calculate length print with tolerance before updating monitoring view
        fields = data.get('fields', {})
        current_count = fields.get('current_count', 0.0)
        unit = fields.get('unit', 'meter')
        
        # Calculate length print with tolerance
        length_print_text = self.calculate_length_print(current_count, unit)
        
        # Add length print to data for monitoring view
        data['length_print_text'] = length_print_text
        data['length_print_value'] = current_count  # Keep original value for internal use
        
        self.monitoring_view.update_data(data)
        
        # Update target length input with length print value (with tolerance)
        if hasattr(self, 'product_form') and self.product_form:
            unit = data.get('unit', 'meter')
            # Use length print text (with tolerance) instead of raw current length
            self.product_form.update_target_with_length_print(length_print_text)
            self.product_form.update_unit_from_monitoring(unit)
            # Set current machine length for print preview
            self.product_form.set_current_machine_length(current_count)
        
        # Handle production logging
        self.handle_production_logging(data)
    
    def handle_production_logging(self, data: Dict[str, Any]):
        """Handle production logging with proper cycle time tracking according to CYCLE_TIME.md specification."""
        try:
            current_time = datetime.now()
            length = data.get('length_meters', 0.0)
            
            # Initialize timing variables if not set
            if not hasattr(self, 'cycle_start_time'):
                self.cycle_start_time = None
                self.roll_start_time = None
                self.last_length = 0.0
                self.current_product_info = {}
                self.product_start_times = []  # Store start times for each product
                self.is_new_product_started = False  # Track if new product has started
                self.last_product_start_time = None  # Track the last product start time
            
            # Detect when length counter == 0.01 (start of new product cycle)
            # This happens after user clicks Reset Counter and starts rolling new product
            if length >= 0.005 and length <= 0.015 and not self.is_new_product_started:
                # New product cycle started - length counter is at 0.01
                self.cycle_start_time = current_time
                self.roll_start_time = current_time
                self.is_new_product_started = True
                
                # Calculate cycle time for previous product if this is not the first product
                if len(self.product_start_times) > 0:
                    previous_product_start = self.product_start_times[-1]  # Previous product start time
                    current_product_start = current_time  # Current product start time
                    previous_cycle_time = (current_product_start - previous_product_start).total_seconds()
                    
                    # Update the previous product's cycle time in the logging table
                    if hasattr(self, 'logging_table_widget') and self.logging_table_widget:
                        self.logging_table_widget.update_last_entry_cycle_time(previous_cycle_time)
                        logger.info(f"Updated previous product cycle time: {previous_cycle_time:.1f}s")
                        
                        # Force immediate refresh to show the update
                        self.logging_table_widget.manual_refresh()
                        
                        # Show user feedback
                        # self.show_kiosk_dialog(
                        #     "information",
                        #     "Cycle Time Updated",
                        #     f"Previous product cycle time has been updated to {previous_cycle_time:.1f}s\n\nThis happened automatically when the new product started (length = 0.01)."
                        # )
                
                # Store this start time for cycle time calculation (after updating previous product)
                self.last_product_start_time = current_time
                
                logger.info(f"New product cycle started - length counter at {length:.3f}m")
            
            # Detect roll length reset to 0 (cycle end - after Reset Counter)
            elif self.last_length > 0.1 and length <= 0.1:
                # Roll length reset to 0 - cycle ended, prepare for next product
                self.is_new_product_started = False
                logger.info(f"Cycle ended - roll length reset to {length:.2f}m")
            
            # Update last length for next comparison
            self.last_length = length
                    
        except Exception as e:
            logger.error(f"Error in production logging: {e}")
    
    def handle_print_logging(self, print_data: Dict[str, Any]):
        """Handle logging when print button is clicked with correct timing according to CYCLE_TIME.md."""
        try:
            current_time = datetime.now()
            
            # Get product info from print data
            product_name = print_data.get('product_name', 'Unknown')
            product_code = print_data.get('product_code', 'Unknown')
            product_length = print_data.get('product_length', 0.0)
            batch = print_data.get('batch', 'Unknown')
            
            # Store current product info for close cycle
            self.current_product_info = {
                'product_name': product_name,
                'product_code': product_code,
                'product_length': product_length,
                'batch': batch
            }
            
            # Calculate roll time (time from roll start to print)
            roll_time = 0.0
            if hasattr(self, 'roll_start_time') and self.roll_start_time:
                roll_time = (current_time - self.roll_start_time).total_seconds()
            
            # For Print button: cycle_time is always None initially
            # Cycle time will be calculated when next product starts (length = 0.01) or Close Cycle is pressed
            cycle_time = None
            
            # Store start time for this product (when length == 0.01)
            if not hasattr(self, 'product_start_times'):
                self.product_start_times = []
            
            # Use cycle_start_time if available, otherwise use current time
            start_time = self.cycle_start_time if self.cycle_start_time else current_time
            self.product_start_times.append(start_time)
            
            # Log the production data with cycle_time = None initially
            if hasattr(self, 'logging_table_widget') and self.logging_table_widget:
                # Get current settings timestamp
                settings_timestamp = None
                if hasattr(self, 'settings_changed_at'):
                    settings_timestamp = self.settings_changed_at.isoformat()
                
                self.logging_table_widget.add_production_entry(
                    product_name=product_name,
                    product_code=product_code,
                    product_length=product_length,
                    batch=batch,
                    cycle_time=cycle_time,  # Always None for Print
                    roll_time=roll_time,
                    settings_timestamp=settings_timestamp  # When settings were last changed
                )
                # Refresh table after print
                self.logging_table_widget.manual_refresh()
            
            logger.info(f"Print logged: {product_code} - Cycle: Empty (will be calculated later), Roll: {roll_time:.1f}s")
            
            # Reset roll_start_time after print - roll time should stop and restart for next print
            # This ensures each print has its own roll time from the last roll start
            if hasattr(self, 'roll_start_time') and self.roll_start_time:
                self.roll_start_time = None
                logger.info(f"Print logged - roll time: {roll_time:.1f}s, roll_start_time reset to None")
            else:
                logger.info(f"Print logged - roll time: {roll_time:.1f}s, roll_start_time was already None")
                    
        except Exception as e:
            logger.error(f"Error in print logging: {e}")
    
    def handle_cycle_timeout(self):
        """Handle cycle timeout after 5-10 minutes of inactivity (last roll detection)."""
        try:
            current_time = datetime.now()
            
            # Calculate final cycle time and roll time
            cycle_time = None
            roll_time = 0.0
            
            if hasattr(self, 'roll_start_time') and self.roll_start_time:
                roll_time = (current_time - self.roll_start_time).total_seconds()
            
            # Log the final production data for this cycle
            if hasattr(self, 'logging_table_widget') and self.logging_table_widget and hasattr(self, 'current_product_info') and self.current_product_info:
                self.logging_table_widget.add_production_entry(
                    product_name=self.current_product_info.get('product_name', 'Unknown'),
                    product_code=self.current_product_info.get('product_code', 'Unknown'),
                    product_length=self.current_product_info.get('product_length', 0.0),
                    batch=self.current_product_info.get('batch', 'Unknown'),
                    cycle_time=cycle_time,
                    roll_time=roll_time
                )
                # Refresh table after timeout
                self.logging_table_widget.manual_refresh()
            
            logger.info(f"Cycle timeout - Final cycle time: {cycle_time if cycle_time is not None else 'Empty'}, roll time: {roll_time:.1f}s")
            
            # Reset timing for next cycle
            self.cycle_start_time = None
            self.roll_start_time = None
            # DON'T reset product_start_times and last_product_start_time
            self.is_new_product_started = False
            
        except Exception as e:
            logger.error(f"Error in cycle timeout handling: {e}")
    
    def close_cycle(self):
        """Close current cycle and get final cycle time for last product according to CYCLE_TIME.md."""
        try:
            # Check if cycle is already closed
            if self.cycle_is_closed:
                logger.warning("Cycle is already closed, ignoring close cycle request")
                self.show_kiosk_dialog(
                    "warning",
                    "Cycle Already Closed",
                    "Current cycle is already closed.\n\nPlease wait for new data to start a new cycle."
                )
                return
            
            current_time = datetime.now()
            
            # Calculate final cycle time for the last product
            cycle_time = None
            if hasattr(self, 'last_product_start_time') and self.last_product_start_time:
                # Use the last product start time (when length = 0.01) to calculate cycle time
                cycle_time = (current_time - self.last_product_start_time).total_seconds()
                logger.info(f"Close cycle: Last product started at {self.last_product_start_time.strftime('%H:%M:%S')}, current time {current_time.strftime('%H:%M:%S')}")
            elif hasattr(self, 'product_start_times') and len(self.product_start_times) > 0:
                # Fallback: use the last product start time from the list
                last_product_start = self.product_start_times[-1]
                cycle_time = (current_time - last_product_start).total_seconds()
                logger.info(f"Close cycle (fallback): Last product started at {last_product_start.strftime('%H:%M:%S')}, current time {current_time.strftime('%H:%M:%S')}")
            
            # Update the last product's cycle time in the logging table
            if hasattr(self, 'logging_table_widget') and self.logging_table_widget:
                if cycle_time is not None:
                    # Update the last entry's cycle time
                    self.logging_table_widget.update_last_entry_cycle_time(cycle_time)
                    logger.info(f"Cycle closed - Final cycle time: {cycle_time:.1f}s")
                    
                    # Show success message
                    self.show_kiosk_dialog(
                        "information",
                        "Cycle Closed",
                        f"Current cycle has been closed.\n\nFinal cycle time: {cycle_time:.1f}s\n\nAll counters have been reset.\n\nNew cycle will start when new data arrives."
                    )
                else:
                    logger.warning("No cycle time calculated for close cycle")
                    self.show_kiosk_dialog(
                        "warning",
                        "Close Cycle",
                        "No cycle time available.\n\nPlease ensure a product has been printed first."
                    )
            else:
                logger.warning("No logging table widget available for close cycle")
                self.show_kiosk_dialog(
                    "warning",
                    "Close Cycle",
                    "No logging table available.\n\nPlease print a product first before closing the cycle."
                )
            
            # Reset ALL timing and state variables for new cycle
            self.cycle_start_time = None
            self.roll_start_time = None
            self.last_length = 0.0
            self.current_product_info = {}
            self.product_start_times = []  # Reset product start times
            self.last_product_start_time = None  # Reset last product start time
            self.is_new_product_started = False
            self.cycle_is_closed = True  # Set cycle closed flag
            
            # Disable close cycle button
            if hasattr(self, 'product_form') and self.product_form:
                self.product_form.close_cycle_button.setEnabled(False)
                self.product_form.close_cycle_button.setText("Cycle Closed")
                self.product_form.close_cycle_button.setStyleSheet(
                    "QPushButton { background-color: #6c757d; color: #ffffff; border: none; padding: 10px; border-radius: 5px; font-weight: bold; }\n"
                    "QPushButton:disabled { background-color: #495057; color: #adb5bd; }"
                )
                logger.info("Close cycle button disabled")
            
            # Send reset command to device to reset counters
            if self.monitor and self.monitor.is_running:
                try:
                    reset_command = "55 AA 01 00 00 00"
                    logger.info(f"Sending reset counter command after close cycle: {reset_command}")
                    
                    if hasattr(self.monitor, 'serial_port') and self.monitor.serial_port:
                        self.monitor.serial_port.send_hex(reset_command)
                        logger.info("Reset counter command sent successfully after close cycle")
                except Exception as e:
                    logger.error(f"Error sending reset command after close cycle: {e}")
            
        except Exception as e:
            logger.error(f"Error in close cycle: {e}")
            self.show_kiosk_dialog(
                "critical",
                "Close Cycle Error",
                f"Error closing cycle:\n\n{str(e)}"
            )
    
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
            if hasattr(self, 'monitoring_view'):
                self.monitoring_view.cleanup()
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
        
        # Accept close event to prevent multiple instances
        event.accept()
        logger.info("Application closed cleanly")

    def calculate_length_print(self, current_length: float, unit: str) -> str:
        """Calculate length print with tolerance based on settings."""
        try:
            # Get tolerance settings from config
            tolerance_percent = self.config.get("length_tolerance", 0.0)
            decimal_points = self.config.get("decimal_points", 1)
            rounding_method = self.config.get("rounding", "UP")
            
            # If no tolerance is set, return current length as is
            if tolerance_percent <= 0:
                # Format with decimal points
                format_str = f"{{:.{decimal_points}f}}"
                if unit == 'yard':
                    return f"{format_str.format(current_length)} yard"
                else:
                    return f"{format_str.format(current_length)} m"
            
            # Apply CORRECT tolerance formula: P_roll = P_target / (1 - T/100)
            # Import calculate_print_length from config
            from monitoring.config import calculate_print_length
            length_with_tolerance = calculate_print_length(current_length, tolerance_percent, decimal_points, rounding_method)
            
            # Format with decimal points
            format_str = f"{{:.{decimal_points}f}}"
            formatted_length = format_str.format(length_with_tolerance)
            
            # Return with unit
            if unit == 'yard':
                return f"{formatted_length} yard"
            else:
                return f"{formatted_length} m"
                
        except Exception as e:
            logger.error(f"Error calculating length print: {e}")
            # Fallback to current length without tolerance
            if unit == 'yard':
                return f"{current_length:.2f} yard"
            else:
                return f"{current_length:.2f} m"

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
    
    # Auto-start monitoring if possible (PRODUCTION MODE)
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