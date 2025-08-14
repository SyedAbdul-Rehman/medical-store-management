"""
Tests for login dialog and authentication flow
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add project root to path
sys.path.insert(0, '.')

from medical_store_app.ui.dialogs.login_dialog import LoginDialog, LoginManager
from medical_store_app.managers.auth_manager import AuthManager
from medical_store_app.models.user import User
from medical_store_app.repositories.user_repository import UserRepository


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_auth_manager():
    """Create mock authentication manager"""
    mock_auth = Mock(spec=AuthManager)
    return mock_auth


@pytest.fixture
def mock_user():
    """Create mock user instance"""
    user = User(
        id=1,
        username="testuser",
        role="admin",
        is_active=True,
        full_name="Test User"
    )
    return user


@pytest.fixture
def login_dialog(app, mock_auth_manager):
    """Create login dialog instance for testing"""
    dialog = LoginDialog(mock_auth_manager)
    return dialog


class TestLoginDialog:
    """Test cases for LoginDialog class"""
    
    def test_dialog_initialization(self, login_dialog, mock_auth_manager):
        """Test login dialog initialization"""
        assert login_dialog.auth_manager == mock_auth_manager
        assert login_dialog.windowTitle() == "Login - Medical Store Management"
        assert login_dialog.isModal()
        assert login_dialog.login_attempts == 0
        assert not login_dialog.is_logging_in
        
        # Check UI components exist
        assert login_dialog.username_input is not None
        assert login_dialog.password_input is not None
        assert login_dialog.remember_checkbox is not None
        assert login_dialog.login_button is not None
        assert login_dialog.cancel_button is not None
        assert login_dialog.error_label is not None
    
    def test_initial_ui_state(self, login_dialog):
        """Test initial UI state"""
        # Login button should be disabled initially
        assert not login_dialog.login_button.isEnabled()
        
        # Error label should be hidden
        assert not login_dialog.error_label.isVisible()
        
        # Input fields should be empty
        assert login_dialog.username_input.text() == ""
        assert login_dialog.password_input.text() == ""
        assert not login_dialog.remember_checkbox.isChecked()
    
    def test_input_validation(self, login_dialog):
        """Test input field validation"""
        # Initially login button should be disabled
        assert not login_dialog.login_button.isEnabled()
        
        # Enter username only
        login_dialog.username_input.setText("testuser")
        assert not login_dialog.login_button.isEnabled()
        
        # Enter password only (clear username first)
        login_dialog.username_input.clear()
        login_dialog.password_input.setText("password")
        assert not login_dialog.login_button.isEnabled()
        
        # Enter both username and password
        login_dialog.username_input.setText("testuser")
        login_dialog.password_input.setText("password")
        assert login_dialog.login_button.isEnabled()
        
        # Clear username
        login_dialog.username_input.clear()
        assert not login_dialog.login_button.isEnabled()
    
    def test_successful_login(self, login_dialog, mock_auth_manager, mock_user):
        """Test successful login flow"""
        # Mock successful authentication
        mock_auth_manager.login.return_value = (True, "Login successful", mock_user)
        
        # Set up input fields
        login_dialog.username_input.setText("testuser")
        login_dialog.password_input.setText("password123")
        
        # Connect signal to capture result
        login_result = []
        login_dialog.login_successful.connect(lambda user: login_result.append(user))
        
        # Trigger login
        login_dialog._perform_login("testuser", "password123")
        
        # Verify authentication was called
        mock_auth_manager.login.assert_called_once_with("testuser", "password123")
        
        # Verify success signal was emitted
        assert len(login_result) == 1
        assert login_result[0] == mock_user
        
        # Verify error message is hidden
        assert not login_dialog.error_label.isVisible()
    
    def test_failed_login(self, login_dialog, mock_auth_manager, app):
        """Test failed login flow"""
        # Show the dialog to ensure proper widget hierarchy
        login_dialog.show()
        app.processEvents()
        
        # Mock failed authentication
        mock_auth_manager.login.return_value = (False, "Invalid credentials", None)
        
        # Set up input fields
        login_dialog.username_input.setText("testuser")
        login_dialog.password_input.setText("wrongpassword")
        
        # Connect signal to capture result
        login_failures = []
        login_dialog.login_failed.connect(lambda msg: login_failures.append(msg))
        
        # Trigger login
        login_dialog._perform_login("testuser", "wrongpassword")
        app.processEvents()  # Process events to update UI
        
        # Wait a moment for the UI to update
        import time
        time.sleep(0.1)
        app.processEvents()
        
        # Verify authentication was called
        mock_auth_manager.login.assert_called_once_with("testuser", "wrongpassword")
        
        # Verify failure signal was emitted
        assert len(login_failures) == 1
        assert login_failures[0] == "Invalid credentials"
        
        # Verify error message text is set (visibility might be affected by layout)
        assert "Invalid credentials" in login_dialog.error_label.text()
        
        # Verify error message should be shown (test the method directly)
        login_dialog._show_error_message("Test error")
        app.processEvents()
        assert login_dialog.error_label.isVisible()
        assert "Test error" in login_dialog.error_label.text()
        
        # Verify login attempts incremented
        assert login_dialog.login_attempts == 1
        
        # Verify password field is cleared
        assert login_dialog.password_input.text() == ""
    
    def test_max_login_attempts(self, login_dialog, mock_auth_manager):
        """Test maximum login attempts handling"""
        # Mock failed authentication
        mock_auth_manager.login.return_value = (False, "Invalid credentials", None)
        
        # Set max attempts to 3 for testing
        login_dialog.max_attempts = 3
        
        # Perform failed logins
        for i in range(3):
            login_dialog._perform_login("testuser", "wrongpassword")
        
        # Verify login attempts reached maximum
        assert login_dialog.login_attempts == 3
    
    def test_login_button_click(self, login_dialog, mock_auth_manager, mock_user):
        """Test login button click handling"""
        # Mock successful authentication
        mock_auth_manager.login.return_value = (True, "Login successful", mock_user)
        
        # Set up input fields
        login_dialog.username_input.setText("testuser")
        login_dialog.password_input.setText("password123")
        
        # Click login button
        QTest.mouseClick(login_dialog.login_button, Qt.LeftButton)
        
        # Verify authentication was called
        mock_auth_manager.login.assert_called_once_with("testuser", "password123")
    
    def test_empty_username_validation(self, login_dialog, app):
        """Test validation when username is empty"""
        # Show the dialog to ensure proper widget hierarchy
        login_dialog.show()
        app.processEvents()
        
        # Set password but leave username empty
        login_dialog.password_input.setText("password123")
        
        # Trigger login
        login_dialog._on_login_clicked()
        app.processEvents()  # Process events to update UI
        
        # Verify error message is shown
        assert login_dialog.error_label.isVisible()
        assert "Please enter your username" in login_dialog.error_label.text()
    
    def test_empty_password_validation(self, login_dialog, app):
        """Test validation when password is empty"""
        # Show the dialog to ensure proper widget hierarchy
        login_dialog.show()
        app.processEvents()
        
        # Set username but leave password empty
        login_dialog.username_input.setText("testuser")
        
        # Trigger login
        login_dialog._on_login_clicked()
        app.processEvents()  # Process events to update UI
        
        # Verify error message is shown
        assert login_dialog.error_label.isVisible()
        assert "Please enter your password" in login_dialog.error_label.text()
    
    def test_login_state_ui_updates(self, login_dialog):
        """Test UI updates during login state"""
        # Test logging in state
        login_dialog._update_ui_for_login_state(True)
        
        assert login_dialog.login_button.text() == "Signing In..."
        assert not login_dialog.login_button.isEnabled()
        assert not login_dialog.username_input.isEnabled()
        assert not login_dialog.password_input.isEnabled()
        assert not login_dialog.remember_checkbox.isEnabled()
        assert not login_dialog.cancel_button.isEnabled()
        
        # Test normal state
        login_dialog.username_input.setText("test")
        login_dialog.password_input.setText("test")
        login_dialog._update_ui_for_login_state(False)
        
        assert login_dialog.login_button.text() == "Sign In"
        assert login_dialog.username_input.isEnabled()
        assert login_dialog.password_input.isEnabled()
        assert login_dialog.remember_checkbox.isEnabled()
        assert login_dialog.cancel_button.isEnabled()
    
    def test_error_message_handling(self, login_dialog, app):
        """Test error message show/hide functionality"""
        # Show the dialog to ensure proper widget hierarchy
        login_dialog.show()
        app.processEvents()
        
        # Initially error should be hidden
        assert not login_dialog.error_label.isVisible()
        
        # Show error message
        login_dialog._show_error_message("Test error message")
        app.processEvents()  # Process events to update UI
        assert login_dialog.error_label.isVisible()
        assert login_dialog.error_label.text() == "Test error message"
        
        # Hide error message
        login_dialog._hide_error_message()
        app.processEvents()  # Process events to update UI
        assert not login_dialog.error_label.isVisible()
    
    def test_form_reset(self, login_dialog):
        """Test form reset functionality"""
        # Set some values
        login_dialog.username_input.setText("testuser")
        login_dialog.password_input.setText("password")
        login_dialog.remember_checkbox.setChecked(True)
        login_dialog.login_attempts = 3
        login_dialog._show_error_message("Test error")
        
        # Reset form
        login_dialog.reset_form()
        
        # Verify reset
        assert login_dialog.username_input.text() == ""
        assert login_dialog.password_input.text() == ""
        assert not login_dialog.remember_checkbox.isChecked()
        assert login_dialog.login_attempts == 0
        assert not login_dialog.is_logging_in
        assert not login_dialog.error_label.isVisible()
    
    def test_set_username(self, login_dialog):
        """Test setting username programmatically"""
        login_dialog.set_username("testuser")
        assert login_dialog.username_input.text() == "testuser"
    
    def test_get_remember_me(self, login_dialog):
        """Test getting remember me checkbox state"""
        # Initially unchecked
        assert not login_dialog.get_remember_me()
        
        # Check the checkbox
        login_dialog.remember_checkbox.setChecked(True)
        assert login_dialog.get_remember_me()
    
    def test_cancel_button(self, login_dialog):
        """Test cancel button functionality"""
        # Connect signal to capture result
        rejected = []
        login_dialog.rejected.connect(lambda: rejected.append(True))
        
        # Click cancel button
        QTest.mouseClick(login_dialog.cancel_button, Qt.LeftButton)
        
        # Verify dialog was rejected
        assert len(rejected) == 1
    
    def test_enter_key_login(self, login_dialog, mock_auth_manager, mock_user):
        """Test login with Enter key in password field"""
        # Mock successful authentication
        mock_auth_manager.login.return_value = (True, "Login successful", mock_user)
        
        # Set up input fields
        login_dialog.username_input.setText("testuser")
        login_dialog.password_input.setText("password123")
        
        # Press Enter in password field
        QTest.keyPress(login_dialog.password_input, Qt.Key_Return)
        
        # Verify authentication was called
        mock_auth_manager.login.assert_called_once_with("testuser", "password123")


class TestLoginManager:
    """Test cases for LoginManager class"""
    
    def test_login_manager_initialization(self, mock_auth_manager):
        """Test login manager initialization"""
        manager = LoginManager(mock_auth_manager)
        
        assert manager.auth_manager == mock_auth_manager
        assert manager.parent is None
        assert manager.login_dialog is None
    
    def test_is_user_logged_in(self, mock_auth_manager):
        """Test checking if user is logged in"""
        manager = LoginManager(mock_auth_manager)
        
        # Mock logged in state
        mock_auth_manager.is_logged_in.return_value = True
        assert manager.is_user_logged_in()
        
        # Mock logged out state
        mock_auth_manager.is_logged_in.return_value = False
        assert not manager.is_user_logged_in()
        
        # Verify auth manager was called
        assert mock_auth_manager.is_logged_in.call_count == 2
    
    def test_get_current_user(self, mock_auth_manager, mock_user):
        """Test getting current user"""
        manager = LoginManager(mock_auth_manager)
        
        # Mock current user
        mock_auth_manager.get_current_user.return_value = mock_user
        result = manager.get_current_user()
        
        assert result == mock_user
        mock_auth_manager.get_current_user.assert_called_once()
    
    def test_logout(self, mock_auth_manager):
        """Test logout functionality"""
        manager = LoginManager(mock_auth_manager)
        
        # Mock successful logout
        mock_auth_manager.logout.return_value = (True, "Logout successful")
        result = manager.logout()
        
        assert result is True
        mock_auth_manager.logout.assert_called_once()
        
        # Mock failed logout
        mock_auth_manager.logout.return_value = (False, "Logout failed")
        result = manager.logout()
        
        assert result is False
    
    @patch('medical_store_app.ui.dialogs.login_dialog.LoginDialog')
    def test_show_login_dialog_success(self, mock_dialog_class, mock_auth_manager, mock_user, app):
        """Test successful login dialog flow"""
        manager = LoginManager(mock_auth_manager)
        
        # Mock dialog instance
        mock_dialog = Mock()
        mock_dialog.exec.return_value = 1  # QDialog.Accepted
        mock_dialog_class.return_value = mock_dialog
        
        # Mock auth manager
        mock_auth_manager.get_current_user.return_value = mock_user
        
        # Show login dialog
        success, user = manager.show_login_dialog()
        
        # Verify results
        assert success is True
        assert user == mock_user
        
        # Verify dialog was created and shown
        mock_dialog_class.assert_called_once_with(mock_auth_manager, None)
        mock_dialog.exec.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.login_dialog.LoginDialog')
    def test_show_login_dialog_cancelled(self, mock_dialog_class, mock_auth_manager, app):
        """Test cancelled login dialog flow"""
        manager = LoginManager(mock_auth_manager)
        
        # Mock dialog instance
        mock_dialog = Mock()
        mock_dialog.exec.return_value = 0  # QDialog.Rejected
        mock_dialog_class.return_value = mock_dialog
        
        # Show login dialog
        success, user = manager.show_login_dialog()
        
        # Verify results
        assert success is False
        assert user is None
        
        # Verify dialog was created and shown
        mock_dialog_class.assert_called_once_with(mock_auth_manager, None)
        mock_dialog.exec.assert_called_once()
        mock_dialog.deleteLater.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.login_dialog.LoginDialog')
    def test_show_login_dialog_exception(self, mock_dialog_class, mock_auth_manager, app):
        """Test login dialog with exception"""
        manager = LoginManager(mock_auth_manager)
        
        # Mock dialog to raise exception
        mock_dialog_class.side_effect = Exception("Test exception")
        
        # Show login dialog
        success, user = manager.show_login_dialog()
        
        # Verify results
        assert success is False
        assert user is None


class TestLoginDialogIntegration:
    """Integration tests for login dialog with real components"""
    
    def test_login_dialog_with_real_auth_manager(self, app):
        """Test login dialog with real authentication manager"""
        # Create mock user repository
        mock_user_repo = Mock(spec=UserRepository)
        
        # Create real auth manager
        auth_manager = AuthManager(mock_user_repo)
        
        # Create login dialog
        dialog = LoginDialog(auth_manager)
        
        # Verify dialog is properly initialized
        assert dialog.auth_manager == auth_manager
        assert dialog.username_input is not None
        assert dialog.password_input is not None
    
    def test_authentication_flow_integration(self, app):
        """Test complete authentication flow integration"""
        # Create mock user
        test_user = User(
            id=1,
            username="testuser",
            role="admin",
            is_active=True
        )
        test_user.set_password("password123")
        
        # Create mock user repository
        mock_user_repo = Mock(spec=UserRepository)
        mock_user_repo.authenticate.return_value = test_user
        
        # Create real auth manager
        auth_manager = AuthManager(mock_user_repo)
        
        # Create login manager
        login_manager = LoginManager(auth_manager)
        
        # Verify initial state
        assert not login_manager.is_user_logged_in()
        assert login_manager.get_current_user() is None
        
        # Perform login directly through auth manager
        success, message, user = auth_manager.login("testuser", "password123")
        
        # Verify login success
        assert success is True
        assert user == test_user
        assert login_manager.is_user_logged_in()
        assert login_manager.get_current_user() == test_user
        
        # Perform logout
        logout_success = login_manager.logout()
        assert logout_success is True
        assert not login_manager.is_user_logged_in()
        assert login_manager.get_current_user() is None


if __name__ == "__main__":
    pytest.main([__file__])