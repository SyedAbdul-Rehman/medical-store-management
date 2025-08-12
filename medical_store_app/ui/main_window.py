"""
Main application window for Medical Store Management Application
Implements main window with header, sidebar area, and content area layout
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QSizePolicy, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette

from ui.components.sidebar import Sidebar


class MainWindow(QMainWindow):
    """Main application window with header, sidebar area, and content area"""
    
    # Signals
    sidebar_toggle_requested = Signal()
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Window properties
        self.setWindowTitle("Medical Store Management System")
        self.setMinimumSize(1024, 768)
        self.resize(1200, 800)
        
        # Initialize UI components
        self.header_widget = None
        self.sidebar = None
        self.content_area = None
        self.main_layout = None
        
        # Center the window on screen
        self._center_window()
        
        # Set up the main UI layout
        self._setup_ui()
        
        # Apply basic styling
        self._apply_basic_styling()
        
        self.logger.info("Main window initialized with header, sidebar area, and content area")
    
    def _center_window(self):
        """Center the window on the screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def _setup_ui(self):
        """Set up the main user interface layout"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main vertical layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create and add header
        self._create_header()
        self.main_layout.addWidget(self.header_widget)
        
        # Create horizontal layout for sidebar and content
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # Create sidebar
        self._create_sidebar()
        body_layout.addWidget(self.sidebar)
        
        # Create content area
        self._create_content_area()
        body_layout.addWidget(self.content_area)
        
        # Add body layout to main layout
        body_widget = QWidget()
        body_widget.setLayout(body_layout)
        self.main_layout.addWidget(body_widget)
    
    def _create_header(self):
        """Create the header bar with title and controls"""
        self.header_widget = QFrame()
        self.header_widget.setFixedHeight(60)
        self.header_widget.setObjectName("headerWidget")
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Sidebar toggle button (hamburger menu)
        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setFixedSize(40, 40)
        self.sidebar_toggle_btn.setObjectName("sidebarToggleBtn")
        self.sidebar_toggle_btn.clicked.connect(self._on_sidebar_toggle)
        header_layout.addWidget(self.sidebar_toggle_btn)
        
        # Application title
        title_label = QLabel("Medical Store Management System")
        title_label.setObjectName("titleLabel")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        
        # Add stretch to push user info to the right
        header_layout.addStretch()
        
        # User info area (placeholder for now)
        user_info_label = QLabel("Welcome, User")
        user_info_label.setObjectName("userInfoLabel")
        header_layout.addWidget(user_info_label)
        
        # Logout button (placeholder for now)
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setFixedHeight(30)
        header_layout.addWidget(logout_btn)
    
    def _create_sidebar(self):
        """Create the sidebar navigation component"""
        self.sidebar = Sidebar(self)
        
        # Connect sidebar signals
        self.sidebar.menu_item_selected.connect(self._on_menu_item_selected)
        self.sidebar.sidebar_toggled.connect(self._on_sidebar_toggled)
    
    def _create_content_area(self):
        """Create the main content area"""
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome content (placeholder)
        welcome_label = QLabel("Welcome to Medical Store Management System")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setObjectName("welcomeLabel")
        
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        welcome_label.setFont(font)
        
        content_layout.addWidget(welcome_label)
        
        # Status message
        status_label = QLabel("Main window layout initialized successfully.\nSidebar and content areas are ready.")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setObjectName("statusLabel")
        status_label.setStyleSheet("color: #27AE60; font-size: 14px; margin-top: 20px;")
        
        content_layout.addWidget(status_label)
        
        # Add stretch to center content vertically
        content_layout.addStretch()
    
    def _on_sidebar_toggle(self):
        """Handle sidebar toggle button click"""
        if self.sidebar:
            self.sidebar.toggle_sidebar()
            self.sidebar_toggle_requested.emit()
    
    def _on_menu_item_selected(self, item_key: str):
        """Handle menu item selection from sidebar"""
        self.logger.info(f"Menu item selected: {item_key}")
        # TODO: Switch content area based on selected item
        # This will be implemented when content widgets are created
        
        # Update content area with selected item info for now
        if hasattr(self, 'content_area'):
            # Find and update the welcome label
            labels = self.content_area.findChildren(QLabel)
            for label in labels:
                if "Welcome" in label.text():
                    label.setText(f"Welcome to Medical Store Management System\nSelected: {item_key.title()}")
                    break
    
    def _on_sidebar_toggled(self, is_expanded: bool):
        """Handle sidebar toggle state change"""
        self.logger.info(f"Sidebar {'expanded' if is_expanded else 'collapsed'}")
        # Additional logic can be added here if needed
    
    def _apply_basic_styling(self):
        """Apply basic styling to the main window"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #F8F9FA;
            }
            
            /* Header */
            #headerWidget {
                background-color: #2D9CDB;
                border-bottom: 2px solid #1E88E5;
            }
            
            #titleLabel {
                color: white;
            }
            
            #userInfoLabel {
                color: white;
                font-size: 12px;
            }
            
            #sidebarToggleBtn {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            
            #sidebarToggleBtn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            #logoutBtn {
                background-color: #E74C3C;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
            }
            
            #logoutBtn:hover {
                background-color: #C0392B;
            }
            
            /* Sidebar styling is handled by the Sidebar component */
            
            /* Content Area */
            #contentArea {
                background-color: #FFFFFF;
            }
            
            #welcomeLabel {
                color: #333333;
            }
            
            #statusLabel {
                color: #27AE60;
            }
        """)
    
    def get_content_area(self):
        """Get the content area widget for adding content"""
        return self.content_area
    
    def get_sidebar(self):
        """Get the sidebar widget"""
        return self.sidebar
    
    def get_header_widget(self):
        """Get the header widget"""
        return self.header_widget
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.info("Application closing...")
        event.accept()