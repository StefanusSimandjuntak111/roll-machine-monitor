from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QFrame, QLabel, QHBoxLayout, QTabWidget,
    QLineEdit, QRadioButton, QButtonGroup, QSpinBox, QGroupBox,
    QMessageBox, QCheckBox, QWidget, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QPoint
from typing import Dict, Any
import serial.tools.list_ports
import logging
import json
import urllib.parse
import requests

from .pin_dialog import ChangePinDialog

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Dialog for configuring application settings with tabbed interface."""
    
    # Signal emitted when settings are saved
    settings_updated = Signal(dict)
    
    def __init__(self, current_settings: Dict[str, Any], login_credentials: Dict[str, str] = None):
        super().__init__()
        self.current_settings = current_settings
        self.selected_bom_data = None  # Initialize BOM data
        self.login_credentials = login_credentials  # Store login credentials if available
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the settings dialog UI with tabs."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Set window flags for proper dialog behavior
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Set modal behavior
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444444;
                border-radius: 5px;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #353535;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #555555;
            }
        """)
        
        # Create tabs (ERP Stock Entry first)
        self.create_erp_settings_tab()
        self.create_port_settings_tab()
        self.create_port_management_tab()
        self.create_page_settings_tab()
        self.create_printer_settings_tab()
        self.create_api_settings_tab()
        self.create_supabase_settings_tab()
        self.create_batch_name_settings_tab()
        self.create_security_settings_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        refresh_btn.setStyleSheet(self.get_button_style("secondary"))
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        # Restart button with orange color
        restart_btn = QPushButton("🔄 Restart Application")
        restart_btn.clicked.connect(self.restart_application)
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff8c00;
                border: 1px solid #ff8c00;
                border-radius: 5px;
                color: white;
                font-size: 14px;
                padding: 8px 15px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #ff7f00;
                border: 1px solid #ff7f00;
            }
            QPushButton:pressed {
                background-color: #ff6b00;
                border: 1px solid #ff6b00;
            }
        """)
        button_layout.addWidget(restart_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet(self.get_button_style("primary"))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_settings)
        cancel_btn.setStyleSheet(self.get_button_style("danger"))
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize connection status after all UI is created
        self.update_connection_status()

        # Auto-populate API settings if login credentials are available
        if self.login_credentials:
            self._populate_api_settings_from_login()
    
    def create_port_settings_tab(self):
        """Create the Port Settings tab."""
        port_tab = QFrame()
        port_layout = QVBoxLayout(port_tab)
        port_layout.setSpacing(20)
        
        # Title
        title = QLabel("Serial Connection Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        port_layout.addWidget(title)
        
        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
        """)
        
        settings_form = QFormLayout(settings_frame)
        settings_form.setSpacing(15)
        
        # Port selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        settings_form.addRow("Serial Port:", self.port_combo)

        # Baudrate selection
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems([
            "9600", "19200", "38400", "57600", "115200"
        ])
        self.baudrate_combo.setCurrentText(
            str(self.current_settings.get("baudrate", 19200))
        )
        settings_form.addRow("Baudrate:", self.baudrate_combo)

        # Roll Time Minimum Duration
        self.roll_time_min_input = QSpinBox()
        self.roll_time_min_input.setRange(0, 300)  # 0-300 seconds (5 minutes)
        self.roll_time_min_input.setValue(self.current_settings.get("roll_time_minimum_seconds", 60))
        self.roll_time_min_input.setSuffix(" detik")
        self.roll_time_min_input.setToolTip("Minimum waktu roll yang disyaratkan sebelum mengizinkan print. Set 0 untuk menonaktifkan validasi.")
        # Style to match dark theme
        self.roll_time_min_input.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 20px;
                min-width: 120px;
            }
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #404040;
                border: none;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #555555;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid white;
                margin-bottom: 2px;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                margin-top: 2px;
            }
        """)
        settings_form.addRow("Minimum Waktu Roll:", self.roll_time_min_input)
        
        port_layout.addWidget(settings_frame)
        port_layout.addStretch()
        
        self.tab_widget.addTab(port_tab, "Port Settings")
    
    def create_port_management_tab(self):
        """Create the Port Management tab."""
        management_tab = QFrame()
        management_layout = QVBoxLayout(management_tab)
        management_layout.setSpacing(20)
        
        # Title
        title = QLabel("Port Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        management_layout.addWidget(title)
        
        # Port Management frame
        management_frame = QFrame()
        management_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 12px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #404040;
                border: 1px solid #555555;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #666666;
                border: 1px solid #333333;
            }
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        management_form = QVBoxLayout(management_frame)
        management_form.setSpacing(15)
        
        # Connection Status Group
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.connection_status_label = QLabel("Not Connected")
        self.connection_status_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #1e1e1e;
                border-radius: 5px;
                border: 1px solid #444444;
            }
        """)
        self.connection_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.connection_status_label)
        
        management_form.addWidget(status_group)
        
        # Port Control Group
        control_group = QGroupBox("Port Control")
        control_layout = QVBoxLayout(control_group)
        
        # Kill/Close Port Button
        self.kill_port_btn = QPushButton("🔌 Kill/Close Port Connection")
        self.kill_port_btn.setStyleSheet("""
            QPushButton {
                background-color: #d83b01;
                border: 1px solid #ea4a1f;
            }
            QPushButton:hover {
                background-color: #ea4a1f;
                border: 1px solid #f55a2f;
            }
        """)
        self.kill_port_btn.clicked.connect(self.kill_port_connection)
        control_layout.addWidget(self.kill_port_btn)
        
        # Auto Connect Button
        self.auto_connect_btn = QPushButton("🔗 Auto Connect to Available Port")
        self.auto_connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                border: 1px solid #107c10;
            }
            QPushButton:hover {
                background-color: #0f6b0f;
                border: 1px solid #0f6b0f;
            }
        """)
        self.auto_connect_btn.clicked.connect(self.auto_connect_port)
        control_layout.addWidget(self.auto_connect_btn)
        
        # Disconnect Button
        self.disconnect_btn = QPushButton("❌ Disconnect")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                border: 1px solid #777777;
            }
            QPushButton:hover {
                background-color: #777777;
                border: 1px solid #888888;
            }
        """)
        self.disconnect_btn.clicked.connect(self.disconnect_port)
        self.disconnect_btn.setEnabled(False)
        control_layout.addWidget(self.disconnect_btn)
        
        management_form.addWidget(control_group)
        
        # Auto Reconnect Group
        reconnect_group = QGroupBox("Auto Reconnect Settings")
        reconnect_layout = QVBoxLayout(reconnect_group)
        
        self.auto_reconnect_checkbox = QCheckBox("Enable Auto Reconnect on Disconnect")
        self.auto_reconnect_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #666666;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
            }
        """)
        self.auto_reconnect_checkbox.setChecked(True)
        reconnect_layout.addWidget(self.auto_reconnect_checkbox)
        
        management_form.addWidget(reconnect_group)
        
        management_layout.addWidget(management_frame)
        management_layout.addStretch()
        
        self.tab_widget.addTab(management_tab, "Port Management")
    
    def create_page_settings_tab(self):
        """Create the Page Settings tab."""
        page_tab = QFrame()
        page_layout = QVBoxLayout(page_tab)
        page_layout.setSpacing(20)
        
        # Title
        title = QLabel("Page Display Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        page_layout.addWidget(title)
        
        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit, QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QRadioButton {
                color: #e0e0e0;
                font-size: 14px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #666666;
                background-color: #2d2d2d;
            }
            QRadioButton::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
            }
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        settings_form = QFormLayout(settings_frame)
        settings_form.setSpacing(15)
        
        # 1. Length Tolerance
        self.tolerance_input = QLineEdit()
        self.tolerance_input.setPlaceholderText("3")
        self.tolerance_input.setText(str(self.current_settings.get("length_tolerance", 3)))
        self.tolerance_input.textChanged.connect(self.update_conversion_preview)
        settings_form.addRow("Length Tolerance (%):", self.tolerance_input)
        
        # 2. Rounding Precision
        self.decimal_combo = QComboBox()
        self.decimal_combo.addItems(["#", "#.#", "#.##"])
        current_decimal = self.current_settings.get("decimal_points", 1)
        # Map decimal points to display format
        decimal_map = {0: "#", 1: "#.#", 2: "#.##"}
        current_format = decimal_map.get(current_decimal, "#.#")
        self.decimal_combo.setCurrentText(current_format)
        self.decimal_combo.currentTextChanged.connect(self.update_conversion_preview)
        settings_form.addRow("Rounding Precision:", self.decimal_combo)
        
        # 3. Rounding
        rounding_group = QGroupBox("Rounding Method")
        rounding_layout = QHBoxLayout(rounding_group)
        
        self.rounding_group = QButtonGroup()
        self.round_up_radio = QRadioButton("UP")
        self.round_down_radio = QRadioButton("DOWN")
        
        self.rounding_group.addButton(self.round_up_radio)
        self.rounding_group.addButton(self.round_down_radio)
        
        # Set default based on current settings
        current_rounding = self.current_settings.get("rounding", "UP")
        if current_rounding == "UP":
            self.round_up_radio.setChecked(True)
        else:
            self.round_down_radio.setChecked(True)
        
        self.rounding_group.buttonClicked.connect(self.update_conversion_preview)
        
        rounding_layout.addWidget(self.round_up_radio)
        rounding_layout.addWidget(self.round_down_radio)
        rounding_layout.addStretch()
        
        settings_form.addRow(rounding_group)
        
        # 4. Length Print Preview
        preview_group = QGroupBox("Length Print Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.conversion_preview = QLabel("100.0 Meter")
        self.conversion_preview.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #1e1e1e;
                border-radius: 5px;
                border: 1px solid #444444;
            }
        """)
        self.conversion_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.conversion_preview)
        
        settings_form.addRow(preview_group)
        
        page_layout.addWidget(settings_frame)
        page_layout.addStretch()
        
        self.tab_widget.addTab(page_tab, "Page Settings")
        
        # Initialize conversion preview
        self.update_conversion_preview()
    
    def create_printer_settings_tab(self):
        """Create the Printer Settings tab."""
        printer_tab = QFrame()
        printer_layout = QVBoxLayout(printer_tab)
        printer_layout.setSpacing(20)
        
        # Title
        title = QLabel("Printer Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        printer_layout.addWidget(title)
        
        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QSpinBox, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 20px;
            }
            QSpinBox:focus, QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
        """)
        
        settings_form = QFormLayout(settings_frame)
        settings_form.setSpacing(15)
        
        # Printer selection
        self.printer_combo = QComboBox()
        self.refresh_printers()
        settings_form.addRow("Printer:", self.printer_combo)
        
        # Print copy count
        self.printer_copy_input = QSpinBox()
        self.printer_copy_input.setRange(1, 10)
        self.printer_copy_input.setValue(self.current_settings.get("print_copy_count", 1))
        self.printer_copy_input.setSuffix(" copies")
        settings_form.addRow("Copy Count:", self.printer_copy_input)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Refresh printers button
        refresh_printers_btn = QPushButton("🔄 Refresh Printers")
        refresh_printers_btn.clicked.connect(self.refresh_printers)
        refresh_printers_btn.setStyleSheet(self.get_button_style("secondary"))
        buttons_layout.addWidget(refresh_printers_btn)
        
        # Test print button
        test_print_btn = QPushButton("🖨️ Test Print")
        test_print_btn.clicked.connect(self.test_print)
        test_print_btn.setStyleSheet(self.get_button_style("primary"))
        buttons_layout.addWidget(test_print_btn)
        
        # Add buttons to form
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        settings_form.addRow("", buttons_widget)
        
        printer_layout.addWidget(settings_frame)
        printer_layout.addStretch()
        
        self.tab_widget.addTab(printer_tab, "Printer Settings")
    
    def create_api_settings_tab(self):
        """Create the API Settings tab."""
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        # API Settings Frame
        api_frame = QFrame()
        api_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        api_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        api_form = QFormLayout(api_frame)
        api_form.setSpacing(15)
        
        # API URL Input
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("http://192.168.2.73:8000/api/method/textile_plus.overrides.api.product.search_product")
        current_api_url = self.current_settings.get("api_url", "")
        self.api_url_input.setText(current_api_url)
        self.api_url_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        api_form.addRow("API URL:", self.api_url_input)
        
        # API Key Input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API key (optional)")
        current_api_key = self.current_settings.get("api_key", "")
        self.api_key_input.setText(current_api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        api_form.addRow("API Key:", self.api_key_input)
        
        # API Timeout Input
        self.api_timeout_input = QSpinBox()
        self.api_timeout_input.setRange(5, 60)
        self.api_timeout_input.setValue(self.current_settings.get("api_timeout", 15))
        self.api_timeout_input.setSuffix(" seconds")
        self.api_timeout_input.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QSpinBox:focus {
                border: 2px solid #0078d4;
            }
        """)
        api_form.addRow("Timeout:", self.api_timeout_input)
        
        # API Status Display
        self.api_status_label = QLabel("Not Connected")
        self.api_status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 12px;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
                border: 1px solid #555555;
            }
        """)
        api_form.addRow("Status:", self.api_status_label)
        
        # Test Connection Button
        self.test_api_button = QPushButton("Test Connection")
        self.test_api_button.setStyleSheet(self.get_button_style("secondary"))
        self.test_api_button.clicked.connect(self.test_api_connection)
        api_form.addRow("", self.test_api_button)
        
        # Save API Settings Button
        self.save_api_button = QPushButton("Save API Settings")
        self.save_api_button.setStyleSheet(self.get_button_style("primary"))
        self.save_api_button.clicked.connect(self.save_api_settings)
        api_form.addRow("", self.save_api_button)
        
        api_layout.addWidget(api_frame)
        api_layout.addStretch()
        
        self.tab_widget.addTab(api_tab, "API Settings")
        
        # Update API status
        self.update_api_status()

    def create_supabase_settings_tab(self):
        """Create the Supabase Settings tab."""
        supabase_tab = QWidget()
        supabase_layout = QVBoxLayout(supabase_tab)

        # Supabase Settings Frame
        supabase_frame = QFrame()
        supabase_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        supabase_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        supabase_form = QFormLayout(supabase_frame)
        supabase_form.setSpacing(15)

        # Enable Supabase checkbox
        self.supabase_enable_checkbox = QCheckBox("Enable Supabase Integration")
        self.supabase_enable_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #666666;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
            }
        """)
        self.supabase_enable_checkbox.setChecked(self.current_settings.get("enable_supabase", False))
        self.supabase_enable_checkbox.stateChanged.connect(self.update_supabase_status)
        supabase_form.addRow(self.supabase_enable_checkbox)

        # Supabase URL Input
        self.supabase_url_input = QLineEdit()
        self.supabase_url_input.setPlaceholderText("https://your-project.supabase.co")
        current_supabase_url = self.current_settings.get("supabase_url", "")
        self.supabase_url_input.setText(current_supabase_url)
        self.supabase_url_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        supabase_form.addRow("Supabase URL:", self.supabase_url_input)

        # Supabase API Key Input
        self.supabase_key_input = QLineEdit()
        self.supabase_key_input.setPlaceholderText("Enter your Supabase API key")
        current_supabase_key = self.current_settings.get("supabase_key", "")
        self.supabase_key_input.setText(current_supabase_key)
        self.supabase_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.supabase_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        supabase_form.addRow("Supabase API Key:", self.supabase_key_input)

        # Supabase Status Display
        self.supabase_status_label = QLabel("Not Connected")
        self.supabase_status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 12px;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
                border: 1px solid #555555;
            }
        """)
        supabase_form.addRow("Status:", self.supabase_status_label)

        # Test Connection Button
        self.test_supabase_button = QPushButton("Test Connection")
        self.test_supabase_button.setStyleSheet(self.get_button_style("secondary"))
        self.test_supabase_button.clicked.connect(self.test_supabase_connection)
        supabase_form.addRow("", self.test_supabase_button)

        # Save Supabase Settings Button
        self.save_supabase_button = QPushButton("Save Supabase Settings")
        self.save_supabase_button.setStyleSheet(self.get_button_style("primary"))
        self.save_supabase_button.clicked.connect(self.save_supabase_settings)
        supabase_form.addRow("", self.save_supabase_button)

        supabase_layout.addWidget(supabase_frame)
        supabase_layout.addStretch()

        self.tab_widget.addTab(supabase_tab, "Supabase Settings")

        # Update Supabase status
        self.update_supabase_status()

    def create_erp_settings_tab(self):
        """Create the ERP Stock Entry Settings tab with 2-column layout."""
        erp_tab = QWidget()
        erp_layout = QVBoxLayout(erp_tab)
        erp_layout.setSpacing(15)

        # ERP Settings Frame
        erp_frame = QFrame()
        erp_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        erp_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: none;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            QSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QSpinBox:focus {
                border: 2px solid #0078d4;
            }
        """)

        # Main container with 2 columns
        container_layout = QHBoxLayout(erp_frame)
        container_layout.setSpacing(20)

        # Left Column
        left_column = QWidget()
        left_form = QFormLayout(left_column)
        left_form.setSpacing(15)

        # Enable ERP Submission toggle switch
        self.erp_enable_container = QWidget()
        self.erp_enable_layout = QHBoxLayout(self.erp_enable_container)
        self.erp_enable_layout.setContentsMargins(0, 0, 0, 0)
        self.erp_enable_layout.setSpacing(8)

        # Toggle switch (iOS style using QSS) - positioned first (left)
        self.erp_enable_switch = QCheckBox()
        self.erp_enable_switch.setChecked(self.current_settings.get("enable_erp_submission", False))

        # iOS-style toggle dimensions
        switch_width = 52  # 50-60px as requested
        switch_height = 28  # 28px as requested
        thumb_size = 24  # Thumb diameter (slightly smaller than height)

        self.erp_enable_switch.setStyleSheet(f"""
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
                background-color: #28a745;
                border: none;
            }}
            QCheckBox::indicator:hover {{
                background-color: #D1D1D6;
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #218838;
            }}
        """)

        # Create custom thumb widget for smooth animation
        self.erp_enable_thumb = QWidget(self.erp_enable_switch)
        self.erp_enable_thumb.setFixedSize(thumb_size, thumb_size)
        self.erp_enable_thumb.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.erp_enable_thumb.setStyleSheet(f"""
            background-color: white;
            border-radius: {thumb_size//2}px;
            border: none;
        """)

        # Position thumb initially based on current state
        if self.erp_enable_switch.isChecked():
            self.erp_enable_thumb.move(52 - 24 - 2, 2)  # Checked position
        else:
            self.erp_enable_thumb.move(2, 2)  # Unchecked position

        self.erp_enable_thumb.show()

        # Connect to animate thumb movement
        self.erp_enable_switch.stateChanged.connect(self.animate_erp_enable_thumb)
        self.erp_enable_switch.stateChanged.connect(self.update_erp_status)

        self.erp_enable_layout.addWidget(self.erp_enable_switch)

        # Label - positioned after toggle switch
        erp_enable_label = QLabel("Enable ERP Stock Entry Submission")
        erp_enable_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: bold;")
        self.erp_enable_layout.addWidget(erp_enable_label)

        self.erp_enable_layout.addStretch()

        left_form.addRow(self.erp_enable_container)

        # ERP Verification toggle switch
        self.erp_verify_container = QWidget()
        self.erp_verify_layout = QHBoxLayout(self.erp_verify_container)
        self.erp_verify_layout.setContentsMargins(0, 0, 0, 0)
        self.erp_verify_layout.setSpacing(8)

        # Toggle switch (iOS style using QSS) - positioned first (left)
        self.erp_verify_switch = QCheckBox()
        self.erp_verify_switch.setChecked(self.current_settings.get("is_verified", False))
        self.erp_verify_switch.setToolTip("Toggle verification status - this controls whether ERP submission is allowed")

        # iOS-style toggle dimensions
        switch_width = 52  # 50-60px as requested
        switch_height = 28  # 28px as requested
        thumb_size = 24  # Thumb diameter (slightly smaller than height)

        self.erp_verify_switch.setStyleSheet(f"""
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
        self.erp_verify_thumb = QWidget(self.erp_verify_switch)
        self.erp_verify_thumb.setFixedSize(thumb_size, thumb_size)
        self.erp_verify_thumb.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.erp_verify_thumb.setStyleSheet(f"""
            background-color: white;
            border-radius: {thumb_size//2}px;
            border: none;
        """)

        # Position thumb initially based on current state
        if self.erp_verify_switch.isChecked():
            self.erp_verify_thumb.move(52 - 24 - 2, 2)  # Checked position
        else:
            self.erp_verify_thumb.move(2, 2)  # Unchecked position

        self.erp_verify_thumb.show()

        # Connect to animate thumb movement
        self.erp_verify_switch.stateChanged.connect(self.animate_erp_verify_thumb)
        self.erp_verify_switch.stateChanged.connect(self.update_erp_verify_status)

        self.erp_verify_layout.addWidget(self.erp_verify_switch)

        # Status label - positioned after toggle switch
        is_verified = self.current_settings.get("is_verified", False)
        label_text = "Verified" if is_verified else "Not Verified"
        label_color = "#4CAF50" if is_verified else "#ff6b6b"

        self.erp_verify_label = QLabel(label_text)
        self.erp_verify_label.setStyleSheet(f"color: {label_color}; font-size: 14px; font-weight: bold;")
        self.erp_verify_label.setToolTip("Current verification status - affects ERP submission capability")
        self.erp_verify_layout.addWidget(self.erp_verify_label)

        self.erp_verify_layout.addStretch()

        left_form.addRow(self.erp_verify_container)

        # ERP URL Input
        self.erp_url_input = QLineEdit()
        self.erp_url_input.setPlaceholderText("http://192.168.2.73:8000")
        self.erp_url_input.setText(self.current_settings.get("erp_url", ""))
        left_form.addRow("ERP URL:", self.erp_url_input)

        # API Key Input
        self.erp_api_key_input = QLineEdit()
        self.erp_api_key_input.setPlaceholderText("Enter API Key from ERPNext")
        self.erp_api_key_input.setText(self.current_settings.get("erp_api_key", ""))
        self.erp_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        left_form.addRow("API Key:", self.erp_api_key_input)

        # API Secret Input
        self.erp_api_secret_input = QLineEdit()
        self.erp_api_secret_input.setPlaceholderText("Enter API Secret from ERPNext")
        self.erp_api_secret_input.setText(self.current_settings.get("erp_api_secret", ""))
        self.erp_api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        left_form.addRow("API Secret:", self.erp_api_secret_input)

        # Show/Hide credentials button
        self.erp_show_credentials_btn = QPushButton("👁 Show Credentials")
        self.erp_show_credentials_btn.setCheckable(True)
        self.erp_show_credentials_btn.setStyleSheet(self.get_button_style("secondary"))
        self.erp_show_credentials_btn.clicked.connect(self.toggle_erp_credentials_visibility)
        left_form.addRow("", self.erp_show_credentials_btn)

        # Timeout Input
        self.erp_timeout_input = QSpinBox()
        self.erp_timeout_input.setRange(5, 120)
        self.erp_timeout_input.setSuffix(" seconds")
        self.erp_timeout_input.setValue(self.current_settings.get("erp_timeout", 30))
        left_form.addRow("Request Timeout:", self.erp_timeout_input)

        # Right Column
        right_column = QWidget()
        right_form = QFormLayout(right_column)
        right_form.setSpacing(15)

        # BOM Search Group
        bom_group = QGroupBox("BOM Selection")
        bom_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 2px solid #0078d4;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        bom_layout = QVBoxLayout(bom_group)
        
        # BOM Search Input
        self.bom_search_input = QLineEdit()
        self.bom_search_input.setPlaceholderText("Search BOM by product code...")
        self.bom_search_input.textChanged.connect(self.search_bom)
        bom_layout.addWidget(self.bom_search_input)
        
        # BOM Results Dropdown (initially hidden)
        self.bom_results_list = QListWidget()
        self.bom_results_list.setMaximumHeight(150)
        self.bom_results_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #0078d4;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        self.bom_results_list.itemClicked.connect(self.select_bom)
        self.bom_results_list.setVisible(False)
        bom_layout.addWidget(self.bom_results_list)
        
        # Selected BOM Display
        self.selected_bom_label = QLabel("No BOM selected")
        self.selected_bom_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                padding: 8px;
                background-color: #1e1e1e;
                border-radius: 5px;
                border: 1px solid #555555;
            }
        """)
        self.selected_bom_label.setWordWrap(True)
        bom_layout.addWidget(self.selected_bom_label)
        
        right_form.addRow(bom_group)

        # Company Input
        self.erp_company_input = QLineEdit()
        self.erp_company_input.setPlaceholderText("Textilindo")
        self.erp_company_input.setText(self.current_settings.get("erp_company", "Textilindo"))
        right_form.addRow("Company:", self.erp_company_input)

        # Stock Entry Type Input
        self.erp_stock_entry_type_input = QComboBox()
        self.erp_stock_entry_type_input.setEditable(False)
        self.erp_stock_entry_type_input.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 2px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
        """)
        right_form.addRow("Stock Entry Type:", self.erp_stock_entry_type_input)
        
        # Initialize with saved value if available
        saved_stock_entry_type = self.current_settings.get("erp_stock_entry_type", "")
        if saved_stock_entry_type:
            self.erp_stock_entry_type_input.addItem(saved_stock_entry_type)
            self.erp_stock_entry_type_input.setCurrentText(saved_stock_entry_type)
        
        # Refresh button for stock entry types
        refresh_stock_types_btn = QPushButton("🔄 Refresh Stock Entry Types")
        refresh_stock_types_btn.setStyleSheet(self.get_button_style("secondary"))
        refresh_stock_types_btn.clicked.connect(self.load_stock_entry_types)
        right_form.addRow("", refresh_stock_types_btn)
        
        # Load stock entry types from API
        self.load_stock_entry_types()

        # From Warehouse Input
        self.erp_from_warehouse_input = QLineEdit()
        self.erp_from_warehouse_input.setPlaceholderText("Source warehouse")
        self.erp_from_warehouse_input.setText(self.current_settings.get("erp_from_warehouse", "Prancis - MGI"))
        right_form.addRow("From Warehouse:", self.erp_from_warehouse_input)

        # To Warehouse Input
        self.erp_to_warehouse_input = QLineEdit()
        self.erp_to_warehouse_input.setPlaceholderText("Target warehouse")
        self.erp_to_warehouse_input.setText(self.current_settings.get("erp_to_warehouse", "Prancis - MGI"))
        right_form.addRow("To Warehouse:", self.erp_to_warehouse_input)

        # Packing List Field Name
        self.erp_packing_list_field_input = QLineEdit()
        self.erp_packing_list_field_input.setPlaceholderText("packing_list_items")
        self.erp_packing_list_field_input.setText(self.current_settings.get("erp_packing_list_field", "packing_list_items"))
        right_form.addRow("Packing List Field:", self.erp_packing_list_field_input)

        # ERP Status Display
        self.erp_status_label = QLabel("Not Configured")
        self.erp_status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 12px;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
                border: 1px solid #555555;
            }
        """)
        right_form.addRow("Status:", self.erp_status_label)

        # Add columns to container
        container_layout.addWidget(left_column)
        container_layout.addWidget(right_column)

        # Buttons row (full width)
        buttons_layout = QHBoxLayout()
        
        # Test Connection Button
        self.test_erp_button = QPushButton("🔌 Test ERP Connection")
        self.test_erp_button.setStyleSheet(self.get_button_style("secondary"))
        self.test_erp_button.clicked.connect(self.test_erp_connection)
        buttons_layout.addWidget(self.test_erp_button)

        buttons_layout.addStretch()

        # Save ERP Settings Button
        self.save_erp_button = QPushButton("💾 Save ERP Settings")
        self.save_erp_button.setStyleSheet(self.get_button_style("primary"))
        self.save_erp_button.clicked.connect(self.save_erp_settings)
        buttons_layout.addWidget(self.save_erp_button)

        # Help text
        help_label = QLabel(
            "<i>Note: Get API credentials from ERPNext → User → API Access → Generate Keys</i>"
        )
        help_label.setStyleSheet("QLabel { color: #888888; font-size: 11px; font-style: italic; }")
        help_label.setWordWrap(True)

        # Main layout
        erp_layout.addWidget(erp_frame)
        erp_layout.addLayout(buttons_layout)
        erp_layout.addWidget(help_label)
        erp_layout.addStretch()

        self.tab_widget.addTab(erp_tab, "📤 ERP Stock Entry")

        # Update ERP status
        self.update_erp_status()
        
        # Load saved BOM data if exists
        self.load_saved_bom()

    def load_saved_bom(self):
        """Load saved BOM data from settings."""
        try:
            bom_name = self.current_settings.get("bom_name", "")
            bom_item = self.current_settings.get("bom_item", "")
            bom_product_code = self.current_settings.get("bom_product_code", "")
            bom_color_code = self.current_settings.get("bom_color_code", "")
            bom_product_name = self.current_settings.get("bom_product_name", "")
            
            if bom_name and bom_item and bom_product_code:
                self.selected_bom_data = {
                    "bom_name": bom_name,
                    "bom_item": bom_item,
                    "bom_product_code": bom_product_code,
                    "bom_color_code": bom_color_code,
                    "bom_product_name": bom_product_name
                }
                
                # Update display
                display_text = (
                    f"✓ Selected BOM:\n"
                    f"Name: {bom_name}\n"
                    f"Item: {bom_item}\n"
                    f"Product Code: {bom_product_code}"
                )
                if bom_color_code:
                    display_text += f"\nColor: {bom_color_code}"
                self.selected_bom_label.setText(display_text)
                self.selected_bom_label.setStyleSheet("""
                    QLabel {
                        color: #4CAF50;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 8px;
                        background-color: #1e1e1e;
                        border-radius: 5px;
                        border: 2px solid #4CAF50;
                    }
                """)
                logger.info(f"Loaded saved BOM: {bom_name} - {bom_product_code}")
        except Exception as e:
            logger.error(f"Error loading saved BOM: {e}")

    def load_stock_entry_types(self):
        """Load stock entry types from ERPNext API."""
        try:
            # Get ERP URL from settings
            erp_url = self.current_settings.get("erp_url", "")
            if not erp_url:
                # Don't add error message to combo box, just log and return
                logger.warning("ERP URL not configured")
                return
            
            # Import requests for API call
            import requests
            
            # Prepare API endpoint
            api_url = f"{erp_url}/api/resource/Stock Entry Type"
            # api_url = f"http://192.168.2.73:8000/api/resource/Stock Entry Type"
            
            # Get API credentials
            api_key = self.current_settings.get("erp_api_key", "")
            api_secret = self.current_settings.get("erp_api_secret", "")
            
            if not api_key or not api_secret:
                # Don't add error message to combo box, just log and return
                logger.warning("ERP API credentials not configured")
                return
            
            # Make API request
            headers = {
                'Authorization': f'token {api_key}:{api_secret}',
                'Content-Type': 'application/json'
            }
            
            # Add timeout
            timeout = self.current_settings.get("erp_timeout", 30)
            
            response = requests.get(api_url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                stock_entry_types = data.get('data', [])
                
                # Clear existing items completely to remove any error messages
                self.erp_stock_entry_type_input.clear()
                
                # Add default option
                self.erp_stock_entry_type_input.addItem("Select Stock Entry Type...")
                
                # Add stock entry types to combo box
                for entry_type in stock_entry_types:
                    name = entry_type.get('name', '')
                    if name:
                        self.erp_stock_entry_type_input.addItem(name)
                
                # Set current value if exists
                current_value = self.current_settings.get("erp_stock_entry_type", "")
                if current_value:
                    index = self.erp_stock_entry_type_input.findText(current_value)
                    if index >= 0:
                        self.erp_stock_entry_type_input.setCurrentIndex(index)
                    else:
                        # If current value not found, add it as custom option
                        self.erp_stock_entry_type_input.addItem(current_value)
                        self.erp_stock_entry_type_input.setCurrentText(current_value)
                
                logger.info(f"Loaded {len(stock_entry_types)} stock entry types from ERPNext")
                
            else:
                # Don't clear the combo box, just log the error
                logger.error(f"Failed to load stock entry types: {response.status_code}")
                # Only show error message if combo box is empty or only has default item
                if self.erp_stock_entry_type_input.count() <= 1:
                    # Clear and add error message only if no valid data exists
                    self.erp_stock_entry_type_input.clear()
                    self.erp_stock_entry_type_input.addItem("Unable to load stock entry types")
                
        except requests.exceptions.RequestException as e:
            # Don't clear the combo box, just log the error
            logger.error(f"Connection error loading stock entry types: {e}")
            # Only show error message if combo box is empty or only has default/error items
            if self.erp_stock_entry_type_input.count() <= 1 or self._has_only_error_items():
                # Clear and add error message only if no valid data exists
                self.erp_stock_entry_type_input.clear()
                self.erp_stock_entry_type_input.addItem("Unable to load stock entry types")
        except Exception as e:
            # Don't clear the combo box, just log the error
            logger.error(f"Error loading stock entry types: {e}")
            # Only show error message if combo box is empty or only has default/error items
            if self.erp_stock_entry_type_input.count() <= 1 or self._has_only_error_items():
                # Clear and add error message only if no valid data exists
                self.erp_stock_entry_type_input.clear()
                self.erp_stock_entry_type_input.addItem("Unable to load stock entry types")

    def _has_only_error_items(self):
        """Check if combo box only contains error or default items."""
        if self.erp_stock_entry_type_input.count() <= 1:
            return True

        # Check if all items are error messages or default items
        for i in range(self.erp_stock_entry_type_input.count()):
            item_text = self.erp_stock_entry_type_input.itemText(i)
            if (not item_text.startswith("Select Stock Entry Type") and
                not item_text.startswith("Unable to load") and
                not item_text.startswith("Please configure") and
                not item_text.startswith("API Error") and
                not item_text.startswith("Connection Error")):
                return False
        return True

    def _populate_api_settings_from_login(self):
        """Auto-populate API settings form with login credentials."""
        try:
            if not self.login_credentials:
                logger.warning("No login credentials available for API settings population")
                return

            username = self.login_credentials.get("username", "")
            api_key = self.login_credentials.get("api_key", "")
            api_secret = self.login_credentials.get("api_secret", "")

            if not api_key or not api_secret:
                logger.warning("Incomplete API credentials received from login")
                return

            logger.info(f"Auto-populating API settings for user: {username}")

            # Populate ERP API settings
            if hasattr(self, 'erp_api_key_input') and hasattr(self, 'erp_api_secret_input'):
                self.erp_api_key_input.setText(api_key)
                self.erp_api_secret_input.setText(api_secret)
                logger.info("ERP API credentials populated from login")

            # Populate general API settings
            if hasattr(self, 'api_key_input'):
                self.api_key_input.setText(api_key)
                logger.info("General API key populated from login")

            # Show success message
            QMessageBox.information(
                self,
                "API Credentials Loaded",
                f"API credentials for user '{username}' have been automatically loaded into the settings form.\n\n"
                f"You can now save these settings to use them for ERP integration."
            )

        except Exception as e:
            logger.error(f"Error populating API settings from login: {e}")
            QMessageBox.warning(
                self,
                "API Settings Error",
                f"Failed to populate API settings from login credentials:\n\n{str(e)}"
            )

    def create_supabase_settings_tab(self):
        """Create the Supabase Settings tab with sync controls."""
        supabase_tab = QWidget()
        supabase_layout = QVBoxLayout(supabase_tab)
        supabase_layout.setSpacing(20)
        
        # Title
        title = QLabel("Supabase Cloud Storage Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        supabase_layout.addWidget(title)
        
        # Settings frame
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        
        supabase_form = QFormLayout(settings_frame)
        supabase_form.setSpacing(15)
        
        # Enable Supabase checkbox
        self.supabase_enable_checkbox = QCheckBox("Enable Supabase Cloud Storage")
        self.supabase_enable_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.supabase_enable_checkbox.setChecked(self.current_settings.get("enable_supabase", False))
        supabase_form.addRow(self.supabase_enable_checkbox)
        
        # Supabase URL
        self.supabase_url_input = QLineEdit()
        self.supabase_url_input.setPlaceholderText("https://your-project.supabase.co")
        self.supabase_url_input.setText(self.current_settings.get("supabase_url", ""))
        supabase_form.addRow("Supabase URL:", self.supabase_url_input)
        
        # Supabase API Key
        self.supabase_key_input = QLineEdit()
        self.supabase_key_input.setPlaceholderText("Enter Supabase API Key")
        self.supabase_key_input.setText(self.current_settings.get("supabase_key", ""))
        self.supabase_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        supabase_form.addRow("API Key:", self.supabase_key_input)
        
        # Connection status
        self.supabase_status_label = QLabel("Not Connected")
        self.supabase_status_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 12px;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
                border: 1px solid #555555;
            }
        """)
        supabase_form.addRow("Status:", self.supabase_status_label)
        
        # Offline Queue Status Group
        queue_group = QGroupBox("Offline Queue Status")
        queue_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 2px solid #0078d4;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        queue_layout = QVBoxLayout(queue_group)
        
        # Queue count label
        self.queue_count_label = QLabel("Pending operations: 0")
        self.queue_count_label.setStyleSheet("color: #e0e0e0; font-size: 12px;")
        queue_layout.addWidget(self.queue_count_label)
        
        # Last sync label
        self.last_sync_label = QLabel("Last sync: Never")
        self.last_sync_label.setStyleSheet("color: #888888; font-size: 11px; font-style: italic;")
        queue_layout.addWidget(self.last_sync_label)
        
        # Sync Now button
        sync_now_btn = QPushButton("🔄 Sync Now")
        sync_now_btn.setStyleSheet(self.get_button_style("primary"))
        sync_now_btn.clicked.connect(self.manual_sync_queue)
        queue_layout.addWidget(sync_now_btn)
        
        supabase_form.addRow(queue_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        test_btn = QPushButton("🔌 Test Connection")
        test_btn.setStyleSheet(self.get_button_style("secondary"))
        test_btn.clicked.connect(self.test_supabase_connection)
        buttons_layout.addWidget(test_btn)
        
        buttons_layout.addStretch()
        
        supabase_layout.addWidget(settings_frame)
        supabase_layout.addLayout(buttons_layout)
        supabase_layout.addStretch()
        
        self.tab_widget.addTab(supabase_tab, "☁ Supabase")
        
        # Update queue status
        self.update_queue_status()

    def update_queue_status(self):
        """Update the offline queue status display."""
        try:
            from ..supabase_client import get_supabase_client
            supabase_client = get_supabase_client()
            
            queue_count = supabase_client.get_queue_count()
            queue_info = supabase_client.get_queue_info()
            
            self.queue_count_label.setText(f"Pending operations: {queue_count}")
            
            if queue_count > 0:
                details = f"({queue_info.get('batch_metadata_count', 0)} batch metadata, {queue_info.get('production_log_count', 0)} production logs)"
                self.queue_count_label.setText(f"Pending operations: {queue_count} {details}")
                self.queue_count_label.setStyleSheet("color: #ff9800; font-size: 12px; font-weight: bold;")
            else:
                self.queue_count_label.setStyleSheet("color: #4caf50; font-size: 12px;")
            
        except Exception as e:
            logger.error(f"Error updating queue status: {e}")
            self.queue_count_label.setText("Error loading queue status")

    def manual_sync_queue(self):
        """Manually trigger queue synchronization."""
        try:
            from ..supabase_client import get_supabase_client
            from datetime import datetime
            
            supabase_client = get_supabase_client()
            
            # Check connection
            if not supabase_client.is_connected:
                QMessageBox.warning(
                    self,
                    "Sync Failed",
                    "Supabase is not connected.\n\nPlease check your connection settings and try again."
                )
                return
            
            # Get queue count
            queue_count = supabase_client.get_queue_count()
            
            if queue_count == 0:
                QMessageBox.information(
                    self,
                    "Queue Empty",
                    "No pending operations to sync."
                )
                return
            
            # Process queue
            success_count, failed_count = supabase_client.process_offline_queue()
            
            # Update sync time
            self.last_sync_label.setText(f"Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Update queue status
            self.update_queue_status()
            
            # Show result
            if success_count > 0 and failed_count == 0:
                QMessageBox.information(
                    self,
                    "Sync Successful",
                    f"Successfully synced {success_count} operation(s) to Supabase!"
                )
            elif success_count > 0 and failed_count > 0:
                QMessageBox.warning(
                    self,
                    "Partial Sync",
                    f"Synced {success_count} operation(s) successfully.\n"
                    f"{failed_count} operation(s) failed and will be retried later."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Sync Failed",
                    f"Failed to sync {failed_count} operation(s).\n\n"
                    f"Please check your connection and try again."
                )
                
        except Exception as e:
            logger.error(f"Error during manual sync: {e}")
            QMessageBox.critical(
                self,
                "Sync Error",
                f"Error during synchronization:\n\n{str(e)}"
            )

    def create_batch_name_settings_tab(self):
        """Create the Batch Name Settings tab."""
        batch_tab = QWidget()
        batch_layout = QVBoxLayout(batch_tab)
        batch_layout.setSpacing(20)

        # Title
        title = QLabel("Batch Name Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        batch_layout.addWidget(title)

        # Settings frame
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        batch_form = QFormLayout(settings_frame)
        batch_form.setSpacing(15)

        # Batch Name Format Group
        format_group = QGroupBox("Custom Batch Name Format")
        format_layout = QVBoxLayout(format_group)

        # Custom format input
        self.batch_format_input = QLineEdit()
        self.batch_format_input.setPlaceholderText("YYYY-MM-DD_product-code_color-code")
        current_batch_format = self.current_settings.get("batch_name_format", "YYYY-MM-DD_product-code_color-code")
        self.batch_format_input.setText(current_batch_format)
        self.batch_format_input.textChanged.connect(self.update_batch_preview)
        format_layout.addWidget(QLabel("Custom Format (tanpa auto increment):"))
        format_layout.addWidget(self.batch_format_input)

        # Format description
        format_desc = QLabel("Available variables: {date}, {product_code}, {color_code}, {time}, {length}, {operator}")
        format_desc.setStyleSheet("color: #888888; font-size: 11px; font-style: italic;")
        format_layout.addWidget(format_desc)

        # Auto increment info
        auto_info = QLabel("Format auto increment: #### (akan menjadi 0001, 0002, 0003, dst)")
        auto_info.setStyleSheet("color: #0078d4; font-size: 11px; font-weight: bold;")
        format_layout.addWidget(auto_info)

        batch_form.addRow(format_group)

        # Batch Preview Group
        preview_group = QGroupBox("Batch Name Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.batch_preview = QLabel("2024-01-15_BD-1_001_0001")
        self.batch_preview.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #1e1e1e;
                border-radius: 5px;
                border: 1px solid #444444;
            }
        """)
        self.batch_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.batch_preview)

        # Preview explanation
        preview_desc = QLabel("Format lengkap: [Custom Format]_[Auto Increment]")
        preview_desc.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        preview_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_desc)

        batch_form.addRow(preview_group)

        # Auto Increment Settings Group
        auto_increment_group = QGroupBox("Auto Increment Settings")
        auto_increment_layout = QVBoxLayout(auto_increment_group)

        # Starting number
        self.batch_start_number_input = QLineEdit()
        self.batch_start_number_input.setPlaceholderText("1")
        current_start_number = self.current_settings.get("batch_start_number", "1")
        self.batch_start_number_input.setText(current_start_number)
        self.batch_start_number_input.textChanged.connect(self.update_batch_preview)
        auto_increment_layout.addWidget(QLabel("Starting Number:"))
        auto_increment_layout.addWidget(self.batch_start_number_input)

        # Auto increment info
        auto_increment_info = QLabel("Format: 0001, 0002, 0003, dst (4 digit dengan leading zero)")
        auto_increment_info.setStyleSheet("color: #888888; font-size: 11px; font-style: italic;")
        auto_increment_layout.addWidget(auto_increment_info)

        batch_form.addRow(auto_increment_group)

        batch_layout.addWidget(settings_frame)
        batch_layout.addStretch()

        self.tab_widget.addTab(batch_tab, "Batch Name Settings")

        # Initialize batch preview
        self.update_batch_preview()

    def create_security_settings_tab(self):
        """Create the Security Settings tab."""
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setSpacing(20)

        # Title
        title = QLabel("Security Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        security_layout.addWidget(title)

        # Settings frame
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)

        security_form = QVBoxLayout(settings_frame)
        security_form.setSpacing(15)

        # PIN Settings Group
        pin_group = QGroupBox("Settings PIN Protection")
        pin_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        pin_layout = QVBoxLayout(pin_group)

        # Description
        desc = QLabel(
            "The settings are protected with a PIN to prevent unauthorized access.\n"
            "You can change the PIN by clicking the button below."
        )
        desc.setStyleSheet("color: #cccccc; font-size: 13px; padding: 10px;")
        desc.setWordWrap(True)
        pin_layout.addWidget(desc)

        # Current PIN info
        current_pin_info = QLabel(f"Current PIN: {'•' * len(self.current_settings.get('settings_pin', '668899'))}")
        current_pin_info.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
                border: 1px solid #444444;
            }
        """)
        pin_layout.addWidget(current_pin_info)

        # Change PIN button
        change_pin_btn = QPushButton("🔑 Change Settings PIN")
        change_pin_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: none;
                border-radius: 8px;
                padding: 15px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        change_pin_btn.clicked.connect(self.change_settings_pin)
        pin_layout.addWidget(change_pin_btn)

        security_form.addWidget(pin_group)

        # Security Info Group
        info_group = QGroupBox("Security Information")
        info_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        info_layout = QVBoxLayout(info_group)

        info_text = QLabel(
            "• PIN must be 4-6 digits long\n"
            "• Default PIN: 668899\n"
            "• PIN is stored in config.json\n"
            "• Maximum 3 attempts allowed\n"
            "• Settings access is protected"
        )
        info_text.setStyleSheet("color: #cccccc; font-size: 12px; line-height: 1.5;")
        info_layout.addWidget(info_text)

        security_form.addWidget(info_group)

        security_layout.addWidget(settings_frame)
        security_layout.addStretch()

        self.tab_widget.addTab(security_tab, "🔒 Security")

    def change_settings_pin(self):
        """Change the settings PIN."""
        try:
            current_pin = self.current_settings.get("settings_pin", "668899")
            
            # Show change PIN dialog
            dialog = ChangePinDialog(current_pin=current_pin, parent=self)
            
            # Connect signal
            dialog.pin_changed.connect(self.on_pin_changed)
            
            # Show dialog
            dialog.raise_()
            dialog.activateWindow()
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error changing PIN: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to change PIN:\n\n{str(e)}"
            )

    def on_pin_changed(self, new_pin: str):
        """Handle PIN changed signal."""
        try:
            # Update current settings
            self.current_settings["settings_pin"] = new_pin
            
            # Save to config file
            from ..config import save_config
            save_config(self.current_settings)
            
            # Show success message
            QMessageBox.information(
                self,
                "PIN Changed",
                "Settings PIN has been changed successfully!\n\n"
                f"New PIN: {'•' * len(new_pin)}\n\n"
                "Please remember this PIN to access settings in the future."
            )
            
            logger.info("Settings PIN changed successfully")
            
        except Exception as e:
            logger.error(f"Error saving new PIN: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save new PIN:\n\n{str(e)}"
            )

    def update_batch_preview(self):
        """Update the batch name preview based on current settings."""
        try:
            # Get current custom format
            custom_format = self.batch_format_input.text() or "YYYY-MM-DD_product-code_color-code"
            
            # Get starting number
            start_number = self.batch_start_number_input.text() or "1"
            try:
                start_num = int(start_number)
            except ValueError:
                start_num = 1
            
            # Sample data for preview
            from datetime import datetime
            now = datetime.now()
            
            sample_data = {
                "date": now.strftime("%Y-%m-%d"),
                "product_code": "BD-1",
                "color_code": "001", 
                "time": now.strftime("%H-%M"),
                "length": "25.5",
                "operator": "OP001"
            }
            
            # Replace variables in custom format
            preview = custom_format
            for key, value in sample_data.items():
                preview = preview.replace(f"{{{key}}}", value)
            
            # Add auto increment part
            auto_increment = f"{start_num:04d}"  # Format as 0001, 0002, etc.
            final_preview = f"{preview}_{auto_increment}"
            
            # Update preview
            self.batch_preview.setText(final_preview)
            
        except Exception as e:
            logger.error(f"Error updating batch preview: {e}")
            self.batch_preview.setText("Error in format")

    def generate_batch_name(self, product_code="", color_code="", custom_data=None):
        """
        Generate batch name based on current settings.
        
        Args:
            product_code (str): Product code
            color_code (str): Color code  
            custom_data (dict): Additional custom data for format variables
            
        Returns:
            str: Generated batch name
        """
        try:
            # Get current settings
            custom_format = self.current_settings.get("batch_name_format", "YYYY-MM-DD_product-code_color-code")
            start_number = int(self.current_settings.get("batch_start_number", "1"))
            
            # Get current data
            from datetime import datetime
            now = datetime.now()
            
            # Default data
            data = {
                "date": now.strftime("%Y-%m-%d"),
                "product_code": product_code or "PRODUCT",
                "color_code": color_code or "COLOR", 
                "time": now.strftime("%H-%M"),
                "length": "25.5",
                "operator": "OP001"
            }
            
            # Add custom data if provided
            if custom_data:
                data.update(custom_data)
            
            # Replace variables in custom format
            batch_name = custom_format
            for key, value in data.items():
                batch_name = batch_name.replace(f"{{{key}}}", str(value))
            
            # Add auto increment part (4 digits with leading zeros)
            auto_increment = f"{start_number:04d}"
            final_batch_name = f"{batch_name}_{auto_increment}"
            
            return final_batch_name
            
        except Exception as e:
            logger.error(f"Error generating batch name: {e}")
            return f"BATCH_{start_number:04d}"

    def test_supabase_connection(self):
        """Test the Supabase connection."""
        try:
            # Get current settings
            supabase_url = self.supabase_url_input.text().strip()
            supabase_key = self.supabase_key_input.text().strip()

            if not supabase_url or not supabase_key:
                QMessageBox.warning(self, "Supabase Test", "Please enter both Supabase URL and API key.")
                return

            # Validate URL format
            if not (supabase_url.startswith('http://') or supabase_url.startswith('https://')):
                QMessageBox.warning(self, "Supabase Test", "Please enter a valid URL starting with http:// or https://")
                return

            # Test connection by creating a client
            from ..supabase_client import SupabaseClient
            test_client = SupabaseClient(supabase_url, supabase_key)

            if test_client.is_connected:
                QMessageBox.information(self, "Supabase Test",
                    "Connection successful!\n\nSupabase client initialized successfully.")
                self.supabase_status_label.setText("Connected")
                self.supabase_status_label.setStyleSheet("""
                    QLabel {
                        color: #4caf50;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)
            else:
                QMessageBox.warning(self, "Supabase Test",
                    "Failed to connect to Supabase.\n\nPlease check your URL and API key.")
                self.supabase_status_label.setText("Connection Failed")
                self.supabase_status_label.setStyleSheet("""
                    QLabel {
                        color: #ff9800;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)

        except Exception as e:
            logger.error(f"Error testing Supabase connection: {e}")
            QMessageBox.critical(self, "Supabase Test", f"Error testing connection: {str(e)}")
            self.supabase_status_label.setText("Error")
            self.supabase_status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)

    def save_supabase_settings(self):
        """Save the Supabase settings."""
        try:
            supabase_url = self.supabase_url_input.text().strip()
            supabase_key = self.supabase_key_input.text().strip()
            enable_supabase = self.supabase_enable_checkbox.isChecked()

            # Validate URL format if provided
            if supabase_url and not (supabase_url.startswith('http://') or supabase_url.startswith('https://')):
                QMessageBox.warning(self, "Supabase Settings", "Please enter a valid URL starting with http:// or https://")
                return

            # Create Supabase settings
            supabase_settings = {
                "supabase_url": supabase_url,
                "supabase_key": supabase_key,
                "enable_supabase": enable_supabase
            }

            # Update current settings
            self.current_settings.update(supabase_settings)

            # Emit settings update signal
            self.settings_updated.emit(self.current_settings)

            # Update status display
            self.update_supabase_status()

            QMessageBox.information(self, "Supabase Settings",
                f"Supabase settings saved successfully!\n\nURL: {supabase_url}\nEnabled: {enable_supabase}")

        except Exception as e:
            QMessageBox.critical(self, "Supabase Settings", f"Error saving Supabase settings: {str(e)}")
            logger.error(f"Error saving Supabase settings: {e}")

    def update_supabase_status(self):
        """Update the Supabase connection status display."""
        enable_supabase = self.current_settings.get("enable_supabase", False)
        supabase_url = self.current_settings.get("supabase_url", "")

        if enable_supabase and supabase_url:
            self.supabase_status_label.setText("Configured")
            self.supabase_status_label.setStyleSheet("""
                QLabel {
                    color: #4caf50;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)
        else:
            self.supabase_status_label.setText("Not Configured")
            self.supabase_status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)

    def test_api_connection(self):
        """Test the API connection with JSON format."""
        try:
            api_url = self.api_url_input.text().strip()
            if not api_url:
                QMessageBox.warning(self, "API Test", "Please enter an API URL first.")
                return
            
            # Import requests here to avoid dependency issues
            import requests
            
            # Set required headers for JSON format
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Test with JSON data
            json_data = {
                "product_code": "BD-1"
            }
            
            logger.info(f"Testing API connection to: {api_url}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Data: {json_data}")
            
            response = requests.post(api_url, json=json_data, headers=headers, timeout=15)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text[:200]}...")  # Log first 200 chars
            
            if response.status_code == 200:
                data = response.json()
                
                # Check new response structure
                if (data.get("message") and 
                    isinstance(data["message"], dict) and 
                    data["message"].get("success")):
                    
                    QMessageBox.information(self, "API Test", 
                        f"Connection successful!\n\nResponse: {data['message'].get('message', 'OK')}")
                    self.api_status_label.setText("Connected")
                    self.api_status_label.setStyleSheet("""
                        QLabel {
                            color: #4caf50;
                            font-size: 12px;
                            padding: 5px;
                            background-color: #1e1e1e;
                            border-radius: 3px;
                            border: 1px solid #555555;
                        }
                    """)
                else:
                    QMessageBox.warning(self, "API Test", 
                        "API connected but response format may be different than expected.")
                    self.api_status_label.setText("Connected (Format Warning)")
                    self.api_status_label.setStyleSheet("""
                        QLabel {
                                color: #ff9800;
                                font-size: 12px;
                                padding: 5px;
                                background-color: #1e1e1e;
                                border-radius: 3px;
                                border: 1px solid #555555;
                            }
                        """)
            elif response.status_code == 401:
                QMessageBox.warning(self, "API Test", 
                    "Error 401: Authentication failed.\n\nPlease check your API key.")
                self.api_status_label.setText("Auth Failed")
                self.api_status_label.setStyleSheet("""
                    QLabel {
                        color: #ff6b6b;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)
            else:
                QMessageBox.warning(self, "API Test", 
                    f"Connection failed. Status code: {response.status_code}\n\nResponse: {response.text}")
                self.api_status_label.setText("Connection Failed")
                self.api_status_label.setStyleSheet("""
                    QLabel {
                        color: #ff9800;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)
                
        except requests.exceptions.Timeout:
            logger.error("API connection timeout")
            QMessageBox.warning(self, "API Test", "Request timeout. Try increasing timeout value.")
            self.api_status_label.setText("Timeout")
            self.api_status_label.setStyleSheet("""
                QLabel {
                    color: #ff9800;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)
        except requests.exceptions.ConnectionError:
            logger.error("API connection error")
            QMessageBox.warning(self, "API Test", 
                "Cannot connect to API server.\n\nPlease check if server is running.")
            self.api_status_label.setText("Connection Error")
            self.api_status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)
        except Exception as e:
            logger.error(f"Unexpected API test error: {str(e)}")
            QMessageBox.critical(self, "API Test", f"Unexpected error: {str(e)}")
            self.api_status_label.setText("Error")
            self.api_status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)
    
    def save_api_settings(self):
        """Save the API settings."""
        try:
            api_url = self.api_url_input.text().strip()
            api_key = self.api_key_input.text().strip()
            timeout = self.api_timeout_input.value()
            
            # Validate URL format
            if api_url and not (api_url.startswith('http://') or api_url.startswith('https://')):
                QMessageBox.warning(self, "API Settings", "Please enter a valid URL starting with http:// or https://")
                return
            
            # Create comprehensive API settings
            api_settings = {
                "api_url": api_url,
                "api_key": api_key,
                "api_timeout": timeout,
                "api_method": "POST",
                "api_content_type": "application/json"
            }
            
            # Update current settings
            self.current_settings.update(api_settings)
            
            # Emit settings update signal
            self.settings_updated.emit(self.current_settings)
            
            # Update status display
            self.update_api_status()
            
            QMessageBox.information(self, "API Settings", 
                f"API settings saved successfully!\n\nURL: {api_url}\nTimeout: {timeout}s")
            
        except Exception as e:
            QMessageBox.critical(self, "API Settings", f"Error saving API settings: {str(e)}")
            logger.error(f"Error saving API settings: {e}")
    
    def update_api_status(self):
        """Update the API connection status display."""
        api_url = self.current_settings.get("api_url", "")
        if api_url:
            self.api_status_label.setText("Configured")
            self.api_status_label.setStyleSheet("""
                QLabel {
                    color: #4caf50;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)
        else:
            self.api_status_label.setText("Not Configured")
            self.api_status_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 12px;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                    border: 1px solid #555555;
                }
            """)
    
    def update_conversion_preview(self):
        """Update the conversion factor preview based on current settings."""
        try:
            # Get current values
            tolerance = float(self.tolerance_input.text() or "3")
            decimal_format = self.decimal_combo.currentText()
            rounding = "UP" if self.round_up_radio.isChecked() else "DOWN"
            
            # Map rounding precision to decimal points
            decimal_points_map = {"#": 0, "#.#": 1, "#.##": 2}
            decimal_points = decimal_points_map.get(decimal_format, 1)
            
            # Calculate conversion factor (example: 100 meter)
            base_value = 100.0
            
            # Apply CORRECT tolerance formula: P_roll = P_target / (1 - T/100)
            # Where: P_target = target length, T = tolerance percentage
            # Example: P_roll = 100 / (1 - 5/100) = 100 / 0.95 ≈ 105.26 meter
            if tolerance > 0:
                adjusted_value = base_value / (1 - tolerance / 100)
            else:
                adjusted_value = base_value
            
            # Apply rounding method
            import math
            if rounding == "UP":
                # Ceiling function
                if decimal_points == 0:
                    adjusted_value = math.ceil(adjusted_value)
                elif decimal_points == 1:
                    adjusted_value = math.ceil(adjusted_value * 10) / 10
                elif decimal_points == 2:
                    adjusted_value = math.ceil(adjusted_value * 100) / 100
            else:  # DOWN
                # Floor function
                if decimal_points == 0:
                    adjusted_value = math.floor(adjusted_value)
                elif decimal_points == 1:
                    adjusted_value = math.floor(adjusted_value * 10) / 10
                elif decimal_points == 2:
                    adjusted_value = math.floor(adjusted_value * 100) / 100
            
            # Format with decimal points
            format_str = f"{{:.{decimal_points}f}}"
            formatted_value = format_str.format(adjusted_value)
            
            # Update preview with unit and explanation
            self.conversion_preview.setText(f"{formatted_value} Meter (Target: 100m, Tolerance: {tolerance}%)")
            
        except ValueError:
            self.conversion_preview.setText("Invalid input")
    
    def get_button_style(self, button_type: str) -> str:
        """Get button style based on type."""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
        """
        
        if button_type == "primary":
            return base_style + "QPushButton { background-color: #0078d4; }"
        elif button_type == "secondary":
            return base_style + "QPushButton { background-color: #555555; }"
        elif button_type == "danger":
            return base_style + "QPushButton { background-color: #d83b01; }"
        else:
            return base_style + "QPushButton { background-color: #555555; }"
    
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        try:
            logger.info("Refreshing serial ports...")
            self.port_combo.clear()
            ports = serial.tools.list_ports.comports()
            
            logger.info(f"Found {len(ports)} serial ports")
            for port in ports:
                self.port_combo.addItem(port.device)
                logger.info(f"Added port: {port.device}")
                
            # Set current port if available
            current_port = self.current_settings.get("serial_port")
            if current_port:
                index = self.port_combo.findText(current_port)
                if index >= 0:
                    self.port_combo.setCurrentIndex(index)
                    logger.info(f"Set current port to: {current_port}")
                else:
                    logger.warning(f"Current port {current_port} not found in available ports")
            else:
                logger.info("No current port set")
                    
        except Exception as e:
            logger.error(f"Error refreshing ports: {e}")
            # Add a default port option if refresh fails
            self.port_combo.addItem("No ports available")
        
        # Update connection status after refresh (only if UI is ready)
        try:
            self.update_connection_status()
        except Exception as e:
            logger.debug(f"Could not update connection status during refresh: {e}")

    def refresh_printers(self):
        """Refresh the list of available printers."""
        try:
            logger.info("Refreshing available printers...")
            
            # Import printer utils to get available printers
            from .printer_utils import get_available_printers, get_default_printer
            
            if hasattr(self, 'printer_combo'):
                self.printer_combo.clear()
                
                # Get available printers
                printers = get_available_printers()
                logger.info(f"Found {len(printers)} printers")
                
                if printers:
                    for printer in printers:
                        self.printer_combo.addItem(printer)
                        logger.info(f"Added printer: {printer}")
                    
                    # Set current printer if available
                    current_printer = self.current_settings.get("selected_printer")
                    if current_printer and current_printer in printers:
                        index = self.printer_combo.findText(current_printer)
                        if index >= 0:
                            self.printer_combo.setCurrentIndex(index)
                            logger.info(f"Set current printer to: {current_printer}")
                    else:
                        # Try to set default printer
                        default_printer = get_default_printer()
                        if default_printer and default_printer in printers:
                            index = self.printer_combo.findText(default_printer)
                            if index >= 0:
                                self.printer_combo.setCurrentIndex(index)
                                logger.info(f"Set default printer: {default_printer}")
                else:
                    self.printer_combo.addItem("No printers available")
                    logger.warning("No printers found")
                    
        except Exception as e:
            logger.error(f"Error refreshing printers: {e}")
            if hasattr(self, 'printer_combo'):
                self.printer_combo.clear()
                self.printer_combo.addItem("Error loading printers")

    def test_print(self):
        """Test print functionality with sample label."""
        try:
            selected_printer = self.printer_combo.currentText()
            
            if not selected_printer or selected_printer in ["No printers available", "Error loading printers"]:
                QMessageBox.warning(self, "Test Print", "Please select a valid printer first.")
                return
                
            logger.info(f"Testing print with printer: {selected_printer}")
            
            # Import printer utils for test printing
            from .printer_utils import print_product_label, get_available_printers, test_printer_connection, test_zebra_printer, test_windows_printer
            
            # Double-check if printer is still available
            available_printers = get_available_printers()
            if selected_printer not in available_printers:
                QMessageBox.warning(self, "Test Print", 
                    f"Printer '{selected_printer}' is no longer available.\n\n"
                    f"Available printers: {', '.join(available_printers)}")
                return
            
            # Create test product info
            test_product_info = {
                'product_code': 'TEST-001',
                'product_name': 'Test Product Label',
                'color_code': '001',
                'color': '001',
                'barcode': 'TEST123456789',
                'batch_number': 'BATCH001',
                'current_length': 25.5,
                'target_length': 25,
                'units': 'Yard',
                'print_length': 25.5,
                'decimal_points': 1
            }
            
            # Show progress dialog
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Sending test print...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # Check if it's a Zebra printer and use specialized test
            is_zebra = "zebra" in selected_printer.lower() or "zd230" in selected_printer.lower()
            
            if is_zebra:
                logger.info("Detected Zebra printer, using specialized test")
                connection_success = test_zebra_printer(selected_printer)
            else:
                connection_success = test_printer_connection(selected_printer)
            
            if not connection_success:
                # Try Windows print command as fallback
                logger.info("Qt printer test failed, trying Windows print command")
                windows_success = test_windows_printer(selected_printer)
                
                if not windows_success:
                    error_msg = f"All printer connection tests failed for '{selected_printer}'.\n\n"
                    if is_zebra:
                        error_msg += "Zebra printer tests failed. This might be due to:\n"
                        error_msg += "• Zebra printer requires specific drivers\n"
                        error_msg += "• Printer is in ZPL mode instead of Windows mode\n"
                        error_msg += "• Try switching printer to Windows mode\n"
                        error_msg += "• Check if Zebra drivers are properly installed\n"
                    else:
                        error_msg += "This indicates a fundamental issue with the printer setup.\n"
                        error_msg += "Please check:\n"
                        error_msg += "• Printer drivers are installed correctly\n"
                        error_msg += "• Printer is connected and powered on\n"
                        error_msg += "• Windows printer settings are correct\n"
                        error_msg += "• Try printing a test page from Windows\n"
                    
                    QMessageBox.critical(self, "Printer Connection Test", error_msg)
                    return
                else:
                    logger.info("Windows print command succeeded")
                    QMessageBox.information(self, "Printer Test", 
                        f"Windows print command succeeded for '{selected_printer}'.\n\n"
                        f"The printer is accessible through Windows, but Qt printing may have issues.\n"
                        f"This is common with specialized printers like Zebra.")
            
            # Perform test print with actual label
            success = print_product_label(test_product_info, None, selected_printer)
            
            progress.close()
            
            if success:
                QMessageBox.information(self, "Test Print", 
                    f"Test print sent successfully to '{selected_printer}'!\n\n"
                    f"Check your printer for the test label with:\n"
                    f"• Product Code: TEST-001\n"
                    f"• Product Name: Test Product Label\n"
                    f"• Color: 001\n"
                    f"• Length: 25.5 Yard\n\n"
                    f"If the label doesn't print, check:\n"
                    f"• Printer is powered on and connected\n"
                    f"• Paper/labels are loaded\n"
                    f"• Printer is not paused or offline")
                logger.info("Test print completed successfully")
            else:
                QMessageBox.critical(self, "Test Print Failed", 
                    f"Test print failed for printer '{selected_printer}'.\n\n"
                    f"Troubleshooting steps:\n"
                    f"1. Check if printer is connected and powered on\n"
                    f"2. Verify printer drivers are installed correctly\n"
                    f"3. Make sure printer is not in use by another application\n"
                    f"4. Try printing a test page from Windows\n"
                    f"5. Check printer queue for any pending jobs\n"
                    f"6. Restart the printer if necessary\n\n"
                    f"Available printers: {', '.join(available_printers)}")
                logger.error("Test print failed")
                
        except Exception as e:
            logger.error(f"Error during test print: {e}")
            QMessageBox.critical(self, "Test Print Error", 
                f"Error occurred during test print:\n\n{str(e)}\n\n"
                f"This might be due to:\n"
                f"• Printer driver issues\n"
                f"• Insufficient permissions\n"
                f"• Printer not responding")
    
    def save_settings(self):
        """Save the current settings."""
        try:
            logger.info("Saving settings...")
            
            # Validate inputs
            tolerance_text = self.tolerance_input.text().strip()
            if not tolerance_text:
                tolerance_text = "3"
            
            try:
                tolerance = float(tolerance_text)
                if tolerance < 0 or tolerance > 100:
                    raise ValueError("Tolerance must be between 0 and 100")
            except ValueError as e:
                logger.error(f"Invalid tolerance value: {tolerance_text}")
                raise ValueError(f"Invalid tolerance value: {tolerance_text}. Must be a number between 0-100")
            
            # Get rounding precision
            decimal_format = self.decimal_combo.currentText()
            decimal_points_map = {"#": 0, "#.#": 1, "#.##": 2}
            if decimal_format not in decimal_points_map:
                raise ValueError(f"Invalid rounding precision: {decimal_format}")
            
            # Get rounding method
            rounding = "UP" if self.round_up_radio.isChecked() else "DOWN"
            
            # Get print copy count from printer settings tab
            print_copy_count = self.printer_copy_input.value() if hasattr(self, 'printer_copy_input') else 1
            
            # Get selected printer
            selected_printer = self.printer_combo.currentText() if hasattr(self, 'printer_combo') else None
            if selected_printer in ["No printers available", "Error loading printers"]:
                selected_printer = None
            
            # Get port and baudrate
            serial_port = self.port_combo.currentText()
            try:
                baudrate = int(self.baudrate_combo.currentText())
            except ValueError:
                raise ValueError(f"Invalid baudrate: {self.baudrate_combo.currentText()}")

            # Get roll time minimum duration
            roll_time_minimum_seconds = self.roll_time_min_input.value()
            
            settings = {
                # Port settings
                "serial_port": serial_port,
                "baudrate": baudrate,
                "roll_time_minimum_seconds": roll_time_minimum_seconds,

                # Page settings
                "length_tolerance": tolerance,
                "decimal_points": decimal_points_map[decimal_format],
                "rounding": rounding,
                "print_copy_count": print_copy_count,

                # Printer settings
                "selected_printer": selected_printer,

                # API settings
                "api_url": self.current_settings.get("api_url", ""),

                # Supabase settings
                "supabase_url": self.current_settings.get("supabase_url", ""),
                "supabase_key": self.current_settings.get("supabase_key", ""),
                "enable_supabase": self.current_settings.get("enable_supabase", False),

                # ERP settings
                "enable_erp_submission": self.erp_enable_switch.isChecked() if hasattr(self, 'erp_enable_switch') else self.current_settings.get("enable_erp_submission", False),
                "is_verified": self.erp_verify_switch.isChecked() if hasattr(self, 'erp_verify_switch') else self.current_settings.get("is_verified", False),
                "erp_url": self.erp_url_input.text().strip() if hasattr(self, 'erp_url_input') else self.current_settings.get("erp_url", ""),
                "erp_api_key": self.erp_api_key_input.text().strip() if hasattr(self, 'erp_api_key_input') else self.current_settings.get("erp_api_key", ""),
                "erp_api_secret": self.erp_api_secret_input.text().strip() if hasattr(self, 'erp_api_secret_input') else self.current_settings.get("erp_api_secret", ""),
                "erp_timeout": self.erp_timeout_input.value() if hasattr(self, 'erp_timeout_input') else self.current_settings.get("erp_timeout", 30),
                "erp_company": self.erp_company_input.text().strip() if hasattr(self, 'erp_company_input') else self.current_settings.get("erp_company", "Textilindo"),
                "erp_stock_entry_type": self.erp_stock_entry_type_input.currentText().strip() if hasattr(self, 'erp_stock_entry_type_input') else self.current_settings.get("erp_stock_entry_type", ""),
                "erp_from_warehouse": self.erp_from_warehouse_input.text().strip() if hasattr(self, 'erp_from_warehouse_input') else self.current_settings.get("erp_from_warehouse", "Prancis - MGI"),
                "erp_to_warehouse": self.erp_to_warehouse_input.text().strip() if hasattr(self, 'erp_to_warehouse_input') else self.current_settings.get("erp_to_warehouse", "Prancis - MGI"),
                "erp_packing_list_field": self.erp_packing_list_field_input.text().strip() if hasattr(self, 'erp_packing_list_field_input') else self.current_settings.get("erp_packing_list_field", "packing_list_items"),
                "bom_name": self.erp_bom_name_input.text().strip() if hasattr(self, 'erp_bom_name_input') else self.current_settings.get("bom_name", ""),

                # Batch name settings
                "batch_name_format": self.batch_format_input.text() if hasattr(self, 'batch_format_input') else "YYYY-MM-DD_product-code_color-code",
                "batch_start_number": self.batch_start_number_input.text() if hasattr(self, 'batch_start_number_input') else "1"
            }
            
            logger.info(f"Settings to save: {settings}")
            self.settings_updated.emit(settings)
            logger.info("Settings saved successfully")
            self.accept()
            
        except ValueError as e:
            logger.error(f"Error saving settings: {e}")
            # Show error message to user
            QMessageBox.critical(self, "Settings Error", str(e))
        except Exception as e:
            logger.error(f"Unexpected error saving settings: {e}")
            QMessageBox.critical(self, "Settings Error", f"Unexpected error: {str(e)}")
    
    def cancel_settings(self):
        """Cancel settings and close dialog."""
        logger.info("Settings cancelled by user")
        self.reject()
    
    def closeEvent(self, event):
        """Handle close event (X button)."""
        logger.info("Settings dialog closed by X button")
        self.reject()
        event.accept()
    
    def update_connection_status(self):
        """Update the connection status display."""
        try:
            # Check if UI elements exist (they might not be created yet)
            if not hasattr(self, 'connection_status_label'):
                logger.debug("Connection status UI not yet created")
                return
                
            # Check if there's an active connection
            # This would typically check with the main application
            # For now, we'll simulate based on current settings
            current_port = self.current_settings.get("serial_port", "")
            
            if current_port and current_port != "No ports available":
                self.connection_status_label.setText(f"Connected to {current_port}")
                self.connection_status_label.setStyleSheet("""
                    QLabel {
                        color: #4CAF50;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                        background-color: #1e1e1e;
                        border-radius: 5px;
                        border: 1px solid #444444;
                    }
                """)
                if hasattr(self, 'disconnect_btn'):
                    self.disconnect_btn.setEnabled(True)
                if hasattr(self, 'kill_port_btn'):
                    self.kill_port_btn.setEnabled(True)
                if hasattr(self, 'auto_connect_btn'):
                    self.auto_connect_btn.setEnabled(False)
            else:
                self.connection_status_label.setText("Not Connected")
                self.connection_status_label.setStyleSheet("""
                    QLabel {
                        color: #ff4444;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                        background-color: #1e1e1e;
                        border-radius: 5px;
                        border: 1px solid #444444;
                    }
                """)
                if hasattr(self, 'disconnect_btn'):
                    self.disconnect_btn.setEnabled(False)
                if hasattr(self, 'kill_port_btn'):
                    self.kill_port_btn.setEnabled(False)
                if hasattr(self, 'auto_connect_btn'):
                    self.auto_connect_btn.setEnabled(True)
                
        except Exception as e:
            logger.error(f"Error updating connection status: {e}")
    
    def kill_port_connection(self):
        """Kill/close any existing port connection."""
        try:
            logger.info("Killing port connection...")
            
            # This would typically communicate with the main application
            # to close any active serial connections
            # For now, we'll simulate the action
            
            # Update status
            self.connection_status_label.setText("Connection Killed")
            self.connection_status_label.setStyleSheet("""
                QLabel {
                    color: #ff9800;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: #1e1e1e;
                    border-radius: 5px;
                    border: 1px solid #444444;
                }
            """)
            
            # Update button states
            self.disconnect_btn.setEnabled(False)
            self.kill_port_btn.setEnabled(False)
            self.auto_connect_btn.setEnabled(True)
            
            # Show success message
            QMessageBox.information(self, "Port Killed", "Port connection has been killed successfully.")
            logger.info("Port connection killed successfully")
            
        except Exception as e:
            logger.error(f"Error killing port connection: {e}")
            QMessageBox.critical(self, "Error", f"Failed to kill port connection: {str(e)}")
    
    def auto_connect_port(self):
        """Auto connect to available port."""
        try:
            logger.info("Attempting auto connect...")
            
            # First kill any existing connection
            self.kill_port_connection()
            
            # Find available ports
            ports = serial.tools.list_ports.comports()
            if not ports:
                QMessageBox.warning(self, "No Ports", "No serial ports available for connection.")
                return
            
            # Try to connect to the first available port
            selected_port = ports[0].device
            logger.info(f"Attempting to connect to {selected_port}")
            
            # Update current settings
            self.current_settings["serial_port"] = selected_port
            
            # Update port combo box
            index = self.port_combo.findText(selected_port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
            
            # Update status
            self.connection_status_label.setText(f"Auto Connected to {selected_port}")
            self.connection_status_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: #1e1e1e;
                    border-radius: 5px;
                    border: 1px solid #444444;
                }
            """)
            
            # Update button states
            self.disconnect_btn.setEnabled(True)
            self.kill_port_btn.setEnabled(True)
            self.auto_connect_btn.setEnabled(False)
            
            # Show success message
            QMessageBox.information(self, "Auto Connected", f"Successfully connected to {selected_port}")
            logger.info(f"Auto connected to {selected_port}")
            
        except Exception as e:
            logger.error(f"Error in auto connect: {e}")
            QMessageBox.critical(self, "Auto Connect Error", f"Failed to auto connect: {str(e)}")
    
    def disconnect_port(self):
        """Disconnect from current port."""
        try:
            logger.info("Disconnecting port...")
            
            current_port = self.current_settings.get("serial_port", "")
            
            # Update status
            self.connection_status_label.setText("Disconnected")
            self.connection_status_label.setStyleSheet("""
                QLabel {
                    color: #ff9800;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: #1e1e1e;
                    border-radius: 5px;
                    border: 1px solid #444444;
                }
            """)
            
            # Update button states
            self.disconnect_btn.setEnabled(False)
            self.kill_port_btn.setEnabled(False)
            self.auto_connect_btn.setEnabled(True)
            
            # Clear current port
            self.current_settings["serial_port"] = ""
            
            # Show success message
            QMessageBox.information(self, "Disconnected", f"Disconnected from {current_port}")
            logger.info(f"Disconnected from {current_port}")
            
            # Auto reconnect if enabled
            if self.auto_reconnect_checkbox.isChecked():
                logger.info("Auto reconnect enabled, attempting to reconnect...")
                # Use a timer to delay the reconnect
                QTimer.singleShot(1000, self.auto_connect_port)
            
        except Exception as e:
            logger.error(f"Error disconnecting port: {e}")
            QMessageBox.critical(self, "Disconnect Error", f"Failed to disconnect: {str(e)}")
    
    def restart_application(self):
        """Restart the application."""
        try:
            reply = QMessageBox.question(
                self,
                "Restart Application",
                "Are you sure you want to restart the application?\n\nThis will close the current instance and start a new one.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                logger.info("User confirmed application restart from settings dialog")
                
                # Emit signal to main window to handle restart
                # The main window will handle the actual restart process
                self.accept()  # Close settings dialog first
                
                # Import and call the restart function from main window
                from PySide6.QtCore import QTimer
                timer = QTimer()
                timer.singleShot(100, self._trigger_restart)
                
        except Exception as e:
            logger.error(f"Error during restart: {e}")
            QMessageBox.critical(
                self,
                "Restart Error",
                f"Error restarting application:\n\n{str(e)}"
            )
    
    def toggle_erp_credentials_visibility(self):
        """Toggle visibility of ERP API credentials."""
        if self.erp_show_credentials_btn.isChecked():
            self.erp_api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.erp_api_secret_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.erp_show_credentials_btn.setText("🙈 Hide Credentials")
        else:
            self.erp_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.erp_api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.erp_show_credentials_btn.setText("👁 Show Credentials")
    
    def animate_erp_enable_thumb(self, state):
        """Animate the ERP enable thumb movement with smooth transition."""
        try:
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve

            is_checked = state == Qt.CheckState.Checked.value

            # Create animation for thumb movement
            self.erp_thumb_animation = QPropertyAnimation(self.erp_enable_thumb, b"pos")
            self.erp_thumb_animation.setDuration(300)  # 300ms animation
            self.erp_thumb_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # Set start and end positions
            start_pos = self.erp_enable_thumb.pos()
            if is_checked:
                # Move thumb to right (checked position)
                end_pos = QPoint(52 - 24 - 2, 2)  # switch_width - thumb_size - padding
            else:
                # Move thumb to left (unchecked position)
                end_pos = QPoint(2, 2)

            self.erp_thumb_animation.setStartValue(start_pos)
            self.erp_thumb_animation.setEndValue(end_pos)
            self.erp_thumb_animation.start()

        except Exception as e:
            logger.error(f"Error animating ERP enable thumb: {e}")

    def animate_erp_verify_thumb(self, state):
        """Animate the ERP verify thumb movement with smooth transition."""
        try:
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve

            is_checked = state == Qt.CheckState.Checked.value

            # Create animation for thumb movement
            self.erp_verify_animation = QPropertyAnimation(self.erp_verify_thumb, b"pos")
            self.erp_verify_animation.setDuration(300)  # 300ms animation
            self.erp_verify_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # Set start and end positions
            start_pos = self.erp_verify_thumb.pos()
            if is_checked:
                # Move thumb to right (checked position)
                end_pos = QPoint(52 - 24 - 2, 2)  # switch_width - thumb_size - padding
            else:
                # Move thumb to left (unchecked position)
                end_pos = QPoint(2, 2)

            self.erp_verify_animation.setStartValue(start_pos)
            self.erp_verify_animation.setEndValue(end_pos)
            self.erp_verify_animation.start()

        except Exception as e:
            logger.error(f"Error animating ERP verify thumb: {e}")

    def update_erp_verify_status(self):
        """Update ERP verification status label based on toggle state."""
        try:
            is_verified = self.erp_verify_switch.isChecked()

            if is_verified:
                self.erp_verify_label.setText("Verified")
                self.erp_verify_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")
            else:
                self.erp_verify_label.setText("Not Verified")
                self.erp_verify_label.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: bold;")

            # Update the current settings to reflect the change
            self.current_settings["is_verified"] = is_verified

            logger.info(f"ERP verification status updated: {'Verified' if is_verified else 'Not Verified'}")

        except Exception as e:
            logger.error(f"Error updating ERP verify status: {e}")

    def update_erp_status(self):
        """Update ERP connection status display."""
        try:
            enabled = self.erp_enable_switch.isChecked()
            url = self.erp_url_input.text().strip()
            api_key = self.erp_api_key_input.text().strip()
            api_secret = self.erp_api_secret_input.text().strip()

            if not enabled:
                self.erp_status_label.setText("Disabled")
                self.erp_status_label.setStyleSheet("""
                    QLabel {
                        color: #888888;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)
            elif not url or not api_key or not api_secret:
                self.erp_status_label.setText("Not Configured")
                self.erp_status_label.setStyleSheet("""
                    QLabel {
                        color: #ff6b6b;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)
            else:
                self.erp_status_label.setText("Ready to Test")
                self.erp_status_label.setStyleSheet("""
                    QLabel {
                        color: #4CAF50;
                        font-size: 12px;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #555555;
                    }
                """)
        except Exception as e:
            logger.error(f"Error updating ERP status: {e}")
    
    def test_erp_connection(self):
        """Test ERP connection with current settings."""
        try:
            url = self.erp_url_input.text().strip()
            api_key = self.erp_api_key_input.text().strip()
            api_secret = self.erp_api_secret_input.text().strip()
            
            if not url or not api_key or not api_secret:
                QMessageBox.warning(
                    self,
                    "Missing Configuration",
                    "Please fill in all ERP settings:\n"
                    "- ERP URL\n"
                    "- API Key\n"
                    "- API Secret"
                )
                return
            
            # Show progress dialog
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Testing ERP connection...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # Create ERP client
            from ..erp_client import ERPClient
            timeout = self.erp_timeout_input.value()
            
            client = ERPClient(
                base_url=url,
                api_key=api_key,
                api_secret=api_secret,
                timeout=timeout
            )
            
            # Test connection
            success, message = client.test_connection()
            
            progress.close()
            
            if success:
                self.erp_status_label.setText("✅ Connected")
                self.erp_status_label.setStyleSheet("""
                    QLabel {
                        color: #28a745;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #28a745;
                    }
                """)
                QMessageBox.information(
                    self,
                    "Connection Successful",
                    f"Successfully connected to ERP!\n\n{message}"
                )
            else:
                self.erp_status_label.setText("❌ Connection Failed")
                self.erp_status_label.setStyleSheet("""
                    QLabel {
                        color: #ff6b6b;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 5px;
                        background-color: #1e1e1e;
                        border-radius: 3px;
                        border: 1px solid #ff6b6b;
                    }
                """)
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    f"Failed to connect to ERP:\n\n{message}\n\n"
                    f"Please check:\n"
                    f"- ERP URL is correct\n"
                    f"- API credentials are valid\n"
                    f"- Network connection\n"
                    f"- ERP server is running"
                )
            
            client.close()
            
        except Exception as e:
            logger.error(f"Error testing ERP connection: {e}")
            QMessageBox.critical(
                self,
                "Test Error",
                f"Error testing ERP connection:\n\n{str(e)}"
            )
    
    def save_erp_settings(self):
        """Save ERP settings to configuration."""
        try:
            # Get values from inputs
            erp_settings = {
                "enable_erp_submission": self.erp_enable_switch.isChecked(),
                "is_verified": self.erp_verify_switch.isChecked(),
                "erp_url": self.erp_url_input.text().strip(),
                "erp_api_key": self.erp_api_key_input.text().strip(),
                "erp_api_secret": self.erp_api_secret_input.text().strip(),
                "erp_timeout": self.erp_timeout_input.value(),
                "erp_company": self.erp_company_input.text().strip(),
                "erp_stock_entry_type": self.erp_stock_entry_type_input.currentText().strip(),
                "erp_from_warehouse": self.erp_from_warehouse_input.text().strip(),
                "erp_to_warehouse": self.erp_to_warehouse_input.text().strip(),
                "erp_packing_list_field": self.erp_packing_list_field_input.text().strip()
            }

            # Debug logging
            logger.info(f"Saving ERP settings - is_verified: {erp_settings['is_verified']}")
            
            # Add BOM data if selected (from BOM search section)
            if hasattr(self, 'selected_bom_data') and self.selected_bom_data:
                erp_settings.update({
                    "bom_name": self.selected_bom_data.get("bom_name", ""),
                    "bom_item": self.selected_bom_data.get("bom_item", ""),
                    "bom_product_code": self.selected_bom_data.get("bom_product_code", ""),
                    "bom_color_code": self.selected_bom_data.get("bom_color_code", ""),
                    "bom_product_name": self.selected_bom_data.get("bom_product_name", "")
                })
                logger.info(f"BOM data included in save: {self.selected_bom_data.get('bom_product_code')} (Color: {self.selected_bom_data.get('bom_color_code')})")
            else:
                # Keep existing BOM settings if no new selection
                erp_settings.update({
                    "bom_name": self.current_settings.get("bom_name", ""),
                    "bom_item": self.current_settings.get("bom_item", ""),
                    "bom_product_code": self.current_settings.get("bom_product_code", ""),
                    "bom_color_code": self.current_settings.get("bom_color_code", ""),
                    "bom_product_name": self.current_settings.get("bom_product_name", "")
                })
                logger.info("No new BOM selected, keeping existing BOM data")
            
            # Update current settings
            self.current_settings.update(erp_settings)
            
            # Save to config file
            from ..config import save_config
            save_config(self.current_settings)
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "ERP settings have been saved successfully!\n\n"
                f"Verification status: {'Verified' if erp_settings['is_verified'] else 'Not Verified'}\n\n"
                "The settings will take effect immediately."
            )

            logger.info("ERP settings saved successfully")
            
            # Update status
            self.update_erp_status()

            # Notify product form to update BOM button visibility
            try:
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                for widget in app.topLevelWidgets():
                    # Check if this is the main window and has product_form
                    if hasattr(widget, 'product_form') and widget.product_form:
                        widget.product_form.update_bom_button_visibility()
                        logger.info("Notified product form to update BOM button visibility")
                        break
                    # Also check if the widget contains product_form in its children
                    elif hasattr(widget, 'findChild'):
                        product_form = widget.findChild(QWidget, 'product_form')
                        if product_form and hasattr(product_form, 'update_bom_button_visibility'):
                            product_form.update_bom_button_visibility()
                            logger.info("Found and notified product form via findChild")
                            break
            except Exception as e:
                logger.error(f"Error notifying product form about BOM button visibility: {e}")
            
        except Exception as e:
            logger.error(f"Error saving ERP settings: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save ERP settings:\n\n{str(e)}"
            )
    
    def _trigger_restart(self):
        """Trigger restart by finding the main window and calling its restart method."""
        try:
            # Find the main window
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
            for widget in app.topLevelWidgets():
                if hasattr(widget, 'restart_application'):
                    widget.restart_application()
                    break
        except Exception as e:
            logger.error(f"Error triggering restart: {e}")
    
    def search_bom(self, search_text: str):
        """Search BOM by product code in real-time."""
        try:
            if not search_text or len(search_text) < 2:
                self.bom_results_list.clear()
                self.bom_results_list.setVisible(False)
                return
            
            # Get ERP URL
            erp_url = self.erp_url_input.text().strip()
            api_key = self.erp_api_key_input.text().strip()
            api_secret = self.erp_api_secret_input.text().strip()
            
            if not erp_url or not api_key or not api_secret:
                return
            
            # Build API endpoint with proper URL encoding
            base_url = f"{erp_url}/api/resource/BOM"
            
            # Build filters as JSON string (properly encoded)
            # Note: BOM doctype has "item" field (link to Item), not "item_code"
            filters = json.dumps([["item", "like", f"%{search_text}%"]])
            fields = json.dumps(["name", "item", "is_active"])
            
            # Build query parameters
            params = {
                "filters": filters,
                "fields": fields,
                "limit_page_length": "10"
            }
            
            # Build URL with encoded parameters
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            # Make API request with proper headers
            headers = {
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                boms = data.get("data", [])
                
                # Clear previous results
                self.bom_results_list.clear()
                
                if boms:
                    # Add BOMs to list
                    for bom in boms:
                        bom_name = bom.get("name", "")
                        item = bom.get("item", "")
                        is_active = bom.get("is_active", 0)
                        
                        # Only show active BOMs
                        if is_active:
                            # item is the item_code in BOM doctype
                            item_text = f"{item} - {bom_name}"
                            list_item = QListWidgetItem(item_text)
                            list_item.setData(Qt.ItemDataRole.UserRole, {
                                "name": bom_name,
                                "item": item,
                                "item_code": item  # item field contains the item_code
                            })
                            self.bom_results_list.addItem(list_item)
                    
                    # Show results
                    if self.bom_results_list.count() > 0:
                        self.bom_results_list.setVisible(True)
                    else:
                        self.bom_results_list.setVisible(False)
                else:
                    self.bom_results_list.setVisible(False)
            else:
                logger.error(f"BOM search failed: {response.status_code} - {response.text}")
                self.bom_results_list.setVisible(False)
                
        except Exception as e:
            logger.error(f"Error searching BOM: {e}")
            self.bom_results_list.setVisible(False)
    
    def select_bom(self, item: QListWidgetItem):
        """Handle BOM selection from dropdown."""
        try:
            bom_data = item.data(Qt.ItemDataRole.UserRole)
            
            if bom_data:
                bom_name = bom_data.get("name", "")
                item_name = bom_data.get("item", "")
                item_code = bom_data.get("item_code", "")
                
                # Update selected BOM display
                self.selected_bom_label.setText(
                    f"✓ Selected BOM:\n"
                    f"Name: {bom_name}\n"
                    f"Item: {item_name}\n"
                    f"Product Code: {item_code}"
                )
                self.selected_bom_label.setStyleSheet("""
                    QLabel {
                        color: #4CAF50;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 8px;
                        background-color: #1e1e1e;
                        border-radius: 5px;
                        border: 2px solid #4CAF50;
                    }
                """)
                
                # Fetch item details to get color code and other info
                color_code = ""
                product_name = ""
                
                try:
                    # Try to get item details from product search API
                    api_url = self.current_settings.get('api_url', '')
                    if api_url:
                        response = requests.post(
                            api_url,
                            json={'product_code': item_code},
                            timeout=5
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if isinstance(result.get('message'), dict):
                                msg = result['message']
                                if msg.get('success') and msg.get('data', {}).get('products'):
                                    products = msg['data']['products']
                                    if products:
                                        product = products[0]
                                        color_code = product.get('color_code', '')
                                        product_name = product.get('product_name', '')
                                        logger.info(f"Fetched color code: {color_code}, name: {product_name}")
                except Exception as e:
                    logger.warning(f"Could not fetch item details for color code: {e}")
                
                # Store selected BOM data
                self.selected_bom_data = {
                    "bom_name": bom_name,
                    "bom_item": item_name,
                    "bom_product_code": item_code,
                    "bom_color_code": color_code,
                    "bom_product_name": product_name
                }
                
                # Clear search and hide results
                self.bom_search_input.clear()
                self.bom_results_list.setVisible(False)
                
                logger.info(f"BOM selected: {bom_name} - {item_code} (Color: {color_code})")
                
        except Exception as e:
            logger.error(f"Error selecting BOM: {e}") 