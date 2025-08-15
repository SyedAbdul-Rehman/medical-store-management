"""
Main application window for Medical Store Management Application
Implements main window with header, sidebar area, and content area layout
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QSizePolicy, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette

from .components.sidebar import Sidebar
from .components.dashboard import DashboardWidget
from .components.medicine_management import MedicineManagementWidget
from .components.billing_widget import BillingWidget
from .dialogs.login_dialog import LoginManager
from ..managers.medicine_manager import MedicineManager
from ..managers.sales_manager import SalesManager
from ..managers.auth_manager import AuthManager
from ..repositories.medicine_repository import MedicineRepository
from ..repositories.sales_repository import SalesRepository
from ..repositories.user_repository import UserRepository
from ..config.database import DatabaseManager
from ..models.user import User


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
        self.user_repository = UserRepository(self.db_manager)
        self.medicine_manager = MedicineManager(self.medicine_repository)
        self.sales_manager = SalesManager(self.sales_repository, self.medicine_repository)
        self.auth_manager = AuthManager(self.user_repository)
        self.login_manager = LoginManager(self.auth_manager, self)
        
        # Current user
        self.current_user: Optional[User] = None
        
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
    
    def start_application(self):
        """Start the application with login process"""
        # Check if this is first run and show startup info
        self._check_first_run_and_show_startup_info()
        
        # Show login dialog
        success, user = self.login_manager.show_login_dialog()
        
        if success and user:
            self.current_user = user
            self._update_ui_for_user(user)
            self.logger.info(f"User logged in successfully: {user.username}")
            return True
        else:
            self.logger.info("Login cancelled or failed")
            return False
    
    def _check_first_run_and_show_startup_info(self):
        """Check if this is first run and show startup information"""
        try:
            # Check if there are any users in the database (indicating first run)
            users = self.auth_manager.get_all_users_for_startup()
            
            # If we have exactly 2 users (the default admin and cashier), show startup info
            if len(users) == 2:
                # Check if both are the default users
                usernames = [user.username for user in users]
                if 'admin' in usernames and 'cashier' in usernames:
                    from .dialogs.startup_info_dialog import StartupInfoDialog
                    StartupInfoDialog.show_startup_info(self)
                    
        except Exception as e:
            self.logger.error(f"Error checking first run: {e}")
            # Continue anyway, don't block the application
    
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
        
        # Logout button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setFixedHeight(30)
        self.logout_btn.clicked.connect(self._on_logout_clicked)
        header_layout.addWidget(self.logout_btn)
        
        # Store user info label reference for updates
        self.user_info_label = user_info_label
    
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
        """Show dashboard content with overview cards and metrics"""
        self._clear_content_area()
        
        try:
            # Create dashboard widget with managers
            dashboard_widget = DashboardWidget(
                medicine_manager=self.medicine_manager,
                sales_manager=self.sales_manager
            )
            
            # Connect navigation signals
            dashboard_widget.navigate_to.connect(self._handle_dashboard_navigation)
            
            # Add to content area
            self.content_layout.addWidget(dashboard_widget)
            self.current_content_widget = dashboard_widget
            dashboard_widget.show()
            
            self.logger.info("Dashboard content displayed with overview cards")
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {str(e)}")
            # Fallback to basic dashboard
            self._show_basic_dashboard_content()
    
    def _show_basic_dashboard_content(self):
        """Show basic dashboard content as fallback"""
        # Create basic dashboard widget
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
        
        # User info
        if self.current_user:
            user_info_label = QLabel(f"Logged in as: {self.current_user.get_display_name()} ({self.current_user.get_role_display()})")
            user_info_label.setAlignment(Qt.AlignCenter)
            user_info_label.setStyleSheet("color: #2D9CDB; font-size: 16px; margin-top: 10px; font-weight: bold;")
            dashboard_layout.addWidget(user_info_label)
        
        # Status message based on user role
        if self.current_user and self.current_user.is_admin():
            status_label = QLabel("As an administrator, you have access to all features including user management.")
        elif self.current_user and self.current_user.is_cashier():
            status_label = QLabel("As a cashier, you can access billing and view medicine inventory.")
        else:
            status_label = QLabel("Select options from the sidebar to navigate the application.")
            
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setObjectName("statusLabel")
        status_label.setStyleSheet("color: #27AE60; font-size: 14px; margin-top: 20px;")
        status_label.setWordWrap(True)
        
        dashboard_layout.addWidget(status_label)
        
        # Quick actions based on role
        if self.current_user:
            actions_label = QLabel("Quick Actions:")
            actions_label.setAlignment(Qt.AlignCenter)
            actions_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold; margin-top: 30px;")
            dashboard_layout.addWidget(actions_label)
            
            if self.current_user.is_admin():
                quick_actions = "• Manage Users (User Management)\n• Add/Edit Medicines (Medicine Management)\n• Process Sales (Billing System)\n• View Reports"
            else:
                quick_actions = "• Process Sales (Billing System)\n• View Medicine Inventory (Medicine Management)"
            
            actions_detail_label = QLabel(quick_actions)
            actions_detail_label.setAlignment(Qt.AlignCenter)
            actions_detail_label.setStyleSheet("color: #666666; font-size: 12px; margin-top: 10px;")
            dashboard_layout.addWidget(actions_detail_label)
        
        dashboard_layout.addStretch()
        
        # Add to content area
        self.content_layout.addWidget(dashboard_widget)
        self.current_content_widget = dashboard_widget
        dashboard_widget.show()
        
        self.logger.info("Basic dashboard content displayed")
    
    def _handle_dashboard_navigation(self, destination: str, filter_type: str = None):
        """Handle navigation from dashboard cards and quick action buttons"""
        try:
            self.logger.info(f"Handling dashboard navigation to: {destination} with filter: {filter_type}")
            
            if destination == "medicine":
                # Add Medicine button - go to medicine management
                self.sidebar.set_active_item("medicine")
                self._show_medicine_management()
                
            elif destination == "billing":
                # Process Sale button - go to billing system
                self.sidebar.set_active_item("billing")
                self._show_billing_content()
                
            elif destination == "inventory":
                # View Inventory, Low Stock, Expired Items buttons - go to medicine management
                self.sidebar.set_active_item("medicine")
                self._show_medicine_management(filter_type=filter_type)
                
            elif destination == "reports":
                # View Reports button, Sales chart, Total Sales card - go to reports
                self.sidebar.set_active_item("reports")
                self._show_reports_content()
                
            else:
                self.logger.warning(f"Unknown dashboard navigation destination: {destination}")
                
        except Exception as e:
            self.logger.error(f"Error handling dashboard navigation: {str(e)}")
    
    def _show_medicine_management(self, filter_type: str = None):
        """Show medicine management content with optional filtering"""
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
        
        # Set access mode based on user role
        if self.current_user:
            if self.current_user.is_admin():
                self.medicine_management_widget.set_readonly_mode(False)
                self.logger.info("Medicine management set to full access mode for admin")
            elif self.current_user.is_cashier():
                self.medicine_management_widget.set_readonly_mode(True)
                self.logger.info("Medicine management set to read-only mode for cashier")
        
        # Add to content area
        self.content_layout.addWidget(self.medicine_management_widget)
        self.current_content_widget = self.medicine_management_widget
        self.medicine_management_widget.show()
        
        # Refresh data
        try:
            self.medicine_management_widget.refresh_data()
        except Exception as e:
            self.logger.error(f"Failed to refresh medicine data: {e}")
        
        # Apply filter if specified, or clear filters if no filter
        try:
            if filter_type:
                self.logger.info(f"Applying filter: {filter_type}")
                self.medicine_management_widget.filter_by_stock_status(filter_type)
            else:
                self.logger.info("Clearing all filters")
                self.medicine_management_widget.clear_all_filters()
        except Exception as e:
            self.logger.error(f"Failed to apply/clear filter: {e}")
        
        self.logger.info(f"Medicine management content displayed with filter: {filter_type}")
    
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
    
    def _show_user_management(self):
        """Show user management dialog (admin only)"""
        # Check if user has admin privileges
        if not self.is_user_admin():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Access Denied",
                "User management is only available to administrators."
            )
            return
        
        try:
            from .dialogs.user_management_dialog import UserManagementDialog
            
            # Create and show user management dialog
            dialog = UserManagementDialog(self.auth_manager, self)
            
            # Connect signal to refresh UI if users are updated
            dialog.users_updated.connect(self._on_users_updated)
            
            # Show dialog
            dialog.exec()
            
            self.logger.info("User management dialog displayed")
            
        except Exception as e:
            self.logger.error(f"Failed to show user management: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open user management:\n{str(e)}"
            )
    
    def _on_users_updated(self):
        """Handle users updated signal"""
        self.logger.info("Users updated, refreshing UI if needed")
        # Add any UI refresh logic here if needed
    
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
    
    # Authentication Methods
    

    
    def _update_ui_for_user(self, user: User):
        """Update UI based on logged-in user"""
        # Update user info in header
        self.user_info_label.setText(f"Welcome, {user.get_display_name()}")
        
        # Update sidebar based on user role
        self._update_sidebar_for_role(user.role)
        
        # Show appropriate default content
        if user.is_admin():
            self._show_dashboard_content()
        else:
            # Cashiers start with billing
            self._show_billing_content()
    
    def _update_sidebar_for_role(self, role: str):
        """Update sidebar menu items based on user role"""
        if role == "cashier":
            # Cashiers can only access billing and basic medicine view
            self._hide_menu_item("users")
            self._hide_menu_item("reports")
            self._hide_menu_item("settings")
            # Medicine management is available but with restrictions
            self._show_menu_item("medicine")
            self._enable_menu_item("medicine")
        elif role == "admin":
            # Admins can access everything
            self._show_menu_item("users")
            self._show_menu_item("reports")
            self._show_menu_item("settings")
            self._show_menu_item("medicine")
            self._enable_menu_item("users")
            self._enable_menu_item("medicine")
    
    def _hide_menu_item(self, item_key: str):
        """Hide a menu item from the sidebar"""
        if item_key in self.sidebar.navigation_buttons:
            button = self.sidebar.navigation_buttons[item_key]
            button.hide()
            self.logger.info(f"Menu item hidden: {item_key}")
    
    def _show_menu_item(self, item_key: str):
        """Show a menu item in the sidebar"""
        if item_key in self.sidebar.navigation_buttons:
            button = self.sidebar.navigation_buttons[item_key]
            button.show()
            self.logger.info(f"Menu item shown: {item_key}")
    
    def _disable_menu_item(self, item_key: str):
        """Disable a menu item (but keep it visible)"""
        if item_key in self.sidebar.navigation_buttons:
            button = self.sidebar.navigation_buttons[item_key]
            button.setEnabled(False)
            button.setToolTip("Access restricted for your role")
            self.logger.info(f"Menu item disabled: {item_key}")
    
    def _enable_menu_item(self, item_key: str):
        """Enable a menu item"""
        if item_key in self.sidebar.navigation_buttons:
            button = self.sidebar.navigation_buttons[item_key]
            button.setEnabled(True)
            button.setToolTip("")
            self.logger.info(f"Menu item enabled: {item_key}")
    
    def _on_logout_clicked(self):
        """Handle logout button click"""
        try:
            # Confirm logout
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Confirm Logout",
                "Are you sure you want to logout?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Perform logout
                success = self.login_manager.logout()
                if success:
                    self.logger.info("User logged out successfully")
                    
                    # Clear current user and UI state
                    self.current_user = None
                    self._clear_content_area()
                    
                    # Reset UI to default state
                    self.user_info_label.setText("Welcome, User")
                    
                    # Hide main window and show login dialog again
                    self.hide()
                    
                    # Show login dialog again
                    success, user = self.login_manager.show_login_dialog()
                    
                    if success and user:
                        self.current_user = user
                        self._update_ui_for_user(user)
                        self.show()
                        self.logger.info(f"User logged in successfully: {user.username}")
                    else:
                        self.logger.info("Login cancelled after logout, closing application")
                        from PySide6.QtWidgets import QApplication
                        QApplication.quit()
                else:
                    self.logger.error("Logout failed")
                    QMessageBox.warning(
                        self,
                        "Logout Error",
                        "Failed to logout properly. Please try again."
                    )
        
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during logout: {str(e)}"
            )
    
    def _on_menu_item_selected(self, item_key: str):
        """Handle menu item selection from sidebar with role-based access control"""
        self.logger.info(f"Menu item selected: {item_key}")
        
        # Check if user has permission for this feature
        if not self._check_feature_permission(item_key):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Access Denied",
                f"You don't have permission to access {item_key.replace('_', ' ').title()}."
            )
            return
        
        # Switch content based on selected item
        if item_key == "dashboard":
            self._show_dashboard_content()
        elif item_key == "medicine":
            self._show_medicine_management()
        elif item_key == "billing":
            self._show_billing_content()
        elif item_key == "users":
            self._show_user_management()
        elif item_key == "reports":
            self._show_reports_content()
        elif item_key == "settings":
            self._show_settings_content()
        else:
            self.logger.warning(f"Unknown menu item: {item_key}")
            self._show_dashboard_content()
    
    def _check_feature_permission(self, feature: str) -> bool:
        """Check if current user has permission for a feature"""
        if not self.current_user:
            return False
        
        return self.auth_manager.has_permission(feature)
    

    
    def get_current_user(self) -> Optional[User]:
        """Get the current logged-in user"""
        return self.current_user
    
    def is_user_admin(self) -> bool:
        """Check if current user is admin"""
        return bool(self.current_user and self.current_user.is_admin())
    
    def is_user_cashier(self) -> bool:
        """Check if current user is cashier"""
        return bool(self.current_user and self.current_user.is_cashier())