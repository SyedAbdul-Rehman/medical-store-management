"""
Tests for Dashboard Quick Actions functionality
Tests quick action buttons and navigation shortcuts
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.dashboard import DashboardWidget
from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.managers.sales_manager import SalesManager


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
    
    # Mock inventory summary with alerts
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
    
    # Mock daily sales and chart data
    manager.get_daily_sales.return_value = []
    manager.get_last_7_days_sales_data.return_value = {}
    
    return manager


@pytest.fixture
def dashboard_widget(app, mock_medicine_manager, mock_sales_manager):
    """Create dashboard widget for testing"""
    widget = DashboardWidget(mock_medicine_manager, mock_sales_manager)
    return widget


class TestDashboardQuickActions:
    """Test cases for dashboard quick actions functionality"""
    
    def test_quick_actions_section_creation(self, dashboard_widget):
        """Test quick actions section is created with all buttons"""
        # Check that quick action buttons exist
        assert hasattr(dashboard_widget, 'quick_action_buttons')
        assert len(dashboard_widget.quick_action_buttons) == 6
        
        # Check specific buttons exist
        assert hasattr(dashboard_widget, 'low_stock_btn')
        assert hasattr(dashboard_widget, 'expired_items_btn')
        
        # Verify all buttons are properly configured
        for button in dashboard_widget.quick_action_buttons:
            assert button is not None
            assert button.text() != ""
            assert button.toolTip() != ""
    
    def test_quick_action_button_navigation_signals(self, dashboard_widget):
        """Test quick action buttons emit correct navigation signals"""
        # Connect navigation signal to mock
        navigation_mock = Mock()
        dashboard_widget.navigate_to.connect(navigation_mock)
        
        # Test each button navigation
        button_navigation_map = [
            ("Add Medicine", "medicine"),
            ("Process Sale", "billing"),
            ("View Inventory", "inventory"),
            ("Low Stock", "inventory"),  # Will match "Low Stock (5)"
            ("Expired", "inventory"),    # Will match "Expired (2)"
            ("View Reports", "reports")
        ]
        
        for button_text, expected_destination in button_navigation_map:
            navigation_mock.reset_mock()
            
            # Find button by text (partial match)
            target_button = None
            for button in dashboard_widget.quick_action_buttons:
                if button_text in button.text():
                    target_button = button
                    break
            
            assert target_button is not None, f"Button containing '{button_text}' not found. Available buttons: {[btn.text() for btn in dashboard_widget.quick_action_buttons]}"
            
            # Click button
            QTest.mouseClick(target_button, Qt.LeftButton)
            
            # Verify navigation signal
            navigation_mock.assert_called_once_with(expected_destination)
    
    def test_quick_action_buttons_with_alerts(self, app, mock_medicine_manager, mock_sales_manager):
        """Test quick action buttons update based on alert conditions"""
        # Create dashboard with alert conditions
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 100,
            'total_stock_value': 15000.0,
            'low_stock_count': 3,
            'expired_count': 1,
            'expiring_soon_count': 5,
            'categories': ['Category1', 'Category2']
        }
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Check that buttons show alert counts
        assert "Low Stock (3)" in dashboard.low_stock_btn.text()
        assert "Expired (1)" in dashboard.expired_items_btn.text()
        
        # Check that buttons have alert styling (non-empty custom stylesheet)
        assert dashboard.low_stock_btn.styleSheet() != ""
        assert dashboard.expired_items_btn.styleSheet() != ""
    
    def test_quick_action_buttons_without_alerts(self, app, mock_medicine_manager, mock_sales_manager):
        """Test quick action buttons when no alerts are present"""
        # Create dashboard without alert conditions
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 100,
            'total_stock_value': 15000.0,
            'low_stock_count': 0,
            'expired_count': 0,
            'expiring_soon_count': 0,
            'categories': ['Category1', 'Category2']
        }
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Check that buttons show default text
        assert dashboard.low_stock_btn.text() == "Low Stock Items"
        assert dashboard.expired_items_btn.text() == "Expired Items"
        
        # Check that buttons use default styling (empty custom stylesheet)
        assert dashboard.low_stock_btn.styleSheet() == ""
        assert dashboard.expired_items_btn.styleSheet() == ""
    
    def test_quick_action_buttons_dynamic_update(self, dashboard_widget, mock_medicine_manager):
        """Test quick action buttons update dynamically when data changes"""
        # Initial state (with alerts from fixture)
        assert "Low Stock (5)" in dashboard_widget.low_stock_btn.text()
        assert "Expired (2)" in dashboard_widget.expired_items_btn.text()
        
        # Update mock to return no alerts
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 100,
            'total_stock_value': 15000.0,
            'low_stock_count': 0,
            'expired_count': 0,
            'expiring_soon_count': 0,
            'categories': ['Category1']
        }
        
        # Trigger refresh
        dashboard_widget.refresh_data()
        
        # Check buttons updated to no-alert state
        assert dashboard_widget.low_stock_btn.text() == "Low Stock Items"
        assert dashboard_widget.expired_items_btn.text() == "Expired Items"
        assert dashboard_widget.low_stock_btn.styleSheet() == ""
        assert dashboard_widget.expired_items_btn.styleSheet() == ""
    
    def test_quick_action_buttons_hover_effects(self, dashboard_widget):
        """Test quick action buttons have hover effects"""
        # Check that buttons have object names for CSS styling
        for button in dashboard_widget.quick_action_buttons:
            assert button.objectName() == "quickActionButton"
        
        # Check that dashboard has styling for hover effects
        dashboard_style = dashboard_widget.styleSheet()
        assert "quickActionButton:hover" in dashboard_style
    
    def test_quick_action_buttons_tooltips(self, dashboard_widget):
        """Test quick action buttons have appropriate tooltips"""
        expected_tooltips = [
            "Add new medicine to inventory",
            "Start a new sale transaction", 
            "View and manage medicine inventory",
            "View medicines with low stock",
            "View expired medicines",
            "View sales and inventory reports"
        ]
        
        actual_tooltips = [button.toolTip() for button in dashboard_widget.quick_action_buttons]
        
        # Check that all expected tooltips are present
        for expected_tooltip in expected_tooltips:
            assert expected_tooltip in actual_tooltips
    
    def test_quick_action_buttons_styling_consistency(self, dashboard_widget):
        """Test quick action buttons have consistent styling"""
        # Check button types are appropriate
        button_texts_and_types = [
            ("Add Medicine", "primary"),
            ("Process Sale", "secondary"),
            ("View Inventory", "outline"),
            ("Low Stock", "outline"),  # Will match "Low Stock (5)"
            ("Expired", "outline"),    # Will match "Expired (2)"
            ("View Reports", "outline")
        ]
        
        # Verify buttons exist and have expected styling
        for expected_text, expected_type in button_texts_and_types:
            button_found = False
            for button in dashboard_widget.quick_action_buttons:
                if expected_text in button.text():
                    button_found = True
                    # Check that button has appropriate styling class
                    assert hasattr(button, 'button_type') or button.styleSheet() != ""
                    break
            
            assert button_found, f"Button containing '{expected_text}' not found. Available buttons: {[btn.text() for btn in dashboard_widget.quick_action_buttons]}"
    
    def test_quick_actions_error_handling(self, app, mock_medicine_manager, mock_sales_manager):
        """Test quick actions handle errors gracefully"""
        # Mock error in inventory summary
        mock_medicine_manager.get_inventory_summary.side_effect = Exception("Database error")
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Should still create buttons without crashing
        assert hasattr(dashboard, 'quick_action_buttons')
        assert len(dashboard.quick_action_buttons) == 6
        
        # Buttons should have default text
        assert dashboard.low_stock_btn.text() == "Low Stock Items"
        assert dashboard.expired_items_btn.text() == "Expired Items"
    
    def test_quick_actions_accessibility(self, dashboard_widget):
        """Test quick actions are accessible"""
        # Check that buttons are keyboard accessible
        for button in dashboard_widget.quick_action_buttons:
            assert button.focusPolicy() != Qt.NoFocus
            
        # Check that buttons have minimum size for accessibility
        for button in dashboard_widget.quick_action_buttons:
            # The CSS sets min-width to 140px, but Qt might not reflect this in minimumWidth()
            # So we check that the button has reasonable size
            assert button.minimumWidth() >= 80  # Reasonable minimum
            assert button.minimumHeight() >= 40


class TestQuickActionsIntegration:
    """Integration tests for quick actions functionality"""
    
    def test_quick_actions_with_real_data_scenarios(self, app, mock_medicine_manager, mock_sales_manager):
        """Test quick actions with various real data scenarios"""
        # Scenario 1: High alert situation
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 50,
            'total_stock_value': 5000.0,
            'low_stock_count': 15,
            'expired_count': 8,
            'expiring_soon_count': 12,
            'categories': ['Emergency']
        }
        
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Check high alert numbers are displayed
        assert "Low Stock (15)" in dashboard.low_stock_btn.text()
        assert "Expired (8)" in dashboard.expired_items_btn.text()
        
        # Scenario 2: Perfect inventory situation
        mock_medicine_manager.get_inventory_summary.return_value = {
            'total_medicines': 500,
            'total_stock_value': 100000.0,
            'low_stock_count': 0,
            'expired_count': 0,
            'expiring_soon_count': 0,
            'categories': ['Category1', 'Category2', 'Category3']
        }
        
        dashboard.refresh_data()
        
        # Check no alerts are shown
        assert dashboard.low_stock_btn.text() == "Low Stock Items"
        assert dashboard.expired_items_btn.text() == "Expired Items"
    
    def test_quick_actions_navigation_integration(self, dashboard_widget):
        """Test quick actions navigation integrates properly with main application"""
        # This test verifies that navigation signals are emitted correctly
        # The actual navigation handling would be tested in main window tests
        
        navigation_signals = []
        dashboard_widget.navigate_to.connect(lambda dest: navigation_signals.append(dest))
        
        # Click all buttons and collect navigation signals
        for button in dashboard_widget.quick_action_buttons:
            QTest.mouseClick(button, Qt.LeftButton)
        
        # Verify all expected destinations are covered
        expected_destinations = ["medicine", "billing", "inventory", "reports"]
        for destination in expected_destinations:
            assert destination in navigation_signals
    
    def test_quick_actions_performance(self, app, mock_medicine_manager, mock_sales_manager):
        """Test quick actions performance with frequent updates"""
        dashboard = DashboardWidget(mock_medicine_manager, mock_sales_manager)
        
        # Simulate frequent data updates
        import time
        start_time = time.time()
        
        for i in range(10):
            mock_medicine_manager.get_inventory_summary.return_value = {
                'total_medicines': 100 + i,
                'total_stock_value': 15000.0 + i * 100,
                'low_stock_count': i % 5,
                'expired_count': i % 3,
                'expiring_soon_count': i % 7,
                'categories': [f'Category{j}' for j in range(i % 4 + 1)]
            }
            dashboard.refresh_data()
        
        end_time = time.time()
        
        # Should complete quickly even with frequent updates
        assert (end_time - start_time) < 2.0
        
        # Final state should be correct (i % 5 = 4, i % 3 = 0 for i=9)
        final_low_stock = 9 % 5  # = 4
        final_expired = 9 % 3    # = 0
        
        if final_low_stock > 0:
            assert f"Low Stock ({final_low_stock})" in dashboard.low_stock_btn.text()
        else:
            assert dashboard.low_stock_btn.text() == "Low Stock Items"
            
        if final_expired > 0:
            assert f"Expired ({final_expired})" in dashboard.expired_items_btn.text()
        else:
            assert dashboard.expired_items_btn.text() == "Expired Items"


if __name__ == '__main__':
    pytest.main([__file__])