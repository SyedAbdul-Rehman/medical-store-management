"""
User repository for Medical Store Management Application
Handles all database operations for user data and authentication
"""

import sqlite3
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..config.database import DatabaseManager
from ..models.user import User


class UserRepository:
    """Repository class for user data access operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize user repository
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def save(self, user: User) -> Optional[User]:
        """
        Save a new user to the database
        
        Args:
            user: User instance to save
            
        Returns:
            User instance with assigned ID if successful, None otherwise
        """
        try:
            # Validate user data
            validation_errors = user.validate()
            if validation_errors:
                self.logger.error(f"User validation failed: {validation_errors}")
                return None
            
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (
                        username, password_hash, role, is_active, 
                        created_at, last_login
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user.username.strip(),
                    user.password_hash,
                    user.role,
                    user.is_active,
                    user.created_at,
                    user.last_login
                ))
                
                user.id = cursor.lastrowid
                self.logger.info(f"User saved successfully: {user.username} (ID: {user.id})")
                return user
                
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                self.logger.error(f"Username already exists: {user.username}")
            else:
                self.logger.error(f"Database integrity error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to save user: {e}")
            return None
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find user by ID
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            
            if row:
                return self._row_to_user(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find user by ID {user_id}: {e}")
            return None
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            if not username or not username.strip():
                return None
                
            row = self.db_manager.execute_single(
                "SELECT * FROM users WHERE username = ?",
                (username.strip(),)
            )
            
            if row:
                return self._row_to_user(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find user by username {username}: {e}")
            return None
    
    def find_all(self) -> List[User]:
        """
        Get all users from database
        
        Returns:
            List of all user instances
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT * FROM users ORDER BY username ASC"
            )
            
            return [self._row_to_user(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve all users: {e}")
            return []
    
    def find_active_users(self) -> List[User]:
        """
        Get all active users from database
        
        Returns:
            List of active user instances
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT * FROM users WHERE is_active = 1 ORDER BY username ASC"
            )
            
            return [self._row_to_user(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve active users: {e}")
            return []
    
    def find_by_role(self, role: str) -> List[User]:
        """
        Find users by role
        
        Args:
            role: Role to filter by ('admin' or 'cashier')
            
        Returns:
            List of users with the specified role
        """
        try:
            if not role or role not in ['admin', 'cashier']:
                return []
            
            rows = self.db_manager.execute_query(
                "SELECT * FROM users WHERE role = ? ORDER BY username ASC",
                (role,)
            )
            
            return [self._row_to_user(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to find users by role '{role}': {e}")
            return []
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        try:
            user = self.find_by_username(username)
            if user and user.is_active and user.verify_password(password):
                # Update last login
                user.update_last_login()
                self.update_last_login(user.id)
                self.logger.info(f"User authenticated successfully: {username}")
                return user
            else:
                self.logger.warning(f"Authentication failed for username: {username}")
                return None
                
        except Exception as e:
            self.logger.error(f"Authentication error for username {username}: {e}")
            return None
    
    def update(self, user: User) -> bool:
        """
        Update existing user in database
        
        Args:
            user: User instance with updated data
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if not user.id:
                self.logger.error("Cannot update user without ID")
                return False
            
            # Validate user data
            validation_errors = user.validate()
            if validation_errors:
                self.logger.error(f"User validation failed: {validation_errors}")
                return False
            
            # Update timestamp
            user.update_timestamp()
            
            rows_affected = self.db_manager.execute_update("""
                UPDATE users SET
                    username = ?, password_hash = ?, role = ?, is_active = ?,
                    last_login = ?
                WHERE id = ?
            """, (
                user.username.strip(),
                user.password_hash,
                user.role,
                user.is_active,
                user.last_login,
                user.id
            ))
            
            if rows_affected > 0:
                self.logger.info(f"User updated successfully: {user.username} (ID: {user.id})")
                return True
            else:
                self.logger.warning(f"No user found with ID {user.id}")
                return False
                
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                self.logger.error(f"Username already exists: {user.username}")
            else:
                self.logger.error(f"Database integrity error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to update user: {e}")
            return False
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user password
        
        Args:
            user_id: ID of user to update
            new_password: New plain text password
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Validate password strength
            if not User.validate_password_strength(new_password):
                self.logger.error("Password does not meet strength requirements")
                return False
            
            # Hash the new password
            password_hash = User.hash_password(new_password)
            updated_at = datetime.now().isoformat()
            
            rows_affected = self.db_manager.execute_update("""
                UPDATE users SET password_hash = ? WHERE id = ?
            """, (password_hash, user_id))
            
            if rows_affected > 0:
                self.logger.info(f"Password updated successfully for user ID {user_id}")
                return True
            else:
                self.logger.warning(f"No user found with ID {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update password for user ID {user_id}: {e}")
            return False
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_id: ID of user to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            last_login = datetime.now().isoformat()
            
            rows_affected = self.db_manager.execute_update("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (last_login, user_id))
            
            if rows_affected > 0:
                return True
            else:
                self.logger.warning(f"No user found with ID {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update last login for user ID {user_id}: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate user account
        
        Args:
            user_id: ID of user to deactivate
            
        Returns:
            True if deactivation successful, False otherwise
        """
        try:
            rows_affected = self.db_manager.execute_update("""
                UPDATE users SET is_active = 0 WHERE id = ?
            """, (user_id,))
            
            if rows_affected > 0:
                self.logger.info(f"User deactivated successfully (ID: {user_id})")
                return True
            else:
                self.logger.warning(f"No user found with ID {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to deactivate user with ID {user_id}: {e}")
            return False
    
    def activate_user(self, user_id: int) -> bool:
        """
        Activate user account
        
        Args:
            user_id: ID of user to activate
            
        Returns:
            True if activation successful, False otherwise
        """
        try:
            rows_affected = self.db_manager.execute_update("""
                UPDATE users SET is_active = 1 WHERE id = ?
            """, (user_id,))
            
            if rows_affected > 0:
                self.logger.info(f"User activated successfully (ID: {user_id})")
                return True
            else:
                self.logger.warning(f"No user found with ID {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to activate user with ID {user_id}: {e}")
            return False
    
    def delete(self, user_id: int) -> bool:
        """
        Delete user from database
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            rows_affected = self.db_manager.execute_update(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            
            if rows_affected > 0:
                self.logger.info(f"User deleted successfully (ID: {user_id})")
                return True
            else:
                self.logger.warning(f"No user found with ID {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete user with ID {user_id}: {e}")
            return False
    
    def get_total_users_count(self) -> int:
        """
        Get total count of users
        
        Returns:
            Total number of user records
        """
        try:
            row = self.db_manager.execute_single("SELECT COUNT(*) as count FROM users")
            return row['count'] if row else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get total users count: {e}")
            return 0
    
    def get_active_users_count(self) -> int:
        """
        Get count of active users
        
        Returns:
            Number of active user records
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT COUNT(*) as count FROM users WHERE is_active = 1"
            )
            return row['count'] if row else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get active users count: {e}")
            return 0
    
    def username_exists(self, username: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        Check if username already exists
        
        Args:
            username: Username to check
            exclude_user_id: User ID to exclude from check (for updates)
            
        Returns:
            True if username exists, False otherwise
        """
        try:
            if exclude_user_id:
                row = self.db_manager.execute_single("""
                    SELECT COUNT(*) as count FROM users 
                    WHERE username = ? AND id != ?
                """, (username.strip(), exclude_user_id))
            else:
                row = self.db_manager.execute_single("""
                    SELECT COUNT(*) as count FROM users WHERE username = ?
                """, (username.strip(),))
            
            return row['count'] > 0 if row else False
            
        except Exception as e:
            self.logger.error(f"Failed to check username existence: {e}")
            return True  # Return True on error to be safe
    
    def _row_to_user(self, row: sqlite3.Row) -> User:
        """
        Convert database row to User instance
        
        Args:
            row: Database row
            
        Returns:
            User instance
        """
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=row['role'],
            is_active=bool(row['is_active']),
            last_login=row['last_login'],
            created_at=row['created_at']
        )