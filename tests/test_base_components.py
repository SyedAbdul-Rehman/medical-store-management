"""
Tests for base UI components
Tests reusable form components, validation widgets, and common UI elements
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent / "medical_store_app"
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDate
from PySide6.QtTest import QTest

from ui.components.base_components import (
    ValidatedLineEdit, ValidatedComboBox, ValidatedSpinBox, 
    ValidatedDoubleSpinBox, ValidatedDateEdit, StyledButton, 
    StyledTable, FormContainer
)


class TestValidatedLineEdit:
    """Test cases for ValidatedLineEdit"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_line_edit_initialization(self):
        """Test that ValidatedLineEdit initializes correctly"""
        line_edit = ValidatedLineEdit("Enter text")
        
        assert line_edit.placeholderText() == "Enter text"
        assert line_edit.error_label is not None
        assert not line_edit.error_label.isVisible()
        
        line_edit.deleteLater()
    
    def test_line_edit_validation(self):
        """Test line edit validation functionality"""
        line_edit = ValidatedLineEdit()
        
        # Add a simple validator
        def not_empty_validator(value):
            if not value.strip():
                return False, "Field cannot be empty"
            return True, ""
        
        line_edit.add_validator(not_empty_validator)
        
        # Test empty value
        line_edit.setText("")
        is_valid, error = line_edit.validate_input()
        assert not is_valid
        assert "empty" in error.lower()
        
        # Test valid value
        line_edit.setText("Valid text")
        is_valid, error = line_edit.validate_input()
        assert is_valid
        assert error == ""
        
        line_edit.deleteLater()
    
    def test_line_edit_error_display(self):
        """Test error display functionality"""
        line_edit = ValidatedLineEdit()
        
        # Show error
        line_edit.show_error("Test error")
        assert line_edit.error_label.isVisible()
        assert "Test error" in line_edit.error_label.text()
        
        # Clear error
        line_edit.clear_error()
        assert not line_edit.error_label.isVisible()
        
        line_edit.deleteLater()


class TestValidatedComboBox:
    """Test cases for ValidatedComboBox"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_combo_box_initialization(self):
        """Test that ValidatedComboBox initializes correctly"""
        items = ["Option 1", "Option 2", "Option 3"]
        combo_box = ValidatedComboBox(items)
        
        assert combo_box.count() == 3
        assert combo_box.itemText(0) == "Option 1"
        assert combo_box.error_label is not None
        
        combo_box.deleteLater()
    
    def test_combo_box_validation(self):
        """Test combo box validation functionality"""
        combo_box = ValidatedComboBox(["", "Valid Option"])
        
        # Add validator
        def not_empty_validator(value):
            if not value.strip():
                return False, "Please select an option"
            return True, ""
        
        combo_box.add_validator(not_empty_validator)
        
        # Test empty selection
        combo_box.setCurrentIndex(0)
        is_valid, error = combo_box.validate_input()
        assert not is_valid
        assert "select" in error.lower()
        
        # Test valid selection
        combo_box.setCurrentIndex(1)
        is_valid, error = combo_box.validate_input()
        assert is_valid
        
        combo_box.deleteLater()


class TestValidatedSpinBox:
    """Test cases for ValidatedSpinBox"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_spin_box_initialization(self):
        """Test that ValidatedSpinBox initializes correctly"""
        spin_box = ValidatedSpinBox(0, 100)
        
        assert spin_box.minimum() == 0
        assert spin_box.maximum() == 100
        assert spin_box.error_label is not None
        
        spin_box.deleteLater()
    
    def test_spin_box_validation(self):
        """Test spin box validation functionality"""
        spin_box = ValidatedSpinBox(0, 100)  # Allow 0 so we can test validation
        
        # Add validator
        def min_value_validator(value):
            if value < 1:
                return False, "Value must be at least 1"
            return True, ""
        
        spin_box.add_validator(min_value_validator)
        
        # Test invalid value
        spin_box.setValue(0)
        is_valid, error = spin_box.validate_input()
        assert not is_valid
        assert "at least 1" in error
        
        # Test valid value
        spin_box.setValue(5)
        is_valid, error = spin_box.validate_input()
        assert is_valid
        
        spin_box.deleteLater()


class TestValidatedDoubleSpinBox:
    """Test cases for ValidatedDoubleSpinBox"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_double_spin_box_initialization(self):
        """Test that ValidatedDoubleSpinBox initializes correctly"""
        spin_box = ValidatedDoubleSpinBox(0.0, 999.99, 2)
        
        assert spin_box.minimum() == 0.0
        assert spin_box.maximum() == 999.99
        assert spin_box.decimals() == 2
        assert spin_box.error_label is not None
        
        spin_box.deleteLater()
    
    def test_double_spin_box_validation(self):
        """Test double spin box validation functionality"""
        spin_box = ValidatedDoubleSpinBox(0.0, 1000.0)  # Allow 0.0 so we can test validation
        
        # Add validator
        def positive_validator(value):
            if value <= 0:
                return False, "Value must be positive"
            return True, ""
        
        spin_box.add_validator(positive_validator)
        
        # Test invalid value
        spin_box.setValue(0.0)
        is_valid, error = spin_box.validate_input()
        assert not is_valid
        assert "positive" in error.lower()
        
        # Test valid value
        spin_box.setValue(10.50)
        is_valid, error = spin_box.validate_input()
        assert is_valid
        
        spin_box.deleteLater()


class TestValidatedDateEdit:
    """Test cases for ValidatedDateEdit"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_date_edit_initialization(self):
        """Test that ValidatedDateEdit initializes correctly"""
        date_edit = ValidatedDateEdit()
        
        assert date_edit.date() == QDate.currentDate()
        assert date_edit.calendarPopup()
        assert date_edit.error_label is not None
        
        date_edit.deleteLater()
    
    def test_date_edit_validation(self):
        """Test date edit validation functionality"""
        date_edit = ValidatedDateEdit()
        
        # Add validator for future dates
        def future_date_validator(date_value):
            if date_value <= QDate.currentDate():
                return False, "Date must be in the future"
            return True, ""
        
        date_edit.add_validator(future_date_validator)
        
        # Test current date (invalid)
        date_edit.setDate(QDate.currentDate())
        is_valid, error = date_edit.validate_input()
        assert not is_valid
        assert "future" in error.lower()
        
        # Test future date (valid)
        future_date = QDate.currentDate().addDays(30)
        date_edit.setDate(future_date)
        is_valid, error = date_edit.validate_input()
        assert is_valid
        
        date_edit.deleteLater()


class TestStyledButton:
    """Test cases for StyledButton"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_styled_button_initialization(self):
        """Test that StyledButton initializes correctly"""
        button = StyledButton("Test Button", "primary")
        
        assert button.text() == "Test Button"
        assert button.button_type == "primary"
        assert len(button.styleSheet()) > 0
        
        button.deleteLater()
    
    def test_styled_button_types(self):
        """Test different button types"""
        button_types = ["primary", "secondary", "danger", "outline"]
        
        for button_type in button_types:
            button = StyledButton("Test", button_type)
            assert button.button_type == button_type
            assert len(button.styleSheet()) > 0
            button.deleteLater()


class TestStyledTable:
    """Test cases for StyledTable"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_styled_table_initialization(self):
        """Test that StyledTable initializes correctly"""
        table = StyledTable(5, 3)
        
        assert table.rowCount() == 5
        assert table.columnCount() == 3
        assert table.isSortingEnabled()
        assert table.alternatingRowColors()
        assert len(table.styleSheet()) > 0
        
        table.deleteLater()
    
    def test_styled_table_behavior(self):
        """Test table behavior settings"""
        table = StyledTable()
        
        # Test selection behavior
        from PySide6.QtWidgets import QAbstractItemView
        assert table.selectionBehavior() == QAbstractItemView.SelectRows
        assert table.selectionMode() == QAbstractItemView.SingleSelection
        
        table.deleteLater()


class TestFormContainer:
    """Test cases for FormContainer"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_form_container_initialization(self):
        """Test that FormContainer initializes correctly"""
        form = FormContainer("Test Form")
        
        assert form.title == "Test Form"
        assert form.form_layout is not None
        assert len(form.form_fields) == 0
        
        form.deleteLater()
    
    def test_form_container_add_field(self):
        """Test adding fields to form container"""
        form = FormContainer()
        
        # Add a line edit field
        line_edit = ValidatedLineEdit("Test input")
        form.add_field("Test Field", line_edit, "test_field")
        
        assert "test_field" in form.form_fields
        assert form.get_field("test_field") == line_edit
        
        form.deleteLater()
    
    def test_form_container_get_form_data(self):
        """Test getting form data"""
        form = FormContainer()
        
        # Add fields
        line_edit = ValidatedLineEdit()
        line_edit.setText("Test Value")
        form.add_field("Text Field", line_edit, "text_field")
        
        spin_box = ValidatedSpinBox()
        spin_box.setValue(42)
        form.add_field("Number Field", spin_box, "number_field")
        
        # Get form data
        data = form.get_form_data()
        
        assert data["text_field"] == "Test Value"
        assert data["number_field"] == 42
        
        form.deleteLater()
    
    def test_form_container_validation(self):
        """Test form validation"""
        form = FormContainer()
        
        # Add field with validation
        line_edit = ValidatedLineEdit()
        line_edit.add_validator(lambda x: (bool(x.strip()), "Field required"))
        form.add_field("Required Field", line_edit, "required_field")
        
        # Test invalid form
        line_edit.setText("")
        is_valid, errors = form.validate_form()
        assert not is_valid
        assert len(errors) > 0
        
        # Test valid form
        line_edit.setText("Valid value")
        is_valid, errors = form.validate_form()
        assert is_valid
        assert len(errors) == 0
        
        form.deleteLater()
    
    def test_form_container_clear(self):
        """Test clearing form"""
        form = FormContainer()
        
        # Add and populate fields
        line_edit = ValidatedLineEdit()
        line_edit.setText("Test")
        form.add_field("Text", line_edit, "text")
        
        spin_box = ValidatedSpinBox()
        spin_box.setValue(10)
        form.add_field("Number", spin_box, "number")
        
        # Clear form
        form.clear_form()
        
        assert line_edit.text() == ""
        # The spin box should be reset to its minimum value (0 in this case)
        assert spin_box.value() == 0
        
        form.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__])