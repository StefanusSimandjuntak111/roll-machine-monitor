from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Slot
import pyqtgraph as pg
from typing import List, Dict, Any, Tuple
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
        self.length_value_label: QLabel = None
        self.speed_value_label: QLabel = None
        self.shift_value_label: QLabel = None
        self.product_value_label: QLabel = None
        self.batch_value_label: QLabel = None
        self.target_value_label: QLabel = None
        
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
        
        layout.addLayout(graphs_layout)
    
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
        """Update display with new data."""
        # Update info cards
        self.length_value_label.setText(f"{data.get('length', 0.0):.1f} m")
        self.speed_value_label.setText(f"{data.get('speed', 0.0):.1f} m/min")
        self.shift_value_label.setText(data.get('shift', 'Day'))
        self.product_value_label.setText(data.get('product_code', 'Not Set'))
        self.batch_value_label.setText(data.get('batch_number', 'Not Set'))
        self.target_value_label.setText(f"{data.get('target_length', 0.0):.1f} m")
        
        # Update graphs
        current_time = datetime.now().timestamp()
        
        self.time_data.append(current_time)
        self.speed_data.append(data.get('speed', 0.0))
        self.length_data.append(data.get('length', 0.0))
        
        # Keep last 60 seconds of data
        if len(self.time_data) > 60:
            self.time_data = self.time_data[-60:]
            self.speed_data = self.speed_data[-60:]
            self.length_data = self.length_data[-60:]
        
        self.speed_curve.setData(self.time_data, self.speed_data)
        self.length_curve.setData(self.time_data, self.length_data) 