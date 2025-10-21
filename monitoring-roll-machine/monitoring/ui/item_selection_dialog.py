"""
Interactive dialog for selecting source and finished items for ERP Stock Entry.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from typing import Dict, Any, List, Optional, Tuple
import logging
import requests

logger = logging.getLogger(__name__)


class ItemSelectionDialog(QDialog):
    """Dialog for selecting BOM and finished item."""
    
    # Signals
    items_selected = Signal(str, str)  # bom_name, finished_item_code
    
    def __init__(self, api_url: str, erp_client, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.api_url = api_url
        self.erp_client = erp_client
        self.config = config
        self.bom_name = None
        self.finished_item = None
        
        self.setWindowTitle("Select Items for Stock Entry")
        self.setMinimumSize(800, 600)
        
        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint
        )
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            QListWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444444;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QListWidget::item:hover {
                background-color: #2d5a7d;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cc1;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        
        # Header
        header_label = QLabel("🔍 Select BOM and Finished Item")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel(
            "Select the BOM (Bill of Materials) for source items and the finished product.\n"
            "The BOM determines which raw materials will be consumed."
        )
        instructions.setStyleSheet("color: #888888; font-size: 12px; font-style: italic;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # BOM Selection Section (replaces Source Item)
        self.create_bom_selection_section(layout)
        
        # Finished Item Section
        self.create_finished_item_section(layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.submit_btn = QPushButton("✅ Submit to ERP")
        self.submit_btn.setEnabled(False)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.submit_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.submit_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_bom_selection_section(self, parent_layout):
        """Create BOM selection section."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 2px solid #ff6b6b;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        # Label
        label = QLabel("📋 BOM (Bill of Materials)")
        label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        label.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(label)
        
        # Check if BOM is configured
        bom_from_config = self.config.get('bom_name', '')
        
        if bom_from_config:
            # Show configured BOM
            info_label = QLabel(f"Using configured BOM: <b>{bom_from_config}</b>")
            info_label.setStyleSheet("color: #28a745; font-size: 12px;")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
            
            # Auto-select this BOM
            self.bom_name = bom_from_config
            self.bom_selected_label = QLabel(f"✅ Selected: {bom_from_config}")
            self.bom_selected_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-weight: bold;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(self.bom_selected_label)
        else:
            # Manual BOM input
            self.bom_input = QLineEdit()
            self.bom_input.setPlaceholderText("Enter BOM name (e.g., BOM-SV-1-002)")
            layout.addWidget(self.bom_input)
            
            # Selected BOM display
            self.bom_selected_label = QLabel("No BOM entered")
            self.bom_selected_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-weight: bold;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(self.bom_selected_label)
            
            # Connect signal to update BOM name
            self.bom_input.textChanged.connect(self.on_bom_text_changed)
        
        parent_layout.addWidget(frame)
    
    def create_finished_item_section(self, parent_layout):
        """Create finished item (product) selection section."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        # Label
        label = QLabel("✅ Finished Item (Product)")
        label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        label.setStyleSheet("color: #28a745;")
        layout.addWidget(label)
        
        # Search input
        self.finished_search_input = QLineEdit()
        self.finished_search_input.setPlaceholderText("Type to search item code or name...")
        self.finished_search_input.textChanged.connect(self.search_finished_items)
        layout.addWidget(self.finished_search_input)
        
        # Results list
        self.finished_list = QListWidget()
        self.finished_list.itemClicked.connect(self.on_finished_item_selected)
        layout.addWidget(self.finished_list)
        
        # Selected item display
        self.finished_selected_label = QLabel("No item selected")
        self.finished_selected_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-weight: bold;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.finished_selected_label)
        
        parent_layout.addWidget(frame)
    
    def on_bom_text_changed(self, text: str):
        """Handle BOM input text change."""
        text = text.strip()
        if text:
            self.bom_name = text
            self.bom_selected_label.setText(f"✅ BOM: {text}")
            self.bom_selected_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-weight: bold;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                }
            """)
        else:
            self.bom_name = None
            self.bom_selected_label.setText("No BOM entered")
            self.bom_selected_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-weight: bold;
                    padding: 5px;
                    background-color: #1e1e1e;
                    border-radius: 3px;
                }
            """)
        self._update_submit_button()
    
    def search_finished_items(self, text: str):
        """Search for finished items using API."""
        if len(text) < 2:
            self.finished_list.clear()
            return
        
        # Debounce search
        if hasattr(self, 'finished_search_timer'):
            self.finished_search_timer.stop()
        
        self.finished_search_timer = QTimer()
        self.finished_search_timer.setSingleShot(True)
        self.finished_search_timer.timeout.connect(lambda: self._perform_search(text, 'finished'))
        self.finished_search_timer.start(300)  # 300ms debounce
    
    def _perform_search(self, query: str, item_type: str):
        """Perform API search for items."""
        try:
            logger.info(f"Searching {item_type} items for: {query}")
            logger.info(f"API URL: {self.api_url}")
            
            # Call the product search API
            # The API expects: POST with JSON body containing 'product_code'
            # Same format as ProductSearchWorker in product_form.py
            response = requests.post(
                self.api_url,
                json={
                    'product_code': query
                },
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=10
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                
                # Handle nested message structure from textile_plus API
                if isinstance(data.get('message'), dict):
                    message_obj = data.get('message', {})
                    logger.info(f"Message object keys: {list(message_obj.keys())}")
                    logger.info(f"Success: {message_obj.get('success')}")
                    
                    if message_obj.get('success'):
                        # Data is nested: message.data.products
                        data_obj = message_obj.get('data', {})
                        logger.info(f"Data object type: {type(data_obj)}")
                        
                        if isinstance(data_obj, dict):
                            items = data_obj.get('products', [])
                            logger.info(f"Extracted {len(items)} products from data.products")
                        elif isinstance(data_obj, list):
                            items = data_obj
                            logger.info(f"Data is list with {len(items)} items")
                        else:
                            items = []
                            logger.warning(f"Data object is neither dict nor list: {type(data_obj)}")
                    else:
                        items = []
                        logger.warning(f"API returned success=false: {message_obj.get('message')}")
                elif isinstance(data.get('message'), list):
                    # Format: {"message": [...]}
                    items = data.get('message', [])
                elif isinstance(data, list):
                    # Format: [...]
                    items = data
                elif isinstance(data.get('data'), list):
                    # Format: {"data": [...]}
                    items = data.get('data', [])
                else:
                    items = []
                
                logger.info(f"Found {len(items)} {item_type} items")
                
                if not items:
                    logger.warning(f"No items found for query: {query}")
                    logger.warning(f"Response data structure: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                
                # Update the appropriate list
                if item_type == 'source':
                    self.source_list.clear()
                    if items:
                        for item in items:
                            self._add_item_to_list(self.source_list, item)
                    else:
                        # Add "no results" item
                        no_results = QListWidgetItem("No items found")
                        no_results.setFlags(Qt.ItemFlag.NoItemFlags)
                        self.source_list.addItem(no_results)
                else:
                    self.finished_list.clear()
                    if items:
                        for item in items:
                            self._add_item_to_list(self.finished_list, item)
                    else:
                        # Add "no results" item
                        no_results = QListWidgetItem("No items found")
                        no_results.setFlags(Qt.ItemFlag.NoItemFlags)
                        self.finished_list.addItem(no_results)
            else:
                logger.error(f"API search failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                
                # Show error in list
                list_widget = self.source_list if item_type == 'source' else self.finished_list
                list_widget.clear()
                error_item = QListWidgetItem(f"Error: HTTP {response.status_code}")
                error_item.setFlags(Qt.ItemFlag.NoItemFlags)
                list_widget.addItem(error_item)
                
        except requests.exceptions.Timeout:
            logger.error(f"API request timeout for {item_type} items")
            list_widget = self.source_list if item_type == 'source' else self.finished_list
            list_widget.clear()
            error_item = QListWidgetItem("Error: Request timeout")
            error_item.setFlags(Qt.ItemFlag.NoItemFlags)
            list_widget.addItem(error_item)
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error searching {item_type} items: {e}")
            list_widget = self.source_list if item_type == 'source' else self.finished_list
            list_widget.clear()
            error_item = QListWidgetItem("Error: Cannot connect to API")
            error_item.setFlags(Qt.ItemFlag.NoItemFlags)
            list_widget.addItem(error_item)
            
        except Exception as e:
            logger.error(f"Error searching {item_type} items: {e}", exc_info=True)
            list_widget = self.source_list if item_type == 'source' else self.finished_list
            list_widget.clear()
            error_item = QListWidgetItem(f"Error: {str(e)}")
            error_item.setFlags(Qt.ItemFlag.NoItemFlags)
            list_widget.addItem(error_item)
    
    def _add_item_to_list(self, list_widget: QListWidget, item_data):
        """Add an item to the list widget."""
        # Handle both string and dictionary formats
        if isinstance(item_data, str):
            # API returns simple string (item code)
            item_code = item_data
            item_name = ''
            # Convert to dict for consistency
            item_dict = {'item_code': item_code, 'item_name': item_name}
        elif isinstance(item_data, dict):
            # API returns dictionary
            # Handle different possible field names from API
            item_code = (
                item_data.get('product_code') or  # textile_plus uses this
                item_data.get('item_code') or 
                item_data.get('code') or 
                item_data.get('name') or 
                ''
            )
            item_name = (
                item_data.get('product_name') or  # textile_plus uses this
                item_data.get('item_name') or 
                item_data.get('description') or 
                item_data.get('title') or 
                ''
            )
            # Store with standardized field names
            item_dict = {
                'item_code': item_code,
                'item_name': item_name,
                'product_code': item_data.get('product_code'),
                'product_name': item_data.get('product_name'),
                'barcode': item_data.get('barcode'),
                'color_code': item_data.get('color_code')
            }
        else:
            logger.warning(f"Unexpected item data type: {type(item_data)} - {item_data}")
            return
        
        # If no item_code found, log the data structure
        if not item_code:
            logger.warning(f"Item data missing item_code: {item_data}")
            return
        
        display_text = f"{item_code}"
        if item_name:
            display_text += f" - {item_name}"
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, item_dict)
        list_widget.addItem(item)
    
    def on_source_item_selected(self, item: QListWidgetItem):
        """Handle source item selection."""
        item_data = item.data(Qt.ItemDataRole.UserRole)
        
        # Check if item has valid data (not error/no results items)
        if not item_data or not isinstance(item_data, dict):
            logger.warning("Clicked on invalid item (no data)")
            return
        
        # Get item code with fallback field names
        self.source_item = (
            item_data.get('product_code') or  # textile_plus uses this
            item_data.get('item_code') or 
            item_data.get('code') or 
            item_data.get('name') or 
            ''
        )
        
        if not self.source_item:
            logger.warning(f"Item has no valid item_code: {item_data}")
            return
        
        # Get item name with fallback field names
        item_name = (
            item_data.get('product_name') or  # textile_plus uses this
            item_data.get('item_name') or 
            item_data.get('description') or 
            item_data.get('title') or 
            ''
        )
        
        display_text = f"✅ Selected: {self.source_item}"
        if item_name:
            display_text += f" - {item_name}"
        self.source_selected_label.setText(display_text)
        
        logger.info(f"Source item selected: {self.source_item}")
        self._update_submit_button()
    
    def on_finished_item_selected(self, item: QListWidgetItem):
        """Handle finished item selection."""
        item_data = item.data(Qt.ItemDataRole.UserRole)
        
        # Check if item has valid data (not error/no results items)
        if not item_data or not isinstance(item_data, dict):
            logger.warning("Clicked on invalid item (no data)")
            return
        
        # Get item code with fallback field names
        self.finished_item = (
            item_data.get('product_code') or  # textile_plus uses this
            item_data.get('item_code') or 
            item_data.get('code') or 
            item_data.get('name') or 
            ''
        )
        
        if not self.finished_item:
            logger.warning(f"Item has no valid item_code: {item_data}")
            return
        
        # Get item name with fallback field names
        item_name = (
            item_data.get('product_name') or  # textile_plus uses this
            item_data.get('item_name') or 
            item_data.get('description') or 
            item_data.get('title') or 
            ''
        )
        
        display_text = f"✅ Selected: {self.finished_item}"
        if item_name:
            display_text += f" - {item_name}"
        self.finished_selected_label.setText(display_text)
        
        logger.info(f"Finished item selected: {self.finished_item}")
        self._update_submit_button()
    
    def _update_submit_button(self):
        """Enable submit button when both BOM and finished item are selected."""
        if self.bom_name and self.finished_item:
            self.submit_btn.setEnabled(True)
        else:
            self.submit_btn.setEnabled(False)
    
    def get_selected_items(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the selected BOM and finished item codes."""
        return self.bom_name, self.finished_item

