"""
Print preview dialog for product information.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QSize, QRectF
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
        """Generate a preview pixmap of the product label with exact table format as requested."""
        try:
            # Create a pixmap with label dimensions (10cm x 10cm at 203 DPI)
            # 10cm = 3.937 inches, 203 DPI * 3.937 = ~800 pixels
            width = 800
            height = 800
            pixmap = QPixmap(width, height)
            pixmap.fill(QColor(255, 255, 255))  # White background
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            
            # Get product data
            product_code = self.product_info.get('product_code', 'DEFAULT')
            product_name = self.product_info.get('product_name', 'Default Product')
            print_length = self.product_info.get('print_length', self.product_info.get('current_length', 0.0))
            decimal_points = self.product_info.get('decimal_points', 1)
            
            # Add margin (0.2-0.5cm) - convert cm to pixels at 203 DPI
            # 1cm = 0.3937 inches, 203 DPI * 0.3937 = ~80 pixels per cm
            margin_cm = 0.3  # 0.3cm margin
            margin_px = int(margin_cm * 80)
            
            # Table dimensions with margin
            table_width = width - (2 * margin_px)
            table_height = int((height - (2 * margin_px)) * 0.8)  # 80% for table, 20% for barcodes
            
            start_x = margin_px
            start_y = margin_px
            
            # Generate QR codes (same as printer_utils.py)
            from .printer_utils import generate_qr_code
            qr_data_1 = str(product_code)  # Barcode 1: Product Code
            qr_image_1 = generate_qr_code(qr_data_1)
            
            # Always use format: product_code-print_length
            # FIX: Use proper decimal formatting instead of {decimal_points}f
            qr_data_2 = f"{product_code}-{print_length:.{decimal_points}f}"
            qr_image_2 = generate_qr_code(qr_data_2)
            
            # Draw table background
            painter.fillRect(start_x, start_y, table_width, table_height, QBrush(Qt.GlobalColor.white))
            
            # Draw table border
            pen = QPen(Qt.GlobalColor.black, 3)
            painter.setPen(pen)
            painter.drawRect(start_x, start_y, table_width, table_height)
            
            # Calculate row heights (exact same structure as printer_utils.py)
            header_height = int(table_height * 0.15)      # Row 1: Product Code
            name_height = int(table_height * 0.15)        # Row 2: Product Name  
            info_height = int(table_height * 0.175)       # Rows 3-6: Info rows (4 rows) - equal height
            
            current_y = start_y
            
            # Row 1: Product Code Header (colspan=2)
            painter.drawLine(start_x, current_y + header_height, start_x + table_width, current_y + header_height)
            
            header_font = QFont("Arial", 28, QFont.Weight.Bold)
            painter.setFont(header_font)
            text_rect = QRectF(start_x, current_y, table_width, header_height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_code)
            current_y += header_height
            
            # Row 2: Product Name (colspan=2)
            painter.drawLine(start_x, current_y + name_height, start_x + table_width, current_y + name_height)
            
            name_font = QFont("Arial", 22, QFont.Weight.Bold)
            painter.setFont(name_font)
            text_rect = QRectF(start_x, current_y, table_width, name_height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_name)
            current_y += name_height
            
            # Draw vertical line for info section (2 columns)
            column_x = start_x + (table_width // 2)
            info_section_height = info_height * 4  # 4 info rows
            painter.drawLine(column_x, current_y, column_x, current_y + info_section_height)
            
            # Info rows (Color, Length, Roll No, Lot No)
            info_font = QFont("Arial", 18, QFont.Weight.Bold)
            painter.setFont(info_font)
            
            info_data = [
                ("Color", str(self.product_info.get('color_code', '1'))),
                ("Length", f"{print_length:.{decimal_points}f} {self.product_info.get('units', 'Yard')}"),
                ("Roll No.", str(self.product_info.get('roll_number', '0'))),
                ("Lot No.", str(self.product_info.get('batch_number', 'None')))
            ]
            
            for i, (label, value) in enumerate(info_data):
                # Draw horizontal line after each row (except last)
                if i < len(info_data) - 1:
                    painter.drawLine(start_x, current_y + info_height, start_x + table_width, current_y + info_height)
                
                # Label (left column)
                label_rect = QRectF(start_x, current_y, table_width // 2, info_height)
                painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)
                
                # Value (right column)
                value_rect = QRectF(column_x, current_y, table_width // 2, info_height)
                painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value)
                
                current_y += info_height
            
            # Barcode section at bottom (remaining 20% of page)
            barcode_y = start_y + table_height + 20  # Increased spacing to avoid border overlap
            barcode_area_height = height - table_height - (2 * margin_px) - 20
            
            # Set barcode size to exactly 1.8cm (1.8cm * 80 pixels/cm = 144 pixels)
            barcode_size = int(1.8 * 80)  # 1.8cm in pixels at 203 DPI
            
            # Position barcodes side by side
            barcode_1_x = start_x + int(table_width * 0.25) - (barcode_size // 2)
            barcode_2_x = start_x + int(table_width * 0.75) - (barcode_size // 2)
            
            # Add product code text above barcodes (small font, centered)
            # Lower position by ~0.2mm (0.2mm * 80 pixels/cm / 10 = ~1.6 pixels)
            product_code_font = QFont("Arial", 10, QFont.Weight.Normal)
            painter.setFont(product_code_font)
            product_code_text_rect = QRectF(start_x, barcode_y - 10, table_width, 20)  # Reduced from -15 to -10
            # Display format: product_code-print_length
            display_text = f"{product_code}-{print_length:.{decimal_points}f}"
            painter.drawText(product_code_text_rect, Qt.AlignmentFlag.AlignCenter, display_text)
            
            # Scale and draw QR codes (actual QR codes, not placeholders)
            scaled_qr_1 = qr_image_1.scaled(barcode_size, barcode_size, 
                                           Qt.AspectRatioMode.KeepAspectRatio, 
                                           Qt.TransformationMode.SmoothTransformation)
            scaled_qr_2 = qr_image_2.scaled(barcode_size, barcode_size,
                                           Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
            
            painter.drawImage(barcode_1_x, barcode_y, scaled_qr_1)
            painter.drawImage(barcode_2_x, barcode_y, scaled_qr_2)
            
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