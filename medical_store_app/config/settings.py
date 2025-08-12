"""
Application settings management for Medical Store Management Application
Handles configuration loading, saving, and default values
"""

import logging
from typing import Any, Dict, Optional
from pathlib import Path


class AppSettings:
    """Manages application settings and configuration"""
    
    def __init__(self):
        """Initialize settings manager"""
        self.logger = logging.getLogger(__name__)
        self._settings_cache: Dict[str, Any] = {}
        self._db_manager = None
        
    def _get_db_manager(self):
        """Get database manager instance (lazy loading to avoid circular imports)"""
        if self._db_manager is None:
            from .database import DatabaseManager
            self._db_manager = DatabaseManager()
        return self._db_manager
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value by key
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        # Check cache first
        if key in self._settings_cache:
            return self._settings_cache[key]
        
        try:
            db_manager = self._get_db_manager()
            result = db_manager.execute_single(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            
            if result:
                value = result['value']
                # Cache the value
                self._settings_cache[key] = value
                return value
            else:
                self.logger.warning(f"Setting '{key}' not found, using default: {default}")
                return default
                
        except Exception as e:
            self.logger.error(f"Failed to get setting '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any, description: str = "") -> bool:
        """
        Set setting value
        
        Args:
            key: Setting key
            value: Setting value
            description: Setting description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db_manager = self._get_db_manager()
            
            # Convert value to string for storage
            str_value = str(value)
            
            # Update or insert setting
            db_manager.execute_update("""
                INSERT OR REPLACE INTO settings (key, value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, str_value, description))
            
            # Update cache
            self._settings_cache[key] = str_value
            
            self.logger.info(f"Setting '{key}' updated to '{str_value}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set setting '{key}': {e}")
            return False
    
    def get_all(self) -> Dict[str, str]:
        """
        Get all settings as dictionary
        
        Returns:
            Dictionary of all settings
        """
        try:
            db_manager = self._get_db_manager()
            results = db_manager.execute_query("SELECT key, value FROM settings")
            
            settings_dict = {}
            for row in results:
                key, value = row['key'], row['value']
                settings_dict[key] = value
                # Update cache
                self._settings_cache[key] = value
            
            return settings_dict
            
        except Exception as e:
            self.logger.error(f"Failed to get all settings: {e}")
            return {}
    
    def get_store_info(self) -> Dict[str, str]:
        """
        Get store information settings
        
        Returns:
            Dictionary with store information
        """
        return {
            'name': self.get('store_name', 'Medical Store'),
            'address': self.get('store_address', ''),
            'phone': self.get('store_phone', ''),
        }
    
    def get_currency(self) -> str:
        """
        Get currency setting
        
        Returns:
            Currency symbol
        """
        return self.get('currency', 'USD')
    
    def get_tax_rate(self) -> float:
        """
        Get tax rate setting
        
        Returns:
            Tax rate as float (percentage)
        """
        try:
            return float(self.get('tax_rate', '0.0'))
        except (ValueError, TypeError):
            self.logger.warning("Invalid tax rate in settings, using 0.0")
            return 0.0
    
    def get_low_stock_threshold(self) -> int:
        """
        Get low stock threshold setting
        
        Returns:
            Low stock threshold as integer
        """
        try:
            return int(self.get('low_stock_threshold', '10'))
        except (ValueError, TypeError):
            self.logger.warning("Invalid low stock threshold in settings, using 10")
            return 10
    
    def update_store_info(self, name: str, address: str, phone: str) -> bool:
        """
        Update store information
        
        Args:
            name: Store name
            address: Store address
            phone: Store phone
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = True
            success &= self.set('store_name', name, 'Store name for receipts and reports')
            success &= self.set('store_address', address, 'Store address')
            success &= self.set('store_phone', phone, 'Store contact phone')
            
            if success:
                self.logger.info("Store information updated successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update store information: {e}")
            return False
    
    def clear_cache(self):
        """Clear settings cache"""
        self._settings_cache.clear()
        self.logger.info("Settings cache cleared")


# Global settings instance
app_settings = AppSettings()