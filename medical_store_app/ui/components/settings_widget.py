"""
Settings widget for Medical Store Management Application
Provides interface for store details configuration, currency and tax rate settings
"""

import logging
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QSpinBox, QGroupBox, QScrollArea, QFrame, QSizePolicy,
    QMessageBox, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QDoubleValidator

from .base_components import ValidatedLineEdit, ValidationMixin
from ..dialogs.base_dialog import BaseDialog
from ...repositories.settings_repository import SettingsRepository
from ...config.database import DatabaseManager


class SettingsWidget(QWidget):
    """Settings management widget with store details and business configuration"""
    
    # Signals
    settings_updated = Signal(dict)  # Emitted when settings are updated
    
    def __init__(self, parent=None):
        """Initialize settings widget"""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Initialize repository
        self.db_manager = DatabaseManager()
        self.settings_repository = SettingsRepository(self.db_manager)
        
        # Current settings cache
        self.current_settings = {}
        
        # UI components
        self.scroll_area = None
        self.main_content = None
        self.store_group = None
        self.business_group = None
        self.system_group = None
        
        # Form fields
        self.store_name_edit = None
        self.store_address_edit = None
        self.store_phone_edit = None
        self.store_email_edit = None
        self.store_website_edit = None
        
        self.currency_combo = None
        self.tax_rate_spin = None
        self.low_stock_threshold_spin = None
        self.enable_barcode_check = None
        self.auto_backup_check = None
        self.backup_frequency_spin = None
        
        # Action buttons
        self.save_button = None
        self.reset_button = None
        self.defaults_button = None
        
        # Status label
        self.status_label = None
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self._auto_save_settings)
        
        # Set up UI
        self._setup_ui()
        self._apply_styling()
        self._load_current_settings()
        
        self.logger.info("Settings widget initialized")
    
    def _setup_ui(self):
        """Set up the settings user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        self._create_header(main_layout)
        
        # Create scroll area for settings content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        self.main_content = QWidget()
        content_layout = QVBoxLayout(self.main_content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Create settings sections
        self._create_store_settings_section(content_layout)
        self._create_business_settings_section(content_layout)
        self._create_system_settings_section(content_layout)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Create action buttons
        self._create_action_buttons(content_layout)
        
        # Set scroll area content
        self.scroll_area.setWidget(self.main_content)
        main_layout.addWidget(self.scroll_area)
        
        # Create status bar
        self._create_status_bar(main_layout)
    
    def _create_header(self, parent_layout):
        """Create settings header"""
        header_frame = QFrame()
        header_frame.setObjectName("settingsHeader")
        header_frame.setFixedHeight(60)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setObjectName("settingsTitle")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        
        # Subtitle
        subtitle_label = QLabel("Configure store details, business settings, and system preferences")
        subtitle_label.setObjectName("settingsSubtitle")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle_label.setFont(subtitle_font)
        
        # Layout
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)
    
    def _create_store_settings_section(self, parent_layout):
        """Create store information settings section"""
        self.store_group = QGroupBox("Store Information")
        self.store_group.setObjectName("settingsGroup")
        
        form_layout = QFormLayout(self.store_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Store name
        self.store_name_edit = ValidatedLineEdit("Enter store name")
        self.store_name_edit.add_validator(self._validate_required_field)
        self.store_name_edit.textChanged.connect(self._on_setting_changed)
        form_layout.addRow("Store Name *:", self.store_name_edit)
        
        # Store address
        self.store_address_edit = QTextEdit()
        self.store_address_edit.setMaximumHeight(80)
        self.store_address_edit.setPlaceholderText("Enter store address")
        self.store_address_edit.textChanged.connect(self._on_setting_changed)
        form_layout.addRow("Address:", self.store_address_edit)
        
        # Store phone
        self.store_phone_edit = ValidatedLineEdit("Enter phone number")
        self.store_phone_edit.add_validator(self._validate_phone_number)
        self.store_phone_edit.textChanged.connect(self._on_setting_changed)
        form_layout.addRow("Phone:", self.store_phone_edit)
        
        # Store email
        self.store_email_edit = ValidatedLineEdit("Enter email address")
        self.store_email_edit.add_validator(self._validate_email)
        self.store_email_edit.textChanged.connect(self._on_setting_changed)
        form_layout.addRow("Email:", self.store_email_edit)
        
        # Store website
        self.store_website_edit = ValidatedLineEdit("Enter website URL")
        self.store_website_edit.textChanged.connect(self._on_setting_changed)
        form_layout.addRow("Website:", self.store_website_edit)
        
        parent_layout.addWidget(self.store_group)
    
    def _create_business_settings_section(self, parent_layout):
        """Create business configuration settings section"""
        self.business_group = QGroupBox("Business Configuration")
        self.business_group.setObjectName("settingsGroup")
        
        form_layout = QFormLayout(self.business_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Currency selection
        self.currency_combo = QComboBox()
        self.currency_combo.addItems([
            "USD - US Dollar",
            "EUR - Euro", 
            "GBP - British Pound",
            "INR - Indian Rupee",
            "PKR - Pakistani Rupee",
            "CAD - Canadian Dollar",
            "AUD - Australian Dollar",
            "JPY - Japanese Yen",
            "CNY - Chinese Yuan"
        ])
        self.currency_combo.setEditable(True)
        self.currency_combo.currentTextChanged.connect(self._on_setting_changed)
        form_layout.addRow("Currency:", self.currency_combo)
        
        # Tax rate
        self.tax_rate_spin = QDoubleSpinBox()
        self.tax_rate_spin.setRange(0.0, 100.0)
        self.tax_rate_spin.setDecimals(2)
        self.tax_rate_spin.setSuffix(" %")
        self.tax_rate_spin.setSingleStep(0.25)
        self.tax_rate_spin.valueChanged.connect(self._on_setting_changed)
        form_layout.addRow("Tax Rate:", self.tax_rate_spin)
        
        # Low stock threshold
        self.low_stock_threshold_spin = QSpinBox()
        self.low_stock_threshold_spin.setRange(1, 1000)
        self.low_stock_threshold_spin.setSuffix(" units")
        self.low_stock_threshold_spin.valueChanged.connect(self._on_setting_changed)
        form_layout.addRow("Low Stock Threshold:", self.low_stock_threshold_spin)
        
        parent_layout.addWidget(self.business_group)
    
    def _create_system_settings_section(self, parent_layout):
        """Create system preferences settings section"""
        self.system_group = QGroupBox("System Preferences")
        self.system_group.setObjectName("settingsGroup")
        
        form_layout = QFormLayout(self.system_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Enable barcode scanning
        self.enable_barcode_check = QCheckBox("Enable barcode scanning functionality")
        self.enable_barcode_check.stateChanged.connect(self._on_setting_changed)
        form_layout.addRow("Barcode Scanning:", self.enable_barcode_check)
        
        # Auto backup
        self.auto_backup_check = QCheckBox("Enable automatic database backup")
        self.auto_backup_check.stateChanged.connect(self._on_setting_changed)
        form_layout.addRow("Auto Backup:", self.auto_backup_check)
        
        # Backup frequency
        backup_layout = QHBoxLayout()
        self.backup_frequency_spin = QSpinBox()
        self.backup_frequency_spin.setRange(1, 30)
        self.backup_frequency_spin.setSuffix(" days")
        self.backup_frequency_spin.valueChanged.connect(self._on_setting_changed)
        backup_layout.addWidget(self.backup_frequency_spin)
        backup_layout.addStretch()
        
        backup_widget = QWidget()
        backup_widget.setLayout(backup_layout)
        form_layout.addRow("Backup Frequency:", backup_widget)
        
        parent_layout.addWidget(self.system_group)
    
    def _create_action_buttons(self, parent_layout):
        """Create action buttons for settings management"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # Reset to defaults button
        self.defaults_button = QPushButton("Reset to Defaults")
        self.defaults_button.setObjectName("defaultsButton")
        self.defaults_button.clicked.connect(self._reset_to_defaults)
        
        # Reset changes button
        self.reset_button = QPushButton("Reset Changes")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self._reset_changes)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self._save_settings)
        
        # Layout buttons
        button_layout.addWidget(self.defaults_button)
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        
        parent_layout.addWidget(button_frame)
    
    def _create_status_bar(self, parent_layout):
        """Create status bar for feedback"""
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setFixedHeight(30)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 5, 20, 5)
        
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        parent_layout.addWidget(status_frame)
    
    def _validate_required_field(self, value: str) -> tuple[bool, str]:
        """Validate required field"""
        if not value or not value.strip():
            return False, "This field is required"
        return True, ""
    
    def _validate_phone_number(self, value: str) -> tuple[bool, str]:
        """Validate phone number format"""
        if not value:
            return True, ""  # Optional field
        
        # Basic phone validation - allow digits, spaces, hyphens, parentheses, plus, dots
        import re
        if not re.match(r'^[\d\s\-\(\)\+\.]+$', value):
            return False, "Invalid phone number format"
        
        return True, ""
    
    def _validate_email(self, value: str) -> tuple[bool, str]:
        """Validate email format"""
        if not value:
            return True, ""  # Optional field
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return False, "Invalid email format"
        
        return True, ""
    
    def _on_setting_changed(self):
        """Handle setting change - trigger auto-save timer"""
        # Reset auto-save timer
        self.auto_save_timer.stop()
        self.auto_save_timer.start(2000)  # Auto-save after 2 seconds of inactivity
        
        # Update status
        self._show_status("Settings modified - will auto-save in 2 seconds", "info")
    
    def _auto_save_settings(self):
        """Auto-save settings after delay"""
        if self._validate_all_fields():
            self._save_settings(show_message=False)
            self._show_status("Settings auto-saved", "success")
        else:
            self._show_status("Please fix validation errors before saving", "error")
    
    def _validate_all_fields(self) -> bool:
        """Validate all form fields"""
        is_valid = True
        
        # Validate store name (required)
        valid, error = self.store_name_edit.validate_input()
        if not valid:
            self.store_name_edit.show_error(error)
            is_valid = False
        else:
            self.store_name_edit.clear_error()
        
        # Validate phone
        valid, error = self.store_phone_edit.validate_input()
        if not valid:
            self.store_phone_edit.show_error(error)
            is_valid = False
        else:
            self.store_phone_edit.clear_error()
        
        # Validate email
        valid, error = self.store_email_edit.validate_input()
        if not valid:
            self.store_email_edit.show_error(error)
            is_valid = False
        else:
            self.store_email_edit.clear_error()
        
        return is_valid
    
    def _load_current_settings(self):
        """Load current settings from database"""
        try:
            # Get all settings
            all_settings = self.settings_repository.get_all()
            self.current_settings = all_settings
            
            # Populate store information
            self.store_name_edit.setText(all_settings.get('store_name', 'Medical Store'))
            self.store_address_edit.setPlainText(all_settings.get('store_address', ''))
            self.store_phone_edit.setText(all_settings.get('store_phone', ''))
            self.store_email_edit.setText(all_settings.get('store_email', ''))
            self.store_website_edit.setText(all_settings.get('store_website', ''))
            
            # Populate business settings
            currency = all_settings.get('currency', 'USD')
            # Find and set currency in combo box
            for i in range(self.currency_combo.count()):
                if self.currency_combo.itemText(i).startswith(currency):
                    self.currency_combo.setCurrentIndex(i)
                    break
            else:
                # If not found, set as custom text
                self.currency_combo.setCurrentText(currency)
            
            self.tax_rate_spin.setValue(float(all_settings.get('tax_rate', '0.0')))
            self.low_stock_threshold_spin.setValue(int(all_settings.get('low_stock_threshold', '10')))
            
            # Populate system settings
            self.enable_barcode_check.setChecked(all_settings.get('enable_barcode_scanning', 'true').lower() == 'true')
            self.auto_backup_check.setChecked(all_settings.get('auto_backup', 'false').lower() == 'true')
            self.backup_frequency_spin.setValue(int(all_settings.get('backup_frequency_days', '7')))
            
            self._show_status("Settings loaded successfully", "success")
            self.logger.info("Settings loaded from database")
            
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self._show_status("Failed to load settings", "error")
    
    def _save_settings(self, show_message: bool = True):
        """Save current settings to database"""
        try:
            if not self._validate_all_fields():
                if show_message:
                    self._show_status("Please fix validation errors", "error")
                return False
            
            # Collect all settings
            settings_to_save = {
                # Store information
                'store_name': self.store_name_edit.text().strip(),
                'store_address': self.store_address_edit.toPlainText().strip(),
                'store_phone': self.store_phone_edit.text().strip(),
                'store_email': self.store_email_edit.text().strip(),
                'store_website': self.store_website_edit.text().strip(),
                
                # Business settings
                'currency': self._extract_currency_code(self.currency_combo.currentText()),
                'tax_rate': str(self.tax_rate_spin.value()),
                'low_stock_threshold': str(self.low_stock_threshold_spin.value()),
                
                # System settings
                'enable_barcode_scanning': 'true' if self.enable_barcode_check.isChecked() else 'false',
                'auto_backup': 'true' if self.auto_backup_check.isChecked() else 'false',
                'backup_frequency_days': str(self.backup_frequency_spin.value())
            }
            
            # Save each setting
            success = True
            for key, value in settings_to_save.items():
                if not self.settings_repository.set(key, value, self._get_setting_description(key)):
                    success = False
                    self.logger.error(f"Failed to save setting: {key}")
            
            if success:
                self.current_settings.update(settings_to_save)
                if show_message:
                    self._show_status("Settings saved successfully", "success")
                
                # Emit signal for other components
                self.settings_updated.emit(settings_to_save)
                
                self.logger.info("Settings saved successfully")
                return True
            else:
                if show_message:
                    self._show_status("Failed to save some settings", "error")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            if show_message:
                self._show_status("Failed to save settings", "error")
            return False
    
    def _reset_changes(self):
        """Reset changes to last saved values"""
        reply = QMessageBox.question(
            self, 
            "Reset Changes",
            "Are you sure you want to reset all changes to the last saved values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._load_current_settings()
            self._show_status("Changes reset to last saved values", "info")
    
    def _reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults", 
            "Are you sure you want to reset all settings to default values? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.settings_repository.reset_to_defaults():
                    self._load_current_settings()
                    self._show_status("Settings reset to defaults", "success")
                    self.logger.info("Settings reset to defaults")
                else:
                    self._show_status("Failed to reset settings", "error")
            except Exception as e:
                self.logger.error(f"Failed to reset settings: {e}")
                self._show_status("Failed to reset settings", "error")
    
    def _extract_currency_code(self, currency_text: str) -> str:
        """Extract currency code from combo box text"""
        if ' - ' in currency_text:
            return currency_text.split(' - ')[0]
        return currency_text
    
    def _get_setting_description(self, key: str) -> str:
        """Get description for a setting key"""
        descriptions = {
            'store_name': 'Store name for receipts and reports',
            'store_address': 'Store address',
            'store_phone': 'Store contact phone',
            'store_email': 'Store email address',
            'store_website': 'Store website URL',
            'currency': 'Currency symbol',
            'tax_rate': 'Default tax rate percentage',
            'low_stock_threshold': 'Low stock alert threshold',
            'enable_barcode_scanning': 'Enable barcode scanning feature',
            'auto_backup': 'Enable automatic backup',
            'backup_frequency_days': 'Backup frequency in days'
        }
        return descriptions.get(key, '')
    
    def _show_status(self, message: str, status_type: str = "info"):
        """Show status message"""
        if self.status_label:
            self.status_label.setText(message)
            
            # Apply styling based on status type
            if status_type == "success":
                self.status_label.setStyleSheet("color: #27AE60; font-weight: 500;")
            elif status_type == "error":
                self.status_label.setStyleSheet("color: #E74C3C; font-weight: 500;")
            elif status_type == "warning":
                self.status_label.setStyleSheet("color: #F39C12; font-weight: 500;")
            else:  # info
                self.status_label.setStyleSheet("color: #2D9CDB; font-weight: 500;")
            
            # Clear status after 5 seconds
            QTimer.singleShot(5000, lambda: self.status_label.clear())
    
    def _apply_styling(self):
        """Apply styling to the settings widget"""
        self.setStyleSheet("""
            /* Settings Widget */
            QWidget {
                background-color: #F8F9FA;
            }
            
            /* Header */
            #settingsHeader {
                background-color: white;
                border-bottom: 1px solid #E1E5E9;
            }
            
            #settingsTitle {
                color: #333333;
            }
            
            #settingsSubtitle {
                color: #666666;
            }
            
            /* Group Boxes */
            QGroupBox#settingsGroup {
                font-weight: 600;
                font-size: 14px;
                color: #333333;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox#settingsGroup::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
            
            /* Form Controls */
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-height: 20px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, 
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #2D9CDB;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 5px;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 16px;
                border: none;
                background-color: #F1F3F4;
            }
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #E1E5E9;
            }
            
            /* Checkboxes */
            QCheckBox {
                font-size: 13px;
                color: #333333;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #E1E5E9;
                border-radius: 3px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2D9CDB;
                border-color: #2D9CDB;
            }
            
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-weight: bold;
            }
            
            /* Buttons */
            QPushButton {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                min-width: 100px;
                background-color: white;
                color: #333333;
            }
            
            QPushButton:hover {
                background-color: #F1F3F4;
                border-color: #2D9CDB;
            }
            
            QPushButton:pressed {
                background-color: #E1E5E9;
            }
            
            QPushButton#saveButton {
                background-color: #2D9CDB;
                color: white;
                border-color: #2D9CDB;
            }
            
            QPushButton#saveButton:hover {
                background-color: #1E88E5;
            }
            
            QPushButton#resetButton {
                background-color: #F39C12;
                color: white;
                border-color: #F39C12;
            }
            
            QPushButton#resetButton:hover {
                background-color: #E67E22;
            }
            
            QPushButton#defaultsButton {
                background-color: #E74C3C;
                color: white;
                border-color: #E74C3C;
            }
            
            QPushButton#defaultsButton:hover {
                background-color: #C0392B;
            }
            
            /* Status Frame */
            #statusFrame {
                background-color: white;
                border-top: 1px solid #E1E5E9;
            }
            
            #statusLabel {
                font-size: 12px;
            }
            
            /* Scroll Area */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #F1F3F4;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #C1C7CD;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #A0A6AC;
            }
        """)
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings as dictionary"""
        return self.current_settings.copy()
    
    def refresh_settings(self):
        """Refresh settings from database"""
        self._load_current_settings()