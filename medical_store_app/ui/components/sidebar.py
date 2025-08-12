"""
Sidebar navigation component for Medical Store Management Application
Implements collapsible sidebar with navigation menu items and content switching
"""

import logging
from typing import Dict, Callable, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QSizePolicy, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, Signal, QEasingCurve, QPropertyAnimation, QRect, Property
from PySide6.QtGui import QFont, QIcon


class NavigationButton(QPushButton):
    """Custom navigation button with enhanced styling and state management"""
    
    def __init__(self, text: str, icon_text: str = "", parent=None):
        """Initialize navigation button"""
        super().__init__(parent)
        self.original_text = text  # Store original text for toggle functionality
        self.setText(text)
        self.icon_text = icon_text
        self.is_active = False
        self.setFixedHeight(45)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setObjectName("navigationButton")
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up button styling"""
        self.setStyleSheet("""
            QPushButton#navigationButton {
                background-color: transparent;
                border: none;
                border-bottom: 1px solid #F1F3F4;
                color: #333333;
                font-size: 13px;
                font-weight: 500;
                padding: 12px 20px;
                text-align: left;
            }
            
            QPushButton#navigationButton:hover {
                background-color: #F1F3F4;
                color: #2D9CDB;
            }
            
            QPushButton#navigationButton:pressed {
                background-color: #E3F2FD;
            }
            
            QPushButton#navigationButton[active="true"] {
                background-color: #E3F2FD;
                color: #2D9CDB;
                border-left: 3px solid #2D9CDB;
                font-weight: 600;
            }
        """)
    
    def set_active(self, active: bool):
        """Set button active state"""
        self.is_active = active
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def get_display_text(self) -> str:
        """Get the display text with icon if available"""
        if self.icon_text:
            return f"{self.icon_text}  {self.original_text}"
        return self.original_text
    
    def get_original_text(self) -> str:
        """Get the original full text"""
        return self.original_text
    
    def get_icon_text(self) -> str:
        """Get just the icon text"""
        return self.icon_text


class Sidebar(QWidget):
    """Sidebar navigation component with collapsible functionality"""
    
    # Signals
    menu_item_selected = Signal(str)  # Emitted when a menu item is selected
    sidebar_toggled = Signal(bool)    # Emitted when sidebar is expanded/collapsed
    
    def __init__(self, parent=None):
        """Initialize sidebar component"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Sidebar state
        self.is_expanded = True
        self.expanded_width = 250
        self.collapsed_width = 60
        self.current_active_button = None
        
        # Menu items configuration
        self.menu_items = [
            {"name": "Dashboard", "icon": "📊", "key": "dashboard"},
            {"name": "Medicine Management", "icon": "💊", "key": "medicine"},
            {"name": "Billing System", "icon": "🧾", "key": "billing"},
            {"name": "Reports", "icon": "📈", "key": "reports"},
            {"name": "Settings", "icon": "⚙️", "key": "settings"}
        ]
        
        # Store navigation buttons
        self.navigation_buttons: Dict[str, NavigationButton] = {}
        
        # Animation for expand/collapse
        self.animation = None
        
        # Set initial properties
        self.setFixedWidth(self.expanded_width)
        self.setObjectName("sidebar")
        
        # Set up UI
        self._setup_ui()
        self._apply_styling()
        
        self.logger.info("Sidebar navigation component initialized")
    
    def _setup_ui(self):
        """Set up the sidebar user interface"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create header section
        self._create_header()
        
        # Create navigation menu
        self._create_navigation_menu()
        
        # Add stretch to push items to top
        self.main_layout.addStretch()
    
    def _create_header(self):
        """Create sidebar header with title"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("sidebarHeader")
        self.header_frame.setFixedHeight(50)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Navigation title
        self.nav_title = QLabel("Navigation")
        self.nav_title.setObjectName("navTitle")
        self.nav_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.nav_title.setFont(font)
        
        header_layout.addWidget(self.nav_title)
        header_layout.addStretch()
        
        self.main_layout.addWidget(self.header_frame)
    
    def _create_navigation_menu(self):
        """Create navigation menu with buttons"""
        # Menu container
        self.menu_frame = QFrame()
        self.menu_frame.setObjectName("menuFrame")
        
        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        # Create navigation buttons
        for item in self.menu_items:
            button = NavigationButton(
                text=item["name"],
                icon_text=item["icon"],
                parent=self.menu_frame
            )
            
            # Connect button click to handler
            button.clicked.connect(lambda checked, key=item["key"]: self._on_menu_item_clicked(key))
            
            # Store button reference
            self.navigation_buttons[item["key"]] = button
            
            # Add to layout
            menu_layout.addWidget(button)
        
        self.main_layout.addWidget(self.menu_frame)
        
        # Set default active item (dashboard)
        self.set_active_item("dashboard")
    
    def _on_menu_item_clicked(self, item_key: str):
        """Handle menu item click"""
        self.logger.info(f"Menu item clicked: {item_key}")
        
        # Set active item
        self.set_active_item(item_key)
        
        # Emit signal
        self.menu_item_selected.emit(item_key)
    
    def set_active_item(self, item_key: str):
        """Set the active menu item"""
        # Only proceed if the item exists
        if item_key in self.navigation_buttons:
            # Deactivate current active button
            if self.current_active_button:
                self.current_active_button.set_active(False)
            
            # Activate new button
            button = self.navigation_buttons[item_key]
            button.set_active(True)
            self.current_active_button = button
            self.logger.info(f"Active menu item set to: {item_key}")
        else:
            self.logger.warning(f"Attempted to set invalid menu item: {item_key}")
    
    def toggle_sidebar(self):
        """Toggle sidebar expanded/collapsed state"""
        self.is_expanded = not self.is_expanded
        target_width = self.expanded_width if self.is_expanded else self.collapsed_width
        
        # Create animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Update fixed width as well
        def update_width():
            self.setFixedWidth(target_width)
            self._update_content_visibility()
            self.sidebar_toggled.emit(self.is_expanded)
        
        self.animation.finished.connect(update_width)
        self.animation.start()
        
        self.logger.info(f"Sidebar toggled: {'expanded' if self.is_expanded else 'collapsed'}")
    
    def _update_content_visibility(self):
        """Update content visibility based on sidebar state"""
        # Show/hide text labels based on expanded state
        if self.is_expanded:
            # Expanded state: show navigation title and full text labels
            self.nav_title.show()
            for button in self.navigation_buttons.values():
                # Restore original full text
                button.setText(button.get_original_text())
        else:
            # Collapsed state: hide navigation title and show only icons
            self.nav_title.hide()
            for button in self.navigation_buttons.values():
                # Show only icon in collapsed state
                if button.get_icon_text():
                    button.setText(button.get_icon_text())
                else:
                    # Fallback to first character if no icon available
                    button.setText(button.get_original_text()[:1])
    
    def _apply_styling(self):
        """Apply styling to the sidebar"""
        self.setStyleSheet("""
            /* Sidebar Container */
            #sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E1E5E9;
            }
            
            /* Sidebar Header */
            #sidebarHeader {
                background-color: #F8F9FA;
                border-bottom: 1px solid #E1E5E9;
            }
            
            #navTitle {
                color: #333333;
                font-weight: 600;
            }
            
            /* Menu Frame */
            #menuFrame {
                background-color: transparent;
            }
        """)
    
    def get_active_item(self) -> Optional[str]:
        """Get the currently active menu item key"""
        for key, button in self.navigation_buttons.items():
            if button.is_active:
                return key
        return None
    
    def add_menu_item(self, name: str, key: str, icon: str = "", callback: Optional[Callable] = None):
        """Add a new menu item to the sidebar"""
        # Create new button
        button = NavigationButton(text=name, icon_text=icon, parent=self.menu_frame)
        
        # Connect callback if provided
        if callback:
            button.clicked.connect(lambda: callback(key))
        else:
            button.clicked.connect(lambda checked, k=key: self._on_menu_item_clicked(k))
        
        # Store button reference
        self.navigation_buttons[key] = button
        
        # Add to layout
        self.menu_frame.layout().addWidget(button)
        
        # Update button text based on current sidebar state
        if not self.is_expanded:
            button.setText(button.get_icon_text() if button.get_icon_text() else button.get_original_text()[:1])
        
        self.logger.info(f"Menu item added: {name} ({key})")
    
    def remove_menu_item(self, key: str):
        """Remove a menu item from the sidebar"""
        if key in self.navigation_buttons:
            button = self.navigation_buttons[key]
            
            # Remove from layout and delete
            self.menu_frame.layout().removeWidget(button)
            button.deleteLater()
            
            # Remove from dictionary
            del self.navigation_buttons[key]
            
            # If this was the active item, clear active state
            if self.current_active_button == button:
                self.current_active_button = None
            
            self.logger.info(f"Menu item removed: {key}")
    
    def is_sidebar_expanded(self) -> bool:
        """Check if sidebar is currently expanded"""
        return self.is_expanded
    
    def expand_sidebar(self):
        """Expand the sidebar if it's collapsed"""
        if not self.is_expanded:
            self.toggle_sidebar()
    
    def collapse_sidebar(self):
        """Collapse the sidebar if it's expanded"""
        if self.is_expanded:
            self.toggle_sidebar()