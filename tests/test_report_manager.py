"""
Tests for ReportManager class
"""

import pytest
import sqlite3
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch

from medical_store_app.managers.report_manager import ReportManager, DateRange, ReportData
from medical_store_app.repositories.sales_repository import SalesRepository
from medical_store_app.repositories.medicine_repository import MedicineRepository
from medical_store_app.models.sale import Sale, SaleItem
from medical_store_app.models.medicine import Medicine
from medical_store_app.config.database import DatabaseManager


class TestDateRange:
    """Test DateRange data class"""
    
    def test_valid_date_range(self):
        """Test valid date range validation"""
        date_range = DateRange("2024-01-01", "2024-01-31")
        errors = date_range.validate()
        assert errors == []
    
    def test_invalid_date_format(self):
        """Test invalid date format validation"""
        date_range = DateRange("2024/01/01", "2024-01-31")
        errors = date_range.validate()
        assert "Dates must be in YYYY-MM-DD format" in errors
    
    def test_start_date_after_end_date(self):
        """Test start date after end date validation"""
        date_range = DateRange("2024-01-31", "2024-01-01")
        errors = date_range.validate()
        assert "Start date must be before or equal to end date" in errors
    
    def test_future_end_date(self):
        """Test future end date validation"""
        future_date = (date.today() + timedelta(days=1)).isoformat()
        date_range = DateRange("2024-01-01", future_date)
        errors = date_range.validate()
        assert "End date cannot be in the future" in errors
    
    def test_get_days_count(self):
        """Test days count calculation"""
        date_range = DateRange("2024-01-01", "2024-01-31")
        assert date_range.get_days_count() == 31
        
        date_range = DateRange("2024-01-01", "2024-01-01")
        assert date_range.get_days_count() == 1


class TestReportManager:
    """Test ReportManager class"""
    
    @pytest.fixture
    def mock_sales_repository(self):
        """Mock sales repository"""
        return Mock(spec=SalesRepository)
    
    @pytest.fixture
    def mock_medicine_repository(self):
        """Mock medicine repository"""
        return Mock(spec=MedicineRepository)
    
    @pytest.fixture
    def report_manager(self, mock_sales_repository, mock_medicine_repository):
        """Create ReportManager instance with mocked dependencies"""
        return ReportManager(mock_sales_repository, mock_medicine_repository)
    
    @pytest.fixture
    def sample_analytics(self):
        """Sample analytics data"""
        return {
            'period': {
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            },
            'summary': {
                'total_transactions': 50,
                'total_revenue': 5000.0,
                'average_transaction': 100.0,
                'min_transaction': 10.0,
                'max_transaction': 500.0,
                'total_discounts': 250.0,
                'total_tax': 450.0
            },
            'daily_breakdown': [
                {'date': '2024-01-01', 'transactions': 5, 'revenue': 500.0},
                {'date': '2024-01-02', 'transactions': 3, 'revenue': 300.0}
            ],
            'payment_methods': [
                {'method': 'cash', 'transactions': 30, 'revenue': 3000.0},
                {'method': 'card', 'transactions': 20, 'revenue': 2000.0}
            ]
        }
    
    @pytest.fixture
    def sample_medicines(self):
        """Sample medicines data"""
        return [
            Medicine(
                id=1, name="Paracetamol", category="Pain Relief",
                batch_no="PAR001", expiry_date="2025-12-31",
                quantity=100, purchase_price=5.0, selling_price=8.0
            ),
            Medicine(
                id=2, name="Amoxicillin", category="Antibiotic",
                batch_no="AMX001", expiry_date="2024-06-30",
                quantity=5, purchase_price=12.0, selling_price=18.0  # Low stock
            ),
            Medicine(
                id=3, name="Expired Med", category="Test",
                batch_no="EXP001", expiry_date="2023-12-31",
                quantity=20, purchase_price=10.0, selling_price=15.0  # Expired
            )
        ]
    
    def test_generate_sales_report_success(self, report_manager, mock_sales_repository, sample_analytics):
        """Test successful sales report generation"""
        # Setup mocks
        mock_sales_repository.get_sales_analytics.return_value = sample_analytics
        mock_sales_repository.get_top_selling_medicines.return_value = [
            {
                'medicine_id': 1,
                'name': 'Paracetamol',
                'total_quantity': 50,
                'total_revenue': 400.0,
                'transactions': 10
            }
        ]
        
        date_range = DateRange("2024-01-01", "2024-01-31")
        
        with patch.object(report_manager, '_calculate_trends') as mock_trends:
            mock_trends.return_value = {'revenue_change': {'percentage': 10.0, 'direction': 'increase'}}
            
            report = report_manager.generate_sales_report(date_range)
        
        # Assertions
        assert report is not None
        assert isinstance(report, ReportData)
        assert report.title == "Sales Report (2024-01-01 to 2024-01-31)"
        assert report.period_start == "2024-01-01"
        assert report.period_end == "2024-01-31"
        assert report.summary == sample_analytics['summary']
        assert len(report.daily_breakdown) == 2
        assert len(report.top_medicines) == 1
        assert len(report.payment_methods) == 2
        
        # Verify repository calls
        mock_sales_repository.get_sales_analytics.assert_called_once_with("2024-01-01", "2024-01-31")
        mock_sales_repository.get_top_selling_medicines.assert_called_once_with("2024-01-01", "2024-01-31", limit=10)
    
    def test_generate_sales_report_invalid_date_range(self, report_manager):
        """Test sales report generation with invalid date range"""
        invalid_date_range = DateRange("2024-01-31", "2024-01-01")  # Start after end
        
        report = report_manager.generate_sales_report(invalid_date_range)
        
        assert report is None
    
    def test_generate_sales_report_exception(self, report_manager, mock_sales_repository):
        """Test sales report generation with exception"""
        mock_sales_repository.get_sales_analytics.side_effect = Exception("Database error")
        
        date_range = DateRange("2024-01-01", "2024-01-31")
        report = report_manager.generate_sales_report(date_range)
        
        assert report is None
    
    def test_generate_inventory_report_success(self, report_manager, mock_medicine_repository, sample_medicines):
        """Test successful inventory report generation"""
        mock_medicine_repository.find_all.return_value = sample_medicines
        
        report = report_manager.generate_inventory_report()
        
        # Assertions
        assert report is not None
        assert report['title'] == 'Inventory Status Report'
        assert 'generated_at' in report
        assert 'summary' in report
        assert 'low_stock_medicines' in report
        assert 'expired_medicines' in report
        assert 'category_breakdown' in report
        
        # Check summary calculations
        summary = report['summary']
        assert summary['total_medicines'] == 3
        assert summary['low_stock_count'] == 1  # Amoxicillin
        assert summary['expired_count'] == 2   # Amoxicillin and Expired Med
        
        # Check low stock medicines
        low_stock = report['low_stock_medicines']
        assert len(low_stock) == 1
        assert low_stock[0]['name'] == 'Amoxicillin'
        
        # Check expired medicines
        expired = report['expired_medicines']
        assert len(expired) == 2
        expired_names = [med['name'] for med in expired]
        assert 'Expired Med' in expired_names
        assert 'Amoxicillin' in expired_names
        
        # Check category breakdown
        categories = report['category_breakdown']
        assert len(categories) == 3  # Pain Relief, Antibiotic, Test
    
    def test_generate_inventory_report_exception(self, report_manager, mock_medicine_repository):
        """Test inventory report generation with exception"""
        mock_medicine_repository.find_all.side_effect = Exception("Database error")
        
        report = report_manager.generate_inventory_report()
        
        assert report is None
    
    def test_get_quick_stats_success(self, report_manager, mock_sales_repository, mock_medicine_repository, sample_medicines):
        """Test successful quick stats retrieval"""
        # Setup mocks
        mock_sales_repository.get_total_revenue.side_effect = [100.0, 500.0, 1500.0, 10000.0]  # today, week, month, total
        mock_sales_repository.get_daily_sales.return_value = [Mock(), Mock()]  # 2 transactions today
        mock_sales_repository.get_total_sales_count.return_value = 200
        mock_medicine_repository.find_all.return_value = sample_medicines
        
        stats = report_manager.get_quick_stats()
        
        # Assertions
        assert 'today' in stats
        assert 'week' in stats
        assert 'month' in stats
        assert 'total' in stats
        
        assert stats['today']['revenue'] == 100.0
        assert stats['today']['transactions'] == 2
        assert stats['week']['revenue'] == 500.0
        assert stats['month']['revenue'] == 1500.0
        assert stats['total']['revenue'] == 10000.0
        assert stats['total']['transactions'] == 200
        assert stats['total']['medicines'] == 3
        assert stats['total']['low_stock'] == 1
        assert stats['total']['expired'] == 2
    
    def test_get_quick_stats_exception(self, report_manager, mock_sales_repository):
        """Test quick stats with exception"""
        mock_sales_repository.get_total_revenue.side_effect = Exception("Database error")
        
        stats = report_manager.get_quick_stats()
        
        assert stats == {}
    
    def test_get_sales_trend_data_success(self, report_manager, mock_sales_repository):
        """Test successful sales trend data retrieval"""
        mock_analytics = {
            'daily_breakdown': [
                {'date': '2024-01-01', 'transactions': 5, 'revenue': 500.0},
                {'date': '2024-01-03', 'transactions': 3, 'revenue': 300.0}
            ]
        }
        mock_sales_repository.get_sales_analytics.return_value = mock_analytics
        
        with patch('medical_store_app.managers.report_manager.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 3)
            
            trend_data = report_manager.get_sales_trend_data(days=3)
        
        # Should have 3 days of data, including missing day
        assert len(trend_data) == 3
        assert trend_data[0]['date'] == '2024-01-01'
        assert trend_data[0]['transactions'] == 5
        assert trend_data[1]['date'] == '2024-01-02'
        assert trend_data[1]['transactions'] == 0  # Missing day
        assert trend_data[2]['date'] == '2024-01-03'
        assert trend_data[2]['transactions'] == 3
    
    def test_get_sales_trend_data_exception(self, report_manager, mock_sales_repository):
        """Test sales trend data with exception"""
        mock_sales_repository.get_sales_analytics.side_effect = Exception("Database error")
        
        trend_data = report_manager.get_sales_trend_data()
        
        assert trend_data == []
    
    def test_calculate_percentage_change(self, report_manager):
        """Test percentage change calculation"""
        # Increase
        result = report_manager._calculate_percentage_change(100.0, 150.0)
        assert result['percentage'] == 50.0
        assert result['direction'] == 'increase'
        assert result['absolute_change'] == 50.0
        
        # Decrease
        result = report_manager._calculate_percentage_change(150.0, 100.0)
        assert result['percentage'] == 33.33
        assert result['direction'] == 'decrease'
        assert result['absolute_change'] == -50.0
        
        # No change
        result = report_manager._calculate_percentage_change(100.0, 100.0)
        assert result['percentage'] == 0.0
        assert result['direction'] == 'stable'
        assert result['absolute_change'] == 0.0
        
        # From zero
        result = report_manager._calculate_percentage_change(0.0, 100.0)
        assert result['percentage'] == 100.0
        assert result['direction'] == 'increase'
        assert result['absolute_change'] == 100.0
    
    def test_get_predefined_date_ranges(self, report_manager):
        """Test predefined date ranges"""
        with patch('medical_store_app.managers.report_manager.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)  # Monday
            
            ranges = report_manager.get_predefined_date_ranges()
        
        assert 'today' in ranges
        assert 'yesterday' in ranges
        assert 'this_week' in ranges
        assert 'last_week' in ranges
        assert 'this_month' in ranges
        assert 'last_month' in ranges
        assert 'last_7_days' in ranges
        assert 'last_30_days' in ranges
        assert 'last_90_days' in ranges
        
        # Check today range
        today_range = ranges['today']
        assert today_range.start_date == '2024-01-15'
        assert today_range.end_date == '2024-01-15'
        
        # Check this month range
        this_month_range = ranges['this_month']
        assert this_month_range.start_date == '2024-01-01'
        assert this_month_range.end_date == '2024-01-15'


class TestReportDataIntegration:
    """Integration tests for report data structures"""
    
    def test_report_data_creation(self):
        """Test ReportData creation and default values"""
        report = ReportData(
            title="Test Report",
            period_start="2024-01-01",
            period_end="2024-01-31"
        )
        
        assert report.title == "Test Report"
        assert report.period_start == "2024-01-01"
        assert report.period_end == "2024-01-31"
        assert isinstance(report.generated_at, str)
        assert report.summary == {}
        assert report.daily_breakdown == []
        assert report.top_medicines == []
        assert report.payment_methods == []
        assert report.trends == {}


if __name__ == "__main__":
    pytest.main([__file__])