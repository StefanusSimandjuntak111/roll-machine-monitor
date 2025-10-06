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
        
        # Configure Zebra label printer with correct page size
        if use_simple_config or "zebra" in printer.printerName().lower():
            logger.info("Configuring Zebra label printer with 10x10cm page size")
            
            # CRITICAL: Must set correct page size for Zebra to prevent 3-blink error
            # This is the #1 cause of media errors on Zebra printers
            try:
                # Try to get label size from config, otherwise use default 10x10cm
                from monitoring.config import load_config
                config = load_config()
                page_width_mm = config.get("label_width_mm", 100.0)  # Default: 10 cm
                page_height_mm = config.get("label_height_mm", 100.0)  # Default: 10 cm
                
                logger.info(f"Label size from config: {page_width_mm}x{page_height_mm}mm")
                
                # Create custom page size for Zebra label
                custom_size = QPageSize(
                    QSizeF(page_width_mm, page_height_mm),
                    QPageSize.Unit.Millimeter,
                    f"ZebraLabel_{page_width_mm}x{page_height_mm}mm",
                    QPageSize.SizeMatchPolicy.ExactMatch
                )
                
                # Set page size FIRST before other settings
                printer.setPageSize(custom_size)
                logger.info(f"✓ Set page size: {page_width_mm}x{page_height_mm}mm")
                
            except Exception as e:
                logger.error(f"✗ Failed to set custom page size: {e}")
                logger.warning("Trying fallback to printer default page size")
            
            # Configure printer for label printing
            printer.setFullPage(True)  # Use full page area for labels
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            
            # Use NativeFormat to respect Windows settings for:
            # - Print darkness/density (configured in Printing Preferences)
            # - Print speed
            # - Tear-off position
            # - Media type
            printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
            
            # Set resolution for Zebra ZD230 (203 DPI standard)
            try:
                printer.setResolution(203)
                logger.info(f"✓ Set resolution: 203 DPI")
            except Exception as e:
                logger.warning(f"Could not set resolution: {e}")
            
            # Log final configuration
            logger.info(f"Final Zebra printer configuration:")
            logger.info(f"  - Printer: {printer.printerName()}")
            logger.info(f"  - Page size: {printer.pageLayout().pageSize().name()}")
            logger.info(f"  - Page size (mm): {printer.pageLayout().pageSize().size(QPageSize.Unit.Millimeter)}")
            logger.info(f"  - Resolution: {printer.resolution()} DPI")
            logger.info(f"  - Full page: {printer.fullPage()}")
            logger.info(f"  - Output format: NativeFormat")
            logger.info(f"  - Orientation: Portrait")
            
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
        
        logger.info(f"Starting print job - Printer: {printer_name}, Copies: {copy_count}")
        
        # Use simple configuration that works for all printers (including Zebra)
        # This is the same approach that works in test_printer_connection()
        printer = create_label_printer(printer_name, use_simple_config=True)
        logger.info(f"Created printer with simple config: {printer.printerName()}")
        
        # Set copy count - simple approach that works for all printers
        try:
            printer.setCopyCount(copy_count)
            actual_copy_count = printer.copyCount()
            logger.info(f"Set copy count to {copy_count}, actual: {actual_copy_count}")
            
            if actual_copy_count != copy_count:
                logger.warning(f"Copy count mismatch: requested {copy_count}, got {actual_copy_count}")
        except Exception as e:
            logger.error(f"Error setting copy count: {e}, continuing with default")
        
        # Check if printer is ready
        if not printer.isValid():
            logger.error(f"Printer '{printer.printerName()}' is not valid")
            return False
        
        # Start printing with detailed logging
        logger.info(f"Starting print job - Printer: {printer.printerName()}, State: {printer.printerState()}")
        painter = QPainter(printer)
        if not painter.isActive():
            logger.error("Failed to start painting on printer")
            logger.error(f"Printer state: {printer.printerState()}")
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
        # Display format: product_code-print_length
        display_text = f"{product_code}-{print_length:.{decimal_points}f}"
        painter.drawText(product_code_text_rect, Qt.AlignmentFlag.AlignCenter, display_text)
        
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
        
        # Log detailed print job completion info
        logger.info(f"Successfully sent print job for {product_code} (copies: {copy_count})")
        logger.info(f"Print job completed - Printer: {printer.printerName()}, State: {printer.printerState()}")
        
        # For Zebra printers, add additional verification
        if "zebra" in printer_name.lower() or "zdesigner" in printer_name.lower():
            logger.info("Zebra printer detected - print job sent to spooler")
        
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

def test_print_copy_count(printer_name: Optional[str] = None, test_copy_counts: List[int] = [1, 2, 3]) -> Dict[str, Any]:
    """Test print copy count functionality with different values."""
    results = {}
    
    try:
        # Get printer name from config if not provided
        if printer_name is None:
            from monitoring.config import load_config
            config = load_config()
            printer_name = config.get("selected_printer")
        
        logger.info(f"Testing print copy count with printer: {printer_name}")
        
        for copy_count in test_copy_counts:
            try:
                logger.info(f"Testing copy count: {copy_count}")
                
                # Create printer
                printer = create_label_printer(printer_name, use_simple_config=True)
                
                # Set copy count
                printer.setCopyCount(copy_count)
                actual_copy_count = printer.copyCount()
                
                logger.info(f"Requested copy count: {copy_count}, Actual copy count: {actual_copy_count}")
                
                # Test if printer is valid
                is_valid = printer.isValid()
                
                # Test if we can start painting
                painter = QPainter(printer)
                can_paint = painter.isActive()
                painter.end()
                
                result = {
                    "success": is_valid and can_paint,
                    "is_valid": is_valid,
                    "can_paint": can_paint,
                    "requested_copy_count": copy_count,
                    "actual_copy_count": actual_copy_count,
                    "copy_count_matches": copy_count == actual_copy_count
                }
                
                results[str(copy_count)] = result
                
                logger.info(f"Copy count {copy_count} test result: {result}")
                
            except Exception as e:
                logger.error(f"Error testing copy count {copy_count}: {e}")
                results[str(copy_count)] = {
                    "success": False,
                    "error": str(e),
                    "is_valid": False,
                    "can_paint": False,
                    "requested_copy_count": copy_count,
                    "actual_copy_count": 0,
                    "copy_count_matches": False
                }
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_print_copy_count: {e}")
        return {"error": str(e)}

def debug_print_copy_issue():
    """Debug function to test print copy count issue."""
    try:
        from monitoring.config import load_config, save_config
        
        # Test case 1: Copy count = 1
        logger.info("=== TEST CASE 1: Copy count = 1 ===")
        config = load_config()
        config["print_copy_count"] = 1
        save_config(config)
        
        # Test print with copy count = 1
        test_result_1 = test_print_copy_count()
        logger.info(f"Test result for copy count 1: {test_result_1}")
        
        # Test case 2: Copy count = 2
        logger.info("=== TEST CASE 2: Copy count = 2 ===")
        config = load_config()
        config["print_copy_count"] = 2
        save_config(config)
        
        # Test print with copy count = 2
        test_result_2 = test_print_copy_count()
        logger.info(f"Test result for copy count 2: {test_result_2}")
        
        # Compare results
        logger.info("=== COMPARISON ===")
        logger.info(f"Copy count 1 success: {test_result_1.get('1', {}).get('success', False)}")
        logger.info(f"Copy count 2 success: {test_result_2.get('2', {}).get('success', False)}")
        
        return {
            "copy_count_1": test_result_1,
            "copy_count_2": test_result_2
        }
        
    except Exception as e:
        logger.error(f"Error in debug_print_copy_issue: {e}")
        return {"error": str(e)}

def print_with_zebra_compatibility(product_info: Dict[str, Any], current_machine_length: Optional[float] = None, printer_name: str = None, copy_count: int = 1) -> bool:
    """Print using the working QPrintDialog approach for Zebra compatibility."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter, QPrinterInfo, QPrintPreviewWidget, QPrintDialog
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPainter, QFont, QPen, QColor, QBrush, QRectF, QPageLayout, QPageSize, QSizeF
        
        logger.info(f"Starting Zebra-compatible print job - Printer: {printer_name}, Copies: {copy_count}")
        
        # Create printer with Zebra-compatible settings
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # Set printer by name
        if printer_name:
            printer.setPrinterName(printer_name)
            logger.info(f"Set printer name to: {printer_name}")
        
        # Set up custom page size (10x10cm) for Zebra label - same as working version
        page_width_mm = 100.0  # 10 cm
        page_height_mm = 100.0  # 10 cm
        
        # Create custom page size
        custom_size = QPageSize(
            QSizeF(page_width_mm, page_height_mm),
            QPageSize.Unit.Millimeter,
            "Custom_10x10cm",
            QPageSize.SizeMatchPolicy.ExactMatch
        )
        
        # Configure printer settings - exactly like working version
        printer.setPageSize(custom_size)
        printer.setFullPage(True)  # Important for label printers
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        
        # Set resolution to match Zebra ZD230 (203 DPI)
        printer.setResolution(203)
        
        # Set copy count
        printer.setCopyCount(copy_count)
        logger.info(f"Set copy count to: {copy_count}")
        
        # Force first page
        printer.setFromTo(1, 1)
        
        # Check if printer is valid
        if not printer.isValid():
            logger.error(f"Printer '{printer_name}' is not valid")
            return False
        
        logger.info(f"Printer is valid, starting print job")
        
        # Use QPrintDialog for better compatibility with Zebra printers
        dialog = QPrintDialog(printer, None)
        
        # For automated printing, we'll bypass the dialog but use the same printing logic
        # This maintains compatibility with the working version
        logger.info("Using direct printing (bypassing dialog for automation)")
        
        # Start printing
        painter = QPainter(printer)
        if not painter.isActive():
            logger.error("Failed to start painting on printer")
            return False
            
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Get page rect in device pixels - same as working version
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        page_width_px = page_rect.width()
        page_height_px = page_rect.height()
        
        logger.info(f"Page dimensions: {page_width_px} x {page_height_px} pixels")
        
        # Calculate table size in pixels (same as working version)
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
        
        # Calculate row heights (same as working version)
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
        
        # Get product data
        print_length = product_info.get('print_length', product_info.get('current_length', product_info.get('target_length', 0.0)))
        decimal_points = product_info.get('decimal_points', 1)
        product_code = product_info.get('product_code', 'DEFAULT')
        product_name = product_info.get('product_name', 'Default Product')
        
        # Header - Product Code (merged across full width)
        header_font = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(header_font)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        
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
            str(product_info.get('color_code', '1')),  # Use color_code field
            f"{print_length:.{decimal_points}f} {product_info.get('units', 'Yard')}",
            str(product_info.get('roll_number', '0')),  # Default roll number: 0
            str(product_info.get('batch_number', 'None'))  # Use batch_number as lot_number
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
        
        # Generate QR codes
        qr_data_1 = str(product_code)  # Barcode 1: Product Code
        qr_image_1 = generate_qr_code(qr_data_1)
        
        # Always use format: product_code-print_length
        qr_data_2 = f"{product_code}-{print_length:.{decimal_points}f}"
        qr_image_2 = generate_qr_code(qr_data_2)
        
        # Scale QR codes
        scaled_qr_1 = qr_image_1.scaled(
            barcode_size_px, 
            barcode_size_px, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        scaled_qr_2 = qr_image_2.scaled(
            barcode_size_px, 
            barcode_size_px, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Draw QR codes
        painter.drawImage(barcode_left_x, barcode_y, scaled_qr_1)
        painter.drawImage(barcode_right_x, barcode_y, scaled_qr_2)
        
        painter.end()
        
        logger.info(f"Successfully sent Zebra-compatible print job for {product_code} (copies: {copy_count})")
        return True
        
    except Exception as e:
        logger.error(f"Error in Zebra-compatible printing: {e}")
        try:
            if 'painter' in locals() and painter.isActive():
                painter.end()
        except:
            pass
        return False 