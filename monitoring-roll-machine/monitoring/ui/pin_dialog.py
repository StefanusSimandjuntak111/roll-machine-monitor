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
import requests
import json
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)


class PinDialog(QDialog):
    """Dialog for PIN input with numeric keypad-like interface."""

    # Signal emitted when PIN is verified
    pin_verified = Signal()

    # Signal emitted when login is successful with user credentials
    login_successful = Signal(str, str, str)  # username, api_key, api_secret

    def __init__(self, correct_pin: str, parent=None):
        super().__init__(parent)
        self.correct_pin = correct_pin
        self.attempts = 0
        self.max_attempts = 3
        self.login_mode = False  # Track if we're in login mode
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
        self.title_label = QLabel("🔒 Settings Protected")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: black;
                margin-bottom: 10px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel("Enter PIN to access settings")
        self.desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: black;
                margin-bottom: 20px;
            }
        """)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

        # PIN input field (initially visible)
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

        # Username input field (initially hidden)
        self.username_input = QLineEdit()
        self.username_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_input.setMinimumHeight(25)
        self.username_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 12px;
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 8px;
                color: white;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.returnPressed.connect(self.verify_login)
        self.username_input.setVisible(False)
        layout.addWidget(self.username_input)

        # Password input field (initially hidden)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.setMinimumHeight(25)
        self.password_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 12px;
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 8px;
                color: white;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.returnPressed.connect(self.verify_login)
        self.password_input.setVisible(False)
        layout.addWidget(self.password_input)

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

        # Login button in the middle
        self.login_btn = QPushButton("🔓 Login")
        self.login_btn.setStyleSheet("""
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
        self.login_btn.clicked.connect(self.switch_to_login_mode)
        button_layout.addWidget(self.login_btn)

        # Store reference to verify button for mode switching
        self.verify_btn = QPushButton("✓ Verify")
        self.verify_btn.setStyleSheet("""
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
        self.verify_btn.clicked.connect(self.verify_pin)
        button_layout.addWidget(self.verify_btn)


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

    def switch_to_pin_mode(self):
        """Switch back to PIN mode from login mode."""
        self.login_mode = False

        # Update title and description
        self.title_label.setText("🔒 Settings Protected")
        self.desc_label.setText("Enter PIN to access settings")

        # Show PIN input, hide username and password inputs
        self.pin_input.setVisible(True)
        self.username_input.setVisible(False)
        self.password_input.setVisible(False)

        # Update button text and function
        self.login_btn.setText("🔓 Login")
        self.login_btn.clicked.disconnect(self.switch_to_pin_mode)
        self.login_btn.clicked.connect(self.switch_to_login_mode)

        # Update verify button text and function
        self.verify_btn.setText("✓ Verify")
        self.verify_btn.clicked.disconnect(self.verify_login)
        self.verify_btn.clicked.connect(self.verify_pin)

        # Clear inputs and status
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.setText("")

        # Set focus to PIN input
        self.pin_input.setFocus()

        # Update window title
        self.setWindowTitle("Enter PIN to Access Settings")

        logger.info("Switched back to PIN mode")

    def switch_to_login_mode(self):
        """Switch the dialog to login mode with username/password fields."""
        self.login_mode = True

        # Update title and description
        self.title_label.setText("🔐 Admin Login")
        self.desc_label.setText("Enter username and password to access settings")

        # Hide PIN input, show username and password inputs
        self.pin_input.setVisible(False)
        self.username_input.setVisible(True)
        self.password_input.setVisible(True)

        # Update button text and function
        self.login_btn.setText("PIN")
        self.login_btn.clicked.disconnect(self.switch_to_login_mode)
        self.login_btn.clicked.connect(self.switch_to_pin_mode)

        # Update verify button text and function
        self.verify_btn.setText("🚪Login")
        self.verify_btn.clicked.disconnect(self.verify_pin)
        self.verify_btn.clicked.connect(self.verify_login)

        # Clear any previous status
        self.status_label.setText("")

        # Set focus to username input
        self.username_input.setFocus()

        # Update window title
        self.setWindowTitle("Admin Login - Access Settings")

        logger.info("Switched to login mode")

    def verify_login(self):
        """Verify username and password for login using ERP API."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username:
            self.status_label.setText("⚠️ Please enter username")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff9800;
                    min-height: 20px;
                }
            """)
            self.username_input.setFocus()
            return

        if not password:
            self.status_label.setText("⚠️ Please enter password")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff9800;
                    min-height: 20px;
                }
            """)
            self.password_input.setFocus()
            return

        # Authenticate using ERP API
        try:
            # ERP login URL
            login_url = "http://192.168.2.73:8080/api/method/login"

            # Prepare login data
            login_data = {
                "usr": username,
                "pwd": password
            }

            logger.info(f"Attempting login for user: {username} to ERP API: {login_url}")

            # Make API request
            response = requests.post(
                login_url,
                json=login_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=15  # 15 second timeout
            )

            logger.info(f"ERP login response status: {response.status_code}")

            if response.status_code == 200:
                # Try to parse response
                try:
                    response_data = response.json()
                    logger.info(f"ERP login response: {response_data}")

                    # Check if login was successful
                    # ERPNext typically returns success message or user data
                    if response_data.get("message") == "Logged In" or response_data.get("full_name"):
                        logger.info(f"Login successful for user: {username}")

                        # Get API key and secret from the authenticated user
                        api_key, api_secret = self._get_user_api_credentials(username, password)

                        # Log the retrieved credentials with security considerations
                        logger.info(f"=== LOGIN SUCCESSFUL ===")
                        logger.info(f"User: {username}")
                        logger.info(f"Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        if api_key and api_secret:
                            logger.info(f"API Key: {api_key}")
                            logger.info(f"API Secret: {api_secret}")
                            logger.info(f"API Credentials Status: VALID")
                        else:
                            logger.warning(f"API Credentials Status: NOT FOUND")
                            logger.warning(f"User {username} does not have API credentials configured")
                        
                        logger.info(f"=== END LOGIN INFO ===")

                        self.status_label.setText("✓ Login successful!")
                        self.status_label.setStyleSheet("""
                            QLabel {
                                font-size: 12px;
                                color: #4CAF50;
                                min-height: 20px;
                            }
                        """)

                        # Emit login successful signal with credentials (even if empty)
                        self.login_successful.emit(username, api_key, api_secret)

                        # Accept dialog
                        self.accept()
                        return
                    else:
                        # Login failed - invalid credentials
                        logger.warning(f"Login failed for user: {username} - Invalid credentials")
                        self._handle_login_failure(username, "Invalid username or password")
                        return

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse ERP login response: {e}")
                    logger.error(f"Raw response: {response.text}")
                    self._handle_login_failure(username, "Invalid response from server")
                    return

            elif response.status_code == 401:
                # Unauthorized - invalid credentials
                logger.warning(f"Login failed for user: {username} - Unauthorized (401)")
                self._handle_login_failure(username, "Invalid username or password")
                return

            elif response.status_code == 403:
                # Forbidden - account disabled or no permissions
                logger.warning(f"Login failed for user: {username} - Forbidden (403)")
                self._handle_login_failure(username, "Account disabled or insufficient permissions")
                return

            elif response.status_code == 500:
                # Internal server error - could be syntax error or other server issues
                logger.error(f"Login failed for user: {username} - Internal Server Error (500)")
                logger.error(f"Server response: {response.text}")
                self._handle_login_failure(username, "Server configuration error. Please contact administrator.")
                return

            else:
                # Other error status codes
                logger.error(f"Login failed for user: {username} - HTTP {response.status_code}: {response.text}")
                self._handle_login_failure(username, f"Server error ({response.status_code})")
                return

        except requests.exceptions.Timeout:
            logger.error(f"Login timeout for user: {username}")
            self.status_label.setText("❌ Connection timeout")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff4444;
                    min-height: 20px;
                }
            """)
            self.password_input.clear()
            self.password_input.setFocus()

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error during login for user: {username}")
            self.status_label.setText("❌ Cannot connect to server")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff4444;
                    min-height: 20px;
                }
            """)
            self.password_input.clear()
            self.password_input.setFocus()

        except Exception as e:
            logger.error(f"Unexpected error during login for user: {username}: {e}")
            self.status_label.setText("❌ Login error")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff4444;
                    min-height: 20px;
                }
            """)
            self.password_input.clear()
            self.password_input.setFocus()

    def _handle_login_failure(self, username: str, reason: str):
        """Handle login failure with attempt counting."""
        self.attempts += 1
        remaining = self.max_attempts - self.attempts

        if remaining > 0:
            self.status_label.setText(f"❌ {reason}. {remaining} attempt(s) remaining")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff4444;
                    min-height: 20px;
                }
            """)
            self.password_input.clear()
            self.password_input.setFocus()
            logger.warning(f"Failed login attempt for user: {username}. {remaining} attempts remaining")
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
            logger.error("Maximum login attempts exceeded")
            # Reject dialog
            QMessageBox.critical(
                self,
                "Access Denied",
                "Maximum login attempts exceeded.\n\nAccess to settings has been denied."
            )
            self.reject()

    def _get_user_api_credentials(self, username: str, password: str) -> tuple[str, str]:
        """Get API key and secret for the authenticated user."""
        try:
            logger.info(f"Attempting to retrieve API credentials for user: {username}")

            # First, we need to authenticate and get a session cookie
            # Then use that session to access the User doctype
            session = requests.Session()
            
            # Step 1: Login to get session cookie
            login_url = "http://192.168.2.73:8080/api/method/login"
            login_data = {
                "usr": username,
                "pwd": password
            }
            
            login_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"Authenticating user {username} to get session...")
            login_response = session.post(login_url, json=login_data, headers=login_headers, timeout=15)
            
            if login_response.status_code != 200:
                logger.error(f"Authentication failed: {login_response.status_code}")
                logger.error(f"Login response: {login_response.text}")
                return "", ""
            
            logger.info("Authentication successful, proceeding to get API credentials...")
            
            # Step 2: Use authenticated session to get API credentials
            api_credentials_url = "http://192.168.2.73:8080/api/resource/User"

            # Query for the specific user to get API key and secret
            params = {
                "filters": json.dumps([["name", "=", username]]),
                "fields": json.dumps(["api_key", "api_secret"])
            }

            # Build URL with encoded parameters
            url = f"{api_credentials_url}?{urllib.parse.urlencode(params)}"
            logger.info(f"API credentials URL: {url}")

            # Make API request with authenticated session
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            logger.info("Making API request to get user credentials...")
            response = session.get(url, headers=headers, timeout=10)
            logger.info(f"API credentials response status: {response.status_code}")
            logger.info(f"API credentials response headers: {dict(response.headers)}")
            logger.info(f"API credentials response text: {response.text}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"API credentials response data: {data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw response text: {response.text}")
                    return "", ""

                users = data.get("data", [])
                logger.info(f"Number of users found: {len(users)}")

                if users and len(users) > 0:
                    user_data = users[0]
                    api_key = user_data.get("api_key", "")
                    api_secret = user_data.get("api_secret", "")

                    logger.info(f"Raw API key from response: '{api_key}'")
                    logger.info(f"Raw API secret from response: '{api_secret}'")

                    if api_key and api_secret:
                        logger.info(f"=== API CREDENTIALS RETRIEVED ===")
                        logger.info(f"User: {username}")
                        logger.info(f"API Key: {api_key}")
                        logger.info(f"API Secret: {api_secret}")
                        logger.info(f"API Key Length: {len(api_key)}")
                        logger.info(f"API Secret Length: {len(api_secret)}")
                        logger.info(f"=== END API CREDENTIALS ===")
                        return api_key, api_secret
                    else:
                        logger.warning(f"=== API CREDENTIALS NOT FOUND ===")
                        logger.warning(f"User: {username}")
                        logger.warning(f"API Key field: '{api_key}' (length: {len(api_key) if api_key else 0})")
                        logger.warning(f"API Secret field: '{api_secret}' (length: {len(api_secret) if api_secret else 0})")
                        logger.warning(f"Status: User does not have API credentials configured")
                        logger.warning(f"=== END API CREDENTIALS WARNING ===")
                        return "", ""
                else:
                    logger.warning(f"=== USER NOT FOUND ===")
                    logger.warning(f"User {username} not found in User doctype")
                    logger.warning(f"Response data: {data}")
                    logger.warning(f"Number of users returned: {len(users)}")
                    logger.warning(f"=== END USER NOT FOUND ===")
                    return "", ""
            else:
                logger.error(f"=== API CREDENTIALS REQUEST FAILED ===")
                logger.error(f"HTTP Status: {response.status_code}")
                logger.error(f"Response Headers: {dict(response.headers)}")
                logger.error(f"Response Content: {response.text}")
                logger.error(f"Request URL: {url}")
                logger.error(f"=== END API CREDENTIALS REQUEST FAILED ===")
                return "", ""

        except Exception as e:
            logger.error(f"Error getting user API credentials: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "", ""
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if self.login_mode:
            # In login mode, allow all characters
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                event.accept()
                self.verify_login()
            elif event.key() == Qt.Key.Key_Escape:
                event.accept()
                self.reject()
            else:
                event.accept()
                super().keyPressEvent(event)
        else:
            # In PIN mode, only allow numbers and backspace
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





