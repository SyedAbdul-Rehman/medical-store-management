"""
Settings repository for Medical Store Management Application
Handles all database operations for application settings
"""

import sqlite3
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..config.database import DatabaseManager


class SettingsRepository:
    """Repository class for application settings data access operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize settings repository
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[str]:
        """
        Get setting value by key
        
        Args:
            key: Setting key
            
        Returns:
            Setting value if found, None otherwise
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT value FROM settings WHERE key = ?",
                (key,)
            )
            
            return row['value'] if row else None
            
        except Exception as e:
            self.logger.error(f"Failed to get setting '{key}': {e}")
            return None
    
    def set(self, key: str, value: str, description: Optional[str] = None) -> bool:
        """
        Set setting value
        
        Args:
            key: Setting key
            value: Setting value
            description: Optional description of the setting
            
        Returns:
            True if setting saved successfully, False otherwise
        """
        try:
            if not key or not key.strip():
                self.logger.error("Setting key cannot be empty")
                return False
            
            updated_at = datetime.now().isoformat()
            
            with self.db_manager.get_cursor() as cursor:
                # Try to update existing setting first
                cursor.execute("""
                    UPDATE settings 
                    SET value = ?, description = ?, updated_at = ?
                    WHERE key = ?
                """, (value, description, updated_at, key.strip()))
                
                if cursor.rowcount == 0:
                    # Setting doesn't exist, insert new one
                    cursor.execute("""
                        INSERT INTO settings (key, value, description, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (key.strip(), value, description, updated_at))
                
                self.logger.info(f"Setting saved successfully: {key} = {value}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set setting '{key}': {e}")
            return False
    
    def get_all(self) -> Dict[str, str]:
        """
        Get all settings as key-value pairs
        
        Returns:
            Dictionary of all settings
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT key, value FROM settings ORDER BY key ASC"
            )
            
            return {row['key']: row['value'] for row in rows}
            
        except Exception as e:
            self.logger.error(f"Failed to get all settings: {e}")
            return {}
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
        """
        Get all settings with full details
        
        Returns:
            List of setting dictionaries with key, value, description, and updated_at
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT * FROM settings ORDER BY key ASC"
            )
            
            return [
                {
                    'key': row['key'],
                    'value': row['value'],
                    'description': row['description'],
                    'updated_at': row['updated_at']
                }
                for row in rows
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get all settings with details: {e}")
            return []
    
    def delete(self, key: str) -> bool:
        """
        Delete setting by key
        
        Args:
            key: Setting key to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            rows_affected = self.db_manager.execute_update(
                "DELETE FROM settings WHERE key = ?",
                (key,)
            )
            
            if rows_affected > 0:
                self.logger.info(f"Setting deleted successfully: {key}")
                return True
            else:
                self.logger.warning(f"No setting found with key: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete setting '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if setting exists
        
        Args:
            key: Setting key to check
            
        Returns:
            True if setting exists, False otherwise
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT COUNT(*) as count FROM settings WHERE key = ?",
                (key,)
            )
            
            return row['count'] > 0 if row else False
            
        except Exception as e:
            self.logger.error(f"Failed to check setting existence '{key}': {e}")
            return False
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get setting value as integer
        
        Args:
            key: Setting key
            default: Default value if setting not found or invalid
            
        Returns:
            Setting value as integer
        """
        try:
            value = self.get(key)
            if value is not None:
                return int(value)
            return default
        except (ValueError, TypeError):
            self.logger.warning(f"Setting '{key}' is not a valid integer, returning default: {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get setting value as float
        
        Args:
            key: Setting key
            default: Default value if setting not found or invalid
            
        Returns:
            Setting value as float
        """
        try:
            value = self.get(key)
            if value is not None:
                return float(value)
            return default
        except (ValueError, TypeError):
            self.logger.warning(f"Setting '{key}' is not a valid float, returning default: {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get setting value as boolean
        
        Args:
            key: Setting key
            default: Default value if setting not found or invalid
            
        Returns:
            Setting value as boolean
        """
        try:
            value = self.get(key)
            if value is not None:
                return value.lower() in ('true', '1', 'yes', 'on')
            return default
        except (AttributeError, TypeError):
            self.logger.warning(f"Setting '{key}' is not a valid boolean, returning default: {default}")
            return default
    
    def set_int(self, key: str, value: int, description: Optional[str] = None) -> bool:
        """
        Set setting value as integer
        
        Args:
            key: Setting key
            value: Integer value
            description: Optional description
            
        Returns:
            True if setting saved successfully, False otherwise
        """
        return self.set(key, str(value), description)
    
    def set_float(self, key: str, value: float, description: Optional[str] = None) -> bool:
        """
        Set setting value as float
        
        Args:
            key: Setting key
            value: Float value
            description: Optional description
            
        Returns:
            True if setting saved successfully, False otherwise
        """
        return self.set(key, str(value), description)
    
    def set_bool(self, key: str, value: bool, description: Optional[str] = None) -> bool:
        """
        Set setting value as boolean
        
        Args:
            key: Setting key
            value: Boolean value
            description: Optional description
            
        Returns:
            True if setting saved successfully, False otherwise
        """
        return self.set(key, 'true' if value else 'false', description)
    
    def get_store_settings(self) -> Dict[str, str]:
        """
        Get store-related settings
        
        Returns:
            Dictionary of store settings
        """
        store_keys = [
            'store_name',
            'store_address',
            'store_phone',
            'store_email',
            'store_website'
        ]
        
        settings = {}
        for key in store_keys:
            value = self.get(key)
            if value is not None:
                settings[key] = value
        
        return settings
    
    def get_business_settings(self) -> Dict[str, Any]:
        """
        Get business-related settings
        
        Returns:
            Dictionary of business settings with appropriate types
        """
        return {
            'currency': self.get('currency') or 'USD',
            'tax_rate': self.get_float('tax_rate', 0.0),
            'low_stock_threshold': self.get_int('low_stock_threshold', 10),
            'enable_barcode_scanning': self.get_bool('enable_barcode_scanning', True),
            'auto_backup': self.get_bool('auto_backup', False),
            'backup_frequency_days': self.get_int('backup_frequency_days', 7)
        }
    
    def update_store_settings(self, settings: Dict[str, str]) -> bool:
        """
        Update multiple store settings at once
        
        Args:
            settings: Dictionary of store settings to update
            
        Returns:
            True if all settings updated successfully, False otherwise
        """
        try:
            success = True
            for key, value in settings.items():
                if not self.set(key, value):
                    success = False
                    self.logger.error(f"Failed to update store setting: {key}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update store settings: {e}")
            return False
    
    def update_business_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update multiple business settings at once
        
        Args:
            settings: Dictionary of business settings to update
            
        Returns:
            True if all settings updated successfully, False otherwise
        """
        try:
            success = True
            
            # Handle different data types appropriately
            for key, value in settings.items():
                if isinstance(value, bool):
                    if not self.set_bool(key, value):
                        success = False
                elif isinstance(value, int):
                    if not self.set_int(key, value):
                        success = False
                elif isinstance(value, float):
                    if not self.set_float(key, value):
                        success = False
                else:
                    if not self.set(key, str(value)):
                        success = False
                
                if not success:
                    self.logger.error(f"Failed to update business setting: {key}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update business settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to default values
        
        Returns:
            True if reset successful, False otherwise
        """
        try:
            # Clear all existing settings
            self.db_manager.execute_update("DELETE FROM settings")
            
            # Insert default settings
            default_settings = [
                ("store_name", "Medical Store", "Store name for receipts and reports"),
                ("store_address", "", "Store address"),
                ("store_phone", "", "Store contact phone"),
                ("store_email", "", "Store email address"),
                ("currency", "USD", "Currency symbol"),
                ("tax_rate", "0.0", "Default tax rate percentage"),
                ("low_stock_threshold", "10", "Low stock alert threshold"),
                ("enable_barcode_scanning", "true", "Enable barcode scanning feature"),
                ("auto_backup", "false", "Enable automatic backup"),
                ("backup_frequency_days", "7", "Backup frequency in days")
            ]
            
            success = True
            for key, value, description in default_settings:
                if not self.set(key, value, description):
                    success = False
            
            if success:
                self.logger.info("Settings reset to defaults successfully")
            else:
                self.logger.error("Some settings failed to reset")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to reset settings to defaults: {e}")
            return False
    
    def get_settings_count(self) -> int:
        """
        Get total count of settings
        
        Returns:
            Total number of setting records
        """
        try:
            row = self.db_manager.execute_single("SELECT COUNT(*) as count FROM settings")
            return row['count'] if row else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get settings count: {e}")
            return 0