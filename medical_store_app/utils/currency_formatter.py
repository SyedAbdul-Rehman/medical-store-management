"""
Currency formatting utilities for Medical Store Management Application
Handles currency display formatting based on application settings
"""

import logging
from typing import Dict, Any, Optional
from ..repositories.settings_repository import SettingsRepository


class CurrencyFormatter:
    """Utility class for formatting currency values based on settings"""
    
    # Currency symbols mapping
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'PKR': '₨',
        'CAD': 'C$',
        'AUD': 'A$',
        'JPY': '¥',
        'CNY': '¥'
    }
    
    def __init__(self, settings_repository: SettingsRepository):
        """
        Initialize currency formatter
        
        Args:
            settings_repository: Settings repository instance
        """
        self.settings_repository = settings_repository
        self.logger = logging.getLogger(__name__)
        self._current_currency = None
        self._current_symbol = None
        self._load_currency_settings()
    
    def _load_currency_settings(self):
        """Load currency settings from database"""
        try:
            currency = self.settings_repository.get('currency') or 'USD'
            self._current_currency = currency
            self._current_symbol = self.CURRENCY_SYMBOLS.get(currency, currency)
            self.logger.debug(f"Loaded currency settings: {currency} ({self._current_symbol})")
        except Exception as e:
            self.logger.error(f"Error loading currency settings: {e}")
            self._current_currency = 'USD'
            self._current_symbol = '$'
    
    def format_amount(self, amount: float, show_symbol: bool = True) -> str:
        """
        Format amount with currency symbol
        
        Args:
            amount: Amount to format
            show_symbol: Whether to show currency symbol
            
        Returns:
            Formatted currency string
        """
        try:
            if show_symbol:
                return f"{self._current_symbol}{amount:.2f}"
            else:
                return f"{amount:.2f}"
        except Exception as e:
            self.logger.error(f"Error formatting amount {amount}: {e}")
            return f"${amount:.2f}" if show_symbol else f"{amount:.2f}"
    
    def get_currency_symbol(self) -> str:
        """
        Get current currency symbol
        
        Returns:
            Current currency symbol
        """
        return self._current_symbol
    
    def get_currency_code(self) -> str:
        """
        Get current currency code
        
        Returns:
            Current currency code
        """
        return self._current_currency
    
    def refresh_settings(self):
        """Refresh currency settings from database"""
        self._load_currency_settings()
    
    def update_currency(self, currency_code: str):
        """
        Update currency settings
        
        Args:
            currency_code: New currency code
        """
        try:
            if currency_code in self.CURRENCY_SYMBOLS:
                self._current_currency = currency_code
                self._current_symbol = self.CURRENCY_SYMBOLS[currency_code]
                self.logger.info(f"Currency updated to: {currency_code} ({self._current_symbol})")
            else:
                # Handle custom currency
                self._current_currency = currency_code
                self._current_symbol = currency_code
                self.logger.info(f"Custom currency set: {currency_code}")
        except Exception as e:
            self.logger.error(f"Error updating currency to {currency_code}: {e}")


class SettingsManager:
    """Manager class for application settings integration"""
    
    def __init__(self, settings_repository: SettingsRepository):
        """
        Initialize settings manager
        
        Args:
            settings_repository: Settings repository instance
        """
        self.settings_repository = settings_repository
        self.currency_formatter = CurrencyFormatter(settings_repository)
        self.logger = logging.getLogger(__name__)
        self._current_settings = {}
        self._load_all_settings()
    
    def _load_all_settings(self):
        """Load all settings from database"""
        try:
            self._current_settings = self.settings_repository.get_all()
            self.logger.debug("Loaded all application settings")
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self._current_settings = {}
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get setting value with type conversion
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value with appropriate type
        """
        try:
            value = self._current_settings.get(key)
            if value is None:
                return default
            
            # Type conversion based on key
            if key in ['tax_rate']:
                return float(value)
            elif key in ['low_stock_threshold', 'backup_frequency_days']:
                return int(value)
            elif key in ['enable_barcode_scanning', 'auto_backup']:
                return value.lower() in ('true', '1', 'yes', 'on')
            else:
                return value
                
        except Exception as e:
            self.logger.error(f"Error getting setting {key}: {e}")
            return default
    
    def get_store_info(self) -> Dict[str, str]:
        """
        Get store information settings
        
        Returns:
            Dictionary of store information
        """
        return {
            'name': self.get_setting('store_name', 'Medical Store'),
            'address': self.get_setting('store_address', ''),
            'phone': self.get_setting('store_phone', ''),
            'email': self.get_setting('store_email', ''),
            'website': self.get_setting('store_website', '')
        }
    
    def get_business_settings(self) -> Dict[str, Any]:
        """
        Get business configuration settings
        
        Returns:
            Dictionary of business settings
        """
        return {
            'currency': self.get_setting('currency', 'USD'),
            'tax_rate': self.get_setting('tax_rate', 0.0),
            'low_stock_threshold': self.get_setting('low_stock_threshold', 10),
            'enable_barcode_scanning': self.get_setting('enable_barcode_scanning', True),
            'auto_backup': self.get_setting('auto_backup', False),
            'backup_frequency_days': self.get_setting('backup_frequency_days', 7)
        }
    
    def refresh_settings(self):
        """Refresh all settings from database"""
        self._load_all_settings()
        self.currency_formatter.refresh_settings()
        self.logger.info("Settings refreshed from database")
    
    def format_currency(self, amount: float, show_symbol: bool = True) -> str:
        """
        Format currency amount using current settings
        
        Args:
            amount: Amount to format
            show_symbol: Whether to show currency symbol
            
        Returns:
            Formatted currency string
        """
        return self.currency_formatter.format_amount(amount, show_symbol)
    
    def get_default_tax_rate(self) -> float:
        """
        Get default tax rate from settings
        
        Returns:
            Default tax rate as percentage
        """
        return self.get_setting('tax_rate', 0.0)
    
    def get_currency_symbol(self) -> str:
        """
        Get current currency symbol
        
        Returns:
            Current currency symbol
        """
        return self.currency_formatter.get_currency_symbol()