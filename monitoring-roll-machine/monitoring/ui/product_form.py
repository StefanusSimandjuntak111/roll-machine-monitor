from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QLabel, QHBoxLayout
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Dict, Any

class ProductForm(QWidget):
    """Form for entering and editing product information."""
    
    # Signal emitted when product info is updated
    product_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the product form UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Create form frame
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: #888888;
                font-size: 12px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #353535;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 10px;
                padding: 15px;
                color: white;
                font-size: 14px;
                min-width: 150px;
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
        """)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Title
        title = QLabel("Product Information")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        form_layout.addRow(title)
        
        # Product Code
        self.product_code = QLineEdit()
        self.product_code.setPlaceholderText("Enter product code")
        form_layout.addRow("Product Code:", self.product_code)
        
        # Batch Number
        self.batch_number = QLineEdit()
        self.batch_number.setPlaceholderText("Enter batch number")
        form_layout.addRow("Batch Number:", self.batch_number)
        
        # Target Length
        self.target_length = QDoubleSpinBox()
        self.target_length.setRange(0, 100000)
        self.target_length.setSuffix(" m")
        self.target_length.setDecimals(1)
        self.target_length.setValue(0.0)
        form_layout.addRow("Target Length:", self.target_length)
        
        # Unit Selection
        self.unit_selection = QSpinBox()
        self.unit_selection.setRange(1, 100)
        self.unit_selection.setSuffix(" units")
        self.unit_selection.setValue(1)
        form_layout.addRow("Number of Units:", self.unit_selection)
        
        # Buttons Layout (untuk meletakkan tombol secara horizontal)
        buttons_layout = QHBoxLayout()
        
        # Save Button
        self.save_button = QPushButton("Save Product Info")
        self.save_button.setMinimumHeight(60)  # Membuat tombol lebih tinggi
        self.save_button.setFont(QFont("Segoe UI", 12))  # Font lebih besar
        self.save_button.clicked.connect(self.save_product_info)
        buttons_layout.addWidget(self.save_button)
        
        # Print Button
        self.print_button = QPushButton("Print")
        self.print_button.setObjectName("print_button")
        self.print_button.setMinimumHeight(60)
        self.print_button.setFont(QFont("Segoe UI", 12))
        self.print_button.clicked.connect(self.print_product_info)
        buttons_layout.addWidget(self.print_button)
        
        # Tambahkan buttons layout ke form
        form_layout.addRow(buttons_layout)
        
        layout.addWidget(form_frame)
        
    def save_product_info(self):
        """Validate and save product information."""
        if not self.validate_inputs():
            return
            
        product_info = {
            'product_code': self.product_code.text().strip(),
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'units': self.unit_selection.value()
        }
        
        self.product_updated.emit(product_info)
        
    def print_product_info(self):
        """Print product information."""
        if not self.validate_inputs():
            return
            
        # TODO: Implement printing functionality
        print("Printing product info...")
        
    def validate_inputs(self) -> bool:
        """Validate form inputs."""
        if not self.product_code.text().strip():
            self.show_error(self.product_code, "Product code is required")
            return False
            
        if not self.batch_number.text().strip():
            self.show_error(self.batch_number, "Batch number is required")
            return False
            
        if self.target_length.value() <= 0:
            self.show_error(self.target_length, "Target length must be greater than 0")
            return False
            
        return True
        
    def show_error(self, widget: QWidget, message: str):
        """Show error styling and tooltip for a widget."""
        widget.setStyleSheet("""
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #353535;
                border: 1px solid #ff4444;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
        """)
        widget.setToolTip(message)
        
    def clear_error(self, widget: QWidget):
        """Clear error styling and tooltip for a widget."""
        widget.setStyleSheet("")
        widget.setToolTip("")
        
    def get_product_info(self) -> Dict[str, Any]:
        """Get current product information."""
        return {
            'product_code': self.product_code.text().strip(),
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'units': self.unit_selection.value()
        }
        
    def set_product_info(self, info: Dict[str, Any]):
        """Set product information in the form."""
        self.product_code.setText(info.get('product_code', ''))
        self.batch_number.setText(info.get('batch_number', ''))
        self.target_length.setValue(info.get('target_length', 0.0))
        self.unit_selection.setValue(info.get('units', 1)) 