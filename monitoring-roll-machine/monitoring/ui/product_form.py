from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QLabel, QHBoxLayout,
    QRadioButton, QButtonGroup, QSizePolicy, QMessageBox,
    QListWidget, QListWidgetItem, QDialog
)
from PySide6.QtCore import Signal, Qt, QSize, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from io import BytesIO
import logging
from datetime import datetime
import re
import json
import urllib.parse

from .connection_settings import ConnectionSettings
from ..batch_manager import get_batch_manager

# Setup logger
logger = logging.getLogger(__name__)


class ProductSearchWorker(QThread):
    """Worker thread for non-blocking API calls."""
    
    # Signals
    search_completed = Signal(dict)  # Emitted when search completes successfully
    search_failed = Signal(str, str)  # Emitted when search fails (error_type, message)
    
    # Class-level session for connection pooling
    _session = None
    
    def __init__(self, product_code: str, api_url: str, headers: Dict[str, str], request_id: str):
        super().__init__()
        self.product_code = product_code
        self.api_url = api_url
        self.headers = headers
        self.request_id = request_id  # Unique ID for this request
        
        # Initialize session if not exists
        if ProductSearchWorker._session is None:
            ProductSearchWorker._session = requests.Session()
            ProductSearchWorker._session.headers.update(headers)
            # Optimize session for better performance
            ProductSearchWorker._session.mount('http://', HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=1
            ))
            ProductSearchWorker._session.mount('https://', HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=1
            ))
        
    def run(self):
        """Run the API call in background thread with JSON format and exact match filtering."""
        try:
            # Ensure session is available
            if ProductSearchWorker._session is None:
                ProductSearchWorker._session = requests.Session()
                ProductSearchWorker._session.headers.update(self.headers)
                # Optimize session for better performance
                ProductSearchWorker._session.mount('http://', HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=20,
                    max_retries=1
                ))
                ProductSearchWorker._session.mount('https://', HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=20,
                    max_retries=1
                ))
                
            # Prepare JSON data
            json_data = {
                "product_code": self.product_code
            }
            
            # Make POST request with JSON data - reduced timeout to match Postman performance
            logger.info(f"Making API request to: {self.api_url}")
            logger.info(f"Request data: {json_data}")
            
            response = ProductSearchWorker._session.post(
                self.api_url,
                json=json_data,
                timeout=5  # Reduced from 15 to 5 seconds for faster response
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"API Response status: {response.status_code}")
            logger.info(f"API Response data: {data}")
            
            # Check if product data is found with new response structure
            if (data.get("message") and 
                isinstance(data["message"], dict) and 
                data["message"].get("success") and 
                data["message"].get("data", {}).get("products")):
                
                products = data["message"]["data"]["products"]
                if products:
                    # Log search behavior for monitoring
                    self._log_search_behavior(products)
                    
                    # Strategy 1: Try exact match first
                    exact_matches = [p for p in products if p.get('product_code') == self.product_code]
                    
                    if exact_matches:
                        # Found exact match
                        product_info = exact_matches[0]
                        product_info["_request_id"] = self.request_id
                        product_info["_search_type"] = "exact_match"
                        self.search_completed.emit(product_info)
                    else:
                        # Strategy 2: Try case-insensitive exact match
                        case_insensitive_matches = [p for p in products if p.get('product_code', '').upper() == self.product_code.upper()]
                        
                        if case_insensitive_matches:
                            product_info = case_insensitive_matches[0]
                            product_info["_request_id"] = self.request_id
                            product_info["_search_type"] = "case_insensitive_match"
                            self.search_completed.emit(product_info)
                        else:
                            # Strategy 3: Try partial match (for cases like SV-1 vs SV-1-60)
                            partial_matches = [p for p in products if self.product_code in p.get('product_code', '')]
                            
                            if partial_matches:
                                # Take the shortest match (most specific)
                                product_info = min(partial_matches, key=lambda x: len(x.get('product_code', '')))
                                product_info["_request_id"] = self.request_id
                                product_info["_search_type"] = "partial_match"
                                self.search_completed.emit(product_info)
                            else:
                                # Strategy 4: If only one product returned, use it (API might be doing exact search)
                                if len(products) == 1:
                                    product_info = products[0]
                                    product_info["_request_id"] = self.request_id
                                    product_info["_search_type"] = "single_result"
                                    self.search_completed.emit(product_info)
                                else:
                                    # No match found
                                    self.search_failed.emit("not_found", f"Product '{self.product_code}' not found (API returned {len(products)} products but no match)")
                else:
                    self.search_failed.emit("not_found", "Product not found")
            else:
                self.search_failed.emit("not_found", "Product not found")
                
        except requests.exceptions.Timeout:
            self.search_failed.emit("timeout", "Search timeout - please try again")
        except requests.exceptions.ConnectionError:
            self.search_failed.emit("connection", "Cannot connect to server")
        except Exception as e:
            self.search_failed.emit("error", f"Search error: {str(e)}")
    
    def _log_search_behavior(self, products):
        """Log search behavior for monitoring and debugging."""
        try:
            logger.info(f"=== SEARCH BEHAVIOR LOG ===")
            logger.info(f"Searched for: '{self.product_code}'")
            logger.info(f"API returned: {len(products)} products")
            
            # Log all returned products for debugging
            logger.info("All returned products:")
            for i, product in enumerate(products):
                logger.info(f"  {i+1}. {product.get('product_code')}: {product.get('product_name')}")
            
            exact_matches = [p for p in products if p.get('product_code') == self.product_code]
            logger.info(f"Exact matches: {len(exact_matches)}")
            
            if len(products) > 1:
                logger.warning(f"API returned multiple products for '{self.product_code}':")
                for product in products:
                    logger.warning(f"  - {product.get('product_code')}: {product.get('product_name')}")
            
            if exact_matches:
                logger.info(f"Exact match found: {exact_matches[0].get('product_name')}")
            else:
                logger.warning(f"No exact match found for '{self.product_code}'")
                logger.warning(f"Available products: {[p.get('product_code') for p in products]}")
                
        except Exception as e:
            logger.error(f"Error logging search behavior: {e}")

class ProductForm(QWidget):
    """Form for entering and editing product information."""
    
    # Signals
    product_updated = Signal(dict)
    reset_counter = Signal()  # Signal for resetting counter
    print_logged = Signal(dict)  # Signal for print logging
    close_cycle = Signal()  # Signal for closing cycle
    
    # Konstanta konversi
    METER_TO_YARD = 1.09361
    YARD_TO_METER = 0.9144
    DEFAULT_IMAGE_URL = "https://thumb.ac-illust.com/b1/b170870007dfa419295d949814474ab2_t.jpeg"
    
    # API Configuration
    API_BASE_URL = "https://erp.textilindo.com/api/method/textile_plus.overrides.api.product.search_product"
    API_HEADERS = {
        "Content-Type": "application/json"
        # Removed Authorization header - API might be public or need different auth
    }
    
    # Simple in-memory cache for product search results
    _product_cache = {}
    _cache_max_size = 100  # Maximum number of cached items
    
    # Search behavior monitoring (class variable for shared stats)
    _search_stats = {
        'total_searches': 0,
        'exact_matches': 0,
        'partial_matches': 0,
        'no_matches': 0,
        'api_issues': 0
    }
    
    def __init__(self):
        super().__init__()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_product_search)

        self._search_worker = None
        self._last_searched_code = ""
        self._is_updating = False
        self._barcode = ""
        self._image_url = None

        # Thread safety for preventing race conditions
        self._current_request_id = None
        self._last_user_input = ""
        self._current_machine_length = None
        self._current_unit = "Meter"  # Default unit
        self._last_valid_length = 0.0  # Store last valid length to prevent reset to 0

        # Initialize instance-specific search stats
        self._instance_search_stats = {
            'total_searches': 0,
            'exact_matches': 0,
            'partial_matches': 0,
            'no_matches': 0,
            'api_issues': 0
        }

        # Initialize batch manager
        # Load settings for batch manager
        try:
            from ..config import load_config
            config = load_config()
            self._batch_manager = get_batch_manager(settings=config)
        except Exception as e:
            logger.warning(f"Could not load config for batch manager: {e}")
            self._batch_manager = get_batch_manager()

        self.setup_ui()

        # Load BOM product code from settings
        self.load_bom_product_code()

        # Settings signals connection removed as BOM search is removed
        
    def load_bom_product_code(self):
        """Load BOM product code from settings and auto-fill product code field."""
        try:
            from ..config import load_config
            config = load_config()

            bom_product_code = config.get("bom_product_code", "")

            if bom_product_code:
                # Auto-fill product code
                self.product_code.setText(bom_product_code)
                self.product_code.setEnabled(False)  # Disable input
                self.product_code.setStyleSheet("""
                    QLineEdit {
                        background-color: #353535;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                        padding: 5px;
                        color: #888888;
                        font-size: 14px;
                        min-height: 40px;
                    }
                """)

                logger.info(f"BOM product code loaded: {bom_product_code}")

                # Also load BOM color code and product name if available
                bom_color_code = config.get("bom_color_code", "")
                bom_product_name = config.get("bom_product_name", "")

                if bom_color_code:
                    self.color_code.setText(bom_color_code)
                    logger.info(f"BOM color code loaded: {bom_color_code}")

                if bom_product_name:
                    self.product_name.setText(bom_product_name)
                    logger.info(f"BOM product name loaded: {bom_product_name}")

                # Trigger product search to populate/update other fields (image, barcode, etc.)
                logger.info("Triggering product search for BOM product code...")
                self._perform_product_search()

                # Update or add info label
                if hasattr(self, 'bom_info_label'):
                    self.bom_info_label.setText(f"✓ Using BOM Product Code: {bom_product_code}")
                else:
                    self.bom_info_label = QLabel(f"✓ Using BOM Product Code: {bom_product_code}")
                    self.bom_info_label.setStyleSheet("""
                        QLabel {
                            color: #4CAF50;
                            font-size: 11px;
                            font-weight: bold;
                            padding: 5px;
                            background-color: #1e3a1e;
                            border-radius: 3px;
                            border: 1px solid #4CAF50;
                        }
                    """)
                    # Insert after product code
                    form_frame = self.findChild(QFrame)
                    if form_frame:
                        layout = form_frame.layout()
                        if layout:
                            # Find product code row and insert after it
                            for i in range(layout.rowCount()):
                                if layout.itemAt(i, QFormLayout.ItemRole.LabelRole):
                                    label = layout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
                                    if label and label.text() == "Product Code:":
                                        layout.insertRow(i + 1, "", self.bom_info_label)
                                        break

                logger.info(f"BOM product code loaded: {bom_product_code}")
            else:
                # No BOM selected - enable product code input
                self.product_code.setEnabled(True)
                self.product_code.setStyleSheet("""
                    QLineEdit {
                        background-color: #353535;
                        border: 1px solid #ffa500;
                        border-radius: 4px;
                        padding: 5px;
                        color: white;
                        font-size: 14px;
                        min-height: 40px;
                    }
                """)

                # Remove info label if exists
                if hasattr(self, 'bom_info_label'):
                    self.bom_info_label.setVisible(False)

                logger.info("No BOM product code found in settings")

        except Exception as e:
            logger.error(f"Error loading BOM product code: {e}")

    def update_bom_button_visibility(self):
        """Update BOM button visibility based on is_verified status."""
        try:
            from ..config import load_config
            config = load_config()
            is_verified = config.get("is_verified", False)

            if hasattr(self, 'bom_search_button'):
                self.bom_search_button.setVisible(is_verified)
                logger.info(f"BOM button visibility updated: {'visible' if is_verified else 'hidden'}")

                # Also update the button's tooltip to reflect the current state
                if is_verified:
                    self.bom_search_button.setToolTip("Click to search and select BOM for product")
                else:
                    self.bom_search_button.setToolTip("BOM search disabled - verification required in settings")
        except Exception as e:
            logger.error(f"Error updating BOM button visibility: {e}")
        
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

        # Call update_bom_button_visibility after UI is set up to ensure button exists
        self.update_bom_button_visibility()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)  # Reduced margins for more compact layout
        main_layout.addWidget(form_frame)
        
        # Set size policy for compact layout
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setMaximumHeight(895)  # Reduced maximum height for more compact layout
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(3)  # Even more reduced spacing for more compact layout
        
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
        
        # Replace "Found" label with BOM search button (show/hide based on is_verified status)
        from ..config import load_config
        config = load_config()
        is_verified = config.get("is_verified", False)

        # Always create the button, but control visibility
        self.bom_search_button = QPushButton("BOM")
        self.bom_search_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 5px 10px;
                min-width: 50px;
                max-width: 50px;
                min-height: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        self.bom_search_button.clicked.connect(self.show_bom_search_dialog)
        self.bom_search_button.setVisible(is_verified)  # Control visibility based on is_verified

        # Set initial tooltip based on verification status
        if is_verified:
            self.bom_search_button.setToolTip("Click to search and select BOM for product")
        else:
            self.bom_search_button.setToolTip("BOM search disabled - verification required in settings")

        product_code_layout.addWidget(self.bom_search_button)
        
        form_layout.addRow("Product Code:", product_code_container)

        # BOM Selection Search Input removed as requested

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
        
        # Current Length (Readonly - from device)
        self.current_length = QDoubleSpinBox()
        self.current_length.setRange(0, 100000)
        self.current_length.setDecimals(2)
        self.current_length.setValue(0.0)  # Default to 0
        self.current_length.setReadOnly(True)  # Readonly - data from device
        self.current_length.setStyleSheet(input_style + """
            QDoubleSpinBox {
                background-color: #2a2a2a;
                color: #00ff00;
                font-weight: bold;
                padding-right: 5px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0;
                height: 0;
                border: none;
                background: none;
            }
        """)
        self.current_length.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_layout.addRow("Current Length:", self.current_length)
        
        # Target Length with buttons (to be sent to device)
        target_length_container = QWidget()
        target_length_layout = QHBoxLayout(target_length_container)
        target_length_layout.setSpacing(5)  # Reduced spacing
        target_length_layout.setContentsMargins(0, 0, 0, 0)
        
        # Target Length Input
        self.target_length = QSpinBox()
        self.target_length.setRange(0, 100000)
        self.target_length.setValue(0)  # Default to 0
        self.target_length.valueChanged.connect(self.on_length_changed)
        # Clear error styling when user changes value
        self.target_length.valueChanged.connect(lambda: self.clear_error(self.target_length))
        self.target_length.setStyleSheet(input_style + """
            QSpinBox {
                background-color: #353535;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
                color: white;
                font-size: 14px;
                min-height: 40px;
                padding-right: 5px;
            }
            QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0;
                height: 0;
                border: none;
                background: none;
            }
        """)
        # Allow manual input - remove setReadOnly(True)
        self.target_length.setReadOnly(False)  # Allow manual keyboard input
        self.target_length.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        target_length_layout.addWidget(self.target_length)
        
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
        target_length_layout.addWidget(self.plus_button)
        
        # Minus Button
        self.minus_button = QPushButton("-")
        self.minus_button.setFont(QFont("Segoe UI", 14))
        self.minus_button.clicked.connect(self.decrement_length)
        self.minus_button.setStyleSheet(button_style)
        self.minus_button.setFixedSize(55, 40)
        target_length_layout.addWidget(self.minus_button)
        
        form_layout.addRow("Target Length:", target_length_container)
        
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

        # Image and Print Preview Container
        image_preview_container = QWidget()
        image_preview_layout = QHBoxLayout(image_preview_container)
        image_preview_layout.setSpacing(10)
        image_preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Image Label (Left side)
        image_container = QWidget()
        image_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        # Set image size relative to form width - reduced for more compact layout
        self.image_label.setFixedSize(120, 120)  # Further reduced size
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #444444;
                border-radius: 4px;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        image_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Print Preview Button (Right side)
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(5)
        
        # Print Preview Button
        self.preview_button = QPushButton("Print Preview")
        self.preview_button.setFixedSize(120, 120)
        self.preview_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 2px dashed #666666;
                border-radius: 4px;
                color: #888888;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #353535;
                border: 2px dashed #888888;
                color: #aaaaaa;
            }
            QPushButton:pressed {
                background-color: #404040;
                border: 2px dashed #aaaaaa;
                color: #cccccc;
            }
        """)
        self.preview_button.clicked.connect(self.show_print_preview)
        preview_layout.addWidget(self.preview_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add both containers to the horizontal layout
        image_preview_layout.addWidget(image_container)
        image_preview_layout.addWidget(preview_container)
        
        form_layout.addRow(image_preview_container)
        
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
        

        # Print Button
        self.print_button = QPushButton("Print")
        self.print_button.setObjectName("print_button")
        self.print_button.clicked.connect(self.print_product_info)
        self.print_button.setStyleSheet(action_button_style)
        self.print_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(self.print_button)

        # Close Cycle Button
        self.close_cycle_button = QPushButton("Close Cycle")
        self.close_cycle_button.setObjectName("close_cycle_button")
        self.close_cycle_button.clicked.connect(self.close_cycle_with_save)
        self.close_cycle_button.setStyleSheet(action_button_style + "\n#close_cycle_button { background-color: #6c757d; }\n#close_cycle_button:hover { background-color: #5a6268; }\n#close_cycle_button:pressed { background-color: #495057; }")
        self.close_cycle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(self.close_cycle_button)
        
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
        
    def on_length_changed(self, value: int):
        """Handle length value change and automatically send to device."""
        if not self._is_updating:
            # Value changed by user, automatically send to device
            if value > 0:
                self.set_target_length_to_device()
            
    def reset_counter_with_save(self):
        """Langsung reset counter tanpa validasi input apapun."""
        logger.info("RESET COUNTER: Sending reset command to device (no validation)")
        self.reset_counter.emit()
        
    def print_product_info(self):
        """
        Save product information first, then print product label.
        Combines save and print functionality into one action.
        """
        # First, save the product information
        if not self._save_product_info():
            return  # If save failed, don't proceed with printing
            
        # Get current config for decimal points and selected printer
        from monitoring.config import load_config
        config = load_config()
        decimal_points = config.get("decimal_points", 1)
        selected_printer = config.get("selected_printer")
        
        # Log selected printer for debugging
        logger.info(f"Print button clicked - Selected printer: {selected_printer}")
        
        # Get product info with consistent field names for printing (same structure as print preview)
        product_info = {
            'product_code': self.product_code.text().strip(),
            'product_name': self.product_name.text().strip(),
            'color_code': self.color_code.text().strip(),
            'color': self.color_code.text().strip(),  # For backward compatibility
            'barcode': self._barcode,
            'batch_number': self.batch_number.text().strip(),
            'current_length': self.current_length.value(),
            'target_length': self.target_length.value(),
            'units': self.unit_group.checkedButton().text(),
            'image_url': self._image_url,  # Add image URL for attachment display
            'decimal_points': decimal_points,  # ← FIELD YANG HILANG! Sama dengan print preview
            'print_length': self.current_length.value()  # ← Tambahan untuk konsistensi
        }
        
        # Get current machine length for print calculations
        current_machine_length = getattr(self, '_current_machine_length', None)
        
        # Import and use printer utils for direct printing
        try:
            from .printer_utils import print_product_label
            # Pass selected_printer explicitly (same as test print in settings)
            success = print_product_label(product_info, current_machine_length, selected_printer)
            
            if success:
                logger.info("Print job sent successfully")
                # Emit print logged signal for logging
                self.emit_print_logged(product_info)
                
                # Show success message
                self._show_kiosk_dialog(
                    "information",
                    "Save & Print Success",
                    f"Product saved and print job sent successfully to '{selected_printer}'!\n\nBatch: {product_info['batch_number']}\nProduct: {product_info['product_code']}"
                )
            else:
                logger.error("Print job failed")
                self._show_kiosk_dialog(
                    "warning",
                    "Print Failed",
                    f"Product saved successfully, but print job failed.\n\nPlease check printer connection and settings."
                )
            
        except Exception as e:
            logger.error(f"Error printing product label: {e}")
            
            # Show error dialog
            self._show_kiosk_dialog(
                "critical",
                "Print Error",
                f"Product saved successfully, but error printing label:\n\n{str(e)}"
            )
    
    def emit_print_logged(self, print_data: dict):
        """Emit print logged signal to main window."""
        self.print_logged.emit(print_data)
        
    def validate_inputs(self) -> bool:
        """Validate form inputs."""
        if not self.product_code.text().strip():
            self.show_error(self.product_code, "Product code is required")
            return False
        
        # Check if product code is from BOM (locked field)
        is_bom_locked = not self.product_code.isEnabled()
        
        # For BOM mode, product name is optional (will use product code if empty)
        if not is_bom_locked and not self.product_name.text().strip():
            self.show_error(self.product_name, "Product name is required")
            return False
        
        # For BOM mode, use product code as product name if empty
        if is_bom_locked and not self.product_name.text().strip():
            logger.info("BOM mode: Using product code as product name")
            self.product_name.setText(self.product_code.text().strip())
        
        # For BOM mode, color code is optional (will use "0" if empty)
        if is_bom_locked and not self.color_code.text().strip():
            logger.info("BOM mode: Using default color code '0'")
            self.color_code.setText("0")
        elif not is_bom_locked and not self.color_code.text().strip():
            self.show_error(self.color_code, "Color code is required")
            return False
            
        # Target length and batch number are now optional (not required)
        # Only validate if they have values
        if self.target_length.value() > 0 and self.target_length.value() < 1:
            self.show_error(self.target_length, "Target panjang minimal 1")
            self._show_kiosk_dialog(
                "warning",
                "Target Length Too Small",
                "Target panjang terlalu kecil!\n\nMinimal panjang yang diizinkan adalah 1."
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
        if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
            # Reset to normal input style for spinbox
            input_style = """
                QSpinBox, QDoubleSpinBox {
                    background-color: #353535;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 5px;
                    color: white;
                    font-size: 14px;
                    min-height: 40px;
                }
                QSpinBox:focus, QDoubleSpinBox:focus {
                    border: 1px solid #0078d4;
                }
                QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    width: 0;
                    height: 0;
                    border: none;
                    background: none;
                }
                QSpinBox, QDoubleSpinBox {
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
            'current_length': self.current_length.value(),
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
        self.current_length.setValue(info.get('current_length', 0.0))
        self.target_length.setValue(info.get('target_length', 0))
        
        # Handle unit selection properly
        unit = info.get('unit', 'Meter')
        if unit.lower() in ['yard', 'yards', 'y']:
            self.yard_radio.setChecked(True)
            self._current_unit = "Yard"
        else:
            self.meter_radio.setChecked(True)
            self._current_unit = "Meter"

    def increment_length(self):
        """Increment target length by 1 and automatically send to device."""
        current_value = self.target_length.value()
        new_value = current_value + 1
        self.target_length.setValue(new_value)
        # Clear any error styling when user interacts
        self.clear_error(self.target_length)
        # Automatically send to device
        if new_value > 0:
            self.set_target_length_to_device()

    def decrement_length(self):
        """Decrement target length by 1 and automatically send to device."""
        current_value = self.target_length.value()
        if current_value > 0:  # Prevent negative values
            new_value = current_value - 1
            self.target_length.setValue(new_value)
            # Clear any error styling when user interacts
            self.clear_error(self.target_length)
            # Automatically send to device
            if new_value > 0:
                self.set_target_length_to_device()

    def update_target_with_current_length(self, current_length: float):
        """Update target length input with current length from monitoring (this will auto-send to device)."""
        if not self._is_updating:
            self._is_updating = True
            self.target_length.setValue(int(round(current_length, 0)))
            self._is_updating = False
    
    def update_target_with_length_print(self, length_print_text: str):
        """Update current length display with length print value from device."""
        if not self._is_updating:
            self._is_updating = True
            try:
                # Extract numeric value from length print text (e.g., "1.34 m" -> 1.34)
                match = re.search(r'(\d+\.?\d*)', length_print_text)
                if match:
                    length_value = float(match.group(1))
                    
                    # Prevent length reset to 0 - use last valid length if current is 0
                    if length_value > 0.001:  # If length is valid (> 0.001)
                        self._last_valid_length = length_value
                    
                    # Use last valid length if current is 0 or very small
                    display_length = length_value if length_value > 0.001 else getattr(self, '_last_valid_length', 0.0)
                    
                    # Update current length display (readonly) - this is the data from device
                    self.current_length.setValue(round(display_length, 2))
                    # logger.info(f"Updated current length display with length print value: {display_length}")
                else:
                    logger.warning(f"Could not extract numeric value from length print text: {length_print_text}")
            except Exception as e:
                logger.error(f"Error updating current length with length print: {e}")
            finally:
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

    def set_current_machine_length(self, current_length: float):
        """Set the current machine length for print preview."""
        self._current_machine_length = current_length
        # Note: current_length display is updated by update_target_with_length_print

    def set_target_length_to_device(self):
        """Send target length to device using JSK3588 protocol commands 10 and 11."""
        try:
            target_value = self.target_length.value()
            if target_value <= 0:
                self._show_kiosk_dialog(
                    "warning",
                    "Invalid Target Length",
                    "Target length must be greater than 0."
                )
                return
            
            # For JSK3588 protocol, we send the value directly (no multiplication)
            # The device expects the value as-is
            target_int = int(target_value)
            
            # Ensure value is within valid range (0-255 for single byte)
            if target_int > 255:
                logger.error(f"Value too large for JSK3588 protocol: {target_int}")
                self._show_kiosk_dialog(
                    "warning",
                    "Value Too Large",
                    f"Target length {target_value} is too large for JSK3588 protocol.\nMaximum value: 255"
                )
                return
            
            # For JSK3588 protocol, we use the value directly
            d3d2_int = 0  # High byte (always 0 for values <= 255)
            d1d0_int = target_int  # Low byte (the actual value)
            
            # Calculate checksums
            checksum1 = (0x55 + 0xAA + 0x0A + 0x00 + 0x00 + d3d2_int) & 0xFF
            checksum2 = (0x55 + 0xAA + 0x0B + 0x00 + d1d0_int + 0x00) & 0xFF
            
            # Create commands
            command1 = f"55 AA 0A 00 00 {d3d2_int:02X} {checksum1:02X}"
            command2 = f"55 AA 0B 00 {d1d0_int:02X} 00 {checksum2:02X}"
            
            logger.info(f"Setting target length to device: {target_value}")
            logger.info(f"Target value: {target_int} (D3D2: 0x00, D1D0: 0x{target_int:02X})")
            logger.info(f"Command 1: {command1}")
            logger.info(f"Command 2: {command2}")
            
            # Find main window and send commands through serial
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
            for widget in app.topLevelWidgets():
                if hasattr(widget, 'monitor') and widget.monitor and widget.monitor.is_running:
                    if hasattr(widget.monitor, 'serial_port') and widget.monitor.serial_port:
                        # Send first command
                        widget.monitor.serial_port.send_hex(command1)
                        logger.info("Sent first command to device")
                        
                        # Wait 500ms before sending second command (must be within 1 second)
                        import time
                        time.sleep(0.5)
                        
                        # Send second command
                        widget.monitor.serial_port.send_hex(command2)
                        logger.info("Sent second command to device")
                        
                        # No success dialog needed since it's automatic
                        return
                    else:
                        logger.error("Serial port not available")
                        break
            
            # If we get here, no suitable main window found
            self._show_kiosk_dialog(
                "warning",
                "Device Not Connected",
                "Cannot set target length: Device not connected or monitoring not active."
            )
            
        except Exception as e:
            logger.error(f"Error setting target length to device: {e}")
            self._show_kiosk_dialog(
                "critical",
                "Set Target Error",
                f"Error setting target length to device:\n\n{str(e)}"
            )

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
                # Store the image URL for attachment print widget
                self._image_url = url
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

    def show_print_preview(self):
        """Show print preview dialog."""
        if not self.validate_inputs():
            return
            
        # Get current config for decimal points
        from monitoring.config import load_config
        config = load_config()
        decimal_points = config.get("decimal_points", 1)
            
        # Get product info for preview
        product_info = {
            'product_code': self.product_code.text().strip(),
            'product_name': self.product_name.text().strip(),
            'color_code': self.color_code.text().strip(),
            'color': self.color_code.text().strip(),  # For backward compatibility
            'barcode': self._barcode,
            'batch_number': self.batch_number.text().strip(),
            'current_length': self.current_length.value(),
            'target_length': self.target_length.value(),
            'units': self.unit_group.checkedButton().text(),
            'image_url': self._image_url,
            'decimal_points': decimal_points,
            'print_length': self.current_length.value()  # Ensure consistency with direct print
        }
        
        # Get current machine length for print calculations
        current_machine_length = getattr(self, '_current_machine_length', None)
        
        # Create and show print preview dialog
        try:
            from .print_preview import PrintPreviewDialog
            preview_dialog = PrintPreviewDialog(product_info, current_machine_length, self)
            preview_dialog.exec()
        except Exception as e:
            logger.error(f"Error showing print preview: {e}")
            self._show_kiosk_dialog(
                "critical",
                "Print Preview Error",
                f"Error showing print preview:\n\n{str(e)}"
            )

    def _save_product_info(self) -> bool:
        """
        Internal method to save product information with auto-batch generation and Supabase integration.
        Returns True if save was successful, False otherwise.
        """
        if not self.validate_inputs():
            return False

        # Get product code
        product_code = self.product_code.text().strip()

        # Auto-generate batch number based on product code
        # If batch_number field is empty, generate automatically
        # Otherwise, use the manual batch number
        batch_number_input = self.batch_number.text().strip()
        if not batch_number_input:
            # Ensure batch_manager has latest settings
            try:
                from ..config import load_config
                config = load_config()
                self._batch_manager.update_settings(config)
            except Exception as e:
                logger.warning(f"Could not update batch manager settings: {e}")

            # Get color code for batch generation
            color_code = self.color_code.text().strip() if hasattr(self, 'color_code') else ""
            batch_number = self._batch_manager.get_batch_for_product(product_code, color_code)
            # Update the batch_number field with auto-generated batch
            self.batch_number.setText(batch_number)
            logger.info(f"Auto-generated batch: {batch_number} for product: {product_code}")
        else:
            batch_number = batch_number_input
            logger.info(f"Using manual batch: {batch_number}")

        # Create product info dictionary with consistent field names
        product_info = {
            'product_code': product_code,
            'product_name': self.product_name.text().strip(),
            'color_code': self.color_code.text().strip(),
            'color': self.color_code.text().strip(),  # For backward compatibility
            'barcode': self._barcode,
            'batch_number': batch_number,
            'current_length': self.current_length.value(),
            'target_length': self.target_length.value(),
            'units': self.unit_group.checkedButton().text()
        }

        # Dual-save batch metadata: local storage FIRST, then Supabase
        try:
            # Prepare batch metadata
            batch_metadata = {
                'batch': batch_number,
                'product_code': product_code,
                'product_name': self.product_name.text().strip(),
                'color_code': self.color_code.text().strip(),
                'target_length': self.target_length.value(),
                'units': self.unit_group.checkedButton().text(),
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # 1. Save to local storage FIRST (always succeeds)
            from ..batch_metadata_store import get_batch_metadata_store
            metadata_store = get_batch_metadata_store()
            local_saved = metadata_store.save_batch_metadata(batch_metadata)
            
            if local_saved:
                logger.info(f"Batch metadata saved to local storage: {batch_number}")
            else:
                logger.error(f"Failed to save batch metadata to local storage: {batch_number}")
            
            # 2. Try to save to Supabase (may fail, but will be queued automatically)
            from ..supabase_client import get_supabase_client
            supabase_client = get_supabase_client()
            
            if supabase_client.is_connected:
                logger.info(f"Saving batch to Supabase: {batch_number}")
                result = supabase_client.insert_batch_metadata(batch_metadata)
                
                if result:
                    logger.info(f"Batch metadata saved to Supabase successfully: {batch_number}")
                else:
                    logger.warning(f"Failed to save batch metadata to Supabase (queued for retry): {batch_number}")
            else:
                logger.info("Supabase not connected, batch queued for sync when connection restored")

        except Exception as e:
            logger.error(f"Error saving batch metadata: {e}")
            # Local save should still succeed, so don't fail the operation

        # Emit the product_updated signal for backward compatibility
        self.product_updated.emit(product_info)
        
        return True

    def close_cycle_with_save(self):
        """Emit signal to close the current cycle and get final cycle time."""
        logger.info("CLOSE CYCLE: Sending close cycle command to device")
        self.close_cycle.emit()

    def _on_product_code_changed(self):
        """Handle text change in product code input."""
        # Track current user input
        self._last_user_input = self.product_code.text().strip()
        
        # Set delay to 3 seconds (3000ms) as requested
        self._search_timer.start(1000)  # Start timer for delayed search

    def _on_product_code_finished(self):
        """Handle editing finished in product code input."""
        self._search_timer.stop()  # Stop timer
        self._perform_product_search()

    def _get_cached_product(self, product_code: str) -> Optional[Dict[str, Any]]:
        """Get product from cache if available."""
        return self._product_cache.get(product_code)

    def _cache_product(self, product_code: str, product_info: Dict[str, Any]):
        """Cache product information."""
        # Implement simple LRU-like cache management
        if len(self._product_cache) >= self._cache_max_size:
            # Remove oldest entry (simple approach - remove first item)
            oldest_key = next(iter(self._product_cache))
            del self._product_cache[oldest_key]
        
        self._product_cache[product_code] = product_info
    
    def _clear_cache_entry(self, product_code: str):
        """Clear specific cache entry."""
        if product_code in self._product_cache:
            del self._product_cache[product_code]
            logger.info(f"Cleared cache entry for: {product_code}")
    
    def clear_all_cache(self):
        """Clear all cached products."""
        self._product_cache.clear()
        logger.info("Cleared all product cache")
    
    def test_search_with_real_data(self, product_code: str):
        """Test search with real API data for debugging."""
        logger.info(f"=== TESTING SEARCH WITH REAL DATA ===")
        logger.info(f"Testing search for: '{product_code}'")
        
        # Clear cache first
        self.clear_all_cache()
        
        # Set the product code
        self.product_code.setText(product_code)
        
        # Trigger search
        self._perform_product_search()
    
    def debug_cache_status(self):
        """Debug cache status."""
        logger.info(f"=== CACHE STATUS ===")
        logger.info(f"Cache size: {len(self._product_cache)}")
        logger.info(f"Cache max size: {self._cache_max_size}")
        logger.info("Cached products:")
        for product_code, product_info in self._product_cache.items():
            logger.info(f"  - {product_code}: {product_info.get('product_name', 'Unknown')}")
    
    def debug_search_status(self):
        """Debug search status."""
        logger.info(f"=== SEARCH STATUS ===")
        logger.info(f"Last searched code: '{self._last_searched_code}'")
        logger.info(f"Last user input: '{self._last_user_input}'")
        logger.info(f"Current request ID: '{self._current_request_id}'")
        logger.info(f"Search worker running: {self._search_worker.isRunning() if self._search_worker else False}")

    def _cancel_current_search(self):
        """Cancel current search worker and cleanup."""
        if self._search_worker and self._search_worker.isRunning():
            logger.info("Cancelling current search worker")
            self._search_worker.terminate()
            self._search_worker.wait(1000)  # Wait up to 1 second
            if self._search_worker.isRunning():
                logger.warning("Force killing search worker")
                self._search_worker.terminate()
                self._search_worker.wait()
        
        # Reset current request ID
        self._current_request_id = None

    def _perform_product_search(self):
        """Perform product search with new API format (JSON)."""
        try:
            product_code = self.product_code.text().strip()
            
            if len(product_code) < 3:
                return
                
            # Update last searched code and user input
            self._last_searched_code = product_code
            self._last_user_input = product_code
            
            # Check cache first - but validate match
            cached_product = self._get_cached_product(product_code)
            if cached_product:
                # Validate that cached product matches (exact or case-insensitive)
                cached_code = cached_product.get('product_code', '')
                if (cached_code == product_code or 
                    cached_code.upper() == product_code.upper() or
                    (product_code in cached_code and len(product_code) >= 3)):
                    logger.info(f"Product found in cache (match): {product_code} -> {cached_code}")
                    # Add request_id for consistency
                    cached_product["_request_id"] = "cache"
                    self._on_search_completed(cached_product)
                    return
                else:
                    logger.warning(f"Cached product mismatch: expected '{product_code}', got '{cached_code}'")
                    # Remove invalid cache entry
                    self._clear_cache_entry(product_code)
            
            self._set_search_status("Searching...", "#ffa500", "Searching for product...")
            
            # Set loading style for product code input
            self.product_code.setStyleSheet(self.loading_style)
            
            # Cancel previous search if running
            self._cancel_current_search()
            
            # Get API settings from config or use defaults
            api_url = self.get_api_url()
            api_key = self.get_api_key()
            timeout = self.get_api_timeout()
            
            # Prepare headers for JSON format
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Add API key if provided
            if api_key:
                headers["Authorization"] = f"token {api_key}"
            
            # Generate a unique request ID
            import uuid
            request_id = str(uuid.uuid4())
            self._current_request_id = request_id
            
            # Start new search in background thread with new format
            self._search_worker = ProductSearchWorker(product_code, api_url, headers, request_id)
            self._search_worker.search_completed.connect(self._on_search_completed)
            self._search_worker.search_failed.connect(self._on_search_failed)
            self._search_worker.start()
            
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            self._on_search_failed("error", f"Search error: {str(e)}")
            
    def _on_search_completed(self, product_info: Dict[str, Any]):
        """Handle successful search completion with exact match validation."""
        # Check if product code is from BOM (locked field)
        is_bom_locked = not self.product_code.isEnabled()
        
        # Thread safety check - only process if this is the current request
        request_id = product_info.get("_request_id")
        current_user_input = self.product_code.text().strip()
        
        # Check if this result is still relevant
        if (request_id != self._current_request_id and 
            request_id != "cache" and 
            current_user_input != self._last_user_input):
            logger.info(f"Ignoring stale search result for request {request_id}")
            return
        
        # Check if user input has changed since this search started (skip for BOM locked fields)
        if not is_bom_locked and current_user_input != self._last_user_input:
            logger.info(f"Ignoring search result - user input changed from {self._last_user_input} to {current_user_input}")
            return
        
        # Validate match (only for API results, not cache)
        if request_id != "cache":
            searched_code = self.product_code.text().strip()
            returned_code = product_info.get('product_code', '')
            search_type = product_info.get('_search_type', 'unknown')
            
            # Check if the returned product is acceptable
            is_valid_match = (
                returned_code == searched_code or  # Exact match
                returned_code.upper() == searched_code.upper() or  # Case-insensitive
                searched_code in returned_code or  # Partial match
                search_type in ['exact_match', 'case_insensitive_match', 'partial_match', 'single_result']  # Valid search types
            )
            
            if not is_valid_match:
                logger.warning(f"Product code mismatch: searched for '{searched_code}', got '{returned_code}' (type: {search_type})")
                self._on_search_failed("mismatch", f"Product code mismatch: expected '{searched_code}', got '{returned_code}'")
                return
        
        # Update search statistics
        self._update_search_stats("exact_matches")
        
        # Cache the result (only for API results, not cache hits)
        if request_id != "cache":
            product_code = self.product_code.text().strip()
            # Remove internal fields before caching
            cache_product_info = product_info.copy()
            cache_product_info.pop("_request_id", None)
            cache_product_info.pop("_search_type", None)
            self._cache_product(product_code, cache_product_info)
        
        # Remove internal fields before populating form
        product_info.pop("_request_id", None)
        product_info.pop("_search_type", None)
        
        self._populate_form_from_api(product_info)
        
        # Show appropriate status based on search type
        search_type = product_info.get('_search_type', 'exact_match')
        if search_type == 'exact_match':
            status_text = "Found ✓"
            status_color = "#28a745"
        elif search_type == 'case_insensitive_match':
            status_text = "Found (CI) ✓"
            status_color = "#28a745"
        elif search_type == 'partial_match':
            status_text = "Found (Partial) ✓"
            status_color = "#ffc107"
        elif search_type == 'single_result':
            status_text = "Found (Single) ✓"
            status_color = "#17a2b8"
        else:
            status_text = "Found ✓"
            status_color = "#28a745"
        
        self._set_search_status(status_text, status_color, f"Found: {product_info.get('product_name', 'Product')} ({search_type})")
        self._reset_input_style()
        
        # Re-lock product code field if it's from BOM
        if is_bom_locked:
            self.product_code.setEnabled(False)
            self.product_code.setStyleSheet("""
                QLineEdit {
                    background-color: #353535;
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                    padding: 5px;
                    color: #888888;
                    font-size: 14px;
                    min-height: 40px;
                }
            """)
            logger.info("Product code field re-locked after search (BOM mode)")
        
    def _on_search_failed(self, error_type: str, message: str):
        """Handle search failure with enhanced error handling."""
        # Check if product code is from BOM (locked field)
        is_bom_locked = not self.product_code.isEnabled()
        
        # Thread safety check - only process if user input hasn't changed
        current_user_input = self.product_code.text().strip()
        if current_user_input != self._last_user_input:
            logger.info(f"Ignoring search failure - user input changed from {self._last_user_input} to {current_user_input}")
            return
        
        # Update search statistics
        if error_type == "not_found":
            self._update_search_stats("no_matches")
        elif error_type == "mismatch":
            self._update_search_stats("api_issues")
        else:
            self._update_search_stats("api_issues")
        
        # Enhanced status mapping with icons
        status_map = {
            "not_found": "Not Found ✗",
            "mismatch": "Mismatch ✗",
            "timeout": "Timeout ⏱",
            "connection": "No Connection 🔌",
            "error": "Error ❌"
        }
        
        color_map = {
            "not_found": "#ff4444",
            "mismatch": "#ff4444",
            "timeout": "#ffc107", 
            "connection": "#dc3545",
            "error": "#dc3545"
        }
        
        # Show user-friendly dialog for mismatch
        if error_type == "mismatch":
            self._show_kiosk_dialog(
                "warning",
                "Search Precision Issue",
                f"The search for '{current_user_input}' returned a different product.\n\n"
                f"This might be due to API search behavior. Please verify the product code."
            )
        
        self._set_search_status(
            status_map.get(error_type, "Error ❌"),
            color_map.get(error_type, "#dc3545"),
            message
        )
        self._reset_input_style()
        
        # Re-lock product code field if it's from BOM
        if is_bom_locked:
            self.product_code.setEnabled(False)
            self.product_code.setStyleSheet("""
                QLineEdit {
                    background-color: #353535;
                    border: 1px solid #4CAF50;
                    border-radius: 4px;
                    padding: 5px;
                    color: #888888;
                    font-size: 14px;
                    min-height: 40px;
                }
            """)
            # For BOM locked fields, don't show error dialog
            logger.warning(f"Product search failed for BOM product code: {error_type} - {message}")
            logger.warning("BOM product code will remain but other fields may be empty")
        else:
            logger.error(f"Search failed: {error_type} - {message}")
    
    def _update_search_stats(self, stat_type: str):
        """Update search statistics for monitoring."""
        try:
            # Update both class and instance stats
            self._search_stats['total_searches'] += 1
            self._instance_search_stats['total_searches'] += 1
            
            if stat_type in self._search_stats:
                self._search_stats[stat_type] += 1
                self._instance_search_stats[stat_type] += 1
            
            # Log statistics periodically (every 10 searches)
            if self._search_stats['total_searches'] % 10 == 0:
                self._log_search_statistics()
                
        except Exception as e:
            logger.error(f"Error updating search stats: {e}")
    
    def _log_search_statistics(self):
        """Log search statistics for monitoring."""
        try:
            stats = self._search_stats
            total = stats['total_searches']
            
            if total > 0:
                exact_rate = (stats['exact_matches'] / total) * 100
                issue_rate = ((stats['api_issues'] + stats['no_matches']) / total) * 100
                
                logger.info(f"=== SEARCH STATISTICS ===")
                logger.info(f"Total searches: {total}")
                logger.info(f"Exact matches: {stats['exact_matches']} ({exact_rate:.1f}%)")
                logger.info(f"No matches: {stats['no_matches']}")
                logger.info(f"API issues: {stats['api_issues']}")
                logger.info(f"Overall success rate: {exact_rate:.1f}%")
                logger.info(f"Issue rate: {issue_rate:.1f}%")
                
                # Alert if issue rate is high
                if issue_rate > 20:
                    logger.warning(f"High search issue rate detected: {issue_rate:.1f}%")
                    
        except Exception as e:
            logger.error(f"Error logging search statistics: {e}")
    
    def get_search_stats(self):
        """Get search statistics for this instance."""
        return self._instance_search_stats.copy()
    
    def clear_form(self):
        """Clear all form fields."""
        try:
            self.product_name.setText("")
            self.color_code.setText("")
            self.batch_number.setText("")
            self.target_length.setValue(0)
            self.current_length.setValue(0)
            self._barcode = ""
            self._image_url = None
            self.load_default_image()
            logger.info("Form cleared")
        except Exception as e:
            logger.error(f"Error clearing form: {e}")

    def search_bom(self, search_text: str):
        """Search BOM by product code in real-time."""
        try:
            if not search_text or len(search_text) < 2:
                self.bom_results_list.clear()
                self.bom_results_list.setVisible(False)
                return

            # Get ERP URL and credentials from config
            from ..config import load_config
            config = load_config()
            erp_url = config.get("erp_url", "")
            api_key = config.get("erp_api_key", "")
            api_secret = config.get("erp_api_secret", "")

            if not erp_url or not api_key or not api_secret:
                logger.warning("ERP settings not configured for BOM search")
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

    def select_bom_and_close(self, item: QListWidgetItem, dialog: QDialog):
        """Handle BOM selection from dialog and close dialog."""
        try:
            bom_data = item.data(Qt.ItemDataRole.UserRole)

            if bom_data:
                bom_name = bom_data.get("name", "")
                item_name = bom_data.get("item", "")
                item_code = bom_data.get("item_code", "")

                # Auto-fill product code
                self.product_code.setText(item_code)
                self.product_code.setEnabled(False)  # Disable input
                self.product_code.setStyleSheet("""
                    QLineEdit {
                        background-color: #353535;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                        padding: 5px;
                        color: #888888;
                        font-size: 14px;
                        min-height: 40px;
                    }
                """)

                # Try to get item details to fill other fields
                try:
                    from ..config import load_config
                    config = load_config()
                    api_url = config.get('api_url', '')
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
                                        self.product_name.setText(product.get('product_name', ''))
                                        color_code = product.get('color_code', '')
                                        if color_code:
                                            self.color_code.setText(str(color_code))
                                        logger.info(f"Fetched product details for BOM: {item_code}")
                except Exception as e:
                    logger.warning(f"Could not fetch product details for BOM: {e}")

                # Close dialog
                dialog.accept()

                logger.info(f"BOM selected: {bom_name} - {item_code}")

        except Exception as e:
            logger.error(f"Error selecting BOM: {e}")
            dialog.reject()

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

    def show_bom_search_dialog(self):
        """Show BOM search dialog when BOM button is clicked."""
        try:
            # Create dialog for BOM search
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel
            from PySide6.QtCore import Qt

            dialog = QDialog(self)
            dialog.setWindowTitle("BOM Selection")
            dialog.setMinimumWidth(500)
            dialog.setMinimumHeight(400)
            dialog.setModal(True)

            # Set window flags for proper dialog behavior
            dialog.setWindowFlags(
                Qt.WindowType.Dialog |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.WindowSystemMenuHint |
                Qt.WindowType.WindowTitleHint
            )

            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Title
            title = QLabel("<b>Select BOM</b>")
            title.setStyleSheet("font-size: 16px; color: #0078d4;")
            layout.addWidget(title)

            # Description
            desc = QLabel("Search and select a BOM to auto-fill product information:")
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666666; margin-bottom: 10px;")
            layout.addWidget(desc)

            # Search input
            search_layout = QHBoxLayout()
            search_label = QLabel("Search BOM:")
            search_layout.addWidget(search_label)

            self.bom_search_input = QLineEdit()
            self.bom_search_input.setPlaceholderText("Enter product code to search BOM...")
            self.bom_search_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border: 1px solid #0078d4;
                }
            """)
            self.bom_search_input.textChanged.connect(lambda text: self.search_bom(text))
            search_layout.addWidget(self.bom_search_input)
            layout.addLayout(search_layout)

            # Results list
            self.bom_results_list = QListWidget()
            self.bom_results_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: white;
                    font-size: 14px;
                }
                QListWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }
                QListWidget::item:hover {
                    background-color: #f0f0f0;
                }
                QListWidget::item:selected {
                    background-color: #0078d4;
                    color: white;
                }
            """)
            self.bom_results_list.itemDoubleClicked.connect(lambda item: self.select_bom_and_close(item, dialog))
            self.bom_results_list.setVisible(False)
            layout.addWidget(self.bom_results_list)

            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)

            # Show dialog
            dialog.exec()

        except Exception as e:
            logger.error(f"Error showing BOM search dialog: {e}")
            self._show_kiosk_dialog(
                "critical",
                "BOM Search Error",
                f"Error showing BOM search dialog:\n\n{str(e)}"
            )

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

    def get_api_url(self):
        """Get API URL from config or use default."""
        # TODO: Get from config when available
        return self.API_BASE_URL
    
    def get_api_key(self):
        """Get API key from config or use default."""
        # TODO: Get from config when available
        return ""
    
    def get_api_timeout(self):
        """Get API timeout from config or use default."""
        # TODO: Get from config when available
        return 3  # Reduced from 15 to 3 seconds for faster response
    
    def _populate_form_from_api(self, product_info: Dict[str, Any]):
        """Populate form fields from API response data with new format."""
        try:
            # Thread safety check - don't update if user is currently typing
            current_user_input = self.product_code.text().strip()
            if current_user_input != self._last_user_input:
                logger.info(f"Skipping form population - user input changed from {self._last_user_input} to {current_user_input}")
                return
            
            self._is_updating = True
            
            # Store current cursor position
            cursor_pos = self.product_code.cursorPosition()
            
            # Map new API fields to form fields
            # Don't overwrite product_code if user is still typing
            if not self.product_code.hasFocus() or current_user_input == self._last_user_input:
                self.product_code.setText(product_info.get("product_code", ""))
                # Restore cursor position
                self.product_code.setCursorPosition(cursor_pos)
            
            self.product_name.setText(product_info.get("product_name", ""))
            
            # Handle color_code (might be null)
            color_code = product_info.get("color_code")
            if color_code:
                self.color_code.setText(str(color_code))
            else:
                self.color_code.setText("")
            
            # Handle barcode (now it's a list)
            barcodes = product_info.get("barcode", [])
            if barcodes:
                self._barcode = barcodes[0]  # Take first barcode
            else:
                self._barcode = ""
            
            # Handle attachment (might be null)
            attachment = product_info.get("attachment")
            if attachment:
                self.load_image(attachment)
            else:
                self.load_default_image()
        
            # Clear batch number for manual input
            self.batch_number.setText("")
            
            # Clear current length and target length
            self.current_length.setValue(0.0)
            self.target_length.setValue(0)
            
            self._is_updating = False
            self._clear_search_status()
            
        except Exception as e:
            logger.error(f"Error populating form from API: {e}")
            self._is_updating = False
            self._clear_search_status()

    # BOM-related methods removed as BOM search input is removed