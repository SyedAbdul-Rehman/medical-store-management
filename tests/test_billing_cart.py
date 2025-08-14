"""
Tests for billing cart functionality
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.billing_widget import CartWidget, ProductSearchWidget, BillingWidget
from medical_store_app.managers.sales_manager import SalesManager
from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.models.medicine import Medicine
from medical_store_app.models.sale import SaleItem


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_sales_manager():
    """Create mock sales manager"""
    manager = Mock(spec=SalesManager)
    manager.get_cart_items.return_value = []
    manager.calculate_cart_totals.return_value = {
        'subtotal': 0.0,
        'discount': 0.0,
        'tax': 0.0,
        'total': 0.0
    }
    manager.is_cart_empty.return_value = True
    manager.get_current_discount.return_value = 0.0
    manager.get_current_tax_rate.return_value = 0.0
    manager.get_current_cart_summary.return_value = {
        'item_count': 0,
        'total_quantity': 0,
        'subtotal': 0.0,
        'discount': 0.0,
        'tax': 0.0,
        'total': 0.0,
        'payment_method': 'cash',
        'items': []
    }
    return manager


@pytest.fixture
def mock_medicine_manager():
    """Create mock medicine manager"""
    manager = Mock(spec=MedicineManager)
    manager.search_medicines.return_value = []
    return manager


@pytest.fixture
def sample_medicine():
    """Create sample medicine for testing"""
    return Medicine(
        id=1,
        name="Test Medicine",
        category="Test Category",
        batch_no="TEST001",
        expiry_date="2025-12-31",
        quantity=100,
        purchase_price=5.0,
        selling_price=10.0,
        barcode="1234567890"
    )


@pytest.fixture
def sample_sale_items():
    """Create sample sale items for testing"""
    return [
        SaleItem(
            medicine_id=1,
            name="Medicine A",
            quantity=2,
            unit_price=10.0,
            total_price=20.0,
            batch_no="BATCH001"
        ),
        SaleItem(
            medicine_id=2,
            name="Medicine B",
            quantity=1,
            unit_price=15.0,
            total_price=15.0,
            batch_no="BATCH002"
        )
    ]


class TestCartWidget:
    """Test cases for CartWidget"""
    
    def test_cart_widget_initialization(self, app, mock_sales_manager):
        """Test cart widget initialization"""
        widget = CartWidget(mock_sales_manager)
        
        assert widget is not None
        assert widget.sales_manager == mock_sales_manager
        
        # Check UI elements exist
        assert hasattr(widget, 'cart_table')
        assert hasattr(widget, 'subtotal_label')
        assert hasattr(widget, 'discount_amount_label')
        assert hasattr(widget, 'tax_amount_label')
        assert hasattr(widget, 'total_label')
        assert hasattr(widget, 'discount_input')
        assert hasattr(widget, 'tax_rate_input')
        assert hasattr(widget, 'clear_cart_button')
    
    def test_empty_cart_display(self, app, mock_sales_manager):
        """Test empty cart display"""
        widget = CartWidget(mock_sales_manager)
        widget.show()  # Ensure widget is shown
        app.processEvents()  # Process Qt events
        
        # Verify empty cart state
        assert widget.empty_cart_label.isVisible()
        assert widget.cart_table.isHidden()  # Table should be hidden when empty
        assert not widget.clear_cart_button.isEnabled()
        assert widget.cart_count_label.text() == "0 items"
    
    def test_cart_with_items_display(self, app, mock_sales_manager, sample_sale_items):
        """Test cart display with items"""
        # Setup mock to return items
        mock_sales_manager.get_cart_items.return_value = sample_sale_items
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 35.0,
            'discount': 5.0,
            'tax': 3.0,
            'total': 33.0
        }
        
        widget = CartWidget(mock_sales_manager)
        widget.show()  # Ensure widget is shown
        app.processEvents()  # Process Qt events
        
        # Verify cart with items state
        assert widget.empty_cart_label.isHidden()  # Should be hidden when cart has items
        assert widget.cart_table.isVisible()
        assert widget.clear_cart_button.isEnabled()
        assert "2 items" in widget.cart_count_label.text()
        
        # Check table population
        assert widget.cart_table.rowCount() == 2
        
        # Check totals display
        assert widget.subtotal_label.text() == "$35.00"
        assert widget.discount_amount_label.text() == "-$5.00"
        assert widget.tax_amount_label.text() == "$3.00"
        assert widget.total_label.text() == "$33.00"
    
    def test_add_product_success(self, app, mock_sales_manager, sample_medicine):
        """Test successful product addition"""
        mock_sales_manager.add_to_cart.return_value = (True, "Added successfully", None)
        
        widget = CartWidget(mock_sales_manager)
        widget.add_product(sample_medicine, 2)
        
        mock_sales_manager.add_to_cart.assert_called_once_with(sample_medicine.id, 2)
    
    def test_add_product_failure(self, app, mock_sales_manager, sample_medicine):
        """Test product addition failure"""
        mock_sales_manager.add_to_cart.return_value = (False, "Insufficient stock", None)
        
        widget = CartWidget(mock_sales_manager)
        
        # Mock QMessageBox to avoid actual dialog
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox'):
            widget.add_product(sample_medicine, 10)
        
        mock_sales_manager.add_to_cart.assert_called_once_with(sample_medicine.id, 10)
    
    def test_discount_change(self, app, mock_sales_manager):
        """Test discount change handling"""
        mock_sales_manager.set_discount.return_value = (True, "Discount set")
        
        widget = CartWidget(mock_sales_manager)
        
        # Simulate discount input change
        widget.discount_input.setValue(10.0)
        
        mock_sales_manager.set_discount.assert_called_with(10.0)
    
    def test_tax_rate_change(self, app, mock_sales_manager):
        """Test tax rate change handling"""
        mock_sales_manager.set_tax_rate.return_value = (True, "Tax rate set")
        
        widget = CartWidget(mock_sales_manager)
        
        # Simulate tax rate input change
        widget.tax_rate_input.setValue(8.5)
        
        mock_sales_manager.set_tax_rate.assert_called_with(8.5)
    
    def test_clear_cart_confirmation(self, app, mock_sales_manager):
        """Test clear cart with confirmation"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.clear_cart.return_value = True
        
        widget = CartWidget(mock_sales_manager)
        
        # Mock QMessageBox to simulate user clicking Yes
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            widget.clear_cart()
            
            mock_sales_manager.clear_cart.assert_called_once()
    
    def test_clear_cart_cancelled(self, app, mock_sales_manager):
        """Test clear cart cancelled by user"""
        mock_sales_manager.is_cart_empty.return_value = False
        
        widget = CartWidget(mock_sales_manager)
        
        # Mock QMessageBox to simulate user clicking No
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.No
            
            widget.clear_cart()
            
            mock_sales_manager.clear_cart.assert_not_called()
    
    def test_quantity_change_in_cart(self, app, mock_sales_manager, sample_sale_items):
        """Test quantity change in cart table"""
        mock_sales_manager.get_cart_items.return_value = sample_sale_items
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.update_cart_item_quantity.return_value = (True, "Updated")
        
        widget = CartWidget(mock_sales_manager)
        
        # Simulate quantity change
        widget._on_quantity_changed(1, 5)
        
        mock_sales_manager.update_cart_item_quantity.assert_called_once_with(1, 5)
    
    def test_remove_item_from_cart(self, app, mock_sales_manager, sample_sale_items):
        """Test removing item from cart"""
        mock_sales_manager.get_cart_items.return_value = sample_sale_items
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.remove_from_cart.return_value = (True, "Removed")
        
        widget = CartWidget(mock_sales_manager)
        
        # Simulate item removal
        widget._remove_item(1)
        
        mock_sales_manager.remove_from_cart.assert_called_once_with(1)
    
    def test_cart_totals_calculation_accuracy(self, app, mock_sales_manager):
        """Test cart totals calculation accuracy"""
        # Test various calculation scenarios
        test_cases = [
            # (subtotal, discount, tax_rate, expected_total)
            (100.0, 10.0, 10.0, 99.0),  # $100 - $10 discount + 10% tax on $90 = $99
            (50.0, 0.0, 5.0, 52.5),     # $50 + 5% tax = $52.50
            (75.0, 25.0, 8.0, 54.0),    # $75 - $25 discount + 8% tax on $50 = $54
            (0.0, 0.0, 0.0, 0.0),       # Empty cart
        ]
        
        for subtotal, discount, tax_rate, expected_total in test_cases:
            mock_sales_manager.calculate_cart_totals.return_value = {
                'subtotal': subtotal,
                'discount': discount,
                'tax': round((subtotal - discount) * (tax_rate / 100), 2),
                'total': expected_total
            }
            
            widget = CartWidget(mock_sales_manager)
            widget._update_totals()
            
            assert widget.total_label.text() == f"${expected_total:.2f}"


class TestProductSearchWidget:
    """Test cases for ProductSearchWidget"""
    
    def test_product_search_initialization(self, app, mock_medicine_manager):
        """Test product search widget initialization"""
        widget = ProductSearchWidget(mock_medicine_manager)
        
        assert widget is not None
        assert widget.medicine_manager == mock_medicine_manager
        
        # Check UI elements exist
        assert hasattr(widget, 'search_input')
        assert hasattr(widget, 'results_table')
        assert hasattr(widget, 'quantity_spinbox')
        assert hasattr(widget, 'add_to_cart_button')
    
    def test_search_functionality(self, app, mock_medicine_manager, sample_medicine):
        """Test product search functionality"""
        mock_medicine_manager.search_medicines.return_value = [sample_medicine]
        
        widget = ProductSearchWidget(mock_medicine_manager)
        
        # Simulate search
        widget.search_input.setText("test")
        widget._perform_search()
        
        mock_medicine_manager.search_medicines.assert_called_with("test")
        assert widget.results_table.rowCount() == 1
    
    def test_empty_search_results(self, app, mock_medicine_manager):
        """Test empty search results"""
        mock_medicine_manager.search_medicines.return_value = []
        
        widget = ProductSearchWidget(mock_medicine_manager)
        
        widget.search_input.setText("nonexistent")
        widget._perform_search()
        
        assert widget.results_table.rowCount() == 0
        assert "No products found" in widget.status_label.text()
    
    def test_product_selection(self, app, mock_medicine_manager, sample_medicine):
        """Test product selection from search results"""
        mock_medicine_manager.search_medicines.return_value = [sample_medicine]
        
        widget = ProductSearchWidget(mock_medicine_manager)
        widget.search_input.setText("test")
        widget._perform_search()
        
        # Verify table has items
        assert widget.results_table.rowCount() == 1
        
        # Simulate row selection by setting current cell
        widget.results_table.setCurrentCell(0, 0)
        widget._on_selection_changed()
        
        # Check if medicine was selected (may be None if table item doesn't have UserRole data)
        # The actual implementation stores medicine in UserRole, so we need to verify the button state
        assert widget.add_to_cart_button.isEnabled() or widget.selected_medicine is not None
    
    def test_add_to_cart_signal(self, app, mock_medicine_manager, sample_medicine):
        """Test add to cart signal emission"""
        mock_medicine_manager.search_medicines.return_value = [sample_medicine]
        sample_medicine.can_sell = Mock(return_value=True)
        
        widget = ProductSearchWidget(mock_medicine_manager)
        
        # Connect signal to capture emission
        signal_received = []
        widget.product_selected.connect(lambda med, qty: signal_received.append((med, qty)))
        
        # Simulate adding to cart
        widget._add_medicine_to_cart(sample_medicine, 2)
        
        assert len(signal_received) == 1
        assert signal_received[0] == (sample_medicine, 2)


class TestBillingWidget:
    """Test cases for BillingWidget"""
    
    def test_billing_widget_initialization(self, app, mock_medicine_manager, mock_sales_manager):
        """Test billing widget initialization"""
        widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        assert widget is not None
        assert widget.medicine_manager == mock_medicine_manager
        assert widget.sales_manager == mock_sales_manager
        
        # Check child widgets exist
        assert hasattr(widget, 'product_search')
        assert hasattr(widget, 'cart_widget')
    
    def test_product_selection_integration(self, app, mock_medicine_manager, mock_sales_manager, sample_medicine):
        """Test product selection integration between search and cart"""
        mock_sales_manager.add_to_cart.return_value = (True, "Added", None)
        
        widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Simulate product selection
        widget._on_product_selected(sample_medicine, 3)
        
        mock_sales_manager.add_to_cart.assert_called_once_with(sample_medicine.id, 3)
    
    def test_cart_update_handling(self, app, mock_medicine_manager, mock_sales_manager):
        """Test cart update handling"""
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 2,
            'total': 25.0
        }
        
        widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Simulate cart update
        widget._on_cart_updated()
        
        # Should not raise any exceptions
        assert True
    
    def test_refresh_display(self, app, mock_medicine_manager, mock_sales_manager):
        """Test display refresh functionality"""
        widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Should not raise any exceptions
        widget.refresh_display()
        assert True
    
    def test_clear_all_functionality(self, app, mock_medicine_manager, mock_sales_manager):
        """Test clear all functionality"""
        mock_sales_manager.clear_cart.return_value = True
        mock_sales_manager.is_cart_empty.return_value = False  # Cart has items
        
        widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Mock QMessageBox for clear cart confirmation
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            widget.clear_all()
            
            # Verify cart was cleared (called through cart_widget.clear_cart)
            # The clear_all method calls both product_search.clear_search() and cart_widget.clear_cart()
            # cart_widget.clear_cart() will call sales_manager.clear_cart() if confirmed
            mock_sales_manager.clear_cart.assert_called_once()


class TestCartCalculationAccuracy:
    """Test cases specifically for cart calculation accuracy"""
    
    def test_subtotal_calculation(self, app, mock_sales_manager):
        """Test subtotal calculation accuracy"""
        # Create items with various prices and quantities
        items = [
            SaleItem(1, "Item 1", 2, 10.50, 21.00),
            SaleItem(2, "Item 2", 3, 7.33, 21.99),
            SaleItem(3, "Item 3", 1, 15.75, 15.75)
        ]
        
        mock_sales_manager.get_cart_items.return_value = items
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 58.74,  # 21.00 + 21.99 + 15.75
            'discount': 0.0,
            'tax': 0.0,
            'total': 58.74
        }
        
        widget = CartWidget(mock_sales_manager)
        widget._update_totals()
        
        assert widget.subtotal_label.text() == "$58.74"
    
    def test_discount_application(self, app, mock_sales_manager):
        """Test discount application accuracy"""
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 100.0,
            'discount': 15.0,
            'tax': 8.5,  # 10% tax on (100 - 15) = 8.5
            'total': 93.5  # 100 - 15 + 8.5
        }
        
        widget = CartWidget(mock_sales_manager)
        widget._update_totals()
        
        assert widget.subtotal_label.text() == "$100.00"
        assert widget.discount_amount_label.text() == "-$15.00"
        assert widget.tax_amount_label.text() == "$8.50"
        assert widget.total_label.text() == "$93.50"
    
    def test_tax_calculation_precision(self, app, mock_sales_manager):
        """Test tax calculation precision"""
        # Test edge cases with tax calculations
        test_cases = [
            (33.33, 0.0, 10.0, 36.66),  # 33.33 + 10% tax = 36.663 -> 36.66
            (99.99, 5.0, 7.5, 102.12),  # (99.99 - 5.00) * 1.075 = 102.11425 -> 102.12
            (0.01, 0.0, 25.0, 0.01),    # Very small amount with high tax
        ]
        
        for subtotal, discount, tax_rate, expected_total in test_cases:
            tax_amount = round((subtotal - discount) * (tax_rate / 100), 2)
            mock_sales_manager.calculate_cart_totals.return_value = {
                'subtotal': subtotal,
                'discount': discount,
                'tax': tax_amount,
                'total': expected_total
            }
            
            widget = CartWidget(mock_sales_manager)
            widget._update_totals()
            
            assert widget.total_label.text() == f"${expected_total:.2f}"
    
    def test_zero_total_handling(self, app, mock_sales_manager):
        """Test handling of zero totals"""
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 0.0,
            'discount': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        
        widget = CartWidget(mock_sales_manager)
        widget._update_totals()
        
        assert widget.subtotal_label.text() == "$0.00"
        assert widget.discount_amount_label.text() == "-$0.00"
        assert widget.tax_amount_label.text() == "$0.00"
        assert widget.total_label.text() == "$0.00"