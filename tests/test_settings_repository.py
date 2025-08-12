"""
Unit tests for Settings Repository
"""

import pytest
import sqlite3
import tempfile
import os

from medical_store_app.config.database import DatabaseManager
from medical_store_app.repositories.settings_repository import SettingsRepository


class TestSettingsRepository:
    """Test cases for SettingsRepository"""
    
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
        """Create settings repository instance"""
        return SettingsRepository(db_manager)
    
    def test_set_and_get_setting(self, repository):
        """Test setting and getting a setting value"""
        # Set a setting
        result = repository.set("test_key", "test_value", "Test description")
        assert result is True
        
        # Get the setting
        value = repository.get("test_key")
        assert value == "test_value"
    
    def test_get_nonexistent_setting(self, repository):
        """Test getting a non-existent setting"""
        value = repository.get("nonexistent_key")
        assert value is None
    
    def test_set_empty_key(self, repository):
        """Test setting with empty key fails"""
        result = repository.set("", "value")
        assert result is False
        
        result = repository.set(None, "value")
        assert result is False
    
    def test_update_existing_setting(self, repository):
        """Test updating an existing setting"""
        # Set initial value
        repository.set("update_key", "initial_value", "Initial description")
        
        # Update the value
        result = repository.set("update_key", "updated_value", "Updated description")
        assert result is True
        
        # Verify the update
        value = repository.get("update_key")
        assert value == "updated_value"
    
    def test_get_all_settings(self, repository):
        """Test getting all settings"""
        # Set multiple settings
        repository.set("key1", "value1")
        repository.set("key2", "value2")
        repository.set("key3", "value3")
        
        # Get all settings
        all_settings = repository.get_all()
        
        # Should include our settings plus any default ones
        assert "key1" in all_settings
        assert "key2" in all_settings
        assert "key3" in all_settings
        assert all_settings["key1"] == "value1"
        assert all_settings["key2"] == "value2"
        assert all_settings["key3"] == "value3"
    
    def test_get_all_with_details(self, repository):
        """Test getting all settings with details"""
        # Set a setting with description
        repository.set("detailed_key", "detailed_value", "Detailed description")
        
        # Get all with details
        all_settings = repository.get_all_with_details()
        
        # Find our setting
        our_setting = None
        for setting in all_settings:
            if setting['key'] == 'detailed_key':
                our_setting = setting
                break
        
        assert our_setting is not None
        assert our_setting['value'] == 'detailed_value'
        assert our_setting['description'] == 'Detailed description'
        assert 'updated_at' in our_setting
    
    def test_delete_setting(self, repository):
        """Test deleting a setting"""
        # Set a setting
        repository.set("delete_key", "delete_value")
        
        # Verify it exists
        value = repository.get("delete_key")
        assert value == "delete_value"
        
        # Delete the setting
        result = repository.delete("delete_key")
        assert result is True
        
        # Verify it's gone
        value = repository.get("delete_key")
        assert value is None
    
    def test_delete_nonexistent_setting(self, repository):
        """Test deleting a non-existent setting"""
        result = repository.delete("nonexistent_key")
        assert result is False
    
    def test_exists(self, repository):
        """Test checking if setting exists"""
        # Initially should not exist
        exists = repository.exists("exists_key")
        assert exists is False
        
        # Set the setting
        repository.set("exists_key", "exists_value")
        
        # Now should exist
        exists = repository.exists("exists_key")
        assert exists is True
    
    def test_get_int(self, repository):
        """Test getting setting as integer"""
        # Set integer value
        repository.set("int_key", "42")
        
        # Get as integer
        value = repository.get_int("int_key")
        assert value == 42
        assert isinstance(value, int)
        
        # Test default value for non-existent key
        value = repository.get_int("nonexistent_int", 100)
        assert value == 100
        
        # Test invalid integer
        repository.set("invalid_int", "not_a_number")
        value = repository.get_int("invalid_int", 50)
        assert value == 50  # Should return default
    
    def test_get_float(self, repository):
        """Test getting setting as float"""
        # Set float value
        repository.set("float_key", "3.14")
        
        # Get as float
        value = repository.get_float("float_key")
        assert value == 3.14
        assert isinstance(value, float)
        
        # Test default value for non-existent key
        value = repository.get_float("nonexistent_float", 2.5)
        assert value == 2.5
        
        # Test invalid float
        repository.set("invalid_float", "not_a_number")
        value = repository.get_float("invalid_float", 1.5)
        assert value == 1.5  # Should return default
    
    def test_get_bool(self, repository):
        """Test getting setting as boolean"""
        # Test various true values
        true_values = ["true", "True", "1", "yes", "on"]
        for i, true_val in enumerate(true_values):
            repository.set(f"bool_true_{i}", true_val)
            value = repository.get_bool(f"bool_true_{i}")
            assert value is True
        
        # Test various false values
        false_values = ["false", "False", "0", "no", "off", "anything_else"]
        for i, false_val in enumerate(false_values):
            repository.set(f"bool_false_{i}", false_val)
            value = repository.get_bool(f"bool_false_{i}")
            assert value is False
        
        # Test default value for non-existent key
        value = repository.get_bool("nonexistent_bool", True)
        assert value is True
    
    def test_set_int(self, repository):
        """Test setting integer value"""
        result = repository.set_int("int_setting", 123, "Integer setting")
        assert result is True
        
        # Verify it was stored as string but can be retrieved as int
        stored_value = repository.get("int_setting")
        assert stored_value == "123"
        
        retrieved_value = repository.get_int("int_setting")
        assert retrieved_value == 123
    
    def test_set_float(self, repository):
        """Test setting float value"""
        result = repository.set_float("float_setting", 12.34, "Float setting")
        assert result is True
        
        # Verify it was stored as string but can be retrieved as float
        stored_value = repository.get("float_setting")
        assert stored_value == "12.34"
        
        retrieved_value = repository.get_float("float_setting")
        assert retrieved_value == 12.34
    
    def test_set_bool(self, repository):
        """Test setting boolean value"""
        # Set true value
        result = repository.set_bool("bool_true", True, "Boolean true setting")
        assert result is True
        
        stored_value = repository.get("bool_true")
        assert stored_value == "true"
        
        retrieved_value = repository.get_bool("bool_true")
        assert retrieved_value is True
        
        # Set false value
        result = repository.set_bool("bool_false", False, "Boolean false setting")
        assert result is True
        
        stored_value = repository.get("bool_false")
        assert stored_value == "false"
        
        retrieved_value = repository.get_bool("bool_false")
        assert retrieved_value is False
    
    def test_get_store_settings(self, repository):
        """Test getting store-related settings"""
        # Set some store settings
        repository.set("store_name", "Test Medical Store")
        repository.set("store_address", "123 Test Street")
        repository.set("store_phone", "555-1234")
        repository.set("other_setting", "not_store_related")
        
        # Get store settings
        store_settings = repository.get_store_settings()
        
        assert "store_name" in store_settings
        assert "store_address" in store_settings
        assert "store_phone" in store_settings
        assert "other_setting" not in store_settings
        
        assert store_settings["store_name"] == "Test Medical Store"
        assert store_settings["store_address"] == "123 Test Street"
        assert store_settings["store_phone"] == "555-1234"
    
    def test_get_business_settings(self, repository):
        """Test getting business-related settings"""
        # Set some business settings
        repository.set("currency", "EUR")
        repository.set_float("tax_rate", 15.5)
        repository.set_int("low_stock_threshold", 5)
        repository.set_bool("enable_barcode_scanning", False)
        
        # Get business settings
        business_settings = repository.get_business_settings()
        
        assert business_settings["currency"] == "EUR"
        assert business_settings["tax_rate"] == 15.5
        assert business_settings["low_stock_threshold"] == 5
        assert business_settings["enable_barcode_scanning"] is False
        
        # Test defaults for missing settings
        repository.delete("currency")
        business_settings = repository.get_business_settings()
        assert business_settings["currency"] == "USD"  # Default
    
    def test_update_store_settings(self, repository):
        """Test updating multiple store settings"""
        settings_to_update = {
            "store_name": "Updated Store Name",
            "store_address": "456 Updated Street",
            "store_phone": "555-5678"
        }
        
        result = repository.update_store_settings(settings_to_update)
        assert result is True
        
        # Verify all settings were updated
        for key, expected_value in settings_to_update.items():
            actual_value = repository.get(key)
            assert actual_value == expected_value
    
    def test_update_business_settings(self, repository):
        """Test updating multiple business settings"""
        settings_to_update = {
            "currency": "GBP",
            "tax_rate": 20.0,
            "low_stock_threshold": 15,
            "enable_barcode_scanning": True,
            "auto_backup": False
        }
        
        result = repository.update_business_settings(settings_to_update)
        assert result is True
        
        # Verify all settings were updated with correct types
        assert repository.get("currency") == "GBP"
        assert repository.get_float("tax_rate") == 20.0
        assert repository.get_int("low_stock_threshold") == 15
        assert repository.get_bool("enable_barcode_scanning") is True
        assert repository.get_bool("auto_backup") is False
    
    def test_reset_to_defaults(self, repository):
        """Test resetting all settings to defaults"""
        # Set some custom settings
        repository.set("custom_setting", "custom_value")
        repository.set("store_name", "Custom Store")
        
        # Reset to defaults
        result = repository.reset_to_defaults()
        assert result is True
        
        # Verify custom setting is gone
        custom_value = repository.get("custom_setting")
        assert custom_value is None
        
        # Verify default settings are present
        store_name = repository.get("store_name")
        assert store_name == "Medical Store"  # Default value
        
        currency = repository.get("currency")
        assert currency == "USD"  # Default value
    
    def test_get_settings_count(self, repository):
        """Test getting settings count"""
        # Get initial count (includes defaults from database initialization)
        initial_count = repository.get_settings_count()
        
        # Add some settings
        repository.set("count_test_1", "value1")
        repository.set("count_test_2", "value2")
        
        # Count should increase by 2
        new_count = repository.get_settings_count()
        assert new_count == initial_count + 2