"""
Tests for Medicine Form Widget
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDate
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.medicine_form import MedicineForm
from medical_store_app.models.medicine import Medicine
from medical_store_app.managers.medicine_manager import MedicineManager


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_medicine_manager():
    """Create mock medicine manager"""
    manager = Mock(spec=MedicineManager)
    return manager


@pytest.fixture
def medicine_form(app, mock_medicine_manager):
    """Create medicine form widget"""
    form = MedicineForm(mock_medicine_manager)
    return form


@pytest.fixture
def sample_medicine():
    """Create sample medicine for testing"""
    return Medicine(
        id=1,
        name="Test Medicine",
        category="Pain Relief",
        batch_no="TEST001",
        expiry_date="2025-12-31",
        quantity=100,
        purchase_price=10.0,
        selling_price=15.0,
        barcode="1234567890"
    )


class TestMedicineForm:
    """Test cases for MedicineForm widget"""
    
    def test_form_initialization(self, medicine_form):
        """Test form initialization"""
        assert medicine_form is not None
        assert medicine_form.medicine_manager is not None
        assert not medicine_form.is_editing
        assert medicine_form.current_medicine is None
        
        # Check that all fields are present
        assert medicine_form.name_field is not None
        assert medicine_form.category_field is not None
        assert medicine_form.batch_field is not None
        assert medicine_form.expiry_field is not None
        assert medicine_form.quantity_field is not None
        assert medicine_form.purchase_price_field is not None
        assert medicine_form.selling_price_field is not None
        assert medicine_form.barcode_field is not None
    
    def test_form_validation_empty_fields(self, medicine_form):
        """Test form validation with empty required fields"""
        # Clear all fields
        medicine_form.clear_form()
        
        # Check validation
        is_valid, errors = medicine_form.form_container.validate_form()
        assert not is_valid
        assert len(errors) > 0
    
    def test_form_validation_valid_data(self, medicine_form):
        """Test form validation with valid data"""
        # Fill form with valid data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("TEST001")
        medicine_form.expiry_field.setDate(QDate.currentDate().addDays(365))
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(10.0)
        medicine_form.selling_price_field.setValue(15.0)
        medicine_form.barcode_field.setText("1234567890")
        
        # Check validation
        is_valid, errors = medicine_form.form_container.validate_form()
        assert is_valid
        assert len(errors) == 0
    
    def test_name_validation(self, medicine_form):
        """Test medicine name validation"""
        # Test empty name
        is_valid, error = medicine_form._validate_name("")
        assert not is_valid
        assert "required" in error.lower()
        
        # Test short name
        is_valid, error = medicine_form._validate_name("A")
        assert not is_valid
        assert "2 characters" in error
        
        # Test long name
        is_valid, error = medicine_form._validate_name("A" * 101)
        assert not is_valid
        assert "100 characters" in error
        
        # Test valid name
        is_valid, error = medicine_form._validate_name("Valid Medicine Name")
        assert is_valid
        assert error == ""
    
    def test_category_validation(self, medicine_form):
        """Test category validation"""
        # Test empty category
        is_valid, error = medicine_form._validate_category("")
        assert not is_valid
        assert "required" in error.lower()
        
        # Test long category
        is_valid, error = medicine_form._validate_category("A" * 51)
        assert not is_valid
        assert "50 characters" in error
        
        # Test valid category
        is_valid, error = medicine_form._validate_category("Pain Relief")
        assert is_valid
        assert error == ""
    
    def test_batch_number_validation(self, medicine_form):
        """Test batch number validation"""
        # Test empty batch number
        is_valid, error = medicine_form._validate_batch_number("")
        assert not is_valid
        assert "required" in error.lower()
        
        # Test long batch number
        is_valid, error = medicine_form._validate_batch_number("A" * 51)
        assert not is_valid
        assert "50 characters" in error
        
        # Test valid batch number
        is_valid, error = medicine_form._validate_batch_number("BATCH001")
        assert is_valid
        assert error == ""
    
    def test_expiry_date_validation(self, medicine_form):
        """Test expiry date validation"""
        # Test past date
        past_date = QDate.currentDate().addDays(-1)
        is_valid, error = medicine_form._validate_expiry_date(past_date)
        assert not is_valid
        assert "future" in error.lower()
        
        # Test future date
        future_date = QDate.currentDate().addDays(365)
        is_valid, error = medicine_form._validate_expiry_date(future_date)
        assert is_valid
        assert error == ""
    
    def test_quantity_validation(self, medicine_form):
        """Test quantity validation"""
        # Test negative quantity
        is_valid, error = medicine_form._validate_quantity(-1)
        assert not is_valid
        assert "negative" in error.lower()
        
        # Test valid quantity
        is_valid, error = medicine_form._validate_quantity(100)
        assert is_valid
        assert error == ""
    
    def test_price_validation(self, medicine_form):
        """Test price validation"""
        # Test negative purchase price
        is_valid, error = medicine_form._validate_purchase_price(-1.0)
        assert not is_valid
        assert "negative" in error.lower()
        
        # Test negative selling price
        is_valid, error = medicine_form._validate_selling_price(-1.0)
        assert not is_valid
        assert "negative" in error.lower()
        
        # Test selling price less than purchase price
        medicine_form.purchase_price_field.setValue(15.0)
        is_valid, error = medicine_form._validate_selling_price(10.0)
        assert not is_valid
        assert "less than purchase price" in error.lower()
        
        # Test valid prices
        is_valid, error = medicine_form._validate_purchase_price(10.0)
        assert is_valid
        assert error == ""
        
        medicine_form.purchase_price_field.setValue(10.0)
        is_valid, error = medicine_form._validate_selling_price(15.0)
        assert is_valid
        assert error == ""
    
    def test_barcode_validation(self, medicine_form):
        """Test barcode validation"""
        # Test empty barcode (should be valid as it's optional)
        is_valid, error = medicine_form._validate_barcode("")
        assert is_valid
        assert error == ""
        
        # Test short barcode
        is_valid, error = medicine_form._validate_barcode("1234567")
        assert not is_valid
        assert "8-20 characters" in error
        
        # Test long barcode
        is_valid, error = medicine_form._validate_barcode("A" * 21)
        assert not is_valid
        assert "8-20 characters" in error
        
        # Test non-alphanumeric barcode
        is_valid, error = medicine_form._validate_barcode("12345678@#")
        assert not is_valid
        assert "letters and numbers" in error.lower()
        
        # Test valid barcode
        is_valid, error = medicine_form._validate_barcode("1234567890")
        assert is_valid
        assert error == ""
    
    def test_get_form_data(self, medicine_form):
        """Test getting form data"""
        # Fill form with test data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("TEST001")
        medicine_form.expiry_field.setDate(QDate(2025, 12, 31))
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(10.0)
        medicine_form.selling_price_field.setValue(15.0)
        medicine_form.barcode_field.setText("1234567890")
        
        # Get form data
        data = medicine_form.get_form_data()
        
        assert data['name'] == "Test Medicine"
        assert data['category'] == "Pain Relief"
        assert data['batch_no'] == "TEST001"
        assert data['expiry_date'] == "2025-12-31"
        assert data['quantity'] == 100
        assert data['purchase_price'] == 10.0
        assert data['selling_price'] == 15.0
        assert data['barcode'] == "1234567890"
    
    def test_load_medicine_for_editing(self, medicine_form, sample_medicine):
        """Test loading medicine data for editing"""
        # Load medicine
        medicine_form.load_medicine(sample_medicine)
        
        # Check that form is in editing mode
        assert medicine_form.is_editing
        assert medicine_form.current_medicine == sample_medicine
        
        # Check that fields are populated
        assert medicine_form.name_field.text() == sample_medicine.name
        assert medicine_form.category_field.currentText() == sample_medicine.category
        assert medicine_form.batch_field.text() == sample_medicine.batch_no
        assert medicine_form.quantity_field.value() == sample_medicine.quantity
        assert medicine_form.purchase_price_field.value() == sample_medicine.purchase_price
        assert medicine_form.selling_price_field.value() == sample_medicine.selling_price
        assert medicine_form.barcode_field.text() == sample_medicine.barcode
        
        # Check button text
        assert medicine_form.save_button.text() == "Update Medicine"
    
    def test_clear_form(self, medicine_form, sample_medicine):
        """Test clearing form"""
        # Load medicine first
        medicine_form.load_medicine(sample_medicine)
        
        # Clear form
        medicine_form.clear_form()
        
        # Check that form is reset
        assert not medicine_form.is_editing
        assert medicine_form.current_medicine is None
        assert medicine_form.name_field.text() == ""
        assert medicine_form.batch_field.text() == ""
        assert medicine_form.quantity_field.value() == 0
        assert medicine_form.purchase_price_field.value() == 0.0
        assert medicine_form.selling_price_field.value() == 0.0
        assert medicine_form.barcode_field.text() == ""
    
    @patch('medical_store_app.ui.components.medicine_form.MedicineFormWorker')
    def test_save_new_medicine(self, mock_worker_class, medicine_form, mock_medicine_manager):
        """Test saving new medicine"""
        # Setup mock worker
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        # Fill form with valid data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("TEST001")
        medicine_form.expiry_field.setDate(QDate.currentDate().addDays(365))
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(10.0)
        medicine_form.selling_price_field.setValue(15.0)
        
        # Save medicine
        medicine_form.save_medicine()
        
        # Check that worker was created and started
        mock_worker_class.assert_called_once()
        mock_worker.start.assert_called_once()
        
        # Check that worker was created and started
        # Note: UI state changes happen in the actual save_medicine method
        # which we're not fully executing in this mock test
    
    def test_is_form_dirty_new_medicine(self, medicine_form):
        """Test form dirty detection for new medicine"""
        # Empty form should not be dirty
        assert not medicine_form.is_form_dirty()
        
        # Form with data should be dirty
        medicine_form.name_field.setText("Test")
        assert medicine_form.is_form_dirty()
    
    def test_is_form_dirty_editing_medicine(self, medicine_form, sample_medicine):
        """Test form dirty detection when editing"""
        # Load medicine
        medicine_form.load_medicine(sample_medicine)
        
        # Unchanged form should not be dirty
        assert not medicine_form.is_form_dirty()
        
        # Changed form should be dirty
        medicine_form.name_field.setText("Modified Name")
        assert medicine_form.is_form_dirty()


class TestMedicineFormIntegration:
    """Integration tests for MedicineForm"""
    
    @patch('medical_store_app.ui.components.medicine_form.QMessageBox')
    def test_save_medicine_success(self, mock_msgbox, medicine_form, mock_medicine_manager):
        """Test successful medicine save operation"""
        # Setup mock manager response
        mock_medicine_manager.add_medicine.return_value = (True, "Medicine added successfully", Mock())
        
        # Fill form with valid data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("TEST001")
        medicine_form.expiry_field.setDate(QDate.currentDate().addDays(365))
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(10.0)
        medicine_form.selling_price_field.setValue(15.0)
        
        # Simulate successful operation
        medicine_form._on_operation_finished(True, "Medicine added successfully", Mock())
        
        # Check that success message was shown
        mock_msgbox.information.assert_called_once()
    
    @patch('medical_store_app.ui.components.medicine_form.QMessageBox')
    def test_save_medicine_failure(self, mock_msgbox, medicine_form):
        """Test failed medicine save operation"""
        # Simulate failed operation
        medicine_form._on_operation_finished(False, "Database error", None)
        
        # Check that error message was shown
        mock_msgbox.critical.assert_called_once()
    
    def test_profit_calculation_display(self, medicine_form):
        """Test profit calculation and display"""
        # Set prices
        medicine_form.purchase_price_field.setValue(10.0)
        medicine_form.selling_price_field.setValue(15.0)
        
        # Trigger profit calculation
        medicine_form._update_profit_info()
        
        # This test mainly ensures the method runs without error
        # In a real implementation, you might check if profit info is displayed
        assert True  # Method completed without error


if __name__ == "__main__":
    pytest.main([__file__])