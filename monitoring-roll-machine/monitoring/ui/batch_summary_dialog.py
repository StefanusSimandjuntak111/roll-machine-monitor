"""
Dialog untuk menampilkan summary/recap per batch.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox,
    QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, date

from ..logging_table import LoggingTable
from ..supabase_client import SupabaseClient
from ..config import load_config

logger = logging.getLogger(__name__)


class BatchSummaryDialog(QDialog):
    """Dialog untuk menampilkan batch summary/recap."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Summary / Recap")
        self.setMinimumSize(1000, 600)
        
        # Initialize data sources
        config = load_config()
        self.logging_table = LoggingTable()
        
        # Initialize Supabase client if enabled
        self.supabase_client = None
        if config.get('enable_supabase', False):
            self.supabase_client = SupabaseClient(
                url=config.get('supabase_url'),
                key=config.get('supabase_key')
            )
        
        self.setup_ui()
        self.load_batches()
    
    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-height: 35px;
            }
            QComboBox:hover {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                gridline-color: #444444;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #e0e0e0;
                padding: 10px;
                border: 1px solid #444444;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cc1;
            }
        """)
        
        # Header
        header_label = QLabel("📊 Batch Production Summary")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Batch selector
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(10)
        
        batch_label = QLabel("Select Batch:")
        batch_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        selector_layout.addWidget(batch_label)
        
        self.batch_combo = QComboBox()
        self.batch_combo.setMinimumWidth(300)
        self.batch_combo.currentTextChanged.connect(self.on_batch_selected)
        selector_layout.addWidget(self.batch_combo)
        
        selector_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_batches)
        selector_layout.addWidget(refresh_btn)
        
        layout.addLayout(selector_layout)
        
        # Summary info frame
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        summary_layout = QVBoxLayout(self.summary_frame)
        
        self.summary_label = QLabel("No batch selected")
        self.summary_label.setFont(QFont("Segoe UI", 11))
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        
        layout.addWidget(self.summary_frame)
        
        # Detail table
        detail_label = QLabel("Production Details:")
        detail_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(detail_label)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(7)
        self.detail_table.setHorizontalHeaderLabels([
            "No", "Product Code", "Product Name", "Length (m)", 
            "Cycle Time (s)", "Roll Time (s)", "Timestamp"
        ])
        
        # Set column widths
        header = self.detail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(60)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.detail_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        export_btn = QPushButton("📥 Export CSV")
        export_btn.clicked.connect(self.export_batch_data)
        button_layout.addWidget(export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_batches(self):
        """Load available batches from Supabase or local JSON."""
        self.batch_combo.clear()
        
        batches = []
        
        # Try Supabase first
        if self.supabase_client and self.supabase_client.is_connected:
            try:
                today = date.today().strftime('%Y-%m-%d')
                batches = self.supabase_client.get_all_batches(date_str=today)
                logger.info(f"Loaded {len(batches)} batches from Supabase")
            except Exception as e:
                logger.error(f"Error loading batches from Supabase: {e}")
        
        # Fallback to local JSON (batch_tracking.json from batch_manager)
        if not batches:
            try:
                # Try to get batch from batch_manager state file
                from ..batch_manager import get_batch_manager
                batch_manager = get_batch_manager()
                current_batch = batch_manager.get_current_batch()
                
                if current_batch:
                    # Get all historical batches (1 to current)
                    batches = [str(i) for i in range(batch_manager.current_counter, 0, -1)]
                    logger.info(f"Loaded {len(batches)} batches from batch_manager (1 to {batch_manager.current_counter})")
                else:
                    # Fallback to production logs
                    all_data = self.logging_table.load_today_data()
                    # Filter out None, empty strings, and "unknown" values
                    batches = list(set(
                        d.get('batch') for d in all_data 
                        if d.get('batch') and 
                        d.get('batch') not in [None, '', 'unknown', 'Unknown']
                    ))
                    batches.sort(reverse=True, key=lambda x: int(x) if x.isdigit() else 0)
                    logger.info(f"Loaded {len(batches)} batches from local JSON")
            except Exception as e:
                logger.error(f"Error loading batches from local sources: {e}")
        
        if batches:
            self.batch_combo.addItems(batches)
        else:
            self.batch_combo.addItem("No batches available")
            self.summary_label.setText("No production data found for today")
    
    def on_batch_selected(self, batch: str):
        """Handle batch selection."""
        if not batch or batch == "No batches available":
            return
        
        # Get batch summary
        summary = self.logging_table.get_batch_summary(batch)
        
        if not summary:
            self.summary_label.setText(f"No data found for batch: {batch}")
            self.detail_table.setRowCount(0)
            return
        
        # Update summary info
        summary_text = f"""
        <b>Batch:</b> {summary['batch']}<br>
        <b>Product Code:</b> {summary['product_code']}<br>
        <b>Product Name:</b> {summary['product_name']}<br>
        <b>Total Rolls:</b> {summary['total_rolls']}<br>
        <b>Total Length:</b> {summary['total_length']:.2f} m<br>
        <b>Average Cycle Time:</b> {summary['avg_cycle_time']:.1f} s<br>
        <b>Average Roll Time:</b> {summary['avg_roll_time']:.1f} s<br>
        <b>Start Time:</b> {self._format_timestamp(summary['start_time'])}<br>
        <b>End Time:</b> {self._format_timestamp(summary['end_time'])}
        """
        self.summary_label.setText(summary_text)
        
        # Update detail table
        logs = summary.get('logs', [])
        self.detail_table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            self.detail_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.detail_table.setItem(i, 1, QTableWidgetItem(log.get('product_code', '')))
            self.detail_table.setItem(i, 2, QTableWidgetItem(log.get('product_name', '')))
            self.detail_table.setItem(i, 3, QTableWidgetItem(f"{log.get('product_length', 0):.2f}"))
            
            cycle_time = log.get('cycle_time')
            self.detail_table.setItem(i, 4, QTableWidgetItem(
                f"{cycle_time:.1f}" if cycle_time is not None else "N/A"
            ))
            
            self.detail_table.setItem(i, 5, QTableWidgetItem(f"{log.get('roll_time', 0):.1f}"))
            self.detail_table.setItem(i, 6, QTableWidgetItem(
                self._format_timestamp(log.get('timestamp', ''))
            ))
    
    def export_batch_data(self):
        """Export current batch data to CSV."""
        batch = self.batch_combo.currentText()
        if not batch or batch == "No batches available":
            QMessageBox.warning(self, "Export Error", "No batch selected")
            return
        
        try:
            from ..session import MonitoringSession
            summary = self.logging_table.get_batch_summary(batch)
            
            if not summary:
                QMessageBox.warning(self, "Export Error", "No data found for selected batch")
                return
            
            # Create session and export
            session = MonitoringSession(export_dir="exports")
            session.data = summary.get('logs', [])
            session.start_time = datetime.fromisoformat(summary['start_time'])
            
            # Export with batch name in filename
            filename = f"batch_{batch.replace(':', '-')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = session.export_dir + "/" + filename
            
            from ..exporter import export_to_csv
            export_to_csv(session.data, filepath)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Batch data exported to:\n{filepath}"
            )
            logger.info(f"Batch {batch} exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting batch data: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export batch data:\n{str(e)}"
            )
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format ISO timestamp to readable format."""
        try:
            if not timestamp_str:
                return "N/A"
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return timestamp_str

