"""
Print preview dialog for product information.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
    QScrollArea, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QSize, QMarginsF, QRectF, QSizeF, QLineF, QPoint
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

logger = logging.getLogger(__name__)

class PrintPreviewDialog(QDialog):
    """Dialog for print preview."""
    
    def __init__(self, product_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.product_info = product_info
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
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the print preview dialog UI."""
        self.setWindowTitle("Print Preview")
        
        # Calculate window size to maintain 1:1 aspect ratio
        screen_size = self.screen().size()
        preview_size = min(screen_size.width() * 0.55, screen_size.height() * 0.55)
        window_width = preview_size
        window_height = preview_size + 80  # Extra space for buttons
        
        self.resize(int(window_width), int(window_height))
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
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
            str(self.product_info.get('color', '1')),  # Ensure color is retrieved as string
            f"{self.product_info.get('target_length', 0)} {self.product_info.get('units', 'Yard')}",
            str(self.product_info.get('roll_number', '0')),
            str(self.product_info.get('lot_number', 'None'))
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
        length = self.product_info.get('target_length', 0)
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
        
        # Calculate row heights
        row_heights = [
            int(table_height_px * 0.18),  # Header (18%)
            int(table_height_px * 0.15),  # Product name (15%)
            int(table_height_px * 0.13),  # Info rows (13% each)
            int(table_height_px * 0.13),
            int(table_height_px * 0.13),
            int(table_height_px * 0.13),
            int(table_height_px * 0.15)   # Bottom row (15%)
        ]
        
        # Draw horizontal lines
        current_y = start_y
        for i, height in enumerate(row_heights):
            current_y += height
            if i < len(row_heights) - 1:  # Don't draw line after last row
                painter.drawLine(
                    start_x, 
                    current_y, 
                    int(start_x + table_width_px), 
                    current_y
                )
        
        # Draw vertical line for column separator (skip for header and bottom rows)
        column_x = int(start_x + (table_width_px // 2))
        
        # Draw content
        current_y = start_y
        
        # Header - Product Code (merged across full width)
        header_font = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(header_font)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        
        product_code = self.product_info.get('product_code', 'PRD-0001')  # Default product code
        text_rect = QRectF(
            start_x, 
            current_y, 
            table_width_px, 
            row_heights[0]
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_code)
        current_y += row_heights[0]
        
        # Product Name (merged across full width)
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
        
        labels = ["Color", "Length", "Roll No.", "Lot No."]
        values = [
            str(self.product_info.get('color', '1')),  # Default color: 1
            f"{self.product_info.get('target_length', 0)} {self.product_info.get('units', 'Yard')}",
            str(self.product_info.get('roll_number', '0')),  # Default roll number: 0
            str(self.product_info.get('lot_number', 'None'))  # Default lot number: None
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
        
        # Bottom section (Product Code with Length) - merged across full width
        bottom_font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(bottom_font)
        
        length = self.product_info.get('target_length', 0)
        bottom_code = f"{product_code}-{length}"
        
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
        
        # Generate QR code
        qr_data = f"{product_code}-{length}"
        qr_image = self.generate_qr_code(qr_data, use_internet_qr=False)
        
        # Scale QR code to desired size
        scaled_qr = qr_image.scaled(
            barcode_size_px, 
            barcode_size_px, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Draw left barcode
        painter.drawImage(barcode_left_x, barcode_y, scaled_qr)
        
        # Draw right barcode
        painter.drawImage(barcode_right_x, barcode_y, scaled_qr)
        
        painter.end()

    def print_document(self):
        """Print the document."""
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.print_preview(self.printer) 