"""
Sales Manager for Medical Store Management Application
Coordinates billing operations, cart management, and transaction processing
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime

from ..models.sale import Sale, SaleItem
from ..models.medicine import Medicine
from ..repositories.sales_repository import SalesRepository
from ..repositories.medicine_repository import MedicineRepository
from ..repositories.settings_repository import SettingsRepository
from ..utils.currency_formatter import SettingsManager


class SalesManager:
    """Manager class for billing and sales operations"""
    
    def __init__(self, sales_repository: SalesRepository, medicine_repository: MedicineRepository, settings_repository: Optional[SettingsRepository] = None):
        """
        Initialize sales manager
        
        Args:
            sales_repository: Sales repository instance
            medicine_repository: Medicine repository instance
            settings_repository: Settings repository instance (optional)
        """
        self.sales_repository = sales_repository
        self.medicine_repository = medicine_repository
        self.settings_repository = settings_repository
        self.logger = logging.getLogger(__name__)
        self._current_cart: List[SaleItem] = []
        self._current_discount = 0.0
        self._current_payment_method = "cash"
        
        # Initialize tax rate from settings
        self.settings_manager = None
        self._current_tax_rate = 0.0
        if self.settings_repository:
            self.settings_manager = SettingsManager(self.settings_repository)
            self._current_tax_rate = self.settings_manager.get_default_tax_rate()
    
    # Cart Management Methods
    
    def add_to_cart(self, medicine_id: int, quantity: int) -> Tuple[bool, str, Optional[SaleItem]]:
        """
        Add medicine to cart
        
        Args:
            medicine_id: ID of medicine to add
            quantity: Quantity to add
            
        Returns:
            Tuple of (success, message, sale_item)
        """
        try:
            # Validate quantity
            if quantity <= 0:
                return False, "Quantity must be positive", None
            
            # Find medicine
            medicine = self.medicine_repository.find_by_id(medicine_id)
            if not medicine:
                return False, f"Medicine with ID {medicine_id} not found", None
            
            # Check stock availability
            if not medicine.can_sell(quantity):
                return False, f"Insufficient stock. Available: {medicine.quantity}, Requested: {quantity}", None
            
            # Check if medicine already in cart
            existing_item = None
            for item in self._current_cart:
                if item.medicine_id == medicine_id:
                    existing_item = item
                    break
            
            if existing_item:
                # Update existing item quantity
                new_quantity = existing_item.quantity + quantity
                if not medicine.can_sell(new_quantity):
                    return False, f"Insufficient stock for total quantity. Available: {medicine.quantity}, Total requested: {new_quantity}", None
                
                existing_item.quantity = new_quantity
                existing_item.total_price = round(existing_item.quantity * existing_item.unit_price, 2)
                sale_item = existing_item
            else:
                # Create new cart item
                sale_item = SaleItem(
                    medicine_id=medicine_id,
                    name=medicine.name,
                    quantity=quantity,
                    unit_price=medicine.selling_price,
                    total_price=round(quantity * medicine.selling_price, 2),
                    batch_no=medicine.batch_no
                )
                self._current_cart.append(sale_item)
            
            success_msg = f"Added {quantity} units of {medicine.name} to cart"
            self.logger.info(success_msg)
            return True, success_msg, sale_item
            
        except Exception as e:
            error_msg = f"Error adding to cart: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def remove_from_cart(self, medicine_id: int) -> Tuple[bool, str]:
        """
        Remove medicine from cart
        
        Args:
            medicine_id: ID of medicine to remove
            
        Returns:
            Tuple of (success, message)
        """
        try:
            for i, item in enumerate(self._current_cart):
                if item.medicine_id == medicine_id:
                    removed_item = self._current_cart.pop(i)
                    success_msg = f"Removed {removed_item.name} from cart"
                    self.logger.info(success_msg)
                    return True, success_msg
            
            return False, f"Medicine with ID {medicine_id} not found in cart"
            
        except Exception as e:
            error_msg = f"Error removing from cart: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def update_cart_item_quantity(self, medicine_id: int, new_quantity: int) -> Tuple[bool, str]:
        """
        Update quantity of item in cart
        
        Args:
            medicine_id: ID of medicine to update
            new_quantity: New quantity
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if new_quantity <= 0:
                return self.remove_from_cart(medicine_id)
            
            # Find item in cart
            cart_item = None
            for item in self._current_cart:
                if item.medicine_id == medicine_id:
                    cart_item = item
                    break
            
            if not cart_item:
                return False, f"Medicine with ID {medicine_id} not found in cart"
            
            # Check stock availability
            medicine = self.medicine_repository.find_by_id(medicine_id)
            if not medicine:
                return False, f"Medicine with ID {medicine_id} not found"
            
            if not medicine.can_sell(new_quantity):
                return False, f"Insufficient stock. Available: {medicine.quantity}, Requested: {new_quantity}"
            
            # Update quantity and total
            cart_item.quantity = new_quantity
            cart_item.total_price = round(cart_item.quantity * cart_item.unit_price, 2)
            
            success_msg = f"Updated {medicine.name} quantity to {new_quantity}"
            self.logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Error updating cart item quantity: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def clear_cart(self) -> bool:
        """
        Clear all items from cart
        
        Returns:
            True if cart cleared successfully
        """
        try:
            self._current_cart.clear()
            self._current_discount = 0.0
            self._current_tax_rate = 0.0
            self._current_payment_method = "cash"
            self.logger.info("Cart cleared")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cart: {str(e)}")
            return False
    
    def get_cart_items(self) -> List[SaleItem]:
        """
        Get current cart items
        
        Returns:
            List of current cart items
        """
        return self._current_cart.copy()
    
    def get_cart_count(self) -> int:
        """
        Get number of items in cart
        
        Returns:
            Number of items in cart
        """
        return len(self._current_cart)
    
    def is_cart_empty(self) -> bool:
        """
        Check if cart is empty
        
        Returns:
            True if cart is empty
        """
        return len(self._current_cart) == 0
    
    # Calculation Methods
    
    def calculate_cart_totals(self) -> Dict[str, float]:
        """
        Calculate cart totals including subtotal, discount, tax, and total
        
        Returns:
            Dictionary with calculated totals
        """
        try:
            subtotal = sum(item.total_price for item in self._current_cart)
            
            # Apply discount
            discount_amount = min(self._current_discount, subtotal)  # Discount cannot exceed subtotal
            discounted_amount = subtotal - discount_amount
            
            # Calculate tax
            tax_amount = round(discounted_amount * (self._current_tax_rate / 100), 2)
            
            # Calculate final total
            total = round(discounted_amount + tax_amount, 2)
            
            return {
                'subtotal': round(subtotal, 2),
                'discount': round(discount_amount, 2),
                'tax': round(tax_amount, 2),
                'total': total
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating cart totals: {str(e)}")
            return {'subtotal': 0.0, 'discount': 0.0, 'tax': 0.0, 'total': 0.0}
    
    def set_discount(self, discount: float) -> Tuple[bool, str]:
        """
        Set discount amount for current cart
        
        Args:
            discount: Discount amount
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if discount < 0:
                return False, "Discount cannot be negative"
            
            subtotal = sum(item.total_price for item in self._current_cart)
            if discount > subtotal:
                return False, f"Discount cannot exceed subtotal (${subtotal:.2f})"
            
            self._current_discount = discount
            return True, f"Discount set to ${discount:.2f}"
            
        except Exception as e:
            error_msg = f"Error setting discount: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def set_tax_rate(self, tax_rate: float) -> Tuple[bool, str]:
        """
        Set tax rate for current cart
        
        Args:
            tax_rate: Tax rate as percentage (e.g., 10.0 for 10%)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if tax_rate < 0:
                return False, "Tax rate cannot be negative"
            if tax_rate > 100:
                return False, "Tax rate cannot exceed 100%"
            
            self._current_tax_rate = tax_rate
            return True, f"Tax rate set to {tax_rate}%"
            
        except Exception as e:
            error_msg = f"Error setting tax rate: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def set_payment_method(self, payment_method: str) -> Tuple[bool, str]:
        """
        Set payment method for current cart
        
        Args:
            payment_method: Payment method
            
        Returns:
            Tuple of (success, message)
        """
        try:
            valid_methods = ["cash", "card", "upi", "cheque", "bank_transfer"]
            if payment_method not in valid_methods:
                return False, f"Invalid payment method. Valid options: {', '.join(valid_methods)}"
            
            self._current_payment_method = payment_method
            return True, f"Payment method set to {payment_method}"
            
        except Exception as e:
            error_msg = f"Error setting payment method: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    # Transaction Processing Methods
    
    def complete_sale(self, cashier_id: Optional[int] = None, customer_name: Optional[str] = None) -> Tuple[bool, str, Optional[Sale]]:
        """
        Complete the current sale transaction
        
        Args:
            cashier_id: ID of cashier processing the sale
            
        Returns:
            Tuple of (success, message, sale_instance)
        """
        try:
            # Validate cart
            if self.is_cart_empty():
                return False, "Cannot complete sale with empty cart", None
            
            # Calculate totals
            totals = self.calculate_cart_totals()
            
            # Create sale instance
            sale = Sale(
                date=date.today().isoformat(),
                items=self._current_cart.copy(),
                subtotal=totals['subtotal'],
                discount=totals['discount'],
                tax=totals['tax'],
                total=totals['total'],
                payment_method=self._current_payment_method,
                cashier_id=cashier_id,
                customer_name=customer_name.strip() if customer_name else None
            )
            
            # Validate sale
            validation_errors = sale.validate()
            if validation_errors:
                error_msg = f"Sale validation failed: {'; '.join(validation_errors)}"
                self.logger.error(error_msg)
                return False, error_msg, None
            
            # Check stock availability for all items
            for item in sale.items:
                medicine = self.medicine_repository.find_by_id(item.medicine_id)
                if not medicine:
                    return False, f"Medicine {item.name} not found", None
                if not medicine.can_sell(item.quantity):
                    return False, f"Insufficient stock for {item.name}. Available: {medicine.quantity}", None
            
            # Save sale
            saved_sale = self.sales_repository.save(sale)
            if not saved_sale:
                return False, "Failed to save sale to database", None
            
            # Update medicine stock
            if not self.sales_repository.update_medicine_stock_after_sale(saved_sale):
                # If stock update fails, we should ideally rollback the sale
                # For now, we'll log the error and continue
                self.logger.error(f"Failed to update stock after sale ID {saved_sale.id}")
                return False, "Sale saved but failed to update stock", saved_sale
            
            # Generate invoice
            try:
                from ..utils.invoice_generator import InvoiceGenerator
                store_info = self.get_store_info()
                invoice = InvoiceGenerator(
                    sale=saved_sale,
                    store_info=store_info,
                    currency_symbol=self.get_currency_symbol()
                )
                invoice_path = invoice.generate()
                self.logger.info(f"Invoice generated at: {invoice_path}")
            except Exception as e:
                self.logger.error(f"Error generating invoice: {str(e)}")

            # Clear cart after successful sale
            self.clear_cart()
            
            success_msg = f"Sale completed successfully. Total: {self.format_currency(saved_sale.total)}"
            self.logger.info(f"Sale completed: ID {saved_sale.id}, Total: {self.format_currency(saved_sale.total)}")
            return True, success_msg, saved_sale
            
        except Exception as e:
            error_msg = f"Error completing sale: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    # Product Search Methods
    
    def search_products(self, query: str) -> List[Medicine]:
        """
        Search products for billing
        
        Args:
            query: Search query (name or barcode)
            
        Returns:
            List of matching medicines with stock > 0
        """
        try:
            if not query or not query.strip():
                return []
            
            # Search medicines
            medicines = self.medicine_repository.search(query.strip())
            
            # Filter out medicines with no stock
            available_medicines = [m for m in medicines if m.quantity > 0]
            
            return available_medicines
            
        except Exception as e:
            self.logger.error(f"Error searching products: {str(e)}")
            return []
    
    def search_products_by_barcode(self, barcode: str) -> Optional[Medicine]:
        """
        Search product by barcode
        
        Args:
            barcode: Product barcode
            
        Returns:
            Medicine instance if found and in stock, None otherwise
        """
        try:
            medicine = self.medicine_repository.find_by_barcode(barcode)
            if medicine and medicine.quantity > 0:
                return medicine
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching product by barcode: {str(e)}")
            return None
    
    # Sales Data Methods
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """
        Get sale by ID
        
        Args:
            sale_id: Sale ID
            
        Returns:
            Sale instance if found, None otherwise
        """
        try:
            return self.sales_repository.find_by_id(sale_id)
        except Exception as e:
            self.logger.error(f"Error getting sale by ID {sale_id}: {str(e)}")
            return None
    
    def get_recent_sales(self, limit: int = 10) -> List[Sale]:
        """
        Get recent sales
        
        Args:
            limit: Maximum number of sales to return
            
        Returns:
            List of recent sales
        """
        try:
            return self.sales_repository.get_recent_sales(limit)
        except Exception as e:
            self.logger.error(f"Error getting recent sales: {str(e)}")
            return []
    
    def get_daily_sales(self, target_date: Optional[str] = None) -> List[Sale]:
        """
        Get sales for a specific date
        
        Args:
            target_date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            List of sales for the date
        """
        try:
            return self.sales_repository.get_daily_sales(target_date)
        except Exception as e:
            self.logger.error(f"Error getting daily sales: {str(e)}")
            return []
    
    def get_sales_by_date_range(self, start_date: str, end_date: str) -> List[Sale]:
        """
        Get sales within date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of sales within date range
        """
        try:
            return self.sales_repository.find_by_date_range(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting sales by date range: {str(e)}")
            return []
    
    def get_last_7_days_sales_data(self) -> Dict[str, float]:
        """
        Get sales data for the last 7 days for chart display
        
        Returns:
            Dictionary with date as key and total sales as value
        """
        try:
            from datetime import date, timedelta
            
            # Calculate date range for last 7 days
            end_date = date.today()
            start_date = end_date - timedelta(days=6)  # 6 days ago + today = 7 days
            
            # Get sales data
            sales = self.get_sales_by_date_range(start_date.isoformat(), end_date.isoformat())
            
            # Initialize data for all 7 days with 0
            sales_data = {}
            current_date = start_date
            while current_date <= end_date:
                sales_data[current_date.isoformat()] = 0.0
                current_date += timedelta(days=1)
            
            # Aggregate sales by date
            for sale in sales:
                if sale.date in sales_data:
                    sales_data[sale.date] += sale.total
            
            return sales_data
            
        except Exception as e:
            self.logger.error(f"Error getting last 7 days sales data: {str(e)}")
            # Return empty data for 7 days
            from datetime import date, timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=6)
            sales_data = {}
            current_date = start_date
            while current_date <= end_date:
                sales_data[current_date.isoformat()] = 0.0
                current_date += timedelta(days=1)
            return sales_data
    
    def get_sales_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get sales analytics for date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing sales analytics
        """
        try:
            return self.sales_repository.get_sales_analytics(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting sales analytics: {str(e)}")
            return {}
    
    def get_total_revenue(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> float:
        """
        Get total revenue for date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            
        Returns:
            Total revenue
        """
        try:
            return self.sales_repository.get_total_revenue(start_date, end_date)
        except Exception as e:
            self.logger.error(f"Error getting total revenue: {str(e)}")
            return 0.0
    
    def get_top_selling_medicines(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top selling medicines for date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of medicines to return
            
        Returns:
            List of top selling medicines
        """
        try:
            return self.sales_repository.get_top_selling_medicines(start_date, end_date, limit)
        except Exception as e:
            self.logger.error(f"Error getting top selling medicines: {str(e)}")
            return []
    
    # Utility Methods
    
    def get_current_cart_summary(self) -> Dict[str, Any]:
        """
        Get summary of current cart
        
        Returns:
            Dictionary with cart summary
        """
        try:
            totals = self.calculate_cart_totals()
            return {
                'item_count': len(self._current_cart),
                'total_quantity': sum(item.quantity for item in self._current_cart),
                'subtotal': totals['subtotal'],
                'discount': totals['discount'],
                'tax': totals['tax'],
                'total': totals['total'],
                'payment_method': self._current_payment_method,
                'items': [
                    {
                        'medicine_id': item.medicine_id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price
                    }
                    for item in self._current_cart
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting cart summary: {str(e)}")
            return {
                'item_count': 0,
                'total_quantity': 0,
                'subtotal': 0.0,
                'discount': 0.0,
                'tax': 0.0,
                'total': 0.0,
                'payment_method': 'cash',
                'items': []
            }
    
    def get_current_discount(self) -> float:
        """Get current discount amount"""
        return self._current_discount
    
    def get_current_tax_rate(self) -> float:
        """Get current tax rate"""
        return self._current_tax_rate
    
    def get_current_payment_method(self) -> str:
        """Get current payment method"""
        return self._current_payment_method
    
    # Settings Integration Methods
    
    def refresh_settings(self):
        """Refresh settings from database"""
        if self.settings_manager:
            self.settings_manager.refresh_settings()
            # Update tax rate to default from settings if current cart is empty
            if self.is_cart_empty():
                self._current_tax_rate = self.settings_manager.get_default_tax_rate()
                self.logger.info(f"Tax rate updated from settings: {self._current_tax_rate}%")
    
    def format_currency(self, amount: float, show_symbol: bool = True) -> str:
        """
        Format currency amount using current settings
        
        Args:
            amount: Amount to format
            show_symbol: Whether to show currency symbol
            
        Returns:
            Formatted currency string
        """
        if self.settings_manager:
            return self.settings_manager.format_currency(amount, show_symbol)
        else:
            # Fallback to USD formatting
            return f"${amount:.2f}" if show_symbol else f"{amount:.2f}"
    
    def get_currency_symbol(self) -> str:
        """
        Get current currency symbol
        
        Returns:
            Current currency symbol
        """
        if self.settings_manager:
            return self.settings_manager.get_currency_symbol()
        else:
            return "$"
    
    def get_store_info(self) -> Dict[str, str]:
        """
        Get store information from settings
        
        Returns:
            Dictionary of store information
        """
        if self.settings_manager:
            return self.settings_manager.get_store_info()
        else:
            return {
                'name': 'Medical Store',
                'address': '',
                'phone': '',
                'email': '',
                'website': ''
            }
    
    def apply_settings_to_cart(self):
        """Apply current settings to cart (tax rate, etc.)"""
        if self.settings_manager and self.is_cart_empty():
            # Only apply default tax rate if cart is empty (new transaction)
            default_tax_rate = self.settings_manager.get_default_tax_rate()
            if default_tax_rate != self._current_tax_rate:
                self._current_tax_rate = default_tax_rate
                self.logger.info(f"Applied default tax rate from settings: {default_tax_rate}%")
