"""
Tests for Medicine Deletion Bug Fix
Tests that medicine deletion properly updates selection state
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.medicine_table import MedicineTableWidget
from medical_store_app.ui.components.medicine_management import MedicineManagementWidget
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
def sample_medicines():
    """Create sample medicine data for testing"""
    medicines = [
        Medicine(
            id=1, name="Medicine A", category="Pain Relief", batch_no="BATCH001",
            expiry_date="2025-12-31", quantity=100, purchase_price=5.0, selling_price=8.0,
            barcode="123456789", created_at="2024-01-01"
        ),
        Medicine(
            id=2, name="Medicine B", category="Antibiotic", batch_no="BATCH002",
            expiry_date="2025-06-30", quantity=50, purchase_price=12.0, selling_price=18.0,
            barcode="987654321", created_at="2024-01-15"
        ),
        Medicine(
            id=3, name="Medicine C", category="Supplement", batch_no="BATCH003",
            expiry_date="2025-03-15", quantity=75, purchase_price=8.0, selling_price=12.0,
            barcode="456789123", created_at="2024-02-01"
        )
    ]
    return medicines


@pytest.fixture
def mock_medicine_manager(sample_medicines):
    """Create mock medicine manager"""
    manager = Mock()
    manager.get_all_medicines.return_value = sample_medicines.copy()
    manager.delete_medicine.return_value = (True, "Medicine deleted successfully")
    return manager


@pytest.fixture
def medicine_table(qapp, mock_medicine_manager):
    """Create medicine table widget for testing"""
    table = MedicineTableWidget(mock_medicine_manager)
    return table


@pytest.fixture
def medicine_management(qapp, mock_medicine_manager):
    """Create medicine management widget for testing"""
    management = MedicineManagementWidget(mock_medicine_manager)
    return management


class TestMedicineDeletionBugFix:
    """Test cases for medicine deletion bug fix"""
    
    def test_selection_cleared_after_deletion(self, medicine_table, sample_medicines):
        """Test that selection is cleared after deleting a medicine"""
        # Initially, no medicine should be selected
        assert medicine_table.selected_medicine is None
        
        # Simulate selecting the first medicine
        medicine_table.selected_medicine = sample_medicines[0]
        assert medicine_table.selected_medicine.id == 1
        
        # Simulate deleting the selected medicine
        medicine_table.remove_medicine_from_table(1)
        
        # Selection should be cleared
        assert medicine_table.selected_medicine is None
        
        # Medicine should be removed from the list
        medicine_ids = [m.id for m in medicine_table.medicines]
        assert 1 not in medicine_ids
        assert len(medicine_table.medicines) == 2
    
    def test_selection_preserved_when_different_medicine_deleted(self, medicine_table, sample_medicines):
        """Test that selection is preserved when a different medicine is deleted"""
        # Select the first medicine
        medicine_table.selected_medicine = sample_medicines[0]  # ID: 1
        assert medicine_table.selected_medicine.id == 1
        
        # Delete a different medicine (ID: 2)
        medicine_table.remove_medicine_from_table(2)
        
        # Selection should still be the first medicine
        assert medicine_table.selected_medicine is not None
        assert medicine_table.selected_medicine.id == 1
        
        # Only medicine with ID 2 should be removed
        medicine_ids = [m.id for m in medicine_table.medicines]
        assert 1 in medicine_ids
        assert 2 not in medicine_ids
        assert 3 in medicine_ids
    
    def test_multiple_deletions_in_sequence(self, medicine_table, sample_medicines):
        """Test multiple deletions in sequence work correctly"""
        # Select and delete first medicine
        medicine_table.selected_medicine = sample_medicines[0]  # ID: 1
        medicine_table.remove_medicine_from_table(1)
        
        # Selection should be cleared
        assert medicine_table.selected_medicine is None
        
        # Select and delete second medicine
        remaining_medicines = [m for m in sample_medicines if m.id != 1]
        medicine_table.selected_medicine = remaining_medicines[0]  # ID: 2
        medicine_table.remove_medicine_from_table(2)
        
        # Selection should be cleared again
        assert medicine_table.selected_medicine is None
        
        # Only one medicine should remain
        assert len(medicine_table.medicines) == 1
        assert medicine_table.medicines[0].id == 3
    
    def test_management_component_selection_handling(self, medicine_management, sample_medicines):
        """Test that medicine management component handles selection properly"""
        # Initially no medicine selected
        assert medicine_management.current_medicine is None
        
        # Simulate medicine selection
        medicine_management._on_medicine_selected(sample_medicines[0])
        assert medicine_management.current_medicine.id == 1
        
        # Simulate deletion of selected medicine
        medicine_management._on_medicine_deleted_from_dialog(1)
        
        # Current medicine should be cleared
        assert medicine_management.current_medicine is None
    
    def test_delete_selected_medicine_with_no_selection(self, medicine_management):
        """Test delete_selected_medicine when no medicine is selected"""
        # Ensure no medicine is selected
        medicine_management.current_medicine = None
        
        # Mock QMessageBox to capture the warning
        with patch('medical_store_app.ui.components.medicine_management.QMessageBox') as mock_msgbox:
            medicine_management.delete_selected_medicine()
            
            # Should show information dialog
            mock_msgbox.information.assert_called_once()
            args = mock_msgbox.information.call_args[0]
            assert "No Selection" in args[1]
            assert "Please select a medicine to delete" in args[2]
    
    def test_delete_selected_medicine_with_selection(self, medicine_management, sample_medicines):
        """Test delete_selected_medicine when a medicine is selected"""
        # Set current medicine
        medicine_management.current_medicine = sample_medicines[0]
        
        # Mock the delete_medicine method
        with patch.object(medicine_management, 'delete_medicine') as mock_delete:
            medicine_management.delete_selected_medicine()
            
            # Should call delete_medicine with the selected medicine
            mock_delete.assert_called_once_with(sample_medicines[0])
    
    def test_table_selection_signal_emitted_on_clear(self, medicine_table, sample_medicines):
        """Test that medicine_selected signal is emitted when selection is cleared"""
        # Set up signal spy
        signal_emitted = []
        medicine_table.medicine_selected.connect(lambda med: signal_emitted.append(med))
        
        # Select a medicine first
        medicine_table.selected_medicine = sample_medicines[0]
        
        # Delete the selected medicine
        medicine_table.remove_medicine_from_table(1)
        
        # Signal should have been emitted with None
        assert len(signal_emitted) == 1
        assert signal_emitted[0] is None
    
    def test_table_selection_cleared_in_ui(self, medicine_table, sample_medicines):
        """Test that table UI selection is cleared after deletion"""
        # Mock the table's clearSelection method
        with patch.object(medicine_table.table, 'clearSelection') as mock_clear:
            # Select a medicine
            medicine_table.selected_medicine = sample_medicines[0]
            
            # Delete the selected medicine
            medicine_table.remove_medicine_from_table(1)
            
            # clearSelection should have been called
            mock_clear.assert_called_once()
    
    def test_deletion_with_filters_applied(self, medicine_table, sample_medicines):
        """Test deletion works correctly when filters are applied"""
        # Apply a filter (this will update filtered_medicines)
        medicine_table.category_filter = "Pain Relief"
        medicine_table._apply_filters()
        
        # Select a medicine
        medicine_table.selected_medicine = sample_medicines[0]  # Pain Relief medicine
        
        # Delete the selected medicine
        medicine_table.remove_medicine_from_table(1)
        
        # Selection should be cleared
        assert medicine_table.selected_medicine is None
        
        # Medicine should be removed from both main list and filtered list
        medicine_ids = [m.id for m in medicine_table.medicines]
        filtered_ids = [m.id for m in medicine_table.filtered_medicines]
        assert 1 not in medicine_ids
        assert 1 not in filtered_ids
    
    def test_logging_for_deletion_operations(self, medicine_management, sample_medicines, caplog):
        """Test that proper logging occurs during deletion operations"""
        import logging
        
        # Set current medicine
        medicine_management.current_medicine = sample_medicines[0]
        
        # Mock delete_medicine to avoid actual dialog
        with patch.object(medicine_management, 'delete_medicine'):
            with caplog.at_level(logging.INFO):
                medicine_management.delete_selected_medicine()
                
                # Should log the deletion attempt
                assert any("Attempting to delete selected medicine" in record.message 
                          for record in caplog.records)
                assert any("Medicine A" in record.message 
                          for record in caplog.records)
                assert any("ID: 1" in record.message 
                          for record in caplog.records)
        
        # Test logging when no selection
        medicine_management.current_medicine = None
        
        with patch('medical_store_app.ui.components.medicine_management.QMessageBox'):
            with caplog.at_level(logging.WARNING):
                medicine_management.delete_selected_medicine()
                
                # Should log the warning
                assert any("Delete attempted with no medicine selected" in record.message 
                          for record in caplog.records)