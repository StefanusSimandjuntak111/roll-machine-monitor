from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QLabel, QHBoxLayout,
    QRadioButton, QButtonGroup, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSize, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap
from typing import Dict, Any, Optional
import requests
from io import BytesIO
import logging
from datetime import datetime

from .connection_settings import ConnectionSettings
from .print_preview import PrintPreviewDialog

# Setup logger
logger = logging.getLogger(__name__)


class ProductSearchWorker(QThread):
    """Worker thread for non-blocking API calls."""
    
    # Signals
    search_completed = Signal(dict)  # Emitted when search completes successfully
    search_failed = Signal(str, str)  # Emitted when search fails (error_type, message)
    
    # Class-level session for connection pooling
    _session = None
    
    def __init__(self, product_code: str, api_url: str, headers: Dict[str, str]):
        super().__init__()
        self.product_code = product_code
        self.api_url = api_url
        self.headers = headers
        
        # Initialize session if not exists
        if ProductSearchWorker._session is None:
            ProductSearchWorker._session = requests.Session()
            ProductSearchWorker._session.headers.update(headers)
        
    def run(self):
        """Run the API call in background thread."""
        try:
            # Ensure session is available
            if ProductSearchWorker._session is None:
                ProductSearchWorker._session = requests.Session()
                ProductSearchWorker._session.headers.update(self.headers)
                
            response = ProductSearchWorker._session.get(
                f"{self.api_url}?item_code={self.product_code}",
                timeout=3
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if product data is found
            if (data.get("message") and 
                isinstance(data["message"], dict) and 
                data["message"].get("success") and 
                data["message"].get("data")):
                
                self.search_completed.emit(data["message"]["data"])
            else:
                self.search_failed.emit("not_found", "Product not found")
                
        except requests.exceptions.Timeout:
            self.search_failed.emit("timeout", "Search timeout - please try again")
        except requests.exceptions.ConnectionError:
            self.search_failed.emit("connection", "Cannot connect to server")
        except Exception as e:
            self.search_failed.emit("error", f"Search error: {str(e)}")

class ProductForm(QWidget):
    """Form for entering and editing product information."""
    
    # Signals
    product_updated = Signal(dict)
    reset_counter = Signal()  # Signal for resetting counter
    
    # Konstanta konversi
    METER_TO_YARD = 1.09361
    YARD_TO_METER = 0.9144
    DEFAULT_IMAGE_URL = "https://thumb.ac-illust.com/b1/b170870007dfa419295d949814474ab2_t.jpeg"
    
    # API Configuration
    API_BASE_URL = "http://192.168.68.111:8001/api/method/frappe.utils.custom_api.get_product_detail"
    API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "token 61996278bcc8bbb:8a178a12b28e784"
    }
    
    def __init__(self):
        super().__init__()
        self._is_updating = False  # Flag untuk mencegah recursive updates
        self._current_unit = "Meter"  # Track current unit
        self._search_timer = QTimer()  # Timer untuk delayed search
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_product_search)
        self._last_searched_code = ""  # Track last searched code to avoid duplicate searches
        self._search_worker = None  # Current search worker thread
        self._barcode = ""  # Store barcode data from API (not displayed in UI)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the form UI."""
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(form_frame)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(10)  # Reduced spacing
        
        # Common style for input fields
        input_style = """
            QLineEdit, QDoubleSpinBox {
                background-color: #353535;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
                color: white;
                font-size: 14px;
                min-height: 40px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus {
                border: 1px solid #0078d4;
            }
        """
        
        # Loading style for product code input
        self.loading_style = """
            QLineEdit {
                background-color: #353535;
                border: 1px solid #ffa500;
                border-radius: 4px;
                padding: 5px;
                color: white;
                font-size: 14px;
                min-height: 40px;
            }
        """
        
        # Radio button style
        radio_style = """
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
                background-color: #353535;
            }
            QRadioButton::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
            }
            QRadioButton::indicator:unchecked:hover {
                border: 2px solid #888888;
            }
            QRadioButton:checked {
                color: white;
            }
        """
        
        # Product Code with search functionality
        product_code_container = QWidget()
        product_code_layout = QHBoxLayout(product_code_container)
        product_code_layout.setContentsMargins(0, 0, 0, 0)
        product_code_layout.setSpacing(5)
        
        self.product_code = QLineEdit()
        self.product_code.setPlaceholderText("Enter product code (auto-search after 3 chars)")
        self.product_code.setStyleSheet(input_style)
        self.product_code.textChanged.connect(self._on_product_code_changed)
        self.product_code.editingFinished.connect(self._on_product_code_finished)
        product_code_layout.addWidget(self.product_code)
        
        # Loading indicator
        self.search_status_label = QLabel("")
        self.search_status_label.setStyleSheet("""
            QLabel {
                color: #ffa500;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.search_status_label.setFixedWidth(80)
        product_code_layout.addWidget(self.search_status_label)
        
        form_layout.addRow("Product Code:", product_code_container)
        
        # Product Name (auto-filled from API)
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Product name (auto-filled)")
        self.product_name.setStyleSheet(input_style)
        self.product_name.setReadOnly(True)  # Read-only field
        form_layout.addRow("Product Name:", self.product_name)
        
        # Color Code
        self.color_code = QLineEdit()
        self.color_code.setPlaceholderText("Enter color code")
        self.color_code.setStyleSheet(input_style)
        form_layout.addRow("Color Code:", self.color_code)
        
        # Batch Number
        self.batch_number = QLineEdit()
        self.batch_number.setPlaceholderText("Enter batch number")
        self.batch_number.setStyleSheet(input_style)
        form_layout.addRow("Batch Number:", self.batch_number)
        
        # Current Length with buttons
        length_container = QWidget()
        length_layout = QHBoxLayout(length_container)
        length_layout.setSpacing(5)  # Reduced spacing
        length_layout.setContentsMargins(0, 0, 0, 0)
        
        # Current Length Input
        self.target_length = QDoubleSpinBox()
        self.target_length.setRange(0, 100000)
        self.target_length.setDecimals(2)
        self.target_length.setValue(0.0)  # Default to 0
        self.target_length.valueChanged.connect(self.on_length_changed)
        # Clear error styling when user changes value
        self.target_length.valueChanged.connect(lambda: self.clear_error(self.target_length))
        self.target_length.setStyleSheet(input_style + """
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0;
                height: 0;
                border: none;
                background: none;
            }
            QDoubleSpinBox {
                padding-right: 5px;  /* Reduce right padding since we removed the buttons */
            }
        """)
        # Allow manual input - remove setReadOnly(True)
        self.target_length.setReadOnly(False)  # Allow manual keyboard input
        self.target_length.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        length_layout.addWidget(self.target_length)
        
        # Button style
        button_style = """
            QPushButton {
                background-color: #444444;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 0px;
                width: 55px;
                height: 50px;
                min-width: 55px;
                min-height: 50px;
                max-width: 55px;
                max-height: 50px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #666666;
            }
        """
        
        # Plus Button
        self.plus_button = QPushButton("+")
        self.plus_button.setFont(QFont("Segoe UI", 14))
        self.plus_button.clicked.connect(self.increment_length)
        self.plus_button.setStyleSheet(button_style)
        self.plus_button.setFixedSize(55, 40)
        length_layout.addWidget(self.plus_button)
        
        # Minus Button
        self.minus_button = QPushButton("-")
        self.minus_button.setFont(QFont("Segoe UI", 14))
        self.minus_button.clicked.connect(self.decrement_length)
        self.minus_button.setStyleSheet(button_style)
        self.minus_button.setFixedSize(55, 40)
        length_layout.addWidget(self.minus_button)
        
        form_layout.addRow("Current Length:", length_container)
        
        # Unit Selection with Radio Buttons
        unit_container = QWidget()
        unit_layout = QHBoxLayout(unit_container)
        unit_layout.setSpacing(20)  # Space between radio buttons
        unit_layout.setContentsMargins(0, 0, 0, 0)
        
        self.unit_group = QButtonGroup(self)
        
        # Meter Radio
        self.meter_radio = QRadioButton("Meter")
        self.meter_radio.setStyleSheet(radio_style)
        self.meter_radio.setChecked(True)  # Default selection
        self.unit_group.addButton(self.meter_radio)
        unit_layout.addWidget(self.meter_radio)
        
        # Yard Radio
        self.yard_radio = QRadioButton("Yard")
        self.yard_radio.setStyleSheet(radio_style)
        self.unit_group.addButton(self.yard_radio)
        unit_layout.addWidget(self.yard_radio)
        
        # Connect radio button signals
        self.unit_group.buttonClicked.connect(self.on_unit_changed)
        
        form_layout.addRow("Unit of Measurement:", unit_container)

        # Image Label
        image_container = QWidget()
        image_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        # Set image size relative to form width
        self.image_label.setFixedSize(150, 150)  # Reduced size
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #444444;
                border-radius: 4px;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        image_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        form_layout.addRow("Attachment:", image_container)
        
        # Load default image
        self.load_default_image()
        
        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Action button style
        action_button_style = """
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            #print_button {
                background-color: #28a745;
            }
            #print_button:hover {
                background-color: #218838;
            }
            #print_button:pressed {
                background-color: #1e7e34;
            }
        """
        
        # Reset Counter Button
        self.reset_button = QPushButton("Reset Counter")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_counter_with_save)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.reset_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(self.reset_button)
        
        # Print Button
        self.print_button = QPushButton("Print")
        self.print_button.setObjectName("print_button")
        self.print_button.clicked.connect(self.print_product_info)
        self.print_button.setStyleSheet(action_button_style)
        self.print_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(self.print_button)
        
        form_layout.addRow(buttons_container)
        
    def on_unit_changed(self, button: QRadioButton):
        """Handle unit selection change."""
        new_unit = button.text()
        
        # Jika unit sama dengan sebelumnya, abaikan
        if new_unit == self._current_unit:
            return
            
        if self._is_updating:
            return
            
        self._is_updating = True
        current_value = self.target_length.value()
        
        if new_unit == "Yard":
            # Convert from meters to yards
            new_value = current_value * self.METER_TO_YARD
        else:
            # Convert from yards to meters
            new_value = current_value * self.YARD_TO_METER
            
        self.target_length.setValue(round(new_value, 2))
        self._current_unit = new_unit  # Update current unit
        self._is_updating = False
        
    def on_length_changed(self, value: float):
        """Handle length value change."""
        if not self._is_updating:
            # Value changed by user, no need to convert
            pass
            
    def reset_counter_with_save(self):
        """Save product info and reset counter."""
        logger.info("RESET COUNTER: Sending reset command to device")
            
        if self.validate_inputs():
            # Create product info dictionary with consistent field names
            product_info = {
                'product_code': self.product_code.text().strip(),
                'product_name': self.product_name.text().strip(),
                'color_code': self.color_code.text().strip(),
                'color': self.color_code.text().strip(),  # For backward compatibility
                'barcode': self._barcode,
                'batch_number': self.batch_number.text().strip(),
                'target_length': self.target_length.value(),
                'units': self.unit_group.checkedButton().text()
            }
            # Emit the product_updated signal
            self.product_updated.emit(product_info)
            # Emit the reset_counter signal
            self.reset_counter.emit()
        
    def print_product_info(self):
        """Print product information."""
        if not self.validate_inputs():
            return
            
        # Get product info with consistent field names for printing
        product_info = {
            'product_code': self.product_code.text().strip(),
            'product_name': self.product_name.text().strip(),
            'color_code': self.color_code.text().strip(),
            'color': self.color_code.text().strip(),  # For backward compatibility
            'barcode': self._barcode,
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'units': self.unit_group.checkedButton().text()
        }
        
        # Show print preview dialog
        preview_dialog = PrintPreviewDialog(product_info, self)
        preview_dialog.exec()
        
    def validate_inputs(self) -> bool:
        """Validate form inputs."""
        if not self.product_code.text().strip():
            self.show_error(self.product_code, "Product code is required")
            return False
            
        if not self.product_name.text().strip():
            self.show_error(self.product_name, "Product name is required")
            return False
            
        if not self.color_code.text().strip():
            self.show_error(self.color_code, "Color code is required")
            return False
            
        if not self.batch_number.text().strip():
            self.show_error(self.batch_number, "Batch number is required")
            return False
            
        if self.target_length.value() <= 0:
            self.show_error(self.target_length, "Panjang belum di set! Masukkan current panjang yang valid.")
            self._show_kiosk_dialog(
                "warning",
                "Current Length Required",
                "Panjang belum di set!\n\nSilakan masukkan current panjang minimal 1 meter sebelum melanjutkan."
            )
            return False
            
        if self.target_length.value() < 1:
            self.show_error(self.target_length, "Current panjang minimal 1 meter")
            self._show_kiosk_dialog(
                "warning",
                "Current Length Too Small",
                "Current panjang terlalu kecil!\n\nMinimal panjang yang diizinkan adalah 1 meter."
            )
            return False
            
        return True
        
    def _show_kiosk_dialog(self, dialog_type: str, title: str, message: str) -> int:
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
    
    def show_error(self, widget: QWidget, message: str):
        """Show error styling and tooltip for a widget."""
        widget.setStyleSheet("""
            QLineEdit, QSpinBox, QDoubleSpinBox, QRadioButton {
                background-color: #353535;
                border: 1px solid #ff4444;
                border-radius: 4px;
                padding: 5px;
                color: white;
                font-size: 14px;
                min-height: 40px;
            }
        """)
        widget.setToolTip(message)
        
    def clear_error(self, widget: QWidget):
        """Clear error styling and tooltip for a widget."""
        # Reset to normal styling based on widget type
        if isinstance(widget, QDoubleSpinBox):
            # Reset to normal input style for spinbox
            input_style = """
                QDoubleSpinBox {
                    background-color: #353535;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 5px;
                    color: white;
                    font-size: 14px;
                    min-height: 40px;
                }
                QDoubleSpinBox:focus {
                    border: 1px solid #0078d4;
                }
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 0;
                    height: 0;
                    border: none;
                    background: none;
                }
                QDoubleSpinBox {
                    padding-right: 5px;
                }
            """
            widget.setStyleSheet(input_style)
        else:
            widget.setStyleSheet("")
        widget.setToolTip("")
        
    def get_product_info(self) -> Dict[str, Any]:
        """Get current product information."""
        return {
            'product_code': self.product_code.text().strip(),
            'product_name': self.product_name.text().strip(),
            'color_code': self.color_code.text().strip(),
            'barcode': self._barcode,
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'unit': self.unit_group.checkedButton().text()
        }
    
    @property
    def product_name_text(self) -> str:
        """Get product name from form."""
        return self.product_name.text().strip() if hasattr(self, 'product_name') else "Unknown"
    
    @property
    def product_code_text(self) -> str:
        """Get product code from form."""
        return self.product_code.text().strip() if hasattr(self, 'product_code') else "Unknown"
    
    @property
    def batch_text(self) -> str:
        """Get batch from form."""
        return self.batch_number.text().strip() if hasattr(self, 'batch_number') else "Unknown"
        
    def set_product_info(self, info: Dict[str, Any]):
        """Set product information in the form."""
        self.product_code.setText(info.get('product_code', ''))
        self.product_name.setText(info.get('product_name', ''))
        self.color_code.setText(info.get('color_code', ''))
        self._barcode = info.get('barcode', '')
        self.batch_number.setText(info.get('batch_number', ''))
        self.target_length.setValue(info.get('target_length', 0.0))
        
        # Handle unit selection properly
        unit = info.get('unit', 'Meter')
        if unit.lower() in ['yard', 'yards', 'y']:
            self.yard_radio.setChecked(True)
            self._current_unit = "Yard"
        else:
            self.meter_radio.setChecked(True)
            self._current_unit = "Meter"

    def increment_length(self):
        """Increment target length by 1."""
        current_value = self.target_length.value()
        self.target_length.setValue(current_value + 1)
        # Clear any error styling when user interacts
        self.clear_error(self.target_length)

    def decrement_length(self):
        """Decrement target length by 1."""
        current_value = self.target_length.value()
        if current_value > 0:  # Prevent negative values
            self.target_length.setValue(current_value - 1)
        # Clear any error styling when user interacts
        self.clear_error(self.target_length)

    def update_target_with_current_length(self, current_length: float):
        """Update target length input with current length from monitoring."""
        if not self._is_updating:
            self._is_updating = True
            self.target_length.setValue(round(current_length, 2))
            self._is_updating = False
    
    def update_unit_from_monitoring(self, unit: str):
        """Update unit radio button based on monitoring data."""
        if not self._is_updating:
            self._is_updating = True
            
            if unit.lower() == "yard":
                if not self.yard_radio.isChecked():
                    self.yard_radio.setChecked(True)
                    self._current_unit = "Yard"
            elif unit.lower() == "meter":
                if not self.meter_radio.isChecked():
                    self.meter_radio.setChecked(True)
                    self._current_unit = "Meter"
            
            self._is_updating = False

    def load_image(self, url):
        """Load image from URL and display it."""
        try:
            if not url or url.strip() == "":
                self.load_default_image()
                return
                
            logger.info(f"Attempting to load image from: {url}")
            response = requests.get(url, timeout=5)  # Add timeout for better error handling
            response.raise_for_status()  # Raise exception for bad status codes
            
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            
            if pixmap.loadFromData(image_data.getvalue()):
                # Successfully loaded image
                scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                # Reset any previous error styling
                self.image_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #444444;
                        border-radius: 4px;
                    }
                """)
                self.image_label.setText("")  # Clear any text
                logger.info(f"Successfully loaded image from: {url}")
            else:
                # Failed to load pixmap data
                logger.warning(f"Failed to load pixmap data from: {url}")
                self.load_default_image()
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout loading image from: {url}")
            self.load_default_image()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error loading image from {url}: {e}")
            self.load_default_image()
        except Exception as e:
            logger.error(f"Unexpected error loading image from {url}: {e}")
            self.load_default_image()

    def load_default_image(self):
        """Load default 'No Image Available' placeholder."""
        try:
            # Try to load the default image URL first
            response = requests.get(self.DEFAULT_IMAGE_URL, timeout=3)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data.getvalue()):
                scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #444444;
                        border-radius: 4px;
                    }
                """)
                self.image_label.setText("")
                logger.info("Loaded default image from URL")
            else:
                self.show_no_image_placeholder()
        except Exception as e:
            logger.warning(f"Could not load default image from URL: {e}")
            self.show_no_image_placeholder()

    def show_no_image_placeholder(self):
        """Show 'No Image Available' text placeholder."""
        self.image_label.clear()  # Clear any existing pixmap
        self.image_label.setText("No Image\nAvailable")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px dashed #666666;
                border-radius: 5px;
                color: #666666;
                font-size: 12px;
                text-align: center;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logger.info("Showing 'No Image Available' placeholder")

    def save_product_info(self):
        """Validate and save product information."""
        if not self.validate_inputs():
            return
            
        # Create product info dictionary with consistent field names
        product_info = {
            'product_code': self.product_code.text().strip(),
            'product_name': self.product_name.text().strip(),
            'color_code': self.color_code.text().strip(),
            'color': self.color_code.text().strip(),  # For backward compatibility
            'barcode': self._barcode,
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'units': self.unit_group.checkedButton().text()
        }
        # Emit the product_updated signal
        self.product_updated.emit(product_info)

    def _on_product_code_changed(self):
        """Handle text change in product code input."""
        # Reduce delay to 150ms for faster response
        self._search_timer.start(150)  # Start timer for delayed search

    def _on_product_code_finished(self):
        """Handle editing finished in product code input."""
        self._search_timer.stop()  # Stop timer
        self._perform_product_search()

    def _perform_product_search(self):
        """Perform product search based on the current product code."""
        product_code = self.product_code.text().strip()
        
        # Only search if code has at least 3 characters and is different from last search
        if len(product_code) >= 3 and product_code != self._last_searched_code:
            self._last_searched_code = product_code
            self._set_search_status("Searching...", "#ffa500", "Searching for product details...")
            
            # Set loading style for product code input
            self.product_code.setStyleSheet(self.loading_style)
            
            # Cancel previous search if running
            if self._search_worker and self._search_worker.isRunning():
                self._search_worker.terminate()
                self._search_worker.wait()
            
            # Start new search in background thread
            self._search_worker = ProductSearchWorker(product_code, self.API_BASE_URL, self.API_HEADERS)
            self._search_worker.search_completed.connect(self._on_search_completed)
            self._search_worker.search_failed.connect(self._on_search_failed)
            self._search_worker.start()
            
        elif len(product_code) < 3:
            # Clear status if less than 3 characters
            self._clear_search_status()
            self._last_searched_code = ""
            
    def _on_search_completed(self, product_info: Dict[str, Any]):
        """Handle successful search completion."""
        self._populate_form_from_api(product_info)
        self._set_search_status("Found", "#28a745", f"Found: {product_info.get('item_name', 'Product')}")
        self._reset_input_style()
        
    def _on_search_failed(self, error_type: str, message: str):
        """Handle search failure."""
        color_map = {
            "not_found": "#ff4444",
            "timeout": "#ff4444", 
            "connection": "#ff4444",
            "error": "#ff4444"
        }
        
        status_map = {
            "not_found": "Not Found",
            "timeout": "Timeout",
            "connection": "No Connection", 
            "error": "Error"
        }
        
        self._set_search_status(
            status_map.get(error_type, "Error"),
            color_map.get(error_type, "#ff4444"),
            message
        )
        self._reset_input_style()
        logger.error(f"Search failed: {error_type} - {message}")

    def search_product_details(self, product_code: str):
        """Perform API call to search for product details."""
        try:
            # Make API request with item_code parameter as per the API endpoint
            response = requests.get(
                f"{self.API_BASE_URL}?item_code={product_code}",
                headers=self.API_HEADERS,
                timeout=3  # Reduce timeout to 3 seconds for faster feedback
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if product data is found based on actual API response structure
            if (data.get("message") and 
                isinstance(data["message"], dict) and 
                data["message"].get("success") and 
                data["message"].get("data")):
                
                product_info = data["message"]["data"]
                self._populate_form_from_api(product_info)
                self._set_search_status("Found", "#28a745", f"Found: {product_info.get('item_name', product_code)}")
                self._reset_input_style()
                logger.info(f"Successfully found product: {product_code} - {product_info.get('item_name', '')}")
                
            else:
                self._set_search_status("Not Found", "#ff4444", "Product not found")
                self._reset_input_style()
                logger.warning(f"Product not found for code: {product_code}")
                
        except requests.exceptions.Timeout:
            self._set_search_status("Timeout", "#ff4444", "Search timeout - please try again")
            self._reset_input_style()
            logger.error(f"Timeout searching for product: {product_code}")
            
        except requests.exceptions.ConnectionError:
            self._set_search_status("No Connection", "#ff4444", "Cannot connect to server")
            self._reset_input_style()
            logger.error(f"Connection error searching for product: {product_code}")
            
        except Exception as e:
            self._set_search_status("Error", "#ff4444", f"Search error: {str(e)}")
            self._reset_input_style()
            logger.error(f"Error searching for product {product_code}: {e}")

    def _set_search_status(self, text: str, color: str, tooltip: str):
        """Set search status label with text, color and tooltip."""
        self.search_status_label.setText(text)
        self.search_status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        self.search_status_label.setToolTip(tooltip)
        self.search_status_label.setFixedWidth(80)
        self.search_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _clear_search_status(self):
        """Clear search status label."""
        self.search_status_label.setText("")
        self.search_status_label.setToolTip("")
        self._reset_input_style()

    def _reset_input_style(self):
        """Reset product code input to normal style."""
        input_style = """
            QLineEdit {
                background-color: #353535;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
                color: white;
                font-size: 14px;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
        """
        self.product_code.setStyleSheet(input_style)

    def _populate_form_from_api(self, product_info: Dict[str, Any]):
        """Populate form fields from API response data."""
        # Map API response fields based on actual API structure
        if "item_code" in product_info:
            # Only update if it's different to avoid cursor movement
            current_text = self.product_code.text().strip()
            new_text = str(product_info["item_code"])
            if current_text.upper() != new_text.upper():
                self.product_code.setText(new_text)
        
        # Set product name from item_name
        if "item_name" in product_info:
            self.product_name.setText(str(product_info["item_name"]))
        
        # Extract color code from variants.attributes[0].abbreviation
        color_code = ""
        if "variants" in product_info and "attributes" in product_info["variants"]:
            attributes = product_info["variants"]["attributes"]
            if isinstance(attributes, list) and len(attributes) > 0:
                color_code = attributes[0].get("abbreviation", "")
        
        # If no color from variants, fallback to item_name
        if not color_code and "item_name" in product_info:
            color_code = str(product_info["item_name"])
        
        self.color_code.setText(color_code)
        
        # Extract barcode from new API response structure
        # The new API provides barcode information in barcode_urls with two arrays:
        # - existing_barcodes: barcodes that already exist in the system
        # - potential_barcodes: barcodes that can be generated (with different quantities)
        barcode = ""
        barcode_source = ""
        
        # Priority 1: Try existing barcodes first (already generated/available)
        if ("barcode_urls" in product_info and 
            "existing_barcodes" in product_info["barcode_urls"] and
            product_info["barcode_urls"]["existing_barcodes"]):
            # Use first existing barcode
            existing_barcode = product_info["barcode_urls"]["existing_barcodes"][0]
            if isinstance(existing_barcode, dict):
                barcode = existing_barcode.get("barcode_id", "")
                barcode_source = "existing_barcodes"
            else:
                barcode = str(existing_barcode)
                barcode_source = "existing_barcodes"
        
        # Priority 2: If no existing barcode, use first potential barcode 
        elif ("barcode_urls" in product_info and 
              "potential_barcodes" in product_info["barcode_urls"] and
              product_info["barcode_urls"]["potential_barcodes"]):
            # Use first potential barcode (usually quantity=1 which is most common)
            potential_barcode = product_info["barcode_urls"]["potential_barcodes"][0]
            if isinstance(potential_barcode, dict):
                barcode = potential_barcode.get("barcode_id", "")
                barcode_source = "potential_barcodes"
        
        # Priority 3: Fallback to legacy barcode fields if new structure not available
        # This ensures backward compatibility with older API versions
        if not barcode:
            if "barcode" in product_info:
                barcode = str(product_info["barcode"]).strip()
                barcode_source = "legacy_barcode"
            elif "barcode_id" in product_info:
                barcode = str(product_info["barcode_id"]).strip()
                barcode_source = "legacy_barcode_id"
        
        # Set barcode field
        self._barcode = barcode.strip() if barcode else ""
        
        # Log barcode extraction details
        if self._barcode:
            logger.info(f"Extracted barcode '{self._barcode}' from {barcode_source} for product {product_info.get('item_code', 'Unknown')}")
        else:
            logger.warning(f"No barcode found for product {product_info.get('item_code', 'Unknown')} - checked existing_barcodes, potential_barcodes, and legacy fields")
        
        # Generate batch number with current date in YMD format
        current_date = datetime.now().strftime("%Y%m%d")
        self.batch_number.setText(current_date)
        
        # Load product image from API if available
        if "image" in product_info and product_info["image"]:
            # Image URL available from API
            image_url = str(product_info["image"]).strip()
            if image_url and image_url.lower() not in ['null', 'none', '']:
                logger.info(f"Loading product image from API: {image_url}")
                self.load_image(image_url)
            else:
                # Image field exists but is empty/null
                logger.info("Image field is empty/null, loading default image")
                self.load_default_image()
        else:
            # No image field in API response
            logger.info("No image field in API response, loading default image")
            self.load_default_image()
        
        # Keep target length at 0.0 - let user input manually
        # No automatic default value setting - user must input target length manually
        
        # Default to Meter unit if not specified
        if not self.meter_radio.isChecked() and not self.yard_radio.isChecked():
            self.meter_radio.setChecked(True)
            self._current_unit = "Meter"
        
        logger.info(f"Form populated with product data for: {product_info.get('item_code', 'Unknown')} - {product_info.get('item_name', '')}") 