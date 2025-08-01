"""
Printer utilities for detecting connected printers and direct printing.
"""
from PySide6.QtPrintSupport import QPrinterInfo, QPrinter
from PySide6.QtCore import QMarginsF, QSizeF, Qt, QRectF
from PySide6.QtGui import QPainter, QFont, QPen, QColor, QBrush, QImage, QPageLayout, QPageSize
from typing import List, Dict, Any, Optional
import logging
import qrcode
from qrcode.constants import ERROR_CORRECT_L
from PIL.Image import Image
from io import BytesIO
from datetime import datetime

logger = logging.getLogger(__name__)

def get_available_printers() -> List[str]:
    """Get list of available printer names."""
    try:
        printers = QPrinterInfo.availablePrinterNames()
        logger.info(f"Found {len(printers)} available printers: {printers}")
        return printers
    except Exception as e:
        logger.error(f"Error getting available printers: {e}")
        return []

def get_default_printer() -> Optional[str]:
    """Get the default printer name."""
    try:
        default_printer = QPrinterInfo.defaultPrinterName()
        logger.info(f"Default printer: {default_printer}")
        return default_printer
    except Exception as e:
        logger.error(f"Error getting default printer: {e}")
        return None

def create_label_printer(printer_name: Optional[str] = None, use_simple_config: bool = False) -> QPrinter:
    """Create a printer configured for label printing using proper Qt methods."""
    try:
        # Use the CORRECT way to create QPrinter based on Qt documentation
        if printer_name:
            # Set printer by name - this is the proper way in Qt
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPrinterName(printer_name)
            logger.info(f"Created printer with name: {printer_name}")
        else:
            # Use default printer
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            logger.info(f"Created default printer: {printer.printerName()}")
        
        # Check if printer is valid AFTER setting the name
        if not printer.isValid():
            logger.error(f"Printer '{printer.printerName()}' is not valid")
            # Try fallback to any available printer
            available_printers = QPrinterInfo.availablePrinterNames()
            if available_printers:
                fallback_name = available_printers[0]
                printer.setPrinterName(fallback_name)
                logger.info(f"Using fallback printer: {fallback_name}")
                if not printer.isValid():
                    raise Exception(f"No valid printers available")
            else:
                raise Exception(f"No printers found on system")
        
        # Use MINIMAL configuration for better compatibility
        if use_simple_config or "zebra" in printer.printerName().lower():
            logger.info("Using simple/Zebra-compatible configuration")
            # Don't set custom page sizes or margins for Zebra
            # Let the printer use its default settings
            printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
            printer.setFullPage(False)  # Use printer's printable area
            return printer
        
        # For other printers, try minimal label configuration
        try:
            # Use A4 size as baseline (most compatible)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
            printer.setFullPage(False)  # Respect printer margins
            logger.info("Standard configuration applied successfully")
        except Exception as e:
            logger.warning(f"Could not apply standard configuration: {e}")
        
        logger.info(f"Successfully created printer: {printer.printerName()}")
        return printer
        
    except Exception as e:
        logger.error(f"Error creating label printer: {e}")
        raise

def generate_qr_code(data: str) -> QImage:
    """Generate QR code image."""
    try:
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
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        raise

def print_product_label(product_info: Dict[str, Any], current_machine_length: Optional[float] = None, printer_name: Optional[str] = None) -> bool:
    """Print product label using simplified approach for better compatibility."""
    try:
        # Get copy count and selected printer from settings
        from monitoring.config import load_config
        config = load_config()
        copy_count = config.get("print_copy_count", 1)
        
        # Use printer_name if provided, otherwise use selected printer from config
        if printer_name is None:
            printer_name = config.get("selected_printer")
        
        logger.info(f"Starting simplified print job - Printer: {printer_name}, Copies: {copy_count}")
        
        # Create printer with minimal configuration
        printer = create_label_printer(printer_name, use_simple_config=True)
        
        # Use built-in copy count (proper Qt way)
        if copy_count > 1:
            printer.setCopyCount(copy_count)
            logger.info(f"Set copy count to {copy_count}")
        
        # Check if printer is ready
        if not printer.isValid():
            logger.error(f"Printer '{printer.printerName()}' is not valid")
            return False
        
        # Start printing
        painter = QPainter(printer)
        if not painter.isActive():
            logger.error("Failed to start painting on printer")
            return False
            
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Get page rect and use 100% width/height as requested
        page_rect = painter.viewport()
        page_width_px = page_rect.width()
        page_height_px = page_rect.height()
        
        logger.info(f"Page dimensions: {page_width_px} x {page_height_px} pixels")
        
        # Get product data
        print_length = product_info.get('print_length', product_info.get('current_length', 0.0))
        decimal_points = product_info.get('decimal_points', 1)
        product_code = product_info.get('product_code', 'DEFAULT')
        product_name = product_info.get('product_name', 'Default Product')
        
        # Add margin (0.2-0.5cm) - convert cm to pixels at 203 DPI
        # 1cm = 0.3937 inches, 203 DPI * 0.3937 = ~80 pixels per cm
        margin_cm = 0.3  # 0.3cm margin
        margin_px = int(margin_cm * 80)
        
        # Table dimensions with margin
        table_width = page_width_px - (2 * margin_px)
        table_height = int((page_height_px - (2 * margin_px)) * 0.8)  # 80% for table, 20% for barcodes
        
        start_x = margin_px
        start_y = margin_px
        
        # Generate QR codes
        qr_data_1 = str(product_code)  # Barcode 1: Product Code
        qr_image_1 = generate_qr_code(qr_data_1)
        
        barcode_api = product_info.get('barcode', '')  # Barcode 2: From API
        if barcode_api:
            qr_data_2 = str(barcode_api)
        else:
            qr_data_2 = f"{product_code}-{print_length:.{decimal_points}f}"
        qr_image_2 = generate_qr_code(qr_data_2)
        
        # Draw table background
        painter.fillRect(start_x, start_y, table_width, table_height, QBrush(Qt.GlobalColor.white))
        
        # Draw table border
        pen = QPen(Qt.GlobalColor.black, 3)
        painter.setPen(pen)
        painter.drawRect(start_x, start_y, table_width, table_height)
        
        # Calculate row heights (6 rows + barcode section)
        header_height = int(table_height * 0.15)      # Row 1: Product Code
        name_height = int(table_height * 0.15)        # Row 2: Product Name  
        info_height = int(table_height * 0.175)       # Rows 3-6: Info rows (4 rows) - equal height
        
        current_y = start_y
        
        # Row 1: Product Code Header (colspan=2)
        painter.drawLine(start_x, current_y + header_height, start_x + table_width, current_y + header_height)
        
        header_font = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(header_font)
        text_rect = QRectF(start_x, current_y, table_width, header_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_code)
        current_y += header_height
        
        # Row 2: Product Name (colspan=2)
        painter.drawLine(start_x, current_y + name_height, start_x + table_width, current_y + name_height)
        
        name_font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(name_font)
        text_rect = QRectF(start_x, current_y, table_width, name_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, product_name)
        current_y += name_height
        
        # Draw vertical line for info section (2 columns)
        column_x = start_x + (table_width // 2)
        info_section_height = info_height * 4  # 4 info rows
        painter.drawLine(column_x, current_y, column_x, current_y + info_section_height)
        
        # Info rows (Color, Length, Roll No, Lot No)
        info_font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(info_font)
        
        info_data = [
            ("Color", str(product_info.get('color_code', '1'))),
            ("Length", f"{print_length:.{decimal_points}f} {product_info.get('units', 'Yard')}"),
            ("Roll No.", str(product_info.get('roll_number', '0'))),
            ("Lot No.", str(product_info.get('batch_number', 'None')))
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
        barcode_area_height = page_height_px - table_height - (2 * margin_px) - 20
        
        # Set barcode size to exactly 1.8cm (1.8cm * 80 pixels/cm = 144 pixels)
        barcode_size = int(1.8 * 80)  # 1.8cm in pixels at 203 DPI
        
        # Position barcodes side by side
        barcode_1_x = start_x + int(table_width * 0.25) - (barcode_size // 2)
        barcode_2_x = start_x + int(table_width * 0.75) - (barcode_size // 2)
        
        # Add product code text above barcodes (small font, centered)
        product_code_font = QFont("Arial", 10, QFont.Weight.Normal)
        painter.setFont(product_code_font)
        product_code_text_rect = QRectF(start_x, barcode_y - 10, table_width, 20)  # Reduced to -10 for more spacing from border
        painter.drawText(product_code_text_rect, Qt.AlignmentFlag.AlignCenter, product_code)
        
        # Scale and draw QR codes
        scaled_qr_1 = qr_image_1.scaled(barcode_size, barcode_size, 
                                       Qt.AspectRatioMode.KeepAspectRatio, 
                                       Qt.TransformationMode.SmoothTransformation)
        scaled_qr_2 = qr_image_2.scaled(barcode_size, barcode_size,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        
        painter.drawImage(barcode_1_x, barcode_y, scaled_qr_1)
        painter.drawImage(barcode_2_x, barcode_y, scaled_qr_2)
        
        painter.end()
        
        logger.info(f"Successfully sent print job for {product_code} (copies: {copy_count})")
        return True
        
    except Exception as e:
        logger.error(f"Error printing product label: {e}")
        # Try to get more specific error information
        try:
            if 'painter' in locals() and painter.isActive():
                painter.end()
        except:
            pass
        
        # Log additional printer state information
        try:
            if 'printer' in locals():
                logger.error(f"Printer state: {printer.printerState()}")
                logger.error(f"Printer name: {printer.printerName()}")
        except:
            pass
            
        return False

def test_printer_connection(printer_name: Optional[str] = None) -> bool:
    """Test if printer is accessible using simplified approach."""
    try:
        logger.info(f"Testing printer connection: {printer_name}")
        
        # Create printer using the same method as main print function
        printer = create_label_printer(printer_name, use_simple_config=True)
        
        # Check if printer is valid
        if not printer.isValid():
            logger.error(f"Printer '{printer.printerName()}' is not valid")
            return False
        
        # Try to create a painter
        painter = QPainter(printer)
        if not painter.isActive():
            logger.error("Failed to start painting on printer")
            return False
        
        # Draw simple test content
        page_rect = painter.viewport()
        painter.setFont(QFont("Arial", 14))
        painter.drawText(page_rect, Qt.AlignmentFlag.AlignCenter, 
                        f"Test Print\nPrinter: {printer.printerName()}\nTime: {datetime.now().strftime('%H:%M:%S')}")
        
        painter.end()
        
        logger.info("Printer test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error testing printer connection: {e}")
        return False

def test_zebra_printer(printer_name: str) -> bool:
    """Simplified test for Zebra printers using standard approach."""
    try:
        logger.info(f"Testing Zebra printer: {printer_name}")
        
        # Use same approach as main print function
        return test_printer_connection(printer_name)
        
    except Exception as e:
        logger.error(f"Error testing Zebra printer: {e}")
        return False

def test_windows_printer(printer_name: str) -> bool:
    """Test printer using Windows print spooler directly."""
    try:
        import subprocess
        import tempfile
        import os
        
        logger.info(f"Testing Windows printer: {printer_name}")
        
        # Create a simple text file for testing
        test_content = f"""Test Print for {printer_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
This is a test print from the application.

If you can see this, the printer connection is working.
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Use Windows print command
            cmd = ['print', '/d:' + printer_name, temp_file]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Windows print command successful")
                return True
            else:
                logger.error(f"Windows print command failed: {result.stderr}")
                return False
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error testing Windows printer: {e}")
        return False 