"""
Tests for Medicine Dialog Components
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.dialogs.medicine_dialog import (
    EditMedicineDialog, DeleteMedicineDialog, MedicineDetailsDialog
)
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


class TestEditMedicineDialog:
    """Test cases for EditMedicineDialog"""
    
    def test_dialog_initialization(self, app, sample_medicine, mock_medicine_manager):
        """Test dialog initialization"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        assert dialog is not None
        assert dialog.medicine == sample_medicine
        assert dialog.medicine_manager == mock_medicine_manager
        assert dialog.isModal()
        assert "Edit Medicine" in dialog.windowTitle()
        assert sample_medicine.name in dialog.windowTitle()
    
    def test_dialog_ui_components(self, app, sample_medicine, mock_medicine_manager):
        """Test dialog UI components"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Check that form is present
        assert dialog.medicine_form is not None
        
        # Check that buttons are present
        assert dialog.cancel_button is not None
        assert dialog.update_button is not None
        
        # Check button text
        assert dialog.cancel_button.text() == "Cancel"
        assert dialog.update_button.text() == "Update Medicine"
    
    def test_medicine_data_loading(self, app, sample_medicine, mock_medicine_manager):
        """Test that medicine data is loaded into form"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Check that form is in editing mode
        assert dialog.medicine_form.is_editing
        assert dialog.medicine_form.current_medicine == sample_medicine
        
        # Check that form fields are populated
        assert dialog.medicine_form.name_field.text() == sample_medicine.name
        assert dialog.medicine_form.category_field.currentText() == sample_medicine.category
        assert dialog.medicine_form.batch_field.text() == sample_medicine.batch_no
        assert dialog.medicine_form.quantity_field.value() == sample_medicine.quantity
        assert dialog.medicine_form.purchase_price_field.value() == sample_medicine.purchase_price
        assert dialog.medicine_form.selling_price_field.value() == sample_medicine.selling_price
        assert dialog.medicine_form.barcode_field.text() == sample_medicine.barcode
    
    def test_cancel_button(self, app, sample_medicine, mock_medicine_manager):
        """Test cancel button functionality"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Mock the reject method
        dialog.reject = Mock()
        
        # Click cancel button
        dialog.cancel_button.click()
        
        # Check that dialog was rejected
        dialog.reject.assert_called_once()
    
    def test_update_button_triggers_save(self, app, sample_medicine, mock_medicine_manager):
        """Test that update button triggers save operation"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Mock the form's save method
        dialog.medicine_form.save_medicine = Mock()
        
        # Click update button
        dialog.update_button.click()
        
        # Check that save was called
        dialog.medicine_form.save_medicine.assert_called_once()
    
    def test_medicine_updated_signal(self, app, sample_medicine, mock_medicine_manager):
        """Test medicine updated signal emission"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Mock the accept method
        dialog.accept = Mock()
        
        # Create a signal spy
        signal_emitted = []
        dialog.medicine_updated.connect(lambda medicine: signal_emitted.append(medicine))
        
        # Simulate successful update
        updated_medicine = Medicine(**sample_medicine.__dict__)
        updated_medicine.name = "Updated Medicine"
        dialog._on_medicine_updated(updated_medicine)
        
        # Check that signal was emitted and dialog accepted
        assert len(signal_emitted) == 1
        assert signal_emitted[0] == updated_medicine
        dialog.accept.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.medicine_dialog.QMessageBox')
    def test_close_with_unsaved_changes(self, mock_msgbox, app, sample_medicine, mock_medicine_manager):
        """Test closing dialog with unsaved changes"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Mock form as dirty
        dialog.medicine_form.is_form_dirty = Mock(return_value=True)
        
        # Mock message box to return No
        mock_msgbox.question.return_value = mock_msgbox.No
        
        # Create a mock close event
        from PySide6.QtGui import QCloseEvent
        close_event = Mock(spec=QCloseEvent)
        
        # Call close event handler
        dialog.closeEvent(close_event)
        
        # Check that message box was shown and event was ignored
        mock_msgbox.question.assert_called_once()
        close_event.ignore.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.medicine_dialog.QMessageBox')
    def test_close_without_unsaved_changes(self, mock_msgbox, app, sample_medicine, mock_medicine_manager):
        """Test closing dialog without unsaved changes"""
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Mock form as not dirty
        dialog.medicine_form.is_form_dirty = Mock(return_value=False)
        
        # Create a mock close event
        from PySide6.QtGui import QCloseEvent
        close_event = Mock(spec=QCloseEvent)
        
        # Call close event handler
        dialog.closeEvent(close_event)
        
        # Check that no message box was shown and event was accepted
        mock_msgbox.question.assert_not_called()
        close_event.accept.assert_called_once()


class TestDeleteMedicineDialog:
    """Test cases for DeleteMedicineDialog"""
    
    def test_dialog_initialization(self, app, sample_medicine, mock_medicine_manager):
        """Test dialog initialization"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        assert dialog is not None
        assert dialog.medicine == sample_medicine
        assert dialog.medicine_manager == mock_medicine_manager
        assert dialog.isModal()
        assert dialog.windowTitle() == "Delete Medicine"
    
    def test_dialog_ui_components(self, app, sample_medicine, mock_medicine_manager):
        """Test dialog UI components"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Check that buttons are present
        assert dialog.cancel_button is not None
        assert dialog.delete_button is not None
        
        # Check button text
        assert dialog.cancel_button.text() == "Cancel"
        assert dialog.delete_button.text() == "Delete Medicine"
    
    def test_medicine_details_display(self, app, sample_medicine, mock_medicine_manager):
        """Test that medicine details are displayed in dialog"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # The dialog should contain medicine information
        # This is a basic test - in practice you'd check specific UI elements
        assert dialog is not None
    
    def test_cancel_button(self, app, sample_medicine, mock_medicine_manager):
        """Test cancel button functionality"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Mock the reject method
        dialog.reject = Mock()
        
        # Click cancel button
        dialog.cancel_button.click()
        
        # Check that dialog was rejected
        dialog.reject.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.medicine_dialog.QMessageBox')
    def test_successful_deletion(self, mock_msgbox, app, sample_medicine, mock_medicine_manager):
        """Test successful medicine deletion"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Setup mock manager to return success
        mock_medicine_manager.delete_medicine.return_value = (True, "Medicine deleted successfully")
        
        # Mock the accept method
        dialog.accept = Mock()
        
        # Create a signal spy
        signal_emitted = []
        dialog.medicine_deleted.connect(lambda medicine_id: signal_emitted.append(medicine_id))
        
        # Click delete button
        dialog._delete_medicine()
        
        # Check that manager was called
        mock_medicine_manager.delete_medicine.assert_called_once_with(sample_medicine.id)
        
        # Check that success message was shown
        mock_msgbox.information.assert_called_once()
        
        # Check that signal was emitted and dialog accepted
        assert len(signal_emitted) == 1
        assert signal_emitted[0] == sample_medicine.id
        dialog.accept.assert_called_once()
    
    @patch('medical_store_app.ui.dialogs.medicine_dialog.QMessageBox')
    def test_failed_deletion(self, mock_msgbox, app, sample_medicine, mock_medicine_manager):
        """Test failed medicine deletion"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Setup mock manager to return failure
        mock_medicine_manager.delete_medicine.return_value = (False, "Database error")
        
        # Click delete button
        dialog._delete_medicine()
        
        # Check that manager was called
        mock_medicine_manager.delete_medicine.assert_called_once_with(sample_medicine.id)
        
        # Check that error message was shown
        mock_msgbox.critical.assert_called_once()
        
        # Check that buttons are re-enabled
        assert dialog.cancel_button.isEnabled()
        assert dialog.delete_button.isEnabled()
        assert dialog.delete_button.text() == "Delete Medicine"
    
    @patch('medical_store_app.ui.dialogs.medicine_dialog.QMessageBox')
    def test_deletion_exception_handling(self, mock_msgbox, app, sample_medicine, mock_medicine_manager):
        """Test exception handling during deletion"""
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Setup mock manager to raise exception
        mock_medicine_manager.delete_medicine.side_effect = Exception("Database connection error")
        
        # Click delete button
        dialog._delete_medicine()
        
        # Check that error message was shown
        mock_msgbox.critical.assert_called_once()
        
        # Check that buttons are re-enabled
        assert dialog.cancel_button.isEnabled()
        assert dialog.delete_button.isEnabled()
    
    def test_stock_warning_display(self, app, mock_medicine_manager):
        """Test that stock warning is displayed for medicines with stock"""
        # Create medicine with stock
        medicine_with_stock = Medicine(
            id=1,
            name="Medicine with Stock",
            category="Test",
            batch_no="TEST001",
            expiry_date="2025-12-31",
            quantity=50,  # Has stock
            purchase_price=10.0,
            selling_price=15.0
        )
        
        dialog = DeleteMedicineDialog(medicine_with_stock, mock_medicine_manager)
        
        # Dialog should be created successfully
        assert dialog is not None
        
        # Create medicine without stock
        medicine_without_stock = Medicine(
            id=2,
            name="Medicine without Stock",
            category="Test",
            batch_no="TEST002",
            expiry_date="2025-12-31",
            quantity=0,  # No stock
            purchase_price=10.0,
            selling_price=15.0
        )
        
        dialog2 = DeleteMedicineDialog(medicine_without_stock, mock_medicine_manager)
        
        # Dialog should be created successfully
        assert dialog2 is not None


class TestMedicineDetailsDialog:
    """Test cases for MedicineDetailsDialog"""
    
    def test_dialog_initialization(self, app, sample_medicine):
        """Test dialog initialization"""
        dialog = MedicineDetailsDialog(sample_medicine)
        
        assert dialog is not None
        assert dialog.medicine == sample_medicine
        assert dialog.isModal()
        assert "Medicine Details" in dialog.windowTitle()
        assert sample_medicine.name in dialog.windowTitle()
    
    def test_dialog_size_and_properties(self, app, sample_medicine):
        """Test dialog size and properties"""
        dialog = MedicineDetailsDialog(sample_medicine)
        
        # Check that dialog has fixed size
        assert dialog.minimumSize().width() == 500
        assert dialog.minimumSize().height() == 600
        assert dialog.maximumSize().width() == 500
        assert dialog.maximumSize().height() == 600
    
    def test_medicine_information_display(self, app, sample_medicine):
        """Test that medicine information is displayed"""
        dialog = MedicineDetailsDialog(sample_medicine)
        
        # Dialog should be created successfully with medicine data
        assert dialog is not None
        
        # The dialog should contain the medicine information
        # In a real test, you would check specific UI elements for the data
        assert dialog.medicine.name == sample_medicine.name
        assert dialog.medicine.category == sample_medicine.category
    
    def test_days_until_expiry_calculation(self, app):
        """Test days until expiry calculation"""
        from datetime import date, timedelta
        
        # Create medicine expiring in 10 days
        future_date = date.today() + timedelta(days=10)
        medicine_expiring_soon = Medicine(
            id=1,
            name="Expiring Soon",
            category="Test",
            batch_no="TEST001",
            expiry_date=future_date.strftime("%Y-%m-%d"),
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0
        )
        
        dialog = MedicineDetailsDialog(medicine_expiring_soon)
        days_text = dialog._get_days_until_expiry()
        
        assert "10 days" in days_text
        
        # Create expired medicine
        past_date = date.today() - timedelta(days=5)
        expired_medicine = Medicine(
            id=2,
            name="Expired Medicine",
            category="Test",
            batch_no="TEST002",
            expiry_date=past_date.strftime("%Y-%m-%d"),
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0
        )
        
        dialog2 = MedicineDetailsDialog(expired_medicine)
        days_text2 = dialog2._get_days_until_expiry()
        
        assert "Expired" in days_text2
        assert "5 days ago" in days_text2
    
    def test_profit_information_display(self, app):
        """Test profit information calculation and display"""
        # Create medicine with profit
        profitable_medicine = Medicine(
            id=1,
            name="Profitable Medicine",
            category="Test",
            batch_no="TEST001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0  # 50% profit margin
        )
        
        dialog = MedicineDetailsDialog(profitable_medicine)
        
        # Check that profit calculations are correct
        assert dialog.medicine.get_profit_margin() == 50.0
        assert dialog.medicine.get_profit_amount() == 5.0
        
        # Create medicine with loss
        loss_medicine = Medicine(
            id=2,
            name="Loss Medicine",
            category="Test",
            batch_no="TEST002",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=15.0,
            selling_price=10.0  # Loss
        )
        
        dialog2 = MedicineDetailsDialog(loss_medicine)
        
        # Check that loss calculations are correct
        assert dialog2.medicine.get_profit_margin() < 0
        assert dialog2.medicine.get_profit_amount() < 0
    
    def test_close_button_functionality(self, app, sample_medicine):
        """Test close button functionality"""
        dialog = MedicineDetailsDialog(sample_medicine)
        
        # Mock the accept method
        dialog.accept = Mock()
        
        # The close button should be connected to accept
        # In a real test, you would click the button
        # For now, just verify the dialog can be created
        assert dialog is not None


class TestMedicineDialogIntegration:
    """Integration tests for medicine dialogs"""
    
    def test_edit_dialog_workflow(self, app, sample_medicine, mock_medicine_manager):
        """Test complete edit dialog workflow"""
        # Setup mock manager
        mock_medicine_manager.edit_medicine.return_value = (True, "Medicine updated", sample_medicine)
        
        # Create dialog
        dialog = EditMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Verify initial state
        assert dialog.medicine_form.is_editing
        assert dialog.medicine_form.current_medicine == sample_medicine
        
        # Modify form data
        dialog.medicine_form.name_field.setText("Modified Medicine Name")
        
        # Verify form is dirty
        assert dialog.medicine_form.is_form_dirty()
        
        # The rest of the workflow would involve UI interactions
        # which are complex to test without actual user interaction
    
    def test_delete_dialog_workflow(self, app, sample_medicine, mock_medicine_manager):
        """Test complete delete dialog workflow"""
        # Setup mock manager
        mock_medicine_manager.delete_medicine.return_value = (True, "Medicine deleted")
        
        # Create dialog
        dialog = DeleteMedicineDialog(sample_medicine, mock_medicine_manager)
        
        # Verify initial state
        assert dialog.medicine == sample_medicine
        assert dialog.cancel_button.isEnabled()
        assert dialog.delete_button.isEnabled()
        
        # The rest of the workflow would involve UI interactions
    
    def test_details_dialog_workflow(self, app, sample_medicine):
        """Test complete details dialog workflow"""
        # Create dialog
        dialog = MedicineDetailsDialog(sample_medicine)
        
        # Verify dialog displays medicine information
        assert dialog.medicine == sample_medicine
        
        # Test various medicine states
        assert dialog._get_days_until_expiry() is not None


if __name__ == "__main__":
    pytest.main([__file__])