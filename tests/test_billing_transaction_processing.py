"""
Integration tests for billing transaction processing
Tests the complete billing workflow from product search to transaction completion
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.billing_widget import CartWidget, ProductSearchWidget, BillingWidget
from medical_store_app.ui.dialogs.receipt_dialog import ReceiptDialog
from medical_store_app.managers.sales_manager import SalesManager
from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.models.medicine import Medicine
from medical_store_app.models.sale import Sale, SaleItem


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_sales_manager():
    """Create mock sales manager with transaction processing capabilities"""
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
    manager.get_current_payment_method.return_value = "cash"
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
    manager.set_payment_method.return_value = (True, "Payment method set")
    manager.complete_sale.return_value = (False, "Cart is empty", None)
    manager.clear_cart.return_value = True
    return manager


@pytest.fixture
def mock_medicine_manager():
    """Create mock medicine manager"""
    manager = Mock(spec=MedicineManager)
    manager.search_medicines.return_value = []
    return manager


@pytest.fixture
def sample_medicines():
    """Create sample medicines for testing"""
    medicines = []
    for i in range(1, 4):
        medicine = Medicine(
            id=i,
            name=f"Medicine {i}",
            category="Test Category",
            batch_no=f"BATCH{i:03d}",
            expiry_date="2025-12-31",
            quantity=50,
            purchase_price=5.0 * i,
            selling_price=10.0 * i,
            barcode=f"123456789{i}"
        )
        medicine.can_sell = Mock(return_value=True)
        medicine.is_low_stock = Mock(return_value=False)
        medicine.is_expired = Mock(return_value=False)
        medicine.is_expiring_soon = Mock(return_value=False)
        medicines.append(medicine)
    return medicines


@pytest.fixture
def sample_sale_items():
    """Create sample sale items for testing"""
    return [
        SaleItem(
            medicine_id=1,
            name="Medicine 1",
            quantity=2,
            unit_price=10.0,
            total_price=20.0,
            batch_no="BATCH001"
        ),
        SaleItem(
            medicine_id=2,
            name="Medicine 2",
            quantity=1,
            unit_price=20.0,
            total_price=20.0,
            batch_no="BATCH002"
        )
    ]


@pytest.fixture
def sample_completed_sale():
    """Create sample completed sale for testing"""
    return Sale(
        id=1,
        date="2024-01-15",
        items=[
            SaleItem(1, "Medicine 1", 2, 10.0, 20.0, "BATCH001"),
            SaleItem(2, "Medicine 2", 1, 20.0, 20.0, "BATCH002")
        ],
        subtotal=40.0,
        discount=5.0,
        tax=3.5,
        total=38.5,
        payment_method="cash",
        cashier_id=1,
        customer_name="John Doe"
    )


class TestTransactionProcessing:
    """Test cases for transaction processing functionality"""
    
    def test_payment_method_selection(self, app, mock_sales_manager):
        """Test payment method selection"""
        widget = CartWidget(mock_sales_manager)
        
        # Test all payment methods
        payment_methods = ["Cash", "Card", "UPI", "Cheque", "Bank Transfer"]
        
        for method in payment_methods:
            widget.payment_method_combo.setCurrentText(method)
            widget._on_payment_method_changed(method)
            
            # Verify the correct internal method was set
            expected_internal = method.lower().replace(" ", "_")
            mock_sales_manager.set_payment_method.assert_called_with(expected_internal)
    
    def test_payment_method_change_failure(self, app, mock_sales_manager):
        """Test payment method change failure handling"""
        mock_sales_manager.set_payment_method.return_value = (False, "Invalid payment method")
        
        widget = CartWidget(mock_sales_manager)
        
        # Try to set invalid payment method
        widget.payment_method_combo.setCurrentText("Card")
        widget._on_payment_method_changed("Card")
        
        # Should revert to Cash
        assert widget.payment_method_combo.currentText() == "Cash"
    
    def test_complete_sale_empty_cart(self, app, mock_sales_manager):
        """Test completing sale with empty cart"""
        mock_sales_manager.is_cart_empty.return_value = True
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            widget._complete_sale()
            
            # Should show warning about empty cart
            mock_msgbox.warning.assert_called_once()
            mock_sales_manager.complete_sale.assert_not_called()
    
    def test_complete_sale_with_confirmation(self, app, mock_sales_manager, sample_sale_items, sample_completed_sale):
        """Test completing sale with user confirmation"""
        # Setup cart with items
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 2,
            'subtotal': 40.0,
            'discount': 5.0,
            'tax': 3.5,
            'total': 38.5
        }
        mock_sales_manager.complete_sale.return_value = (True, "Sale completed", sample_completed_sale)
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            # Mock user clicking Yes to confirm
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            widget._complete_sale()
            
            # Verify confirmation dialog was shown
            mock_msgbox.question.assert_called_once()
            
            # Verify sale was completed
            mock_sales_manager.complete_sale.assert_called_once()
    
    def test_complete_sale_cancelled_by_user(self, app, mock_sales_manager, sample_sale_items):
        """Test completing sale cancelled by user"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 2,
            'subtotal': 40.0,
            'discount': 5.0,
            'tax': 3.5,
            'total': 38.5
        }
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            # Mock user clicking No to cancel
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.No
            
            widget._complete_sale()
            
            # Verify sale was not completed
            mock_sales_manager.complete_sale.assert_not_called()
    
    def test_complete_sale_with_customer_name(self, app, mock_sales_manager, sample_completed_sale):
        """Test completing sale with customer name"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 20.0,
            'discount': 0.0,
            'tax': 2.0,
            'total': 22.0
        }
        mock_sales_manager.complete_sale.return_value = (True, "Sale completed", sample_completed_sale)
        
        widget = CartWidget(mock_sales_manager)
        widget.customer_name_input.setText("John Doe")
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            widget._complete_sale()
            
            # Verify customer name was passed to complete_sale
            mock_sales_manager.complete_sale.assert_called_once_with(cashier_id=None, customer_name="John Doe")
    
    def test_complete_sale_failure(self, app, mock_sales_manager):
        """Test completing sale failure handling"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 20.0,
            'discount': 0.0,
            'tax': 2.0,
            'total': 22.0
        }
        mock_sales_manager.complete_sale.return_value = (False, "Insufficient stock", None)
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            widget._complete_sale()
            
            # Should show error message
            mock_msgbox.critical.assert_called_once()
    
    def test_cancel_sale_empty_cart(self, app, mock_sales_manager):
        """Test cancelling sale with empty cart"""
        mock_sales_manager.is_cart_empty.return_value = True
        
        widget = CartWidget(mock_sales_manager)
        widget._cancel_sale()
        
        # Should not show confirmation dialog for empty cart
        mock_sales_manager.clear_cart.assert_not_called()
    
    def test_cancel_sale_with_confirmation(self, app, mock_sales_manager):
        """Test cancelling sale with confirmation"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.clear_cart.return_value = True
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            widget._cancel_sale()
            
            # Should clear cart and reset inputs
            mock_sales_manager.clear_cart.assert_called_once()
            assert widget.customer_name_input.text() == ""
            assert widget.payment_method_combo.currentText() == "Cash"
    
    def test_cancel_sale_declined(self, app, mock_sales_manager):
        """Test cancelling sale declined by user"""
        mock_sales_manager.is_cart_empty.return_value = False
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.No
            
            widget._cancel_sale()
            
            # Should not clear cart
            mock_sales_manager.clear_cart.assert_not_called()
    
    def test_transaction_success_dialog(self, app, mock_sales_manager, sample_completed_sale):
        """Test transaction success dialog display"""
        widget = CartWidget(mock_sales_manager)
        widget.customer_name_input.setText("John Doe")
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox_instance = Mock()
            mock_msgbox.return_value = mock_msgbox_instance
            mock_msgbox_instance.addButton.return_value = Mock()
            mock_msgbox_instance.clickedButton.return_value = Mock()
            
            widget._show_transaction_success(sample_completed_sale)
            
            # Verify success dialog was created and shown
            mock_msgbox.assert_called_once()
            mock_msgbox_instance.exec.assert_called_once()
    
    def test_receipt_text_generation(self, app, mock_sales_manager, sample_completed_sale):
        """Test receipt text generation"""
        widget = CartWidget(mock_sales_manager)
        
        receipt_text = widget._generate_receipt_text(sample_completed_sale)
        
        # Verify receipt contains key information
        assert "MEDICAL STORE RECEIPT" in receipt_text
        assert f"Transaction ID: {sample_completed_sale.id}" in receipt_text
        assert f"Date: {sample_completed_sale.date}" in receipt_text
        assert f"Payment Method: {sample_completed_sale.payment_method.title()}" in receipt_text
        assert f"TOTAL: ${sample_completed_sale.total:.2f}" in receipt_text
        
        # Verify items are included
        for item in sample_completed_sale.items:
            assert item.name in receipt_text
            assert f"Qty: {item.quantity}" in receipt_text
            assert f"${item.unit_price:.2f}" in receipt_text
    
    def test_print_receipt_placeholder(self, app, mock_sales_manager, sample_completed_sale):
        """Test print receipt placeholder functionality"""
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            widget._print_receipt(sample_completed_sale)
            
            # Should show placeholder message
            mock_msgbox.information.assert_called_once()
    
    def test_complete_sale_button_state(self, app, mock_sales_manager):
        """Test complete sale button enabled/disabled state"""
        widget = CartWidget(mock_sales_manager)
        
        # Initially disabled for empty cart
        assert not widget.complete_sale_button.isEnabled()
        
        # Enable when cart has items
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_cart_items.return_value = [
            SaleItem(1, "Test", 1, 10.0, 10.0)
        ]
        
        widget.refresh_cart()
        
        assert widget.complete_sale_button.isEnabled()


class TestReceiptDialog:
    """Test cases for receipt dialog"""
    
    def test_receipt_dialog_initialization(self, app, sample_completed_sale):
        """Test receipt dialog initialization"""
        dialog = ReceiptDialog(sample_completed_sale)
        
        assert dialog is not None
        assert dialog.sale == sample_completed_sale
        assert dialog.windowTitle() == f"Receipt - Transaction {sample_completed_sale.id}"
    
    def test_receipt_dialog_content(self, app, sample_completed_sale):
        """Test receipt dialog content population"""
        dialog = ReceiptDialog(sample_completed_sale)
        
        # Get the receipt text
        receipt_text = dialog.receipt_text.toPlainText()
        
        # Verify key information is present
        assert "MEDICAL STORE MANAGEMENT SYSTEM" in receipt_text
        assert f"Transaction ID: {sample_completed_sale.id}" in receipt_text
        assert f"Date: {sample_completed_sale.date}" in receipt_text
        assert f"TOTAL AMOUNT: ${sample_completed_sale.total:.2f}" in receipt_text
        
        # Verify items are listed
        for item in sample_completed_sale.items:
            assert item.name in receipt_text
    
    def test_receipt_dialog_print_button(self, app, sample_completed_sale):
        """Test receipt dialog print button"""
        dialog = ReceiptDialog(sample_completed_sale)
        
        with patch('medical_store_app.ui.dialogs.receipt_dialog.QMessageBox') as mock_msgbox:
            dialog._print_receipt()
            
            # Should show placeholder print message
            mock_msgbox.information.assert_called_once()


class TestCompleteWorkflowIntegration:
    """Integration tests for complete billing workflow"""
    
    def test_end_to_end_billing_workflow(self, app, mock_medicine_manager, mock_sales_manager, sample_medicines, sample_completed_sale):
        """Test complete end-to-end billing workflow"""
        # Setup mocks for complete workflow
        mock_medicine_manager.search_medicines.return_value = sample_medicines
        mock_sales_manager.add_to_cart.return_value = (True, "Added", None)
        mock_sales_manager.is_cart_empty.return_value = False  # Cart has items
        mock_sales_manager.get_cart_items.return_value = [
            SaleItem(1, "Medicine 1", 2, 10.0, 20.0)
        ]
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 20.0,
            'discount': 0.0,
            'tax': 2.0,
            'total': 22.0
        }
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 20.0,
            'discount': 0.0,
            'tax': 2.0,
            'total': 22.0
        }
        mock_sales_manager.complete_sale.return_value = (True, "Sale completed", sample_completed_sale)
        mock_sales_manager.set_payment_method.return_value = (True, "Payment method set")
        
        # Create billing widget
        billing_widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Step 1: Search for products
        billing_widget.product_search.search_input.setText("Medicine")
        billing_widget.product_search._perform_search()
        
        # Verify search was performed
        mock_medicine_manager.search_medicines.assert_called_with("Medicine")
        
        # Step 2: Add product to cart
        billing_widget._on_product_selected(sample_medicines[0], 2)
        
        # Verify product was added to cart
        mock_sales_manager.add_to_cart.assert_called_with(sample_medicines[0].id, 2)
        
        # Step 3: Set payment method
        billing_widget.cart_widget.payment_method_combo.setCurrentText("Card")
        billing_widget.cart_widget._on_payment_method_changed("Card")
        
        # Verify payment method was set
        mock_sales_manager.set_payment_method.assert_called_with("card")
        
        # Step 4: Complete sale
        from PySide6.QtWidgets import QMessageBox as RealQMessageBox
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.StandardButton = RealQMessageBox.StandardButton
            mock_msgbox.question.return_value = RealQMessageBox.StandardButton.Yes
            
            billing_widget.cart_widget._complete_sale()
            
            # Verify sale was completed
            mock_sales_manager.complete_sale.assert_called_once_with(cashier_id=None, customer_name=None)
    
    def test_workflow_with_discount_and_tax(self, app, mock_medicine_manager, mock_sales_manager, sample_medicines, sample_completed_sale):
        """Test billing workflow with discount and tax"""
        # Setup mocks
        mock_medicine_manager.search_medicines.return_value = sample_medicines
        mock_sales_manager.add_to_cart.return_value = (True, "Added", None)
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.set_discount.return_value = (True, "Discount set")
        mock_sales_manager.set_tax_rate.return_value = (True, "Tax rate set")
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 100.0,
            'discount': 10.0,
            'tax': 9.0,
            'total': 99.0
        }
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 100.0,
            'discount': 10.0,
            'tax': 9.0,
            'total': 99.0
        }
        mock_sales_manager.complete_sale.return_value = (True, "Sale completed", sample_completed_sale)
        
        billing_widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Add product to cart
        billing_widget._on_product_selected(sample_medicines[0], 1)
        
        # Apply discount
        billing_widget.cart_widget.discount_input.setValue(10.0)
        billing_widget.cart_widget._on_discount_changed(10.0)
        
        # Apply tax
        billing_widget.cart_widget.tax_rate_input.setValue(10.0)
        billing_widget.cart_widget._on_tax_rate_changed(10.0)
        
        # Complete sale
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            billing_widget.cart_widget._complete_sale()
            
            # Verify all operations were performed
            mock_sales_manager.set_discount.assert_called_with(10.0)
            mock_sales_manager.set_tax_rate.assert_called_with(10.0)
            mock_sales_manager.complete_sale.assert_called_once()
    
    def test_workflow_error_handling(self, app, mock_medicine_manager, mock_sales_manager, sample_medicines):
        """Test workflow error handling"""
        # Setup mocks for various error scenarios
        mock_medicine_manager.search_medicines.return_value = sample_medicines
        mock_sales_manager.add_to_cart.return_value = (False, "Insufficient stock", None)
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.complete_sale.return_value = (False, "Database error", None)
        
        billing_widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Test add to cart error
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            billing_widget._on_product_selected(sample_medicines[0], 100)  # Large quantity
            
            # Should show error message
            mock_msgbox.warning.assert_called_once()
        
        # Test complete sale error
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 20.0,
            'discount': 0.0,
            'tax': 2.0,
            'total': 22.0
        }
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            billing_widget.cart_widget._complete_sale()
            
            # Should show error message
            mock_msgbox.critical.assert_called_once()
    
    def test_workflow_state_consistency(self, app, mock_medicine_manager, mock_sales_manager, sample_medicines):
        """Test workflow maintains consistent state"""
        # Setup mocks - initially empty cart
        mock_medicine_manager.search_medicines.return_value = sample_medicines
        mock_sales_manager.add_to_cart.return_value = (True, "Added", None)
        mock_sales_manager.is_cart_empty.return_value = True  # Start with empty cart
        mock_sales_manager.get_cart_items.return_value = []
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 0.0,
            'discount': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 0,
            'subtotal': 0.0,
            'discount': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        
        billing_widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Initially cart should be empty
        assert not billing_widget.cart_widget.complete_sale_button.isEnabled()
        
        # Simulate adding item to cart
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_cart_items.return_value = [
            SaleItem(1, "Medicine 1", 1, 10.0, 10.0)
        ]
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 10.0,
            'discount': 0.0,
            'tax': 1.0,
            'total': 11.0
        }
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 10.0,
            'discount': 0.0,
            'tax': 1.0,
            'total': 11.0
        }
        
        billing_widget._on_product_selected(sample_medicines[0], 1)
        billing_widget.cart_widget.refresh_cart()
        
        # Button should be enabled
        assert billing_widget.cart_widget.complete_sale_button.isEnabled()
        
        # Simulate clearing cart
        mock_sales_manager.is_cart_empty.return_value = True
        mock_sales_manager.get_cart_items.return_value = []
        mock_sales_manager.calculate_cart_totals.return_value = {
            'subtotal': 0.0,
            'discount': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 0,
            'subtotal': 0.0,
            'discount': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        mock_sales_manager.clear_cart.return_value = True
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            billing_widget.cart_widget.clear_cart()
            billing_widget.cart_widget.refresh_cart()
        
        # Button should be disabled again
        assert not billing_widget.cart_widget.complete_sale_button.isEnabled()
    
    def test_transaction_with_cashier_id(self, app, mock_medicine_manager, mock_sales_manager, sample_completed_sale):
        """Test transaction processing with cashier ID"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_current_cart_summary.return_value = {
            'item_count': 1,
            'subtotal': 20.0,
            'discount': 0.0,
            'tax': 2.0,
            'total': 22.0
        }
        mock_sales_manager.complete_sale.return_value = (True, "Sale completed", sample_completed_sale)
        
        billing_widget = BillingWidget(mock_medicine_manager, mock_sales_manager)
        
        # Mock the complete sale with cashier ID
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
            
            billing_widget.cart_widget._complete_sale()
            
            # Verify sale was completed with None cashier_id (will be updated when auth is implemented)
            mock_sales_manager.complete_sale.assert_called_once_with(cashier_id=None, customer_name=None)
    
    def test_receipt_dialog_with_customer_name(self, app, sample_completed_sale):
        """Test receipt dialog with customer name"""
        sample_completed_sale.customer_name = "Jane Doe"
        
        dialog = ReceiptDialog(sample_completed_sale)
        receipt_text = dialog.receipt_text.toPlainText()
        
        # Verify customer name is included in receipt
        assert "Customer: Jane Doe" in receipt_text
    
    def test_receipt_dialog_with_cashier_id(self, app, sample_completed_sale):
        """Test receipt dialog with cashier ID"""
        sample_completed_sale.cashier_id = 123
        
        dialog = ReceiptDialog(sample_completed_sale)
        receipt_text = dialog.receipt_text.toPlainText()
        
        # Verify cashier ID is included in receipt
        assert "Cashier ID: 123" in receipt_text
    
    def test_transaction_processing_exception_handling(self, app, mock_sales_manager):
        """Test transaction processing with exceptions"""
        mock_sales_manager.is_cart_empty.return_value = False
        mock_sales_manager.get_current_cart_summary.side_effect = Exception("Database error")
        
        widget = CartWidget(mock_sales_manager)
        
        with patch('medical_store_app.ui.components.billing_widget.QMessageBox') as mock_msgbox:
            widget._complete_sale()
            
            # Should show error message
            mock_msgbox.critical.assert_called_once()
    
    def test_receipt_generation_exception_handling(self, app, mock_sales_manager):
        """Test receipt generation with exceptions"""
        # Create a sale with invalid data to trigger exception
        invalid_sale = Sale()
        invalid_sale.id = None  # This should cause an error in receipt generation
        
        widget = CartWidget(mock_sales_manager)
        
        # This should not raise an exception, but handle it gracefully
        receipt_text = widget._generate_receipt_text(invalid_sale)
        
        # Should return a receipt with None ID and $0.00 total
        assert "Transaction ID: None" in receipt_text and "TOTAL: $0.00" in receipt_text


if __name__ == "__main__":
    pytest.main([__file__])