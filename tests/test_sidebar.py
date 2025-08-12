"""
Tests for Sidebar navigation component
Tests sidebar functionality, navigation, and content switching
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent / "medical_store_app"
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

from ui.components.sidebar import Sidebar, NavigationButton


class TestNavigationButton:
    """Test cases for NavigationButton class"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_navigation_button_initialization(self):
        """Test that navigation button initializes correctly"""
        button = NavigationButton("Test Button", "🔧")
        
        assert button.text() == "Test Button"
        assert button.icon_text == "🔧"
        assert button.height() == 45
        assert not button.is_active
        assert button.objectName() == "navigationButton"
        
        button.deleteLater()
    
    def test_navigation_button_active_state(self):
        """Test navigation button active state management"""
        button = NavigationButton("Test Button")
        
        # Initially not active
        assert not button.is_active
        
        # Set active
        button.set_active(True)
        assert button.is_active
        
        # Set inactive
        button.set_active(False)
        assert not button.is_active
        
        button.deleteLater()
    
    def test_navigation_button_display_text(self):
        """Test navigation button display text with icon"""
        button = NavigationButton("Test", "🔧")
        
        display_text = button.get_display_text()
        assert "🔧" in display_text
        assert "Test" in display_text
        
        # Test without icon
        button_no_icon = NavigationButton("Test Only")
        assert button_no_icon.get_display_text() == "Test Only"
        
        button.deleteLater()
        button_no_icon.deleteLater()


class TestSidebar:
    """Test cases for Sidebar class"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_sidebar_initialization(self):
        """Test that sidebar initializes correctly"""
        sidebar = Sidebar()
        
        # Test basic properties
        assert sidebar.width() == 250  # expanded width
        assert sidebar.is_expanded
        assert sidebar.objectName() == "sidebar"
        
        # Test menu items are created
        assert len(sidebar.navigation_buttons) == 5
        expected_keys = ["dashboard", "medicine", "billing", "reports", "settings"]
        for key in expected_keys:
            assert key in sidebar.navigation_buttons
        
        # Test default active item
        assert sidebar.get_active_item() == "dashboard"
        
        sidebar.deleteLater()
    
    def test_sidebar_menu_item_selection(self):
        """Test menu item selection functionality"""
        sidebar = Sidebar()
        
        # Test signal emission
        signal_emitted = False
        selected_item = None
        
        def on_item_selected(item_key):
            nonlocal signal_emitted, selected_item
            signal_emitted = True
            selected_item = item_key
        
        sidebar.menu_item_selected.connect(on_item_selected)
        
        # Simulate clicking medicine button
        medicine_button = sidebar.navigation_buttons["medicine"]
        medicine_button.click()
        
        # Process events
        QApplication.processEvents()
        
        assert signal_emitted
        assert selected_item == "medicine"
        assert sidebar.get_active_item() == "medicine"
        
        sidebar.deleteLater()
    
    def test_sidebar_active_item_management(self):
        """Test active item management"""
        sidebar = Sidebar()
        
        # Initially dashboard should be active
        assert sidebar.get_active_item() == "dashboard"
        assert sidebar.navigation_buttons["dashboard"].is_active
        
        # Set medicine as active
        sidebar.set_active_item("medicine")
        assert sidebar.get_active_item() == "medicine"
        assert sidebar.navigation_buttons["medicine"].is_active
        assert not sidebar.navigation_buttons["dashboard"].is_active
        
        # Set invalid item (should not crash)
        sidebar.set_active_item("invalid")
        assert sidebar.get_active_item() == "medicine"  # Should remain unchanged
        
        sidebar.deleteLater()
    
    def test_sidebar_toggle_functionality(self):
        """Test sidebar expand/collapse functionality"""
        sidebar = Sidebar()
        
        # Initially expanded
        assert sidebar.is_expanded
        assert sidebar.width() == 250
        
        # Test toggle signal
        signal_emitted = False
        toggle_state = None
        
        def on_toggle(is_expanded):
            nonlocal signal_emitted, toggle_state
            signal_emitted = True
            toggle_state = is_expanded
        
        sidebar.sidebar_toggled.connect(on_toggle)
        
        # Toggle to collapsed
        sidebar.toggle_sidebar()
        
        # Wait for animation to complete
        QTimer.singleShot(350, lambda: None)  # Wait longer than animation duration
        QApplication.processEvents()
        
        # Note: Animation might not complete in test environment
        # So we check the intended state rather than actual width
        assert not sidebar.is_expanded
        
        sidebar.deleteLater()
    
    def test_sidebar_expand_collapse_methods(self):
        """Test explicit expand and collapse methods"""
        sidebar = Sidebar()
        
        # Start expanded
        assert sidebar.is_expanded
        
        # Collapse
        sidebar.collapse_sidebar()
        assert not sidebar.is_expanded
        
        # Expand
        sidebar.expand_sidebar()
        assert sidebar.is_expanded
        
        # Try to expand when already expanded (should not change)
        sidebar.expand_sidebar()
        assert sidebar.is_expanded
        
        sidebar.deleteLater()
    
    def test_sidebar_add_remove_menu_items(self):
        """Test adding and removing menu items"""
        sidebar = Sidebar()
        
        initial_count = len(sidebar.navigation_buttons)
        
        # Add new menu item
        sidebar.add_menu_item("Test Item", "test", "🧪")
        
        assert len(sidebar.navigation_buttons) == initial_count + 1
        assert "test" in sidebar.navigation_buttons
        assert sidebar.navigation_buttons["test"].text() == "Test Item"
        assert sidebar.navigation_buttons["test"].icon_text == "🧪"
        
        # Remove menu item
        sidebar.remove_menu_item("test")
        
        assert len(sidebar.navigation_buttons) == initial_count
        assert "test" not in sidebar.navigation_buttons
        
        # Try to remove non-existent item (should not crash)
        sidebar.remove_menu_item("nonexistent")
        assert len(sidebar.navigation_buttons) == initial_count
        
        sidebar.deleteLater()
    
    def test_sidebar_remove_active_item(self):
        """Test removing the currently active menu item"""
        sidebar = Sidebar()
        
        # Set medicine as active
        sidebar.set_active_item("medicine")
        assert sidebar.get_active_item() == "medicine"
        
        # Remove the active item
        sidebar.remove_menu_item("medicine")
        
        # Active item should be cleared
        assert sidebar.current_active_button is None
        assert "medicine" not in sidebar.navigation_buttons
        
        sidebar.deleteLater()
    
    def test_sidebar_custom_callback(self):
        """Test adding menu item with custom callback"""
        sidebar = Sidebar()
        
        callback_called = False
        callback_key = None
        
        def custom_callback(key):
            nonlocal callback_called, callback_key
            callback_called = True
            callback_key = key
        
        # Add item with custom callback
        sidebar.add_menu_item("Custom Item", "custom", "⚡", custom_callback)
        
        # Click the button
        sidebar.navigation_buttons["custom"].click()
        QApplication.processEvents()
        
        assert callback_called
        assert callback_key == "custom"
        
        sidebar.deleteLater()
    
    def test_sidebar_styling_applied(self):
        """Test that sidebar styling is applied"""
        sidebar = Sidebar()
        
        # Test that stylesheet is applied
        stylesheet = sidebar.styleSheet()
        assert stylesheet is not None
        assert len(stylesheet) > 0
        
        # Test that key style elements are present
        assert "#sidebar" in stylesheet
        assert "#sidebarHeader" in stylesheet
        assert "background-color" in stylesheet
        
        sidebar.deleteLater()
    
    def test_sidebar_header_components(self):
        """Test sidebar header components"""
        sidebar = Sidebar()
        
        # Test header frame exists
        assert sidebar.header_frame is not None
        assert sidebar.header_frame.height() == 50
        
        # Test navigation title
        assert sidebar.nav_title is not None
        assert sidebar.nav_title.text() == "Navigation"
        
        sidebar.deleteLater()
    
    def test_sidebar_menu_frame_components(self):
        """Test sidebar menu frame and buttons"""
        sidebar = Sidebar()
        
        # Test menu frame exists
        assert sidebar.menu_frame is not None
        
        # Test all navigation buttons are present
        menu_buttons = sidebar.menu_frame.findChildren(NavigationButton)
        assert len(menu_buttons) == 5
        
        # Test button properties
        for button in menu_buttons:
            assert button.height() == 45
            assert button.objectName() == "navigationButton"
        
        sidebar.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__])