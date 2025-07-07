from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QFrame, QLabel, QHBoxLayout, QTabWidget,
    QLineEdit, QRadioButton, QButtonGroup, QSpinBox, QGroupBox,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
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
        self.create_page_settings_tab()
        
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
        
        # 4. Conversion Factor Preview
        preview_group = QGroupBox("Conversion Factor Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.conversion_preview = QLabel("65.00 Yard / Meter")
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
            
            # Calculate conversion factor (example: 65 yard/meter)
            base_value = 65.0
            
            # Apply tolerance
            if rounding == "UP":
                adjusted_value = base_value * (1 + tolerance / 100)
            else:
                adjusted_value = base_value * (1 - tolerance / 100)
            
            # Format with decimal points
            format_str = f"{{:.{decimal_points}f}}"
            formatted_value = format_str.format(adjusted_value)
            
            # Update preview
            self.conversion_preview.setText(f"{formatted_value} Yard / Meter")
            
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
                "rounding": rounding
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