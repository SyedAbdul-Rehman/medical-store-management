"""
Tests for User Management Dialog
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from medical_store_app.ui.dialogs.user_management_dialog import (
    UserManagementDialog, UserFormWidget, UserTableWidget
)
from medical_store_app.managers.auth_manager import AuthManager
from medical_store_app.models.user import User


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_auth_manager():
    """Create mock auth manager"""
    auth_manager = Mock(spec=AuthManager)
    
    # Mock users data
    test_users = [
        User(id=1, username="admin", role="admin", is_active=True, 
             full_name="Administrator", email="admin@test.com"),
        User(id=2, username="cashier1", role="cashier", is_active=True,
             full_name="Cashier One", email="cashier1@test.com"),
        User(id=3, username="cashier2", role="cashier", is_active=False,
             full_name="Cashier Two", email="cashier2@test.com")
    ]
    
    auth_manager.get_all_users.return_value = test_users
    auth_manager.create_user.return_value = (True, "User created successfully", test_users[0])
    auth_manager.update_user.return_value = (True, "User updated successfully", test_users[0])
    auth_manager.delete_user.return_value = (True, "User deleted successfully")
    auth_manager.activate_user.return_value = (True, "User activated successfully")
    auth_manager.deactivate_user.return_value = (True, "User deactivated successfully")
    
    return auth_manager


class TestUserFormWidget:
    """Test cases for UserFormWidget"""
    
    def test_form_initialization(self, app):
        """Test form widget initialization"""
        form = UserFormWidget()
        
        # Check that all form fields are created
        assert form.username_input is not None
        assert form.password_input is not None
        assert form.confirm_password_input is not None
        assert form.role_combo is not None
        assert form.is_active_checkbox is not None
        assert form.full_name_input is not None
        assert form.email_input is not None
        assert form.phone_input is not None
        
        # Check default values
        assert form.role_combo.currentText() == "cashier"
        assert form.is_active_checkbox.isChecked() is True
    
    def test_set_user_data(self, app):
        """Test setting user data in form"""
        form = UserFormWidget()
        
        user = User(
            id=1,
            username="testuser",
            role="admin",
            is_active=False,
            full_name="Test User",
            email="test@example.com",
            phone="123-456-7890"
        )
        
        form.set_user_data(user)
        
        assert form.username_input.text() == "testuser"
        assert form.role_combo.currentText() == "admin"
        assert form.is_active_checkbox.isChecked() is False
        assert form.full_name_input.text() == "Test User"
        assert form.email_input.text() == "test@example.com"
        assert form.phone_input.text() == "123-456-7890"
    
    def test_get_form_data(self, app):
        """Test getting form data"""
        form = UserFormWidget()
        
        # Set form values
        form.username_input.setText("newuser")
        form.password_input.setText("password123")
        form.role_combo.setCurrentText("admin")
        form.is_active_checkbox.setChecked(False)
        form.full_name_input.setText("New User")
        form.email_input.setText("new@example.com")
        form.phone_input.setText("987-654-3210")
        
        data = form.get_form_data()
        
        assert data['username'] == "newuser"
        assert data['password'] == "password123"
        assert data['role'] == "admin"
        assert data['is_active'] is False
        assert data['full_name'] == "New User"
        assert data['email'] == "new@example.com"
        assert data['phone'] == "987-654-3210"
    
    def test_form_validation_valid(self, app):
        """Test form validation with valid data"""
        form = UserFormWidget()
        
        # Set valid form data
        form.username_input.setText("validuser")
        form.password_input.setText("password123")
        form.confirm_password_input.setText("password123")
        form.email_input.setText("valid@example.com")
        
        is_valid, errors = form.validate_form()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_form_validation_invalid_username(self, app):
        """Test form validation with invalid username"""
        form = UserFormWidget()
        
        # Set invalid username (too short)
        form.username_input.setText("ab")
        form.password_input.setText("password123")
        form.confirm_password_input.setText("password123")
        
        is_valid, errors = form.validate_form()
        
        assert is_valid is False
        assert any("Username must be at least 3 characters" in error for error in errors)
    
    def test_form_validation_password_mismatch(self, app):
        """Test form validation with password mismatch"""
        form = UserFormWidget()
        
        # Set mismatched passwords
        form.username_input.setText("validuser")
        form.password_input.setText("password123")
        form.confirm_password_input.setText("different123")
        
        is_valid, errors = form.validate_form()
        
        assert is_valid is False
        assert any("Passwords do not match" in error for error in errors)
    
    def test_form_validation_invalid_email(self, app):
        """Test form validation with invalid email"""
        form = UserFormWidget()
        
        # Set valid required fields and invalid email
        form.username_input.setText("validuser")
        form.password_input.setText("password123")
        form.confirm_password_input.setText("password123")
        form.email_input.setText("invalid-email")
        
        is_valid, errors = form.validate_form()
        
        assert is_valid is False
        assert any("Invalid email format" in error for error in errors)
    
    def test_clear_form(self, app):
        """Test clearing form data"""
        form = UserFormWidget()
        
        # Set form data
        form.username_input.setText("testuser")
        form.password_input.setText("password123")
        form.full_name_input.setText("Test User")
        
        # Clear form
        form.clear_form()
        
        assert form.username_input.text() == ""
        assert form.password_input.text() == ""
        assert form.full_name_input.text() == ""
        assert form.role_combo.currentText() == "cashier"
        assert form.is_active_checkbox.isChecked() is True


class TestUserTableWidget:
    """Test cases for UserTableWidget"""
    
    def test_table_initialization(self, app):
        """Test table widget initialization"""
        table = UserTableWidget()
        
        # Check table setup
        assert table.columnCount() == 8
        assert table.rowCount() == 0
        
        # Check headers
        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        expected_headers = ["ID", "Username", "Full Name", "Role", "Status", "Email", "Last Login", "Created"]
        assert headers == expected_headers
    
    def test_load_users(self, app):
        """Test loading users into table"""
        table = UserTableWidget()
        
        users = [
            User(id=1, username="admin", role="admin", is_active=True, full_name="Administrator"),
            User(id=2, username="cashier", role="cashier", is_active=False, full_name="Cashier")
        ]
        
        table.load_users(users)
        
        assert table.rowCount() == 2
        assert table.item(0, 1).text() == "admin"  # Username
        assert table.item(0, 3).text() == "Admin"  # Role
        assert table.item(1, 1).text() == "cashier"
        assert table.item(1, 3).text() == "Cashier"
    
    def test_get_selected_user(self, app):
        """Test getting selected user"""
        table = UserTableWidget()
        
        users = [
            User(id=1, username="admin", role="admin", is_active=True),
            User(id=2, username="cashier", role="cashier", is_active=True)
        ]
        
        table.load_users(users)
        
        # Select first row
        table.selectRow(0)
        selected_user = table.get_selected_user()
        
        assert selected_user is not None
        assert selected_user.username == "admin"


class TestUserManagementDialog:
    """Test cases for UserManagementDialog"""
    
    def test_dialog_initialization(self, app, mock_auth_manager):
        """Test dialog initialization"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Check that components are created
        assert dialog.user_table is not None
        assert dialog.user_form is not None
        assert dialog.add_button is not None
        assert dialog.edit_button is not None
        assert dialog.delete_button is not None
        
        # Check that users are loaded
        mock_auth_manager.get_all_users.assert_called_once()
    
    def test_refresh_users(self, app, mock_auth_manager):
        """Test refreshing users list"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Reset mock to clear initialization call
        mock_auth_manager.reset_mock()
        
        # Call refresh
        dialog._refresh_users()
        
        # Verify auth manager was called
        mock_auth_manager.get_all_users.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.user_management_dialog.MessageDialog')
    def test_add_user_success(self, mock_message_dialog, app, mock_auth_manager):
        """Test successful user addition"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Set up form with valid data
        dialog.user_form.username_input.setText("newuser")
        dialog.user_form.password_input.setText("password123")
        dialog.user_form.confirm_password_input.setText("password123")
        dialog.user_form.role_combo.setCurrentText("cashier")
        
        # Enable form
        dialog._enable_form()
        
        # Call save user
        dialog._save_user()
        
        # Verify auth manager was called
        mock_auth_manager.create_user.assert_called_once()
        
        # Verify success message was shown
        mock_message_dialog.show_success.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.user_management_dialog.MessageDialog')
    def test_add_user_validation_error(self, mock_message_dialog, app, mock_auth_manager):
        """Test user addition with validation error"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Set up form with invalid data (no username)
        dialog.user_form.password_input.setText("password123")
        dialog.user_form.confirm_password_input.setText("password123")
        
        # Enable form
        dialog._enable_form()
        
        # Call save user
        dialog._save_user()
        
        # Verify auth manager was NOT called
        mock_auth_manager.create_user.assert_not_called()
        
        # Verify error message was shown
        mock_message_dialog.show_error.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.user_management_dialog.ConfirmationDialog')
    @patch('medical_store_app.ui.dialogs.user_management_dialog.MessageDialog')
    def test_delete_user_success(self, mock_message_dialog, mock_confirmation_dialog, app, mock_auth_manager):
        """Test successful user deletion"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Mock confirmation dialog to return True
        mock_confirmation_dialog.confirm.return_value = True
        
        # Set selected user
        test_user = User(id=1, username="testuser", role="cashier", is_active=True)
        dialog.selected_user = test_user
        
        # Call delete user
        dialog._delete_user()
        
        # Verify confirmation was shown
        mock_confirmation_dialog.confirm.assert_called_once()
        
        # Verify auth manager was called
        mock_auth_manager.delete_user.assert_called_once_with(1)
        
        # Verify success message was shown
        mock_message_dialog.show_success.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.user_management_dialog.ConfirmationDialog')
    def test_delete_user_cancelled(self, mock_confirmation_dialog, app, mock_auth_manager):
        """Test user deletion cancelled"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Mock confirmation dialog to return False
        mock_confirmation_dialog.confirm.return_value = False
        
        # Set selected user
        test_user = User(id=1, username="testuser", role="cashier", is_active=True)
        dialog.selected_user = test_user
        
        # Call delete user
        dialog._delete_user()
        
        # Verify confirmation was shown
        mock_confirmation_dialog.confirm.assert_called_once()
        
        # Verify auth manager was NOT called
        mock_auth_manager.delete_user.assert_not_called()
    
    @patch('medical_store_app.ui.dialogs.user_management_dialog.MessageDialog')
    def test_activate_user(self, mock_message_dialog, app, mock_auth_manager):
        """Test user activation"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Set selected user
        test_user = User(id=1, username="testuser", role="cashier", is_active=False)
        dialog.selected_user = test_user
        
        # Call activate user
        dialog._activate_user()
        
        # Verify auth manager was called
        mock_auth_manager.activate_user.assert_called_once_with(1)
        
        # Verify success message was shown
        mock_message_dialog.show_success.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.user_management_dialog.ConfirmationDialog')
    @patch('medical_store_app.ui.dialogs.user_management_dialog.MessageDialog')
    def test_deactivate_user(self, mock_message_dialog, mock_confirmation_dialog, app, mock_auth_manager):
        """Test user deactivation"""
        dialog = UserManagementDialog(mock_auth_manager)
        
        # Mock confirmation dialog to return True
        mock_confirmation_dialog.confirm.return_value = True
        
        # Set selected user
        test_user = User(id=1, username="testuser", role="cashier", is_active=True)
        dialog.selected_user = test_user
        
        # Call deactivate user
        dialog._deactivate_user()
        
        # Verify confirmation was shown
        mock_confirmation_dialog.confirm.assert_called_once()
        
        # Verify auth manager was called
        mock_auth_manager.deactivate_user.assert_called_once_with(1)
        
        # Verify success message was shown
        mock_message_dialog.show_success.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])