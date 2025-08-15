"""
Integration tests for Dashboard Navigation functionality
Tests that dashboard quick actions properly navigate to correct sections
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.main_window import MainWindow
from medical_store_app.models.user import User


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()


@pytest.fixture
def main_window_with_dashboard(app):
    """Create main window with dashboard loaded"""
    main_window = MainWindow()
    
    # Create test user
    test_user = User(
        username="admin",
        role="admin",
        full_name="Test Admin"
    )
    test_user.set_password("admin123")
    
    # Set current user and show dashboard
    main_window.current_user = test_user
    main_window._update_sidebar_for_role("admin")
    main_window._show_dashboard_content()
    
    return main_window


class TestDashboardNavigationIntegration:
    """Integration tests for dashboard navigation functionality"""
    
    def test_dashboard_navigation_handler_exists(self, main_window_with_dashboard):
        """Test that dashboard navigation handler method exists"""
        main_window = main_window_with_dashboard
        
        # Check that the navigation handler method exists
        assert hasattr(main_window, '_handle_dashboard_navigation')
        assert callable(main_window._handle_dashboard_navigation)
    
    def test_dashboard_navigation_to_medicine(self, main_window_with_dashboard):
        """Test navigation from dashboard to medicine management"""
        main_window = main_window_with_dashboard
        
        # Mock the sidebar and content methods
        main_window.sidebar.set_active_item = Mock()
        main_window._show_medicine_management = Mock()
        
        # Test navigation to medicine
        main_window._handle_dashboard_navigation("medicine", None)
        
        # Verify correct methods were called
        main_window.sidebar.set_active_item.assert_called_once_with("medicine")
        main_window._show_medicine_management.assert_called_once()
    
    def test_dashboard_navigation_to_billing(self, main_window_with_dashboard):
        """Test navigation from dashboard to billing system"""
        main_window = main_window_with_dashboard
        
        # Mock the sidebar and content methods
        main_window.sidebar.set_active_item = Mock()
        main_window._show_billing_content = Mock()
        
        # Test navigation to billing
        main_window._handle_dashboard_navigation("billing", None)
        
        # Verify correct methods were called
        main_window.sidebar.set_active_item.assert_called_once_with("billing")
        main_window._show_billing_content.assert_called_once()
    
    def test_dashboard_navigation_to_inventory(self, main_window_with_dashboard):
        """Test navigation from dashboard to inventory (medicine management)"""
        main_window = main_window_with_dashboard
        
        # Mock the sidebar and content methods
        main_window.sidebar.set_active_item = Mock()
        main_window._show_medicine_management = Mock()
        
        # Test navigation to inventory
        main_window._handle_dashboard_navigation("inventory", None)
        
        # Verify correct methods were called
        main_window.sidebar.set_active_item.assert_called_once_with("medicine")
        main_window._show_medicine_management.assert_called_once()
    
    def test_dashboard_navigation_to_reports(self, main_window_with_dashboard):
        """Test navigation from dashboard to reports"""
        main_window = main_window_with_dashboard
        
        # Mock the sidebar and content methods
        main_window.sidebar.set_active_item = Mock()
        main_window._show_reports_content = Mock()
        
        # Test navigation to reports
        main_window._handle_dashboard_navigation("reports", None)
        
        # Verify correct methods were called
        main_window.sidebar.set_active_item.assert_called_once_with("reports")
        main_window._show_reports_content.assert_called_once()
    
    def test_dashboard_navigation_unknown_destination(self, main_window_with_dashboard):
        """Test navigation with unknown destination"""
        main_window = main_window_with_dashboard
        
        # Mock logger to capture warning
        main_window.logger.warning = Mock()
        
        # Test navigation to unknown destination
        main_window._handle_dashboard_navigation("unknown", None)
        
        # Verify warning was logged
        main_window.logger.warning.assert_called_once()
        assert "Unknown dashboard navigation destination" in str(main_window.logger.warning.call_args)
    
    def test_dashboard_navigation_error_handling(self, main_window_with_dashboard):
        """Test navigation error handling"""
        main_window = main_window_with_dashboard
        
        # Mock sidebar to raise exception
        main_window.sidebar.set_active_item = Mock(side_effect=Exception("Test error"))
        main_window.logger.error = Mock()
        
        # Test navigation with error
        main_window._handle_dashboard_navigation("medicine", None)
        
        # Verify error was logged
        main_window.logger.error.assert_called_once()
        assert "Error handling dashboard navigation" in str(main_window.logger.error.call_args)
    
    def test_dashboard_quick_actions_connected(self, main_window_with_dashboard):
        """Test that dashboard quick action buttons are properly connected"""
        main_window = main_window_with_dashboard
        
        # Get the dashboard widget
        dashboard_widget = None
        if hasattr(main_window, 'current_content_widget'):
            dashboard_widget = main_window.current_content_widget
            
            # Check if it's the dashboard widget (has quick action buttons)
            if hasattr(dashboard_widget, 'quick_action_buttons'):
                # Verify quick action buttons exist
                assert len(dashboard_widget.quick_action_buttons) == 6
                
                # Verify buttons are clickable (have click method)
                for button in dashboard_widget.quick_action_buttons:
                    assert hasattr(button, 'clicked')
                    assert callable(button.click)
    
    def test_dashboard_cards_navigation_connected(self, main_window_with_dashboard):
        """Test that dashboard metric cards are properly connected for navigation"""
        main_window = main_window_with_dashboard
        
        # Get the dashboard widget
        dashboard_widget = None
        if hasattr(main_window, 'current_content_widget'):
            dashboard_widget = main_window.current_content_widget
            
            # Check if it's the dashboard widget (has metric cards)
            if hasattr(dashboard_widget, 'metric_cards'):
                # Verify metric cards exist
                assert len(dashboard_widget.metric_cards) == 4
                
                # Verify cards have click signal
                for card in dashboard_widget.metric_cards:
                    assert hasattr(card, 'card_clicked')
                    assert hasattr(card, 'mousePressEvent')
    
    def test_dashboard_chart_navigation_connected(self, main_window_with_dashboard):
        """Test that dashboard sales chart is properly connected for navigation"""
        main_window = main_window_with_dashboard
        
        # Get the dashboard widget
        dashboard_widget = None
        if hasattr(main_window, 'current_content_widget'):
            dashboard_widget = main_window.current_content_widget
            
            # Check if it's the dashboard widget (has sales chart)
            if hasattr(dashboard_widget, 'sales_chart_card'):
                chart_card = dashboard_widget.sales_chart_card
                
                # Verify chart card has click signal and mouse event handling
                assert hasattr(chart_card, 'card_clicked')
                assert hasattr(chart_card, 'mousePressEvent')
    
    def test_all_navigation_destinations_supported(self, main_window_with_dashboard):
        """Test that all expected navigation destinations are supported"""
        main_window = main_window_with_dashboard
        
        # Mock all navigation methods
        main_window.sidebar.set_active_item = Mock()
        main_window._show_medicine_management = Mock()
        main_window._show_billing_content = Mock()
        main_window._show_reports_content = Mock()
        
        # Test all expected destinations
        expected_destinations = ["medicine", "billing", "inventory", "reports"]
        
        for destination in expected_destinations:
            # Reset mocks
            main_window.sidebar.set_active_item.reset_mock()
            main_window._show_medicine_management.reset_mock()
            main_window._show_billing_content.reset_mock()
            main_window._show_reports_content.reset_mock()
            
            # Test navigation
            main_window._handle_dashboard_navigation(destination, None)
            
            # Verify at least one method was called
            methods_called = [
                main_window.sidebar.set_active_item.called,
                main_window._show_medicine_management.called,
                main_window._show_billing_content.called,
                main_window._show_reports_content.called
            ]
            
            assert any(methods_called), f"No navigation method called for destination: {destination}"
    
    def test_dashboard_navigation_logging(self, main_window_with_dashboard):
        """Test that dashboard navigation is properly logged"""
        main_window = main_window_with_dashboard
        
        # Mock logger and navigation methods
        main_window.logger.info = Mock()
        main_window.sidebar.set_active_item = Mock()
        main_window._show_medicine_management = Mock()
        
        # Test navigation
        main_window._handle_dashboard_navigation("medicine", None)
        
        # Verify navigation was logged
        main_window.logger.info.assert_called_once()
        assert "Handling dashboard navigation to: medicine" in str(main_window.logger.info.call_args)


class TestDashboardNavigationEndToEnd:
    """End-to-end tests for dashboard navigation"""
    
    def test_complete_navigation_flow(self, main_window_with_dashboard):
        """Test complete navigation flow from dashboard to different sections"""
        main_window = main_window_with_dashboard
        
        # Test navigation to each section and verify sidebar state
        navigation_tests = [
            ("medicine", "medicine"),
            ("billing", "billing"),
            ("inventory", "medicine"),  # inventory maps to medicine
            ("reports", "reports")
        ]
        
        for destination, expected_sidebar_item in navigation_tests:
            # Navigate to destination
            main_window._handle_dashboard_navigation(destination, None)
            
            # Verify sidebar active item (if sidebar has get_active_item method)
            if hasattr(main_window.sidebar, 'get_active_item'):
                active_item = main_window.sidebar.get_active_item()
                assert active_item == expected_sidebar_item, f"Expected {expected_sidebar_item}, got {active_item}"
    
    def test_navigation_preserves_user_context(self, main_window_with_dashboard):
        """Test that navigation preserves user context"""
        main_window = main_window_with_dashboard
        
        # Store original user
        original_user = main_window.current_user
        
        # Navigate to different sections
        destinations = ["medicine", "billing", "inventory", "reports"]
        
        for destination in destinations:
            main_window._handle_dashboard_navigation(destination, None)
            
            # Verify user context is preserved
            assert main_window.current_user == original_user
            assert main_window.current_user.username == "admin"
            assert main_window.current_user.role == "admin"
    
    def test_dashboard_filtering_functionality(self, main_window_with_dashboard):
        """Test dashboard filtering functionality for Low Stock and Expired items"""
        main_window = main_window_with_dashboard
        
        # Mock the medicine management widget methods
        main_window._show_medicine_management = Mock()
        main_window.sidebar.set_active_item = Mock()
        
        # Test Low/Out of Stock filter
        main_window._handle_dashboard_navigation("inventory", "Low/Out of Stock")
        main_window.sidebar.set_active_item.assert_called_with("medicine")
        main_window._show_medicine_management.assert_called_with(filter_type="Low/Out of Stock")
        
        # Reset mocks
        main_window._show_medicine_management.reset_mock()
        main_window.sidebar.set_active_item.reset_mock()
        
        # Test Expired filter
        main_window._handle_dashboard_navigation("inventory", "Expired")
        main_window.sidebar.set_active_item.assert_called_with("medicine")
        main_window._show_medicine_management.assert_called_with(filter_type="Expired")
        
        # Reset mocks
        main_window._show_medicine_management.reset_mock()
        main_window.sidebar.set_active_item.reset_mock()
        
        # Test no filter (should clear filters)
        main_window._handle_dashboard_navigation("inventory", "")
        main_window.sidebar.set_active_item.assert_called_with("medicine")
        main_window._show_medicine_management.assert_called_with(filter_type="")


if __name__ == '__main__':
    pytest.main([__file__])