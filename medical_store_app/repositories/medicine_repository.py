"""
Medicine repository for Medical Store Management Application
Handles all database operations for medicine data
"""

import sqlite3
import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from ..config.database import DatabaseManager
from ..models.medicine import Medicine


class MedicineRepository:
    """Repository class for medicine data access operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize medicine repository
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def save(self, medicine: Medicine) -> Optional[Medicine]:
        """
        Save a new medicine to the database
        
        Args:
            medicine: Medicine instance to save
            
        Returns:
            Medicine instance with assigned ID if successful, None otherwise
        """
        try:
            # Validate medicine data
            validation_errors = medicine.validate()
            if validation_errors:
                self.logger.error(f"Medicine validation failed: {validation_errors}")
                return None
            
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO medicines (
                        name, category, batch_no, expiry_date, quantity,
                        purchase_price, selling_price, barcode, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    medicine.name.strip(),
                    medicine.category.strip(),
                    medicine.batch_no.strip(),
                    medicine.expiry_date,
                    medicine.quantity,
                    medicine.purchase_price,
                    medicine.selling_price,
                    medicine.barcode.strip() if medicine.barcode else None,
                    medicine.created_at,
                    medicine.updated_at
                ))
                
                medicine.id = cursor.lastrowid
                self.logger.info(f"Medicine saved successfully: {medicine.name} (ID: {medicine.id})")
                return medicine
                
        except sqlite3.IntegrityError as e:
            if "barcode" in str(e).lower():
                self.logger.error(f"Barcode already exists: {medicine.barcode}")
            else:
                self.logger.error(f"Database integrity error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to save medicine: {e}")
            return None
    
    def find_by_id(self, medicine_id: int) -> Optional[Medicine]:
        """
        Find medicine by ID
        
        Args:
            medicine_id: Medicine ID to search for
            
        Returns:
            Medicine instance if found, None otherwise
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT * FROM medicines WHERE id = ?",
                (medicine_id,)
            )
            
            if row:
                return self._row_to_medicine(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find medicine by ID {medicine_id}: {e}")
            return None
    
    def find_by_barcode(self, barcode: str) -> Optional[Medicine]:
        """
        Find medicine by barcode
        
        Args:
            barcode: Barcode to search for
            
        Returns:
            Medicine instance if found, None otherwise
        """
        try:
            if not barcode or not barcode.strip():
                return None
                
            row = self.db_manager.execute_single(
                "SELECT * FROM medicines WHERE barcode = ?",
                (barcode.strip(),)
            )
            
            if row:
                return self._row_to_medicine(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find medicine by barcode {barcode}: {e}")
            return None
    
    def find_all(self) -> List[Medicine]:
        """
        Get all medicines from database
        
        Returns:
            List of all medicine instances
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT * FROM medicines ORDER BY name ASC"
            )
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve all medicines: {e}")
            return []
    
    def search_by_name(self, name: str) -> List[Medicine]:
        """
        Search medicines by name (case-insensitive partial match)
        
        Args:
            name: Name to search for
            
        Returns:
            List of matching medicine instances
        """
        try:
            if not name or not name.strip():
                return []
            
            search_term = f"%{name.strip()}%"
            rows = self.db_manager.execute_query(
                "SELECT * FROM medicines WHERE name LIKE ? ORDER BY name ASC",
                (search_term,)
            )
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to search medicines by name '{name}': {e}")
            return []
    
    def search(self, query: str) -> List[Medicine]:
        """
        Search medicines by name or barcode
        
        Args:
            query: Search query (name or barcode)
            
        Returns:
            List of matching medicine instances
        """
        try:
            if not query or not query.strip():
                return []
            
            search_term = f"%{query.strip()}%"
            rows = self.db_manager.execute_query("""
                SELECT * FROM medicines 
                WHERE name LIKE ? OR barcode LIKE ? 
                ORDER BY name ASC
            """, (search_term, search_term))
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to search medicines with query '{query}': {e}")
            return []
    
    def update(self, medicine: Medicine) -> bool:
        """
        Update existing medicine in database
        
        Args:
            medicine: Medicine instance with updated data
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if not medicine.id:
                self.logger.error("Cannot update medicine without ID")
                return False
            
            # Validate medicine data
            validation_errors = medicine.validate()
            if validation_errors:
                self.logger.error(f"Medicine validation failed: {validation_errors}")
                return False
            
            # Update timestamp
            medicine.update_timestamp()
            
            rows_affected = self.db_manager.execute_update("""
                UPDATE medicines SET
                    name = ?, category = ?, batch_no = ?, expiry_date = ?,
                    quantity = ?, purchase_price = ?, selling_price = ?,
                    barcode = ?, updated_at = ?
                WHERE id = ?
            """, (
                medicine.name.strip(),
                medicine.category.strip(),
                medicine.batch_no.strip(),
                medicine.expiry_date,
                medicine.quantity,
                medicine.purchase_price,
                medicine.selling_price,
                medicine.barcode.strip() if medicine.barcode else None,
                medicine.updated_at,
                medicine.id
            ))
            
            if rows_affected > 0:
                self.logger.info(f"Medicine updated successfully: {medicine.name} (ID: {medicine.id})")
                return True
            else:
                self.logger.warning(f"No medicine found with ID {medicine.id}")
                return False
                
        except sqlite3.IntegrityError as e:
            if "barcode" in str(e).lower():
                self.logger.error(f"Barcode already exists: {medicine.barcode}")
            else:
                self.logger.error(f"Database integrity error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to update medicine: {e}")
            return False
    
    def delete(self, medicine_id: int) -> bool:
        """
        Delete medicine from database
        
        Args:
            medicine_id: ID of medicine to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            rows_affected = self.db_manager.execute_update(
                "DELETE FROM medicines WHERE id = ?",
                (medicine_id,)
            )
            
            if rows_affected > 0:
                self.logger.info(f"Medicine deleted successfully (ID: {medicine_id})")
                return True
            else:
                self.logger.warning(f"No medicine found with ID {medicine_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete medicine with ID {medicine_id}: {e}")
            return False
    
    def get_low_stock_medicines(self, threshold: int = 10) -> List[Medicine]:
        """
        Get medicines with low stock
        
        Args:
            threshold: Stock threshold below which medicine is considered low stock
            
        Returns:
            List of low stock medicine instances
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT * FROM medicines WHERE quantity <= ? ORDER BY quantity ASC, name ASC",
                (threshold,)
            )
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get low stock medicines: {e}")
            return []
    
    def get_expired_medicines(self) -> List[Medicine]:
        """
        Get expired medicines
        
        Returns:
            List of expired medicine instances
        """
        try:
            today = date.today().isoformat()
            rows = self.db_manager.execute_query(
                "SELECT * FROM medicines WHERE expiry_date <= ? ORDER BY expiry_date ASC, name ASC",
                (today,)
            )
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get expired medicines: {e}")
            return []
    
    def get_expiring_soon_medicines(self, days: int = 30) -> List[Medicine]:
        """
        Get medicines expiring within specified days
        
        Args:
            days: Number of days to check for upcoming expiry
            
        Returns:
            List of medicines expiring soon
        """
        try:
            today = date.today()
            future_date = (today + timedelta(days=days)).isoformat()
            today_str = today.isoformat()
            
            rows = self.db_manager.execute_query("""
                SELECT * FROM medicines 
                WHERE expiry_date > ? AND expiry_date <= ? 
                ORDER BY expiry_date ASC, name ASC
            """, (today_str, future_date))
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get medicines expiring soon: {e}")
            return []
    
    def get_medicines_by_category(self, category: str) -> List[Medicine]:
        """
        Get medicines by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of medicines in the specified category
        """
        try:
            if not category or not category.strip():
                return []
            
            rows = self.db_manager.execute_query(
                "SELECT * FROM medicines WHERE category = ? ORDER BY name ASC",
                (category.strip(),)
            )
            
            return [self._row_to_medicine(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get medicines by category '{category}': {e}")
            return []
    
    def get_all_categories(self) -> List[str]:
        """
        Get all unique medicine categories
        
        Returns:
            List of unique category names
        """
        try:
            rows = self.db_manager.execute_query(
                "SELECT DISTINCT category FROM medicines ORDER BY category ASC"
            )
            
            return [row['category'] for row in rows if row['category']]
            
        except Exception as e:
            self.logger.error(f"Failed to get medicine categories: {e}")
            return []
    
    def update_stock(self, medicine_id: int, quantity_change: int) -> bool:
        """
        Update medicine stock quantity with transaction and retry logic
        
        Args:
            medicine_id: ID of medicine to update
            quantity_change: Change in quantity (positive for addition, negative for reduction)
            
        Returns:
            True if update successful, False otherwise
        """
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                with self.db_manager.get_cursor() as cursor:
                    # Get current quantity within transaction
                    row = cursor.execute(
                        "SELECT quantity FROM medicines WHERE id = ? FOR UPDATE",
                        (medicine_id,)
                    ).fetchone()
                    
                    current_quantity = row['quantity']
                    new_quantity = current_quantity + quantity_change
                    
                    if new_quantity < 0:
                        self.logger.error(f"Cannot reduce stock below zero. Current: {current_quantity}, Change: {quantity_change}")
                        return False
                    
                    # Update quantity and timestamp
                    updated_at = datetime.now().isoformat()
                    cursor.execute("""
                        UPDATE medicines 
                        SET quantity = ?, updated_at = ? 
                        WHERE id = ?
                    """, (new_quantity, updated_at, medicine_id))
                        
                    # Commit transaction
                    self.db_manager.commit()
                    
                    self.logger.info(f"Stock updated for medicine ID {medicine_id}: {current_quantity} -> {new_quantity}")
                    return True
                        
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and retry_count < max_retries - 1:
                    retry_count += 1
                    wait_time = 0.1 * (2 ** retry_count)
                    self.logger.warning(f"Database locked, retrying in {wait_time}s (attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                raise
            except sqlite3.IntegrityError as e:
                self.logger.error(f"Integrity error updating stock: {e}")
                self.db_manager.rollback()
                return False
            except Exception as e:
                self.logger.error(f"Failed to update stock for medicine ID {medicine_id}: {e}")
                self.db_manager.rollback()
                return False
                
        return False
    
    def get_total_medicines_count(self) -> int:
        """
        Get total count of medicines
        
        Returns:
            Total number of medicine records
        """
        try:
            row = self.db_manager.execute_single("SELECT COUNT(*) as count FROM medicines")
            return row['count'] if row else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get total medicines count: {e}")
            return 0
    
    def get_total_stock_value(self) -> float:
        """
        Get total value of all stock at selling prices
        
        Returns:
            Total stock value
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT SUM(quantity * selling_price) as total_value FROM medicines"
            )
            return float(row['total_value']) if row and row['total_value'] else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to get total stock value: {e}")
            return 0.0
    
    def _row_to_medicine(self, row: sqlite3.Row) -> Medicine:
        """
        Convert database row to Medicine instance
        
        Args:
            row: Database row
            
        Returns:
            Medicine instance
        """
        return Medicine(
            id=row['id'],
            name=row['name'],
            category=row['category'],
            batch_no=row['batch_no'],
            expiry_date=row['expiry_date'],
            quantity=row['quantity'],
            purchase_price=row['purchase_price'],
            selling_price=row['selling_price'],
            barcode=row['barcode'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
