"""
Medicine data model for Medical Store Management Application
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, date
import re
from .base import BaseModel


@dataclass
class Medicine(BaseModel):
    """Medicine model with validation and business logic"""
    
    name: str = ""
    category: str = ""
    batch_no: str = ""
    expiry_date: str = ""  # ISO format date string (YYYY-MM-DD)
    quantity: int = 0
    purchase_price: float = 0.0
    selling_price: float = 0.0
    barcode: Optional[str] = None
    
    def validate(self) -> List[str]:
        """
        Validate medicine data
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Name validation
        if not self.name or not self.name.strip():
            errors.append("Medicine name is required")
        elif len(self.name.strip()) < 2:
            errors.append("Medicine name must be at least 2 characters long")
        elif len(self.name.strip()) > 100:
            errors.append("Medicine name must be less than 100 characters")
        
        # Category validation
        if not self.category or not self.category.strip():
            errors.append("Category is required")
        elif len(self.category.strip()) > 50:
            errors.append("Category must be less than 50 characters")
        
        # Batch number validation
        if not self.batch_no or not self.batch_no.strip():
            errors.append("Batch number is required")
        elif len(self.batch_no.strip()) > 50:
            errors.append("Batch number must be less than 50 characters")
        
        # Expiry date validation
        if not self.expiry_date:
            errors.append("Expiry date is required")
        else:
            try:
                expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
                if expiry <= date.today():
                    errors.append("Expiry date must be in the future")
            except ValueError:
                errors.append("Expiry date must be in YYYY-MM-DD format")
        
        # Quantity validation
        if self.quantity < 0:
            errors.append("Quantity cannot be negative")
        elif self.quantity > 999999:
            errors.append("Quantity cannot exceed 999,999")
        
        # Purchase price validation
        if self.purchase_price < 0:
            errors.append("Purchase price cannot be negative")
        elif self.purchase_price > 999999.99:
            errors.append("Purchase price cannot exceed 999,999.99")
        
        # Selling price validation
        if self.selling_price < 0:
            errors.append("Selling price cannot be negative")
        elif self.selling_price > 999999.99:
            errors.append("Selling price cannot exceed 999,999.99")
        
        # Price relationship validation
        if self.purchase_price > 0 and self.selling_price > 0:
            if self.selling_price < self.purchase_price:
                errors.append("Selling price should not be less than purchase price")
        
        # Barcode validation (if provided)
        if self.barcode:
            # Remove whitespace
            self.barcode = self.barcode.strip()
            if self.barcode:
                # Basic barcode format validation (alphanumeric, 8-20 characters)
                if not re.match(r'^[A-Za-z0-9]{8,20}$', self.barcode):
                    errors.append("Barcode must be 8-20 alphanumeric characters")
            else:
                self.barcode = None
        
        return errors
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        """
        Check if medicine stock is low
        
        Args:
            threshold: Stock threshold below which medicine is considered low stock
            
        Returns:
            True if stock is low, False otherwise
        """
        return self.quantity <= threshold
    
    def is_expired(self) -> bool:
        """
        Check if medicine is expired
        
        Returns:
            True if medicine is expired, False otherwise
        """
        try:
            expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
            return expiry <= date.today()
        except (ValueError, TypeError):
            # If expiry date is invalid, consider it expired for safety
            return True
    
    def is_expiring_soon(self, days: int = 30) -> bool:
        """
        Check if medicine is expiring soon
        
        Args:
            days: Number of days to check for upcoming expiry
            
        Returns:
            True if medicine expires within the specified days, False otherwise
        """
        try:
            expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
            today = date.today()
            days_until_expiry = (expiry - today).days
            return 0 <= days_until_expiry <= days
        except (ValueError, TypeError):
            return False
    
    def get_profit_margin(self) -> float:
        """
        Calculate profit margin percentage
        
        Returns:
            Profit margin as percentage (0-100)
        """
        if self.purchase_price <= 0:
            return 0.0
        
        profit = self.selling_price - self.purchase_price
        margin = (profit / self.purchase_price) * 100
        return round(margin, 2)
    
    def get_profit_amount(self) -> float:
        """
        Calculate profit amount per unit
        
        Returns:
            Profit amount per unit
        """
        return round(self.selling_price - self.purchase_price, 2)
    
    def get_total_value(self) -> float:
        """
        Calculate total inventory value at selling price
        
        Returns:
            Total value of current stock
        """
        return round(self.quantity * self.selling_price, 2)
    
    def get_total_cost(self) -> float:
        """
        Calculate total inventory cost at purchase price
        
        Returns:
            Total cost of current stock
        """
        return round(self.quantity * self.purchase_price, 2)
    
    def update_stock(self, quantity_change: int) -> bool:
        """
        Update medicine stock quantity
        
        Args:
            quantity_change: Change in quantity (positive for addition, negative for reduction)
            
        Returns:
            True if update successful, False if would result in negative stock
        """
        new_quantity = self.quantity + quantity_change
        if new_quantity < 0:
            return False
        
        self.quantity = new_quantity
        self.update_timestamp()
        return True
    
    def can_sell(self, requested_quantity: int) -> bool:
        """
        Check if requested quantity can be sold
        
        Args:
            requested_quantity: Quantity requested for sale
            
        Returns:
            True if sufficient stock available, False otherwise
        """
        return self.quantity >= requested_quantity and requested_quantity > 0
    
    def get_display_name(self) -> str:
        """
        Get formatted display name for UI
        
        Returns:
            Formatted medicine name with category
        """
        return f"{self.name} ({self.category})"
    
    def get_stock_status(self, low_stock_threshold: int = 10) -> str:
        """
        Get stock status description
        
        Args:
            low_stock_threshold: Threshold for low stock warning
            
        Returns:
            Stock status string
        """
        if self.quantity == 0:
            return "Out of Stock"
        elif self.is_low_stock(low_stock_threshold):
            return "Low Stock"
        else:
            return "In Stock"
    
    def __str__(self) -> str:
        """String representation of medicine"""
        return f"{self.name} - {self.category} (Qty: {self.quantity})"