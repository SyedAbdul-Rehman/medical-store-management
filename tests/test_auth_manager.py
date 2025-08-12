"""
Unit tests for Authentication Manager
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from medical_store_app.managers.auth_manager import AuthManager
from medical_store_app.models.user import User
from medical_store_app.repositories.user_repository import UserRepository


class TestAuthManager:
    """Test cases for AuthManager class"""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository"""
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def auth_manager(self, mock_user_repository):
        """Create auth manager with mock repository"""
        return AuthManager(mock_user_repository)
    
    @pytest.fixture
    def sample_admin_user(self):
        """Sample admin user for testing"""
        user = User(
            id=1,
            username='admin',
            role='admin',
            is_active=True,
            full_name='Admin User'
        )
        user.set_password('admin123')
        return user
    
    @pytest.fixture
    def sample_cashier_user(self):
        """Sample cashier user for testing"""
        user = User(
            id=2,
            username='cashier',
            role='cashier',
            is_active=True,
            full_name='Cashier User'
        )
        user.set_password('cashier123')
        return user
    
    def test_login_success_admin(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test successful admin login"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        
        # Act
        success, message, user = auth_manager.login('admin', 'admin123')
        
        # Assert
        assert success is True
        assert "Login successful" in message
        assert user == sample_admin_user
        assert auth_manager.is_logged_in() is True
        assert auth_manager.is_admin() is True
        mock_user_repository.authenticate.assert_called_once_with('admin', 'admin123')
    
    def test_login_success_cashier(self, auth_manager, mock_user_repository, sample_cashier_user):
        """Test successful cashier login"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_cashier_user
        
        # Act
        success, message, user = auth_manager.login('cashier', 'cashier123')
        
        # Assert
        assert success is True
        assert "Login successful" in message
        assert user == sample_cashier_user
        assert auth_manager.is_logged_in() is True
        assert auth_manager.is_cashier() is True
    
    def test_login_invalid_credentials(self, auth_manager, mock_user_repository):
        """Test login with invalid credentials"""
        # Arrange
        mock_user_repository.authenticate.return_value = None
        
        # Act
        success, message, user = auth_manager.login('admin', 'wrongpassword')
        
        # Assert
        assert success is False
        assert "Invalid credentials" in message
        assert user is None
        assert auth_manager.is_logged_in() is False
    
    def test_login_empty_username(self, auth_manager):
        """Test login with empty username"""
        # Act
        success, message, user = auth_manager.login('', 'password')
        
        # Assert
        assert success is False
        assert "Username is required" in message
        assert user is None
    
    def test_login_empty_password(self, auth_manager):
        """Test login with empty password"""
        # Act
        success, message, user = auth_manager.login('admin', '')
        
        # Assert
        assert success is False
        assert "Password is required" in message
        assert user is None
    
    def test_login_account_lockout(self, auth_manager, mock_user_repository):
        """Test account lockout after multiple failed attempts"""
        # Arrange
        mock_user_repository.authenticate.return_value = None
        
        # Act - Make multiple failed attempts
        for i in range(5):
            success, message, user = auth_manager.login('admin', 'wrongpassword')
            assert success is False
        
        # Act - Next attempt should be locked
        success, message, user = auth_manager.login('admin', 'wrongpassword')
        
        # Assert
        assert success is False
        assert "Account locked" in message
        assert user is None
    
    def test_logout_success(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test successful logout"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.logout()
        
        # Assert
        assert success is True
        assert "Logout successful" in message
        assert auth_manager.is_logged_in() is False
        assert auth_manager.get_current_user() is None
    
    def test_logout_no_active_session(self, auth_manager):
        """Test logout with no active session"""
        # Act
        success, message = auth_manager.logout()
        
        # Assert
        assert success is False
        assert "No active session" in message
    
    def test_session_timeout(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test session timeout"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.set_session_timeout(1)  # 1 minute timeout
        auth_manager.login('admin', 'admin123')
        
        # Mock datetime to simulate time passage
        with patch('medical_store_app.managers.auth_manager.datetime') as mock_datetime:
            # Simulate 2 minutes later
            future_time = datetime.now() + timedelta(minutes=2)
            mock_datetime.now.return_value = future_time
            
            # Act
            is_logged_in = auth_manager.is_logged_in()
            
            # Assert
            assert is_logged_in is False
    
    def test_refresh_session(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test session refresh"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        result = auth_manager.refresh_session()
        
        # Assert
        assert result is True
        assert auth_manager.is_logged_in() is True
    
    def test_has_permission_admin(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test admin permissions"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act & Assert
        assert auth_manager.has_permission('medicine_management') is True
        assert auth_manager.has_permission('user_management') is True
        assert auth_manager.has_permission('billing') is True
    
    def test_has_permission_cashier(self, auth_manager, mock_user_repository, sample_cashier_user):
        """Test cashier permissions"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_cashier_user
        auth_manager.login('cashier', 'cashier123')
        
        # Act & Assert
        assert auth_manager.has_permission('billing') is True
        assert auth_manager.has_permission('medicine_view') is True
        assert auth_manager.has_permission('user_management') is False
    
    def test_require_admin_success(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test require admin with admin user"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        has_access, message = auth_manager.require_admin()
        
        # Assert
        assert has_access is True
        assert message == "Access granted"
    
    def test_require_admin_failure_not_logged_in(self, auth_manager):
        """Test require admin without login"""
        # Act
        has_access, message = auth_manager.require_admin()
        
        # Assert
        assert has_access is False
        assert message == "Authentication required"
    
    def test_require_admin_failure_not_admin(self, auth_manager, mock_user_repository, sample_cashier_user):
        """Test require admin with cashier user"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_cashier_user
        auth_manager.login('cashier', 'cashier123')
        
        # Act
        has_access, message = auth_manager.require_admin()
        
        # Assert
        assert has_access is False
        assert message == "Admin privileges required"
    
    def test_create_user_success(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test successful user creation"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.username_exists.return_value = False
        new_user = User(id=3, username='newuser', role='cashier')
        mock_user_repository.save.return_value = new_user
        
        auth_manager.login('admin', 'admin123')
        
        user_data = {
            'username': 'newuser',
            'password': 'password123',
            'role': 'cashier',
            'full_name': 'New User'
        }
        
        # Act
        success, message, user = auth_manager.create_user(user_data)
        
        # Assert
        assert success is True
        assert "created successfully" in message
        assert user == new_user
        mock_user_repository.username_exists.assert_called_once_with('newuser')
        mock_user_repository.save.assert_called_once()
    
    def test_create_user_duplicate_username(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test user creation with duplicate username"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.username_exists.return_value = True
        
        auth_manager.login('admin', 'admin123')
        
        user_data = {
            'username': 'existinguser',
            'password': 'password123',
            'role': 'cashier'
        }
        
        # Act
        success, message, user = auth_manager.create_user(user_data)
        
        # Assert
        assert success is False
        assert "already exists" in message
        assert user is None
    
    def test_create_user_weak_password(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test user creation with weak password"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.username_exists.return_value = False
        
        auth_manager.login('admin', 'admin123')
        
        user_data = {
            'username': 'newuser',
            'password': '123',  # Weak password
            'role': 'cashier'
        }
        
        # Act
        success, message, user = auth_manager.create_user(user_data)
        
        # Assert
        assert success is False
        assert "Password must be at least 6 characters" in message
        assert user is None
    
    def test_create_user_not_admin(self, auth_manager, mock_user_repository, sample_cashier_user):
        """Test user creation without admin privileges"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_cashier_user
        auth_manager.login('cashier', 'cashier123')
        
        user_data = {
            'username': 'newuser',
            'password': 'password123',
            'role': 'cashier'
        }
        
        # Act
        success, message, user = auth_manager.create_user(user_data)
        
        # Assert
        assert success is False
        assert "Admin privileges required" in message
        assert user is None
    
    def test_update_user_success(self, auth_manager, mock_user_repository, sample_admin_user, sample_cashier_user):
        """Test successful user update"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.find_by_id.return_value = sample_cashier_user
        mock_user_repository.username_exists.return_value = False
        mock_user_repository.update.return_value = True
        
        auth_manager.login('admin', 'admin123')
        
        user_data = {
            'username': 'updated_cashier',
            'role': 'cashier',
            'full_name': 'Updated Cashier'
        }
        
        # Act
        success, message, user = auth_manager.update_user(2, user_data)
        
        # Assert
        assert success is True
        assert "updated successfully" in message
        assert user.username == 'updated_cashier'
        mock_user_repository.update.assert_called_once()
    
    def test_delete_user_success(self, auth_manager, mock_user_repository, sample_admin_user, sample_cashier_user):
        """Test successful user deletion"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.find_by_id.return_value = sample_cashier_user
        mock_user_repository.delete.return_value = True
        
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.delete_user(2)
        
        # Assert
        assert success is True
        assert "deleted successfully" in message
        mock_user_repository.delete.assert_called_once_with(2)
    
    def test_delete_user_current_user(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test deleting current user (should fail)"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.delete_user(1)  # Same ID as current user
        
        # Assert
        assert success is False
        assert "Cannot delete currently logged-in user" in message
    
    def test_change_password_success(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test successful password change"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.update_password.return_value = True
        
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.change_password('admin123', 'newpassword123')
        
        # Assert
        assert success is True
        assert "Password changed successfully" in message
        mock_user_repository.update_password.assert_called_once_with(1, 'newpassword123')
    
    def test_change_password_wrong_current(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test password change with wrong current password"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.change_password('wrongpassword', 'newpassword123')
        
        # Assert
        assert success is False
        assert "Current password is incorrect" in message
    
    def test_change_password_weak_new_password(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test password change with weak new password"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.change_password('admin123', '123')
        
        # Assert
        assert success is False
        assert "New password must be at least 6 characters" in message
    
    def test_get_all_users_admin(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test getting all users as admin"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.find_all.return_value = [sample_admin_user]
        
        auth_manager.login('admin', 'admin123')
        
        # Act
        users = auth_manager.get_all_users()
        
        # Assert
        assert len(users) == 1
        assert users[0] == sample_admin_user
        mock_user_repository.find_all.assert_called_once()
    
    def test_get_all_users_not_admin(self, auth_manager, mock_user_repository, sample_cashier_user):
        """Test getting all users as non-admin"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_cashier_user
        auth_manager.login('cashier', 'cashier123')
        
        # Act
        users = auth_manager.get_all_users()
        
        # Assert
        assert users == []
        mock_user_repository.find_all.assert_not_called()
    
    def test_activate_deactivate_user(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test user activation and deactivation"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        mock_user_repository.activate_user.return_value = True
        mock_user_repository.deactivate_user.return_value = True
        
        auth_manager.login('admin', 'admin123')
        
        # Act - Activate
        success, message = auth_manager.activate_user(2)
        assert success is True
        assert "activated successfully" in message
        
        # Act - Deactivate
        success, message = auth_manager.deactivate_user(2)
        assert success is True
        assert "deactivated successfully" in message
    
    def test_deactivate_current_user(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test deactivating current user (should fail)"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        success, message = auth_manager.deactivate_user(1)  # Same ID as current user
        
        # Assert
        assert success is False
        assert "Cannot deactivate currently logged-in user" in message
    
    def test_get_session_info(self, auth_manager, mock_user_repository, sample_admin_user):
        """Test getting session information"""
        # Arrange
        mock_user_repository.authenticate.return_value = sample_admin_user
        auth_manager.login('admin', 'admin123')
        
        # Act
        session_info = auth_manager.get_session_info()
        
        # Assert
        assert session_info['logged_in'] is True
        assert session_info['user']['username'] == 'admin'
        assert 'last_activity' in session_info
        assert 'session_timeout_minutes' in session_info
    
    def test_get_session_info_not_logged_in(self, auth_manager):
        """Test getting session info when not logged in"""
        # Act
        session_info = auth_manager.get_session_info()
        
        # Assert
        assert session_info['logged_in'] is False
    
    def test_configuration_methods(self, auth_manager):
        """Test configuration methods"""
        # Test session timeout
        assert auth_manager.set_session_timeout(60) is True
        assert auth_manager.set_session_timeout(0) is False
        
        # Test max failed attempts
        assert auth_manager.set_max_failed_attempts(3) is True
        assert auth_manager.get_max_failed_attempts() == 3
        assert auth_manager.set_max_failed_attempts(0) is False
        
        # Test lockout duration
        assert auth_manager.set_lockout_duration(15) is True
        assert auth_manager.get_lockout_duration() == 15
        assert auth_manager.set_lockout_duration(0) is False
    
    def test_exception_handling(self, auth_manager, mock_user_repository):
        """Test exception handling in various methods"""
        # Arrange
        mock_user_repository.authenticate.side_effect = Exception("Database error")
        
        # Act & Assert
        success, message, user = auth_manager.login('admin', 'password')
        assert success is False
        assert "Login failed due to system error" in message
        assert user is None