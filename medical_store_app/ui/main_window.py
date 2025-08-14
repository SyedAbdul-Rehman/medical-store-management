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

from .components.sidebar import Sidebar
from .components.medicine_management import MedicineManagementWidget
from .components.billing_widget import BillingWidget
from ..managers.medicine_manager import MedicineManager
from ..managers.sales_manager import SalesManager
from ..repositories.medicine_repository import MedicineRepository
from ..repositories.sales_repository import SalesRepository
from ..config.database import DatabaseManager


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
        
        # Initialize managers and repositories
        self.db_manager = DatabaseManager()
        self.medicine_repository = MedicineRepository(self.db_manager)
        self.sales_repository = SalesRepository(self.db_manager)
        self.medicine_manager = MedicineManager(self.medicine_repository)
        self.sales_manager = SalesManager(self.sales_repository, self.medicine_repository)
        
        # Content widgets
        self.medicine_management_widget = None
        self.billing_widget = None
        self.current_content_widget = None
        
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
        
        # Create layout for content area
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Show dashboard by default
        self._show_dashboard_content()
    
    def _on_sidebar_toggle(self):
        """Handle sidebar toggle button click"""
        if self.sidebar:
            self.sidebar.toggle_sidebar()
            self.sidebar_toggle_requested.emit()
    
    def _on_menu_item_selected(self, item_key: str):
        """Handle menu item selection from sidebar"""
        self.logger.info(f"Menu item selected: {item_key}")
        
        # Switch content based on selected item
        if item_key == "dashboard":
            self._show_dashboard_content()
        elif item_key == "medicine":
            self._show_medicine_management()
        elif item_key == "billing":
            self._show_billing_content()
        elif item_key == "reports":
            self._show_reports_content()
        elif item_key == "settings":
            self._show_settings_content()
        else:
            self.logger.warning(f"Unknown menu item: {item_key}")
            self._show_dashboard_content()
    
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
    
    def _clear_content_area(self):
        """Clear the current content from content area"""
        if self.current_content_widget:
            self.content_layout.removeWidget(self.current_content_widget)
            self.current_content_widget.hide()
            self.current_content_widget = None
    
    def _show_dashboard_content(self):
        """Show dashboard content"""
        self._clear_content_area()
        
        # Create dashboard widget
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome content
        welcome_label = QLabel("Welcome to Medical Store Management System")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setObjectName("welcomeLabel")
        
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        welcome_label.setFont(font)
        
        dashboard_layout.addWidget(welcome_label)
        
        # Status message
        status_label = QLabel("Select 'Medicine Management' from the sidebar to manage your medicine inventory.")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setObjectName("statusLabel")
        status_label.setStyleSheet("color: #27AE60; font-size: 14px; margin-top: 20px;")
        
        dashboard_layout.addWidget(status_label)
        dashboard_layout.addStretch()
        
        # Add to content area
        self.content_layout.addWidget(dashboard_widget)
        self.current_content_widget = dashboard_widget
        dashboard_widget.show()
        
        self.logger.info("Dashboard content displayed")
    
    def _show_medicine_management(self):
        """Show medicine management content"""
        self._clear_content_area()
        
        # Create medicine management widget if not exists
        if not self.medicine_management_widget:
            try:
                self.medicine_management_widget = MedicineManagementWidget(self.medicine_manager)
                
                # Connect signals for logging
                self.medicine_management_widget.medicine_added.connect(
                    lambda medicine: self.logger.info(f"Medicine added: {medicine.name}")
                )
                self.medicine_management_widget.medicine_updated.connect(
                    lambda medicine: self.logger.info(f"Medicine updated: {medicine.name}")
                )
                self.medicine_management_widget.medicine_deleted.connect(
                    lambda medicine_id: self.logger.info(f"Medicine deleted: ID {medicine_id}")
                )
                
                self.logger.info("Medicine management widget created successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to create medicine management widget: {e}")
                self._show_error_content("Medicine Management", str(e))
                return
        
        # Add to content area
        self.content_layout.addWidget(self.medicine_management_widget)
        self.current_content_widget = self.medicine_management_widget
        self.medicine_management_widget.show()
        
        # Refresh data
        try:
            self.medicine_management_widget.refresh_data()
        except Exception as e:
            self.logger.error(f"Failed to refresh medicine data: {e}")
        
        self.logger.info("Medicine management content displayed")
    
    def _show_billing_content(self):
        """Show billing content"""
        self._clear_content_area()
        
        # Create billing widget if not exists
        if not self.billing_widget:
            try:
                self.billing_widget = BillingWidget(self.medicine_manager, self.sales_manager)
                
                # Connect signals for logging
                self.billing_widget.cart_widget.cart_updated.connect(
                    lambda: self.logger.debug("Cart updated")
                )
                
                self.logger.info("Billing widget created successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to create billing widget: {e}")
                self._show_error_content("Billing System", str(e))
                return
        
        # Add to content area
        self.content_layout.addWidget(self.billing_widget)
        self.current_content_widget = self.billing_widget
        self.billing_widget.show()
        
        # Refresh display
        try:
            self.billing_widget.refresh_display()
        except Exception as e:
            self.logger.error(f"Failed to refresh billing display: {e}")
        
        self.logger.info("Billing content displayed")
    
    def _show_reports_content(self):
        """Show reports content (placeholder)"""
        self._show_placeholder_content("Reports", "Reports functionality will be implemented in a future update.")
    
    def _show_settings_content(self):
        """Show settings content (placeholder)"""
        self._show_placeholder_content("Settings", "Settings functionality will be implemented in a future update.")
    
    def _show_placeholder_content(self, title: str, message: str):
        """Show placeholder content for unimplemented features"""
        self._clear_content_area()
        
        # Create placeholder widget
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("placeholderTitle")
        
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        
        placeholder_layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setObjectName("placeholderMessage")
        message_label.setStyleSheet("color: #666666; font-size: 14px; margin-top: 20px;")
        message_label.setWordWrap(True)
        
        placeholder_layout.addWidget(message_label)
        placeholder_layout.addStretch()
        
        # Add to content area
        self.content_layout.addWidget(placeholder_widget)
        self.current_content_widget = placeholder_widget
        placeholder_widget.show()
        
        self.logger.info(f"Placeholder content displayed: {title}")
    
    def _show_error_content(self, title: str, error_message: str):
        """Show error content when something fails to load"""
        self._clear_content_area()
        
        # Create error widget
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setContentsMargins(20, 20, 20, 20)
        
        # Error title
        title_label = QLabel(f"Error Loading {title}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("errorTitle")
        title_label.setStyleSheet("color: #E74C3C; font-size: 18px; font-weight: bold;")
        
        error_layout.addWidget(title_label)
        
        # Error message
        message_label = QLabel(f"An error occurred while loading the {title.lower()} module:\n\n{error_message}")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setObjectName("errorMessage")
        message_label.setStyleSheet("color: #666666; font-size: 14px; margin-top: 20px;")
        message_label.setWordWrap(True)
        
        error_layout.addWidget(message_label)
        error_layout.addStretch()
        
        # Add to content area
        self.content_layout.addWidget(error_widget)
        self.current_content_widget = error_widget
        error_widget.show()
        
        self.logger.error(f"Error content displayed: {title} - {error_message}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.info("Application closing...")
        event.accept()