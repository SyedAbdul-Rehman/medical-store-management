"""
Integration tests for User Management functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from medical_store_app.managers.auth_manager import AuthManager
from medical_store_app.repositories.user_repository import UserRepository
from medical_store_app.models.user import User
from medical_store_app.config.database import DatabaseManager


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_db_manager():
    """Create mock database manager"""
    db_manager = Mock(spec=DatabaseManager)
    db_manager.get_cursor.return_value.__enter__ = Mock()
    db_manager.get_cursor.return_value.__exit__ = Mock()
    return db_manager


@pytest.fixture
def user_repository(mock_db_manager):
    """Create user repository with mock database"""
    return UserRepository(mock_db_manager)


@pytest.fixture
def auth_manager(user_repository):
    """Create auth manager with mock repository"""
    return AuthManager(user_repository)


class TestUserManagementIntegration:
    """Integration tests for user management functionality"""
    
    def test_auth_manager_user_creation_flow(self, auth_manager):
        """Test complete user creation flow through auth manager"""
        # Mock the repository methods
        auth_manager.user_repository.username_exists = Mock(return_value=False)
        auth_manager.user_repository.save = Mock(return_value=User(
            id=1, username="testuser", role="cashier", is_active=True
        ))
        
        # Set current user as admin and establish session
        admin_user = User(id=1, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test user creation
        user_data = {
            'username': 'testuser',
            'password': 'password123',
            'role': 'cashier',
            'is_active': True,
            'full_name': 'Test User',
            'email': 'test@example.com'
        }
        
        success, message, user = auth_manager.create_user(user_data)
        
        assert success is True
        assert "created successfully" in message
        assert user is not None
        assert user.username == "testuser"
    
    def test_auth_manager_user_update_flow(self, auth_manager):
        """Test complete user update flow through auth manager"""
        # Mock the repository methods
        existing_user = User(id=1, username="testuser", role="cashier", is_active=True)
        auth_manager.user_repository.find_by_id = Mock(return_value=existing_user)
        auth_manager.user_repository.username_exists = Mock(return_value=False)
        auth_manager.user_repository.update = Mock(return_value=True)
        
        # Set current user as admin and establish session
        admin_user = User(id=2, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test user update
        user_data = {
            'username': 'updateduser',
            'role': 'admin',
            'is_active': False,
            'full_name': 'Updated User'
        }
        
        success, message, user = auth_manager.update_user(1, user_data)
        
        assert success is True
        assert "updated successfully" in message
        assert user is not None
        assert user.username == "updateduser"
        assert user.role == "admin"
        assert user.is_active is False
    
    def test_auth_manager_user_deletion_flow(self, auth_manager):
        """Test complete user deletion flow through auth manager"""
        # Mock the repository methods
        existing_user = User(id=1, username="testuser", role="cashier", is_active=True)
        auth_manager.user_repository.find_by_id = Mock(return_value=existing_user)
        auth_manager.user_repository.delete = Mock(return_value=True)
        
        # Set current user as admin (different from user being deleted) and establish session
        admin_user = User(id=2, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test user deletion
        success, message = auth_manager.delete_user(1)
        
        assert success is True
        assert "deleted successfully" in message
    
    def test_auth_manager_user_activation_flow(self, auth_manager):
        """Test user activation flow through auth manager"""
        # Mock the repository method
        auth_manager.user_repository.activate_user = Mock(return_value=True)
        
        # Set current user as admin and establish session
        admin_user = User(id=1, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test user activation
        success, message = auth_manager.activate_user(2)
        
        assert success is True
        assert "activated successfully" in message
    
    def test_auth_manager_user_deactivation_flow(self, auth_manager):
        """Test user deactivation flow through auth manager"""
        # Mock the repository method
        auth_manager.user_repository.deactivate_user = Mock(return_value=True)
        
        # Set current user as admin (different from user being deactivated) and establish session
        admin_user = User(id=1, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test user deactivation
        success, message = auth_manager.deactivate_user(2)
        
        assert success is True
        assert "deactivated successfully" in message
    
    def test_auth_manager_get_all_users(self, auth_manager):
        """Test getting all users through auth manager"""
        # Mock users data
        test_users = [
            User(id=1, username="admin", role="admin", is_active=True),
            User(id=2, username="cashier1", role="cashier", is_active=True),
            User(id=3, username="cashier2", role="cashier", is_active=False)
        ]
        
        auth_manager.user_repository.find_all = Mock(return_value=test_users)
        
        # Set current user as admin and establish session
        admin_user = User(id=1, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test getting all users
        users = auth_manager.get_all_users()
        
        assert len(users) == 3
        assert users[0].username == "admin"
        assert users[1].username == "cashier1"
        assert users[2].username == "cashier2"
    
    def test_auth_manager_access_control_admin(self, auth_manager):
        """Test access control for admin user"""
        # Set current user as admin and establish session
        admin_user = User(id=1, username="admin", role="admin", is_active=True)
        auth_manager._current_user = admin_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test admin permissions
        assert auth_manager.is_admin() is True
        assert auth_manager.is_cashier() is False
        assert auth_manager.has_permission("users") is True
        assert auth_manager.has_permission("medicine") is True
        assert auth_manager.has_permission("billing") is True
        
        # Test admin-only operations
        has_access, message = auth_manager.require_admin()
        assert has_access is True
        assert message == "Access granted"
    
    def test_auth_manager_access_control_cashier(self, auth_manager):
        """Test access control for cashier user"""
        # Set current user as cashier and establish session
        cashier_user = User(id=2, username="cashier", role="cashier", is_active=True)
        auth_manager._current_user = cashier_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test cashier permissions
        assert auth_manager.is_admin() is False
        assert auth_manager.is_cashier() is True
        assert auth_manager.has_permission("users") is False  # Cashiers can't manage users
        assert auth_manager.has_permission("billing") is True
        assert auth_manager.has_permission("medicine_view") is True
        
        # Test admin-only operations should fail
        has_access, message = auth_manager.require_admin()
        assert has_access is False
        assert "Admin privileges required" in message
    
    def test_user_management_permission_validation(self, auth_manager):
        """Test that user management operations require admin privileges"""
        # Set current user as cashier and establish session
        cashier_user = User(id=2, username="cashier", role="cashier", is_active=True)
        auth_manager._current_user = cashier_user
        from datetime import datetime
        auth_manager._last_activity = datetime.now()
        
        # Test that cashier cannot create users
        user_data = {'username': 'test', 'password': 'password123', 'role': 'cashier'}
        success, message, user = auth_manager.create_user(user_data)
        assert success is False
        assert "Admin privileges required" in message
        
        # Test that cashier cannot update users
        success, message, user = auth_manager.update_user(1, user_data)
        assert success is False
        assert "Admin privileges required" in message
        
        # Test that cashier cannot delete users
        success, message = auth_manager.delete_user(1)
        assert success is False
        assert "Admin privileges required" in message
        
        # Test that cashier cannot get all users
        users = auth_manager.get_all_users()
        assert len(users) == 0  # Should return empty list for non-admin


if __name__ == '__main__':
    pytest.main([__file__])