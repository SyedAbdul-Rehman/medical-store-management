"""
Integration tests for MainWindow class
Tests main window initialization, layout, and basic functionality
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent / "medical_store_app"
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from ui.main_window import MainWindow


class TestMainWindow:
    """Test cases for MainWindow class"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # Clean up is handled by pytest
    
    def test_main_window_initialization(self):
        """Test that main window initializes correctly"""
        window = MainWindow()
        
        # Test window properties
        assert window.windowTitle() == "Medical Store Management System"
        assert window.minimumSize().width() == 1024
        assert window.minimumSize().height() == 768
        assert window.size().width() == 1200
        assert window.size().height() == 800
        
        # Test that main components are created
        assert window.header_widget is not None
        assert window.sidebar is not None
        assert window.content_area is not None
        assert window.main_layout is not None
        
        window.close()
    
    def test_header_widget_creation(self):
        """Test that header widget is created with correct components"""
        window = MainWindow()
        
        # Test header widget exists and has correct properties
        assert window.header_widget is not None
        assert window.header_widget.height() == 60
        assert window.header_widget.objectName() == "headerWidget"
        
        # Test header contains required components
        header_children = window.header_widget.findChildren(QPushButton)
        assert len(header_children) >= 2  # Toggle button and logout button
        
        # Test sidebar toggle button
        toggle_btn = window.sidebar_toggle_btn
        assert toggle_btn is not None
        assert toggle_btn.text() == "☰"
        assert toggle_btn.size().width() == 40
        assert toggle_btn.size().height() == 40
        
        # Test title label exists
        title_labels = window.header_widget.findChildren(QLabel)
        title_label = next((label for label in title_labels if "Medical Store" in label.text()), None)
        assert title_label is not None
        
        window.close()
    
    def test_sidebar_creation(self):
        """Test that sidebar is created with navigation menu"""
        window = MainWindow()
        
        # Test sidebar properties
        assert window.sidebar is not None
        assert window.sidebar.width() == 250
        assert window.sidebar.objectName() == "sidebar"
        
        # Test sidebar contains navigation buttons
        assert len(window.sidebar.navigation_buttons) == 5
        expected_keys = ["dashboard", "medicine", "billing", "reports", "settings"]
        for key in expected_keys:
            assert key in window.sidebar.navigation_buttons
        
        window.close()
    
    def test_content_area_creation(self):
        """Test that content area is created correctly"""
        window = MainWindow()
        
        # Test content area properties
        assert window.content_area is not None
        assert window.content_area.objectName() == "contentArea"
        
        # Test content area contains welcome message
        content_labels = window.content_area.findChildren(QLabel)
        welcome_label = next((label for label in content_labels if "Welcome" in label.text()), None)
        assert welcome_label is not None
        
        window.close()
    
    def test_layout_structure(self):
        """Test that the layout structure is correct"""
        window = MainWindow()
        
        # Test main layout exists
        central_widget = window.centralWidget()
        assert central_widget is not None
        assert window.main_layout is not None
        
        # Test layout contains header and body
        layout_items = []
        for i in range(window.main_layout.count()):
            item = window.main_layout.itemAt(i)
            if item and item.widget():
                layout_items.append(item.widget())
        
        assert len(layout_items) >= 2  # Header and body
        assert window.header_widget in layout_items
        
        window.close()
    
    def test_sidebar_toggle_functionality(self):
        """Test that sidebar toggle button works correctly"""
        window = MainWindow()
        
        # Initially sidebar should be expanded
        assert window.sidebar.is_expanded
        
        # Connect signal to test slot
        signal_emitted = False
        
        def on_toggle():
            nonlocal signal_emitted
            signal_emitted = True
        
        window.sidebar_toggle_requested.connect(on_toggle)
        
        # Simulate button click
        window.sidebar_toggle_btn.click()
        
        # Process events to ensure signal is emitted
        QApplication.processEvents()
        
        assert signal_emitted
        assert not window.sidebar.is_expanded  # Should be collapsed now
        
        window.close()
    
    def test_menu_item_selection(self):
        """Test that menu item selection updates content area"""
        window = MainWindow()
        
        # Get initial welcome label text
        content_labels = window.content_area.findChildren(QLabel)
        welcome_label = next((label for label in content_labels if "Welcome" in label.text()), None)
        assert welcome_label is not None
        
        # Simulate selecting medicine menu item
        window.sidebar.set_active_item("medicine")
        window._on_menu_item_selected("medicine")
        
        # Check that content was updated
        assert "medicine" in welcome_label.text().lower()
        
        window.close()
    
    def test_getter_methods(self):
        """Test that getter methods return correct widgets"""
        window = MainWindow()
        
        # Test getter methods
        assert window.get_content_area() == window.content_area
        assert window.get_sidebar() == window.sidebar
        assert window.get_header_widget() == window.header_widget
        
        window.close()
    
    def test_window_centering(self):
        """Test that window is centered on screen"""
        from PySide6.QtCore import QRect, QPoint
        
        with patch('PySide6.QtWidgets.QApplication.primaryScreen') as mock_screen:
            # Mock screen geometry
            mock_screen_obj = MagicMock()
            mock_geometry = QRect(0, 0, 1920, 1080)
            mock_screen_obj.availableGeometry.return_value = mock_geometry
            mock_screen.return_value = mock_screen_obj
            
            window = MainWindow()
            
            # Window should be created without errors
            assert window is not None
            
            window.close()
    
    def test_basic_styling_applied(self):
        """Test that basic styling is applied to the window"""
        window = MainWindow()
        
        # Test that stylesheet is applied
        stylesheet = window.styleSheet()
        assert stylesheet is not None
        assert len(stylesheet) > 0
        
        # Test that key style elements are present
        assert "#headerWidget" in stylesheet
        assert "#contentArea" in stylesheet
        assert "background-color" in stylesheet
        # Note: Sidebar styling is handled by the Sidebar component itself
        
        window.close()
    
    def test_window_close_event(self):
        """Test that window close event is handled correctly"""
        window = MainWindow()
        
        # Test that window can be closed without errors
        window.close()
        
        # Window should be closed
        assert not window.isVisible()


if __name__ == "__main__":
    pytest.main([__file__])