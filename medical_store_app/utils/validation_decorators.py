"""
Validation decorators for Medical Store Management Application
Provides reusable validation decorators for form fields
"""

from typing import Callable, Any, Optional
from datetime import date
from PySide6.QtCore import QDate
import re


class Validation:
    """Validation decorators for form fields"""
    
    @staticmethod
    def required(error_msg: str = "This field is required"):
        """Decorator to validate required fields"""
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                # Handle different value types
                if value is None:
                    return False, error_msg
                
                # For strings, check if not empty after stripping
                if isinstance(value, str) and not value.strip():
                    return False, error_msg
                
                # For other types, check if falsy
                if not value and not isinstance(value, (int, float)):
                    return False, error_msg
                
                # Call the original validation function
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def min_length(length: int, error_msg: Optional[str] = None):
        """Decorator to validate minimum length"""
        if error_msg is None:
            error_msg = f"Must be at least {length} characters"
            
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, str) and len(value.strip()) < length:
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def max_length(length: int, error_msg: Optional[str] = None):
        """Decorator to validate maximum length"""
        if error_msg is None:
            error_msg = f"Must be no more than {length} characters"
            
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, str) and len(value.strip()) > length:
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def min_value(min_val: float, error_msg: Optional[str] = None):
        """Decorator to validate minimum numeric value"""
        if error_msg is None:
            error_msg = f"Must be at least {min_val}"
            
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, (int, float)) and value < min_val:
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def max_value(max_val: float, error_msg: Optional[str] = None):
        """Decorator to validate maximum numeric value"""
        if error_msg is None:
            error_msg = f"Must be no more than {max_val}"
            
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, (int, float)) and value > max_val:
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def date_future(error_msg: Optional[str] = None):
        """Decorator to validate date is in the future"""
        if error_msg is None:
            error_msg = "Date must be in the future"
            
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, QDate):
                    if value.toPython() <= date.today():
                        return False, error_msg
                elif isinstance(value, date):
                    if value <= date.today():
                        return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def pattern(regex: str, error_msg: str):
        """Decorator to validate against a regex pattern"""
        compiled_regex = re.compile(regex)
        
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, str) and not compiled_regex.match(value.strip()):
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def email(error_msg: Optional[str] = None):
        """Decorator to validate email format"""
        if error_msg is None:
            error_msg = "Invalid email format"
            
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        compiled_regex = re.compile(email_regex)
        
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, str) and not compiled_regex.match(value.strip()):
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
    
    @staticmethod
    def numeric(error_msg: Optional[str] = None):
        """Decorator to validate numeric values"""
        if error_msg is None:
            error_msg = "Must be a valid number"
            
        def decorator(func: Callable) -> Callable:
            def wrapper(self, value: Any) -> tuple[bool, str]:
                if isinstance(value, str):
                    try:
                        float(value.strip())
                    except ValueError:
                        return False, error_msg
                elif not isinstance(value, (int, float)):
                    return False, error_msg
                return func(self, value)
            return wrapper
        return decorator
