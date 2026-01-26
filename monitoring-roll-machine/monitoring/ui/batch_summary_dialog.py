"""
Dialog untuk menampilkan summary/recap per batch.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox,
    QHeaderView, QFrame, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from typing import Dict, Any, List, Optional
import logging
import re
from datetime import datetime, date

from ..logging_table import LoggingTable
from ..supabase_client import SupabaseClient
from ..config import load_config
from ..erp_client import get_erp_client

logger = logging.getLogger(__name__)


class BatchSummaryDialog(QDialog):
    """Dialog untuk menampilkan batch summary/recap."""
    
    def __init__(self, parent=None, safe_mode=False, safe_mode_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Summary / Recap")
        self.setMinimumSize(1000, 600)

        # Initialize data sources
        self.config = self._load_config_from_parent_or_disk()
        self.safe_mode = safe_mode  # Safe Mode flag
        self.safe_mode_settings = safe_mode_settings or {}  # Safe Mode settings
        self.logging_table = LoggingTable(safe_mode=safe_mode)

        # Initialize external clients based on config
        self.supabase_client: Optional[SupabaseClient] = None
        self.erp_client = None
        self._refresh_external_clients()

        self.setup_ui()
        self.load_batches()

    def _load_config_from_parent_or_disk(self) -> Dict[str, Any]:
        """Load konfigurasi terbaru dari parent (jika ada) atau dari disk.

        Ini mencegah kasus di mana dialog ini memakai snapshot config lama, padahal
        Settings sudah disimpan (misalnya BOM sudah dipilih).
        """
        parent = self.parent()
        try:
            parent_config = getattr(parent, "config", None) if parent is not None else None
            if isinstance(parent_config, dict) and parent_config:
                return dict(parent_config)
        except Exception as exc:
            logger.warning(f"Failed to read config from parent: {exc}")

        return load_config()

    def _refresh_external_clients(self) -> None:
        """(Re)inisialisasi client Supabase/ERP sesuai konfigurasi."""
        # Supabase
        self.supabase_client = None
        if self.config.get("enable_supabase", False):
            self.supabase_client = SupabaseClient(
                url=self.config.get("supabase_url"),
                key=self.config.get("supabase_key"),
            )

        # ERP
        self.erp_client = None
        if self.config.get("enable_erp_submission", False):
            self.erp_client = get_erp_client(self.config)

    def apply_settings_update(self, settings: Dict[str, Any]) -> None:
        """Terima update settings saat dialog sudah terbuka."""
        if not settings:
            return

        self.config.update(settings)
        self._refresh_external_clients()
        self._update_erp_button_state()
    
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
                background-color: #0078d4;
            }
            QComboBox:focus {
                border: 2px solid #0078d4;
                background-color: #1a1a1a;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 10px 12px;
                border: none;
                border-radius: 3px;
                margin: 1px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #0078d4;
                border-radius: 3px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
                color: white;
                border: 1px solid #1084d8;
                border-radius: 3px;
                font-weight: bold;
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
            QTableCornerButton::section {
                background-color: #252525;
                border: 1px solid #444444;
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

        # Hide default vertical header (row number strip) to avoid light/white area on empty rows.
        # We already have a "No" column for numbering.
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.setCornerButtonEnabled(False)
        self.detail_table.setShowGrid(True)
        
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
        
        # Submit to ERP button (replaces Export CSV)
        self.submit_btn = QPushButton("📤 Submit to ERP")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_to_erp)
        button_layout.addWidget(self.submit_btn)
        
        # Keep export CSV as secondary option (hidden by default, can be shown for backup)
        self.export_btn = QPushButton("📥 Export CSV")
        self.export_btn.clicked.connect(self.export_batch_data)
        self.export_btn.setVisible(False)  # Hidden by default
        button_layout.addWidget(self.export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Check if ERP is configured and update button state
        self._update_erp_button_state()
        
        # Initialize submitted batches tracking
        self.submitted_batches = self._load_submitted_batches()
    
    def _load_submitted_batches(self):
        """Load list of batches that have been submitted to ERP."""
        try:
            import json
            import os
            from pathlib import Path
            
            # Create submitted batches file path
            submitted_file = Path("logs") / "submitted_batches.json"
            
            if submitted_file.exists():
                with open(submitted_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('submitted_batches', []))
            else:
                return set()
        except Exception as e:
            logger.error(f"Error loading submitted batches: {e}")
            return set()
    
    def _save_submitted_batches(self):
        """Save list of submitted batches to file."""
        try:
            import json
            import os
            from pathlib import Path
            
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Save submitted batches
            submitted_file = logs_dir / "submitted_batches.json"
            data = {
                'submitted_batches': list(self.submitted_batches),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(submitted_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(self.submitted_batches)} submitted batches")
        except Exception as e:
            logger.error(f"Error saving submitted batches: {e}")
    
    def _mark_batch_as_submitted(self, batch_name):
        """Mark a batch as submitted to ERP."""
        self.submitted_batches.add(batch_name)
        self._save_submitted_batches()
        logger.info(f"Marked batch {batch_name} as submitted to ERP")
    
    def _extract_increment_number(self, batch_name: str) -> int:
        """
        Extract 4 digit autoincrement number dari akhir nama batch.
        
        Args:
            batch_name: Nama batch (contoh: PRE.BD_2026-01-20_021_0101_0046)
            
        Returns:
            Angka increment (contoh: 46) atau 0 jika tidak ditemukan
        """
        try:
            # Ambil 4 digit terakhir dari nama batch
            # Format: PRE.BD_2026-01-20_021_0101_0046
            # Split by underscore dan ambil bagian terakhir
            parts = batch_name.split('_')
            if parts:
                last_part = parts[-1]
                # Extract angka dari bagian terakhir
                if last_part.isdigit():
                    return int(last_part)
                # Jika tidak langsung angka, coba extract angka dari akhir string
                match = re.search(r'(\d{4})$', batch_name)
                if match:
                    return int(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting increment number from batch '{batch_name}': {e}")
        return 0
    
    def _sort_batches_by_increment(self, batches: List[str]) -> List[str]:
        """
        Sort batch list berdasarkan 4 digit autoincrement di akhir nama batch.
        Angka terbesar berada di paling atas, angka terkecil di paling bawah (descending).
        
        Args:
            batches: List of batch names
            
        Returns:
            Sorted list of batch names (descending by increment number)
        """
        try:
            # Sort berdasarkan increment number (descending: besar ke kecil)
            # Angka terbesar di atas, angka terkecil di bawah
            sorted_batches = sorted(batches, key=lambda x: self._extract_increment_number(x), reverse=True)
            logger.info(f"Sorted {len(sorted_batches)} batches by increment number (descending)")
            return sorted_batches
        except Exception as e:
            logger.error(f"Error sorting batches by increment: {e}")
            # Fallback to original order if sorting fails
            return batches
    
    def load_batches(self):
        """Load available batches from Supabase or local JSON."""
        self.batch_combo.clear()
        
        batches = []
        batches_from_supabase = []
        batches_from_local = []
        
        # Try Supabase first
        if self.supabase_client and self.supabase_client.is_connected:
            try:
                today = date.today().strftime('%Y-%m-%d')
                batches_from_supabase = self.supabase_client.get_all_batches(date_str=today)
                logger.info(f"Loaded {len(batches_from_supabase)} batches from Supabase")
            except Exception as e:
                logger.error(f"Error loading batches from Supabase: {e}")
        
        # Load from local batch metadata store
        try:
            from ..batch_metadata_store import get_batch_metadata_store
            metadata_store = get_batch_metadata_store()
            today = date.today().strftime('%Y-%m-%d')
            batches_from_local = metadata_store.get_all_batches(date_str=today)
            logger.info(f"Loaded {len(batches_from_local)} batches from local storage")
        except Exception as e:
            logger.error(f"Error loading batches from local storage: {e}")
        
        # Merge and deduplicate batches from both sources
        # Use set to deduplicate, then convert back to list and sort
        all_batches = set(batches_from_supabase + batches_from_local)
        
        # Filter out submitted batches
        available_batches = [batch for batch in all_batches if batch not in self.submitted_batches]
        # Sort berdasarkan 4 digit autoincrement di akhir nama batch (ascending: kecil ke besar)
        batches = self._sort_batches_by_increment(available_batches)
        
        logger.info(f"Filtered out {len(all_batches) - len(available_batches)} submitted batches")
        
        # Additional fallback to production logs if both sources are empty
        # HANYA ambil dari data logging hari ini, TIDAK generate dari batch_manager counter
        if not batches:
            try:
                # HANYA ambil dari production logs hari ini
                all_data = self.logging_table.load_today_data()
                # Filter out None, empty strings, and "unknown" values
                all_batches = list(set(
                    d.get('batch') for d in all_data 
                    if d.get('batch') and 
                    d.get('batch') not in [None, '', 'unknown', 'Unknown']
                ))
                # Filter out submitted batches
                batches = [batch for batch in all_batches if batch not in self.submitted_batches]
                # Sort berdasarkan 4 digit autoincrement di akhir nama batch (ascending: kecil ke besar)
                batches = self._sort_batches_by_increment(batches)
                logger.info(f"Loaded {len(batches)} batches from today's production logs (filtered from {len(all_batches)})")
            except Exception as e:
                logger.error(f"Error loading batches from local sources: {e}")
        
        if batches:
            self.batch_combo.addItems(batches)
        else:
            self.batch_combo.addItem("No batches available")
            if self.submitted_batches:
                self.summary_label.setText(f"No new batches available. {len(self.submitted_batches)} batch(es) already submitted to ERP.")
            else:
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
            # Gunakan length_print jika tersedia (dengan tolerance), fallback ke product_length
            length_value = log.get('length_print') if log.get('length_print') is not None else log.get('product_length', 0)
            self.detail_table.setItem(i, 3, QTableWidgetItem(f"{length_value:.2f}"))
            
            cycle_time = log.get('cycle_time')
            self.detail_table.setItem(i, 4, QTableWidgetItem(
                f"{cycle_time:.1f}" if cycle_time is not None else "N/A"
            ))
            
            self.detail_table.setItem(i, 5, QTableWidgetItem(f"{log.get('roll_time', 0):.1f}"))
            self.detail_table.setItem(i, 6, QTableWidgetItem(
                self._format_timestamp(log.get('timestamp', ''))
            ))
    
    def _update_erp_button_state(self):
        """Update ERP button state based on configuration."""
        if not self.config.get('enable_erp_submission', False):
            self.submit_btn.setEnabled(False)
            self.submit_btn.setToolTip("ERP submission is disabled in configuration")
            self.export_btn.setVisible(True)  # Show CSV export if ERP disabled
            logger.info("ERP submission disabled - showing CSV export option")
        elif not self.erp_client:
            self.submit_btn.setEnabled(False)
            self.submit_btn.setToolTip("ERP not configured - check API credentials")
            self.export_btn.setVisible(True)  # Show CSV export as fallback
            logger.warning("ERP client not initialized - credentials may be missing")
        else:
            self.submit_btn.setEnabled(True)
            self.submit_btn.setToolTip("Submit batch data to ERP system")
            logger.info("ERP submission enabled and ready")
    
    def submit_to_erp(self):
        """Submit current batch data to ERP system."""
        # Always refresh config before submission (avoid stale BOM/ERP settings)
        self.config = self._load_config_from_parent_or_disk()
        self._refresh_external_clients()
        self._update_erp_button_state()

        # Check if Safe Mode is active and ERP is not allowed
        if self.safe_mode and not self.safe_mode_settings.get("send_erp", False):
            QMessageBox.warning(
                self,
                "Safe Mode Active",
                "Safe Mode is currently active.\n\n"
                "ERP submission is disabled in your Safe Mode configuration.\n\n"
                "To enable ERP submission, disable Safe Mode and reconfigure it."
            )
            logger.warning("ERP submission blocked - Safe Mode active and ERP not allowed")
            return

        batch = self.batch_combo.currentText()
        if not batch or batch == "No batches available":
            QMessageBox.warning(
                self,
                "Submission Error",
                "No batch selected. Please select a batch to submit."
            )
            return

        # Check ERP client
        if not self.erp_client:
            QMessageBox.critical(
                self,
                "ERP Not Configured",
                "ERP system is not configured.\n\n"
                "Please configure ERP settings:\n"
                "- ERP URL\n"
                "- API Key\n"
                "- API Secret\n\n"
                "Contact administrator for assistance."
            )
            return
        
        # Get batch summary
        summary = self.logging_table.get_batch_summary(batch)
        
        if not summary:
            QMessageBox.warning(
                self,
                "Submission Error",
                f"No data found for batch: {batch}"
            )
            return
        
        # Get BOM from config
        bom_name = self.config.get('bom_name', '').strip()
        
        if not bom_name:
            QMessageBox.warning(
                self,
                "BOM Not Configured",
                "BOM is not configured.\n\n"
                "Please configure BOM in Settings:\n"
                "Settings → 📤 ERP Stock Entry → BOM Selection\n\n"
                "The BOM determines which raw materials will be consumed\n"
                "and what finished item will be produced."
            )
            return
        
        logger.info(f"Using BOM from config: {bom_name}")
        
        # Get finished item from BOM config or product code
        finished_item = self.config.get('bom_item', '') or summary.get('product_code', '')
        
        logger.info(f"BOM: {bom_name}, Finished Item: {finished_item}")
        
        # Confirm submission
        confirm_msg = (
            f"<b>Submit Batch to ERP?</b><br><br>"
            f"<b>Batch:</b> {batch}<br>"
            f"<b>Product:</b> {summary.get('product_code', 'N/A')} - {summary.get('product_name', 'N/A')}<br>"
            f"<b>Total Rolls:</b> {summary.get('total_rolls', 0)}<br>"
            f"<b>Total Length:</b> {summary.get('total_length', 0):.2f} yards<br><br>"
            f"<b>BOM:</b> {bom_name}<br>"
            f"<b>Finished Item:</b> {finished_item}<br><br>"
            f"This will create a Repack Stock Entry in the ERP system.<br>"
            f"Source items will be taken from the BOM.<br>"
            f"<b>Do you want to continue?</b>"
        )
        
        reply = QMessageBox.question(
            self,
            "Confirm ERP Submission",
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            logger.info(f"User cancelled ERP submission for batch {batch}")
            return
        
        # Show progress dialog
        progress = QProgressDialog(
            "Submitting batch to ERP system...",
            "Cancel",
            0,
            0,
            self
        )
        progress.setWindowTitle("Submitting to ERP")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)  # No cancel button
        progress.show()
        
        try:
            # Test connection first
            logger.info("Testing ERP connection...")
            progress.setLabelText("Testing ERP connection...")
            connected, conn_msg = self.erp_client.test_connection()
            
            if not connected:
                progress.close()
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    f"Failed to connect to ERP system:\n\n{conn_msg}\n\n"
                    f"Please check:\n"
                    f"- Network connection\n"
                    f"- ERP server is running\n"
                    f"- API credentials are correct"
                )
                logger.error(f"ERP connection test failed: {conn_msg}")
                return
            
            logger.info(f"ERP connection successful: {conn_msg}")
            
            # Submit batch data
            progress.setLabelText("Creating Stock Entry...")
            logger.info(f"Submitting batch {batch} to ERP...")
            
            # Get stock entry type from config
            stock_entry_type = self.config.get('erp_stock_entry_type', 'Repack')

            success, message, response_data = self.erp_client.create_stock_entry(
                batch_data=summary,
                company=self.config.get('erp_company', 'Textilindo'),
                from_warehouse=self.config.get('erp_from_warehouse', 'Prancis - MGI'),
                to_warehouse=self.config.get('erp_to_warehouse', 'Prancis - MGI'),
                bom_name=bom_name,
                finished_item_code=finished_item,
                stock_entry_type=stock_entry_type
            )
            
            progress.close()
            
            if success:
                # Success message with details
                doc_name = "Unknown"
                if response_data:
                    doc_name = response_data.get('data', {}).get('name', 'Unknown')
                
                success_msg = (
                    f"<b>Batch submitted successfully!</b><br><br>"
                    f"<b>Batch:</b> {batch}<br>"
                    f"<b>Stock Entry:</b> {doc_name}<br>"
                    f"<b>Type:</b> {stock_entry_type}<br>"
                    f"<b>BOM:</b> {bom_name}<br>"
                    f"<b>Finished Item:</b> {finished_item}<br>"
                    f"<b>Rolls:</b> {summary.get('total_rolls', 0)}<br>"
                    f"<b>Total Length:</b> {summary.get('total_length', 0):.2f} yards<br><br>"
                    f"The Stock Entry has been created as <b>Draft</b> in the ERP system.<br>"
                    f"Source items from BOM have been added automatically.<br>"
                    f"Please review and submit it in ERPNext."
                )
                
                QMessageBox.information(
                    self,
                    "Submission Successful",
                    success_msg
                )
                
                logger.info(f"Batch {batch} submitted successfully: {doc_name}")
                
                # Mark batch as submitted
                self._mark_batch_as_submitted(batch)
                
                # Refresh batch list to remove submitted batch
                self.load_batches()
                
            else:
                # Error message
                error_msg = (
                    f"<b>Failed to submit batch to ERP</b><br><br>"
                    f"<b>Error:</b> {message}<br><br>"
                    f"Please check the error message and try again.<br>"
                    f"If the problem persists, contact your administrator."
                )
                
                QMessageBox.critical(
                    self,
                    "Submission Failed",
                    error_msg
                )
                
                logger.error(f"Failed to submit batch {batch}: {message}")
                
        except Exception as e:
            progress.close()
            error_msg = (
                f"<b>Unexpected error during submission</b><br><br>"
                f"<b>Error:</b> {str(e)}<br><br>"
                f"Please check the log files for more details."
            )
            
            QMessageBox.critical(
                self,
                "Submission Error",
                error_msg
            )
            
            logger.error(f"Unexpected error submitting batch {batch}: {e}", exc_info=True)
    
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

