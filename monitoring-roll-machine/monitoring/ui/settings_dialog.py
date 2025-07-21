from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QFrame, QLabel, QHBoxLayout, QTabWidget,
    QLineEdit, QRadioButton, QButtonGroup, QSpinBox, QGroupBox,
    QMessageBox, QCheckBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from typing import Dict, Any
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Dialog for configuring application settings with tabbed interface."""
    
    # Signal emitted when settings are saved
    settings_updated = Signal(dict)
    
    def __init__(self, current_settings: Dict[str, Any]):
        super().__init__()
        self.current_settings = current_settings
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
        
        # Create tabs
        self.create_port_settings_tab()
        self.create_port_management_tab()
        self.create_page_settings_tab()
        self.create_api_settings_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        refresh_btn.setStyleSheet(self.get_button_style("secondary"))
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
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
        
        # 2. Decimal Point
        self.decimal_combo = QComboBox()
        self.decimal_combo.addItems(["#", "#.#", "#.##"])
        current_decimal = self.current_settings.get("decimal_points", 1)
        # Map decimal points to display format
        decimal_map = {0: "#", 1: "#.#", 2: "#.##"}
        current_format = decimal_map.get(current_decimal, "#.#")
        self.decimal_combo.setCurrentText(current_format)
        self.decimal_combo.currentTextChanged.connect(self.update_conversion_preview)
        settings_form.addRow("Decimal Format:", self.decimal_combo)
        
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
        self.api_url_input.setPlaceholderText("http://localhost:8000/api/method/textile_plus.overrides.api.product.search_product")
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
            
            # Map decimal format to decimal points
            decimal_points_map = {"#": 0, "#.#": 1, "#.##": 2}
            decimal_points = decimal_points_map.get(decimal_format, 1)
            
            # Calculate conversion factor (example: 100 meter)
            base_value = 100.0
            
            # Apply tolerance formula: length_display = length_input * (1 - tolerance_percent / 100)
            adjusted_value = base_value * (1 - tolerance / 100)
            
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
            
            # Update preview with unit
            self.conversion_preview.setText(f"{formatted_value} Meter")
            
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
            
            # Get decimal format
            decimal_format = self.decimal_combo.currentText()
            decimal_points_map = {"#": 0, "#.#": 1, "#.##": 2}
            if decimal_format not in decimal_points_map:
                raise ValueError(f"Invalid decimal format: {decimal_format}")
            
            # Get rounding method
            rounding = "UP" if self.round_up_radio.isChecked() else "DOWN"
            
            # Get port and baudrate
            serial_port = self.port_combo.currentText()
            try:
                baudrate = int(self.baudrate_combo.currentText())
            except ValueError:
                raise ValueError(f"Invalid baudrate: {self.baudrate_combo.currentText()}")
            
            settings = {
                # Port settings
                "serial_port": serial_port,
                "baudrate": baudrate,
                
                # Page settings
                "length_tolerance": tolerance,
                "decimal_points": decimal_points_map[decimal_format],
                "rounding": rounding,
                
                # API settings
                "api_url": self.current_settings.get("api_url", "")
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