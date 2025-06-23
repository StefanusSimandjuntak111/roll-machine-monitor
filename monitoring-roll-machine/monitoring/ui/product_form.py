from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QLabel, QHBoxLayout,
    QRadioButton, QButtonGroup, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QPixmap
from typing import Dict, Any
import requests
from io import BytesIO

class ProductForm(QWidget):
    """Form for entering and editing product information."""
    
    # Signals
    product_updated = Signal(dict)
    start_monitoring = Signal()  # Signal for starting monitoring
    
    # Konstanta konversi
    METER_TO_YARD = 1.09361
    YARD_TO_METER = 0.9144
    DEFAULT_IMAGE_URL = "https://thumb.ac-illust.com/b1/b170870007dfa419295d949814474ab2_t.jpeg"
    
    def __init__(self):
        super().__init__()
        self._is_updating = False  # Flag untuk mencegah recursive updates
        self._current_unit = "Meter"  # Track current unit
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
        
        # Product Code
        self.product_code = QLineEdit()
        self.product_code.setPlaceholderText("Enter product code")
        self.product_code.setStyleSheet(input_style)
        form_layout.addRow("Product Code:", self.product_code)
        
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
        
        # Target Length with buttons
        length_container = QWidget()
        length_layout = QHBoxLayout(length_container)
        length_layout.setSpacing(5)  # Reduced spacing
        length_layout.setContentsMargins(0, 0, 0, 0)
        
        # Target Length Input
        self.target_length = QDoubleSpinBox()
        self.target_length.setRange(0, 100000)
        self.target_length.setDecimals(2)
        self.target_length.setValue(0.0)
        self.target_length.valueChanged.connect(self.on_length_changed)
        self.target_length.setStyleSheet(input_style + """
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0px;
                border: none;
            }
        """)
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
        
        form_layout.addRow("Target Length:", length_container)
        
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
        self.load_image(self.DEFAULT_IMAGE_URL)
        
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
        
        # Start Button
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_monitoring_with_save)
        self.start_button.setStyleSheet(action_button_style)
        self.start_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(self.start_button)
        
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
            
    def start_monitoring_with_save(self):
        """Save product info and start monitoring."""
        if self.validate_inputs():
            # Create product info dictionary
            product_info = {
                'product_code': self.product_code.text().strip(),
                'color_code': self.color_code.text().strip(),
                'batch_number': self.batch_number.text().strip(),
                'target_length': self.target_length.value(),
                'units': self.unit_group.checkedButton().text()
            }
            # Emit the product_updated signal
            self.product_updated.emit(product_info)
            # Emit the start_monitoring signal
            self.start_monitoring.emit()
        
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
            QLineEdit, QSpinBox, QDoubleSpinBox, QRadioButton {
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
            'color_code': self.color_code.text().strip(),
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'unit': self.unit_group.checkedButton().text()
        }
        
    def set_product_info(self, info: Dict[str, Any]):
        """Set product information in the form."""
        self.product_code.setText(info.get('product_code', ''))
        self.color_code.setText(info.get('color_code', ''))
        self.batch_number.setText(info.get('batch_number', ''))
        self.target_length.setValue(info.get('target_length', 0.0))
        self.unit_group.checkedButton().setChecked(True)

    def increment_length(self):
        """Increment target length by 1."""
        current_value = self.target_length.value()
        self.target_length.setValue(current_value + 1)

    def decrement_length(self):
        """Decrement target length by 1."""
        current_value = self.target_length.value()
        if current_value > 0:  # Prevent negative values
            self.target_length.setValue(current_value - 1)

    def load_image(self, url):
        """Load image from URL and display it."""
        try:
            response = requests.get(url)
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            # Load no-image placeholder
            self.image_label.setText("No Image Available")
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    border: 1px dashed #666666;
                    border-radius: 5px;
                    color: #666666;
                    font-size: 14px;
                }
            """)

    def save_product_info(self):
        """Validate and save product information."""
        if not self.validate_inputs():
            return
            
        # Create product info dictionary
        product_info = {
            'product_code': self.product_code.text().strip(),
            'color_code': self.color_code.text().strip(),
            'batch_number': self.batch_number.text().strip(),
            'target_length': self.target_length.value(),
            'units': self.unit_group.checkedButton().text()
        }
        # Emit the product_updated signal
        self.product_updated.emit(product_info) 