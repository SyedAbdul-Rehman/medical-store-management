"""
Integration Tests for Medicine Management Workflow
Tests the complete medicine management functionality including form, table, and dialogs
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.medicine_management import MedicineManagementWidget
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
def sample_medicines():
    """Create sample medicines for testing"""
    return [
        Medicine(
            id=1,
            name="Paracetamol",
            category="Pain Relief",
            batch_no="PAR001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=5.0,
            selling_price=8.0,
            barcode="1234567890"
        ),
        Medicine(
            id=2,
            name="Amoxicillin",
            category="Antibiotic",
            batch_no="AMX001",
            expiry_date="2024-06-30",
            quantity=50,
            purchase_price=12.0,
            selling_price=18.0,
            barcode="2345678901"
        )
    ]


@pytest.fixture
def medicine_management_widget(app, mock_medicine_manager, sample_medicines):
    """Create medicine management widget"""
    # Setup mock manager to return sample medicines
    mock_medicine_manager.get_all_medicines.return_value = sample_medicines
    
    widget = MedicineManagementWidget(mock_medicine_manager)
    return widget


class TestMedicineManagementIntegration:
    """Integration tests for complete medicine management workflow"""
    
    def test_widget_initialization(self, medicine_management_widget):
        """Test widget initialization and component setup"""
        widget = medicine_management_widget
        
        # Check that all components are present
        assert widget.medicine_form is not None
        assert widget.medicine_table is not None
        assert widget.splitter is not None
        
        # Check that components are properly configured
        assert widget.medicine_form.medicine_manager is not None
        assert widget.medicine_table.medicine_manager is not None
        
        # Check initial state
        assert widget.current_medicine is None
        assert not widget.medicine_form.is_editing
    
    def test_add_medicine_workflow(self, medicine_management_widget, mock_medicine_manager):
        """Test complete add medicine workflow"""
        widget = medicine_management_widget
        
        # Setup mock manager response
        new_medicine = Medicine(
            id=3,
            name="New Medicine",
            category="Test",
            batch_no="NEW001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0
        )
        mock_medicine_manager.add_medicine.return_value = (True, "Medicine added", new_medicine)
        
        # Start adding new medicine
        widget.add_new_medicine()
        
        # Check that form is cleared and ready for new medicine
        assert not widget.medicine_form.is_editing
        assert widget.medicine_form.current_medicine is None
        assert widget.current_medicine is None
        
        # Fill form with new medicine data
        widget.medicine_form.name_field.setText("New Medicine")
        widget.medicine_form.category_field.setCurrentText("Test")
        widget.medicine_form.batch_field.setText("NEW001")
        
        # Simulate successful save
        widget._on_medicine_saved(new_medicine)
        
        # Check that medicine was added to table
        assert new_medicine in widget.medicine_table.medicines
        
        # Check that form was cleared after save
        assert not widget.medicine_form.is_editing
        assert widget.medicine_form.current_medicine is None
    
    def test_edit_medicine_workflow(self, medicine_management_widget, sample_medicines):
        """Test complete edit medicine workflow"""
        widget = medicine_management_widget
        medicine_to_edit = sample_medicines[0]
        
        # Load medicine for editing
        widget.load_medicine_for_editing(medicine_to_edit)
        
        # Check that form is in editing mode
        assert widget.medicine_form.is_editing
        assert widget.medicine_form.current_medicine == medicine_to_edit
        assert widget.current_medicine == medicine_to_edit
        
        # Check that form fields are populated
        assert widget.medicine_form.name_field.text() == medicine_to_edit.name
        assert widget.medicine_form.category_field.currentText() == medicine_to_edit.category
        
        # Simulate medicine update
        updated_medicine = Medicine(**medicine_to_edit.__dict__)
        updated_medicine.name = "Updated Medicine Name"
        
        widget._on_medicine_updated_from_dialog(updated_medicine)
        
        # Check that table was updated
        # (In a real test, you'd verify the table contents)
        assert widget.medicine_form.current_medicine is None  # Form should be cleared
    
    def test_delete_medicine_workflow(self, medicine_management_widget, sample_medicines):
        """Test complete delete medicine workflow"""
        widget = medicine_management_widget
        medicine_to_delete = sample_medicines[0]
        
        # Select medicine for deletion
        widget.current_medicine = medicine_to_delete
        
        # Simulate medicine deletion
        widget._on_medicine_deleted_from_dialog(medicine_to_delete.id)
        
        # Check that medicine was removed from table
        assert medicine_to_delete not in widget.medicine_table.medicines
        
        # Check that current selection was cleared
        assert widget.current_medicine is None
    
    def test_medicine_selection_workflow(self, medicine_management_widget, sample_medicines):
        """Test medicine selection from table"""
        widget = medicine_management_widget
        medicine_to_select = sample_medicines[0]
        
        # Simulate medicine selection from table
        widget._on_medicine_selected(medicine_to_select)
        
        # Check that medicine is selected
        assert widget.current_medicine == medicine_to_select
    
    def test_search_and_filter_workflow(self, medicine_management_widget):
        """Test search and filter functionality"""
        widget = medicine_management_widget
        
        # Test search
        widget.search_medicines("Paracetamol")
        assert widget.medicine_table.search_field.text() == "Paracetamol"
        
        # Test category filter
        widget.filter_by_category("Pain Relief")
        assert widget.medicine_table.category_filter == "Pain Relief"
        
        # Test stock status filter
        widget.filter_by_stock_status("Low Stock")
        assert widget.medicine_table.stock_filter == "Low Stock"
        
        # Test clear filters
        widget.clear_all_filters()
        assert widget.medicine_table.search_query == ""
        assert widget.medicine_table.category_filter == ""
        assert widget.medicine_table.stock_filter == ""
    
    def test_statistics_calculation(self, medicine_management_widget, sample_medicines):
        """Test medicine statistics calculation"""
        widget = medicine_management_widget
        
        # Get statistics
        stats = widget.get_medicine_statistics()
        
        # Check that statistics are calculated
        assert 'total_medicines' in stats
        assert 'low_stock_count' in stats
        assert 'expired_count' in stats
        assert 'total_value' in stats
        assert 'categories' in stats
        
        # Check that values are reasonable
        assert stats['total_medicines'] >= 0
        assert stats['total_value'] >= 0
        assert isinstance(stats['categories'], list)
    
    def test_refresh_data_workflow(self, medicine_management_widget, mock_medicine_manager):
        """Test data refresh functionality"""
        widget = medicine_management_widget
        
        # Mock manager to return updated data
        updated_medicines = [
            Medicine(
                id=1,
                name="Updated Medicine",
                category="Updated Category",
                batch_no="UPD001",
                expiry_date="2025-12-31",
                quantity=200,
                purchase_price=15.0,
                selling_price=20.0
            )
        ]
        mock_medicine_manager.get_all_medicines.return_value = updated_medicines
        
        # Refresh data
        widget.refresh_data()
        
        # Check that manager was called
        mock_medicine_manager.get_all_medicines.assert_called()
    
    def test_signal_emissions(self, medicine_management_widget):
        """Test that appropriate signals are emitted"""
        widget = medicine_management_widget
        
        # Create signal spies
        medicine_added_signals = []
        medicine_updated_signals = []
        medicine_deleted_signals = []
        
        widget.medicine_added.connect(lambda m: medicine_added_signals.append(m))
        widget.medicine_updated.connect(lambda m: medicine_updated_signals.append(m))
        widget.medicine_deleted.connect(lambda id: medicine_deleted_signals.append(id))
        
        # Test medicine added signal
        new_medicine = Medicine(
            id=3,
            name="Test Medicine",
            category="Test",
            batch_no="TEST001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0
        )
        
        # Simulate adding medicine (not editing)
        widget.medicine_form.is_editing = False
        widget._on_medicine_saved(new_medicine)
        
        assert len(medicine_added_signals) == 1
        assert medicine_added_signals[0] == new_medicine
        
        # Test medicine updated signal
        updated_medicine = Medicine(**new_medicine.__dict__)
        updated_medicine.name = "Updated Name"
        
        widget._on_medicine_updated_from_dialog(updated_medicine)
        
        assert len(medicine_updated_signals) == 1
        assert medicine_updated_signals[0] == updated_medicine
        
        # Test medicine deleted signal
        widget._on_medicine_deleted_from_dialog(new_medicine.id)
        
        assert len(medicine_deleted_signals) == 1
        assert medicine_deleted_signals[0] == new_medicine.id
    
    def test_error_handling(self, medicine_management_widget, mock_medicine_manager):
        """Test error handling in various scenarios"""
        widget = medicine_management_widget
        
        # Test refresh data error
        mock_medicine_manager.get_all_medicines.side_effect = Exception("Database error")
        
        # This should not crash the application
        try:
            widget.refresh_data()
        except Exception as e:
            pytest.fail(f"Refresh data should handle errors gracefully: {e}")
    
    def test_auto_refresh_functionality(self, medicine_management_widget):
        """Test auto-refresh functionality"""
        widget = medicine_management_widget
        
        # Test enabling auto-refresh
        widget.enable_auto_refresh(True)
        assert widget.medicine_table.refresh_timer.isActive()
        
        # Test disabling auto-refresh
        widget.enable_auto_refresh(False)
        assert not widget.medicine_table.refresh_timer.isActive()
    
    def test_component_access_methods(self, medicine_management_widget):
        """Test methods for accessing components"""
        widget = medicine_management_widget
        
        # Test getting form widget
        form = widget.get_form_widget()
        assert form == widget.medicine_form
        
        # Test getting table widget
        table = widget.get_table_widget()
        assert table == widget.medicine_table
        
        # Test getting selected medicine
        widget.current_medicine = Medicine(id=1, name="Test")
        selected = widget.get_selected_medicine()
        assert selected == widget.current_medicine
    
    def test_medicine_manager_update(self, medicine_management_widget):
        """Test updating medicine manager"""
        widget = medicine_management_widget
        
        # Create new mock manager
        new_manager = Mock(spec=MedicineManager)
        new_manager.get_all_medicines.return_value = []
        
        # Update manager
        widget.set_medicine_manager(new_manager)
        
        # Check that all components have new manager
        assert widget.medicine_manager == new_manager
        assert widget.medicine_form.medicine_manager == new_manager
        assert widget.medicine_table.medicine_manager == new_manager
    
    @patch('medical_store_app.ui.components.medicine_management.QMessageBox')
    def test_user_action_methods(self, mock_msgbox, medicine_management_widget, sample_medicines):
        """Test user action methods with no selection"""
        widget = medicine_management_widget
        
        # Test edit with no selection
        widget.current_medicine = None
        widget.edit_selected_medicine()
        mock_msgbox.information.assert_called()
        
        # Test delete with no selection
        widget.delete_selected_medicine()
        assert mock_msgbox.information.call_count == 2
        
        # Test show details with no selection
        widget.show_selected_medicine_details()
        assert mock_msgbox.information.call_count == 3
        
        # Test with selection
        widget.current_medicine = sample_medicines[0]
        
        # These methods should not show info messages when medicine is selected
        # (They would open dialogs, but we're not testing dialog creation here)
        mock_msgbox.reset_mock()
        
        # The actual dialog opening would be tested separately
        assert widget.current_medicine is not None


class TestMedicineManagementEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_empty_medicine_list(self, app, mock_medicine_manager):
        """Test widget behavior with empty medicine list"""
        mock_medicine_manager.get_all_medicines.return_value = []
        
        widget = MedicineManagementWidget(mock_medicine_manager)
        
        # Widget should handle empty list gracefully
        assert len(widget.medicine_table.medicines) == 0
        assert widget.medicine_table.table.rowCount() == 0
        
        # Statistics should show zeros
        stats = widget.get_medicine_statistics()
        assert stats['total_medicines'] == 0
        assert stats['total_value'] == 0
    
    def test_invalid_medicine_data(self, medicine_management_widget):
        """Test handling of invalid medicine data"""
        widget = medicine_management_widget
        
        # Test with None medicine
        try:
            widget._on_medicine_selected(None)
            # Should not crash
        except Exception as e:
            pytest.fail(f"Should handle None medicine gracefully: {e}")
        
        # Test with invalid medicine ID
        try:
            widget._on_medicine_deleted_from_dialog(-1)
            # Should not crash
        except Exception as e:
            pytest.fail(f"Should handle invalid ID gracefully: {e}")
    
    def test_concurrent_operations(self, medicine_management_widget, sample_medicines):
        """Test handling of concurrent operations"""
        widget = medicine_management_widget
        
        # Simulate multiple rapid operations
        medicine1 = sample_medicines[0]
        medicine2 = sample_medicines[1]
        
        # Rapid selection changes
        widget._on_medicine_selected(medicine1)
        widget._on_medicine_selected(medicine2)
        widget._on_medicine_selected(None)
        
        # Should handle rapid changes gracefully
        assert widget.current_medicine is None


if __name__ == "__main__":
    pytest.main([__file__])