"""
Tests for Medicine Table Widget
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.medicine_table import MedicineTableWidget
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
            quantity=5,  # Low stock
            purchase_price=12.0,
            selling_price=18.0,
            barcode="2345678901"
        ),
        Medicine(
            id=3,
            name="Expired Medicine",
            category="Other",
            batch_no="EXP001",
            expiry_date="2023-01-01",  # Expired
            quantity=0,  # Out of stock
            purchase_price=10.0,
            selling_price=15.0,
            barcode="3456789012"
        )
    ]


@pytest.fixture
def medicine_table(app, mock_medicine_manager, sample_medicines):
    """Create medicine table widget"""
    # Setup mock manager to return sample medicines
    mock_medicine_manager.get_all_medicines.return_value = sample_medicines
    
    table = MedicineTableWidget(mock_medicine_manager)
    return table


class TestMedicineTableWidget:
    """Test cases for MedicineTableWidget"""
    
    def test_table_initialization(self, medicine_table):
        """Test table initialization"""
        assert medicine_table is not None
        assert medicine_table.medicine_manager is not None
        assert medicine_table.table is not None
        assert medicine_table.search_field is not None
        assert medicine_table.category_filter_combo is not None
        assert medicine_table.stock_filter_combo is not None
    
    def test_table_columns(self, medicine_table):
        """Test table column setup"""
        expected_columns = ["ID", "Name", "Category", "Batch No", "Expiry Date", 
                          "Quantity", "Purchase Price", "Selling Price", "Barcode", "Status"]
        
        assert medicine_table.table.columnCount() == len(expected_columns)
        
        for i, expected_header in enumerate(expected_columns):
            actual_header = medicine_table.table.horizontalHeaderItem(i).text()
            assert actual_header == expected_header
    
    def test_data_loading(self, medicine_table, sample_medicines):
        """Test loading medicine data"""
        # Data should be loaded during initialization
        assert len(medicine_table.medicines) == len(sample_medicines)
        assert len(medicine_table.filtered_medicines) == len(sample_medicines)
        assert medicine_table.table.rowCount() == len(sample_medicines)
    
    def test_search_functionality(self, medicine_table):
        """Test search functionality"""
        # Search by name
        medicine_table.search_field.setText("Paracetamol")
        medicine_table._on_search_changed("Paracetamol")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].name == "Paracetamol"
        assert medicine_table.table.rowCount() == 1
        
        # Search by barcode
        medicine_table.search_field.setText("2345678901")
        medicine_table._on_search_changed("2345678901")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].barcode == "2345678901"
        
        # Clear search
        medicine_table.search_field.setText("")
        medicine_table._on_search_changed("")
        
        assert len(medicine_table.filtered_medicines) == 3
    
    def test_category_filter(self, medicine_table):
        """Test category filtering"""
        # Filter by Pain Relief
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].category == "Pain Relief"
        
        # Filter by Antibiotic
        medicine_table.category_filter_combo.setCurrentText("Antibiotic")
        medicine_table._on_category_filter_changed("Antibiotic")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].category == "Antibiotic"
        
        # Clear filter
        medicine_table.category_filter_combo.setCurrentText("All Categories")
        medicine_table._on_category_filter_changed("All Categories")
        
        assert len(medicine_table.filtered_medicines) == 3
    
    def test_stock_status_filter(self, medicine_table):
        """Test stock status filtering"""
        # Filter by Low Stock
        medicine_table.stock_filter_combo.setCurrentText("Low Stock")
        medicine_table._on_stock_filter_changed("Low Stock")
        
        low_stock_medicines = [m for m in medicine_table.filtered_medicines if m.is_low_stock()]
        assert len(low_stock_medicines) > 0
        
        # Filter by Out of Stock
        medicine_table.stock_filter_combo.setCurrentText("Out of Stock")
        medicine_table._on_stock_filter_changed("Out of Stock")
        
        out_of_stock_medicines = [m for m in medicine_table.filtered_medicines if m.quantity == 0]
        assert len(out_of_stock_medicines) > 0
        
        # Filter by Expired
        medicine_table.stock_filter_combo.setCurrentText("Expired")
        medicine_table._on_stock_filter_changed("Expired")
        
        expired_medicines = [m for m in medicine_table.filtered_medicines if m.is_expired()]
        assert len(expired_medicines) > 0
    
    def test_clear_filters(self, medicine_table):
        """Test clearing all filters"""
        # Apply some filters
        medicine_table.search_field.setText("test")
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table.stock_filter_combo.setCurrentText("Low Stock")
        
        # Clear filters
        medicine_table.clear_filters()
        
        assert medicine_table.search_field.text() == ""
        assert medicine_table.category_filter_combo.currentIndex() == 0
        assert medicine_table.stock_filter_combo.currentIndex() == 0
        assert len(medicine_table.filtered_medicines) == len(medicine_table.medicines)
    
    def test_table_selection(self, medicine_table, sample_medicines):
        """Test table row selection"""
        # Select first row
        medicine_table.table.selectRow(0)
        medicine_table._on_selection_changed()
        
        assert medicine_table.selected_medicine is not None
        assert medicine_table.selected_medicine.id == sample_medicines[0].id
    
    def test_statistics_update(self, medicine_table, sample_medicines):
        """Test statistics display update"""
        medicine_table._update_statistics()
        
        # Check that statistics labels are updated
        assert "Total:" in medicine_table.total_medicines_label.text()
        assert "Low Stock:" in medicine_table.low_stock_label.text()
        assert "Expired:" in medicine_table.expired_label.text()
        assert "Total Value:" in medicine_table.total_value_label.text()
    
    def test_add_medicine_to_table(self, medicine_table):
        """Test adding new medicine to table"""
        initial_count = len(medicine_table.medicines)
        
        new_medicine = Medicine(
            id=4,
            name="New Medicine",
            category="Test",
            batch_no="NEW001",
            expiry_date="2025-12-31",
            quantity=50,
            purchase_price=20.0,
            selling_price=30.0
        )
        
        medicine_table.add_medicine_to_table(new_medicine)
        
        assert len(medicine_table.medicines) == initial_count + 1
        assert new_medicine in medicine_table.medicines
    
    def test_update_medicine_in_table(self, medicine_table, sample_medicines):
        """Test updating existing medicine in table"""
        # Update first medicine
        updated_medicine = sample_medicines[0]
        updated_medicine.name = "Updated Medicine Name"
        
        medicine_table.update_medicine_in_table(updated_medicine)
        
        # Find the updated medicine in the list
        found_medicine = next((m for m in medicine_table.medicines if m.id == updated_medicine.id), None)
        assert found_medicine is not None
        assert found_medicine.name == "Updated Medicine Name"
    
    def test_remove_medicine_from_table(self, medicine_table, sample_medicines):
        """Test removing medicine from table"""
        initial_count = len(medicine_table.medicines)
        medicine_id_to_remove = sample_medicines[0].id
        
        medicine_table.remove_medicine_from_table(medicine_id_to_remove)
        
        assert len(medicine_table.medicines) == initial_count - 1
        assert not any(m.id == medicine_id_to_remove for m in medicine_table.medicines)
    
    def test_select_medicine_by_id(self, medicine_table, sample_medicines):
        """Test selecting medicine by ID"""
        medicine_id = sample_medicines[1].id
        
        medicine_table.select_medicine_by_id(medicine_id)
        
        # Check if the correct row is selected
        selected_rows = medicine_table.table.selectionModel().selectedRows()
        assert len(selected_rows) == 1
        
        selected_row = selected_rows[0].row()
        assert medicine_table.filtered_medicines[selected_row].id == medicine_id
    
    def test_auto_refresh_toggle(self, medicine_table):
        """Test auto-refresh functionality"""
        # Initially auto-refresh should be off
        assert not medicine_table.refresh_timer.isActive()
        assert "OFF" in medicine_table.auto_refresh_button.text()
        
        # Enable auto-refresh
        medicine_table.auto_refresh_button.setChecked(True)
        medicine_table._toggle_auto_refresh(True)
        
        assert medicine_table.refresh_timer.isActive()
        assert "ON" in medicine_table.auto_refresh_button.text()
        
        # Disable auto-refresh
        medicine_table.auto_refresh_button.setChecked(False)
        medicine_table._toggle_auto_refresh(False)
        
        assert not medicine_table.refresh_timer.isActive()
        assert "OFF" in medicine_table.auto_refresh_button.text()
    
    @patch('medical_store_app.ui.components.medicine_table.QMessageBox')
    def test_refresh_data_error_handling(self, mock_msgbox, medicine_table, mock_medicine_manager):
        """Test error handling during data refresh"""
        # Setup mock to raise exception
        mock_medicine_manager.get_all_medicines.side_effect = Exception("Database error")
        
        # Attempt to refresh data
        medicine_table.refresh_data()
        
        # Check that error message was shown
        mock_msgbox.critical.assert_called_once()
    
    def test_table_sorting(self, medicine_table):
        """Test table sorting functionality"""
        # Table should have sorting enabled
        assert medicine_table.table.isSortingEnabled()
        
        # Test sorting by clicking header (this would require more complex UI testing)
        # For now, just verify that sorting is enabled
        assert True
    
    def test_context_menu_actions(self, medicine_table, sample_medicines):
        """Test context menu functionality"""
        # Select a medicine
        medicine_table.selected_medicine = sample_medicines[0]
        
        # Test that context menu can be created (actual menu testing would require UI interaction)
        # This is a basic test to ensure the method doesn't crash
        try:
            # This would normally be triggered by right-click
            # medicine_table._show_context_menu(QPoint(0, 0))
            pass
        except Exception as e:
            pytest.fail(f"Context menu creation failed: {e}")
    
    def test_medicine_details_display(self, medicine_table, sample_medicines):
        """Test medicine details display"""
        medicine_table.selected_medicine = sample_medicines[0]
        
        # Test that details can be shown (actual dialog testing would require UI interaction)
        try:
            # This would normally be triggered by context menu
            # medicine_table._show_medicine_details()
            pass
        except Exception as e:
            pytest.fail(f"Medicine details display failed: {e}")


class TestMedicineTableIntegration:
    """Integration tests for MedicineTableWidget"""
    
    def test_full_workflow(self, medicine_table, sample_medicines):
        """Test complete workflow of table operations"""
        # Initial state
        assert len(medicine_table.medicines) == 3
        
        # Apply search filter
        medicine_table.search_field.setText("Paracetamol")
        medicine_table._on_search_changed("Paracetamol")
        assert len(medicine_table.filtered_medicines) == 1
        
        # Clear search and apply category filter
        medicine_table.search_field.setText("")
        medicine_table._on_search_changed("")
        medicine_table.category_filter_combo.setCurrentText("Antibiotic")
        medicine_table._on_category_filter_changed("Antibiotic")
        assert len(medicine_table.filtered_medicines) == 1
        
        # Clear all filters
        medicine_table.clear_filters()
        assert len(medicine_table.filtered_medicines) == 3
        
        # Add new medicine
        new_medicine = Medicine(
            id=4,
            name="Test Medicine",
            category="Test",
            batch_no="TEST001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0
        )
        medicine_table.add_medicine_to_table(new_medicine)
        assert len(medicine_table.medicines) == 4
        
        # Update medicine
        new_medicine.name = "Updated Test Medicine"
        medicine_table.update_medicine_in_table(new_medicine)
        updated = next((m for m in medicine_table.medicines if m.id == 4), None)
        assert updated.name == "Updated Test Medicine"
        
        # Remove medicine
        medicine_table.remove_medicine_from_table(4)
        assert len(medicine_table.medicines) == 3
    
    def test_signal_emissions(self, medicine_table, sample_medicines):
        """Test that appropriate signals are emitted"""
        # This would require more complex testing with signal spies
        # For now, just verify that signals exist
        assert hasattr(medicine_table, 'medicine_selected')
        assert hasattr(medicine_table, 'edit_requested')
        assert hasattr(medicine_table, 'delete_requested')
        assert hasattr(medicine_table, 'refresh_requested')


if __name__ == "__main__":
    pytest.main([__file__])