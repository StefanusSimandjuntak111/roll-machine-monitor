import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton,
                             QFrame, QScrollArea)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime
import json
import os

from ..logging_table import LoggingTable

class LoggingTableWidget(QWidget):
    """Widget untuk menampilkan tabel logging produksi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logging_table = LoggingTable()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Tabel Logging Produksi (50 Data Terakhir)")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_table)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Waktu", "Nama Produk", "Kode Produk", "Panjang (m)", 
            "Batch", "Waktu ke Print (s)", "Waktu ke Gulung (s)"
        ])
        
        # Set table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Waktu
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nama Produk
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Kode Produk
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Panjang
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Batch
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Waktu ke Print
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Waktu ke Gulung
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #bdc3c7;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #2c3e50;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Status label
        self.status_label = QLabel("Memuat data...")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin: 5px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        """Setup timer untuk auto-refresh setiap 5 menit (300000 ms)"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_table)
        self.refresh_timer.start(300000)  # 5 minutes

    def refresh_table(self):
        """Refresh tabel dengan data terbaru"""
        try:
            data = self.logging_table.get_last_50_entries()
            self.populate_table(data)
            self.status_label.setText(f"Data terakhir diperbarui: {datetime.now().strftime('%H:%M:%S')} - {len(data)} entri")
        except Exception as e:
            self.status_label.setText(f"Error memuat data: {str(e)}")

    # Public method to allow manual refresh from outside (e.g., after print)
    def manual_refresh(self):
        self.refresh_table()
            
    def populate_table(self, data):
        """Populate table dengan data"""
        self.table.setRowCount(len(data))
        
        for row, entry in enumerate(data):
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(entry.get('timestamp', ''))
                time_str = timestamp.strftime('%H:%M:%S')
            except:
                time_str = entry.get('timestamp', 'N/A')
                
            # Create table items
            items = [
                QTableWidgetItem(time_str),
                QTableWidgetItem(entry.get('product_name', 'N/A')),
                QTableWidgetItem(entry.get('product_code', 'N/A')),
                QTableWidgetItem(f"{entry.get('product_length', 0):.2f}"),
                QTableWidgetItem(entry.get('batch', 'N/A')),
                QTableWidgetItem(f"{entry.get('time_to_print', 0):.1f}"),
                QTableWidgetItem(f"{entry.get('time_to_roll', 0):.1f}")
            ]
            
            # Set items in table
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
                
        # Highlight latest entry
        if data:
            for col in range(self.table.columnCount()):
                item = self.table.item(len(data) - 1, col)
                if item:
                    item.setBackground(QColor(255, 255, 200))  # Light yellow
                    
    def add_production_entry(self, product_name, product_code, product_length, 
                           batch, time_to_print, time_to_roll):
        """Add new production entry to logging"""
        self.logging_table.log_production_data(
            product_name=product_name,
            product_code=product_code,
            product_length=product_length,
            batch=batch,
            time_to_print=time_to_print,
            time_to_roll=time_to_roll
        )
        self.refresh_table() 