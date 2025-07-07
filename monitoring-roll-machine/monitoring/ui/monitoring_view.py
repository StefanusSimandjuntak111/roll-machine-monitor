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
    
    def __init__(self):
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
        
        # Serial data display
        self.serial_display: Optional[QTextEdit] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the monitoring view UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Create info cards grid
        info_grid = QGridLayout()
        info_grid.setSpacing(15)
        
        # Length card
        length_card, self.length_value_label = self.create_info_card("Current Length", "0.0 m")
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
        
        # Target card
        target_card, self.target_value_label = self.create_info_card("Target Length", "Not Set")
        info_grid.addWidget(target_card, 1, 2)
        
        layout.addLayout(info_grid)
        
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
        
        # Right side: Serial Data Display
        serial_widget = QWidget()
        serial_layout = QVBoxLayout(serial_widget)
        
        # Serial data group
        serial_group = QGroupBox("Serial Communication")
        serial_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        serial_group_layout = QVBoxLayout(serial_group)
        
        # Serial data display
        self.serial_display = QTextEdit()
        self.serial_display.setFont(QFont("Consolas", 9))
        self.serial_display.setMaximumHeight(300)
        self.serial_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        serial_group_layout.addWidget(self.serial_display)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Display")
        clear_btn.clicked.connect(self.clear_serial_display)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        serial_group_layout.addLayout(button_layout)
        
        serial_layout.addWidget(serial_group)
        splitter.addWidget(serial_widget)
        
        # Set splitter proportions (70% graphs, 30% serial)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
    
    def create_info_card(self, title: str, initial_value: str) -> Tuple[QFrame, QLabel]:
        """Create an info card with title and value."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(initial_value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        return card, value_label
    
    @Slot(dict)
    def update_data(self, data: Dict[str, Any]):
        """Update display with new data from parsed JSK3588 packet."""
        # Update info cards with parsed data
        if self.length_value_label:
            # Use parsed length from JSK3588 packet
            length_meters = data.get('length_meters', 0.0)
            self.length_value_label.setText(f"{length_meters:.2f} m")
        
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
            self.target_value_label.setText(f"{data.get('target_length', 0.0):.1f} m")
        
        # Update graphs with parsed data
        current_time = datetime.now().timestamp()
        
        self.time_data.append(current_time)
        
        # Use parsed speed and length from JSK3588 packet
        speed_mps = data.get('speed_mps', 0.0)
        length_meters = data.get('length_meters', 0.0)
        
        self.speed_data.append(speed_mps)
        self.length_data.append(length_meters)
        
        # Keep last 60 seconds of data
        if len(self.time_data) > 60:
            self.time_data = self.time_data[-60:]
            self.speed_data = self.speed_data[-60:]
            self.length_data = self.length_data[-60:]
        
        self.speed_curve.setData(self.time_data, self.speed_data)
        self.length_curve.setData(self.time_data, self.length_data)
    
    @Slot(str)
    def add_serial_data(self, data: str):
        """Add serial data to the display."""
        if self.serial_display:
            self.serial_display.append(data)
            
            # Auto-scroll to bottom
            cursor = self.serial_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.serial_display.setTextCursor(cursor)
    
    def add_packet_analysis(self, packet_hex: str):
        """Add packet analysis table to the display."""
        if self.serial_display:
            try:
                # Convert hex string to bytes
                hex_clean = packet_hex.replace(' ', '').upper()
                if len(hex_clean) % 2 != 0:
                    return
                
                packet_bytes = bytes.fromhex(hex_clean)
                
                # Import parser function
                from ..parser import format_packet_table
                
                # Format packet table
                table = format_packet_table(packet_bytes)
                
                # Add to display
                self.serial_display.append("\n" + "="*50)
                self.serial_display.append("PACKET ANALYSIS:")
                self.serial_display.append(table)
                self.serial_display.append("="*50 + "\n")
                
                # Auto-scroll to bottom
                cursor = self.serial_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.serial_display.setTextCursor(cursor)
                
            except Exception as e:
                self.serial_display.append(f"Error analyzing packet: {e}")
    
    def clear_serial_display(self):
        """Clear the serial data display."""
        if self.serial_display:
            self.serial_display.clear() 