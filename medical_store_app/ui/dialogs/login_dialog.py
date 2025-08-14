"""
Login dialog for Medical Store Management Application
Provides user authentication interface with username and password fields
"""

import logging
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from .base_dialog import BaseDialog
from ..components.base_components import StyledButton, FormContainer
from ...managers.auth_manager import AuthManager
from ...models.user import User


class LoginDialog(BaseDialog):
    """Login dialog with username and password authentication"""
    
    # Signals
    login_successful = Signal(User)  # Emitted when login is successful
    login_failed = Signal(str)       # Emitted when login fails
    
    def __init__(self, auth_manager: AuthManager, parent=None):
        """
        Initialize login dialog
        
        Args:
            auth_manager: Authentication manager instance
            parent: Parent widget
        """
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        
        # UI components
        self.username_input = None
        self.password_input = None
        self.remember_checkbox = None
        self.login_button = None
        self.cancel_button = None
        self.error_label = None
        
        # State
        self.login_attempts = 0
        self.max_attempts = 5
        self.is_logging_in = False
        
        super().__init__("Login - Medical Store Management", parent, modal=True)
        
        # Set dialog properties
        self.setFixedSize(450, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        
        # Set up the login form
        self._setup_login_form()
        
        # Connect signals
        self._connect_signals()
        
        self.logger.info("Login dialog initialized")
    
    def _setup_login_form(self):
        """Set up the login form UI"""
        # Create main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 30, 40, 20)
        content_layout.setSpacing(20)
        
        # Header section
        self._create_header_section(content_layout)
        
        # Form section
        self._create_form_section(content_layout)
        
        # Error message section
        self._create_error_section(content_layout)
        
        # Button section
        self._create_button_section(content_layout)
        
        # Add stretch to center content
        content_layout.addStretch()
        
        # Set content widget
        self.set_content_widget(content_widget)
    
    def _create_header_section(self, layout: QVBoxLayout):
        """Create the header section with title and icon"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        
        # Application icon/logo (using text for now)
        icon_label = QLabel("🏥")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Medical Store Management")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2D9CDB; margin-bottom: 5px;")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please sign in to continue")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666666; font-size: 12px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
    
    def _create_form_section(self, layout: QVBoxLayout):
        """Create the form section with input fields"""
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Username field
        username_layout = QVBoxLayout()
        username_layout.setSpacing(5)
        
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: bold; color: #333333;")
        username_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E1E5E9;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2D9CDB;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #B8C5D1;
            }
        """)
        username_layout.addWidget(self.username_input)
        
        form_layout.addLayout(username_layout)
        
        # Password field
        password_layout = QVBoxLayout()
        password_layout.setSpacing(5)
        
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: bold; color: #333333;")
        password_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E1E5E9;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2D9CDB;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #B8C5D1;
            }
        """)
        password_layout.addWidget(self.password_input)
        
        form_layout.addLayout(password_layout)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #666666;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #E1E5E9;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2D9CDB;
                border-radius: 3px;
                background-color: #2D9CDB;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)
        form_layout.addWidget(self.remember_checkbox)
        
        layout.addLayout(form_layout)
    
    def _create_error_section(self, layout: QVBoxLayout):
        """Create the error message section"""
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #E74C3C;
                background-color: #FADBD8;
                border: 1px solid #F1948A;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        self.error_label.setVisible(False)  # Initially hidden
        
        layout.addWidget(self.error_label)
    
    def _create_button_section(self, layout: QVBoxLayout):
        """Create the button section"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel button
        self.cancel_button = StyledButton("Cancel", "outline")
        self.cancel_button.setFixedHeight(40)
        button_layout.addWidget(self.cancel_button)
        
        # Login button
        self.login_button = StyledButton("Sign In", "primary")
        self.login_button.setFixedHeight(40)
        self.login_button.setDefault(True)  # Make it the default button
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # Button signals
        self.login_button.clicked.connect(self._on_login_clicked)
        self.cancel_button.clicked.connect(self.reject)
        
        # Input field signals
        self.username_input.textChanged.connect(self._on_input_changed)
        self.password_input.textChanged.connect(self._on_input_changed)
        self.password_input.returnPressed.connect(self._on_login_clicked)
        
        # Initially disable login button
        self._update_login_button_state()
    
    def _on_input_changed(self):
        """Handle input field changes"""
        self._update_login_button_state()
        self._hide_error_message()
    
    def _update_login_button_state(self):
        """Update login button enabled state based on input validation"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Enable login button only if both fields have content
        has_input = bool(username and password)
        self.login_button.setEnabled(has_input and not self.is_logging_in)
    
    def _on_login_clicked(self):
        """Handle login button click"""
        if self.is_logging_in:
            return
        
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username:
            self._show_error_message("Please enter your username")
            self.username_input.setFocus()
            return
        
        if not password:
            self._show_error_message("Please enter your password")
            self.password_input.setFocus()
            return
        
        # Perform login
        self._perform_login(username, password)
    
    def _perform_login(self, username: str, password: str):
        """
        Perform the login operation
        
        Args:
            username: Username to authenticate
            password: Password to authenticate
        """
        try:
            self.is_logging_in = True
            self._update_ui_for_login_state(True)
            
            # Attempt authentication
            success, message, user = self.auth_manager.login(username, password)
            
            if success and user:
                self.logger.info(f"Login successful for user: {username}")
                
                # Hide error message
                self._hide_error_message()
                
                # Emit success signal
                self.login_successful.emit(user)
                
                # Accept dialog
                self.accept()
            else:
                self.login_attempts += 1
                self.logger.warning(f"Login failed for user: {username}. Attempt {self.login_attempts}")
                
                # Show error message
                self._show_error_message(message or "Invalid username or password")
                
                # Emit failure signal
                self.login_failed.emit(message or "Login failed")
                
                # Check if max attempts reached
                if self.login_attempts >= self.max_attempts:
                    self._handle_max_attempts_reached()
                else:
                    # Clear password field and focus username
                    self.password_input.clear()
                    self.username_input.setFocus()
                    self.username_input.selectAll()
        
        except Exception as e:
            error_msg = f"Login error: {str(e)}"
            self.logger.error(error_msg)
            self._show_error_message("An error occurred during login. Please try again.")
            self.login_failed.emit(error_msg)
        
        finally:
            self.is_logging_in = False
            self._update_ui_for_login_state(False)
    
    def _update_ui_for_login_state(self, is_logging_in: bool):
        """
        Update UI elements based on login state
        
        Args:
            is_logging_in: Whether login is in progress
        """
        # Update button text and state
        if is_logging_in:
            self.login_button.setText("Signing In...")
            self.login_button.setEnabled(False)
        else:
            self.login_button.setText("Sign In")
            self._update_login_button_state()
        
        # Enable/disable input fields
        self.username_input.setEnabled(not is_logging_in)
        self.password_input.setEnabled(not is_logging_in)
        self.remember_checkbox.setEnabled(not is_logging_in)
        self.cancel_button.setEnabled(not is_logging_in)
    
    def _show_error_message(self, message: str):
        """
        Show error message to user
        
        Args:
            message: Error message to display
        """
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.error_label.show()  # Force show
        
        # Auto-hide error message after 5 seconds
        QTimer.singleShot(5000, self._hide_error_message)
    
    def _hide_error_message(self):
        """Hide error message"""
        self.error_label.setVisible(False)
        self.error_label.hide()  # Force hide
    
    def _handle_max_attempts_reached(self):
        """Handle when maximum login attempts are reached"""
        self.logger.warning(f"Maximum login attempts ({self.max_attempts}) reached")
        
        # Show critical error message
        QMessageBox.critical(
            self,
            "Login Blocked",
            f"Too many failed login attempts. The application will close.\n\n"
            f"Please contact your administrator if you need assistance."
        )
        
        # Close the dialog and application
        self.reject()
    
    def reset_form(self):
        """Reset the login form to initial state"""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self._hide_error_message()
        self.login_attempts = 0
        self.is_logging_in = False
        self._update_login_button_state()
        
        # Focus on username field
        self.username_input.setFocus()
    
    def set_username(self, username: str):
        """
        Set the username field
        
        Args:
            username: Username to set
        """
        self.username_input.setText(username)
        self.password_input.setFocus()
    
    def get_remember_me(self) -> bool:
        """
        Get the remember me checkbox state
        
        Returns:
            True if remember me is checked, False otherwise
        """
        return self.remember_checkbox.isChecked()
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        
        # Reset form when dialog is shown
        self.reset_form()
        
        # Focus on username field
        self.username_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Handle Escape key
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class LoginManager:
    """Manager class for handling login dialog and authentication flow"""
    
    def __init__(self, auth_manager: AuthManager, parent=None):
        """
        Initialize login manager
        
        Args:
            auth_manager: Authentication manager instance
            parent: Parent widget for dialogs
        """
        self.auth_manager = auth_manager
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        self.login_dialog = None
    
    def show_login_dialog(self) -> Tuple[bool, Optional[User]]:
        """
        Show login dialog and handle authentication
        
        Returns:
            Tuple of (success, user_instance)
        """
        try:
            # Create login dialog
            self.login_dialog = LoginDialog(self.auth_manager, self.parent)
            
            # Show dialog and get result
            result = self.login_dialog.exec()
            
            if result == 1:  # QDialog.Accepted
                # Get current user from auth manager
                current_user = self.auth_manager.get_current_user()
                if current_user:
                    self.logger.info(f"Login dialog completed successfully for user: {current_user.username}")
                    return True, current_user
                else:
                    self.logger.error("Login dialog accepted but no current user found")
                    return False, None
            else:
                self.logger.info("Login dialog was cancelled or rejected")
                return False, None
        
        except Exception as e:
            error_msg = f"Error showing login dialog: {str(e)}"
            self.logger.error(error_msg)
            return False, None
        
        finally:
            # Clean up dialog
            if self.login_dialog:
                self.login_dialog.deleteLater()
                self.login_dialog = None
    
    def is_user_logged_in(self) -> bool:
        """
        Check if user is currently logged in
        
        Returns:
            True if user is logged in, False otherwise
        """
        return self.auth_manager.is_logged_in()
    
    def get_current_user(self) -> Optional[User]:
        """
        Get current logged-in user
        
        Returns:
            Current user instance if logged in, None otherwise
        """
        return self.auth_manager.get_current_user()
    
    def logout(self) -> bool:
        """
        Logout current user
        
        Returns:
            True if logout successful, False otherwise
        """
        success, message = self.auth_manager.logout()
        if success:
            self.logger.info("User logged out successfully")
        else:
            self.logger.error(f"Logout failed: {message}")
        
        return success