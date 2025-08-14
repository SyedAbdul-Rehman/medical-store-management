"""
Tests for Sales Chart functionality
Tests sales chart widget showing last 7 days performance
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime, timedelta
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.sales_chart import SalesChartWidget, SalesChartCard
from medical_store_app.managers.sales_manager import SalesManager


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()


@pytest.fixture
def sample_sales_data():
    """Create sample sales data for testing"""
    today = date.today()
    data = {}
    
    # Generate 7 days of sample data
    for i in range(7):
        test_date = today - timedelta(days=6-i)
        data[test_date.isoformat()] = float(100 + i * 50)  # Increasing sales trend
    
    return data


@pytest.fixture
def empty_sales_data():
    """Create empty sales data for testing"""
    today = date.today()
    data = {}
    
    # Generate 7 days of zero data
    for i in range(7):
        test_date = today - timedelta(days=6-i)
        data[test_date.isoformat()] = 0.0
    
    return data


class TestSalesChartWidget:
    """Test cases for SalesChartWidget component"""
    
    def test_sales_chart_widget_creation(self, app):
        """Test sales chart widget creation and initialization"""
        chart = SalesChartWidget()
        
        assert chart is not None
        assert hasattr(chart, 'figure')
        assert hasattr(chart, 'canvas')
        assert hasattr(chart, 'ax')
        assert hasattr(chart, 'sales_data')
        assert chart.sales_data == {}
    
    def test_sales_chart_update_with_data(self, app, sample_sales_data):
        """Test updating chart with sales data"""
        chart = SalesChartWidget()
        
        # Update chart with sample data
        chart.update_chart_data(sample_sales_data)
        
        # Verify data was stored
        assert chart.sales_data == sample_sales_data
        
        # Verify chart was drawn (canvas should have been updated)
        assert chart.canvas is not None
    
    def test_sales_chart_update_with_empty_data(self, app, empty_sales_data):
        """Test updating chart with empty/zero sales data"""
        chart = SalesChartWidget()
        
        # Update chart with empty data
        chart.update_chart_data(empty_sales_data)
        
        # Verify data was stored
        assert chart.sales_data == empty_sales_data
    
    def test_sales_chart_update_with_no_data(self, app):
        """Test updating chart with no data"""
        chart = SalesChartWidget()
        
        # Update chart with empty dict
        chart.update_chart_data({})
        
        # Verify empty data handling
        assert chart.sales_data == {}
    
    def test_sales_chart_summary_statistics(self, app, sample_sales_data):
        """Test chart summary statistics calculation"""
        chart = SalesChartWidget()
        chart.update_chart_data(sample_sales_data)
        
        summary = chart.get_chart_summary()
        
        assert isinstance(summary, dict)
        assert 'total' in summary
        assert 'average' in summary
        assert 'max' in summary
        assert 'min' in summary
        
        # Verify calculations
        values = list(sample_sales_data.values())
        assert summary['total'] == sum(values)
        assert summary['average'] == sum(values) / len(values)
        assert summary['max'] == max(values)
        assert summary['min'] == min(values)
    
    def test_sales_chart_summary_with_empty_data(self, app):
        """Test chart summary with empty data"""
        chart = SalesChartWidget()
        
        summary = chart.get_chart_summary()
        
        assert summary['total'] == 0.0
        assert summary['average'] == 0.0
        assert summary['max'] == 0.0
        assert summary['min'] == 0.0
    
    def test_sales_chart_click_signal(self, app):
        """Test chart click signal emission"""
        chart = SalesChartWidget()
        
        # Connect signal to mock
        signal_mock = Mock()
        chart.chart_clicked.connect(signal_mock)
        
        # Simulate mouse click
        QTest.mouseClick(chart, Qt.LeftButton)
        
        # Verify signal was emitted
        signal_mock.assert_called_once()
    
    def test_sales_chart_styling(self, app):
        """Test chart styling is applied"""
        chart = SalesChartWidget()
        
        # Check that styling is applied
        assert chart.styleSheet() != ""
        
        # Check chart frame exists and has styling
        assert hasattr(chart, 'chart_frame')
        assert chart.chart_frame.frameStyle() != 0


class TestSalesChartCard:
    """Test cases for SalesChartCard component"""
    
    def test_sales_chart_card_creation(self, app):
        """Test sales chart card creation"""
        card = SalesChartCard()
        
        assert card is not None
        assert hasattr(card, 'chart_widget')
        assert isinstance(card.chart_widget, SalesChartWidget)
    
    def test_sales_chart_card_update_data(self, app, sample_sales_data):
        """Test updating chart card with data"""
        card = SalesChartCard()
        
        # Update with sample data
        card.update_chart_data(sample_sales_data)
        
        # Verify data was passed to chart widget
        assert card.chart_widget.sales_data == sample_sales_data
    
    def test_sales_chart_card_get_summary(self, app, sample_sales_data):
        """Test getting summary from chart card"""
        card = SalesChartCard()
        card.update_chart_data(sample_sales_data)
        
        summary = card.get_chart_summary()
        
        assert isinstance(summary, dict)
        assert 'total' in summary
        assert summary['total'] > 0
    
    def test_sales_chart_card_click_signal(self, app):
        """Test chart card click signal emission"""
        card = SalesChartCard()
        
        # Connect signal to mock
        signal_mock = Mock()
        card.card_clicked.connect(signal_mock)
        
        # Simulate mouse click on card
        QTest.mouseClick(card, Qt.LeftButton)
        
        # Verify signal was emitted
        signal_mock.assert_called_once()
    
    def test_sales_chart_card_styling(self, app):
        """Test chart card styling"""
        card = SalesChartCard()
        
        # Check styling is applied
        assert card.styleSheet() != ""
        
        # Check frame style
        assert card.frameStyle() != 0
        
        # Check cursor is set for clickability
        assert card.cursor().shape() == Qt.PointingHandCursor


class TestSalesManagerChartData:
    """Test cases for sales manager chart data methods"""
    
    def test_get_last_7_days_sales_data(self):
        """Test getting last 7 days sales data from sales manager"""
        
        # Create mock sales manager
        mock_sales_repo = Mock()
        mock_medicine_repo = Mock()
        sales_manager = SalesManager(mock_sales_repo, mock_medicine_repo)
        
        # Mock the get_sales_by_date_range method
        from medical_store_app.models.sale import Sale, SaleItem
        
        # Use today's actual date for testing
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        sample_sales = [
            Sale(
                id=1,
                date=today.isoformat(),
                items=[SaleItem(medicine_id=1, name="Medicine A", quantity=1, unit_price=10.0, total_price=10.0)],
                subtotal=10.0,
                discount=0.0,
                tax=1.0,
                total=11.0,
                payment_method="cash"
            ),
            Sale(
                id=2,
                date=yesterday.isoformat(),
                items=[SaleItem(medicine_id=2, name="Medicine B", quantity=2, unit_price=15.0, total_price=30.0)],
                subtotal=30.0,
                discount=0.0,
                tax=3.0,
                total=33.0,
                payment_method="card"
            )
        ]
        
        sales_manager.get_sales_by_date_range = Mock(return_value=sample_sales)
        
        # Get chart data
        chart_data = sales_manager.get_last_7_days_sales_data()
        
        # Verify data structure
        assert isinstance(chart_data, dict)
        assert len(chart_data) == 7  # 7 days of data
        
        # Verify date range (should be last 7 days including today)
        expected_start = (today - timedelta(days=6)).isoformat()
        expected_end = today.isoformat()
        
        dates = list(chart_data.keys())
        assert min(dates) == expected_start
        assert max(dates) == expected_end
        
        # Verify sales totals for the days we have data
        assert chart_data[today.isoformat()] == 11.0
        assert chart_data[yesterday.isoformat()] == 33.0
        
        # Verify other days have 0.0
        for date_str in chart_data:
            if date_str not in [today.isoformat(), yesterday.isoformat()]:
                assert chart_data[date_str] == 0.0
    
    def test_get_last_7_days_sales_data_error_handling(self):
        """Test error handling in get_last_7_days_sales_data"""
        # Create mock sales manager with error
        mock_sales_repo = Mock()
        mock_medicine_repo = Mock()
        sales_manager = SalesManager(mock_sales_repo, mock_medicine_repo)
        
        # Mock method to raise exception
        sales_manager.get_sales_by_date_range = Mock(side_effect=Exception("Database error"))
        
        # Get chart data
        chart_data = sales_manager.get_last_7_days_sales_data()
        
        # Should return 7 days of zero data
        assert isinstance(chart_data, dict)
        assert len(chart_data) == 7
        
        # All values should be 0.0
        for value in chart_data.values():
            assert value == 0.0


class TestSalesChartIntegration:
    """Integration tests for sales chart functionality"""
    
    def test_chart_data_processing_with_real_dates(self, app):
        """Test chart data processing with real date scenarios"""
        chart = SalesChartWidget()
        
        # Create data with various scenarios
        today = date.today()
        test_data = {}
        
        # Some days with sales, some without
        for i in range(7):
            test_date = today - timedelta(days=6-i)
            if i % 2 == 0:  # Every other day has sales
                test_data[test_date.isoformat()] = float(50 + i * 25)
            else:
                test_data[test_date.isoformat()] = 0.0
        
        # Update chart
        chart.update_chart_data(test_data)
        
        # Verify data was processed correctly
        assert chart.sales_data == test_data
        
        # Get summary
        summary = chart.get_chart_summary()
        assert summary['total'] > 0
        assert summary['max'] >= summary['average']
        assert summary['min'] <= summary['average']
    
    def test_chart_performance_with_large_values(self, app):
        """Test chart performance with large sales values"""
        chart = SalesChartWidget()
        
        # Create data with large values
        today = date.today()
        large_data = {}
        
        for i in range(7):
            test_date = today - timedelta(days=6-i)
            large_data[test_date.isoformat()] = float(10000 + i * 5000)  # Large sales values
        
        # Update chart (should handle large values gracefully)
        import time
        start_time = time.time()
        chart.update_chart_data(large_data)
        end_time = time.time()
        
        # Should complete quickly
        assert (end_time - start_time) < 2.0
        
        # Verify data
        summary = chart.get_chart_summary()
        assert summary['total'] > 50000  # Should handle large totals
    
    def test_chart_with_invalid_date_formats(self, app):
        """Test chart handling of invalid date formats"""
        chart = SalesChartWidget()
        
        # Create data with invalid date formats
        invalid_data = {
            "2024-13-45": 100.0,  # Invalid date
            "not-a-date": 200.0,  # Not a date at all
            "2024-01-15": 300.0,  # Valid date
        }
        
        # Should handle gracefully without crashing
        chart.update_chart_data(invalid_data)
        
        # Chart should still function
        assert chart.sales_data == invalid_data
        summary = chart.get_chart_summary()
        assert isinstance(summary, dict)


if __name__ == '__main__':
    pytest.main([__file__])