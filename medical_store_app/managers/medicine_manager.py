"""
Medicine Manager for Medical Store Management Application
Coordinates between UI and repository for medicine operations
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, timedelta

from ..models.medicine import Medicine
from ..repositories.medicine_repository import MedicineRepository
from ..repositories.settings_repository import SettingsRepository


class MedicineManager:
    """Manager class for medicine inventory operations"""
    
    def __init__(self, medicine_repository: MedicineRepository, settings_repository: Optional[SettingsRepository] = None):
        """
        Initialize medicine manager
        
        Args:
            medicine_repository: Medicine repository instance
            settings_repository: Settings repository instance (optional)
        """
        self.medicine_repository = medicine_repository
        self.settings_repository = settings_repository
        self.logger = logging.getLogger(__name__)
        self._low_stock_threshold = 10
        self._expiry_warning_days = 30
        
        # Load settings if available
        if self.settings_repository:
            self._load_settings()
    
    def _load_settings(self):
        """Load settings from repository"""
        try:
            if self.settings_repository:
                self._low_stock_threshold = self.settings_repository.get_int('low_stock_threshold', 10)
                self.logger.info(f"Loaded low stock threshold from settings: {self._low_stock_threshold}")
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self._low_stock_threshold = 10
    
    def refresh_settings(self):
        """Refresh settings from database"""
        self._load_settings()
    
    def get_low_stock_threshold(self) -> int:
        """Get current low stock threshold"""
        return self._low_stock_threshold
    
    def add_medicine(self, medicine_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Medicine]]:
        """
        Add a new medicine to inventory
        
        Args:
            medicine_data: Dictionary containing medicine information
            
        Returns:
            Tuple of (success, message, medicine_instance)
        """
        try:
            # Create medicine instance from data
            medicine = Medicine(
                name=medicine_data.get('name', ''),
                category=medicine_data.get('category', ''),
                batch_no=medicine_data.get('batch_no', ''),
                expiry_date=medicine_data.get('expiry_date', ''),
                quantity=medicine_data.get('quantity', 0),
                purchase_price=medicine_data.get('purchase_price', 0.0),
                selling_price=medicine_data.get('selling_price', 0.0),
                barcode=medicine_data.get('barcode')
            )
            
            # Validate medicine data
            validation_errors = medicine.validate()
            if validation_errors:
                error_msg = "; ".join(validation_errors)
                self.logger.warning(f"Medicine validation failed: {error_msg}")
                return False, f"Validation failed: {error_msg}", None
            
            # Check for duplicate barcode if provided
            if medicine.barcode:
                existing = self.medicine_repository.find_by_barcode(medicine.barcode)
                if existing:
                    error_msg = f"Medicine with barcode '{medicine.barcode}' already exists"
                    self.logger.warning(error_msg)
                    return False, error_msg, None
            
            # Save medicine
            saved_medicine = self.medicine_repository.save(medicine)
            if saved_medicine:
                success_msg = f"Medicine '{saved_medicine.name}' added successfully"
                self.logger.info(success_msg)
                return True, success_msg, saved_medicine
            else:
                error_msg = "Failed to save medicine to database"
                self.logger.error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error adding medicine: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def edit_medicine(self, medicine_id: int, medicine_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Medicine]]:
        """
        Edit existing medicine
        
        Args:
            medicine_id: ID of medicine to edit
            medicine_data: Dictionary containing updated medicine information
            
        Returns:
            Tuple of (success, message, medicine_instance)
        """
        try:
            # Find existing medicine
            existing_medicine = self.medicine_repository.find_by_id(medicine_id)
            if not existing_medicine:
                error_msg = f"Medicine with ID {medicine_id} not found"
                self.logger.warning(error_msg)
                return False, error_msg, None
            
            # Update medicine data
            existing_medicine.name = medicine_data.get('name', existing_medicine.name)
            existing_medicine.category = medicine_data.get('category', existing_medicine.category)
            existing_medicine.batch_no = medicine_data.get('batch_no', existing_medicine.batch_no)
            existing_medicine.expiry_date = medicine_data.get('expiry_date', existing_medicine.expiry_date)
            existing_medicine.quantity = medicine_data.get('quantity', existing_medicine.quantity)
            existing_medicine.purchase_price = medicine_data.get('purchase_price', existing_medicine.purchase_price)
            existing_medicine.selling_price = medicine_data.get('selling_price', existing_medicine.selling_price)
            existing_medicine.barcode = medicine_data.get('barcode', existing_medicine.barcode)
            
            # Validate updated medicine data
            validation_errors = existing_medicine.validate()
            if validation_errors:
                error_msg = "; ".join(validation_errors)
                self.logger.warning(f"Medicine validation failed: {error_msg}")
                return False, f"Validation failed: {error_msg}", None
            
            # Check for duplicate barcode if changed
            if existing_medicine.barcode:
                duplicate = self.medicine_repository.find_by_barcode(existing_medicine.barcode)
                if duplicate and duplicate.id != medicine_id:
                    error_msg = f"Medicine with barcode '{existing_medicine.barcode}' already exists"
                    self.logger.warning(error_msg)
                    return False, error_msg, None
            
            # Update medicine
            if self.medicine_repository.update(existing_medicine):
                success_msg = f"Medicine '{existing_medicine.name}' updated successfully"
                self.logger.info(success_msg)
                return True, success_msg, existing_medicine
            else:
                error_msg = "Failed to update medicine in database"
                self.logger.error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error editing medicine: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def delete_medicine(self, medicine_id: int) -> Tuple[bool, str]:
        """
        Delete medicine from inventory
        
        Args:
            medicine_id: ID of medicine to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Find medicine to get name for logging
            medicine = self.medicine_repository.find_by_id(medicine_id)
            if not medicine:
                error_msg = f"Medicine with ID {medicine_id} not found"
                self.logger.warning(error_msg)
                return False, error_msg
            
            # Delete medicine
            if self.medicine_repository.delete(medicine_id):
                success_msg = f"Medicine '{medicine.name}' deleted successfully"
                self.logger.info(success_msg)
                return True, success_msg
            else:
                error_msg = "Failed to delete medicine from database"
                self.logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error deleting medicine: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_medicine_by_id(self, medicine_id: int) -> Optional[Medicine]:
        """
        Get medicine by ID
        
        Args:
            medicine_id: Medicine ID
            
        Returns:
            Medicine instance if found, None otherwise
        """
        try:
            return self.medicine_repository.find_by_id(medicine_id)
        except Exception as e:
            self.logger.error(f"Error getting medicine by ID {medicine_id}: {str(e)}")
            return None
    
    def get_medicine_by_barcode(self, barcode: str) -> Optional[Medicine]:
        """
        Get medicine by barcode
        
        Args:
            barcode: Medicine barcode
            
        Returns:
            Medicine instance if found, None otherwise
        """
        try:
            return self.medicine_repository.find_by_barcode(barcode)
        except Exception as e:
            self.logger.error(f"Error getting medicine by barcode {barcode}: {str(e)}")
            return None
    
    def get_all_medicines(self) -> List[Medicine]:
        """
        Get all medicines
        
        Returns:
            List of all medicine instances
        """
        try:
            return self.medicine_repository.find_all()
        except Exception as e:
            self.logger.error(f"Error getting all medicines: {str(e)}")
            return []
    
    def search_medicines(self, query: str) -> List[Medicine]:
        """
        Search medicines by name or barcode
        
        Args:
            query: Search query
            
        Returns:
            List of matching medicine instances
        """
        try:
            if not query or not query.strip():
                return []
            
            return self.medicine_repository.search(query.strip())
        except Exception as e:
            self.logger.error(f"Error searching medicines with query '{query}': {str(e)}")
            return []
    
    def search_medicines_by_name(self, name: str) -> List[Medicine]:
        """
        Search medicines by name
        
        Args:
            name: Medicine name to search
            
        Returns:
            List of matching medicine instances
        """
        try:
            if not name or not name.strip():
                return []
            
            return self.medicine_repository.search_by_name(name.strip())
        except Exception as e:
            self.logger.error(f"Error searching medicines by name '{name}': {str(e)}")
            return []
    
    def get_medicines_by_category(self, category: str) -> List[Medicine]:
        """
        Get medicines by category
        
        Args:
            category: Category name
            
        Returns:
            List of medicines in the category
        """
        try:
            return self.medicine_repository.get_medicines_by_category(category)
        except Exception as e:
            self.logger.error(f"Error getting medicines by category '{category}': {str(e)}")
            return []
    
    def get_all_categories(self) -> List[str]:
        """
        Get all medicine categories
        
        Returns:
            List of unique category names
        """
        try:
            return self.medicine_repository.get_all_categories()
        except Exception as e:
            self.logger.error(f"Error getting medicine categories: {str(e)}")
            return []
    
    def update_stock(self, medicine_id: int, quantity_change: int) -> Tuple[bool, str]:
        """
        Update medicine stock quantity
        
        Args:
            medicine_id: Medicine ID
            quantity_change: Change in quantity (positive for addition, negative for reduction)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if self.medicine_repository.update_stock(medicine_id, quantity_change):
                success_msg = f"Stock updated successfully for medicine ID {medicine_id}"
                self.logger.info(success_msg)
                return True, success_msg
            else:
                error_msg = f"Failed to update stock for medicine ID {medicine_id}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error updating stock: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def check_stock_availability(self, medicine_id: int, requested_quantity: int) -> Tuple[bool, str, int]:
        """
        Check if requested quantity is available in stock
        
        Args:
            medicine_id: Medicine ID
            requested_quantity: Requested quantity
            
        Returns:
            Tuple of (available, message, current_stock)
        """
        try:
            medicine = self.medicine_repository.find_by_id(medicine_id)
            if not medicine:
                return False, f"Medicine with ID {medicine_id} not found", 0
            
            if medicine.can_sell(requested_quantity):
                return True, "Stock available", medicine.quantity
            else:
                return False, f"Insufficient stock. Available: {medicine.quantity}, Requested: {requested_quantity}", medicine.quantity
                
        except Exception as e:
            error_msg = f"Error checking stock availability: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, 0
    
    def get_low_stock_medicines(self, threshold: Optional[int] = None) -> List[Medicine]:
        """
        Get medicines with low stock
        
        Args:
            threshold: Stock threshold (uses default if not provided)
            
        Returns:
            List of low stock medicines
        """
        try:
            threshold = threshold or self._low_stock_threshold
            return self.medicine_repository.get_low_stock_medicines(threshold)
        except Exception as e:
            self.logger.error(f"Error getting low stock medicines: {str(e)}")
            return []
    
    def get_expired_medicines(self) -> List[Medicine]:
        """
        Get expired medicines
        
        Returns:
            List of expired medicines
        """
        try:
            return self.medicine_repository.get_expired_medicines()
        except Exception as e:
            self.logger.error(f"Error getting expired medicines: {str(e)}")
            return []
    
    def get_expiring_soon_medicines(self, days: Optional[int] = None) -> List[Medicine]:
        """
        Get medicines expiring soon
        
        Args:
            days: Number of days to check (uses default if not provided)
            
        Returns:
            List of medicines expiring soon
        """
        try:
            days = days or self._expiry_warning_days
            return self.medicine_repository.get_expiring_soon_medicines(days)
        except Exception as e:
            self.logger.error(f"Error getting medicines expiring soon: {str(e)}")
            return []
    
    def generate_stock_alerts(self) -> Dict[str, List[Medicine]]:
        """
        Generate comprehensive stock alerts
        
        Returns:
            Dictionary with alert types and corresponding medicines
        """
        try:
            alerts = {
                'low_stock': self.get_low_stock_medicines(),
                'expired': self.get_expired_medicines(),
                'expiring_soon': self.get_expiring_soon_medicines()
            }
            
            # Log alert summary
            total_alerts = sum(len(medicines) for medicines in alerts.values())
            if total_alerts > 0:
                self.logger.info(f"Generated {total_alerts} stock alerts: "
                               f"Low Stock: {len(alerts['low_stock'])}, "
                               f"Expired: {len(alerts['expired'])}, "
                               f"Expiring Soon: {len(alerts['expiring_soon'])}")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error generating stock alerts: {str(e)}")
            return {'low_stock': [], 'expired': [], 'expiring_soon': []}
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """
        Get inventory summary statistics
        
        Returns:
            Dictionary with inventory statistics
        """
        try:
            total_medicines = self.medicine_repository.get_total_medicines_count()
            total_value = self.medicine_repository.get_total_stock_value()
            low_stock_count = len(self.get_low_stock_medicines())
            expired_count = len(self.get_expired_medicines())
            expiring_soon_count = len(self.get_expiring_soon_medicines())
            
            summary = {
                'total_medicines': total_medicines,
                'total_stock_value': total_value,
                'low_stock_count': low_stock_count,
                'expired_count': expired_count,
                'expiring_soon_count': expiring_soon_count,
                'categories': self.get_all_categories()
            }
            
            self.logger.info(f"Generated inventory summary: {total_medicines} medicines, "
                           f"${total_value:.2f} total value, {low_stock_count} low stock alerts")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting inventory summary: {str(e)}")
            return {
                'total_medicines': 0,
                'total_stock_value': 0.0,
                'low_stock_count': 0,
                'expired_count': 0,
                'expiring_soon_count': 0,
                'categories': []
            }
    
    def set_low_stock_threshold(self, threshold: int) -> bool:
        """
        Set low stock threshold
        
        Args:
            threshold: New threshold value
            
        Returns:
            True if set successfully
        """
        try:
            if threshold < 0:
                self.logger.warning("Low stock threshold cannot be negative")
                return False
            
            self._low_stock_threshold = threshold
            self.logger.info(f"Low stock threshold set to {threshold}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting low stock threshold: {str(e)}")
            return False
    
    def set_expiry_warning_days(self, days: int) -> bool:
        """
        Set expiry warning days
        
        Args:
            days: Number of days for expiry warning
            
        Returns:
            True if set successfully
        """
        try:
            if days < 0:
                self.logger.warning("Expiry warning days cannot be negative")
                return False
            
            self._expiry_warning_days = days
            self.logger.info(f"Expiry warning days set to {days}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting expiry warning days: {str(e)}")
            return False
    
    def get_low_stock_threshold(self) -> int:
        """Get current low stock threshold"""
        return self._low_stock_threshold
    
    def get_expiry_warning_days(self) -> int:
        """Get current expiry warning days"""
        return self._expiry_warning_days