"""
Tests for Dashboard Overview Cards functionality
Tests dashboard widget with key metrics cards and real-time data display
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime, timedelta
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.dashboard import DashboardWidget, MetricCard
from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.managers.sales_manager import SalesManager
from medical_store_app.models.medicine import Medicine
from medical_store_app.models.sale import Sale, SaleItem


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()


@pytest.fixture
def mock_medicine_manager():
    """Create mock medicine manager"""
    manager = Mock(spec=MedicineManager)
    
    # Mock inventory summary
    manager.get_inventory_summary.return_value = {
        'total_medicines': 150,
        'total_stock_value': 25000.50,
        'low_stock_count': 5,
        'expired_count': 2,
        'expiring_soon_count': 8,
        'categories': ['Pain Relief', 'Antibiotics', 'Vitamins', 'First Aid']
    }
    
    return manager


@pytest.fixture
def mock_sales_manager():
    """Create mock sales manager"""
    manager = Mock(spec=SalesManager)
    
    # Mock daily sales data
    today = date.today().isoformat()
    sample_sales = [
        Sale(
            id=1,
            date=today,
            items=[
                SaleItem(medicine_id=1, name="Paracetamol", quantity=2, unit_price=5.0, total_price=10.0)
            ],
            subtotal=10.0,
            discount=0.0,
            tax=1.0,
            total=11.0,
            payment_method="cash"
        ),
        Sale(
            id=2,
            date=today,
            items=[
                SaleItem(medicine_id=2, name="Amoxicillin", quantity=1, unit_price=15.0, total_price=15.0)
            ],
            subtotal=15.0,
            discount=2.0,
            tax=1.3,
            total=14.3,
            payment_method="card"
        )
    ]
    
    manager.get_daily_sales.return_value = sample_sales
    
    return manager


@pytest.fixture
def dashboard_widget(app, mock_medicine_manager, mock_sales_manager):
    """Create dashboard widget for testing"""
    widget = DashboardWidget(mock_medicine_manager, mock_sales_manager)
    return widget


class TestMetricCard:
    """Test cases for MetricCard component"""
    
    def test_metric_card_creation(self, app):
        """Test metric card creation with basic properties"""
        card = MetricCard(
            title="Test Metric",
            value="100",
            subtitle="Test subtitle",
            card_type="success",
            clickable=True
        )
        
        assert card.title == "Test Metric"
        assert card.value == "100"
        assert card.subtitle == "Test subtitle"
        assert card.card_type == "success"
        assert card.clickable is True
        
        # Check UI elements exist
        assert hasattr(card, 'title_label')
        assert hasattr(card, 'value_label')
        assert hasattr(card, 'subtitle_label')
        
        # Check text content
        assert card.title_label.text() == "Test Metric"
        assert card.value_label.text() == "100"
        assert card.subtitle_label.text() == "Test subtitle"
    
    def test_metric_card_without_subtitle(self, app):
        """Test metric card creation without subtitle"""
        card = MetricCard(
            title="Simple Metric",
            value="50",
            card_type="default"
        )
        
        assert card.subtitle == ""
        assert card.subtitle_label is None
    
    def test_metric_card_update_value(self, app):
        """Test updating metric card value and subtitle"""
        card = MetricCard(
            title="Dynamic Metric",
            value="0",
            subtitle="Initial",
            card_type="warning"
        )
        
        # Update value and subtitle
        card.update_value("250", "Updated subtitle")
        
        assert card.value == "250"
        assert card.subtitle == "Updated subtitle"
        assert card.value_label.text() == "250"
        assert card.subtitle_label.text() == "Updated subtitle"
    
    def test_metric_card_click_signal(self, app):
        """Test metric card click signal emission"""
        card = MetricCard(
            title="Clickable Metric",
            value="75",
            card_type="danger",
            clickable=True
        )
        
        # Connect signal to mock
        signal_mock = Mock()
        card.card_clicked.connect(signal_mock)
        
        # Simulate mouse click
        QTest.mouseClick(card, Qt.LeftButton)
        
        # Verify signal was emitted with correct card type
        signal_mock.assert_called_once_with("danger")
    
    def test_metric_card_styling_types(self, app):
        """Test different card styling types"""
        card_types = ["default", "success", "warning", "danger"]
        
        for card_type in card_types:
            card = MetricCard(
                title=f"{card_type.title()} Card",
                value="123",
                card_type=card_type
            )
            
            # Verify card type is set
            assert card.card_type == card_type
            
            # Verify styling is applied (check if styleSheet is not empty)
            assert card.styleSheet() != ""


class TestDashboardWidget:
    """Test cases for DashboardWidget component"""
    
    def test_dashboard_widget_creation(self, dashboard_widget):
        """Test dashboard widget creation and initialization"""
        assert dashboard_widget is not None
        assert hasattr(dashboard_widget, 'medicine_manager')
        assert hasattr(dashboard_widget, 'sales_manager')
        assert hasattr(dashboard_widget, 'refresh_timer')
        
        # Check metric cards exist
        assert hasattr(dashboard_widget, 'total_sales_card')
        assert hasattr(dashboard_widget, 'total_medicines_card')
        assert hasattr(dashboard_widget, 'low_stock_card')
        assert hasattr(dashboard_widget, 'expired_stock_card')
        assert hasattr(dashboard_widget, 'metric_cards')
        
        # Verify all cards are in the metric_cards list
        assert len(dashboard_widget.metric_cards) == 4
    
    def test_dashboard_data_refresh(self, dashboard_widget, mock_medicine_manager, mock_sales_manager):
        """Test dashboard data refresh functionality"""
        # Reset mocks since they were called during initialization
        mock_sales_manager.reset_mock()
        mock_medicine_manager.reset_mock()
        
        # Trigger data refresh
        dashboard_widget.refresh_data()
        
        # Verify managers were called
        mock_sales_manager.get_daily_sales.assert_called_once()
        mock_medicine_manager.get_inventory_summary.assert_called_once()
        
        # Check card values were updated
        assert dashboard_widget.total_sales_card.value == "$25.30"  # 11.0 + 14.3
        assert dashboard_widget.total_sales_card.subtitle == "2 transactions"
        
        assert dashboard_widget.total_medicines_card.value == "150"
        assert dashboard_widget.total_medicines_card.subtitle == "4 categories"
        
        assert dashboard_widget.low_stock_card.value == "5"
        assert dashboard_widget.low_stock_card.subtitle == "Requires attention"
        
        assert dashboard_widget.expired_stock_card.value == "2"
        assert dashboard_widget.expired_stock_card.subtitle == "Immediate action needed"
    
    def test_dashboard_zero_values(self, app, mock_medicine_manager, mock_sales_manager):
        """Test dashboard with zero values"""
        # Mock empty data
        mock_sales_manager.get_daily_sales.return_value = []
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 0,
            'total_stock_value': 0.0,
            'low_stock_count': 0,
            'expired_count': 0,
            'expiring_soon_count': 0,
            'categories': []
        }
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        dashboard.refresh_data()
        
        # Check zero values are displayed correctly
        assert dashboard.total_sales_card.value == "$0.00"
        assert dashboard.total_sales_card.subtitle == "0 transactions"
        
        assert dashboard.total_medicines_card.value == "0"
        assert dashboard.total_medicines_card.subtitle == "0 categories"
        
        assert dashboard.low_stock_card.value == "0"
        assert dashboard.low_stock_card.subtitle == "All good"
        
        assert dashboard.expired_stock_card.value == "0"
        assert dashboard.expired_stock_card.subtitle == "All good"
    
    def test_dashboard_error_handling(self, app, mock_medicine_manager, mock_sales_manager):
        """Test dashboard error handling when data retrieval fails"""
        # Mock exceptions
        mock_sales_manager.get_daily_sales.side_effect = Exception("Database error")
        mock_medicine_manager.get_inventory_summary.side_effect = Exception("Connection error")
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        dashboard.refresh_data()
        
        # Check error state is handled gracefully
        for card in dashboard.metric_cards:
            assert card.value_label.text() == "Error"
    
    def test_dashboard_get_metrics(self, dashboard_widget, mock_medicine_manager, mock_sales_manager):
        """Test getting dashboard metrics for testing purposes"""
        metrics = dashboard_widget.get_dashboard_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_sales_today' in metrics
        assert 'transaction_count' in metrics
        assert 'total_medicines' in metrics
        assert 'categories_count' in metrics
        assert 'low_stock_count' in metrics
        assert 'expired_count' in metrics
        
        # Check values match expected data
        assert metrics['total_sales_today'] == 25.3  # 11.0 + 14.3
        assert metrics['transaction_count'] == 2
        assert metrics['total_medicines'] == 150
        assert metrics['categories_count'] == 4
        assert metrics['low_stock_count'] == 5
        assert metrics['expired_count'] == 2
    
    def test_dashboard_card_navigation_signals(self, dashboard_widget):
        """Test dashboard card click navigation signals"""
        # Connect navigation signal to mock
        navigation_mock = Mock()
        dashboard_widget.navigate_to.connect(navigation_mock)
        
        # Test each card navigation
        QTest.mouseClick(dashboard_widget.total_sales_card, Qt.LeftButton)
        navigation_mock.assert_called_with("reports")
        
        navigation_mock.reset_mock()
        QTest.mouseClick(dashboard_widget.total_medicines_card, Qt.LeftButton)
        navigation_mock.assert_called_with("inventory")
        
        navigation_mock.reset_mock()
        QTest.mouseClick(dashboard_widget.low_stock_card, Qt.LeftButton)
        navigation_mock.assert_called_with("inventory")
        
        navigation_mock.reset_mock()
        QTest.mouseClick(dashboard_widget.expired_stock_card, Qt.LeftButton)
        navigation_mock.assert_called_with("inventory")
    
    def test_dashboard_refresh_timer(self, dashboard_widget):
        """Test dashboard auto-refresh timer functionality"""
        # Check timer is running
        assert dashboard_widget.refresh_timer.isActive()
        
        # Test setting refresh interval
        dashboard_widget.set_refresh_interval(60)
        assert dashboard_widget.refresh_timer.interval() == 60000  # 60 seconds in milliseconds
        
        # Test stopping refresh
        dashboard_widget.stop_refresh()
        assert not dashboard_widget.refresh_timer.isActive()
        
        # Test starting refresh
        dashboard_widget.start_refresh()
        assert dashboard_widget.refresh_timer.isActive()
    
    def test_dashboard_responsive_layout(self, dashboard_widget):
        """Test dashboard responsive layout"""
        # Show the widget to make it visible
        dashboard_widget.show()
        QTest.qWait(100)
        
        # Test different window sizes
        dashboard_widget.resize(800, 600)
        QTest.qWait(100)  # Allow layout to update
        
        dashboard_widget.resize(1200, 800)
        QTest.qWait(100)
        
        dashboard_widget.resize(1600, 1000)
        QTest.qWait(100)
        
        # Verify widget is still functional after resizing
        assert dashboard_widget.isVisible()
        assert len(dashboard_widget.metric_cards) == 4
    
    def test_dashboard_styling_application(self, dashboard_widget):
        """Test dashboard styling is properly applied"""
        # Check main widget has styling
        assert dashboard_widget.styleSheet() != ""
        
        # Check cards have styling
        for card in dashboard_widget.metric_cards:
            assert card.styleSheet() != ""
    
    @patch('medical_store_app.ui.components.dashboard.date')
    def test_dashboard_date_handling(self, mock_date, dashboard_widget, mock_sales_manager):
        """Test dashboard handles date correctly for daily sales"""
        # Mock today's date
        test_date = date(2024, 1, 15)
        mock_date.today.return_value = test_date
        
        dashboard_widget.refresh_data()
        
        # Verify get_daily_sales was called with correct date
        mock_sales_manager.get_daily_sales.assert_called_with("2024-01-15")


class TestDashboardIntegration:
    """Integration tests for dashboard functionality"""
    
    def test_dashboard_real_time_updates(self, app, mock_medicine_manager, mock_sales_manager):
        """Test dashboard real-time data updates"""
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Initial state
        initial_metrics = dashboard.get_dashboard_metrics()
        
        # Update mock data
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 200,
            'total_stock_value': 30000.0,
            'low_stock_count': 3,
            'expired_count': 1,
            'expiring_soon_count': 5,
            'categories': ['Pain Relief', 'Antibiotics', 'Vitamins', 'First Aid', 'Supplements']
        }
        
        # Refresh data
        dashboard.refresh_data()
        
        # Check updates
        updated_metrics = dashboard.get_dashboard_metrics()
        assert updated_metrics['total_medicines'] != initial_metrics['total_medicines']
        assert updated_metrics['categories_count'] != initial_metrics['categories_count']
        assert updated_metrics['low_stock_count'] != initial_metrics['low_stock_count']
        assert updated_metrics['expired_count'] != initial_metrics['expired_count']
    
    def test_dashboard_performance_with_large_data(self, app, mock_medicine_manager, mock_sales_manager):
        """Test dashboard performance with large datasets"""
        # Mock large dataset
        large_sales = []
        for i in range(100):
            sale = Sale(
                id=i,
                date=date.today().isoformat(),
                items=[SaleItem(medicine_id=1, name=f"Medicine {i}", quantity=1, unit_price=10.0, total_price=10.0)],
                subtotal=10.0,
                discount=0.0,
                tax=1.0,
                total=11.0,
                payment_method="cash"
            )
            large_sales.append(sale)
        
        mock_sales_manager.get_daily_sales.return_value = large_sales
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 10000,
            'total_stock_value': 500000.0,
            'low_stock_count': 100,
            'expired_count': 50,
            'expiring_soon_count': 200,
            'categories': [f"Category {i}" for i in range(50)]
        }
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Measure refresh time (should be fast)
        import time
        start_time = time.time()
        dashboard.refresh_data()
        end_time = time.time()
        
        refresh_time = end_time - start_time
        assert refresh_time < 1.0  # Should complete within 1 second
        
        # Verify data is correctly calculated
        metrics = dashboard.get_dashboard_metrics()
        assert metrics['total_sales_today'] == 1100.0  # 100 sales * 11.0 each
        assert metrics['transaction_count'] == 100
        assert metrics['total_medicines'] == 10000
        assert metrics['categories_count'] == 50


if __name__ == '__main__':
    pytest.main([__file__])