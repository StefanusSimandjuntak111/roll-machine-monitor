from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QTextEdit, QPushButton,
    QGroupBox, QSplitter
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QTextCursor
import pyqtgraph as pg
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

class MonitoringView(QWidget):
    """Main monitoring view with real-time data display."""
    
    def __init__(self, logging_table_widget=None):
        super().__init__()
        
        # Initialize data storage
        self.time_data: List[float] = []
        self.speed_data: List[float] = []
        self.length_data: List[float] = []
        
        # Initialize value labels
        self.length_value_label: Optional[QLabel] = None
        self.speed_value_label: Optional[QLabel] = None
        self.shift_value_label: Optional[QLabel] = None
        self.product_value_label: Optional[QLabel] = None
        self.batch_value_label: Optional[QLabel] = None
        self.target_value_label: Optional[QLabel] = None
        
        # Store last valid length to prevent reset to 0
        self.last_valid_length: float = 0.0
        
        # Serial data display
        # Serial display removed
        self.logging_table_widget = logging_table_widget
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the monitoring view UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Create info cards grid
        info_grid = QGridLayout()
        info_grid.setSpacing(15)
        # info_grid.setContentsMargins(5, 5, 5, 5)
        
        # Length card
        length_card, self.length_value_label = self.create_info_card("Current Length (Machine)", "0.0 m")
        info_grid.addWidget(length_card, 0, 0)
        
        # Speed card
        speed_card, self.speed_value_label = self.create_info_card("Current Speed", "0.0 m/min")
        info_grid.addWidget(speed_card, 0, 1)
        
        # Shift card
        shift_card, self.shift_value_label = self.create_info_card("Current Shift", "Day")
        info_grid.addWidget(shift_card, 0, 2)
        
        # Product card
        product_card, self.product_value_label = self.create_info_card("Product Code", "Not Set")
        info_grid.addWidget(product_card, 1, 0)
        
        # Batch card
        batch_card, self.batch_value_label = self.create_info_card("Batch Number", "Not Set")
        info_grid.addWidget(batch_card, 1, 1)
        
        # Current Length card (renamed from Target Length)
        target_card, self.target_value_label = self.create_info_card("Length Print", "0.00 m")
        info_grid.addWidget(target_card, 1, 2)
        
        layout.addLayout(info_grid)
        
        # Add moderate spacing before table (reduced for 1366x768)
        layout.addSpacing(15)
        
        # Add logging table widget below info cards if available
        if self.logging_table_widget is not None:
            layout.addWidget(self.logging_table_widget)
        
        # Create splitter for graphs and serial data
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Graphs
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        
        # Create graphs
        graphs_layout = QHBoxLayout()
        
        # Speed graph
        speed_frame = QFrame()
        speed_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        speed_layout = QVBoxLayout(speed_frame)
        
        speed_label = QLabel("Speed Over Time")
        speed_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        speed_layout.addWidget(speed_label)
        
        self.speed_plot = pg.PlotWidget()
        self.speed_plot.setBackground('transparent')
        self.speed_plot.setTitle("Speed (m/min)")
        self.speed_plot.showGrid(x=True, y=True, alpha=0.3)
        self.speed_curve = self.speed_plot.plot(pen='g')
        speed_layout.addWidget(self.speed_plot)
        
        graphs_layout.addWidget(speed_frame)
        
        # Length graph
        length_frame = QFrame()
        length_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        length_layout = QVBoxLayout(length_frame)
        
        length_label = QLabel("Length Progress")
        length_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        length_layout.addWidget(length_label)
        
        self.length_plot = pg.PlotWidget()
        self.length_plot.setBackground('transparent')
        self.length_plot.setTitle("Length (m)")
        self.length_plot.showGrid(x=True, y=True, alpha=0.3)
        self.length_curve = self.length_plot.plot(pen='b')
        length_layout.addWidget(self.length_plot)
        
        graphs_layout.addWidget(length_frame)
        
        graphs_widget.setLayout(graphs_layout)
        splitter.addWidget(graphs_widget)
        
        # No serial display widget - removed to make space for cards
        
        layout.addWidget(splitter)
    
    def create_info_card(self, title: str, initial_value: str) -> Tuple[QFrame, QLabel]:
        """Create an info card with title and value."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 0.1px;
                min-height: 50px;
                max-height: 180px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        # layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888888; font-size: 12px; font-weight: normal;")
        # title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Add small stretch to separate title and value
        # layout.addStretch(1)
        
        value_label = QLabel(initial_value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # value_label.setWordWrap(True)
        layout.addWidget(value_label)
        
        # Add small stretch at bottom
        # layout.addStretch(1)
        
        return card, value_label
    
    @Slot(dict)
    def update_data(self, data: Dict[str, Any]):
        """Update display with new data from parsed JSK3588 packet."""
        # Update info cards with parsed data
        if self.length_value_label:
            # Display in original unit from machine (not always meters)
            fields = data.get('fields', {})
            current_count = fields.get('current_count', 0.0)
            unit = fields.get('unit', 'meter')
            factor = fields.get('factor', '×1.0')
            
            # Prevent length reset to 0 - use last valid length if current is 0
            if current_count > 0.001:  # If current length is valid (> 0.001)
                self.last_valid_length = current_count
            
            # Use last valid length if current is 0 or very small
            display_length = current_count if current_count > 0.001 else self.last_valid_length
            
            # Get decimal points from config (default to 2)
            try:
                from monitoring.config import get_config
                config = get_config()
                decimal_points = config.get("decimal_points", 2)
            except:
                decimal_points = 2
            
            # Format display with proper decimal points
            if unit == 'yard':
                self.length_value_label.setText(f"{display_length:.{decimal_points}f} yard")
            else:
                self.length_value_label.setText(f"{display_length:.{decimal_points}f} m")
        
        if self.speed_value_label:
            # Use parsed speed from JSK3588 packet
            speed_text = data.get('fields', {}).get('speed_text', '0.00 m/min')
            self.speed_value_label.setText(speed_text)
        
        if self.shift_value_label:
            # Use parsed shift from JSK3588 packet
            shift_text = data.get('fields', {}).get('shift_text', 'Day')
            self.shift_value_label.setText(shift_text)
        
        # Keep existing product info (not from JSK3588)
        if self.product_value_label:
            self.product_value_label.setText(data.get('product_code', 'Not Set'))
        if self.batch_value_label:
            self.batch_value_label.setText(data.get('batch_number', 'Not Set'))
        if self.target_value_label:
            # Display length print with tolerance (calculated in main_window)
            length_print_text = data.get('length_print_text', '0.00 m')
            self.target_value_label.setText(length_print_text)
        
        # Update graphs with parsed data
        current_time = datetime.now().timestamp()
        
        self.time_data.append(current_time)
        
        # Use parsed speed and length from JSK3588 packet
        speed_mps = data.get('speed_mps', 0.0)
        length_meters = data.get('length_meters', 0.0)
        
        # Use last valid length for graphs if current is 0
        if length_meters > 0.001:
            self.length_data.append(length_meters)
        elif self.last_valid_length > 0.001:
            self.length_data.append(self.last_valid_length)
        else:
            self.length_data.append(0.0)
        
        self.speed_data.append(speed_mps)
        
        # Keep last 60 seconds of data
        if len(self.time_data) > 60:
            self.time_data = self.time_data[-60:]
            self.speed_data = self.speed_data[-60:]
            self.length_data = self.length_data[-60:]
        
        # Safely update graphs - check if objects still exist
        try:
            if hasattr(self, 'speed_curve') and self.speed_curve is not None:
                self.speed_curve.setData(self.time_data, self.speed_data)
        except Exception as e:
            # If speed curve is deleted, recreate it
            try:
                self.speed_curve = self.speed_plot.plot(pen='g')
                self.speed_curve.setData(self.time_data, self.speed_data)
            except:
                pass  # Ignore if plot widget is also deleted
        
        try:
            if hasattr(self, 'length_curve') and self.length_curve is not None:
                self.length_curve.setData(self.time_data, self.length_data)
        except Exception as e:
            # If length curve is deleted, recreate it
            try:
                self.length_curve = self.length_plot.plot(pen='b')
                self.length_curve.setData(self.time_data, self.length_data)
            except:
                pass  # Ignore if plot widget is also deleted
    
    # Serial display methods removed - no longer needed
    
    def cleanup(self):
        """Clean up resources to prevent memory leaks."""
        try:
            # Clear plot data
            if hasattr(self, 'speed_curve') and self.speed_curve is not None:
                self.speed_curve.clear()
                self.speed_curve = None
            if hasattr(self, 'length_curve') and self.length_curve is not None:
                self.length_curve.clear()
                self.length_curve = None
            
            # Clear data lists
            self.time_data.clear()
            self.speed_data.clear()
            self.length_data.clear()
            
            # No serial display to clear anymore
                
        except Exception as e:
            # Ignore cleanup errors
            pass 