"""
User Management Dialog for Medical Store Management Application
Provides interface for admin users to manage user accounts, roles, and permissions
"""

import logging
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QFrame, QSplitter,
    QGroupBox, QFormLayout, QTextEdit, QDateTimeEdit, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QDateTime
from PySide6.QtGui import QFont, QIcon

from .base_dialog import BaseDialog, ConfirmationDialog, MessageDialog
from ..components.base_components import StyledButton, FormContainer
from ...managers.auth_manager import AuthManager
from ...models.user import User


class UserFormWidget(QWidget):
    """Widget for user form (add/edit user)"""
    
    # Signals
    form_data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Form fields
        self.username_input = None
        self.password_input = None
        self.confirm_password_input = None
        self.role_combo = None
        self.is_active_checkbox = None
        self.full_name_input = None
        self.email_input = None
        self.phone_input = None
        
        # Current user being edited (None for new user)
        self.current_user: Optional[User] = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the form UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Basic Information Group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username (3-50 characters)")
        self.username_input.setMaxLength(50)
        basic_layout.addRow("Username *:", self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password (min 6 characters)")
        self.password_input.setMaxLength(128)
        basic_layout.addRow("Password *:", self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setMaxLength(128)
        basic_layout.addRow("Confirm Password *:", self.confirm_password_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["cashier", "admin"])
        self.role_combo.setCurrentText("cashier")
        basic_layout.addRow("Role *:", self.role_combo)
        
        # Active status
        self.is_active_checkbox = QCheckBox("User account is active")
        self.is_active_checkbox.setChecked(True)
        basic_layout.addRow("Status:", self.is_active_checkbox)
        
        layout.addWidget(basic_group)
        
        # Additional Information Group
        additional_group = QGroupBox("Additional Information (Optional)")
        additional_layout = QFormLayout(additional_group)
        additional_layout.setSpacing(10)
        
        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter full name")
        self.full_name_input.setMaxLength(100)
        additional_layout.addRow("Full Name:", self.full_name_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        self.email_input.setMaxLength(100)
        additional_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.phone_input.setMaxLength(20)
        additional_layout.addRow("Phone:", self.phone_input)
        
        layout.addWidget(additional_group)
        
        # Password requirements note
        requirements_label = QLabel(
            "Password Requirements:\n"
            "• At least 6 characters long\n"
            "• Must contain at least one letter\n"
            "• Must contain at least one number"
        )
        requirements_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                background-color: #F8F9FA;
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(requirements_label)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect form field signals"""
        self.username_input.textChanged.connect(self.form_data_changed.emit)
        self.password_input.textChanged.connect(self.form_data_changed.emit)
        self.confirm_password_input.textChanged.connect(self.form_data_changed.emit)
        self.role_combo.currentTextChanged.connect(self.form_data_changed.emit)
        self.is_active_checkbox.toggled.connect(self.form_data_changed.emit)
        self.full_name_input.textChanged.connect(self.form_data_changed.emit)
        self.email_input.textChanged.connect(self.form_data_changed.emit)
        self.phone_input.textChanged.connect(self.form_data_changed.emit)
    
    def set_user_data(self, user: User):
        """Set form data from user object"""
        self.current_user = user
        
        self.username_input.setText(user.username)
        self.role_combo.setCurrentText(user.role)
        self.is_active_checkbox.setChecked(user.is_active)
        self.full_name_input.setText(user.full_name or "")
        self.email_input.setText(user.email or "")
        self.phone_input.setText(user.phone or "")
        
        # For editing, password is optional
        self.password_input.setPlaceholderText("Leave blank to keep current password")
        self.confirm_password_input.setPlaceholderText("Leave blank to keep current password")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get form data as dictionary"""
        data = {
            'username': self.username_input.text().strip(),
            'role': self.role_combo.currentText(),
            'is_active': self.is_active_checkbox.isChecked(),
            'full_name': self.full_name_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'phone': self.phone_input.text().strip() or None
        }
        
        # Only include password if provided
        password = self.password_input.text()
        if password:
            data['password'] = password
        
        return data
    
    def validate_form(self) -> tuple[bool, List[str]]:
        """Validate form data"""
        errors = []
        
        # Username validation
        username = self.username_input.text().strip()
        if not username:
            errors.append("Username is required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        elif len(username) > 50:
            errors.append("Username must be less than 50 characters")
        
        # Password validation (required for new users, optional for editing)
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not self.current_user:  # New user
            if not password:
                errors.append("Password is required for new users")
            elif not User.validate_password_strength(password):
                errors.append("Password must be at least 6 characters with letters and numbers")
        else:  # Editing user
            if password and not User.validate_password_strength(password):
                errors.append("Password must be at least 6 characters with letters and numbers")
        
        # Password confirmation
        if password and password != confirm_password:
            errors.append("Passwords do not match")
        
        # Email validation (if provided)
        email = self.email_input.text().strip()
        if email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Invalid email format")
        
        return len(errors) == 0, errors
    
    def clear_form(self):
        """Clear all form fields"""
        self.current_user = None
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.role_combo.setCurrentText("cashier")
        self.is_active_checkbox.setChecked(True)
        self.full_name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        
        # Reset password placeholders
        self.password_input.setPlaceholderText("Enter password (min 6 characters)")
        self.confirm_password_input.setPlaceholderText("Confirm password")


class UserTableWidget(QTableWidget):
    """Custom table widget for displaying users"""
    
    # Signals
    user_selected = Signal(User)
    user_double_clicked = Signal(User)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Store users data
        self.users_data: List[User] = []
        
        self._setup_table()
    
    def _setup_table(self):
        """Set up table structure and styling"""
        # Set column headers
        headers = ["ID", "Username", "Full Name", "Role", "Status", "Email", "Last Login", "Created"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Configure table properties
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Username
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Full Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Role
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Email
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Last Login
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Created
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Apply styling
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #E1E5E9;
                background-color: white;
                alternate-background-color: #F8F9FA;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F1F3F4;
                padding: 8px;
                border: 1px solid #E1E5E9;
                font-weight: bold;
            }
        """)
    
    def load_users(self, users: List[User]):
        """Load users data into table"""
        self.users_data = users
        self.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # ID
            self.setItem(row, 0, QTableWidgetItem(str(user.id or "")))
            
            # Username
            self.setItem(row, 1, QTableWidgetItem(user.username))
            
            # Full Name
            self.setItem(row, 2, QTableWidgetItem(user.full_name or ""))
            
            # Role
            role_item = QTableWidgetItem(user.get_role_display())
            if user.is_admin():
                role_item.setBackground(Qt.yellow)
            self.setItem(row, 3, role_item)
            
            # Status
            status_item = QTableWidgetItem("Active" if user.is_active else "Inactive")
            if user.is_active:
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.red)
            self.setItem(row, 4, status_item)
            
            # Email
            self.setItem(row, 5, QTableWidgetItem(user.email or ""))
            
            # Last Login
            last_login = "Never"
            if user.last_login:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(user.last_login.replace('Z', '+00:00'))
                    last_login = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    last_login = user.last_login
            self.setItem(row, 6, QTableWidgetItem(last_login))
            
            # Created
            created = ""
            if user.created_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(user.created_at.replace('Z', '+00:00'))
                    created = dt.strftime("%Y-%m-%d")
                except:
                    created = user.created_at
            self.setItem(row, 7, QTableWidgetItem(created))
        
        # Sort by username by default
        self.sortItems(1, Qt.AscendingOrder)
    
    def get_selected_user(self) -> Optional[User]:
        """Get currently selected user"""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.users_data):
            return self.users_data[current_row]
        return None
    
    def _on_selection_changed(self):
        """Handle selection change"""
        user = self.get_selected_user()
        if user:
            self.user_selected.emit(user)
    
    def _on_item_double_clicked(self, item):
        """Handle item double click"""
        user = self.get_selected_user()
        if user:
            self.user_double_clicked.emit(user)


class UserManagementDialog(BaseDialog):
    """Main user management dialog"""
    
    # Signals
    users_updated = Signal()
    
    def __init__(self, auth_manager: AuthManager, parent=None):
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        
        # UI components
        self.user_table = None
        self.user_form = None
        self.add_button = None
        self.edit_button = None
        self.delete_button = None
        self.activate_button = None
        self.deactivate_button = None
        self.refresh_button = None
        self.close_button = None
        
        # Current selected user
        self.selected_user: Optional[User] = None
        
        super().__init__("User Management", parent, modal=True)
        
        # Set dialog size
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        
        # Load initial data
        self._refresh_users()
        
        self.logger.info("User management dialog initialized")
    
    def _setup_ui(self):
        """Override base setup to create custom UI"""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create content area
        self._create_content_area()
        
        # Create button area
        self._create_button_area()
    
    def _create_content_area(self):
        """Create the main content area"""
        content_widget = QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 10)
        
        # Title
        title_label = QLabel("User Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2D9CDB; margin-bottom: 10px;")
        content_layout.addWidget(title_label)
        
        # Create splitter for table and form
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - User table and controls
        left_widget = self._create_table_section()
        splitter.addWidget(left_widget)
        
        # Right side - User form
        right_widget = self._create_form_section()
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        
        content_layout.addWidget(splitter)
        
        self.main_layout.addWidget(content_widget)
    
    def _create_table_section(self) -> QWidget:
        """Create the user table section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 10, 0)
        
        # Table controls
        controls_layout = QHBoxLayout()
        
        self.refresh_button = StyledButton("🔄 Refresh", "outline")
        self.refresh_button.clicked.connect(self._refresh_users)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        
        # Action buttons
        self.add_button = StyledButton("➕ Add User", "primary")
        self.add_button.clicked.connect(self._add_user)
        controls_layout.addWidget(self.add_button)
        
        self.edit_button = StyledButton("✏️ Edit", "outline")
        self.edit_button.clicked.connect(self._edit_user)
        self.edit_button.setEnabled(False)
        controls_layout.addWidget(self.edit_button)
        
        self.delete_button = StyledButton("🗑️ Delete", "danger")
        self.delete_button.clicked.connect(self._delete_user)
        self.delete_button.setEnabled(False)
        controls_layout.addWidget(self.delete_button)
        
        layout.addLayout(controls_layout)
        
        # User table
        self.user_table = UserTableWidget()
        self.user_table.user_selected.connect(self._on_user_selected)
        self.user_table.user_double_clicked.connect(self._edit_user)
        layout.addWidget(self.user_table)
        
        # Status controls
        status_layout = QHBoxLayout()
        
        self.activate_button = StyledButton("✅ Activate", "success")
        self.activate_button.clicked.connect(self._activate_user)
        self.activate_button.setEnabled(False)
        status_layout.addWidget(self.activate_button)
        
        self.deactivate_button = StyledButton("❌ Deactivate", "warning")
        self.deactivate_button.clicked.connect(self._deactivate_user)
        self.deactivate_button.setEnabled(False)
        status_layout.addWidget(self.deactivate_button)
        
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        return widget
    
    def _create_form_section(self) -> QWidget:
        """Create the user form section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 0, 0, 0)
        
        # Form title
        form_title = QLabel("User Details")
        form_font = QFont()
        form_font.setPointSize(14)
        form_font.setBold(True)
        form_title.setFont(form_font)
        form_title.setStyleSheet("color: #333333; margin-bottom: 10px;")
        layout.addWidget(form_title)
        
        # User form
        self.user_form = UserFormWidget()
        self.user_form.form_data_changed.connect(self._on_form_data_changed)
        layout.addWidget(self.user_form)
        
        # Form buttons
        form_buttons_layout = QHBoxLayout()
        
        self.save_button = StyledButton("💾 Save", "primary")
        self.save_button.clicked.connect(self._save_user)
        self.save_button.setEnabled(False)
        form_buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = StyledButton("❌ Cancel", "outline")
        self.cancel_button.clicked.connect(self._cancel_form)
        self.cancel_button.setEnabled(False)
        form_buttons_layout.addWidget(self.cancel_button)
        
        form_buttons_layout.addStretch()
        
        layout.addLayout(form_buttons_layout)
        
        return widget
    
    def _create_button_area(self):
        """Create the dialog button area"""
        button_area = QFrame()
        button_area.setObjectName("buttonArea")
        button_area.setFixedHeight(60)
        
        button_layout = QHBoxLayout(button_area)
        button_layout.setContentsMargins(20, 10, 20, 10)
        button_layout.addStretch()
        
        # Close button
        self.close_button = StyledButton("Close", "outline")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        self.main_layout.addWidget(button_area)
    
    def _refresh_users(self):
        """Refresh users list"""
        try:
            users = self.auth_manager.get_all_users()
            self.user_table.load_users(users)
            self.logger.info(f"Loaded {len(users)} users")
        except Exception as e:
            self.logger.error(f"Failed to refresh users: {e}")
            MessageDialog.show_error(self, "Error", f"Failed to load users: {str(e)}")
    
    def _on_user_selected(self, user: User):
        """Handle user selection"""
        self.selected_user = user
        
        # Enable/disable buttons based on selection
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Enable activate/deactivate based on user status
        self.activate_button.setEnabled(not user.is_active)
        self.deactivate_button.setEnabled(user.is_active)
        
        # Load user data into form for viewing
        self.user_form.set_user_data(user)
        self._disable_form()
    
    def _add_user(self):
        """Add new user"""
        self.selected_user = None
        self.user_form.clear_form()
        self._enable_form()
    
    def _edit_user(self):
        """Edit selected user"""
        if not self.selected_user:
            MessageDialog.show_warning(self, "Warning", "Please select a user to edit.")
            return
        
        self.user_form.set_user_data(self.selected_user)
        self._enable_form()
    
    def _delete_user(self):
        """Delete selected user"""
        if not self.selected_user:
            MessageDialog.show_warning(self, "Warning", "Please select a user to delete.")
            return
        
        # Confirm deletion
        if not ConfirmationDialog.confirm(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete user '{self.selected_user.username}'?\n\n"
            f"This action cannot be undone."
        ):
            return
        
        try:
            success, message = self.auth_manager.delete_user(self.selected_user.id)
            if success:
                MessageDialog.show_success(self, "Success", message)
                self._refresh_users()
                self.user_form.clear_form()
                self._disable_form()
                self.users_updated.emit()
            else:
                MessageDialog.show_error(self, "Error", message)
        except Exception as e:
            self.logger.error(f"Failed to delete user: {e}")
            MessageDialog.show_error(self, "Error", f"Failed to delete user: {str(e)}")
    
    def _activate_user(self):
        """Activate selected user"""
        if not self.selected_user:
            return
        
        try:
            success, message = self.auth_manager.activate_user(self.selected_user.id)
            if success:
                MessageDialog.show_success(self, "Success", message)
                self._refresh_users()
                self.users_updated.emit()
            else:
                MessageDialog.show_error(self, "Error", message)
        except Exception as e:
            self.logger.error(f"Failed to activate user: {e}")
            MessageDialog.show_error(self, "Error", f"Failed to activate user: {str(e)}")
    
    def _deactivate_user(self):
        """Deactivate selected user"""
        if not self.selected_user:
            return
        
        # Confirm deactivation
        if not ConfirmationDialog.confirm(
            self,
            "Confirm Deactivation",
            f"Are you sure you want to deactivate user '{self.selected_user.username}'?\n\n"
            f"The user will not be able to log in until reactivated."
        ):
            return
        
        try:
            success, message = self.auth_manager.deactivate_user(self.selected_user.id)
            if success:
                MessageDialog.show_success(self, "Success", message)
                self._refresh_users()
                self.users_updated.emit()
            else:
                MessageDialog.show_error(self, "Error", message)
        except Exception as e:
            self.logger.error(f"Failed to deactivate user: {e}")
            MessageDialog.show_error(self, "Error", f"Failed to deactivate user: {str(e)}")
    
    def _save_user(self):
        """Save user (add or update)"""
        # Validate form
        is_valid, errors = self.user_form.validate_form()
        if not is_valid:
            error_message = "Please fix the following errors:\n\n" + "\n".join(errors)
            MessageDialog.show_error(self, "Validation Error", error_message)
            return
        
        # Get form data
        form_data = self.user_form.get_form_data()
        
        try:
            if self.user_form.current_user:  # Editing existing user
                success, message, user = self.auth_manager.update_user(
                    self.user_form.current_user.id, form_data
                )
            else:  # Adding new user
                success, message, user = self.auth_manager.create_user(form_data)
            
            if success:
                MessageDialog.show_success(self, "Success", message)
                self._refresh_users()
                self.user_form.clear_form()
                self._disable_form()
                self.users_updated.emit()
            else:
                MessageDialog.show_error(self, "Error", message)
        
        except Exception as e:
            self.logger.error(f"Failed to save user: {e}")
            MessageDialog.show_error(self, "Error", f"Failed to save user: {str(e)}")
    
    def _cancel_form(self):
        """Cancel form editing"""
        self.user_form.clear_form()
        self._disable_form()
    
    def _enable_form(self):
        """Enable form for editing"""
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.user_form.setEnabled(True)
    
    def _disable_form(self):
        """Disable form editing"""
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.user_form.setEnabled(False)
    
    def _on_form_data_changed(self):
        """Handle form data changes"""
        # Enable save button if form is enabled
        if self.user_form.isEnabled():
            self.save_button.setEnabled(True)