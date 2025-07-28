"""
Print preview dialog for product information.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QBrush
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PrintPreviewDialog(QDialog):
    """Dialog for showing print preview of product label."""
    
    def __init__(self, product_info: Dict[str, Any], current_machine_length: Optional[float], parent=None):
        super().__init__(parent)
        self.product_info = product_info
        self.current_machine_length = current_machine_length
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Print Preview")
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Set dialog size
        self.resize(600, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Print Preview")
        title_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Scroll area for preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
        
        # Preview widget
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create preview label
        preview_label = QLabel()
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #444444;
                border-radius: 5px;
            }
        """)
        
        # Generate preview pixmap
        preview_pixmap = self.generate_preview_pixmap()
        preview_label.setPixmap(preview_pixmap)
        
        preview_layout.addWidget(preview_label)
        scroll_area.setWidget(preview_widget)
        main_layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Close button
        close_button = QPushButton("Close (X)")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        close_button.clicked.connect(self.close)
        
        # Print button
        print_button = QPushButton("Print")
        print_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        print_button.clicked.connect(self.print_label)
        
        button_layout.addStretch()
        button_layout.addWidget(print_button)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def generate_preview_pixmap(self) -> QPixmap:
        """Generate a preview pixmap of the product label."""
        try:
            # Create a pixmap with label dimensions (10cm x 10cm at 203 DPI)
            # 10cm = 3.937 inches, 203 DPI * 3.937 = ~800 pixels
            width = 800
            height = 800
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(255, 255, 255))  # White background
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Set up fonts
            title_font = QFont("Arial", 16, QFont.Weight.Bold)
            normal_font = QFont("Arial", 12)
            small_font = QFont("Arial", 10)
            
            # Draw border
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawRect(10, 10, width - 20, height - 20)
            
            # Draw title
            painter.setFont(title_font)
            painter.setPen(QColor(0, 0, 0))
            title_text = "PRODUCT LABEL"
            title_rect = painter.boundingRect(0, 30, width, 50, Qt.AlignmentFlag.AlignCenter, title_text)
            painter.drawText(title_rect, title_text)
            
            # Draw product information
            painter.setFont(normal_font)
            y_pos = 100
            line_height = 25
            
            # Product Code
            product_code = self.product_info.get('product_code', 'N/A')
            painter.drawText(50, y_pos, f"Product Code: {product_code}")
            y_pos += line_height
            
            # Product Name
            product_name = self.product_info.get('product_name', 'N/A')
            painter.drawText(50, y_pos, f"Product Name: {product_name}")
            y_pos += line_height
            
            # Color Code
            color_code = self.product_info.get('color_code', 'N/A')
            painter.drawText(50, y_pos, f"Color Code: {color_code}")
            y_pos += line_height
            
            # Batch Number
            batch_number = self.product_info.get('batch_number', 'N/A')
            painter.drawText(50, y_pos, f"Batch Number: {batch_number}")
            y_pos += line_height
            
            # Current Length
            current_length = self.product_info.get('current_length', 0.0)
            units = self.product_info.get('units', 'Meter')
            painter.drawText(50, y_pos, f"Current Length: {current_length:.2f} {units}")
            y_pos += line_height
            
            # Target Length
            target_length = self.product_info.get('target_length', 0)
            painter.drawText(50, y_pos, f"Target Length: {target_length} {units}")
            y_pos += line_height
            
            # Machine Length (if available)
            if self.current_machine_length is not None:
                painter.drawText(50, y_pos, f"Machine Length: {self.current_machine_length:.2f} {units}")
                y_pos += line_height
            
            # Draw barcode placeholder
            if self.product_info.get('barcode'):
                painter.setFont(small_font)
                painter.drawText(50, y_pos + 20, f"Barcode: {self.product_info.get('barcode')}")
            
            # Draw QR code placeholder
            qr_text = f"{product_code}|{color_code}|{batch_number}"
            painter.setFont(small_font)
            painter.drawText(50, height - 80, f"QR Code: {qr_text}")
            
            painter.end()
            
            return pixmap
            
        except Exception as e:
            logger.error(f"Error generating preview pixmap: {e}")
            # Return a simple error pixmap
            error_pixmap = QPixmap(400, 300)
            error_pixmap.fill(QColor(255, 255, 255))
            
            painter = QPainter(error_pixmap)
            painter.setPen(QColor(255, 0, 0))
            painter.setFont(QFont("Arial", 14))
            painter.drawText(error_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Error generating preview")
            painter.end()
            
            return error_pixmap
    
    def print_label(self):
        """Print the label using printer utils."""
        try:
            from .printer_utils import print_product_label
            print_product_label(self.product_info, self.current_machine_length)
            
            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Print Success",
                "Label printed successfully!"
            )
            
        except Exception as e:
            logger.error(f"Error printing label: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Print Error",
                f"Error printing label:\n\n{str(e)}"
            ) 