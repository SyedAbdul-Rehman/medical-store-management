"""
Unit tests for Medicine Manager
"""

import pytest
import sqlite3
from unittest.mock import Mock, patch
from datetime import date, timedelta

from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.models.medicine import Medicine
from medical_store_app.repositories.medicine_repository import MedicineRepository


class TestMedicineManager:
    """Test cases for MedicineManager class"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock medicine repository"""
        return Mock(spec=MedicineRepository)
    
    @pytest.fixture
    def medicine_manager(self, mock_repository):
        """Create medicine manager with mock repository"""
        return MedicineManager(mock_repository)
    
    @pytest.fixture
    def sample_medicine_data(self):
        """Sample medicine data for testing"""
        return {
            'name': 'Test Medicine',
            'category': 'Test Category',
            'batch_no': 'TEST001',
            'expiry_date': '2025-12-31',
            'quantity': 100,
            'purchase_price': 10.0,
            'selling_price': 15.0,
            'barcode': 'TEST123456789'
        }
    
    @pytest.fixture
    def sample_medicine(self):
        """Sample medicine instance for testing"""
        return Medicine(
            id=1,
            name='Test Medicine',
            category='Test Category',
            batch_no='TEST001',
            expiry_date='2025-12-31',
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0,
            barcode='TEST123456789'
        )
    
    def test_add_medicine_success(self, medicine_manager, mock_repository, sample_medicine_data, sample_medicine):
        """Test successful medicine addition"""
        # Arrange
        mock_repository.find_by_barcode.return_value = None
        mock_repository.save.return_value = sample_medicine
        
        # Act
        success, message, result = medicine_manager.add_medicine(sample_medicine_data)
        
        # Assert
        assert success is True
        assert "added successfully" in message
        assert result == sample_medicine
        mock_repository.find_by_barcode.assert_called_once_with('TEST123456789')
        mock_repository.save.assert_called_once()
    
    def test_add_medicine_validation_error(self, medicine_manager, mock_repository):
        """Test medicine addition with validation errors"""
        # Arrange
        invalid_data = {
            'name': '',  # Invalid: empty name
            'category': 'Test Category',
            'batch_no': 'TEST001',
            'expiry_date': '2025-12-31',
            'quantity': 100,
            'purchase_price': 10.0,
            'selling_price': 15.0
        }
        
        # Act
        success, message, result = medicine_manager.add_medicine(invalid_data)
        
        # Assert
        assert success is False
        assert "Validation failed" in message
        assert result is None
        mock_repository.save.assert_not_called()
    
    def test_add_medicine_duplicate_barcode(self, medicine_manager, mock_repository, sample_medicine_data, sample_medicine):
        """Test medicine addition with duplicate barcode"""
        # Arrange
        mock_repository.find_by_barcode.return_value = sample_medicine
        
        # Act
        success, message, result = medicine_manager.add_medicine(sample_medicine_data)
        
        # Assert
        assert success is False
        assert "already exists" in message
        assert result is None
        mock_repository.find_by_barcode.assert_called_once_with('TEST123456789')
        mock_repository.save.assert_not_called()
    
    def test_add_medicine_save_failure(self, medicine_manager, mock_repository, sample_medicine_data):
        """Test medicine addition when save fails"""
        # Arrange
        mock_repository.find_by_barcode.return_value = None
        mock_repository.save.return_value = None
        
        # Act
        success, message, result = medicine_manager.add_medicine(sample_medicine_data)
        
        # Assert
        assert success is False
        assert "Failed to save" in message
        assert result is None
    
    def test_edit_medicine_success(self, medicine_manager, mock_repository, sample_medicine, sample_medicine_data):
        """Test successful medicine editing"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_medicine
        mock_repository.find_by_barcode.return_value = None
        mock_repository.update.return_value = True
        
        updated_data = sample_medicine_data.copy()
        updated_data['name'] = 'Updated Medicine'
        
        # Act
        success, message, result = medicine_manager.edit_medicine(1, updated_data)
        
        # Assert
        assert success is True
        assert "updated successfully" in message
        assert result.name == 'Updated Medicine'
        mock_repository.find_by_id.assert_called_once_with(1)
        mock_repository.update.assert_called_once()
    
    def test_edit_medicine_not_found(self, medicine_manager, mock_repository, sample_medicine_data):
        """Test editing non-existent medicine"""
        # Arrange
        mock_repository.find_by_id.return_value = None
        
        # Act
        success, message, result = medicine_manager.edit_medicine(999, sample_medicine_data)
        
        # Assert
        assert success is False
        assert "not found" in message
        assert result is None
        mock_repository.update.assert_not_called()
    
    def test_edit_medicine_duplicate_barcode(self, medicine_manager, mock_repository, sample_medicine, sample_medicine_data):
        """Test editing medicine with duplicate barcode"""
        # Arrange
        existing_medicine = sample_medicine
        duplicate_medicine = Medicine(id=2, barcode='TEST123456789')
        
        mock_repository.find_by_id.return_value = existing_medicine
        mock_repository.find_by_barcode.return_value = duplicate_medicine
        
        # Act
        success, message, result = medicine_manager.edit_medicine(1, sample_medicine_data)
        
        # Assert
        assert success is False
        assert "already exists" in message
        assert result is None
        mock_repository.update.assert_not_called()
    
    def test_delete_medicine_success(self, medicine_manager, mock_repository, sample_medicine):
        """Test successful medicine deletion"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_medicine
        mock_repository.delete.return_value = True
        
        # Act
        success, message = medicine_manager.delete_medicine(1)
        
        # Assert
        assert success is True
        assert "deleted successfully" in message
        mock_repository.find_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_medicine_not_found(self, medicine_manager, mock_repository):
        """Test deleting non-existent medicine"""
        # Arrange
        mock_repository.find_by_id.return_value = None
        
        # Act
        success, message = medicine_manager.delete_medicine(999)
        
        # Assert
        assert success is False
        assert "not found" in message
        mock_repository.delete.assert_not_called()
    
    def test_get_medicine_by_id(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting medicine by ID"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_medicine
        
        # Act
        result = medicine_manager.get_medicine_by_id(1)
        
        # Assert
        assert result == sample_medicine
        mock_repository.find_by_id.assert_called_once_with(1)
    
    def test_get_medicine_by_barcode(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting medicine by barcode"""
        # Arrange
        mock_repository.find_by_barcode.return_value = sample_medicine
        
        # Act
        result = medicine_manager.get_medicine_by_barcode('TEST123456789')
        
        # Assert
        assert result == sample_medicine
        mock_repository.find_by_barcode.assert_called_once_with('TEST123456789')
    
    def test_get_all_medicines(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting all medicines"""
        # Arrange
        medicines = [sample_medicine]
        mock_repository.find_all.return_value = medicines
        
        # Act
        result = medicine_manager.get_all_medicines()
        
        # Assert
        assert result == medicines
        mock_repository.find_all.assert_called_once()
    
    def test_search_medicines(self, medicine_manager, mock_repository, sample_medicine):
        """Test searching medicines"""
        # Arrange
        medicines = [sample_medicine]
        mock_repository.search.return_value = medicines
        
        # Act
        result = medicine_manager.search_medicines('test')
        
        # Assert
        assert result == medicines
        mock_repository.search.assert_called_once_with('test')
    
    def test_search_medicines_empty_query(self, medicine_manager, mock_repository):
        """Test searching medicines with empty query"""
        # Act
        result = medicine_manager.search_medicines('')
        
        # Assert
        assert result == []
        mock_repository.search.assert_not_called()
    
    def test_update_stock_success(self, medicine_manager, mock_repository):
        """Test successful stock update"""
        # Arrange
        mock_repository.update_stock.return_value = True
        
        # Act
        success, message = medicine_manager.update_stock(1, 10)
        
        # Assert
        assert success is True
        assert "updated successfully" in message
        mock_repository.update_stock.assert_called_once_with(1, 10)
    
    def test_update_stock_failure(self, medicine_manager, mock_repository):
        """Test stock update failure"""
        # Arrange
        mock_repository.update_stock.return_value = False
        
        # Act
        success, message = medicine_manager.update_stock(1, 10)
        
        # Assert
        assert success is False
        assert "Failed to update" in message
    
    def test_check_stock_availability_sufficient(self, medicine_manager, mock_repository, sample_medicine):
        """Test stock availability check with sufficient stock"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_medicine
        
        # Act
        available, message, current_stock = medicine_manager.check_stock_availability(1, 50)
        
        # Assert
        assert available is True
        assert message == "Stock available"
        assert current_stock == 100
    
    def test_check_stock_availability_insufficient(self, medicine_manager, mock_repository, sample_medicine):
        """Test stock availability check with insufficient stock"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_medicine
        
        # Act
        available, message, current_stock = medicine_manager.check_stock_availability(1, 150)
        
        # Assert
        assert available is False
        assert "Insufficient stock" in message
        assert current_stock == 100
    
    def test_check_stock_availability_medicine_not_found(self, medicine_manager, mock_repository):
        """Test stock availability check for non-existent medicine"""
        # Arrange
        mock_repository.find_by_id.return_value = None
        
        # Act
        available, message, current_stock = medicine_manager.check_stock_availability(999, 10)
        
        # Assert
        assert available is False
        assert "not found" in message
        assert current_stock == 0
    
    def test_get_low_stock_medicines(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting low stock medicines"""
        # Arrange
        low_stock_medicines = [sample_medicine]
        mock_repository.get_low_stock_medicines.return_value = low_stock_medicines
        
        # Act
        result = medicine_manager.get_low_stock_medicines()
        
        # Assert
        assert result == low_stock_medicines
        mock_repository.get_low_stock_medicines.assert_called_once_with(10)
    
    def test_get_low_stock_medicines_custom_threshold(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting low stock medicines with custom threshold"""
        # Arrange
        low_stock_medicines = [sample_medicine]
        mock_repository.get_low_stock_medicines.return_value = low_stock_medicines
        
        # Act
        result = medicine_manager.get_low_stock_medicines(5)
        
        # Assert
        assert result == low_stock_medicines
        mock_repository.get_low_stock_medicines.assert_called_once_with(5)
    
    def test_get_expired_medicines(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting expired medicines"""
        # Arrange
        expired_medicines = [sample_medicine]
        mock_repository.get_expired_medicines.return_value = expired_medicines
        
        # Act
        result = medicine_manager.get_expired_medicines()
        
        # Assert
        assert result == expired_medicines
        mock_repository.get_expired_medicines.assert_called_once()
    
    def test_get_expiring_soon_medicines(self, medicine_manager, mock_repository, sample_medicine):
        """Test getting medicines expiring soon"""
        # Arrange
        expiring_medicines = [sample_medicine]
        mock_repository.get_expiring_soon_medicines.return_value = expiring_medicines
        
        # Act
        result = medicine_manager.get_expiring_soon_medicines()
        
        # Assert
        assert result == expiring_medicines
        mock_repository.get_expiring_soon_medicines.assert_called_once_with(30)
    
    def test_generate_stock_alerts(self, medicine_manager, mock_repository, sample_medicine):
        """Test generating stock alerts"""
        # Arrange
        mock_repository.get_low_stock_medicines.return_value = [sample_medicine]
        mock_repository.get_expired_medicines.return_value = []
        mock_repository.get_expiring_soon_medicines.return_value = [sample_medicine]
        
        # Act
        alerts = medicine_manager.generate_stock_alerts()
        
        # Assert
        assert 'low_stock' in alerts
        assert 'expired' in alerts
        assert 'expiring_soon' in alerts
        assert len(alerts['low_stock']) == 1
        assert len(alerts['expired']) == 0
        assert len(alerts['expiring_soon']) == 1
    
    def test_get_inventory_summary(self, medicine_manager, mock_repository):
        """Test getting inventory summary"""
        # Arrange
        mock_repository.get_total_medicines_count.return_value = 100
        mock_repository.get_total_stock_value.return_value = 5000.0
        mock_repository.get_low_stock_medicines.return_value = [Mock()]
        mock_repository.get_expired_medicines.return_value = []
        mock_repository.get_expiring_soon_medicines.return_value = [Mock(), Mock()]
        mock_repository.get_all_categories.return_value = ['Category1', 'Category2']
        
        # Act
        summary = medicine_manager.get_inventory_summary()
        
        # Assert
        assert summary['total_medicines'] == 100
        assert summary['total_stock_value'] == 5000.0
        assert summary['low_stock_count'] == 1
        assert summary['expired_count'] == 0
        assert summary['expiring_soon_count'] == 2
        assert len(summary['categories']) == 2
    
    def test_set_low_stock_threshold(self, medicine_manager):
        """Test setting low stock threshold"""
        # Act
        result = medicine_manager.set_low_stock_threshold(15)
        
        # Assert
        assert result is True
        assert medicine_manager.get_low_stock_threshold() == 15
    
    def test_set_low_stock_threshold_negative(self, medicine_manager):
        """Test setting negative low stock threshold"""
        # Act
        result = medicine_manager.set_low_stock_threshold(-5)
        
        # Assert
        assert result is False
        assert medicine_manager.get_low_stock_threshold() == 10  # Should remain default
    
    def test_set_expiry_warning_days(self, medicine_manager):
        """Test setting expiry warning days"""
        # Act
        result = medicine_manager.set_expiry_warning_days(45)
        
        # Assert
        assert result is True
        assert medicine_manager.get_expiry_warning_days() == 45
    
    def test_set_expiry_warning_days_negative(self, medicine_manager):
        """Test setting negative expiry warning days"""
        # Act
        result = medicine_manager.set_expiry_warning_days(-10)
        
        # Assert
        assert result is False
        assert medicine_manager.get_expiry_warning_days() == 30  # Should remain default
    
    def test_exception_handling(self, medicine_manager, mock_repository):
        """Test exception handling in various methods"""
        # Arrange
        mock_repository.find_by_id.side_effect = Exception("Database error")
        
        # Act & Assert
        result = medicine_manager.get_medicine_by_id(1)
        assert result is None
        
        success, message = medicine_manager.delete_medicine(1)
        assert success is False
        assert "Error deleting medicine" in message