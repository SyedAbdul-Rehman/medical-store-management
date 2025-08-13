"""
Tests for Medicine Form Bug Fixes
Tests for Bug 1: Validation warnings after saving
Tests for Bug 2: Category dropdown disappearing after saving
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDate
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.medicine_form import MedicineForm
from medical_store_app.models.medicine import Medicine


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def mock_medicine_manager():
    """Create mock medicine manager"""
    manager = Mock()
    manager.add_medicine.return_value = (True, "Medicine added successfully", Mock(id=1, name="Test Medicine"))
    manager.edit_medicine.return_value = (True, "Medicine updated successfully", Mock(id=1, name="Test Medicine"))
    return manager


@pytest.fixture
def medicine_form(qapp, mock_medicine_manager):
    """Create medicine form for testing"""
    form = MedicineForm(mock_medicine_manager)
    return form


class TestMedicineFormBugFixes:
    """Test cases for medicine form bug fixes"""
    
    def test_bug1_validation_messages_cleared_after_save(self, medicine_form):
        """
        Bug 1: Test that validation warnings are cleared after saving
        and don't appear immediately after form clearing
        """
        # Fill out the form with valid data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("BATCH001")
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(5.0)
        medicine_form.selling_price_field.setValue(8.0)
        
        # Simulate saving the medicine
        medicine_form.save_medicine()
        
        # Wait for the operation to complete (simulate async operation)
        medicine_form._on_operation_finished(True, "Medicine added successfully", Mock(id=1, name="Test Medicine"))
        
        # Check that form is cleared
        assert medicine_form.name_field.text() == ""
        assert medicine_form.batch_field.text() == ""
        
        # Check that no validation error messages are visible
        assert not medicine_form.name_field.error_label.isVisible()
        assert not medicine_form.category_field.error_label.isVisible()
        assert not medicine_form.batch_field.error_label.isVisible()
        
        # Check that error labels are empty
        assert medicine_form.name_field.error_label.text() == ""
        assert medicine_form.category_field.error_label.text() == ""
        assert medicine_form.batch_field.error_label.text() == ""
    
    def test_bug2_category_dropdown_visible_after_save(self, medicine_form):
        """
        Bug 2: Test that category dropdown remains visible and populated after saving
        """
        # Check initial state - category dropdown should be populated
        initial_category_count = medicine_form.category_field.count()
        assert initial_category_count > 0
        assert "Pain Relief" in [medicine_form.category_field.itemText(i) for i in range(initial_category_count)]
        
        # Fill out the form with valid data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("BATCH001")
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(5.0)
        medicine_form.selling_price_field.setValue(8.0)
        
        # Simulate saving the medicine
        medicine_form.save_medicine()
        
        # Wait for the operation to complete
        medicine_form._on_operation_finished(True, "Medicine added successfully", Mock(id=1, name="Test Medicine"))
        
        # Check that category dropdown is still populated with all categories
        after_save_count = medicine_form.category_field.count()
        assert after_save_count == initial_category_count
        assert after_save_count > 0
        
        # Check that all original categories are still there
        categories_after_save = [medicine_form.category_field.itemText(i) for i in range(after_save_count)]
        assert "Pain Relief" in categories_after_save
        assert "Antibiotic" in categories_after_save
        assert "Vitamins & Supplements" in categories_after_save
        
        # Check that the dropdown is visible and functional
        assert medicine_form.category_field.isVisible()
        assert medicine_form.category_field.isEnabled()
        
        # Check that the dropdown shows placeholder text (no selection)
        if medicine_form.category_field.isEditable():
            assert medicine_form.category_field.currentText() == "" or medicine_form.category_field.currentIndex() == -1
    
    def test_multiple_saves_in_row(self, medicine_form):
        """
        Test adding multiple medicines in a row to ensure both bugs are fixed
        """
        medicines_data = [
            ("Medicine 1", "Pain Relief", "BATCH001"),
            ("Medicine 2", "Antibiotic", "BATCH002"),
            ("Medicine 3", "Vitamins & Supplements", "BATCH003")
        ]
        
        for i, (name, category, batch) in enumerate(medicines_data):
            # Fill out the form
            medicine_form.name_field.setText(name)
            medicine_form.category_field.setCurrentText(category)
            medicine_form.batch_field.setText(batch)
            medicine_form.quantity_field.setValue(50 + i * 10)
            medicine_form.purchase_price_field.setValue(5.0 + i)
            medicine_form.selling_price_field.setValue(8.0 + i)
            
            # Save the medicine
            medicine_form.save_medicine()
            medicine_form._on_operation_finished(True, f"Medicine {i+1} added successfully", Mock(id=i+1, name=name))
            
            # After each save, check that:
            # 1. Form is cleared
            assert medicine_form.name_field.text() == ""
            assert medicine_form.batch_field.text() == ""
            
            # 2. No validation errors are shown
            assert not medicine_form.name_field.error_label.isVisible()
            assert not medicine_form.category_field.error_label.isVisible()
            assert not medicine_form.batch_field.error_label.isVisible()
            
            # 3. Category dropdown is still populated and functional
            assert medicine_form.category_field.count() > 0
            assert medicine_form.category_field.isVisible()
            assert medicine_form.category_field.isEnabled()
            
            # 4. Can select categories for next iteration
            categories = [medicine_form.category_field.itemText(j) for j in range(medicine_form.category_field.count())]
            assert "Pain Relief" in categories
            assert "Antibiotic" in categories
    
    def test_form_validation_still_works_after_clear(self, medicine_form):
        """
        Test that validation still works properly after clearing the form
        """
        # Fill and save a medicine first
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("BATCH001")
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(5.0)
        medicine_form.selling_price_field.setValue(8.0)
        
        medicine_form.save_medicine()
        medicine_form._on_operation_finished(True, "Medicine added successfully", Mock(id=1, name="Test Medicine"))
        
        # Now try to save without filling required fields
        # This should trigger validation errors
        medicine_form.save_medicine()
        
        # Validation should prevent saving and show errors when user tries to save
        # The save operation should not proceed due to validation
        # We can't easily test the QMessageBox, but we can verify the form validation
        is_valid, errors = medicine_form.form_container.validate_form()
        assert not is_valid
        assert len(errors) > 0
    
    def test_category_dropdown_editable_functionality(self, medicine_form):
        """
        Test that the category dropdown remains editable and functional after clearing
        """
        # Test that category field is editable
        assert medicine_form.category_field.isEditable()
        
        # Add a custom category
        custom_category = "Custom Category"
        medicine_form.category_field.setEditText(custom_category)
        
        # Fill other required fields
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.batch_field.setText("BATCH001")
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(5.0)
        medicine_form.selling_price_field.setValue(8.0)
        
        # Save the medicine
        medicine_form.save_medicine()
        medicine_form._on_operation_finished(True, "Medicine added successfully", Mock(id=1, name="Test Medicine"))
        
        # After clearing, the dropdown should still be editable
        assert medicine_form.category_field.isEditable()
        
        # Should be able to type in custom categories again
        another_custom = "Another Custom"
        medicine_form.category_field.setEditText(another_custom)
        assert medicine_form.category_field.currentText() == another_custom
    
    def test_clear_form_method_directly(self, medicine_form):
        """
        Test the clear_form method directly to ensure it properly resets everything
        """
        # Fill the form with data
        medicine_form.name_field.setText("Test Medicine")
        medicine_form.category_field.setCurrentText("Pain Relief")
        medicine_form.batch_field.setText("BATCH001")
        medicine_form.quantity_field.setValue(100)
        medicine_form.purchase_price_field.setValue(5.0)
        medicine_form.selling_price_field.setValue(8.0)
        medicine_form.barcode_field.setText("123456789")
        
        # Manually trigger validation to show some errors (by clearing required fields first)
        medicine_form.name_field.setText("")
        medicine_form.name_field._on_text_changed("")  # Trigger validation
        
        # Verify error is shown
        assert medicine_form.name_field.error_label.isVisible()
        
        # Now clear the form
        medicine_form.clear_form()
        
        # Check that all fields are cleared
        assert medicine_form.name_field.text() == ""
        assert medicine_form.batch_field.text() == ""
        assert medicine_form.barcode_field.text() == ""
        
        # Check that validation errors are cleared
        assert not medicine_form.name_field.error_label.isVisible()
        assert not medicine_form.category_field.error_label.isVisible()
        assert not medicine_form.batch_field.error_label.isVisible()
        
        # Check that category dropdown is repopulated
        assert medicine_form.category_field.count() > 0
        categories = [medicine_form.category_field.itemText(i) for i in range(medicine_form.category_field.count())]
        assert "Pain Relief" in categories
        
        # Check form state is reset
        assert not medicine_form.is_editing
        assert medicine_form.current_medicine is None
        assert medicine_form.save_button.text() == "Save Medicine"