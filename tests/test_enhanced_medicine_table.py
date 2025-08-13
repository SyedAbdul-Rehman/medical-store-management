"""
Tests for Enhanced Medicine Table with Advanced Filtering
"""

import pytest
import sys
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDate
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.medicine_table import MedicineTableWidget
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
            id=1, name="Paracetamol", category="Pain Relief", batch_no="PAR001",
            expiry_date="2025-12-31", quantity=100, purchase_price=5.0, selling_price=8.0,
            barcode="123456789", created_at="2024-01-01"
        ),
        Medicine(
            id=2, name="Amoxicillin", category="Antibiotic", batch_no="AMX001",
            expiry_date="2024-06-30", quantity=50, purchase_price=12.0, selling_price=18.0,
            barcode="987654321", created_at="2024-01-15"
        ),
        Medicine(
            id=3, name="Ibuprofen", category="Pain Relief", batch_no="IBU001",
            expiry_date="2025-03-15", quantity=5, purchase_price=8.0, selling_price=12.0,
            barcode="456789123", created_at="2024-02-01"
        ),
        Medicine(
            id=4, name="Aspirin", category="Pain Relief", batch_no="ASP001",
            expiry_date="2024-01-15", quantity=0, purchase_price=3.0, selling_price=5.0,
            barcode="789123456", created_at="2024-01-20"
        ),
        Medicine(
            id=5, name="Cephalexin", category="Antibiotic", batch_no="CEP001",
            expiry_date="2025-08-20", quantity=75, purchase_price=15.0, selling_price=22.0,
            barcode="321654987", created_at="2024-02-10"
        ),
        Medicine(
            id=6, name="Vitamin C", category="Supplement", batch_no="VIT001",
            expiry_date="2026-01-01", quantity=200, purchase_price=2.0, selling_price=4.0,
            barcode="654987321", created_at="2024-01-05"
        )
    ]
    return medicines


@pytest.fixture
def mock_medicine_manager(sample_medicines):
    """Create mock medicine manager"""
    manager = Mock()
    manager.get_all_medicines.return_value = sample_medicines
    return manager


@pytest.fixture
def medicine_table(qapp, mock_medicine_manager):
    """Create medicine table widget for testing"""
    table = MedicineTableWidget(mock_medicine_manager)
    return table


class TestEnhancedMedicineTableFiltering:
    """Test cases for enhanced medicine table filtering capabilities"""
    
    def test_basic_search_all_fields(self, medicine_table):
        """Test basic search across all fields"""
        # Search by name
        medicine_table.search_field.setText("Paracetamol")
        medicine_table._on_search_changed("Paracetamol")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].name == "Paracetamol"
        
        # Search by category
        medicine_table.search_field.setText("Antibiotic")
        medicine_table._on_search_changed("Antibiotic")
        
        assert len(medicine_table.filtered_medicines) == 2
        categories = [med.category for med in medicine_table.filtered_medicines]
        assert all(cat == "Antibiotic" for cat in categories)
        
        # Search by batch number
        medicine_table.search_field.setText("PAR001")
        medicine_table._on_search_changed("PAR001")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].batch_no == "PAR001"
    
    def test_search_type_specific(self, medicine_table):
        """Test search with specific search types"""
        # Name only search
        medicine_table.search_type_combo.setCurrentText("Name Only")
        medicine_table.search_field.setText("Pain")  # Should not match category
        medicine_table._on_search_changed("Pain")
        
        assert len(medicine_table.filtered_medicines) == 0
        
        # Category only search
        medicine_table.search_type_combo.setCurrentText("Category Only")
        medicine_table.search_field.setText("Pain")
        medicine_table._on_search_changed("Pain")
        
        assert len(medicine_table.filtered_medicines) == 3  # Pain Relief medicines
        
        # Batch number search
        medicine_table.search_type_combo.setCurrentText("Batch Number")
        medicine_table.search_field.setText("AMX")
        medicine_table._on_search_changed("AMX")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert "AMX" in medicine_table.filtered_medicines[0].batch_no
        
        # Barcode search
        medicine_table.search_type_combo.setCurrentText("Barcode Only")
        medicine_table.search_field.setText("123456789")
        medicine_table._on_search_changed("123456789")
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].barcode == "123456789"
    
    def test_category_filtering(self, medicine_table):
        """Test category-based filtering"""
        # Filter by Pain Relief
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        
        assert len(medicine_table.filtered_medicines) == 3
        categories = [med.category for med in medicine_table.filtered_medicines]
        assert all(cat == "Pain Relief" for cat in categories)
        
        # Filter by Antibiotic
        medicine_table.category_filter_combo.setCurrentText("Antibiotic")
        medicine_table._on_category_filter_changed("Antibiotic")
        
        assert len(medicine_table.filtered_medicines) == 2
        categories = [med.category for med in medicine_table.filtered_medicines]
        assert all(cat == "Antibiotic" for cat in categories)
        
        # Clear category filter
        medicine_table.category_filter_combo.setCurrentText("All Categories")
        medicine_table._on_category_filter_changed("All Categories")
        
        assert len(medicine_table.filtered_medicines) == 6
    
    def test_stock_status_filtering(self, medicine_table):
        """Test stock status filtering"""
        # Filter by Low Stock (quantity <= 10)
        medicine_table.stock_filter_combo.setCurrentText("Low Stock")
        medicine_table._on_stock_filter_changed("Low Stock")
        
        low_stock_medicines = [med for med in medicine_table.filtered_medicines if med.quantity <= 10]
        assert len(medicine_table.filtered_medicines) == len(low_stock_medicines)
        
        # Filter by Out of Stock
        medicine_table.stock_filter_combo.setCurrentText("Out of Stock")
        medicine_table._on_stock_filter_changed("Out of Stock")
        
        out_of_stock = [med for med in medicine_table.filtered_medicines if med.quantity == 0]
        assert len(medicine_table.filtered_medicines) == len(out_of_stock)
        
        # Filter by In Stock
        medicine_table.stock_filter_combo.setCurrentText("In Stock")
        medicine_table._on_stock_filter_changed("In Stock")
        
        in_stock = [med for med in medicine_table.filtered_medicines if med.quantity > 0]
        assert len(medicine_table.filtered_medicines) == len(in_stock)
    
    def test_price_range_filtering(self, medicine_table):
        """Test price range filtering"""
        # Set price range $5-$15
        medicine_table.min_price_spinbox.setValue(5.0)
        medicine_table.max_price_spinbox.setValue(15.0)
        medicine_table._on_price_filter_changed()
        
        for medicine in medicine_table.filtered_medicines:
            assert 5.0 <= medicine.selling_price <= 15.0
        
        # Set narrow price range
        medicine_table.min_price_spinbox.setValue(10.0)
        medicine_table.max_price_spinbox.setValue(12.0)
        medicine_table._on_price_filter_changed()
        
        for medicine in medicine_table.filtered_medicines:
            assert 10.0 <= medicine.selling_price <= 12.0
    
    def test_quantity_range_filtering(self, medicine_table):
        """Test quantity range filtering"""
        # Set quantity range 50-150
        medicine_table.min_qty_spinbox.setValue(50)
        medicine_table.max_qty_spinbox.setValue(150)
        medicine_table._on_quantity_filter_changed()
        
        for medicine in medicine_table.filtered_medicines:
            assert 50 <= medicine.quantity <= 150
        
        # Set high quantity threshold
        medicine_table.min_qty_spinbox.setValue(100)
        medicine_table.max_qty_spinbox.setValue(999999)
        medicine_table._on_quantity_filter_changed()
        
        for medicine in medicine_table.filtered_medicines:
            assert medicine.quantity >= 100
    
    def test_expiry_date_filtering(self, medicine_table):
        """Test expiry date filtering"""
        # Filter by Next 30 Days
        medicine_table.expiry_filter_combo.setCurrentText("Next 30 Days")
        medicine_table._on_expiry_filter_changed("Next 30 Days")
        
        # Should filter medicines expiring within 30 days
        current_date = date.today()
        thirty_days_later = current_date + timedelta(days=30)
        
        for medicine in medicine_table.filtered_medicines:
            expiry_date = datetime.strptime(medicine.expiry_date, "%Y-%m-%d").date()
            assert current_date <= expiry_date <= thirty_days_later
        
        # Filter by Past Due
        medicine_table.expiry_filter_combo.setCurrentText("Past Due")
        medicine_table._on_expiry_filter_changed("Past Due")
        
        for medicine in medicine_table.filtered_medicines:
            expiry_date = datetime.strptime(medicine.expiry_date, "%Y-%m-%d").date()
            assert expiry_date < current_date
    
    def test_combined_filtering(self, medicine_table):
        """Test multiple filters applied together"""
        # Combine category and stock filters
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        
        medicine_table.stock_filter_combo.setCurrentText("In Stock")
        medicine_table._on_stock_filter_changed("In Stock")
        
        for medicine in medicine_table.filtered_medicines:
            assert medicine.category == "Pain Relief"
            assert medicine.quantity > 0
        
        # Add price filter
        medicine_table.min_price_spinbox.setValue(6.0)
        medicine_table.max_price_spinbox.setValue(15.0)
        medicine_table._on_price_filter_changed()
        
        for medicine in medicine_table.filtered_medicines:
            assert medicine.category == "Pain Relief"
            assert medicine.quantity > 0
            assert 6.0 <= medicine.selling_price <= 15.0
    
    def test_sorting_functionality(self, medicine_table):
        """Test sorting by various fields"""
        # Sort by Name A-Z
        medicine_table.sort_combo.setCurrentText("Name (A-Z)")
        medicine_table._on_sort_changed("Name (A-Z)")
        
        names = [med.name for med in medicine_table.filtered_medicines]
        assert names == sorted(names)
        
        # Sort by Name Z-A
        medicine_table.sort_combo.setCurrentText("Name (Z-A)")
        medicine_table._on_sort_changed("Name (Z-A)")
        
        names = [med.name for med in medicine_table.filtered_medicines]
        assert names == sorted(names, reverse=True)
        
        # Sort by Quantity Low-High
        medicine_table.sort_combo.setCurrentText("Quantity (Low-High)")
        medicine_table._on_sort_changed("Quantity (Low-High)")
        
        quantities = [med.quantity for med in medicine_table.filtered_medicines]
        assert quantities == sorted(quantities)
        
        # Sort by Price High-Low
        medicine_table.sort_combo.setCurrentText("Price (High-Low)")
        medicine_table._on_sort_changed("Price (High-Low)")
        
        prices = [med.selling_price for med in medicine_table.filtered_medicines]
        assert prices == sorted(prices, reverse=True)
    
    def test_clear_filters(self, medicine_table):
        """Test clearing all filters"""
        # Apply multiple filters
        medicine_table.search_field.setText("Pain")
        medicine_table._on_search_changed("Pain")
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        medicine_table.min_price_spinbox.setValue(5.0)
        medicine_table._on_price_filter_changed()
        
        # Verify filters are applied
        assert len(medicine_table.filtered_medicines) < len(medicine_table.medicines)
        
        # Clear filters
        medicine_table.clear_filters()
        
        # Verify all medicines are shown
        assert len(medicine_table.filtered_medicines) == len(medicine_table.medicines)
        assert medicine_table.search_field.text() == ""
        assert medicine_table.category_filter_combo.currentText() == "All Categories"
        assert medicine_table.min_price_spinbox.value() == 0.0
    
    def test_advanced_search_panel(self, medicine_table):
        """Test advanced search panel functionality"""
        # Initially panel should be hidden
        assert medicine_table.advanced_search_button.text() == "Advanced"
        
        # Toggle advanced search panel
        medicine_table.advanced_search_button.setChecked(True)
        medicine_table._toggle_advanced_search(True)
        
        # Check button text changed
        assert medicine_table.advanced_search_button.text() == "Hide Advanced"
        
        # Test batch number search in advanced panel
        # Force the panel to be visible for the filter to work
        medicine_table.advanced_panel.show()
        medicine_table.batch_search_field.setText("PAR")
        medicine_table._apply_filters()
        
        # Should only show medicines with "PAR" in batch number
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].batch_no == "PAR001"
        
        # Test barcode search in advanced panel
        medicine_table.batch_search_field.setText("")
        medicine_table.barcode_search_field.setText("123456789")
        medicine_table._apply_filters()
        
        assert len(medicine_table.filtered_medicines) == 1
        assert medicine_table.filtered_medicines[0].barcode == "123456789"
        
        # Hide advanced panel
        medicine_table.advanced_search_button.setChecked(False)
        medicine_table._toggle_advanced_search(False)
        
        assert medicine_table.advanced_search_button.text() == "Advanced"
    
    def test_profit_margin_filtering(self, medicine_table):
        """Test profit margin filtering in advanced search"""
        # Show advanced panel
        medicine_table.advanced_search_button.setChecked(True)
        medicine_table._toggle_advanced_search(True)
        medicine_table.advanced_panel.show()  # Force visibility for testing
        
        # Set profit margin range 30-120% (to accommodate our test data)
        medicine_table.min_margin_spinbox.setValue(30.0)
        medicine_table.max_margin_spinbox.setValue(120.0)
        medicine_table._apply_filters()
        
        for medicine in medicine_table.filtered_medicines:
            margin = medicine.get_profit_margin()
            assert 30.0 <= margin <= 120.0
    
    def test_date_range_filtering(self, medicine_table):
        """Test date range filtering in advanced search"""
        # Show advanced panel
        medicine_table.advanced_search_button.setChecked(True)
        medicine_table._toggle_advanced_search(True)
        medicine_table.advanced_panel.show()  # Force visibility for testing
        
        # Set date range to include our test data (2024-01-01 to 2024-02-15)
        start_date = QDate(2024, 1, 1)
        end_date = QDate(2024, 2, 15)
        
        medicine_table.added_after_date.setDate(start_date)
        medicine_table.added_before_date.setDate(end_date)
        medicine_table._apply_filters()
        
        for medicine in medicine_table.filtered_medicines:
            created_date = datetime.strptime(medicine.created_at, "%Y-%m-%d").date()
            assert start_date.toPython() <= created_date <= end_date.toPython()
    
    def test_saved_filters(self, medicine_table):
        """Test saving and loading filter configurations"""
        # Apply some filters
        medicine_table.search_field.setText("Paracetamol")
        medicine_table._on_search_changed("Paracetamol")
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        
        # Save filter
        filter_name = "Test Filter"
        medicine_table.saved_filters[filter_name] = {
            'search_query': 'Paracetamol',
            'search_type': 'All Fields',
            'category_filter': 'Pain Relief',
            'stock_filter': '',
            'min_price': 0.0,
            'max_price': 999999.99,
            'min_quantity': 0,
            'max_quantity': 999999,
            'expiry_filter': 'All',
            'sort_option': 'Name (A-Z)'
        }
        medicine_table._update_saved_filters_combo()
        
        # Clear current filters
        medicine_table.clear_filters()
        assert medicine_table.search_field.text() == ""
        
        # Load saved filter
        medicine_table._load_saved_filter(filter_name)
        
        assert medicine_table.search_field.text() == "Paracetamol"
        assert medicine_table.category_filter_combo.currentText() == "Pain Relief"
    
    def test_statistics_update(self, medicine_table):
        """Test statistics update with filtering"""
        # Check initial statistics
        medicine_table._update_statistics()
        
        # Apply filter and check statistics update
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        
        # Statistics should reflect filtered data
        total_text = medicine_table.total_medicines_label.text()
        assert "3" in total_text  # 3 Pain Relief medicines
    
    def test_auto_refresh_functionality(self, medicine_table):
        """Test auto-refresh functionality"""
        # Enable auto-refresh
        medicine_table.auto_refresh_button.setChecked(True)
        medicine_table._toggle_auto_refresh(True)
        
        assert medicine_table.refresh_timer.isActive()
        assert medicine_table.auto_refresh_button.text() == "Auto-Refresh: ON"
        
        # Disable auto-refresh
        medicine_table.auto_refresh_button.setChecked(False)
        medicine_table._toggle_auto_refresh(False)
        
        assert not medicine_table.refresh_timer.isActive()
        assert medicine_table.auto_refresh_button.text() == "Auto-Refresh: OFF"


class TestMedicineTableIntegration:
    """Integration tests for enhanced medicine table functionality"""
    
    def test_full_workflow_filtering_and_sorting(self, medicine_table):
        """Test complete workflow of filtering and sorting"""
        # Start with all medicines
        assert len(medicine_table.filtered_medicines) == 6
        
        # Apply category filter
        medicine_table.category_filter_combo.setCurrentText("Pain Relief")
        medicine_table._on_category_filter_changed("Pain Relief")
        assert len(medicine_table.filtered_medicines) == 3
        
        # Add stock filter
        medicine_table.stock_filter_combo.setCurrentText("In Stock")
        medicine_table._on_stock_filter_changed("In Stock")
        in_stock_count = len([m for m in medicine_table.filtered_medicines if m.quantity > 0])
        assert len(medicine_table.filtered_medicines) == in_stock_count
        
        # Add search
        medicine_table.search_field.setText("Ibuprofen")
        medicine_table._on_search_changed("Ibuprofen")
        assert len(medicine_table.filtered_medicines) <= 1
        
        # Sort results
        medicine_table.sort_combo.setCurrentText("Name (A-Z)")
        medicine_table._on_sort_changed("Name (A-Z)")
        
        # Verify final results are properly filtered and sorted
        for medicine in medicine_table.filtered_medicines:
            assert medicine.category == "Pain Relief"
            assert medicine.quantity > 0
            assert "Ibuprofen" in medicine.name
    
    def test_performance_with_large_dataset(self, medicine_table):
        """Test filtering performance with larger dataset"""
        # Create larger dataset
        large_dataset = []
        for i in range(1000):
            medicine = Medicine(
                id=i, name=f"Medicine_{i}", category=f"Category_{i%10}",
                batch_no=f"BATCH_{i}", expiry_date="2025-12-31",
                quantity=i%100, purchase_price=float(i%50), selling_price=float((i%50)*1.5),
                barcode=f"BARCODE_{i}", created_at="2024-01-01"
            )
            large_dataset.append(medicine)
        
        medicine_table.medicines = large_dataset
        
        # Test filtering performance
        import time
        start_time = time.time()
        
        medicine_table.search_field.setText("Medicine_1")
        medicine_table._on_search_changed("Medicine_1")
        
        end_time = time.time()
        
        # Should complete filtering within reasonable time (< 1 second)
        assert (end_time - start_time) < 1.0
        
        # Verify results
        assert len(medicine_table.filtered_medicines) > 0
        for medicine in medicine_table.filtered_medicines:
            assert "Medicine_1" in medicine.name