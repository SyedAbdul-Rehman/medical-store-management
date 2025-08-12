"""
Unit tests for User Repository
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime

from medical_store_app.config.database import DatabaseManager
from medical_store_app.repositories.user_repository import UserRepository
from medical_store_app.models.user import User


class TestUserRepository:
    """Test cases for UserRepository"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing"""
        # Create temporary database file
        db_fd, db_path = tempfile.mkstemp()
        os.close(db_fd)
        
        db_manager = DatabaseManager(db_path)
        db_manager.initialize()
        
        yield db_manager
        
        # Cleanup
        db_manager.close()
        os.unlink(db_path)
    
    @pytest.fixture
    def repository(self, db_manager):
        """Create user repository instance"""
        return UserRepository(db_manager)
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing"""
        user = User(
            username="testuser",
            role="cashier",
            is_active=True
        )
        user.set_password("password123")
        return user
    
    @pytest.fixture
    def admin_user(self):
        """Create a sample admin user for testing"""
        user = User(
            username="admin",
            role="admin",
            is_active=True
        )
        user.set_password("admin123")
        return user
    
    def test_save_user_success(self, repository, sample_user):
        """Test successful user save"""
        result = repository.save(sample_user)
        
        assert result is not None
        assert result.id is not None
        assert result.username == "testuser"
        assert result.role == "cashier"
        assert result.is_active is True
    
    def test_save_user_with_duplicate_username(self, repository, sample_user):
        """Test saving user with duplicate username fails"""
        # Save first user
        result1 = repository.save(sample_user)
        assert result1 is not None
        
        # Try to save another user with same username
        duplicate_user = User(
            username="testuser",  # Same username
            role="admin",
            is_active=True
        )
        duplicate_user.set_password("different123")
        
        result2 = repository.save(duplicate_user)
        assert result2 is None
    
    def test_save_invalid_user(self, repository):
        """Test saving invalid user fails"""
        invalid_user = User(
            username="",  # Invalid: empty username
            role="cashier",
            is_active=True
        )
        invalid_user.set_password("password123")
        
        result = repository.save(invalid_user)
        assert result is None
    
    def test_find_by_id_success(self, repository, sample_user):
        """Test finding user by ID"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Find by ID
        found_user = repository.find_by_id(saved_user.id)
        assert found_user is not None
        assert found_user.id == saved_user.id
        assert found_user.username == "testuser"
    
    def test_find_by_id_not_found(self, repository):
        """Test finding non-existent user by ID"""
        result = repository.find_by_id(999)
        assert result is None
    
    def test_find_by_username_success(self, repository, sample_user):
        """Test finding user by username"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Find by username
        found_user = repository.find_by_username("testuser")
        assert found_user is not None
        assert found_user.username == "testuser"
        assert found_user.role == "cashier"
    
    def test_find_by_username_not_found(self, repository):
        """Test finding non-existent user by username"""
        result = repository.find_by_username("nonexistent")
        assert result is None
    
    def test_find_by_username_empty(self, repository):
        """Test finding user with empty username"""
        result = repository.find_by_username("")
        assert result is None
        
        result = repository.find_by_username(None)
        assert result is None
    
    def test_find_all(self, repository, sample_user, admin_user):
        """Test finding all users"""
        # Save multiple users
        repository.save(sample_user)
        repository.save(admin_user)
        
        # Find all
        all_users = repository.find_all()
        assert len(all_users) >= 2  # At least our 2 users (plus default admin)
        
        # Check they are sorted by username
        usernames = [u.username for u in all_users]
        assert usernames == sorted(usernames)
    
    def test_find_active_users(self, repository, sample_user):
        """Test finding active users"""
        # Save active user
        repository.save(sample_user)
        
        # Create and save inactive user
        inactive_user = User(
            username="inactive",
            role="cashier",
            is_active=False
        )
        inactive_user.set_password("password123")
        repository.save(inactive_user)
        
        # Find active users
        active_users = repository.find_active_users()
        active_usernames = [u.username for u in active_users]
        
        assert "testuser" in active_usernames
        assert "inactive" not in active_usernames
    
    def test_find_by_role(self, repository, sample_user, admin_user):
        """Test finding users by role"""
        # Save users with different roles
        repository.save(sample_user)
        repository.save(admin_user)
        
        # Find cashiers
        cashiers = repository.find_by_role("cashier")
        cashier_usernames = [u.username for u in cashiers]
        assert "testuser" in cashier_usernames
        
        # Find admins
        admins = repository.find_by_role("admin")
        admin_usernames = [u.username for u in admins]
        assert "admin" in admin_usernames
    
    def test_authenticate_success(self, repository, sample_user):
        """Test successful authentication"""
        # Save user first
        repository.save(sample_user)
        
        # Authenticate
        authenticated_user = repository.authenticate("testuser", "password123")
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"
        assert authenticated_user.last_login is not None
    
    def test_authenticate_wrong_password(self, repository, sample_user):
        """Test authentication with wrong password"""
        # Save user first
        repository.save(sample_user)
        
        # Try to authenticate with wrong password
        result = repository.authenticate("testuser", "wrongpassword")
        assert result is None
    
    def test_authenticate_nonexistent_user(self, repository):
        """Test authentication with non-existent user"""
        result = repository.authenticate("nonexistent", "password123")
        assert result is None
    
    def test_authenticate_inactive_user(self, repository, sample_user):
        """Test authentication with inactive user"""
        # Save user and deactivate
        saved_user = repository.save(sample_user)
        repository.deactivate_user(saved_user.id)
        
        # Try to authenticate
        result = repository.authenticate("testuser", "password123")
        assert result is None
    
    def test_update_user_success(self, repository, sample_user):
        """Test successful user update"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Update user
        saved_user.username = "updateduser"
        saved_user.role = "admin"
        
        result = repository.update(saved_user)
        assert result is True
        
        # Verify update
        updated_user = repository.find_by_id(saved_user.id)
        assert updated_user.username == "updateduser"
        assert updated_user.role == "admin"
    
    def test_update_user_without_id(self, repository, sample_user):
        """Test updating user without ID fails"""
        sample_user.id = None
        result = repository.update(sample_user)
        assert result is False
    
    def test_update_nonexistent_user(self, repository, sample_user):
        """Test updating non-existent user"""
        sample_user.id = 999
        result = repository.update(sample_user)
        assert result is False
    
    def test_update_password_success(self, repository, sample_user):
        """Test successful password update"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Update password
        result = repository.update_password(saved_user.id, "newpassword123")
        assert result is True
        
        # Verify new password works
        authenticated_user = repository.authenticate("testuser", "newpassword123")
        assert authenticated_user is not None
        
        # Verify old password doesn't work
        old_auth = repository.authenticate("testuser", "password123")
        assert old_auth is None
    
    def test_update_password_weak(self, repository, sample_user):
        """Test updating password with weak password fails"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Try to update with weak password
        result = repository.update_password(saved_user.id, "123")  # Too short
        assert result is False
    
    def test_update_password_nonexistent_user(self, repository):
        """Test updating password for non-existent user"""
        result = repository.update_password(999, "newpassword123")
        assert result is False
    
    def test_update_last_login(self, repository, sample_user):
        """Test updating last login timestamp"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Update last login
        result = repository.update_last_login(saved_user.id)
        assert result is True
        
        # Verify last login was updated
        updated_user = repository.find_by_id(saved_user.id)
        assert updated_user.last_login is not None
    
    def test_deactivate_user_success(self, repository, sample_user):
        """Test successful user deactivation"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        assert saved_user.is_active is True
        
        # Deactivate user
        result = repository.deactivate_user(saved_user.id)
        assert result is True
        
        # Verify deactivation
        deactivated_user = repository.find_by_id(saved_user.id)
        assert deactivated_user.is_active is False
    
    def test_activate_user_success(self, repository, sample_user):
        """Test successful user activation"""
        # Save user and deactivate first
        saved_user = repository.save(sample_user)
        repository.deactivate_user(saved_user.id)
        
        # Activate user
        result = repository.activate_user(saved_user.id)
        assert result is True
        
        # Verify activation
        activated_user = repository.find_by_id(saved_user.id)
        assert activated_user.is_active is True
    
    def test_delete_user_success(self, repository, sample_user):
        """Test successful user deletion"""
        # Save user first
        saved_user = repository.save(sample_user)
        assert saved_user is not None
        
        # Delete user
        result = repository.delete(saved_user.id)
        assert result is True
        
        # Verify deletion
        deleted_user = repository.find_by_id(saved_user.id)
        assert deleted_user is None
    
    def test_delete_nonexistent_user(self, repository):
        """Test deleting non-existent user"""
        result = repository.delete(999)
        assert result is False
    
    def test_get_total_users_count(self, repository, sample_user):
        """Test getting total users count"""
        # Get initial count (should include default admin)
        initial_count = repository.get_total_users_count()
        
        # Save user
        repository.save(sample_user)
        
        # Count should increase by 1
        new_count = repository.get_total_users_count()
        assert new_count == initial_count + 1
    
    def test_get_active_users_count(self, repository, sample_user):
        """Test getting active users count"""
        # Get initial count
        initial_count = repository.get_active_users_count()
        
        # Save active user
        repository.save(sample_user)
        
        # Save inactive user
        inactive_user = User(
            username="inactive",
            role="cashier",
            is_active=False
        )
        inactive_user.set_password("password123")
        repository.save(inactive_user)
        
        # Active count should increase by 1 (only active user)
        new_count = repository.get_active_users_count()
        assert new_count == initial_count + 1
    
    def test_username_exists(self, repository, sample_user):
        """Test checking username existence"""
        # Initially should not exist
        exists = repository.username_exists("testuser")
        assert exists is False
        
        # Save user
        saved_user = repository.save(sample_user)
        
        # Now should exist
        exists = repository.username_exists("testuser")
        assert exists is True
        
        # Should not exist when excluding the user's own ID
        exists = repository.username_exists("testuser", exclude_user_id=saved_user.id)
        assert exists is False