"""
Report Manager for Medical Store Management Application
Handles report generation, data aggregation, and analytics
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field

from ..repositories.sales_repository import SalesRepository
from ..repositories.medicine_repository import MedicineRepository
from ..models.sale import Sale


@dataclass
class ReportData:
    """Data structure for report information"""
    
    title: str
    period_start: str
    period_end: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: Dict[str, Any] = field(default_factory=dict)
    daily_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    top_medicines: List[Dict[str, Any]] = field(default_factory=list)
    payment_methods: List[Dict[str, Any]] = field(default_factory=list)
    trends: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DateRange:
    """Date range for filtering reports"""
    
    start_date: str
    end_date: str
    
    def validate(self) -> List[str]:
        """Validate date range"""
        errors = []
        
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            
            if start > end:
                errors.append("Start date must be before or equal to end date")
            
            if end > datetime.now():
                errors.append("End date cannot be in the future")
                
        except ValueError:
            errors.append("Dates must be in YYYY-MM-DD format")
        
        return errors
    
    def get_days_count(self) -> int:
        """Get number of days in the range"""
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            return (end - start).days + 1
        except ValueError:
            return 0


class ReportManager:
    """Manager class for report generation and analytics"""
    
    def __init__(self, sales_repository: SalesRepository, medicine_repository: MedicineRepository):
        """
        Initialize report manager
        
        Args:
            sales_repository: Sales repository instance
            medicine_repository: Medicine repository instance
        """
        self.sales_repository = sales_repository
        self.medicine_repository = medicine_repository
        self.logger = logging.getLogger(__name__)
    
    def generate_sales_report(self, date_range: DateRange) -> Optional[ReportData]:
        """
        Generate comprehensive sales report for date range
        
        Args:
            date_range: Date range for the report
            
        Returns:
            ReportData instance with complete report information
        """
        try:
            # Validate date range
            validation_errors = date_range.validate()
            if validation_errors:
                self.logger.error(f"Invalid date range: {validation_errors}")
                return None
            
            self.logger.info(f"Generating sales report for {date_range.start_date} to {date_range.end_date}")
            
            # Get sales analytics
            analytics = self.sales_repository.get_sales_analytics(
                date_range.start_date, 
                date_range.end_date
            )
            
            # Get top selling medicines
            top_medicines = self.sales_repository.get_top_selling_medicines(
                date_range.start_date,
                date_range.end_date,
                limit=10
            )
            
            # Calculate trends
            trends = self._calculate_trends(date_range)
            
            # Create report data
            report = ReportData(
                title=f"Sales Report ({date_range.start_date} to {date_range.end_date})",
                period_start=date_range.start_date,
                period_end=date_range.end_date,
                summary=analytics.get('summary', {}),
                daily_breakdown=analytics.get('daily_breakdown', []),
                top_medicines=top_medicines,
                payment_methods=analytics.get('payment_methods', []),
                trends=trends
            )
            
            self.logger.info(f"Sales report generated successfully with {len(report.daily_breakdown)} daily records")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate sales report: {e}")
            return None
    
    def generate_inventory_report(self) -> Optional[Dict[str, Any]]:
        """
        Generate inventory status report
        
        Returns:
            Dictionary containing inventory report data
        """
        try:
            self.logger.info("Generating inventory report")
            
            # Get all medicines
            medicines = self.medicine_repository.find_all()
            
            # Calculate inventory statistics
            total_medicines = len(medicines)
            total_stock_value = sum(med.quantity * med.purchase_price for med in medicines)
            total_selling_value = sum(med.quantity * med.selling_price for med in medicines)
            
            # Get low stock medicines
            low_stock_medicines = [
                {
                    'id': med.id,
                    'name': med.name,
                    'category': med.category,
                    'quantity': med.quantity,
                    'batch_no': med.batch_no
                }
                for med in medicines if med.is_low_stock()
            ]
            
            # Get expired medicines
            expired_medicines = [
                {
                    'id': med.id,
                    'name': med.name,
                    'category': med.category,
                    'expiry_date': med.expiry_date,
                    'quantity': med.quantity,
                    'batch_no': med.batch_no
                }
                for med in medicines if med.is_expired()
            ]
            
            # Category breakdown
            category_stats = {}
            for med in medicines:
                if med.category not in category_stats:
                    category_stats[med.category] = {
                        'count': 0,
                        'total_quantity': 0,
                        'stock_value': 0.0
                    }
                
                category_stats[med.category]['count'] += 1
                category_stats[med.category]['total_quantity'] += med.quantity
                category_stats[med.category]['stock_value'] += med.quantity * med.purchase_price
            
            report = {
                'title': 'Inventory Status Report',
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_medicines': total_medicines,
                    'total_stock_value': round(total_stock_value, 2),
                    'total_selling_value': round(total_selling_value, 2),
                    'potential_profit': round(total_selling_value - total_stock_value, 2),
                    'low_stock_count': len(low_stock_medicines),
                    'expired_count': len(expired_medicines)
                },
                'low_stock_medicines': low_stock_medicines,
                'expired_medicines': expired_medicines,
                'category_breakdown': [
                    {
                        'category': category,
                        'count': stats['count'],
                        'total_quantity': stats['total_quantity'],
                        'stock_value': round(stats['stock_value'], 2)
                    }
                    for category, stats in category_stats.items()
                ]
            }
            
            self.logger.info(f"Inventory report generated with {total_medicines} medicines")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate inventory report: {e}")
            return None
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """
        Get quick statistics for dashboard
        
        Returns:
            Dictionary containing quick stats
        """
        try:
            today = date.today().isoformat()
            week_ago = (date.today() - timedelta(days=7)).isoformat()
            month_ago = (date.today() - timedelta(days=30)).isoformat()
            
            # Today's sales
            today_revenue = self.sales_repository.get_total_revenue(today, today)
            today_transactions = len(self.sales_repository.get_daily_sales(today))
            
            # This week's sales
            week_revenue = self.sales_repository.get_total_revenue(week_ago, today)
            
            # This month's sales
            month_revenue = self.sales_repository.get_total_revenue(month_ago, today)
            
            # Total statistics
            total_revenue = self.sales_repository.get_total_revenue()
            total_transactions = self.sales_repository.get_total_sales_count()
            
            # Medicine statistics
            medicines = self.medicine_repository.find_all()
            total_medicines = len(medicines)
            low_stock_count = len([med for med in medicines if med.is_low_stock()])
            expired_count = len([med for med in medicines if med.is_expired()])
            
            return {
                'today': {
                    'revenue': round(today_revenue, 2),
                    'transactions': today_transactions
                },
                'week': {
                    'revenue': round(week_revenue, 2)
                },
                'month': {
                    'revenue': round(month_revenue, 2)
                },
                'total': {
                    'revenue': round(total_revenue, 2),
                    'transactions': total_transactions,
                    'medicines': total_medicines,
                    'low_stock': low_stock_count,
                    'expired': expired_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get quick stats: {e}")
            return {}
    
    def get_sales_trend_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get sales trend data for specified number of days
        
        Args:
            days: Number of days to include in trend
            
        Returns:
            List of daily sales data for trend analysis
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            # Get sales analytics for the period
            analytics = self.sales_repository.get_sales_analytics(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            # Create complete daily data (including days with no sales)
            trend_data = []
            current_date = start_date
            daily_data = {item['date']: item for item in analytics.get('daily_breakdown', [])}
            
            while current_date <= end_date:
                date_str = current_date.isoformat()
                if date_str in daily_data:
                    trend_data.append(daily_data[date_str])
                else:
                    trend_data.append({
                        'date': date_str,
                        'transactions': 0,
                        'revenue': 0.0
                    })
                current_date += timedelta(days=1)
            
            return trend_data
            
        except Exception as e:
            self.logger.error(f"Failed to get sales trend data: {e}")
            return []
    
    def _calculate_trends(self, date_range: DateRange) -> Dict[str, Any]:
        """
        Calculate trend analysis for the report period
        
        Args:
            date_range: Date range for trend calculation
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            # Get current period data
            current_analytics = self.sales_repository.get_sales_analytics(
                date_range.start_date,
                date_range.end_date
            )
            
            # Calculate previous period for comparison
            days_count = date_range.get_days_count()
            start_date = datetime.strptime(date_range.start_date, "%Y-%m-%d")
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=days_count-1)
            
            # Get previous period data
            prev_analytics = self.sales_repository.get_sales_analytics(
                prev_start_date.strftime("%Y-%m-%d"),
                prev_end_date.strftime("%Y-%m-%d")
            )
            
            # Calculate percentage changes
            current_revenue = current_analytics.get('summary', {}).get('total_revenue', 0)
            prev_revenue = prev_analytics.get('summary', {}).get('total_revenue', 0)
            
            current_transactions = current_analytics.get('summary', {}).get('total_transactions', 0)
            prev_transactions = prev_analytics.get('summary', {}).get('total_transactions', 0)
            
            revenue_change = self._calculate_percentage_change(prev_revenue, current_revenue)
            transaction_change = self._calculate_percentage_change(prev_transactions, current_transactions)
            
            return {
                'revenue_change': revenue_change,
                'transaction_change': transaction_change,
                'comparison_period': {
                    'start': prev_start_date.strftime("%Y-%m-%d"),
                    'end': prev_end_date.strftime("%Y-%m-%d")
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trends: {e}")
            return {}
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> Dict[str, Any]:
        """
        Calculate percentage change between two values
        
        Args:
            old_value: Previous period value
            new_value: Current period value
            
        Returns:
            Dictionary with change information
        """
        if old_value == 0:
            if new_value == 0:
                return {'percentage': 0.0, 'direction': 'stable', 'absolute_change': 0.0}
            else:
                return {'percentage': 100.0, 'direction': 'increase', 'absolute_change': new_value}
        
        percentage = ((new_value - old_value) / old_value) * 100
        direction = 'increase' if percentage > 0 else 'decrease' if percentage < 0 else 'stable'
        
        return {
            'percentage': round(abs(percentage), 2),
            'direction': direction,
            'absolute_change': round(new_value - old_value, 2)
        }
    
    def get_predefined_date_ranges(self) -> Dict[str, DateRange]:
        """
        Get predefined date ranges for common report periods
        
        Returns:
            Dictionary of predefined date ranges
        """
        today = date.today()
        
        return {
            'today': DateRange(
                start_date=today.isoformat(),
                end_date=today.isoformat()
            ),
            'yesterday': DateRange(
                start_date=(today - timedelta(days=1)).isoformat(),
                end_date=(today - timedelta(days=1)).isoformat()
            ),
            'this_week': DateRange(
                start_date=(today - timedelta(days=today.weekday())).isoformat(),
                end_date=today.isoformat()
            ),
            'last_week': DateRange(
                start_date=(today - timedelta(days=today.weekday() + 7)).isoformat(),
                end_date=(today - timedelta(days=today.weekday() + 1)).isoformat()
            ),
            'this_month': DateRange(
                start_date=today.replace(day=1).isoformat(),
                end_date=today.isoformat()
            ),
            'last_month': DateRange(
                start_date=(today.replace(day=1) - timedelta(days=1)).replace(day=1).isoformat(),
                end_date=(today.replace(day=1) - timedelta(days=1)).isoformat()
            ),
            'last_7_days': DateRange(
                start_date=(today - timedelta(days=6)).isoformat(),
                end_date=today.isoformat()
            ),
            'last_30_days': DateRange(
                start_date=(today - timedelta(days=29)).isoformat(),
                end_date=today.isoformat()
            ),
            'last_90_days': DateRange(
                start_date=(today - timedelta(days=89)).isoformat(),
                end_date=today.isoformat()
            )
        }