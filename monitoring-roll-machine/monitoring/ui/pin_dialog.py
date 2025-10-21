"""
PIN input dialog for settings protection.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class PinDialog(QDialog):
    """Dialog for PIN input with numeric keypad-like interface."""
    
    # Signal emitted when PIN is verified
    pin_verified = Signal()
    
    def __init__(self, correct_pin: str, parent=None):
        super().__init__(parent)
        self.correct_pin = correct_pin
        self.attempts = 0
        self.max_attempts = 3
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the PIN dialog UI."""
        self.setWindowTitle("Enter PIN to Access Settings")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        # Set window flags for proper dialog behavior
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint
        )
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🔒 Settings Protected")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Enter PIN to access settings")
        desc.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                margin-bottom: 20px;
            }
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # PIN input field
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setMaxLength(6)  # Support up to 6 digits
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
                padding: 15px;
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 10px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.pin_input.setPlaceholderText("••••••")
        self.pin_input.returnPressed.connect(self.verify_pin)
        layout.addWidget(self.pin_input)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #ff9800;
                min-height: 20px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        verify_btn = QPushButton("✓ Verify")
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        verify_btn.clicked.connect(self.verify_pin)
        button_layout.addWidget(verify_btn)
        
        layout.addLayout(button_layout)
        
        # Set focus to PIN input
        self.pin_input.setFocus()
        
    def verify_pin(self):
        """Verify the entered PIN."""
        entered_pin = self.pin_input.text().strip()
        
        if not entered_pin:
            self.status_label.setText("⚠️ Please enter a PIN")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff9800;
                    min-height: 20px;
                }
            """)
            return
        
        # Check PIN length
        if len(entered_pin) < 4:
            self.status_label.setText("⚠️ PIN must be at least 4 digits")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff9800;
                    min-height: 20px;
                }
            """)
            self.pin_input.clear()
            return
        
        # Verify PIN
        if entered_pin == self.correct_pin:
            logger.info("PIN verified successfully")
            self.status_label.setText("✓ PIN verified successfully!")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #4CAF50;
                    min-height: 20px;
                }
            """)
            # Accept dialog
            self.accept()
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            
            if remaining > 0:
                self.status_label.setText(f"❌ Incorrect PIN. {remaining} attempt(s) remaining")
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        color: #ff4444;
                        min-height: 20px;
                    }
                """)
                self.pin_input.clear()
                self.pin_input.setFocus()
                logger.warning(f"Failed PIN attempt. {remaining} attempts remaining")
            else:
                self.status_label.setText("❌ Maximum attempts exceeded. Access denied.")
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        color: #ff0000;
                        min-height: 20px;
                        font-weight: bold;
                    }
                """)
                logger.error("Maximum PIN attempts exceeded")
                # Reject dialog
                QMessageBox.critical(
                    self,
                    "Access Denied",
                    "Maximum PIN attempts exceeded.\n\nAccess to settings has been denied."
                )
                self.reject()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Allow numbers and backspace
        if event.key() in range(Qt.Key.Key_0, Qt.Key.Key_9 + 1):
            event.accept()
            super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Backspace:
            event.accept()
            super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            event.accept()
            self.verify_pin()
        elif event.key() == Qt.Key.Key_Escape:
            event.accept()
            self.reject()
        else:
            event.ignore()


class ChangePinDialog(QDialog):
    """Dialog for changing the PIN."""
    
    # Signal emitted when PIN is changed successfully
    pin_changed = Signal(str)
    
    def __init__(self, current_pin: str, parent=None):
        super().__init__(parent)
        self.current_pin = current_pin
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the change PIN dialog UI."""
        self.setWindowTitle("Change PIN")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        self.setModal(True)
        
        # Set window flags for proper dialog behavior
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint
        )
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🔑 Change Settings PIN")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: white;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Enter current PIN and choose a new PIN")
        desc.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                margin-bottom: 20px;
            }
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Current PIN
        current_pin_label = QLabel("Current PIN:")
        current_pin_label.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        layout.addWidget(current_pin_label)
        
        self.current_pin_input = QLineEdit()
        self.current_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pin_input.setMaxLength(6)
        self.current_pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_pin_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 6px;
                padding: 12px;
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.current_pin_input.setPlaceholderText("••••••")
        layout.addWidget(self.current_pin_input)
        
        # New PIN
        new_pin_label = QLabel("New PIN (4-6 digits):")
        new_pin_label.setStyleSheet("color: #e0e0e0; font-size: 14px; margin-top: 10px;")
        layout.addWidget(new_pin_label)
        
        self.new_pin_input = QLineEdit()
        self.new_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pin_input.setMaxLength(6)
        self.new_pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.new_pin_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 6px;
                padding: 12px;
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.new_pin_input.setPlaceholderText("••••••")
        layout.addWidget(self.new_pin_input)
        
        # Confirm New PIN
        confirm_pin_label = QLabel("Confirm New PIN:")
        confirm_pin_label.setStyleSheet("color: #e0e0e0; font-size: 14px; margin-top: 10px;")
        layout.addWidget(confirm_pin_label)
        
        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pin_input.setMaxLength(6)
        self.confirm_pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.confirm_pin_input.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 6px;
                padding: 12px;
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.confirm_pin_input.setPlaceholderText("••••••")
        self.confirm_pin_input.returnPressed.connect(self.change_pin)
        layout.addWidget(self.confirm_pin_input)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #ff9800;
                min-height: 20px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        change_btn = QPushButton("✓ Change PIN")
        change_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        change_btn.clicked.connect(self.change_pin)
        button_layout.addWidget(change_btn)
        
        layout.addLayout(button_layout)
        
        # Set focus to current PIN input
        self.current_pin_input.setFocus()
        
    def change_pin(self):
        """Change the PIN after validation."""
        current = self.current_pin_input.text().strip()
        new = self.new_pin_input.text().strip()
        confirm = self.confirm_pin_input.text().strip()
        
        # Validate current PIN
        if current != self.current_pin:
            self.status_label.setText("❌ Current PIN is incorrect")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff4444;
                    min-height: 20px;
                }
            """)
            self.current_pin_input.clear()
            self.current_pin_input.setFocus()
            return
        
        # Validate new PIN length
        if len(new) < 4:
            self.status_label.setText("⚠️ New PIN must be at least 4 digits")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff9800;
                    min-height: 20px;
                }
            """)
            self.new_pin_input.clear()
            self.confirm_pin_input.clear()
            self.new_pin_input.setFocus()
            return
        
        # Validate confirmation
        if new != confirm:
            self.status_label.setText("❌ New PIN and confirmation do not match")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff4444;
                    min-height: 20px;
                }
            """)
            self.confirm_pin_input.clear()
            self.confirm_pin_input.setFocus()
            return
        
        # Check if new PIN is different from current
        if new == current:
            self.status_label.setText("⚠️ New PIN must be different from current PIN")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff9800;
                    min-height: 20px;
                }
            """)
            self.new_pin_input.clear()
            self.confirm_pin_input.clear()
            self.new_pin_input.setFocus()
            return
        
        # Success
        logger.info("PIN changed successfully")
        self.status_label.setText("✓ PIN changed successfully!")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #4CAF50;
                min-height: 20px;
            }
        """)
        
        # Emit signal with new PIN
        self.pin_changed.emit(new)
        
        # Accept dialog
        self.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Allow numbers and backspace
        if event.key() in range(Qt.Key.Key_0, Qt.Key.Key_9 + 1):
            event.accept()
            super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Backspace:
            event.accept()
            super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            event.accept()
            self.change_pin()
        elif event.key() == Qt.Key.Key_Escape:
            event.accept()
            self.reject()
        else:
            event.ignore()





