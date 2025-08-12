"""
Unit tests for Sales Manager
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from medical_store_app.managers.sales_manager import SalesManager
from medical_store_app.models.sale import Sale, SaleItem
from medical_store_app.models.medicine import Medicine
from medical_store_app.repositories.sales_repository import SalesRepository
from medical_store_app.repositories.medicine_repository import MedicineRepository


class TestSalesManager:
    """Test cases for SalesManager class"""
    
    @pytest.fixture
    def mock_sales_repository(self):
        """Create mock sales repository"""
        return Mock(spec=SalesRepository)
    
    @pytest.fixture
    def mock_medicine_repository(self):
        """Create mock medicine repository"""
        return Mock(spec=MedicineRepository)
    
    @pytest.fixture
    def sales_manager(self, mock_sales_repository, mock_medicine_repository):
        """Create sales manager with mock repositories"""
        return SalesManager(mock_sales_repository, mock_medicine_repository)
    
    @pytest.fixture
    def sample_medicine(self):
        """Sample medicine for testing"""
        return Medicine(
            id=1,
            name='Test Medicine',
            category='Test Category',
            batch_no='TEST001',
            expiry_date='2025-12-31',
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0,
            barcode='TEST123456789'
        )
    
    @pytest.fixture
    def sample_sale_item(self):
        """Sample sale item for testing"""
        return SaleItem(
            medicine_id=1,
            name='Test Medicine',
            quantity=2,
            unit_price=15.0,
            total_price=30.0,
            batch_no='TEST001'
        )
    
    @pytest.fixture
    def sample_sale(self, sample_sale_item):
        """Sample sale for testing"""
        return Sale(
            id=1,
            date='2024-01-15',
            items=[sample_sale_item],
            subtotal=30.0,
            discount=0.0,
            tax=0.0,
            total=30.0,
            payment_method='cash',
            cashier_id=1
        )
    
    def test_add_to_cart_success(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test successful addition to cart"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        
        # Act
        success, message, sale_item = sales_manager.add_to_cart(1, 5)
        
        # Assert
        assert success is True
        assert "Added 5 units" in message
        assert sale_item is not None
        assert sale_item.quantity == 5
        assert sale_item.medicine_id == 1
        assert len(sales_manager.get_cart_items()) == 1
    
    def test_add_to_cart_invalid_quantity(self, sales_manager):
        """Test adding to cart with invalid quantity"""
        # Act
        success, message, sale_item = sales_manager.add_to_cart(1, 0)
        
        # Assert
        assert success is False
        assert "Quantity must be positive" in message
        assert sale_item is None
    
    def test_add_to_cart_medicine_not_found(self, sales_manager, mock_medicine_repository):
        """Test adding to cart when medicine not found"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = None
        
        # Act
        success, message, sale_item = sales_manager.add_to_cart(999, 5)
        
        # Assert
        assert success is False
        assert "not found" in message
        assert sale_item is None
    
    def test_add_to_cart_insufficient_stock(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test adding to cart with insufficient stock"""
        # Arrange
        sample_medicine.quantity = 3  # Less than requested
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        
        # Act
        success, message, sale_item = sales_manager.add_to_cart(1, 5)
        
        # Assert
        assert success is False
        assert "Insufficient stock" in message
        assert sale_item is None
    
    def test_add_to_cart_existing_item(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test adding to cart when item already exists"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        
        # Act - Add first time
        success1, _, item1 = sales_manager.add_to_cart(1, 3)
        # Act - Add second time (same medicine)
        success2, message2, item2 = sales_manager.add_to_cart(1, 2)
        
        # Assert
        assert success1 is True
        assert success2 is True
        assert len(sales_manager.get_cart_items()) == 1  # Still one item
        assert sales_manager.get_cart_items()[0].quantity == 5  # Combined quantity
    
    def test_remove_from_cart_success(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test successful removal from cart"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 5)
        
        # Act
        success, message = sales_manager.remove_from_cart(1)
        
        # Assert
        assert success is True
        assert "Removed" in message
        assert len(sales_manager.get_cart_items()) == 0
    
    def test_remove_from_cart_not_found(self, sales_manager):
        """Test removing non-existent item from cart"""
        # Act
        success, message = sales_manager.remove_from_cart(999)
        
        # Assert
        assert success is False
        assert "not found in cart" in message
    
    def test_update_cart_item_quantity_success(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test successful quantity update"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 5)
        
        # Act
        success, message = sales_manager.update_cart_item_quantity(1, 8)
        
        # Assert
        assert success is True
        assert "Updated" in message
        assert sales_manager.get_cart_items()[0].quantity == 8
    
    def test_update_cart_item_quantity_zero_removes_item(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test updating quantity to zero removes item"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 5)
        
        # Act
        success, message = sales_manager.update_cart_item_quantity(1, 0)
        
        # Assert
        assert success is True
        assert len(sales_manager.get_cart_items()) == 0
    
    def test_clear_cart(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test clearing cart"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 5)
        sales_manager.set_discount(10.0)
        
        # Act
        result = sales_manager.clear_cart()
        
        # Assert
        assert result is True
        assert len(sales_manager.get_cart_items()) == 0
        assert sales_manager.get_current_discount() == 0.0
    
    def test_calculate_cart_totals_no_discount_no_tax(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test cart totals calculation without discount or tax"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 2)  # 2 * 15.0 = 30.0
        
        # Act
        totals = sales_manager.calculate_cart_totals()
        
        # Assert
        assert totals['subtotal'] == 30.0
        assert totals['discount'] == 0.0
        assert totals['tax'] == 0.0
        assert totals['total'] == 30.0
    
    def test_calculate_cart_totals_with_discount_and_tax(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test cart totals calculation with discount and tax"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 2)  # 2 * 15.0 = 30.0
        sales_manager.set_discount(5.0)  # 30.0 - 5.0 = 25.0
        sales_manager.set_tax_rate(10.0)  # 25.0 * 0.1 = 2.5
        
        # Act
        totals = sales_manager.calculate_cart_totals()
        
        # Assert
        assert totals['subtotal'] == 30.0
        assert totals['discount'] == 5.0
        assert totals['tax'] == 2.5
        assert totals['total'] == 27.5  # 25.0 + 2.5
    
    def test_set_discount_success(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test setting discount successfully"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 2)  # subtotal = 30.0
        
        # Act
        success, message = sales_manager.set_discount(10.0)
        
        # Assert
        assert success is True
        assert "Discount set to $10.00" in message
        assert sales_manager.get_current_discount() == 10.0
    
    def test_set_discount_negative(self, sales_manager):
        """Test setting negative discount"""
        # Act
        success, message = sales_manager.set_discount(-5.0)
        
        # Assert
        assert success is False
        assert "cannot be negative" in message
    
    def test_set_discount_exceeds_subtotal(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test setting discount that exceeds subtotal"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 2)  # subtotal = 30.0
        
        # Act
        success, message = sales_manager.set_discount(50.0)
        
        # Assert
        assert success is False
        assert "cannot exceed subtotal" in message
    
    def test_set_tax_rate_success(self, sales_manager):
        """Test setting tax rate successfully"""
        # Act
        success, message = sales_manager.set_tax_rate(15.0)
        
        # Assert
        assert success is True
        assert "Tax rate set to 15.0%" in message
        assert sales_manager.get_current_tax_rate() == 15.0
    
    def test_set_tax_rate_negative(self, sales_manager):
        """Test setting negative tax rate"""
        # Act
        success, message = sales_manager.set_tax_rate(-5.0)
        
        # Assert
        assert success is False
        assert "cannot be negative" in message
    
    def test_set_tax_rate_over_100(self, sales_manager):
        """Test setting tax rate over 100%"""
        # Act
        success, message = sales_manager.set_tax_rate(150.0)
        
        # Assert
        assert success is False
        assert "cannot exceed 100%" in message
    
    def test_set_payment_method_success(self, sales_manager):
        """Test setting payment method successfully"""
        # Act
        success, message = sales_manager.set_payment_method('card')
        
        # Assert
        assert success is True
        assert "Payment method set to card" in message
        assert sales_manager.get_current_payment_method() == 'card'
    
    def test_set_payment_method_invalid(self, sales_manager):
        """Test setting invalid payment method"""
        # Act
        success, message = sales_manager.set_payment_method('crypto')
        
        # Assert
        assert success is False
        assert "Invalid payment method" in message
    
    def test_complete_sale_success(self, sales_manager, mock_sales_repository, mock_medicine_repository, sample_medicine, sample_sale):
        """Test successful sale completion"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        mock_sales_repository.save.return_value = sample_sale
        mock_sales_repository.update_medicine_stock_after_sale.return_value = True
        
        sales_manager.add_to_cart(1, 2)
        
        # Act
        success, message, sale = sales_manager.complete_sale(cashier_id=1)
        
        # Assert
        assert success is True
        assert "completed successfully" in message
        assert sale is not None
        assert len(sales_manager.get_cart_items()) == 0  # Cart should be cleared
        mock_sales_repository.save.assert_called_once()
        mock_sales_repository.update_medicine_stock_after_sale.assert_called_once()
    
    def test_complete_sale_empty_cart(self, sales_manager):
        """Test completing sale with empty cart"""
        # Act
        success, message, sale = sales_manager.complete_sale()
        
        # Assert
        assert success is False
        assert "empty cart" in message
        assert sale is None
    
    def test_complete_sale_insufficient_stock(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test completing sale with insufficient stock"""
        # Arrange - First add to cart with sufficient stock, then reduce stock
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 2)  # Add with sufficient stock
        
        # Now reduce stock to simulate stock change after adding to cart
        sample_medicine.quantity = 1  # Less than cart quantity
        
        # Act
        success, message, sale = sales_manager.complete_sale()
        
        # Assert
        assert success is False
        assert "Insufficient stock" in message
        assert sale is None
    
    def test_complete_sale_save_failure(self, sales_manager, mock_sales_repository, mock_medicine_repository, sample_medicine):
        """Test completing sale when save fails"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        mock_sales_repository.save.return_value = None
        sales_manager.add_to_cart(1, 2)
        
        # Act
        success, message, sale = sales_manager.complete_sale()
        
        # Assert
        assert success is False
        assert "Failed to save" in message
        assert sale is None
    
    def test_complete_sale_stock_update_failure(self, sales_manager, mock_sales_repository, mock_medicine_repository, sample_medicine, sample_sale):
        """Test completing sale when stock update fails"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        mock_sales_repository.save.return_value = sample_sale
        mock_sales_repository.update_medicine_stock_after_sale.return_value = False
        sales_manager.add_to_cart(1, 2)
        
        # Act
        success, message, sale = sales_manager.complete_sale()
        
        # Assert
        assert success is False
        assert "failed to update stock" in message
        assert sale is not None  # Sale is still returned
    
    def test_search_products(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test product search"""
        # Arrange
        mock_medicine_repository.search.return_value = [sample_medicine]
        
        # Act
        results = sales_manager.search_products('test')
        
        # Assert
        assert len(results) == 1
        assert results[0] == sample_medicine
        mock_medicine_repository.search.assert_called_once_with('test')
    
    def test_search_products_empty_query(self, sales_manager, mock_medicine_repository):
        """Test product search with empty query"""
        # Act
        results = sales_manager.search_products('')
        
        # Assert
        assert results == []
        mock_medicine_repository.search.assert_not_called()
    
    def test_search_products_filters_out_of_stock(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test product search filters out medicines with no stock"""
        # Arrange
        out_of_stock_medicine = Medicine(id=2, name='Out of Stock', quantity=0, selling_price=10.0)
        mock_medicine_repository.search.return_value = [sample_medicine, out_of_stock_medicine]
        
        # Act
        results = sales_manager.search_products('test')
        
        # Assert
        assert len(results) == 1
        assert results[0] == sample_medicine  # Only in-stock medicine returned
    
    def test_search_products_by_barcode(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test product search by barcode"""
        # Arrange
        mock_medicine_repository.find_by_barcode.return_value = sample_medicine
        
        # Act
        result = sales_manager.search_products_by_barcode('TEST123456789')
        
        # Assert
        assert result == sample_medicine
        mock_medicine_repository.find_by_barcode.assert_called_once_with('TEST123456789')
    
    def test_search_products_by_barcode_out_of_stock(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test product search by barcode for out of stock medicine"""
        # Arrange
        sample_medicine.quantity = 0
        mock_medicine_repository.find_by_barcode.return_value = sample_medicine
        
        # Act
        result = sales_manager.search_products_by_barcode('TEST123456789')
        
        # Assert
        assert result is None  # Should return None for out of stock
    
    def test_get_recent_sales(self, sales_manager, mock_sales_repository, sample_sale):
        """Test getting recent sales"""
        # Arrange
        mock_sales_repository.get_recent_sales.return_value = [sample_sale]
        
        # Act
        results = sales_manager.get_recent_sales(5)
        
        # Assert
        assert len(results) == 1
        assert results[0] == sample_sale
        mock_sales_repository.get_recent_sales.assert_called_once_with(5)
    
    def test_get_daily_sales(self, sales_manager, mock_sales_repository, sample_sale):
        """Test getting daily sales"""
        # Arrange
        mock_sales_repository.get_daily_sales.return_value = [sample_sale]
        
        # Act
        results = sales_manager.get_daily_sales('2024-01-15')
        
        # Assert
        assert len(results) == 1
        assert results[0] == sample_sale
        mock_sales_repository.get_daily_sales.assert_called_once_with('2024-01-15')
    
    def test_get_sales_analytics(self, sales_manager, mock_sales_repository):
        """Test getting sales analytics"""
        # Arrange
        analytics_data = {'total_revenue': 1000.0, 'total_transactions': 10}
        mock_sales_repository.get_sales_analytics.return_value = analytics_data
        
        # Act
        result = sales_manager.get_sales_analytics('2024-01-01', '2024-01-31')
        
        # Assert
        assert result == analytics_data
        mock_sales_repository.get_sales_analytics.assert_called_once_with('2024-01-01', '2024-01-31')
    
    def test_get_current_cart_summary(self, sales_manager, mock_medicine_repository, sample_medicine):
        """Test getting current cart summary"""
        # Arrange
        mock_medicine_repository.find_by_id.return_value = sample_medicine
        sales_manager.add_to_cart(1, 2)
        sales_manager.set_discount(5.0)
        sales_manager.set_tax_rate(10.0)
        
        # Act
        summary = sales_manager.get_current_cart_summary()
        
        # Assert
        assert summary['item_count'] == 1
        assert summary['total_quantity'] == 2
        assert summary['subtotal'] == 30.0
        assert summary['discount'] == 5.0
        assert summary['tax'] == 2.5
        assert summary['total'] == 27.5
        assert len(summary['items']) == 1
    
    def test_cart_state_methods(self, sales_manager):
        """Test cart state checking methods"""
        # Test empty cart
        assert sales_manager.is_cart_empty() is True
        assert sales_manager.get_cart_count() == 0
        
        # Add item and test again
        with patch.object(sales_manager.medicine_repository, 'find_by_id') as mock_find:
            mock_find.return_value = Medicine(id=1, name='Test', quantity=10, selling_price=15.0)
            sales_manager.add_to_cart(1, 2)
        
        assert sales_manager.is_cart_empty() is False
        assert sales_manager.get_cart_count() == 1
    
    def test_exception_handling(self, sales_manager, mock_medicine_repository):
        """Test exception handling in various methods"""
        # Arrange
        mock_medicine_repository.find_by_id.side_effect = Exception("Database error")
        
        # Act & Assert
        success, message, item = sales_manager.add_to_cart(1, 5)
        assert success is False
        assert "Error adding to cart" in message
        
        results = sales_manager.search_products("test")
        assert results == []