"""
Sale data models for Medical Store Management Application
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
from .base import BaseModel


@dataclass
class SaleItem:
    """Individual item in a sale transaction"""
    
    medicine_id: int
    name: str
    quantity: int
    unit_price: float
    total_price: float
    batch_no: Optional[str] = None
    
    def __post_init__(self):
        """Validate and calculate total price"""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        
        # Ensure total price is correctly calculated
        self.total_price = round(self.quantity * self.unit_price, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'medicine_id': self.medicine_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'batch_no': self.batch_no
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaleItem':
        """Create SaleItem from dictionary"""
        return cls(
            medicine_id=data['medicine_id'],
            name=data['name'],
            quantity=data['quantity'],
            unit_price=data['unit_price'],
            total_price=data['total_price'],
            batch_no=data.get('batch_no')
        )

@dataclass
class Sale(BaseModel):
    """Sale transaction model"""
    
    date: str = ""  # ISO format date string (YYYY-MM-DD)
    items: List[SaleItem] = field(default_factory=list)
    subtotal: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    payment_method: str = "cash"
    cashier_id: Optional[int] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Initialize sale with current date if not provided"""
        super().__post_init__()
        if not self.date:
            self.date = date.today().isoformat()
    
    def validate(self) -> List[str]:
        """
        Validate sale data
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Date validation
        if not self.date:
            errors.append("Sale date is required")
        else:
            try:
                datetime.strptime(self.date, "%Y-%m-%d")
            except ValueError:
                errors.append("Sale date must be in YYYY-MM-DD format")
        
        # Items validation
        if not self.items:
            errors.append("Sale must contain at least one item")
        
        # Financial validation
        if self.subtotal < 0:
            errors.append("Subtotal cannot be negative")
        if self.discount < 0:
            errors.append("Discount cannot be negative")
        if self.tax < 0:
            errors.append("Tax cannot be negative")
        if self.total < 0:
            errors.append("Total cannot be negative")
        
        # Payment method validation
        valid_payment_methods = ["cash", "card", "upi", "cheque", "bank_transfer"]
        if self.payment_method not in valid_payment_methods:
            errors.append(f"Payment method must be one of: {', '.join(valid_payment_methods)}")
        
        return errors 
   
    def add_item(self, medicine_id: int, name: str, quantity: int, unit_price: float, batch_no: Optional[str] = None) -> bool:
        """
        Add item to sale
        
        Args:
            medicine_id: ID of the medicine
            name: Name of the medicine
            quantity: Quantity to sell
            unit_price: Price per unit
            batch_no: Batch number (optional)
            
        Returns:
            True if item added successfully, False otherwise
        """
        try:
            total_price = round(quantity * unit_price, 2)
            item = SaleItem(
                medicine_id=medicine_id,
                name=name,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                batch_no=batch_no
            )
            self.items.append(item)
            self.calculate_totals()
            return True
        except ValueError:
            return False
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total amounts"""
        self.subtotal = round(sum(item.total_price for item in self.items), 2)
        
        # Apply discount
        discounted_amount = self.subtotal - self.discount
        if discounted_amount < 0:
            discounted_amount = 0
        
        # Calculate total with tax
        self.total = round(discounted_amount + self.tax, 2)
        self.update_timestamp()
    
    def get_items_json(self) -> str:
        """
        Get items as JSON string for database storage
        
        Returns:
            JSON string representation of items
        """
        items_data = [item.to_dict() for item in self.items]
        return json.dumps(items_data)
    
    def __str__(self) -> str:
        """String representation of sale"""
        return f"Sale {self.id} - {self.date} - ${self.total} ({len(self.items)} items)"