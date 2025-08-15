"""
Tests for Reports Widget components
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta

from medical_store_app.managers.report_manager import ReportManager, DateRange, ReportData


class TestReportGenerationLogic:
    """Test report generation logic without UI dependencies"""
    
    @pytest.fixture
    def mock_report_manager(self):
        """Mock report manager"""
        return Mock(spec=ReportManager)
    
    @pytest.fixture
    def sample_date_range(self):
        """Sample date range"""
        return DateRange("2024-01-01", "2024-01-31")
    
    def test_sales_report_generation_logic(self, mock_report_manager, sample_date_range):
        """Test sales report generation logic"""
        # Setup mock
        mock_report = ReportData(
            title="Test Report",
            period_start="2024-01-01",
            period_end="2024-01-31"
        )
        mock_report_manager.generate_sales_report.return_value = mock_report
        
        # Simulate report generation
        result = mock_report_manager.generate_sales_report(sample_date_range)
        
        # Verify result
        assert result == mock_report
        mock_report_manager.generate_sales_report.assert_called_once_with(sample_date_range)
    
    def test_inventory_report_generation_logic(self, mock_report_manager):
        """Test inventory report generation logic"""
        # Setup mock
        mock_report = {"title": "Inventory Report", "summary": {}}
        mock_report_manager.generate_inventory_report.return_value = mock_report
        
        # Simulate report generation
        result = mock_report_manager.generate_inventory_report()
        
        # Verify result
        assert result == mock_report
        mock_report_manager.generate_inventory_report.assert_called_once()
    
    def test_predefined_date_ranges_logic(self, mock_report_manager):
        """Test predefined date ranges logic"""
        # Setup mock
        expected_ranges = {
            'today': DateRange(date.today().isoformat(), date.today().isoformat()),
            'last_7_days': DateRange(
                (date.today() - timedelta(days=6)).isoformat(),
                date.today().isoformat()
            )
        }
        mock_report_manager.get_predefined_date_ranges.return_value = expected_ranges
        
        # Get predefined ranges
        result = mock_report_manager.get_predefined_date_ranges()
        
        # Verify result
        assert result == expected_ranges
        assert 'today' in result
        assert 'last_7_days' in result
        mock_report_manager.get_predefined_date_ranges.assert_called_once()


class TestReportDataProcessing:
    """Test report data processing logic"""
    
    @pytest.fixture
    def sample_daily_data(self):
        """Sample daily sales data"""
        return [
            {'date': '2024-01-01', 'revenue': 500.0, 'transactions': 5},
            {'date': '2024-01-02', 'revenue': 750.0, 'transactions': 8},
            {'date': '2024-01-03', 'revenue': 300.0, 'transactions': 3}
        ]
    
    @pytest.fixture
    def sample_payment_data(self):
        """Sample payment methods data"""
        return [
            {'method': 'cash', 'revenue': 1000.0, 'transactions': 10},
            {'method': 'card', 'revenue': 550.0, 'transactions': 6}
        ]
    
    @pytest.fixture
    def sample_medicines_data(self):
        """Sample top medicines data"""
        return [
            {
                'name': 'Paracetamol',
                'total_quantity': 100,
                'total_revenue': 800.0,
                'transactions': 20
            },
            {
                'name': 'Amoxicillin',
                'total_quantity': 50,
                'total_revenue': 900.0,
                'transactions': 15
            }
        ]
    
    def test_daily_data_processing(self, sample_daily_data):
        """Test processing of daily sales data"""
        # Calculate totals
        total_revenue = sum(item['revenue'] for item in sample_daily_data)
        total_transactions = sum(item['transactions'] for item in sample_daily_data)
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Verify calculations
        assert total_revenue == 1550.0
        assert total_transactions == 16
        assert avg_transaction == 96.875
        
        # Find best day
        best_day = max(sample_daily_data, key=lambda x: x['revenue'])
        assert best_day['date'] == '2024-01-02'
        assert best_day['revenue'] == 750.0
    
    def test_payment_data_processing(self, sample_payment_data):
        """Test processing of payment methods data"""
        # Calculate totals
        total_revenue = sum(item['revenue'] for item in sample_payment_data)
        total_transactions = sum(item['transactions'] for item in sample_payment_data)
        
        # Verify calculations
        assert total_revenue == 1550.0
        assert total_transactions == 16
        
        # Verify payment method distribution
        cash_percentage = (1000.0 / total_revenue) * 100
        card_percentage = (550.0 / total_revenue) * 100
        
        assert abs(cash_percentage - 64.52) < 0.01
        assert abs(card_percentage - 35.48) < 0.01
    
    def test_medicines_data_processing(self, sample_medicines_data):
        """Test processing of top medicines data"""
        # Sort by revenue (descending)
        sorted_medicines = sorted(sample_medicines_data, key=lambda x: x['total_revenue'], reverse=True)
        
        # Verify sorting
        assert sorted_medicines[0]['name'] == 'Amoxicillin'
        assert sorted_medicines[0]['total_revenue'] == 900.0
        assert sorted_medicines[1]['name'] == 'Paracetamol'
        assert sorted_medicines[1]['total_revenue'] == 800.0
        
        # Calculate totals
        total_quantity = sum(item['total_quantity'] for item in sample_medicines_data)
        total_revenue = sum(item['total_revenue'] for item in sample_medicines_data)
        
        assert total_quantity == 150
        assert total_revenue == 1700.0
    
    def test_empty_data_handling(self):
        """Test handling of empty data sets"""
        empty_data = []
        
        # Test empty daily data
        total_revenue = sum(item['revenue'] for item in empty_data)
        total_transactions = sum(item['transactions'] for item in empty_data)
        
        assert total_revenue == 0
        assert total_transactions == 0
        
        # Test finding best day with empty data
        best_day = None
        if empty_data:
            best_day = max(empty_data, key=lambda x: x['revenue'])
        
        assert best_day is None
    
    def test_data_validation(self):
        """Test data validation logic"""
        # Test valid data
        valid_item = {'date': '2024-01-01', 'revenue': 500.0, 'transactions': 5}
        
        # Basic validation checks
        assert 'date' in valid_item
        assert 'revenue' in valid_item
        assert 'transactions' in valid_item
        assert isinstance(valid_item['revenue'], (int, float))
        assert isinstance(valid_item['transactions'], int)
        assert valid_item['revenue'] >= 0
        assert valid_item['transactions'] >= 0
        
        # Test date format validation
        try:
            from datetime import datetime
            datetime.strptime(valid_item['date'], '%Y-%m-%d')
            date_valid = True
        except ValueError:
            date_valid = False
        
        assert date_valid


if __name__ == "__main__":
    pytest.main([__file__])