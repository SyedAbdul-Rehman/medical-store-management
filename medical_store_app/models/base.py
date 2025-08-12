"""
Base model class with common functionality for Medical Store Management Application
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


@dataclass
class BaseModel(ABC):
    """Base model class with common functionality for all data models"""
    
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization hook for additional setup"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in value
                ]
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create model instance from dictionary
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model instance
        """
        # Filter out keys that don't exist in the dataclass
        if hasattr(cls, '__dataclass_fields__'):
            valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        else:
            filtered_data = data
        return cls(**filtered_data)
    
    def to_json(self) -> str:
        """
        Convert model instance to JSON string
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str):
        """
        Create model instance from JSON string
        
        Args:
            json_str: JSON string containing model data
            
        Returns:
            Model instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    @abstractmethod
    def validate(self) -> List[str]:
        """
        Validate model data
        
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    def is_valid(self) -> bool:
        """
        Check if model data is valid
        
        Returns:
            True if valid, False otherwise
        """
        return len(self.validate()) == 0
    
    def get_validation_errors(self) -> List[str]:
        """
        Get validation error messages
        
        Returns:
            List of validation error messages
        """
        return self.validate()
    
    def __str__(self) -> str:
        """String representation of the model"""
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the model"""
        return f"{self.__class__.__name__}({self.to_dict()})"