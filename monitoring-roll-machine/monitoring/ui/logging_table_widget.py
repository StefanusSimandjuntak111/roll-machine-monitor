import sys
import json
import os
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QFrame, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from ..logging_table import LoggingTable

# Setup logger
logger = logging.getLogger(__name__)

class LoggingTableWidget(QWidget):
    """Widget to display production logging table"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logging_table = LoggingTable()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Simple title
        title_label = QLabel("Production Logging Table")
        layout.addWidget(title_label)

        # Simple refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_table)
        layout.addWidget(refresh_btn)
        
        # Table - MINIMAL VERSION
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "No", "Date/Time", "Product Code", "Product Name", "Length (m)",
            "Batch", "Cycle Time", "Roll Time"
        ])
        
        # Basic table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Set table size
        self.table.setMinimumHeight(250)  # Reduced for compact layout
        self.table.setMinimumWidth(600)   # Reduced for better fit
        self.table.setMaximumHeight(350)  # Limit maximum height
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # No
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Date/Time      
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Product Code
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Product Name   
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Length
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Batch
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Cycle Time     
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Roll Time      

        # NO STYLING AT ALL
        layout.addWidget(self.table)
        
        # Status label
        self.status_label = QLabel("Loading data...")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        """Setup timer for auto-refresh every 5 minutes (300000 ms)"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_table)
        self.refresh_timer.start(300000)  # 5 minutes

    def refresh_table(self):
        """Refresh table with latest data"""
        try:
            data = self.logging_table.get_last_50_entries()
            self.populate_table(data)
            self.status_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')} - {len(data)} entries")
        except Exception as e:
            self.status_label.setText(f"Error loading data: {str(e)}")

    # Public method to allow manual refresh from outside (e.g., after print)
    def manual_refresh(self):
        self.refresh_table()
            
    def populate_table(self, data):
        """Populate table with data"""
        self.table.setRowCount(len(data))
        
        for row, entry in enumerate(data):
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(entry.get('timestamp', ''))
                time_str = timestamp.strftime('%H:%M:%S')
            except:
                time_str = entry.get('timestamp', 'N/A')
            
            # Handle cycle_time - display empty string if None
            cycle_time = entry.get('cycle_time', 0)
            cycle_time_str = f"{cycle_time:.1f}" if cycle_time is not None else ""
                
            # Create table items with row number
            items = [
                QTableWidgetItem(str(row + 1)),  # No
                QTableWidgetItem(time_str),
                QTableWidgetItem(entry.get('product_code', 'N/A')),
                QTableWidgetItem(entry.get('product_name', 'N/A')),
                QTableWidgetItem(f"{entry.get('product_length', 0):.2f}"),
                QTableWidgetItem(entry.get('batch', 'N/A')),
                QTableWidgetItem(cycle_time_str),  # Use formatted cycle time string
                QTableWidgetItem(f"{entry.get('roll_time', 0):.1f}")
            ]
            
            # Set items in table
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
                
        # Highlight latest entry
        if data:
            for col in range(self.table.columnCount()):
                item = self.table.item(len(data) - 1, col)
                if item:
                    item.setBackground(QColor(52, 152, 219))  # Blue highlight for dark theme
                    
    def add_production_entry(self, product_name, product_code, product_length, 
                           batch, cycle_time, roll_time):
        """Add new production entry to logging"""
        self.logging_table.log_production_data(
            product_name=product_name,
            product_code=product_code,
            product_length=product_length,
            batch=batch,
            cycle_time=cycle_time,
            roll_time=roll_time
        )
        self.refresh_table()
    
    def update_last_entry_cycle_time(self, cycle_time):
        """Update the cycle time of the last entry in the logging table"""
        try:
            # Get the last entry from logging table
            data = self.logging_table.load_today_data()
            if data:
                # Update the last entry's cycle time
                last_entry = data[-1]
                last_entry['cycle_time'] = cycle_time
                
                # Save the updated data back to file by overwriting the entire file
                filename = self.logging_table.get_today_filename()
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Refresh the table to show the update
                self.refresh_table()
                
                logger.info(f"Updated last entry cycle time to: {cycle_time:.1f}s")
                except Exception as e:
                    logger.error(f"Error saving updated data to file: {e}")
            else:
                logger.warning("No entries found to update cycle time")
        except Exception as e:
            logger.error(f"Error updating last entry cycle time: {e}") 