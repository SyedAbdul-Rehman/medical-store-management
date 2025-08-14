"""
Authentication Manager for Medical Store Management Application
Handles user authentication, session management, and access control
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timedelta

from ..models.user import User
from ..repositories.user_repository import UserRepository


class AuthManager:
    """Manager class for authentication and user access control"""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize authentication manager
        
        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository
        self.logger = logging.getLogger(__name__)
        self._current_user: Optional[User] = None
        self._session_timeout_minutes = 480  # 8 hours default
        self._last_activity: Optional[datetime] = None
        self._failed_login_attempts: Dict[str, int] = {}
        self._max_failed_attempts = 5
        self._lockout_duration_minutes = 30
        self._locked_accounts: Dict[str, datetime] = {}
    
    # Authentication Methods
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user and start session
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message, user_instance)
        """
        try:
            # Validate input
            if not username or not username.strip():
                return False, "Username is required", None
            
            if not password:
                return False, "Password is required", None
            
            username = username.strip()
            
            # Check if account is locked
            if self._is_account_locked(username):
                remaining_time = self._get_lockout_remaining_time(username)
                return False, f"Account locked. Try again in {remaining_time} minutes", None
            
            # Attempt authentication
            user = self.user_repository.authenticate(username, password)
            
            if user:
                # Reset failed attempts on successful login
                self._failed_login_attempts.pop(username, None)
                self._locked_accounts.pop(username, None)
                
                # Start session
                self._current_user = user
                self._last_activity = datetime.now()
                
                success_msg = f"Login successful for {user.get_display_name()}"
                self.logger.info(f"User logged in: {username} (ID: {user.id})")
                return True, success_msg, user
            else:
                # Track failed attempt
                self._track_failed_login(username)
                
                # Check if account should be locked
                failed_count = self._failed_login_attempts.get(username, 0)
                if failed_count >= self._max_failed_attempts:
                    self._lock_account(username)
                    return False, f"Too many failed attempts. Account locked for {self._lockout_duration_minutes} minutes", None
                
                remaining_attempts = self._max_failed_attempts - failed_count
                return False, f"Invalid credentials. {remaining_attempts} attempts remaining", None
                
        except Exception as e:
            error_msg = f"Login error: {str(e)}"
            self.logger.error(error_msg)
            return False, "Login failed due to system error", None
    
    def logout(self) -> Tuple[bool, str]:
        """
        End current user session
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if self._current_user:
                username = self._current_user.username
                self._current_user = None
                self._last_activity = None
                self.logger.info(f"User logged out: {username}")
                return True, "Logout successful"
            else:
                return False, "No active session to logout"
                
        except Exception as e:
            error_msg = f"Logout error: {str(e)}"
            self.logger.error(error_msg)
            return False, "Logout failed due to system error"
    
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in
        
        Returns:
            True if user is logged in and session is valid
        """
        try:
            if not self._current_user or not self._last_activity:
                return False
            
            # Check session timeout
            if self._is_session_expired():
                self.logout()
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking login status: {str(e)}")
            return False
    
    def get_current_user(self) -> Optional[User]:
        """
        Get current logged-in user
        
        Returns:
            Current user instance if logged in, None otherwise
        """
        if self.is_logged_in():
            return self._current_user
        return None
    
    def refresh_session(self) -> bool:
        """
        Refresh current session activity timestamp
        
        Returns:
            True if session refreshed successfully
        """
        try:
            if self.is_logged_in():
                self._last_activity = datetime.now()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error refreshing session: {str(e)}")
            return False
    
    # Access Control Methods
    
    def has_permission(self, feature: str) -> bool:
        """
        Check if current user has permission for a feature
        
        Args:
            feature: Feature name to check
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            current_user = self.get_current_user()
            if not current_user:
                return False
            
            return current_user.can_access_feature(feature)
            
        except Exception as e:
            self.logger.error(f"Error checking permission for {feature}: {str(e)}")
            return False
    
    def is_admin(self) -> bool:
        """
        Check if current user is admin
        
        Returns:
            True if current user is admin, False otherwise
        """
        current_user = self.get_current_user()
        return current_user.is_admin() if current_user else False
    
    def is_cashier(self) -> bool:
        """
        Check if current user is cashier
        
        Returns:
            True if current user is cashier, False otherwise
        """
        current_user = self.get_current_user()
        return current_user.is_cashier() if current_user else False
    
    def require_admin(self) -> Tuple[bool, str]:
        """
        Check if current user has admin privileges
        
        Returns:
            Tuple of (has_access, message)
        """
        if not self.is_logged_in():
            return False, "Authentication required"
        
        if not self.is_admin():
            return False, "Admin privileges required"
        
        return True, "Access granted"
    
    def require_permission(self, feature: str) -> Tuple[bool, str]:
        """
        Check if current user has permission for specific feature
        
        Args:
            feature: Feature name to check
            
        Returns:
            Tuple of (has_access, message)
        """
        if not self.is_logged_in():
            return False, "Authentication required"
        
        if not self.has_permission(feature):
            return False, f"Permission denied for {feature}"
        
        return True, "Access granted"
    
    # User Management Methods (Admin only)
    
    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
        """
        Create new user (admin only)
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Tuple of (success, message, user_instance)
        """
        try:
            # Check admin permission
            has_access, access_msg = self.require_admin()
            if not has_access:
                return False, access_msg, None
            
            # Validate required fields
            username = user_data.get('username', '').strip()
            password = user_data.get('password', '')
            role = user_data.get('role', 'cashier')
            
            if not username:
                return False, "Username is required", None
            
            if not password:
                return False, "Password is required", None
            
            # Check if username already exists
            if self.user_repository.username_exists(username):
                return False, f"Username '{username}' already exists", None
            
            # Validate password strength
            if not User.validate_password_strength(password):
                return False, "Password must be at least 6 characters with letters and numbers", None
            
            # Create user instance
            user = User(
                username=username,
                role=role,
                is_active=user_data.get('is_active', True),
                full_name=user_data.get('full_name'),
                email=user_data.get('email'),
                phone=user_data.get('phone')
            )
            
            # Set password
            if not user.set_password(password):
                return False, "Failed to set password", None
            
            # Save user
            saved_user = self.user_repository.save(user)
            if saved_user:
                success_msg = f"User '{saved_user.username}' created successfully"
                self.logger.info(f"User created by {self._current_user.username}: {saved_user.username}")
                return True, success_msg, saved_user
            else:
                return False, "Failed to save user to database", None
                
        except Exception as e:
            error_msg = f"Error creating user: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
        """
        Update existing user (admin only)
        
        Args:
            user_id: ID of user to update
            user_data: Dictionary containing updated user information
            
        Returns:
            Tuple of (success, message, user_instance)
        """
        try:
            # Check admin permission
            has_access, access_msg = self.require_admin()
            if not has_access:
                return False, access_msg, None
            
            # Find existing user
            existing_user = self.user_repository.find_by_id(user_id)
            if not existing_user:
                return False, f"User with ID {user_id} not found", None
            
            # Update user data
            if 'username' in user_data:
                new_username = user_data['username'].strip()
                if new_username != existing_user.username:
                    if self.user_repository.username_exists(new_username, user_id):
                        return False, f"Username '{new_username}' already exists", None
                    existing_user.username = new_username
            
            if 'role' in user_data:
                existing_user.role = user_data['role']
            
            if 'is_active' in user_data:
                existing_user.is_active = user_data['is_active']
            
            if 'full_name' in user_data:
                existing_user.full_name = user_data['full_name']
            
            if 'email' in user_data:
                existing_user.email = user_data['email']
            
            if 'phone' in user_data:
                existing_user.phone = user_data['phone']
            
            # Update password if provided
            if 'password' in user_data and user_data['password']:
                if not existing_user.set_password(user_data['password']):
                    return False, "Password must be at least 6 characters with letters and numbers", None
            
            # Save updated user
            if self.user_repository.update(existing_user):
                success_msg = f"User '{existing_user.username}' updated successfully"
                self.logger.info(f"User updated by {self._current_user.username}: {existing_user.username}")
                return True, success_msg, existing_user
            else:
                return False, "Failed to update user in database", None
                
        except Exception as e:
            error_msg = f"Error updating user: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Delete user (admin only)
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check admin permission
            has_access, access_msg = self.require_admin()
            if not has_access:
                return False, access_msg
            
            # Prevent deleting current user
            if self._current_user and self._current_user.id == user_id:
                return False, "Cannot delete currently logged-in user"
            
            # Find user to get username for logging
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False, f"User with ID {user_id} not found"
            
            # Delete user
            if self.user_repository.delete(user_id):
                success_msg = f"User '{user.username}' deleted successfully"
                self.logger.info(f"User deleted by {self._current_user.username}: {user.username}")
                return True, success_msg
            else:
                return False, "Failed to delete user from database"
                
        except Exception as e:
            error_msg = f"Error deleting user: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_all_users(self) -> List[User]:
        """
        Get all users (admin only)
        
        Returns:
            List of all users if admin, empty list otherwise
        """
        try:
            if not self.is_admin():
                return []
            
            return self.user_repository.find_all()
            
        except Exception as e:
            self.logger.error(f"Error getting all users: {str(e)}")
            return []
    
    def get_all_users_for_startup(self) -> List[User]:
        """
        Get all users for startup check (no authentication required)
        This is used only for checking if default users exist during startup
        
        Returns:
            List of all users
        """
        try:
            return self.user_repository.find_all()
            
        except Exception as e:
            self.logger.error(f"Error getting users for startup: {str(e)}")
            return []
    
    def get_users_by_role(self, role: str) -> List[User]:
        """
        Get users by role (admin only)
        
        Args:
            role: Role to filter by
            
        Returns:
            List of users with specified role if admin, empty list otherwise
        """
        try:
            if not self.is_admin():
                return []
            
            return self.user_repository.find_by_role(role)
            
        except Exception as e:
            self.logger.error(f"Error getting users by role {role}: {str(e)}")
            return []
    
    def activate_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Activate user account (admin only)
        
        Args:
            user_id: ID of user to activate
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check admin permission
            has_access, access_msg = self.require_admin()
            if not has_access:
                return False, access_msg
            
            if self.user_repository.activate_user(user_id):
                return True, "User activated successfully"
            else:
                return False, "Failed to activate user"
                
        except Exception as e:
            error_msg = f"Error activating user: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def deactivate_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Deactivate user account (admin only)
        
        Args:
            user_id: ID of user to deactivate
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check admin permission
            has_access, access_msg = self.require_admin()
            if not has_access:
                return False, access_msg
            
            # Prevent deactivating current user
            if self._current_user and self._current_user.id == user_id:
                return False, "Cannot deactivate currently logged-in user"
            
            if self.user_repository.deactivate_user(user_id):
                return True, "User deactivated successfully"
            else:
                return False, "Failed to deactivate user"
                
        except Exception as e:
            error_msg = f"Error deactivating user: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change current user's password
        
        Args:
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.is_logged_in():
                return False, "Authentication required"
            
            # Verify current password
            if not self._current_user.verify_password(current_password):
                return False, "Current password is incorrect"
            
            # Validate new password strength
            if not User.validate_password_strength(new_password):
                return False, "New password must be at least 6 characters with letters and numbers"
            
            # Update password
            if self.user_repository.update_password(self._current_user.id, new_password):
                # Update current user's password hash
                self._current_user.password_hash = User.hash_password(new_password)
                self.logger.info(f"Password changed for user: {self._current_user.username}")
                return True, "Password changed successfully"
            else:
                return False, "Failed to update password"
                
        except Exception as e:
            error_msg = f"Error changing password: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    # Session Management Methods
    
    def set_session_timeout(self, minutes: int) -> bool:
        """
        Set session timeout duration
        
        Args:
            minutes: Timeout duration in minutes
            
        Returns:
            True if set successfully
        """
        try:
            if minutes < 1:
                return False
            
            self._session_timeout_minutes = minutes
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting session timeout: {str(e)}")
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information
        
        Returns:
            Dictionary with session information
        """
        try:
            if not self.is_logged_in():
                return {'logged_in': False}
            
            time_remaining = self._get_session_time_remaining()
            
            return {
                'logged_in': True,
                'user': self._current_user.to_safe_dict(),
                'last_activity': self._last_activity.isoformat() if self._last_activity else None,
                'session_timeout_minutes': self._session_timeout_minutes,
                'time_remaining_minutes': time_remaining
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session info: {str(e)}")
            return {'logged_in': False}
    
    # Private Helper Methods
    
    def _is_session_expired(self) -> bool:
        """Check if current session has expired"""
        if not self._last_activity:
            return True
        
        timeout_delta = timedelta(minutes=self._session_timeout_minutes)
        return datetime.now() - self._last_activity > timeout_delta
    
    def _get_session_time_remaining(self) -> int:
        """Get remaining session time in minutes"""
        if not self._last_activity:
            return 0
        
        timeout_delta = timedelta(minutes=self._session_timeout_minutes)
        remaining = timeout_delta - (datetime.now() - self._last_activity)
        return max(0, int(remaining.total_seconds() / 60))
    
    def _track_failed_login(self, username: str):
        """Track failed login attempt"""
        self._failed_login_attempts[username] = self._failed_login_attempts.get(username, 0) + 1
        self.logger.warning(f"Failed login attempt for {username}. Count: {self._failed_login_attempts[username]}")
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if username not in self._locked_accounts:
            return False
        
        lock_time = self._locked_accounts[username]
        lockout_delta = timedelta(minutes=self._lockout_duration_minutes)
        
        if datetime.now() - lock_time > lockout_delta:
            # Lockout period expired, remove lock
            self._locked_accounts.pop(username, None)
            self._failed_login_attempts.pop(username, None)
            return False
        
        return True
    
    def _lock_account(self, username: str):
        """Lock account due to too many failed attempts"""
        self._locked_accounts[username] = datetime.now()
        self.logger.warning(f"Account locked due to failed attempts: {username}")
    
    def _get_lockout_remaining_time(self, username: str) -> int:
        """Get remaining lockout time in minutes"""
        if username not in self._locked_accounts:
            return 0
        
        lock_time = self._locked_accounts[username]
        lockout_delta = timedelta(minutes=self._lockout_duration_minutes)
        remaining = lockout_delta - (datetime.now() - lock_time)
        return max(0, int(remaining.total_seconds() / 60))
    
    # Configuration Methods
    
    def set_max_failed_attempts(self, max_attempts: int) -> bool:
        """Set maximum failed login attempts before lockout"""
        if max_attempts < 1:
            return False
        self._max_failed_attempts = max_attempts
        return True
    
    def set_lockout_duration(self, minutes: int) -> bool:
        """Set account lockout duration in minutes"""
        if minutes < 1:
            return False
        self._lockout_duration_minutes = minutes
        return True
    
    def get_max_failed_attempts(self) -> int:
        """Get maximum failed login attempts"""
        return self._max_failed_attempts
    
    def get_lockout_duration(self) -> int:
        """Get lockout duration in minutes"""
        return self._lockout_duration_minutes