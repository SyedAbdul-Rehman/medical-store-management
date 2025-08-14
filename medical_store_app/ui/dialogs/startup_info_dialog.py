"""
Startup Information Dialog for Medical Store Management Application
Shows default login credentials and system information on first run
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .base_dialog import BaseDialog
from ..components.base_components import StyledButton


class StartupInfoDialog(BaseDialog):
    """Dialog showing startup information and default credentials"""
    
    def __init__(self, parent=None):
        super().__init__("Welcome to Medical Store Management", parent, modal=True)
        self.logger = logging.getLogger(__name__)
        
        # Set dialog size
        self.setFixedSize(500, 400)
        
        # Create content
        self._create_content()
        
        self.logger.info("Startup info dialog initialized")
    
    def _create_content(self):
        """Create the dialog content"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(20)
        
        # Header
        header_label = QLabel("🏥 Medical Store Management System")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #2D9CDB; margin-bottom: 10px;")
        content_layout.addWidget(header_label)
        
        # Welcome message
        welcome_label = QLabel("Welcome! This appears to be your first time running the application.")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #333333; font-size: 14px;")
        welcome_label.setWordWrap(True)
        content_layout.addWidget(welcome_label)
        
        # Credentials section
        creds_frame = QFrame()
        creds_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #E1E5E9;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        creds_layout = QVBoxLayout(creds_frame)
        
        creds_title = QLabel("Default Login Credentials")
        creds_title.setAlignment(Qt.AlignCenter)
        creds_title_font = QFont()
        creds_title_font.setPointSize(14)
        creds_title_font.setBold(True)
        creds_title.setFont(creds_title_font)
        creds_title.setStyleSheet("color: #333333; margin-bottom: 10px;")
        creds_layout.addWidget(creds_title)
        
        # Admin credentials
        admin_label = QLabel("👤 Administrator Account")
        admin_label.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 13px;")
        creds_layout.addWidget(admin_label)
        
        admin_details = QLabel("Username: admin\nPassword: admin123")
        admin_details.setStyleSheet("color: #333333; font-size: 12px; margin-left: 20px; margin-bottom: 10px;")
        creds_layout.addWidget(admin_details)
        
        admin_desc = QLabel("• Full access to all features\n• Can manage users, medicines, and settings\n• Can view all reports")
        admin_desc.setStyleSheet("color: #666666; font-size: 11px; margin-left: 20px; margin-bottom: 15px;")
        creds_layout.addWidget(admin_desc)
        
        # Cashier credentials
        cashier_label = QLabel("👤 Cashier Account")
        cashier_label.setStyleSheet("color: #27AE60; font-weight: bold; font-size: 13px;")
        creds_layout.addWidget(cashier_label)
        
        cashier_details = QLabel("Username: cashier\nPassword: cashier123")
        cashier_details.setStyleSheet("color: #333333; font-size: 12px; margin-left: 20px; margin-bottom: 10px;")
        creds_layout.addWidget(cashier_details)
        
        cashier_desc = QLabel("• Can process sales and billing\n• Can view medicine inventory\n• Limited access to system features")
        cashier_desc.setStyleSheet("color: #666666; font-size: 11px; margin-left: 20px;")
        creds_layout.addWidget(cashier_desc)
        
        content_layout.addWidget(creds_frame)
        
        # Security note
        security_label = QLabel("⚠️ Security Note: Please change these default passwords after your first login!")
        security_label.setAlignment(Qt.AlignCenter)
        security_label.setStyleSheet("""
            color: #F39C12; 
            font-weight: bold; 
            font-size: 12px; 
            background-color: #FEF9E7;
            border: 1px solid #F39C12;
            border-radius: 4px;
            padding: 8px;
        """)
        security_label.setWordWrap(True)
        content_layout.addWidget(security_label)
        
        # Instructions
        instructions_label = QLabel("Click 'Continue' to proceed to the login screen.")
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("color: #666666; font-size: 12px;")
        content_layout.addWidget(instructions_label)
        
        content_layout.addStretch()
        
        # Set content widget
        self.set_content_widget(content_widget)
        
        # Add continue button
        continue_btn = self.add_button("Continue", "primary", self.accept)
        continue_btn.setDefault(True)
    
    @staticmethod
    def show_startup_info(parent=None) -> bool:
        """
        Show startup information dialog
        
        Args:
            parent: Parent widget
            
        Returns:
            True if user clicked continue, False otherwise
        """
        dialog = StartupInfoDialog(parent)
        result = dialog.exec()
        return result == 1  # QDialog.Accepted