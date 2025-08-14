"""
Tests for Product Search Widget in Billing System
Tests product search and selection functionality
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.billing_widget import ProductSearchWidget, BillingWidget
from medical_store_app.models.medicine import Medicine
from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.managers.sales_manager import SalesManager


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


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
            barcode="PAR001234567"
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
            barcode="AMX001234567"
        ),
        Medicine(
            id=3,
            name="Aspirin",
            category="Pain Relief",
            batch_no="ASP001",
            expiry_date="2025-03-15",
            quantity=0,  # Out of stock
            purchase_price=3.0,
            selling_price=5.0,
            barcode="ASP001234567"
        ),
        Medicine(
            id=4,
            name="Ibuprofen",
            category="Pain Relief",
            batch_no="IBU001",
            expiry_date="2024-01-15",  # Expired
            quantity=25,
            purchase_price=8.0,
            selling_price=12.0,
            barcode="IBU001234567"
        )
    ]


@pytest.fixture
def mock_medicine_manager(sample_medicines):
    """Create mock medicine manager"""
    manager = Mock(spec=MedicineManager)
    
    # Mock search methods
    def mock_search(query):
        query_lower = query.lower()
        results = []
        for medicine in sample_medicines:
            if (query_lower in medicine.name.lower() or 
                query_lower in medicine.barcode.lower() or
                query_lower in medicine.category.lower()):
                results.append(medicine)
        return results
    
    manager.search_medicines.side_effect = mock_search
    
    return manager


@pytest.fixture
def mock_sales_manager():
    """Create mock sales manager"""
    return Mock(spec=SalesManager)


@pytest.fixture
def product_search_widget(app, mock_medicine_manager):
    """Create ProductSearchWidget instance for testing"""
    widget = ProductSearchWidget(mock_medicine_manager)
    widget.show()
    return widget


@pytest.fixture
def billing_widget(app, mock_medicine_manager, mock_sales_manager):
    """Create BillingWidget instance for testing"""
    widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
    widget.show()
    return widget


class TestProductSearchWidget:
    """Test cases for ProductSearchWidget"""
    
    def test_widget_initialization(self, product_search_widget):
        """Test widget initialization"""
        widget = product_search_widget
        
        # Check UI elements exist
        assert widget.search_input is not None
        assert widget.search_button is not None
        assert widget.clear_button is not None
        assert widget.results_table is not None
        assert widget.quantity_spinbox is not None
        assert widget.add_to_cart_button is not None
        assert widget.status_label is not None
        
        # Check initial state
        assert widget.search_input.text() == ""
        assert widget.results_table.rowCount() == 0
        assert widget.quantity_spinbox.value() == 1
        assert not widget.add_to_cart_button.isEnabled()
        assert widget.selected_medicine is None
    
    def test_search_input_placeholder(self, product_search_widget):
        """Test search input placeholder text"""
        widget = product_search_widget
        assert "Search by name or barcode" in widget.search_input.placeholderText()
    
    def test_table_headers(self, product_search_widget):
        """Test table column headers"""
        widget = product_search_widget
        table = widget.results_table
        
        expected_headers = ["Name", "Category", "Batch No", "Stock", "Price", "Expiry", "Action"]
        actual_headers = []
        
        for col in range(table.columnCount()):
            actual_headers.append(table.horizontalHeaderItem(col).text())
        
        assert actual_headers == expected_headers
    
    def test_search_functionality(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test search functionality"""
        widget = product_search_widget
        
        # Test search by name
        widget.search_input.setText("Paracetamol")
        widget._perform_search()
        
        # Verify search was called
        mock_medicine_manager.search_medicines.assert_called_with("Paracetamol")
        
        # Check results table is populated
        assert widget.results_table.rowCount() == 1
        assert widget.results_table.item(0, 0).text() == "Paracetamol"
        assert widget.results_table.item(0, 1).text() == "Pain Relief"
        assert widget.results_table.item(0, 3).text() == "100"
        assert widget.results_table.item(0, 4).text() == "$8.00"
    
    def test_search_filters_out_of_stock(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test that search filters out medicines with no stock"""
        widget = product_search_widget
        
        # Search for "Aspirin" which has 0 stock
        widget.search_input.setText("Aspirin")
        widget._perform_search()
        
        # Should not show out of stock items
        assert widget.results_table.rowCount() == 0
        assert "No products found or all out of stock" in widget.status_label.text()
    
    def test_search_by_category(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test search by category"""
        widget = product_search_widget
        
        # Search by category
        widget.search_input.setText("Pain Relief")
        widget._perform_search()
        
        # Should find Paracetamol and Ibuprofen (both in Pain Relief category)
        # But Aspirin should be filtered out due to 0 stock
        assert widget.results_table.rowCount() == 2
    
    def test_search_by_barcode(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test search by barcode"""
        widget = product_search_widget
        
        # Search by barcode
        widget.search_input.setText("PAR001234567")
        widget._perform_search()
        
        # Should find Paracetamol
        assert widget.results_table.rowCount() == 1
        assert widget.results_table.item(0, 0).text() == "Paracetamol"
    
    def test_clear_search(self, product_search_widget):
        """Test clear search functionality"""
        widget = product_search_widget
        
        # Add some search text and results
        widget.search_input.setText("test")
        widget.results_table.setRowCount(5)  # Simulate results
        
        # Clear search
        widget.clear_search()
        
        # Check everything is cleared
        assert widget.search_input.text() == ""
        assert widget.results_table.rowCount() == 0
        assert widget.selected_medicine is None
        assert not widget.add_to_cart_button.isEnabled()
    
    def test_selection_handling(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test table selection handling"""
        widget = product_search_widget
        
        # Populate results
        widget.search_input.setText("Paracetamol")
        widget._perform_search()
        
        # Select first row
        widget.results_table.selectRow(0)
        widget._on_selection_changed()
        
        # Check selection state
        assert widget.selected_medicine is not None
        assert widget.selected_medicine.name == "Paracetamol"
        assert widget.add_to_cart_button.isEnabled()
    
    def test_quantity_spinbox_limits(self, product_search_widget):
        """Test quantity spinbox limits"""
        widget = product_search_widget
        spinbox = widget.quantity_spinbox
        
        assert spinbox.minimum() == 1
        assert spinbox.maximum() == 9999
        assert spinbox.value() == 1
    
    def test_product_selection_signal(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test product selection signal emission"""
        widget = product_search_widget
        
        # Connect signal to mock
        signal_mock = Mock()
        widget.product_selected.connect(signal_mock)
        
        # Populate results and select
        widget.search_input.setText("Paracetamol")
        widget._perform_search()
        widget.results_table.selectRow(0)
        widget._on_selection_changed()
        
        # Set quantity and add to cart
        widget.quantity_spinbox.setValue(5)
        widget._add_selected_to_cart()
        
        # Check signal was emitted
        signal_mock.assert_called_once()
        args = signal_mock.call_args[0]
        assert args[0].name == "Paracetamol"
        assert args[1] == 5
    
    def test_add_button_in_table(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test add button functionality in table"""
        widget = product_search_widget
        
        # Connect signal to mock
        signal_mock = Mock()
        widget.product_selected.connect(signal_mock)
        
        # Populate results
        widget.search_input.setText("Paracetamol")
        widget._perform_search()
        
        # Get the add button from the table
        add_button = widget.results_table.cellWidget(0, 6)
        assert add_button is not None
        
        # Click the add button
        add_button.click()
        
        # Check signal was emitted with default quantity (1)
        signal_mock.assert_called_once()
        args = signal_mock.call_args[0]
        assert args[0].name == "Paracetamol"
        assert args[1] == 1
    
    def test_insufficient_stock_warning(self, product_search_widget, mock_medicine_manager, sample_medicines):
        """Test insufficient stock warning"""
        widget = product_search_widget
        
        # Mock QMessageBox to avoid actual dialog
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            # Find a medicine with limited stock
            medicine = sample_medicines[1]  # Amoxicillin with 50 stock
            
            # Try to add more than available stock
            widget._add_medicine_to_cart(medicine, 100)
            
            # Check warning was shown
            mock_msgbox.warning.assert_called_once()
            args = mock_msgbox.warning.call_args[0]
            assert "Insufficient Stock" in args[1]
            assert "Cannot add 100 units" in args[2]
    
    def test_search_timer_delay(self, product_search_widget):
        """Test search timer delay functionality"""
        widget = product_search_widget
        
        # Mock the timer
        with patch.object(widget.search_timer, 'start') as mock_start:
            with patch.object(widget.search_timer, 'stop') as mock_stop:
                # Type in search box
                widget.search_input.setText("test")
                widget._on_search_text_changed()
                
                # Check timer was stopped and started
                assert mock_stop.called  # Timer should be stopped
                mock_start.assert_called_with(500)  # Timer should be started with 500ms delay
    
    def test_empty_search_clears_results(self, product_search_widget):
        """Test that empty search clears results"""
        widget = product_search_widget
        
        # Add some results first
        widget.results_table.setRowCount(3)
        
        # Clear search input
        widget.search_input.setText("")
        widget._on_search_text_changed()
        
        # Check results are cleared
        assert widget.results_table.rowCount() == 0
    
    def test_focus_search(self, product_search_widget):
        """Test focus search functionality"""
        widget = product_search_widget
        
        # Set some text
        widget.search_input.setText("test")
        
        # Focus search
        widget.focus_search()
        
        # Check focus and selection
        assert widget.search_input.hasFocus()
        assert widget.search_input.selectedText() == "test"


class TestBillingWidget:
    """Test cases for BillingWidget"""
    
    def test_widget_initialization(self, billing_widget):
        """Test billing widget initialization"""
        widget = billing_widget
        
        # Check product search widget exists
        assert widget.product_search is not None
        assert isinstance(widget.product_search, ProductSearchWidget)
    
    def test_product_selection_handling(self, billing_widget, sample_medicines):
        """Test product selection handling"""
        widget = billing_widget
        
        # Mock QMessageBox to avoid actual dialog
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            # Simulate product selection
            medicine = sample_medicines[0]  # Paracetamol
            widget._on_product_selected(medicine, 3)
            
            # Check information dialog was shown
            mock_msgbox.information.assert_called_once()
            args = mock_msgbox.information.call_args[0]
            assert "Product Selected" in args[1]
            assert "Paracetamol" in args[2]
            assert "Quantity: 3" in args[2]
    
    def test_clear_all(self, billing_widget):
        """Test clear all functionality"""
        widget = billing_widget
        
        # Set some search text
        widget.product_search.search_input.setText("test")
        
        # Clear all
        widget.clear_all()
        
        # Check search is cleared
        assert widget.product_search.search_input.text() == ""
    
    def test_refresh_display(self, billing_widget):
        """Test refresh display functionality"""
        widget = billing_widget
        
        # Mock focus_search method
        with patch.object(widget.product_search, 'focus_search') as mock_focus:
            widget.refresh_display()
            mock_focus.assert_called_once()


class TestIntegration:
    """Integration tests for billing widget components"""
    
    def test_search_and_select_workflow(self, billing_widget, mock_medicine_manager, sample_medicines):
        """Test complete search and select workflow"""
        widget = billing_widget
        
        # Mock QMessageBox to avoid actual dialog
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            # Perform search
            widget.product_search.search_input.setText("Paracetamol")
            widget.product_search._perform_search()
            
            # Verify search results
            assert widget.product_search.results_table.rowCount() == 1
            
            # Select product
            widget.product_search.results_table.selectRow(0)
            widget.product_search._on_selection_changed()
            
            # Set quantity and add to cart
            widget.product_search.quantity_spinbox.setValue(2)
            widget.product_search._add_selected_to_cart()
            
            # Verify product selection dialog
            mock_msgbox.information.assert_called_once()
            args = mock_msgbox.information.call_args[0]
            assert "Paracetamol" in args[2]
            assert "Quantity: 2" in args[2]
    
    def test_barcode_search_workflow(self, billing_widget, mock_medicine_manager, sample_medicines):
        """Test barcode search workflow"""
        widget = billing_widget
        
        # Search by barcode
        widget.product_search.search_input.setText("AMX001234567")
        widget.product_search._perform_search()
        
        # Should find Amoxicillin
        assert widget.product_search.results_table.rowCount() == 1
        assert widget.product_search.results_table.item(0, 0).text() == "Amoxicillin"
        
        # Click add button directly
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            add_button = widget.product_search.results_table.cellWidget(0, 6)
            add_button.click()
            
            # Verify product was added
            mock_msgbox.information.assert_called_once()
            args = mock_msgbox.information.call_args[0]
            assert "Amoxicillin" in args[2]


if __name__ == "__main__":
    pytest.main([__file__])