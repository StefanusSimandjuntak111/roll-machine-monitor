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

# Application version
from ..version import get_version_string
APP_VERSION = get_version_string()
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox,
    QLineEdit, QFormLayout, QGroupBox, QScrollArea,
    QSizePolicy, QApplication, QMessageBox, QFrame,
    QStackedWidget, QDialog, QCheckBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer, Slot, Signal, QPoint
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
from .batch_summary_dialog import BatchSummaryDialog
from .pin_dialog import PinDialog

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

    # Signals
    settings_updated = Signal(dict)  # Emitted when settings are updated

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
        self.is_kiosk_mode = True  # Initialize kiosk mode flag
        self.safe_mode_active = False  # Safe Mode flag - when True, no database operations
        self.current_length_print_value = None  # Store current length_print value (with tolerance) for logging
        self.current_machine_length_raw = None  # Store raw machine length (in machine unit) for logging
        self.current_user_unit = 'meter'  # Store current user selected unit for logging
        self.current_machine_unit = 'meter'  # Store current machine unit for logging

        # Login session tracking
        self.user_logged_in = False  # Track if user is logged in
        self.login_time = None  # Track login timestamp
        self.login_timeout_minutes = 30  # Login session timeout (30 minutes)
        self.temp_api_credentials = None  # Temporary storage for API credentials from login
        
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
        self.batch_summary_dialog = None

        # Initialize logging table with Safe Mode awareness
        from ..logging_table import LoggingTable
        self.logging_table = LoggingTable(safe_mode=self.safe_mode_active)

        # Initialize Safe Mode settings from config
        self.safe_mode_settings = self.config.get("safe_mode_settings", {
            "print": True,
            "save_log": False,
            "save_batch": False,
            "send_erp": False
        })
        logger.info(f"Safe Mode settings loaded: {self.safe_mode_settings}")
        
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
        
        # Safe Mode starts based on config.json status
        safe_mode_enabled = self.config.get("safe_mode_enabled", False)
        if hasattr(self, 'safe_mode_switch'):
            self.safe_mode_switch.setChecked(safe_mode_enabled)
            logger.info(f"Safe Mode initialized from config: {safe_mode_enabled}")

        # Initialize Safe Mode indicator visibility
        if hasattr(self, 'safe_mode_indicator'):
            self.safe_mode_indicator.setVisible(safe_mode_enabled)

        # Initialize Safe Mode status label
        if hasattr(self, 'safe_mode_status_label'):
            if safe_mode_enabled:
                self.safe_mode_status_label.setText("ON")
                self.safe_mode_status_label.setStyleSheet("color: #0078d4; font-size: 14px; font-weight: bold;")
            else:
                self.safe_mode_status_label.setText("OFF")
                self.safe_mode_status_label.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: bold;")
            logger.info(f"Safe Mode status label initialized: {'ON' if safe_mode_enabled else 'OFF'}")

        # Initialize Safe Mode active flag based on config
        self.safe_mode_active = safe_mode_enabled
        logger.info(f"Safe Mode active flag set to: {self.safe_mode_active}")
        
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

        # Setup timer for login session timeout check
        self.login_check_timer = QTimer()
        self.login_check_timer.timeout.connect(self._check_login_session_timeout)
        self.login_check_timer.start(60000)  # Check every minute
        
        # Setup timer for Supabase offline queue sync (every 5 minutes)
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_offline_queue)
        self.sync_timer.start(300000)  # Sync every 5 minutes (300000 ms)
        
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
        
        # Add Safe Mode toggle switch with label
        safe_mode_container = QWidget()
        safe_mode_layout = QHBoxLayout(safe_mode_container)
        safe_mode_layout.setContentsMargins(0, 0, dynamic_padding, 0)
        safe_mode_layout.setSpacing(8)
        
        # Safe Mode label
        safe_mode_label = QLabel("Safe Mode:")
        button_font_size = max(10, min(20, int(dynamic_font_size * 0.6)))
        safe_mode_label.setStyleSheet(f"color: white; font-size: {button_font_size}px;")
        safe_mode_layout.addWidget(safe_mode_label)

        # Safe Mode status label
        self.safe_mode_status_label = QLabel("OFF")
        self.safe_mode_status_label.setStyleSheet(f"color: #ff6b6b; font-size: {button_font_size}px; font-weight: bold;")
        self.safe_mode_status_label.setToolTip("Current Safe Mode status - affects database operations")
        safe_mode_layout.addWidget(self.safe_mode_status_label)
        
        # Safe Mode toggle switch (iOS style using QSS)
        self.safe_mode_switch = QCheckBox()
        self.safe_mode_switch.setChecked(False)  # Default: OFF

        # iOS-style toggle dimensions
        switch_width = 52  # 50-60px as requested
        switch_height = 28  # 28px as requested
        thumb_size = 24  # Thumb diameter (slightly smaller than height)

        self.safe_mode_switch.setStyleSheet(f"""
            QCheckBox {{
                spacing: 0px;
            }}
            QCheckBox::indicator {{
                width: {switch_width}px;
                height: {switch_height}px;
                border-radius: {switch_height//2}px;
                background-color: #E5E5EA;
                border: none;
            }}
            QCheckBox::indicator:checked {{
                background-color: #0078d4;
                border: none;
            }}
            QCheckBox::indicator:hover {{
                background-color: #D1D1D6;
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #0056CC;
            }}
        """)

        # Create custom thumb widget for smooth animation
        self.safe_mode_thumb = QWidget(self.safe_mode_switch)
        self.safe_mode_thumb.setFixedSize(thumb_size, thumb_size)
        self.safe_mode_thumb.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.safe_mode_thumb.setStyleSheet(f"""
            background-color: white;
            border-radius: {thumb_size//2}px;
            border: none;
        """)

        # Position thumb initially based on config status
        if self.safe_mode_active:
            self.safe_mode_thumb.move(52 - 24 - 2, 2)  # Checked position
        else:
            self.safe_mode_thumb.move(2, 2)  # Unchecked position
        self.safe_mode_thumb.show()

        # Connect to animate thumb movement
        self.safe_mode_switch.stateChanged.connect(self.animate_safe_mode_thumb)
        self.safe_mode_switch.stateChanged.connect(self.on_safe_mode_changed)
        safe_mode_layout.addWidget(self.safe_mode_switch)
        
        header_layout.addWidget(safe_mode_container)
        
        # Add reset counter button with dynamic sizing
        reset_btn = QPushButton("🔄 Reset Counter")
        button_font_size = max(10, min(20, int(dynamic_font_size * 0.6)))
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                border: none;
                border-radius: 5px;
                padding: {dynamic_padding//2}px {dynamic_padding}px;
                color: white;
                font-size: {button_font_size}px;
                margin-right: {dynamic_padding//2}px;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
        """)
        reset_btn.clicked.connect(self.reset_counter)
        header_layout.addWidget(reset_btn)
        

        
        # Add batch recap button with dynamic sizing
        recap_btn = QPushButton("📊 Batch Recap")
        recap_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                border: none;
                border-radius: 5px;
                padding: {dynamic_padding//2}px {dynamic_padding}px;
                color: white;
                font-size: {button_font_size}px;
                margin-right: {dynamic_padding//2}px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
        """)
        recap_btn.clicked.connect(self.show_batch_recap)
        header_layout.addWidget(recap_btn)
        
        # Add settings button with dynamic sizing
        settings_btn = QPushButton("⚙️ Settings")
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
        self.logging_table_widget = LoggingTableWidget(safe_mode=self.safe_mode_active)
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
        
        # Add Safe Mode indicator label (initially hidden)
        self.safe_mode_indicator = QLabel("SAFE MODE")
        self.safe_mode_indicator.setStyleSheet(f"""
            color: #FFD700;
            font-size: {dynamic_status_font_size}px;
            font-weight: bold;
            background-color: #2d2d2d;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            margin-left: 10px;
        """)
        self.safe_mode_indicator.setVisible(False)  # Initially hidden
        status_layout.addWidget(self.safe_mode_indicator)
        
        status_layout.addStretch()
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"color: white; font-size: {dynamic_status_font_size}px;")
        status_layout.addWidget(self.clock_label)
        
        # Add version label
        self.version_label = QLabel(APP_VERSION)
        self.version_label.setStyleSheet(f"color: #888888; font-size: {dynamic_status_font_size * 0.8}px; margin-left: 10px;")
        status_layout.addWidget(self.version_label)
        
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
        """Show the settings dialog with PIN protection."""
        # Check if user is already logged in and session is still valid
        if self.user_logged_in and self._is_login_session_valid():
            logger.info("User already logged in, skipping PIN verification")
            # Show settings dialog directly
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
            return

        # Get PIN from config
        pin = self.config.get("settings_pin", "668899")

        # Show PIN dialog first
        pin_dialog = PinDialog(correct_pin=pin, parent=self)

        # Connect to login successful signal to handle API credentials
        pin_dialog.login_successful.connect(self._handle_login_credentials)

        pin_dialog.raise_()
        pin_dialog.activateWindow()

        if pin_dialog.exec() != QDialog.DialogCode.Accepted:
            # User cancelled or failed PIN verification
            logger.info("Settings access denied - PIN verification failed or cancelled")
            return

        # PIN verified, mark user as logged in
        self.user_logged_in = True
        self.login_time = datetime.now()
        logger.info(f"User logged in successfully at {self.login_time}")

        # Show settings dialog with login credentials if available
        login_credentials = getattr(self, 'temp_api_credentials', None)
        dialog = SettingsDialog(self.config, login_credentials)

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
    
    def show_safe_mode_config_dialog(self):
        """Show Safe Mode configuration dialog with process selection."""
        try:
            # Create custom dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Safe Mode Configuration")
            dialog.setMinimumWidth(500)
            dialog.setMinimumHeight(400)

            # Force dialog to stay on top
            dialog.setWindowFlags(
                Qt.WindowType.Dialog |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.WindowSystemMenuHint |
                Qt.WindowType.WindowTitleHint
            )

            # Main layout
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Title
            title = QLabel("<b>Safe Mode Configuration</b>")
            title.setStyleSheet("font-size: 16px; color: #0078d4;")
            layout.addWidget(title)

            # Description
            desc = QLabel(
                "Pilih proses apa saja yang BISA dilakukan saat Safe Mode aktif.\n"
                "Proses yang tidak dipilih akan diblokir sepenuhnya."
            )
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666666; margin-bottom: 10px;")
            layout.addWidget(desc)

            # Process selection checkboxes
            self.safe_mode_checkboxes = {}

            # Available processes
            processes = [
                ("print", "Print - Mencetak produk"),
                ("save_log", "Save to Log"),
                ("save_batch", "Save to Batch"),
                ("send_erp", "Send to ERP")
            ]

            # Load current settings from config (default only print enabled)
            safe_mode_settings = self.config.get("safe_mode_settings", {
                "print": True,
                "save_log": False,
                "save_batch": False,
                "send_erp": False
            })

            for process_key, process_desc in processes:
                checkbox = QCheckBox(process_desc)
                checkbox.setChecked(safe_mode_settings.get(process_key, True))
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 12px;
                        padding: 5px;
                        margin-bottom: 5px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                    }
                """)
                layout.addWidget(checkbox)
                self.safe_mode_checkboxes[process_key] = checkbox

            # Warning text
            warning = QLabel(
                "<b>⚠️ Peringatan:</b> Proses yang tidak dipilih akan sepenuhnya diblokir.\n"
                "Anda dapat mengubah pengaturan ini kapan saja dengan menonaktifkan\n"
                "dan mengaktifkan kembali Safe Mode."
            )
            warning.setStyleSheet("color: #ff6b35; background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px;")
            warning.setWordWrap(True)
            layout.addWidget(warning)

            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            ok_button = QPushButton("Aktifkan Safe Mode")
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    min-width: 150px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            cancel_button = QPushButton("Batal")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)

            # Show dialog
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Save selected processes to config
                selected_processes = {}
                for process_key, checkbox in self.safe_mode_checkboxes.items():
                    selected_processes[process_key] = checkbox.isChecked()

                self.config["safe_mode_settings"] = selected_processes
                save_config(self.config)

                # Apply Safe Mode restrictions
                self.apply_safe_mode_restrictions(selected_processes)

                # Set Safe Mode as active
                self.safe_mode_active = True

                # Update Safe Mode indicator in footer
                if hasattr(self, 'safe_mode_indicator'):
                    self.safe_mode_indicator.setVisible(True)

                # Update logging table Safe Mode status
                if hasattr(self, 'logging_table'):
                    self.logging_table.safe_mode = True
                    logger.info("Logging table Safe Mode updated: True")

                # Update logging table widget Safe Mode status
                if hasattr(self, 'logging_table_widget'):
                    self.logging_table_widget.logging_table.safe_mode = True
                    logger.info("Logging table widget Safe Mode updated: True")

                # Update Safe Mode switch to ON position
                if hasattr(self, 'safe_mode_switch'):
                    self.safe_mode_switch.setChecked(True)
                    logger.info("Safe Mode switch set to ON position")

                # Update Safe Mode status label
                if hasattr(self, 'safe_mode_status_label'):
                    self.safe_mode_status_label.setText("ON")
                    self.safe_mode_status_label.setStyleSheet("color: #0078d4; font-size: 14px; font-weight: bold;")
                    logger.info("Safe Mode status label updated to ON")

                # Show confirmation
                enabled_processes = [k for k, v in selected_processes.items() if v]
                disabled_processes = [k for k, v in selected_processes.items() if not v]

                confirm_msg = (
                    f"<b>Safe Mode telah diaktifkan!</b><br><br>"
                    f"<b>✅ Proses yang DIaktifkan ({len(enabled_processes)}):</b><br>"
                )

                process_names = {
                    "print": "Print",
                    "save_log": "Save to Log",
                    "save_batch": "Save to Batch",
                    "send_erp": "Send to ERP"
                }

                for process in enabled_processes:
                    confirm_msg += f"• {process_names.get(process, process)}<br>"

                if disabled_processes:
                    confirm_msg += f"<br><b>❌ Proses yang Diblokir ({len(disabled_processes)}):</b><br>"
                    for process in disabled_processes:
                        confirm_msg += f"• {process_names.get(process, process)}<br>"

                confirm_msg += (
                    "<br><b>Semua operasi berjalan dalam mode simulasi.</b><br>"
                    "Data hanya tersimpan di file lokal untuk testing."
                )

                self.show_kiosk_dialog(
                    "information",
                    "Safe Mode Enabled",
                    confirm_msg
                )

                # Simpan status Safe Mode ke config
                self.config["safe_mode_enabled"] = True
                save_config(self.config)
                logger.info(f"Safe Mode enabled with settings: {selected_processes}")
            else:
                # User cancelled, disable Safe Mode
                logger.info("Safe Mode activation cancelled by user")
                if hasattr(self, 'safe_mode_switch'):
                    # Set toggle back to OFF position since user cancelled
                    self.safe_mode_switch.setChecked(False)
                self.safe_mode_active = False

        except Exception as e:
            logger.error(f"Error showing Safe Mode config dialog: {e}")
            self.show_kiosk_dialog(
                "critical",
                "Safe Mode Error",
                f"Error menampilkan dialog konfigurasi Safe Mode:\n\n{str(e)}"
            )

    def apply_safe_mode_restrictions(self, safe_mode_settings):
        """Apply Safe Mode restrictions based on selected processes."""
        try:
            # Store Safe Mode settings for use in other components
            self.safe_mode_settings = safe_mode_settings

            # Update BatchSummaryDialog with Safe Mode settings
            if hasattr(self, 'batch_summary_dialog'):
                self.batch_summary_dialog.safe_mode_settings = safe_mode_settings

            logger.info(f"Safe Mode restrictions applied: {safe_mode_settings}")

        except Exception as e:
            logger.error(f"Error applying Safe Mode restrictions: {e}")

    def show_batch_recap(self):
        """Show the batch summary/recap dialog."""
        try:
            # Check if Safe Mode is active and save_batch is not allowed
            if self.safe_mode_active and not self.safe_mode_settings.get("save_batch", False):
                self.show_kiosk_dialog(
                    "warning",
                    "Batch Recap Blocked - Safe Mode",
                    "Batch recap functionality is disabled in your Safe Mode configuration.\n\n"
                    "To enable batch recap, disable Safe Mode and reconfigure it."
                )
                logger.warning("Batch recap blocked - Safe Mode active and save_batch not allowed")
                return

            self.batch_summary_dialog = BatchSummaryDialog(
                self,
                safe_mode=self.safe_mode_active,
                safe_mode_settings=getattr(self, "safe_mode_settings", {}),
            )
            dialog = self.batch_summary_dialog
            dialog.finished.connect(lambda _: setattr(self, "batch_summary_dialog", None))

            # Force dialog to stay on top in kiosk mode
            dialog.setWindowFlags(
                Qt.WindowType.Dialog |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.WindowSystemMenuHint |
                Qt.WindowType.WindowTitleHint
            )

            dialog.raise_()
            dialog.activateWindow()
            dialog.exec()

            logger.info("Batch recap dialog shown")

        except Exception as e:
            logger.error(f"Error showing batch recap dialog: {e}")
            self.show_kiosk_dialog(
                "critical",
                "Batch Recap Error",
                f"Failed to show batch recap:\n\n{str(e)}"
            )
    
    def restart_application(self):
        """Restart the application with improved reliability."""
        try:
            # Show confirmation dialog
            reply = self.show_kiosk_dialog(
                "question",
                "Restart Application",
                "Are you sure you want to restart the application?\n\nThis will close the current instance and start a new one."
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                logger.info("User confirmed application restart")
                
                # Clean up resources
                self.cleanup_before_restart()
                
                # Try multiple restart methods
                if self.try_improved_restart():
                    # Close current application
                    QApplication.quit()
                else:
                    # Fallback: just quit and show message
                    logger.warning("Restart failed, quitting application")
                    self.show_kiosk_dialog(
                        "information",
                        "Restart Failed",
                        "The application will close. Please restart it manually."
                    )
                    QApplication.quit()
                
        except Exception as e:
            logger.error(f"Error during restart: {e}")
            self.show_kiosk_dialog(
                "critical",
                "Restart Error",
                f"Error restarting application:\n\n{str(e)}"
            )
    
    def try_improved_restart(self) -> bool:
        """Try multiple restart methods with improved reliability."""
        try:
            # Method 1: Direct executable restart (for compiled exe)
            if self.try_direct_executable_restart():
                return True
            
            # Method 2: Process-based restart
            if self.try_process_based_restart():
                return True
            
            # Method 3: Script-based restart (fallback)
            if self.try_script_based_restart():
                return True
            
            logger.error("All restart methods failed")
            return False
            
        except Exception as e:
            logger.error(f"Error in improved restart: {e}")
            return False
    
    def try_direct_executable_restart(self) -> bool:
        """Try to restart using direct executable path."""
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
                logger.info(f"Attempting direct executable restart: {exe_path}")
                
                # Start new process
                import subprocess
                subprocess.Popen([exe_path], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
                return True
            return False
        except Exception as e:
            logger.error(f"Direct executable restart failed: {e}")
            return False
    
    def try_process_based_restart(self) -> bool:
        """Try to restart using process-based method."""
        try:
            import subprocess
            import tempfile
            
            # Get current process info
            current_pid = os.getpid()
            
            # Create a simple restart script
            temp_dir = tempfile.gettempdir()
            restart_script = os.path.join(temp_dir, "restart_monitor.bat")
            
            if getattr(sys, 'frozen', False):
                # For compiled executable
                script_content = f'''@echo off
timeout /t 1 /nobreak > nul
start "" "{sys.executable}"
del "%~f0"
'''
            else:
                # For Python script
                script_content = f'''@echo off
timeout /t 1 /nobreak > nul
cd /d "{os.getcwd()}"
python run_app.py
del "%~f0"
'''
            
            with open(restart_script, 'w') as f:
                f.write(script_content)
            
            # Execute restart script
            subprocess.Popen(['cmd', '/c', restart_script], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            logger.info(f"Process-based restart initiated: {restart_script}")
            return True
            
        except Exception as e:
            logger.error(f"Process-based restart failed: {e}")
            return False
    
    def try_script_based_restart(self) -> bool:
        """Try to restart using the original script method."""
        try:
            self.create_restart_script()
            return True
        except Exception as e:
            logger.error(f"Script-based restart failed: {e}")
            return False
    
    def cleanup_before_restart(self):
        """Clean up resources before restart."""
        try:
            # Stop monitoring if running
            if hasattr(self, 'monitor') and self.monitor and self.monitor.is_running:
                logger.info("Stopping monitor before restart")
                self.monitor.stop()
            
            # Clean up heartbeat
            if hasattr(self, 'heartbeat'):
                logger.info("Cleaning up heartbeat before restart")
                self.heartbeat.cleanup()
            
            # Release singleton lock
            if hasattr(self, 'singleton_lock'):
                logger.info("Releasing singleton lock before restart")
                self.singleton_lock.release()
            
            logger.info("Cleanup completed before restart")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def create_restart_script(self):
        """Create a script to restart the application."""
        try:
            import sys
            import os
            
            # Get the current script path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_path = sys.executable
            else:
                # Running as script - handle different cases
                if len(sys.argv) > 0:
                    if sys.argv[0].endswith('python.exe') or sys.argv[0].endswith('python'):
                        # Running with python -m monitoring
                        # Get the current working directory and create the command
                        current_dir = os.getcwd()
                        app_path = f'python -m monitoring'
                        working_dir = current_dir
                    else:
                        # Running as direct script
                        app_path = sys.argv[0]
                        working_dir = os.path.dirname(os.path.abspath(app_path))
                else:
                    # Fallback
                    app_path = 'python -m monitoring'
                    working_dir = os.getcwd()
            
            # Create restart script content
            if app_path.startswith('python'):
                # For python -m monitoring command
                restart_script_content = f'''@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
cd /d "{working_dir}"
{app_path}
del "%~f0"
'''
            else:
                # For direct executable
                restart_script_content = f'''@echo off
REM Restart script for Roll Machine Monitor
echo Restarting Roll Machine Monitor...
timeout /t 2 /nobreak > nul
start "" "{app_path}"
del "%~f0"
'''
            
            # Write restart script to temp file
            import tempfile
            temp_dir = tempfile.gettempdir()
            restart_script_path = os.path.join(temp_dir, "restart_roll_machine.bat")
            
            with open(restart_script_path, 'w') as f:
                f.write(restart_script_content)
            
            # Execute restart script
            import subprocess
            subprocess.Popen(['cmd', '/c', restart_script_path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            logger.info(f"Restart script created: {restart_script_path}")
            logger.info(f"App path: {app_path}")
            logger.info(f"Working dir: {working_dir}")
            
        except Exception as e:
            logger.error(f"Error creating restart script: {e}")
            # Fallback: just quit and let user restart manually
            logger.info("Fallback: quitting application for manual restart")
    
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

        # Emit settings updated signal for other components
        self.settings_updated.emit(settings)

        # Refresh open dialogs that depend on config (e.g. batch recap)
        try:
            if getattr(self, "batch_summary_dialog", None) is not None:
                self.batch_summary_dialog.apply_settings_update(settings)
                logger.info("Batch recap dialog config refreshed after settings update")
        except Exception as e:
            logger.error(f"Error refreshing batch recap dialog config: {e}")

        # Refresh BOM product code in product form if BOM settings changed
        if any(key in settings for key in ['bom_name', 'bom_item', 'bom_product_code']):
            try:
                if hasattr(self, 'product_form') and self.product_form:
                    # Apply immediately from payload to avoid config path/timing issues
                    bom_product_code = settings.get("bom_product_code", "")
                    if bom_product_code:
                        self.product_form.apply_bom_to_form(
                            bom_product_code=bom_product_code,
                            bom_product_name=settings.get("bom_product_name", ""),
                            bom_color_code=settings.get("bom_color_code", ""),
                        )
                        logger.info("Applied BOM to ProductForm directly from settings payload")

                    # Delay slightly to ensure config is fully persisted before ProductForm reloads.
                    QTimer.singleShot(400, self.product_form.load_bom_product_code)
                    logger.info("Scheduled BOM reload in product form (400ms)")
            except Exception as e:
                logger.error(f"Error refreshing BOM product code: {e}")

        # Update BOM button visibility if verification status changed
        if 'is_verified' in settings:
            try:
                if hasattr(self, 'product_form') and self.product_form:
                    self.product_form.update_bom_button_visibility()
                    logger.info("BOM button visibility updated after verification status change")
            except Exception as e:
                logger.error(f"Error updating BOM button visibility: {e}")

        # Update BatchManager settings if batch name settings changed
        if any(key in settings for key in ['batch_name_format', 'batch_start_number']):
            try:
                from ..batch_manager import get_batch_manager
                batch_manager = get_batch_manager(settings=self.config)
                logger.info("Updated BatchManager with new batch name settings")
            except Exception as e:
                logger.error(f"Error updating BatchManager settings: {e}")

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
        """Handle product information updates with Supabase integration."""
        logger.info(f"Product info updated: {product_info}")
        if self.monitor:
            self.monitor.update_product_info(product_info)

        # Check if Safe Mode is active - skip database operations
        if self.safe_mode_active:
            logger.info("Safe Mode active - skipping database operations for product update")
            return

        # Check if Safe Mode is active and save_log is not allowed
        if self.safe_mode_active and not self.safe_mode_settings.get("save_log", False):
            logger.info("Safe Mode active and save_log not allowed - skipping database operations for product update")
            return

        # Also save to Supabase if connected
        try:
            from ..supabase_client import get_supabase_client
            supabase_client = get_supabase_client()

            if supabase_client.is_connected:
                # Get batch number with fallback
                batch_number = product_info.get('batch_number') or product_info.get('batch')

                # If no batch number, try to get from batch_manager
                if not batch_number or batch_number == 'Unknown':
                    from ..batch_manager import get_batch_manager
                    from ..config import load_config
                    config = load_config()
                    batch_manager = get_batch_manager(settings=config)
                    product_code = product_info.get('product_code', '')
                    if product_code:
                        color_code = product_info.get('color_code', '')
                        batch_number = batch_manager.get_batch_for_product(product_code, color_code)
                        logger.info(f"Auto-generated batch for production log: {batch_number}")

                # Save production log to Supabase
                production_log_data = {
                    'batch': batch_number or 'Unknown',
                    'product_code': product_info.get('product_code', 'Unknown'),
                    'product_name': product_info.get('product_name', 'Unknown'),
                    'color_code': product_info.get('color_code', 'Unknown'),
                    'product_length': product_info.get('current_length', 0.0),
                    'target_length': product_info.get('target_length', 0),
                    'units': product_info.get('units', 'Meter'),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'saved'
                }

                result = supabase_client.insert_production_log(production_log_data)

                if result:
                    logger.info(f"Production log saved to Supabase: {batch_number}")
                else:
                    logger.error(f"Failed to save production log to Supabase: {batch_number}")
            else:
                logger.warning("Supabase not connected, skipping production log save")

        except Exception as e:
            logger.error(f"Error saving production log to Supabase: {e}")
    
    @Slot()
    def reset_counter(self):
        """Reset counter by sending command 55 AA 01 00 00 00 to device."""
        try:
            # Show confirmation dialog first
            reply = self.show_kiosk_dialog(
                "question",
                "Reset Counter",
                "Are you sure you want to reset the counter?\n\nThis will reset the current collection data to zero and reset cycle time tracking.\n\nNext product will start when length counter reaches 0.01."
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                logger.info("User cancelled reset counter")
                return
            
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
                    
                    # Reset length display in monitoring view
                    if hasattr(self, 'monitoring_view') and self.monitoring_view:
                        self.monitoring_view.reset_length_display()
                        logger.info("Length display reset in monitoring view")
                    
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
    
    def animate_safe_mode_thumb(self, state):
        """Animate the Safe Mode thumb movement with smooth transition."""
        try:
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve

            is_checked = state == Qt.CheckState.Checked.value

            # Create animation for thumb movement
            self.thumb_animation = QPropertyAnimation(self.safe_mode_thumb, b"pos")
            self.thumb_animation.setDuration(300)  # 300ms animation
            self.thumb_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # Set start and end positions
            start_pos = self.safe_mode_thumb.pos()
            if is_checked:
                # Move thumb to right (checked position)
                end_pos = QPoint(52 - 24 - 2, 2)  # switch_width - thumb_size - padding
            else:
                # Move thumb to left (unchecked position)
                end_pos = QPoint(2, 2)

            self.thumb_animation.setStartValue(start_pos)
            self.thumb_animation.setEndValue(end_pos)
            self.thumb_animation.start()

            # Handle Safe Mode logic
            self.on_safe_mode_changed(state)

            # Update logging table Safe Mode status
            if hasattr(self, 'logging_table'):
                self.logging_table.safe_mode = self.safe_mode_active
                logger.info(f"Logging table Safe Mode updated: {self.safe_mode_active}")

            # Update logging table widget Safe Mode status
            if hasattr(self, 'logging_table_widget'):
                self.logging_table_widget.logging_table.safe_mode = self.safe_mode_active
                logger.info(f"Logging table widget Safe Mode updated: {self.safe_mode_active}")

        except Exception as e:
            logger.error(f"Error animating Safe Mode thumb: {e}")

    def on_safe_mode_changed(self, state):
        """Handle Safe Mode toggle switch changes."""
        try:
            is_enabled = state == Qt.CheckState.Checked.value

            if is_enabled:
                # When toggle is switched ON, temporarily disconnect signal to prevent visual change
                # until user confirms in dialog
                logger.info("Safe Mode toggle clicked - showing configuration dialog")

                # Temporarily disconnect the signal to prevent immediate visual feedback
                self.safe_mode_switch.stateChanged.disconnect(self.on_safe_mode_changed)

                # Show Safe Mode configuration dialog
                # The dialog will handle setting the toggle state based on user choice
                self.show_safe_mode_config_dialog()

                # Reconnect the signal after dialog is handled
                self.safe_mode_switch.stateChanged.connect(self.on_safe_mode_changed)
            else:
                # When toggle is switched OFF, disable Safe Mode immediately
                logger.info("Safe Mode DISABLED - Database operations enabled")

                # Update Safe Mode indicator in footer
                if hasattr(self, 'safe_mode_indicator'):
                    self.safe_mode_indicator.setVisible(False)

                # Set Safe Mode flag for database operations
                self.safe_mode_active = False

                # Update logging table Safe Mode status
                if hasattr(self, 'logging_table'):
                    self.logging_table.safe_mode = False
                    logger.info("Logging table Safe Mode updated: False")

                # Update logging table widget Safe Mode status
                if hasattr(self, 'logging_table_widget'):
                    self.logging_table_widget.logging_table.safe_mode = False
                    logger.info("Logging table widget Safe Mode updated: False")

                # Update Safe Mode switch to OFF position
                if hasattr(self, 'safe_mode_switch'):
                    self.safe_mode_switch.setChecked(False)
                    logger.info("Safe Mode switch set to OFF position")

                # Update Safe Mode status label
                if hasattr(self, 'safe_mode_status_label'):
                    self.safe_mode_status_label.setText("OFF")
                    self.safe_mode_status_label.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: bold;")
                    logger.info("Safe Mode status label updated to OFF")

                # Show confirmation message
                self.show_kiosk_dialog(
                    "information",
                    "Safe Mode Disabled",
                    "Safe Mode telah dinonaktifkan.\n\nSemua proses aplikasi akan kembali normal\ndengan penyimpanan data ke database.\n\nData akan tersimpan seperti biasa."
                )

                # Simpan status Safe Mode ke config
                self.config["safe_mode_enabled"] = False
                save_config(self.config)
                logger.info("Safe Mode status saved to config: False")

        except Exception as e:
            logger.error(f"Error handling Safe Mode change: {e}")
            # Make sure to reconnect signal if there's an error
            try:
                self.safe_mode_switch.stateChanged.connect(self.on_safe_mode_changed)
            except:
                pass
            self.show_kiosk_dialog(
                "critical",
                "Safe Mode Error",
                f"Error mengubah status Safe Mode:\n\n{str(e)}"
            )
    
    @Slot()
    def sync_offline_queue(self):
        """
        Automatically sync offline queue with Supabase.
        Called by timer every 5 minutes.
        """
        # Check if Safe Mode is active - skip database operations
        if self.safe_mode_active:
            logger.debug("Safe Mode active - skipping offline queue sync")
            return

        # Check if Safe Mode is active and save_log is not allowed
        if self.safe_mode_active and not self.safe_mode_settings.get("save_log", False):
            logger.debug("Safe Mode active and save_log not allowed - skipping offline queue sync")
            return

        try:
            from ..supabase_client import get_supabase_client
            supabase_client = get_supabase_client()

            # Check if Supabase is connected
            if not supabase_client.is_connected:
                logger.debug("Supabase not connected, skipping queue sync")
                return

            # Get queue count before processing
            queue_count = supabase_client.get_queue_count()

            if queue_count == 0:
                logger.debug("No pending operations in queue")
                return

            logger.info(f"Starting automatic queue sync - {queue_count} operations pending")

            # Process the queue
            success_count, failed_count = supabase_client.process_offline_queue()

            if success_count > 0:
                logger.info(f"Queue sync completed: {success_count} synced, {failed_count} failed")
                # Update status bar with sync info
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(
                        f"Synced {success_count} operations to cloud",
                        5000  # Show for 5 seconds
                    )
            elif failed_count > 0:
                logger.warning(f"Queue sync had errors: {failed_count} operations failed")

        except Exception as e:
            logger.error(f"Error during automatic queue sync: {e}")
    
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
                    auto_send_interval=1200  # Changed from 100ms to 1200ms
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
        machine_unit = fields.get('unit', 'meter')  # Unit from machine
        
        # Get user selected unit from product form
        user_selected_unit = 'meter'  # Default
        if hasattr(self, 'product_form') and self.product_form:
            selected_unit_text = self.product_form.selected_unit
            user_selected_unit = selected_unit_text.lower() if selected_unit_text else 'meter'
        
        # Convert current_count to user selected unit if different from machine unit
        length_for_calculation = current_count
        if machine_unit != user_selected_unit:
            if machine_unit == 'yard' and user_selected_unit == 'meter':
                # Convert from yard to meter
                length_for_calculation = current_count * 0.9144
            elif machine_unit == 'meter' and user_selected_unit == 'yard':
                # Convert from meter to yard
                length_for_calculation = current_count * 1.09361
        
        # Calculate length print with tolerance using user selected unit
        length_print_text = self.calculate_length_print(length_for_calculation, user_selected_unit)
        
        # Store values for logging (to ensure consistency with "Length Print" card)
        self.current_machine_length_raw = current_count  # Store raw machine length
        self.current_user_unit = user_selected_unit  # Store user selected unit
        self.current_machine_unit = machine_unit  # Store machine unit
        
        # Calculate the numeric value of length_print (with tolerance) for logging
        try:
            tolerance_percent = self.config.get("length_tolerance", 0.0)
            decimal_points = self.config.get("decimal_points", 1)
            rounding_method = self.config.get("rounding", "UP")
            
            if tolerance_percent > 0:
                from ..config import calculate_print_length
                self.current_length_print_value = calculate_print_length(length_for_calculation, tolerance_percent, decimal_points, rounding_method)
            else:
                self.current_length_print_value = length_for_calculation
        except Exception as e:
            logger.warning(f"Error calculating length_print_value: {e}")
            self.current_length_print_value = length_for_calculation
        
        # Add length print to data for monitoring view
        data['length_print_text'] = length_print_text
        data['length_print_value'] = self.current_length_print_value  # Store calculated value with tolerance
        data['user_selected_unit'] = user_selected_unit  # Add user selected unit to data
        
        self.monitoring_view.update_data(data)
        
        # Update target length input with length print value (with tolerance)
        if hasattr(self, 'product_form') and self.product_form:
            machine_unit = fields.get('unit', 'meter')
            # Use length print text (with tolerance) instead of raw current length
            self.product_form.update_target_with_length_print(length_print_text)
            self.product_form.update_unit_from_monitoring(machine_unit)
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
            
            # Detect start of a new product cycle.
            #
            # Sebelumnya memakai trigger "length ~ 0.01", namun di lapangan nilai bisa meloncat
            # (misal langsung 0.20) sehingga event start terlewat dan cycle time jadi N/A.
            # Untuk lebih robust, kita anggap cycle mulai saat length sudah bergerak di atas 0.1m
            # setelah reset (is_new_product_started False).
            if length > 0.1 and not self.is_new_product_started:
                # New product cycle started
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
                self.product_start_times.append(current_time)  # Add to list for tracking
                
                logger.info(
                    f"New product cycle started - length counter at {length:.3f}m, "
                    f"total products: {len(self.product_start_times)}"
                )
            
            # Detect roll length reset to 0 (cycle end - after Reset Counter)
            elif self.last_length > 0.1 and length <= 0.1:
                # Roll length reset to 0 - cycle ended, prepare for next product
                self.is_new_product_started = False
                logger.info(f"Cycle ended - roll length reset to {length:.2f}m")
                
                # Reset length display in monitoring view when device resets
                if hasattr(self, 'monitoring_view') and self.monitoring_view:
                    self.monitoring_view.reset_length_display()
                    logger.info("Length display reset in monitoring view (device reset detected)")
            
            # Update last length for next comparison
            self.last_length = length
                    
        except Exception as e:
            logger.error(f"Error in production logging: {e}")
    
    def handle_print_logging(self, print_data: Dict[str, Any]):
        """Handle logging when print button is clicked with correct timing according to CYCLE_TIME.md."""
        try:
            # Check if Safe Mode is active and print is not allowed
            if self.safe_mode_active and not self.safe_mode_settings.get("print", False):
                self.show_kiosk_dialog(
                    "warning",
                    "Print Blocked - Safe Mode",
                    "Print functionality is disabled in your Safe Mode configuration.\n\n"
                    "To enable printing, disable Safe Mode and reconfigure it."
                )
                logger.warning("Print blocked - Safe Mode active and print not allowed")
                return

            current_time = datetime.now()

            # Get product info from print data
            product_name = print_data.get('product_name', 'Unknown')
            product_code = print_data.get('product_code', 'Unknown')
            product_length = print_data.get('product_length', 0.0)
            # Try both 'batch_number' and 'batch' for backwards compatibility
            batch = print_data.get('batch_number') or print_data.get('batch', 'Unknown')

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

            # Ensure we have a valid "product start time" for Close Cycle.
            # In real devices, the "start trigger" can be missed; in that case, fallback to roll_start_time.
            if not getattr(self, "last_product_start_time", None) and getattr(self, "roll_start_time", None):
                self.last_product_start_time = self.roll_start_time
                if hasattr(self, "product_start_times") and isinstance(self.product_start_times, list):
                    if not self.product_start_times:
                        self.product_start_times.append(self.last_product_start_time)
                logger.info(
                    "Initialized last_product_start_time from roll_start_time during print "
                    f"({self.last_product_start_time.strftime('%H:%M:%S')})"
                )

            # Check minimum roll time requirement BEFORE logging
            min_roll_time = self.config.get("roll_time_minimum_seconds", 60)
            if min_roll_time > 0 and roll_time < min_roll_time:
                # Show warning dialog and ask user to confirm
                reply = self.show_kiosk_dialog(
                    "question",
                    "Waktu Roll Terlalu Singkat",
                    f"⚠️ PERINGATAN: Waktu roll saat ini hanya {roll_time:.1f} detik.\n\n"
                    f"Minimum waktu roll yang disyaratkan: {min_roll_time} detik.\n\n"
                    f"Apakah data ini benar-benar ingin disimpan?\n\n"
                    f"Jika waktu roll terlalu singkat, mungkin ada kesalahan dalam proses rolling."
                )

                if reply != 0x00004000:  # QMessageBox.StandardButton.Yes
                    logger.info(f"User cancelled print due to short roll time: {roll_time:.1f}s < {min_roll_time}s")
                    # User chose not to save - return silently without notification
                    return

            # For Print button: cycle_time is always None initially
            # Cycle time will be calculated when next product starts (length = 0.01) or Close Cycle is pressed
            cycle_time = None

            # Initialize product_start_times if not exists
            if not hasattr(self, 'product_start_times'):
                self.product_start_times = []
            
            # NOTE: product_start_times will be appended in handle_production_logging when length = 0.01
            # This ensures cycle time is calculated correctly between products

            # Calculate length_print (with tolerance) for logging
            # Use the stored values from handle_data to ensure consistency with "Length Print" card
            length_print_value = None
            try:
                # First, try to use the stored length_print_value (most accurate, matches card display)
                if hasattr(self, 'current_length_print_value') and self.current_length_print_value is not None:
                    length_print_value = self.current_length_print_value
                    logger.info(f"Using stored length_print_value: {length_print_value:.2f} for logging")
                # Second, try to get from product_form's current_machine_length and recalculate
                elif hasattr(self, 'product_form') and self.product_form:
                    current_machine_length = getattr(self.product_form, '_current_machine_length', None)
                    if current_machine_length is not None:
                        # Get unit from product_form
                        user_selected_unit = 'meter'
                        if hasattr(self.product_form, 'selected_unit'):
                            selected_unit_text = self.product_form.selected_unit
                            user_selected_unit = selected_unit_text.lower() if selected_unit_text else 'meter'
                        
                        # Get machine unit (assume same as stored or default to meter)
                        machine_unit = getattr(self, 'current_machine_unit', 'meter')
                        
                        # Convert to user selected unit if different
                        length_for_calc = current_machine_length
                        if machine_unit != user_selected_unit:
                            if machine_unit == 'yard' and user_selected_unit == 'meter':
                                length_for_calc = current_machine_length * 0.9144
                            elif machine_unit == 'meter' and user_selected_unit == 'yard':
                                length_for_calc = current_machine_length * 1.09361
                        
                        # Get tolerance settings from config
                        tolerance_percent = self.config.get("length_tolerance", 0.0)
                        decimal_points = self.config.get("decimal_points", 1)
                        rounding_method = self.config.get("rounding", "UP")
                        
                        # Calculate length_print using the same logic as calculate_length_print
                        if tolerance_percent > 0:
                            from ..config import calculate_print_length
                            length_print_value = calculate_print_length(length_for_calc, tolerance_percent, decimal_points, rounding_method)
                        else:
                            length_print_value = length_for_calc
                            
                        logger.info(f"Calculated length_print from product_form machine length: {length_print_value:.2f} {user_selected_unit} (from {current_machine_length:.2f} {machine_unit})")
                else:
                    # Fallback: recalculate from stored machine length and unit
                    if hasattr(self, 'current_machine_length_raw') and self.current_machine_length_raw is not None:
                        machine_length = self.current_machine_length_raw
                        user_selected_unit = getattr(self, 'current_user_unit', 'meter')
                        
                        # Get machine unit from stored value
                        machine_unit = getattr(self, 'current_machine_unit', 'meter')
                        
                        # Convert to user selected unit if different
                        length_for_calc = machine_length
                        if machine_unit != user_selected_unit:
                            if machine_unit == 'yard' and user_selected_unit == 'meter':
                                length_for_calc = machine_length * 0.9144
                            elif machine_unit == 'meter' and user_selected_unit == 'yard':
                                length_for_calc = machine_length * 1.09361
                        
                        # Get tolerance settings from config
                        tolerance_percent = self.config.get("length_tolerance", 0.0)
                        decimal_points = self.config.get("decimal_points", 1)
                        rounding_method = self.config.get("rounding", "UP")
                        
                        # Calculate length_print using the same logic as calculate_length_print
                        if tolerance_percent > 0:
                            from ..config import calculate_print_length
                            length_print_value = calculate_print_length(length_for_calc, tolerance_percent, decimal_points, rounding_method)
                        else:
                            length_print_value = length_for_calc
                            
                        logger.info(f"Calculated length_print from machine length: {length_print_value:.2f} {user_selected_unit} (from {machine_length:.2f} {machine_unit})")
                    else:
                        # Last fallback: use product_length and calculate
                        tolerance_percent = self.config.get("length_tolerance", 0.0)
                        decimal_points = self.config.get("decimal_points", 1)
                        rounding_method = self.config.get("rounding", "UP")
                        
                        units_text = print_data.get('units', 'Meter')
                        user_selected_unit = units_text.lower() if units_text else 'meter'
                        length_for_calc = product_length
                        
                        if tolerance_percent > 0:
                            from ..config import calculate_print_length
                            length_print_value = calculate_print_length(length_for_calc, tolerance_percent, decimal_points, rounding_method)
                        else:
                            length_print_value = length_for_calc
                            
                        logger.warning(f"Using fallback calculation for length_print: {length_print_value:.2f} (from product_length: {product_length:.2f})")
            except Exception as e:
                logger.error(f"Error calculating length_print for logging: {e}, using product_length as fallback")
                length_print_value = product_length

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
                        settings_timestamp=settings_timestamp,  # When settings were last changed
                        safe_mode=self.safe_mode_active,  # Pass Safe Mode status
                        length_print=length_print_value  # Length with tolerance
                    )
                    # Refresh table after print
                    if hasattr(self.logging_table_widget, 'manual_refresh'):
                        self.logging_table_widget.manual_refresh()

            logger.info(f"Print logged: {product_code} - Cycle: Empty (will be calculated later), Roll: {roll_time:.1f}s")

            # DO NOT reset roll_start_time after print - roll time should accumulate until new product starts
            # Roll time represents the time spent rolling for each individual print operation
            logger.info(f"Print logged - roll time: {roll_time:.1f}s, roll_start_time preserved for next print")

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
            
            # Calculate length_print for timeout logging - use stored value for consistency
            length_print_value = None
            try:
                # First, try to use the stored length_print_value (most accurate, matches card display)
                if hasattr(self, 'current_length_print_value') and self.current_length_print_value is not None:
                    length_print_value = self.current_length_print_value
                    logger.info(f"Using stored length_print_value for timeout: {length_print_value:.2f}")
                else:
                    # Fallback: recalculate from stored machine length and unit
                    if hasattr(self, 'current_machine_length_raw') and self.current_machine_length_raw is not None:
                        machine_length = self.current_machine_length_raw
                        user_selected_unit = getattr(self, 'current_user_unit', 'meter')
                        machine_unit = getattr(self, 'current_machine_unit', 'meter')
                        
                        # Convert to user selected unit if different
                        length_for_calc = machine_length
                        if machine_unit != user_selected_unit:
                            if machine_unit == 'yard' and user_selected_unit == 'meter':
                                length_for_calc = machine_length * 0.9144
                            elif machine_unit == 'meter' and user_selected_unit == 'yard':
                                length_for_calc = machine_length * 1.09361
                        
                        # Get tolerance settings from config
                        tolerance_percent = self.config.get("length_tolerance", 0.0)
                        decimal_points = self.config.get("decimal_points", 1)
                        rounding_method = self.config.get("rounding", "UP")
                        
                        # Calculate length_print using the same logic as calculate_length_print
                        if tolerance_percent > 0:
                            from ..config import calculate_print_length
                            length_print_value = calculate_print_length(length_for_calc, tolerance_percent, decimal_points, rounding_method)
                        else:
                            length_print_value = length_for_calc
                    else:
                        # Last fallback: use product_length from current_product_info
                        product_length = self.current_product_info.get('product_length', 0.0) if hasattr(self, 'current_product_info') and self.current_product_info else 0.0
                        tolerance_percent = self.config.get("length_tolerance", 0.0)
                        decimal_points = self.config.get("decimal_points", 1)
                        rounding_method = self.config.get("rounding", "UP")
                        
                        if tolerance_percent > 0:
                            from ..config import calculate_print_length
                            length_print_value = calculate_print_length(product_length, tolerance_percent, decimal_points, rounding_method)
                        else:
                            length_print_value = product_length
                            
                        logger.warning(f"Using fallback calculation for timeout length_print: {length_print_value:.2f}")
            except Exception as e:
                logger.error(f"Error calculating length_print for timeout logging: {e}")
                length_print_value = self.current_product_info.get('product_length', 0.0) if hasattr(self, 'current_product_info') and self.current_product_info else 0.0

            # Log the final production data for this cycle
            if hasattr(self, 'logging_table_widget') and self.logging_table_widget and hasattr(self, 'current_product_info') and self.current_product_info:
                self.logging_table_widget.add_production_entry(
                    product_name=self.current_product_info.get('product_name', 'Unknown'),
                    product_code=self.current_product_info.get('product_code', 'Unknown'),
                    product_length=self.current_product_info.get('product_length', 0.0),
                    batch=self.current_product_info.get('batch', 'Unknown'),
                    cycle_time=cycle_time,
                    roll_time=roll_time,
                    length_print=length_print_value
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
            elif hasattr(self, 'roll_start_time') and self.roll_start_time:
                # Last fallback: use roll_start_time (can exist even if start trigger was missed)
                cycle_time = (current_time - self.roll_start_time).total_seconds()
                logger.info(
                    f"Close cycle (roll_start_time fallback): roll started at "
                    f"{self.roll_start_time.strftime('%H:%M:%S')}, current time {current_time.strftime('%H:%M:%S')}"
                )
            
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
            
            # Reset length display in monitoring view
            if hasattr(self, 'monitoring_view') and self.monitoring_view:
                self.monitoring_view.reset_length_display()
                logger.info("Length display reset in monitoring view after close cycle")
            
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
        # Serial display has been removed - no longer needed
        # This method now only handles heartbeat recording
        
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

    def _is_login_session_valid(self):
        """Check if the current login session is still valid."""
        if not self.user_logged_in or not self.login_time:
            return False

        # Check if session has timed out
        elapsed_minutes = (datetime.now() - self.login_time).total_seconds() / 60
        if elapsed_minutes >= self.login_timeout_minutes:
            logger.info(f"Login session expired after {elapsed_minutes:.1f} minutes")
            self.user_logged_in = False
            self.login_time = None
            return False

        return True

    def _check_login_session_timeout(self):
        """Check login session timeout periodically."""
        if self.user_logged_in and not self._is_login_session_valid():
            logger.info("Login session timeout detected during periodic check")
            # Session has expired, no need to show message as user might not be actively using settings

    def _handle_login_credentials(self, username: str, api_key: str, api_secret: str):
        """Handle successful login credentials from PIN dialog."""
        try:
            logger.info(f"=== RECEIVED LOGIN CREDENTIALS ===")
            logger.info(f"Username: {username}")
            logger.info(f"API Key: {api_key}")
            logger.info(f"API Secret: {api_secret}")
            logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Store the credentials temporarily for settings dialog
            self.temp_api_credentials = {
                "username": username,
                "api_key": api_key,
                "api_secret": api_secret
            }

            logger.info("API credentials stored temporarily for settings dialog")
            
            # Log credential validation status
            if api_key and api_secret:
                logger.info(f"Credential Status: VALID - User has API access")
                logger.info(f"API Key Length: {len(api_key)}")
                logger.info(f"API Secret Length: {len(api_secret)}")
            else:
                logger.warning(f"Credential Status: INVALID - User lacks API credentials")
            
            logger.info(f"=== END LOGIN CREDENTIALS HANDLING ===")

        except Exception as e:
            logger.error(f"Error handling login credentials: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def keyPressEvent(self, event):
        """Override key press events to handle shortcuts and disable certain shortcuts in kiosk mode."""
        # Record user activity
        self.heartbeat.record_activity()
        
        # Handle keyboard shortcuts
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_P:
                # Ctrl+P: Print product info
                logger.info("Keyboard shortcut: Ctrl+P - Print product info")
                if hasattr(self, 'product_form') and self.product_form:
                    self.product_form.print_product_info()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_C:
                # Ctrl+C: Close cycle
                logger.info("Keyboard shortcut: Ctrl+C - Close cycle")
                if hasattr(self, 'product_form') and self.product_form:
                    self.product_form.close_cycle_with_save()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_R:
                # Ctrl+R: Reset counter
                logger.info("Keyboard shortcut: Ctrl+R - Reset counter")
                self.reset_counter()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_S:
                # Ctrl+S: Open settings
                logger.info("Keyboard shortcut: Ctrl+S - Open settings")
                self.show_settings()
                event.accept()
                return
        
        # Handle Ctrl+Shift+R for restart (only in settings dialog)
        if (event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and 
            event.key() == Qt.Key.Key_R):
            # Check if settings dialog is open
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            for widget in app.topLevelWidgets():
                if hasattr(widget, 'windowTitle') and "Settings" in widget.windowTitle():
                    logger.info("Keyboard shortcut: Ctrl+Shift+R - Restart application")
                    if hasattr(widget, 'restart_application'):
                        widget.restart_application()
                    event.accept()
                    return
        
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
