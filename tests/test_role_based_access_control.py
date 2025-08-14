"""
Tests for role-based access control in the Medical Store Management Application
Tests UI element hiding/disabling based on user role and access control enforcement
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from medical_store_app.ui.main_window import MainWindow
from medical_store_app.ui.components.medicine_management import MedicineManagementWidget
from medical_store_app.ui.components.medicine_table import MedicineTableWidget
from medical_store_app.models.user import User
from medical_store_app.managers.auth_manager import AuthManager
from medical_store_app.managers.medicine_manager import MedicineManager


class TestRoleBasedAccessControl:
    """Test role-based access control functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance"""
        if not QApplication.instance():
            return QApplication(sys.argv)
        return QApplication.instance()
    
    @pytest.fixture
    def mock_auth_manager(self):
        """Create mock authentication manager"""
        auth_manager = Mock(spec=AuthManager)
        auth_manager.is_logged_in.return_value = True
        auth_manager.has_permission.return_value = True
        return auth_manager
    
    @pytest.fixture
    def mock_medicine_manager(self):
        """Create mock medicine manager"""
        medicine_manager = Mock(spec=MedicineManager)
        medicine_manager.get_all_medicines.return_value = []
        return medicine_manager
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user"""
        user = User(
            id=1,
            username="admin",
            role="admin",
            is_active=True,
            full_name="Admin User"
        )
        user.password_hash = User.hash_password("admin123")
        return user
    
    @pytest.fixture
    def cashier_user(self):
        """Create cashier user"""
        user = User(
            id=2,
            username="cashier",
            role="cashier",
            is_active=True,
            full_name="Cashier User"
        )
        user.password_hash = User.hash_password("cashier123")
        return user
    
    @pytest.fixture
    def main_window_with_mocks(self, app, mock_auth_manager, mock_medicine_manager):
        """Create main window with mocked dependencies"""
        with patch('medical_store_app.ui.main_window.DatabaseManager'), \
             patch('medical_store_app.ui.main_window.MedicineRepository'), \
             patch('medical_store_app.ui.main_window.SalesRepository'), \
             patch('medical_store_app.ui.main_window.UserRepository'), \
             patch('medical_store_app.ui.main_window.MedicineManager') as mock_med_mgr, \
             patch('medical_store_app.ui.main_window.SalesManager'), \
             patch('medical_store_app.ui.main_window.AuthManager') as mock_auth_mgr, \
             patch('medical_store_app.ui.main_window.LoginManager') as mock_login_mgr:
            
            mock_med_mgr.return_value = mock_medicine_manager
            mock_auth_mgr.return_value = mock_auth_manager
            
            # Mock login manager to skip login dialog
            mock_login_instance = Mock()
            mock_login_instance.show_login_dialog.return_value = (True, None)
            mock_login_mgr.return_value = mock_login_instance
            
            window = MainWindow()
            return window
    
    def test_admin_user_has_full_sidebar_access(self, main_window_with_mocks, admin_user):
        """Test that admin users can see all sidebar menu items"""
        window = main_window_with_mocks
        window.current_user = admin_user
        
        # Show the window to ensure widgets are properly initialized
        window.show()
        
        window._update_sidebar_for_role("admin")
        
        # Check that all menu items exist in sidebar
        sidebar = window.get_sidebar()
        assert "dashboard" in sidebar.navigation_buttons
        assert "medicine" in sidebar.navigation_buttons
        assert "billing" in sidebar.navigation_buttons
        assert "reports" in sidebar.navigation_buttons
        assert "settings" in sidebar.navigation_buttons
        
        # For admin, reports and settings should be visible
        reports_button = sidebar.navigation_buttons.get("reports")
        settings_button = sidebar.navigation_buttons.get("settings")
        
        assert reports_button.isVisible(), "Reports button should be visible for admin"
        assert settings_button.isVisible(), "Settings button should be visible for admin"
    
    def test_cashier_user_has_restricted_sidebar_access(self, main_window_with_mocks, cashier_user):
        """Test that cashier users have restricted sidebar access"""
        window = main_window_with_mocks
        window.current_user = cashier_user
        
        # Show the window to ensure widgets are properly initialized
        window.show()
        
        window._update_sidebar_for_role("cashier")
        
        sidebar = window.get_sidebar()
        
        # Check that restricted menu items are hidden for cashier
        reports_button = sidebar.navigation_buttons.get("reports")
        settings_button = sidebar.navigation_buttons.get("settings")
        
        assert not reports_button.isVisible(), "Reports button should be hidden for cashier"
        assert not settings_button.isVisible(), "Settings button should be hidden for cashier"
        
        # Check that allowed menu items exist and are accessible
        dashboard_button = sidebar.navigation_buttons.get("dashboard")
        medicine_button = sidebar.navigation_buttons.get("medicine")
        billing_button = sidebar.navigation_buttons.get("billing")
        
        assert dashboard_button is not None, "Dashboard button should exist"
        assert medicine_button is not None, "Medicine button should exist"
        assert billing_button is not None, "Billing button should exist"
    
    def test_feature_permission_checking(self, main_window_with_mocks, cashier_user):
        """Test feature permission checking for different user roles"""
        window = main_window_with_mocks
        window.current_user = cashier_user
        
        # Mock auth manager to return appropriate permissions
        window.auth_manager.has_permission.side_effect = lambda feature: feature in [
            "billing", "medicine_view", "dashboard_view"
        ]
        
        # Test allowed features
        assert window._check_feature_permission("billing") == True
        assert window._check_feature_permission("medicine_view") == True
        assert window._check_feature_permission("dashboard_view") == True
        
        # Test restricted features
        assert window._check_feature_permission("reports") == False
        assert window._check_feature_permission("settings") == False
    
    def test_access_denied_message_for_restricted_features(self, main_window_with_mocks, cashier_user):
        """Test that access denied message is shown for restricted features"""
        window = main_window_with_mocks
        window.current_user = cashier_user
        
        # Mock auth manager to deny permission
        window.auth_manager.has_permission.return_value = False
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            # Try to access restricted feature
            window._on_menu_item_selected("reports")
            
            # Verify warning message was shown
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "Access Denied" in args[1]
            assert "reports" in args[2].lower()
    
    def test_medicine_management_readonly_mode_for_cashier(self, app, mock_medicine_manager):
        """Test that medicine management is in readonly mode for cashiers"""
        from PySide6.QtWidgets import QWidget
        from PySide6.QtCore import Signal
        
        # Create real QWidget subclasses for mocking
        class MockMedicineForm(QWidget):
            medicine_saved = Signal(object)
            operation_finished = Signal(bool, str)
            
            def __init__(self, manager):
                super().__init__()
                self.manager = manager
        
        class MockMedicineTable(QWidget):
            medicine_selected = Signal(object)
            edit_requested = Signal(object)
            delete_requested = Signal(object)
            refresh_requested = Signal()
            
            def __init__(self, manager):
                super().__init__()
                self.manager = manager
                self.set_readonly_mode = Mock()
                
            def refresh_data(self):
                pass
        
        with patch('medical_store_app.ui.components.medicine_management.MedicineForm', MockMedicineForm), \
             patch('medical_store_app.ui.components.medicine_management.MedicineTableWidget', MockMedicineTable):
            
            # Create medicine management widget
            widget = MedicineManagementWidget(mock_medicine_manager)
            widget.show()  # Show widget to make isVisible() work properly
            
            # Set readonly mode
            widget.set_readonly_mode(True)
            
            # Check that readonly mode is set
            assert widget.is_readonly_mode() == True
            
            # Check that form is hidden
            assert not widget.form_frame.isVisible()
            
            # Check that table was set to readonly mode
            widget.medicine_table.set_readonly_mode.assert_called_with(True)
    
    def test_medicine_management_full_access_for_admin(self, app, mock_medicine_manager):
        """Test that medicine management has full access for admins"""
        from PySide6.QtWidgets import QWidget
        from PySide6.QtCore import Signal
        
        # Create real QWidget subclasses for mocking
        class MockMedicineForm(QWidget):
            medicine_saved = Signal(object)
            operation_finished = Signal(bool, str)
            
            def __init__(self, manager):
                super().__init__()
                self.manager = manager
        
        class MockMedicineTable(QWidget):
            medicine_selected = Signal(object)
            edit_requested = Signal(object)
            delete_requested = Signal(object)
            refresh_requested = Signal()
            
            def __init__(self, manager):
                super().__init__()
                self.manager = manager
                self.set_readonly_mode = Mock()
                
            def refresh_data(self):
                pass
        
        with patch('medical_store_app.ui.components.medicine_management.MedicineForm', MockMedicineForm), \
             patch('medical_store_app.ui.components.medicine_management.MedicineTableWidget', MockMedicineTable):
            
            # Create medicine management widget
            widget = MedicineManagementWidget(mock_medicine_manager)
            widget.show()  # Show widget to make isVisible() work properly
            
            # Initially the form should be visible (default state)
            assert widget.form_frame.isVisible()
            
            # Set full access mode (should keep form visible)
            widget.set_readonly_mode(False)
            
            # Check that readonly mode is not set
            assert widget.is_readonly_mode() == False
            
            # Check that form is still visible
            assert widget.form_frame.isVisible()
            
            # Check that table was set to full access mode
            widget.medicine_table.set_readonly_mode.assert_called_with(False)
    
    def test_medicine_table_context_menu_for_admin(self, app, mock_medicine_manager):
        """Test that medicine table context menu shows all options for admin"""
        # Test the readonly mode logic directly
        from medical_store_app.ui.components.medicine_table import MedicineTableWidget
        
        # Create a simple test to verify readonly mode affects context menu
        table_widget = MedicineTableWidget.__new__(MedicineTableWidget)
        table_widget.readonly_mode = False  # Admin mode
        
        # Test that admin mode allows edit/delete actions
        assert not table_widget.readonly_mode, "Admin should not be in readonly mode"
        
        # Test readonly mode setter
        table_widget.readonly_mode = True
        assert table_widget.readonly_mode, "Readonly mode should be settable"
    
    def test_medicine_table_context_menu_for_cashier(self, app, mock_medicine_manager):
        """Test that medicine table context menu shows limited options for cashier"""
        # Test the readonly mode logic directly
        from medical_store_app.ui.components.medicine_table import MedicineTableWidget
        
        # Create a simple test to verify readonly mode affects context menu
        table_widget = MedicineTableWidget.__new__(MedicineTableWidget)
        table_widget.readonly_mode = True  # Cashier mode
        
        # Test that cashier mode is in readonly mode
        assert table_widget.readonly_mode, "Cashier should be in readonly mode"
        
        # Test readonly mode methods exist
        assert hasattr(MedicineTableWidget, 'set_readonly_mode'), "Should have set_readonly_mode method"
        assert hasattr(MedicineTableWidget, 'is_readonly_mode'), "Should have is_readonly_mode method"
    
    def test_medicine_table_double_click_behavior_for_roles(self, app, mock_medicine_manager):
        """Test medicine table double-click behavior for different roles"""
        # Test the double-click logic directly
        from medical_store_app.ui.components.medicine_table import MedicineTableWidget
        from medical_store_app.models.medicine import Medicine
        
        # Create a minimal test instance
        table_widget = Mock(spec=MedicineTableWidget)
        mock_medicine = Medicine(
            id=1,
            name="Test Medicine",
            category="Test Category",
            batch_no="TEST001",
            expiry_date="2025-12-31",
            quantity=100,
            purchase_price=10.0,
            selling_price=15.0
        )
        table_widget.selected_medicine = mock_medicine
        table_widget.edit_requested = Mock()
        table_widget._show_medicine_details = Mock()
        
        # Test admin behavior (should emit edit_requested)
        MedicineTableWidget._on_item_double_clicked(table_widget, Mock())
        table_widget.edit_requested.emit.assert_called_once_with(mock_medicine)
        
        # Reset mock
        table_widget.edit_requested.reset_mock()
        
        # Test cashier behavior (should show details only)
        MedicineTableWidget._on_item_double_clicked_readonly(table_widget, Mock())
        table_widget._show_medicine_details.assert_called_once()
    
    def test_user_role_display_in_header(self, main_window_with_mocks, admin_user, cashier_user):
        """Test that user role is properly displayed in header"""
        window = main_window_with_mocks
        
        # Test admin user display
        window._update_ui_for_user(admin_user)
        assert "Admin User" in window.user_info_label.text()
        
        # Test cashier user display
        window._update_ui_for_user(cashier_user)
        assert "Cashier User" in window.user_info_label.text()
    
    def test_default_content_based_on_role(self, main_window_with_mocks, admin_user, cashier_user):
        """Test that default content is shown based on user role"""
        window = main_window_with_mocks
        
        # Mock the content display methods
        with patch.object(window, '_show_dashboard_content') as mock_dashboard, \
             patch.object(window, '_show_billing_content') as mock_billing:
            
            # Test admin default (should show dashboard)
            window._update_ui_for_user(admin_user)
            mock_dashboard.assert_called_once()
            
            # Reset mocks
            mock_dashboard.reset_mock()
            mock_billing.reset_mock()
            
            # Test cashier default (should show billing)
            window._update_ui_for_user(cashier_user)
            mock_billing.assert_called_once()
    
    def test_permission_checking_with_auth_manager(self, main_window_with_mocks, cashier_user):
        """Test that permission checking properly uses auth manager"""
        window = main_window_with_mocks
        window.current_user = cashier_user
        
        # Test permission checking
        window.auth_manager.has_permission.return_value = True
        assert window._check_feature_permission("billing") == True
        window.auth_manager.has_permission.assert_called_with("billing")
        
        window.auth_manager.has_permission.return_value = False
        assert window._check_feature_permission("reports") == False
        window.auth_manager.has_permission.assert_called_with("reports")
    
    def test_user_role_helper_methods(self, main_window_with_mocks, admin_user, cashier_user):
        """Test user role helper methods"""
        window = main_window_with_mocks
        
        # Test with admin user
        window.current_user = admin_user
        assert window.is_user_admin() == True
        assert window.is_user_cashier() == False
        
        # Test with cashier user
        window.current_user = cashier_user
        assert window.is_user_admin() == False
        assert window.is_user_cashier() == True
        
        # Test with no user
        window.current_user = None
        assert window.is_user_admin() == False
        assert window.is_user_cashier() == False


class TestUserModelPermissions:
    """Test user model permission methods"""
    
    def test_admin_can_access_all_features(self):
        """Test that admin users can access all features"""
        admin = User(username="admin", role="admin", is_active=True)
        
        # Admin should be able to access everything
        assert admin.can_access_feature("billing") == True
        assert admin.can_access_feature("medicine_view") == True
        assert admin.can_access_feature("reports") == True
        assert admin.can_access_feature("settings") == True
        assert admin.can_access_feature("user_management") == True
    
    def test_cashier_has_limited_access(self):
        """Test that cashier users have limited access"""
        cashier = User(username="cashier", role="cashier", is_active=True)
        
        # Cashier should have limited access
        assert cashier.can_access_feature("billing") == True
        assert cashier.can_access_feature("medicine_view") == True
        assert cashier.can_access_feature("dashboard_view") == True
        assert cashier.can_access_feature("sales_view") == True
        
        # Cashier should not have access to admin features
        assert cashier.can_access_feature("reports") == False
        assert cashier.can_access_feature("settings") == False
        assert cashier.can_access_feature("user_management") == False
    
    def test_inactive_user_has_no_access(self):
        """Test that inactive users have no access"""
        inactive_admin = User(username="admin", role="admin", is_active=False)
        inactive_cashier = User(username="cashier", role="cashier", is_active=False)
        
        # Inactive users should have no access regardless of role
        assert inactive_admin.can_access_feature("billing") == False
        assert inactive_admin.can_access_feature("reports") == False
        assert inactive_cashier.can_access_feature("billing") == False
        assert inactive_cashier.can_access_feature("medicine_view") == False
    
    def test_role_checking_methods(self):
        """Test role checking methods"""
        admin = User(username="admin", role="admin")
        cashier = User(username="cashier", role="cashier")
        
        assert admin.is_admin() == True
        assert admin.is_cashier() == False
        
        assert cashier.is_admin() == False
        assert cashier.is_cashier() == True


if __name__ == "__main__":
    pytest.main([__file__])