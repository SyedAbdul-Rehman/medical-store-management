"""
Sales repository for Medical Store Management Application
Handles all database operations for sales data
"""

import sqlite3
import logging
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta

from ..config.database import DatabaseManager
from ..models.sale import Sale, SaleItem


class SalesRepository:
    """Repository class for sales data access operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize sales repository
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def save(self, sale: Sale) -> Optional[Sale]:
        """
        Save a new sale to the database
        
        Args:
            sale: Sale instance to save
            
        Returns:
            Sale instance with assigned ID if successful, None otherwise
        """
        try:
            # Validate sale data
            validation_errors = sale.validate()
            if validation_errors:
                self.logger.error(f"Sale validation failed: {validation_errors}")
                return None
            
            # Calculate totals before saving
            sale.calculate_totals()
            
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sales (
                        date, items, subtotal, discount, tax, total,
                        payment_method, cashier_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sale.date,
                    sale.get_items_json(),
                    sale.subtotal,
                    sale.discount,
                    sale.tax,
                    sale.total,
                    sale.payment_method,
                    sale.cashier_id,
                    sale.created_at
                ))
                
                sale.id = cursor.lastrowid
                self.logger.info(f"Sale saved successfully: ID {sale.id}, Total: ${sale.total}")
                return sale
                
        except Exception as e:
            self.logger.error(f"Failed to save sale: {e}")
            return None
    
    def find_by_id(self, sale_id: int) -> Optional[Sale]:
        """
        Find sale by ID
        
        Args:
            sale_id: Sale ID to search for
            
        Returns:
            Sale instance if found, None otherwise
        """
        try:
            row = self.db_manager.execute_single(
                "SELECT * FROM sales WHERE id = ?",
                (sale_id,)
            )
            
            if row:
                return self._row_to_sale(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find sale by ID {sale_id}: {e}")
            return None
    
    def find_all(self, limit: Optional[int] = None) -> List[Sale]:
        """
        Get all sales from database
        
        Args:
            limit: Maximum number of sales to return (optional)
            
        Returns:
            List of sale instances
        """
        try:
            query = "SELECT * FROM sales ORDER BY date DESC, created_at DESC"
            params = ()
            
            if limit:
                query += " LIMIT ?"
                params = (limit,)
            
            rows = self.db_manager.execute_query(query, params)
            return [self._row_to_sale(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve all sales: {e}")
            return []
    
    def find_by_date_range(self, start_date: str, end_date: str) -> List[Sale]:
        """
        Find sales within date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of sales within the date range
        """
        try:
            rows = self.db_manager.execute_query("""
                SELECT * FROM sales 
                WHERE date >= ? AND date <= ? 
                ORDER BY date DESC, created_at DESC
            """, (start_date, end_date))
            
            return [self._row_to_sale(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to find sales by date range {start_date} to {end_date}: {e}")
            return []
    
    def find_by_cashier(self, cashier_id: int) -> List[Sale]:
        """
        Find sales by cashier ID
        
        Args:
            cashier_id: Cashier ID to search for
            
        Returns:
            List of sales by the specified cashier
        """
        try:
            rows = self.db_manager.execute_query("""
                SELECT * FROM sales 
                WHERE cashier_id = ? 
                ORDER BY date DESC, created_at DESC
            """, (cashier_id,))
            
            return [self._row_to_sale(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to find sales by cashier {cashier_id}: {e}")
            return []
    
    def get_daily_sales(self, target_date: Optional[str] = None) -> List[Sale]:
        """
        Get sales for a specific date
        
        Args:
            target_date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            List of sales for the specified date
        """
        try:
            if not target_date:
                target_date = date.today().isoformat()
            
            rows = self.db_manager.execute_query("""
                SELECT * FROM sales 
                WHERE date = ? 
                ORDER BY created_at DESC
            """, (target_date,))
            
            return [self._row_to_sale(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get daily sales for {target_date}: {e}")
            return []
    
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
            # Get basic sales statistics
            stats_row = self.db_manager.execute_single("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(total) as total_revenue,
                    AVG(total) as average_transaction,
                    MIN(total) as min_transaction,
                    MAX(total) as max_transaction,
                    SUM(discount) as total_discounts,
                    SUM(tax) as total_tax
                FROM sales 
                WHERE date >= ? AND date <= ?
            """, (start_date, end_date))
            
            # Get daily sales breakdown
            daily_rows = self.db_manager.execute_query("""
                SELECT 
                    date,
                    COUNT(*) as transactions,
                    SUM(total) as revenue
                FROM sales 
                WHERE date >= ? AND date <= ?
                GROUP BY date
                ORDER BY date
            """, (start_date, end_date))
            
            # Get payment method breakdown
            payment_rows = self.db_manager.execute_query("""
                SELECT 
                    payment_method,
                    COUNT(*) as transactions,
                    SUM(total) as revenue
                FROM sales 
                WHERE date >= ? AND date <= ?
                GROUP BY payment_method
                ORDER BY revenue DESC
            """, (start_date, end_date))
            
            analytics = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'summary': {
                    'total_transactions': stats_row['total_transactions'] if stats_row else 0,
                    'total_revenue': float(stats_row['total_revenue']) if stats_row and stats_row['total_revenue'] else 0.0,
                    'average_transaction': float(stats_row['average_transaction']) if stats_row and stats_row['average_transaction'] else 0.0,
                    'min_transaction': float(stats_row['min_transaction']) if stats_row and stats_row['min_transaction'] else 0.0,
                    'max_transaction': float(stats_row['max_transaction']) if stats_row and stats_row['max_transaction'] else 0.0,
                    'total_discounts': float(stats_row['total_discounts']) if stats_row and stats_row['total_discounts'] else 0.0,
                    'total_tax': float(stats_row['total_tax']) if stats_row and stats_row['total_tax'] else 0.0
                },
                'daily_breakdown': [
                    {
                        'date': row['date'],
                        'transactions': row['transactions'],
                        'revenue': float(row['revenue'])
                    }
                    for row in daily_rows
                ],
                'payment_methods': [
                    {
                        'method': row['payment_method'],
                        'transactions': row['transactions'],
                        'revenue': float(row['revenue'])
                    }
                    for row in payment_rows
                ]
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get sales analytics: {e}")
            return {
                'period': {'start_date': start_date, 'end_date': end_date},
                'summary': {},
                'daily_breakdown': [],
                'payment_methods': []
            }
    
    def get_top_selling_medicines(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top selling medicines for date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of medicines to return
            
        Returns:
            List of top selling medicines with quantities and revenue
        """
        try:
            # Get all sales in the date range
            sales = self.find_by_date_range(start_date, end_date)
            
            # Aggregate medicine sales
            medicine_stats = {}
            for sale in sales:
                for item in sale.items:
                    medicine_id = item.medicine_id
                    if medicine_id not in medicine_stats:
                        medicine_stats[medicine_id] = {
                            'medicine_id': medicine_id,
                            'name': item.name,
                            'total_quantity': 0,
                            'total_revenue': 0.0,
                            'transactions': 0
                        }
                    
                    medicine_stats[medicine_id]['total_quantity'] += item.quantity
                    medicine_stats[medicine_id]['total_revenue'] += item.total_price
                    medicine_stats[medicine_id]['transactions'] += 1
            
            # Sort by total revenue and return top medicines
            top_medicines = sorted(
                medicine_stats.values(),
                key=lambda x: x['total_revenue'],
                reverse=True
            )[:limit]
            
            return top_medicines
            
        except Exception as e:
            self.logger.error(f"Failed to get top selling medicines: {e}")
            return []
    
    def update_medicine_stock_after_sale(self, sale: Sale) -> bool:
        """
        Update medicine stock quantities after a sale
        
        Args:
            sale: Sale instance containing items sold
            
        Returns:
            True if all stock updates successful, False otherwise
        """
        try:
            with self.db_manager.get_cursor() as cursor:
                for item in sale.items:
                    # Reduce medicine quantity
                    cursor.execute("""
                        UPDATE medicines 
                        SET quantity = quantity - ?, updated_at = ?
                        WHERE id = ? AND quantity >= ?
                    """, (
                        item.quantity,
                        datetime.now().isoformat(),
                        item.medicine_id,
                        item.quantity
                    ))
                    
                    if cursor.rowcount == 0:
                        # Stock update failed - insufficient quantity
                        self.logger.error(f"Insufficient stock for medicine ID {item.medicine_id}")
                        return False
                
                self.logger.info(f"Stock updated for sale ID {sale.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update medicine stock after sale: {e}")
            return False
    
    def get_total_sales_count(self) -> int:
        """
        Get total count of sales
        
        Returns:
            Total number of sale records
        """
        try:
            row = self.db_manager.execute_single("SELECT COUNT(*) as count FROM sales")
            return row['count'] if row else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get total sales count: {e}")
            return 0
    
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
            if start_date and end_date:
                row = self.db_manager.execute_single("""
                    SELECT SUM(total) as total_revenue 
                    FROM sales 
                    WHERE date >= ? AND date <= ?
                """, (start_date, end_date))
            else:
                row = self.db_manager.execute_single(
                    "SELECT SUM(total) as total_revenue FROM sales"
                )
            
            return float(row['total_revenue']) if row and row['total_revenue'] else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to get total revenue: {e}")
            return 0.0
    
    def get_recent_sales(self, limit: int = 10) -> List[Sale]:
        """
        Get most recent sales
        
        Args:
            limit: Maximum number of sales to return
            
        Returns:
            List of recent sales
        """
        try:
            rows = self.db_manager.execute_query("""
                SELECT * FROM sales 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [self._row_to_sale(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent sales: {e}")
            return []
    
    def delete(self, sale_id: int) -> bool:
        """
        Delete sale from database
        
        Args:
            sale_id: ID of sale to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            rows_affected = self.db_manager.execute_update(
                "DELETE FROM sales WHERE id = ?",
                (sale_id,)
            )
            
            if rows_affected > 0:
                self.logger.info(f"Sale deleted successfully (ID: {sale_id})")
                return True
            else:
                self.logger.warning(f"No sale found with ID {sale_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete sale with ID {sale_id}: {e}")
            return False
    
    def _row_to_sale(self, row: sqlite3.Row) -> Sale:
        """
        Convert database row to Sale instance
        
        Args:
            row: Database row
            
        Returns:
            Sale instance
        """
        # Parse items JSON
        items = []
        if row['items']:
            try:
                items_data = json.loads(row['items'])
                items = [SaleItem.from_dict(item_data) for item_data in items_data]
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"Failed to parse sale items JSON: {e}")
        
        return Sale(
            id=row['id'],
            date=row['date'],
            items=items,
            subtotal=row['subtotal'],
            discount=row['discount'],
            tax=row['tax'],
            total=row['total'],
            payment_method=row['payment_method'],
            cashier_id=row['cashier_id'],
            created_at=row['created_at']
        )