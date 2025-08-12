"""
User data model for Medical Store Management Application
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import hashlib
import re
from .base import BaseModel


@dataclass
class User(BaseModel):
    """User model with authentication and role-based access"""
    
    username: str = ""
    password_hash: str = ""
    role: str = "cashier"  # 'admin' or 'cashier'
    is_active: bool = True
    last_login: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    def validate(self) -> List[str]:
        """
        Validate user data
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Username validation
        if not self.username or not self.username.strip():
            errors.append("Username is required")
        elif len(self.username.strip()) < 3:
            errors.append("Username must be at least 3 characters long")
        elif len(self.username.strip()) > 50:
            errors.append("Username must be less than 50 characters")
        elif not re.match(r'^[a-zA-Z0-9_]+$', self.username.strip()):
            errors.append("Username can only contain letters, numbers, and underscores")
        
        # Password hash validation
        if not self.password_hash:
            errors.append("Password hash is required")
        
        # Role validation
        valid_roles = ["admin", "cashier"]
        if self.role not in valid_roles:
            errors.append(f"Role must be one of: {', '.join(valid_roles)}")
        
        # Full name validation (if provided)
        if self.full_name and len(self.full_name.strip()) > 100:
            errors.append("Full name must be less than 100 characters")
        
        # Email validation (if provided)
        if self.email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email.strip()):
                errors.append("Invalid email format")
            elif len(self.email.strip()) > 100:
                errors.append("Email must be less than 100 characters")
        
        # Phone validation (if provided)
        if self.phone:
            # Remove spaces and dashes for validation
            clean_phone = re.sub(r'[\s-]', '', self.phone)
            if not re.match(r'^\+?[1-9]\d{1,14}$', clean_phone):
                errors.append("Invalid phone number format")
        
        return errors    

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def set_password(self, password: str) -> bool:
        """
        Set user password (hashes automatically)
        
        Args:
            password: Plain text password
            
        Returns:
            True if password set successfully, False if invalid
        """
        if self.validate_password_strength(password):
            self.password_hash = self.hash_password(password)
            self.update_timestamp()
            return True
        return False
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return self.password_hash == self.hash_password(password)
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            True if password meets requirements, False otherwise
        """
        if len(password) < 6:
            return False
        if len(password) > 128:
            return False
        # At least one letter and one number
        if not re.search(r'[a-zA-Z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    def is_admin(self) -> bool:
        """
        Check if user has admin role
        
        Returns:
            True if user is admin, False otherwise
        """
        return self.role == "admin"
    
    def is_cashier(self) -> bool:
        """
        Check if user has cashier role
        
        Returns:
            True if user is cashier, False otherwise
        """
        return self.role == "cashier" 
   
    def can_access_feature(self, feature: str) -> bool:
        """
        Check if user can access a specific feature
        
        Args:
            feature: Feature name to check access for
            
        Returns:
            True if user can access feature, False otherwise
        """
        if not self.is_active:
            return False
        
        # Admin can access everything
        if self.is_admin():
            return True
        
        # Cashier permissions
        cashier_features = [
            "billing",
            "medicine_view",
            "dashboard_view",
            "sales_view"
        ]
        
        return feature in cashier_features
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now().isoformat()
        self.update_timestamp()
    
    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        self.update_timestamp()
    
    def activate(self):
        """Activate user account"""
        self.is_active = True
        self.update_timestamp()
    
    def get_display_name(self) -> str:
        """
        Get display name for UI
        
        Returns:
            Full name if available, otherwise username
        """
        return self.full_name.strip() if self.full_name else self.username
    
    def get_role_display(self) -> str:
        """
        Get formatted role name for display
        
        Returns:
            Capitalized role name
        """
        return self.role.capitalize()
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding password hash for security"""
        data = super().to_dict()
        # Remove password hash from dictionary for security
        data.pop('password_hash', None)
        return data
    
    def to_safe_dict(self) -> dict:
        """
        Convert to dictionary with only safe fields for API responses
        
        Returns:
            Dictionary with safe user data
        """
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'full_name': self.full_name,
            'email': self.email,
            'last_login': self.last_login,
            'created_at': self.created_at
        }
    
    def __str__(self) -> str:
        """String representation of user"""
        return f"{self.get_display_name()} ({self.role})"