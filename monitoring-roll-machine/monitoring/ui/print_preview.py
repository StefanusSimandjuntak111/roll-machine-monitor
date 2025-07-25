"""
Print preview dialog for product information.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
    QScrollArea, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt, QSize, QMarginsF, QRectF, QSizeF, QLineF, QPoint, Signal
from PySide6.QtPrintSupport import (
    QPrinter, QPrintDialog, QPrintPreviewWidget,
    QPrinterInfo
)
from PySide6.QtGui import (
    QPainter, QPageLayout, QPageSize, QFont, QPen,
    QColor, QImage, QBrush, QRegion
)
from typing import Dict, Any, List, Tuple
import logging
import qrcode
from qrcode.constants import ERROR_CORRECT_L
from PIL.Image import Image
from io import BytesIO
import requests

from ..config import load_config, calculate_print_length

logger = logging.getLogger(__name__)

class PrintPreviewDialog(QDialog):
    """Dialog for print preview."""
    
    # Signal emitted when production is logged
    production_logged = Signal(dict)
    
    def __init__(self, product_info: Dict[str, Any], parent=None, current_machine_length: float = None):
        super().__init__(parent)
        self.product_info = product_info
        self.current_machine_length = current_machine_length
        self.printer = QPrinter(QPrinterInfo.defaultPrinter())
        
        # Set up custom page size (10x10cm) for Zebra label
        page_width_mm = 100.0  # 10 cm
        page_height_mm = 100.0  # 10 cm
        
        # Create custom page size
        custom_size = QPageSize(
            QSizeF(page_width_mm, page_height_mm),
            QPageSize.Unit.Millimeter,
            "Custom_10x10cm",
            QPageSize.SizeMatchPolicy.ExactMatch
        )
        
        # Configure printer settings
        self.printer.setPageSize(custom_size)
        self.printer.setFullPage(True)  # Important for label printers
        self.printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        
        # Set resolution to match Zebra ZD230 (203 DPI)
        self.printer.setResolution(203)
        
        # Force first page
        self.printer.setFromTo(1, 1)
        self.printer.setCopyCount(1)
        # Set page margins to 0 using QMarginsF
        margins = QMarginsF(0, 0, 0, 0)
        self.printer.setPageMargins(margins, QPageLayout.Unit.Millimeter)  # No margins
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the print preview dialog UI."""
        self.setWindowTitle("Print Preview")
        
        # Force dialog to stay on top in kiosk mode
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint
        )
        
        # Calculate window size to maintain 1:1 aspect ratio
        screen_size = self.screen().size()
        preview_size = min(screen_size.width() * 0.55, screen_size.height() * 0.55)
        window_width = preview_size
        window_height = preview_size + 120  # Extra space for buttons and tolerance info
        
        self.resize(int(window_width), int(window_height))
        
        # Ensure dialog appears in front
        self.raise_()
        self.activateWindow()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tolerance info label
        self.tolerance_label = QLabel("Tolerance calculation info will appear here")
        self.tolerance_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 5px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                text-align: center;
            }
        """)
        self.tolerance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tolerance_label)
        
        # Print copy input
        copy_layout = QHBoxLayout()
        copy_layout.setSpacing(10)
        
        copy_label = QLabel("Print Copies:")
        copy_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        self.copy_spinbox = QSpinBox()
        self.copy_spinbox.setRange(1, 10)
        self.copy_spinbox.setValue(1)
        self.copy_spinbox.setStyleSheet("""
            QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                min-width: 80px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #cccccc;
                background-color: #f8f9fa;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e9ecef;
            }
        """)
        
        copy_layout.addWidget(copy_label)
        copy_layout.addWidget(self.copy_spinbox)
        copy_layout.addStretch()
        
        layout.addLayout(copy_layout)
        
        # Preview widget in a fixed-size container
        preview_container = QWidget()
        preview_container.setFixedSize(int(preview_size), int(preview_size))
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)
        
        self.preview = QPrintPreviewWidget(self.printer, preview_container)
        self.preview.paintRequested.connect(self.print_preview)
        self.preview.setZoomMode(QPrintPreviewWidget.ZoomMode.FitInView)
        preview_layout.addWidget(self.preview)
        
        layout.addWidget(preview_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        print_btn = QPushButton("Print")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        print_btn.clicked.connect(self.print_document)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(print_btn)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Setup preview table and update tolerance info
        self.setup_preview_table()

    def create_table(self) -> QTableWidget:
        """Create and configure the table widget."""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setRowCount(7)  # Header (2) + Info (4) + Bottom (1)
        
        # Set table properties for clean look
        table.setShowGrid(True)
        table.setGridStyle(Qt.PenStyle.SolidLine)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        
        # Set column widths to be equal
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Clean modern style
        table.setStyleSheet("""
            QTableWidget {
                border: 2px solid black;
                gridline-color: black;
                background-color: white;
                selection-background-color: transparent;
            }
            QTableWidget::item {
                padding: 10px;
                border: 1px solid black;
            }
            QTableWidget::item:selected {
                background-color: transparent;
                color: black;
            }
        """)
        
        return table

    def setup_table_content(self, table: QTableWidget):
        """Set up the table content with proper formatting."""
        # Header section (Product Code)
        header_font = QFont("Arial", 24, QFont.Weight.Bold)
        
        product_code = self.product_info.get('product_code', 'PRD-0001')  # Default product code
        code_item = QTableWidgetItem(product_code)
        code_item.setFont(header_font)
        code_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
        table.setSpan(0, 0, 1, 2)  # Merge first row
        table.setItem(0, 0, code_item)
        
        # Product Name
        product_name = self.product_info.get('product_name', 'Default Product')  # Default product name
        name_item = QTableWidgetItem(product_name)
        name_item.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        name_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
        table.setSpan(1, 0, 1, 2)  # Merge second row
        table.setItem(1, 0, name_item)
        
        # Info section
        info_font = QFont("Arial", 18, QFont.Weight.Bold)
        
        value_font = QFont("Arial", 18, QFont.Weight.Bold)
        
        labels = ["Color", "Length", "Roll No.", "Lot No."]
        values = [
            str(self.product_info.get('color_code', '1')),  # Use color_code field
            f"{self.product_info.get('print_length', self.product_info.get('target_length', 0))} {self.product_info.get('units', 'Yard')}",
            str(self.product_info.get('roll_number', '0')),
            str(self.product_info.get('batch_number', 'None'))  # Use batch_number as lot_number
        ]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            row = i + 2  # Start after header rows
            
            # Label (left column)
            label_item = QTableWidgetItem(label)
            label_item.setFont(info_font)
            label_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))
            table.setItem(row, 0, label_item)
            
            # Value (right column)
            value_item = QTableWidgetItem(value)
            value_item.setFont(value_font)
            value_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))
            table.setItem(row, 1, value_item)
        
        # Bottom section (Product Code with Length)
        bottom_font = QFont("Arial", 20, QFont.Weight.Bold)
        length = self.product_info.get('print_length', self.product_info.get('target_length', 0))
        bottom_code = f"{product_code}-{length}"
        
        bottom_item = QTableWidgetItem(bottom_code)
        bottom_item.setFont(bottom_font)
        bottom_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
        table.setSpan(6, 0, 1, 2)  # Merge bottom row
        table.setItem(6, 0, bottom_item)

    def generate_qr_code(self, data: str, use_internet_qr: bool = False) -> QImage:
        """Generate QR code image.
        
        Args:
            data: Data to encode in QR code
            use_internet_qr: If True, use a sample QR from internet (for testing)
        """
        if use_internet_qr:
            try:
                # Use a sample QR code from internet for testing
                url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + data
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    qimage = QImage()
                    qimage.loadFromData(response.content)
                    return qimage
            except Exception as e:
                logger.warning(f"Failed to fetch internet QR: {e}")
                # Fall back to local generation
        
        # Generate QR code locally
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        pil_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL Image to QImage
        buffer = BytesIO()
        pil_img.save(buffer, 'PNG')
        qr_bytes = buffer.getvalue()
        
        qimage = QImage()
        qimage.loadFromData(qr_bytes)
        return qimage
        
    def print_preview(self, printer: QPrinter) -> None:
        """Draw the preview content on the printer."""
        painter = QPainter(printer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Get page rect in device pixels
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        page_width_px = page_rect.width()
        page_height_px = page_rect.height()
        
        # Calculate table size in pixels (7.5cm x 7cm with reduced margins)
        dpi = printer.resolution()
        mm_to_inch = 25.4
        
        # Calculate margins (0.5cm on all sides)
        margin_px = int((5.0 / mm_to_inch) * dpi)  # 5mm = 0.5cm
        
        # Calculate table size to fit within margins
        table_width_px = int(page_width_px - (2 * margin_px))  # Full width minus margins
        table_height_px = int((70.0 / mm_to_inch) * dpi)  # 70mm = 7cm height
        
        # Center the table on the page
        start_x = margin_px  # Start at left margin
        start_y = int((page_height_px - table_height_px) // 2) - int((10.0 / mm_to_inch) * dpi)  # Move table up by 1cm
        
        # Draw white background for table area
        painter.fillRect(
            start_x, 
            start_y, 
            table_width_px, 
            table_height_px, 
            QBrush(Qt.GlobalColor.white)
        )
        
        # Draw table border
        pen = QPen(Qt.GlobalColor.black, 4)  # Thicker border
        painter.setPen(pen)
        painter.drawRect(
            start_x, 
            start_y, 
            table_width_px, 
            table_height_px
        )
        
        # Calculate row heights (7 rows total)
        row_heights = [int(table_height_px * ratio) for ratio in [0.15, 0.15, 0.12, 0.12, 0.12, 0.12, 0.22]]
        
        # Calculate column position (vertical line at 50%)
        column_x = start_x + (table_width_px // 2)
        
        # Draw horizontal lines
        current_y = start_y
        for i, height in enumerate(row_heights):
            if i < len(row_heights) - 1:  # Don't draw line after last row
                painter.drawLine(
                    start_x, 
                    current_y + height, 
                    start_x + table_width_px, 
                    current_y + height
                )
            current_y += height
        
        # Reset current_y for content drawing
        current_y = start_y
        
        # Header section (Product Code)
        header_font = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(header_font)
        
        product_code = self.product_info.get('product_code', 'DEFAULT')
        text_rect = QRectF(
            start_x, 
            current_y, 
            table_width_px, 
            row_heights[0]
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_code)
        current_y += row_heights[0]
        
        # Product Name section
        name_font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(name_font)
        
        product_name = self.product_info.get('product_name', 'Default Product')  # Default product name
        text_rect = QRectF(
            start_x, 
            current_y, 
            table_width_px, 
            row_heights[1]
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_name)
        current_y += row_heights[1]
        
        # Draw vertical line for info section only
        painter.drawLine(
            column_x, 
            current_y, 
            column_x, 
            int(start_y + table_height_px - row_heights[6])  # Stop before bottom row
        )
        
        # Info section
        info_font = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(info_font)
        
        # Load config for tolerance settings
        config = load_config()
        tolerance_percent = config.get("length_tolerance", 3.0)
        decimal_points = config.get("decimal_points", 1)
        rounding = config.get("rounding", "UP")
        
        # Calculate print length with tolerance
        # Always use current machine length for print preview (same as print length)
        if self.current_machine_length is not None:
            target_length = self.current_machine_length
        else:
            target_length = self.product_info.get('target_length', 0)
        print_length = calculate_print_length(target_length, tolerance_percent, decimal_points, rounding)
        
        labels = ["Color", "Length", "Roll No.", "Lot No."]
        values = [
            str(self.product_info.get('color_code', '1')),  # Use color_code field
            f"{print_length:.{decimal_points}f} {self.product_info.get('units', 'Yard')}",
            str(self.product_info.get('roll_number', '0')),  # Default roll number: 0
            str(self.product_info.get('batch_number', 'None'))  # Use batch_number as lot_number
        ]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            # Label (left column)
            label_rect = QRectF(
                start_x, 
                current_y, 
                table_width_px // 2, 
                row_heights[i + 2]
            )
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)
            
            # Value (right column)
            value_rect = QRectF(
                column_x, 
                current_y, 
                table_width_px // 2, 
                row_heights[i + 2]
            )
            painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value)
            
            current_y += row_heights[i + 2]
        
        # Bottom section (Product Code with Print Length) - merged across full width
        bottom_font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(bottom_font)
        
        bottom_code = f"{product_code}-{print_length:.{decimal_points}f}"
        
        text_rect = QRectF(
            start_x, 
            current_y, 
            table_width_px, 
            row_heights[6]
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, bottom_code)
        
        # Add QR barcodes below the table
        barcode_size_px = int((20.0 / mm_to_inch) * dpi)  # 20mm = 2cm (reduced from 2.5cm)
        spacing_px = int((3.0 / mm_to_inch) * dpi)  # 3mm = 0.3cm spacing (reduced from 0.5cm)
        
        barcode_y = start_y + table_height_px + spacing_px
        
        # Calculate positions for left and right barcodes
        barcode_left_x = start_x + int((table_width_px * 0.25) - (barcode_size_px // 2))
        barcode_right_x = start_x + int((table_width_px * 0.75) - (barcode_size_px // 2))
        
        # Generate QR code with print length
        qr_data = f"{product_code}-{print_length:.{decimal_points}f}"
        qr_image = self.generate_qr_code(qr_data, use_internet_qr=False)
        
        # Scale QR code to desired size
        scaled_qr = qr_image.scaled(
            barcode_size_px, 
            barcode_size_px, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Draw left barcode (Product Details QR)
        painter.drawImage(barcode_left_x, barcode_y, scaled_qr)
        
        # Draw right barcode (Barcode Reference QR)
        barcode_ref = self.product_info.get('barcode', '')
        if barcode_ref:
            # Use barcode reference if available
            qr_data_right = str(barcode_ref)
        else:
            # Fallback to product details
            qr_data_right = f"{product_code}-{print_length:.{decimal_points}f}"
        
        qr_image_right = self.generate_qr_code(qr_data_right, use_internet_qr=False)
        scaled_qr_right = qr_image_right.scaled(
            barcode_size_px, 
            barcode_size_px, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        painter.drawImage(barcode_right_x, barcode_y, scaled_qr_right)
        
        painter.end()

    def print_document(self):
        """Print the document and log production data."""
        # Get copy count from spinbox
        copy_count = self.copy_spinbox.value()
        
        # Set printer copy count
        self.printer.setCopyCount(copy_count)
        
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            # Log production data when print is confirmed
            self.log_production_data()
            # Print the document
            self.print_preview(self.printer) 
    
    def log_production_data(self):
        """Log production data with cycle time and roll time."""
        try:
            from datetime import datetime
            
            # Get current time for logging
            current_time = datetime.now()
            
            # Get product info
            product_name = self.product_info.get('product_name', 'Unknown')
            product_code = self.product_info.get('product_code', 'Unknown')
            product_length = self.product_info.get('target_length', 0.0)
            batch = self.product_info.get('batch_number', 'Unknown')
            
            # Emit signal to main window with print data
            print_data = {
                'product_name': product_name,
                'product_code': product_code,
                'product_length': product_length,
                'batch': batch,
                'print_time': current_time
            }
            
            self.production_logged.emit(print_data)
            logger.info(f"Print signal emitted: {product_code} - {product_name} - Length: {product_length}")
                
        except Exception as e:
            logger.error(f"Error in print logging: {e}") 

    def setup_preview_table(self):
        """Set up the preview table with product information."""
        # Create table using the existing create_table method
        table = self.create_table()
        
        # Load config for tolerance settings
        config = load_config()
        tolerance_percent = config.get("length_tolerance", 3.0)
        decimal_points = config.get("decimal_points", 1)
        rounding = config.get("rounding", "UP")
        
        # Calculate print length with tolerance
        # Always use current machine length for print preview (same as print length)
        if self.current_machine_length is not None:
            target_length = self.current_machine_length
        else:
            target_length = self.product_info.get('target_length', 0)
        print_length = calculate_print_length(target_length, tolerance_percent, decimal_points, rounding)
        
        # Update product_info with print_length for use in setup_table_content
        self.product_info['print_length'] = print_length
        
        # Setup table content using the existing method
        self.setup_table_content(table)
        
        # Update tolerance info label
        tolerance_info = f"Target: {target_length:.{decimal_points}f}m, Tolerance: {tolerance_percent}%, Print: {print_length:.{decimal_points}f}m"
        self.tolerance_label.setText(tolerance_info) 