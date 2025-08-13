"""
Alert Widgets for Medical Store Management Application
Provides alert displays for low-stock and expiry warnings
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QPushButton, QGroupBox, QGridLayout, QSizePolicy, QSpacerItem,
    QMessageBox, QDialog, QDialogButtonBox, QSpinBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPen

from .base_components import StyledButton
from ...models.medicine import Medicine
from ...managers.medicine_manager import MedicineManager
from ...repositories.settings_repository import SettingsRepository


class AlertCard(QFrame):
    """Individual alert card widget"""
    
    # Signals
    medicine_clicked = Signal(object)  # Emitted when medicine is clicked
    action_requested = Signal(str, object)  # Emitted when action is requested
    
    def __init__(self, medicine: Medicine, alert_type: str, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        self.alert_type = alert_type
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._setup_styling()
    
    def _setup_ui(self):
        """Set up the alert card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # Header with medicine name and alert icon
        header_layout = QHBoxLayout()
        
        # Alert icon
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet(self._get_icon_style())
        header_layout.addWidget(icon_label)
        
        # Medicine name
        name_label = QLabel(self.medicine.name)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(10)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #333333;")
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # Alert severity indicator
        severity_label = QLabel(self._get_severity_text())
        severity_label.setStyleSheet(self._get_severity_style())
        severity_label.setAlignment(Qt.AlignCenter)
        severity_label.setFixedSize(60, 20)
        header_layout.addWidget(severity_label)
        
        layout.addLayout(header_layout)
        
        # Details section
        details_layout = QGridLayout()
        details_layout.setSpacing(4)
        
        # Category and batch
        details_layout.addWidget(QLabel("Category:"), 0, 0)
        details_layout.addWidget(QLabel(self.medicine.category), 0, 1)
        details_layout.addWidget(QLabel("Batch:"), 0, 2)
        details_layout.addWidget(QLabel(self.medicine.batch_no), 0, 3)
        
        # Quantity and expiry
        details_layout.addWidget(QLabel("Quantity:"), 1, 0)
        quantity_label = QLabel(str(self.medicine.quantity))
        quantity_label.setStyleSheet(self._get_quantity_style())
        details_layout.addWidget(quantity_label, 1, 1)
        
        details_layout.addWidget(QLabel("Expiry:"), 1, 2)
        expiry_label = QLabel(self.medicine.expiry_date)
        expiry_label.setStyleSheet(self._get_expiry_style())
        details_layout.addWidget(expiry_label, 1, 3)
        
        layout.addLayout(details_layout)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        # View details button
        view_btn = QPushButton("View")
        view_btn.setMaximumWidth(60)
        view_btn.clicked.connect(lambda: self.medicine_clicked.emit(self.medicine))
        actions_layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumWidth(60)
        edit_btn.clicked.connect(lambda: self.action_requested.emit("edit", self.medicine))
        actions_layout.addWidget(edit_btn)
        
        # Alert-specific action button
        if self.alert_type == "low_stock":
            restock_btn = QPushButton("Restock")
            restock_btn.setMaximumWidth(80)
            restock_btn.clicked.connect(lambda: self.action_requested.emit("restock", self.medicine))
            actions_layout.addWidget(restock_btn)
        elif self.alert_type == "expired":
            remove_btn = QPushButton("Remove")
            remove_btn.setMaximumWidth(80)
            remove_btn.setStyleSheet("QPushButton { background-color: #FFEBEE; color: #C62828; }")
            remove_btn.clicked.connect(lambda: self.action_requested.emit("remove", self.medicine))
            actions_layout.addWidget(remove_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
    
    def _setup_styling(self):
        """Set up card styling based on alert type"""
        base_style = """
            AlertCard {
                border: 1px solid %s;
                border-radius: 8px;
                background-color: %s;
                margin: 2px;
            }
            
            QLabel {
                color: #333333;
                font-size: 9pt;
            }
            
            QPushButton {
                background-color: #F8F9FA;
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 8pt;
            }
            
            QPushButton:hover {
                background-color: #E9ECEF;
            }
        """
        
        if self.alert_type == "low_stock":
            border_color = "#F57C00"
            bg_color = "#FFF8E1"
        elif self.alert_type == "expired":
            border_color = "#C62828"
            bg_color = "#FFEBEE"
        elif self.alert_type == "expiring_soon":
            border_color = "#FF9800"
            bg_color = "#FFF3E0"
        else:
            border_color = "#E1E5E9"
            bg_color = "#F8F9FA"
        
        self.setStyleSheet(base_style % (border_color, bg_color))
    
    def _get_icon_style(self) -> str:
        """Get icon style based on alert type"""
        if self.alert_type == "low_stock":
            return "background-color: #F57C00; border-radius: 12px;"
        elif self.alert_type == "expired":
            return "background-color: #C62828; border-radius: 12px;"
        elif self.alert_type == "expiring_soon":
            return "background-color: #FF9800; border-radius: 12px;"
        return "background-color: #E1E5E9; border-radius: 12px;"
    
    def _get_severity_text(self) -> str:
        """Get severity text based on alert type"""
        if self.alert_type == "low_stock":
            return "LOW"
        elif self.alert_type == "expired":
            return "EXPIRED"
        elif self.alert_type == "expiring_soon":
            return "EXPIRING"
        return "INFO"
    
    def _get_severity_style(self) -> str:
        """Get severity label style"""
        if self.alert_type == "low_stock":
            return "background-color: #F57C00; color: white; border-radius: 10px; font-size: 8pt; font-weight: bold;"
        elif self.alert_type == "expired":
            return "background-color: #C62828; color: white; border-radius: 10px; font-size: 8pt; font-weight: bold;"
        elif self.alert_type == "expiring_soon":
            return "background-color: #FF9800; color: white; border-radius: 10px; font-size: 8pt; font-weight: bold;"
        return "background-color: #E1E5E9; color: #333333; border-radius: 10px; font-size: 8pt; font-weight: bold;"
    
    def _get_quantity_style(self) -> str:
        """Get quantity label style"""
        if self.medicine.quantity == 0:
            return "color: #C62828; font-weight: bold;"
        elif self.medicine.is_low_stock():
            return "color: #F57C00; font-weight: bold;"
        return "color: #333333;"
    
    def _get_expiry_style(self) -> str:
        """Get expiry label style"""
        if self.medicine.is_expired():
            return "color: #C62828; font-weight: bold;"
        elif self.medicine.is_expiring_soon():
            return "color: #F57C00; font-weight: bold;"
        return "color: #333333;"


class AlertSection(QWidget):
    """Alert section widget containing multiple alert cards"""
    
    # Signals
    medicine_clicked = Signal(object)
    action_requested = Signal(str, object)
    
    def __init__(self, title: str, alert_type: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.alert_type = alert_type
        self.medicines = []
        self.cards = []
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the alert section UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Section header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 8, 15, 8)
        
        # Title
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        # Count badge
        self.count_label = QLabel("0")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setFixedSize(30, 20)
        self.count_label.setStyleSheet(self._get_count_style())
        header_layout.addWidget(self.count_label)
        
        header_layout.addStretch()
        
        # Expand/collapse button
        self.toggle_button = QPushButton("▼")
        self.toggle_button.setFixedSize(30, 20)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self._toggle_section)
        header_layout.addWidget(self.toggle_button)
        
        layout.addWidget(header_frame)
        
        # Scrollable content area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setMaximumHeight(300)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(5)
        
        # Empty state label
        self.empty_label = QLabel(f"No {self.title.lower()} alerts")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #666666; font-style: italic; padding: 20px;")
        self.content_layout.addWidget(self.empty_label)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up section styling"""
        header_color = self._get_header_color()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {header_color};
                border: 1px solid #E1E5E9;
                border-radius: 6px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)
    
    def _get_header_color(self) -> str:
        """Get header color based on alert type"""
        if self.alert_type == "low_stock":
            return "#FFF8E1"
        elif self.alert_type == "expired":
            return "#FFEBEE"
        elif self.alert_type == "expiring_soon":
            return "#FFF3E0"
        return "#F8F9FA"
    
    def _get_count_style(self) -> str:
        """Get count badge style"""
        if self.alert_type == "low_stock":
            return "background-color: #F57C00; color: white; border-radius: 10px; font-size: 9pt; font-weight: bold;"
        elif self.alert_type == "expired":
            return "background-color: #C62828; color: white; border-radius: 10px; font-size: 9pt; font-weight: bold;"
        elif self.alert_type == "expiring_soon":
            return "background-color: #FF9800; color: white; border-radius: 10px; font-size: 9pt; font-weight: bold;"
        return "background-color: #E1E5E9; color: #333333; border-radius: 10px; font-size: 9pt; font-weight: bold;"
    
    def _toggle_section(self):
        """Toggle section expand/collapse"""
        if self.toggle_button.isChecked():
            self.scroll_area.show()
            self.toggle_button.setText("▼")
        else:
            self.scroll_area.hide()
            self.toggle_button.setText("▶")
    
    def update_medicines(self, medicines: List[Medicine]):
        """Update medicines in this section"""
        self.medicines = medicines
        self._refresh_cards()
        self._update_count()
    
    def _refresh_cards(self):
        """Refresh alert cards"""
        # Clear existing cards
        for card in self.cards:
            card.setParent(None)
        self.cards.clear()
        
        # Remove empty label if it exists
        if self.empty_label.parent():
            self.empty_label.setParent(None)
        
        if not self.medicines:
            # Show empty state
            self.content_layout.addWidget(self.empty_label)
        else:
            # Create cards for medicines
            for medicine in self.medicines:
                card = AlertCard(medicine, self.alert_type)
                card.medicine_clicked.connect(self.medicine_clicked.emit)
                card.action_requested.connect(self.action_requested.emit)
                
                self.cards.append(card)
                self.content_layout.addWidget(card)
        
        # Add stretch at the end
        self.content_layout.addStretch()
    
    def _update_count(self):
        """Update count badge"""
        count = len(self.medicines)
        self.count_label.setText(str(count))
        
        # Update title color based on count
        if count > 0:
            if self.alert_type == "expired":
                self.title_label.setStyleSheet("color: #C62828; font-weight: bold;")
            elif self.alert_type == "low_stock":
                self.title_label.setStyleSheet("color: #F57C00; font-weight: bold;")
            elif self.alert_type == "expiring_soon":
                self.title_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            self.title_label.setStyleSheet("color: #333333; font-weight: bold;")


class AlertThresholdDialog(QDialog):
    """Dialog for configuring alert thresholds"""
    
    def __init__(self, settings_repository: SettingsRepository, parent=None):
        super().__init__(parent)
        self.settings_repository = settings_repository
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Alert Threshold Settings")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Set up dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Low stock threshold
        self.low_stock_spinbox = QSpinBox()
        self.low_stock_spinbox.setRange(1, 1000)
        self.low_stock_spinbox.setValue(10)
        self.low_stock_spinbox.setSuffix(" units")
        form_layout.addRow("Low Stock Threshold:", self.low_stock_spinbox)
        
        # Expiry warning days
        self.expiry_days_spinbox = QSpinBox()
        self.expiry_days_spinbox.setRange(1, 365)
        self.expiry_days_spinbox.setValue(30)
        self.expiry_days_spinbox.setSuffix(" days")
        form_layout.addRow("Expiry Warning Days:", self.expiry_days_spinbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_current_settings(self):
        """Load current threshold settings"""
        try:
            low_stock_threshold = self.settings_repository.get_int('low_stock_threshold', 10)
            expiry_warning_days = self.settings_repository.get_int('expiry_warning_days', 30)
            
            self.low_stock_spinbox.setValue(low_stock_threshold)
            self.expiry_days_spinbox.setValue(expiry_warning_days)
            
        except Exception as e:
            self.logger.error(f"Error loading threshold settings: {e}")
    
    def _save_settings(self):
        """Save threshold settings"""
        try:
            low_stock_threshold = self.low_stock_spinbox.value()
            expiry_warning_days = self.expiry_days_spinbox.value()
            
            success = True
            success &= self.settings_repository.set_int(
                'low_stock_threshold', 
                low_stock_threshold,
                'Low stock alert threshold'
            )
            success &= self.settings_repository.set_int(
                'expiry_warning_days', 
                expiry_warning_days,
                'Days before expiry to show warning'
            )
            
            if success:
                self.logger.info(f"Alert thresholds updated: low_stock={low_stock_threshold}, expiry_days={expiry_warning_days}")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to save threshold settings")
                
        except Exception as e:
            self.logger.error(f"Error saving threshold settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")


class AlertSystemWidget(QWidget):
    """Main alert system widget containing all alert sections"""
    
    # Signals
    medicine_selected = Signal(object)
    edit_requested = Signal(object)
    restock_requested = Signal(object)
    remove_requested = Signal(object)
    settings_changed = Signal()
    
    def __init__(self, medicine_manager: MedicineManager, settings_repository: SettingsRepository, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.settings_repository = settings_repository
        self.logger = logging.getLogger(__name__)
        
        # Alert sections
        self.sections = {}
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_alerts)
        
        self._setup_ui()
        self._connect_signals()
        
        # Initial load
        self.refresh_alerts()
        
        # Start auto-refresh (every 5 minutes)
        self.refresh_timer.start(300000)
    
    def _setup_ui(self):
        """Set up the alert system UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Inventory Alerts")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Settings button
        self.settings_button = StyledButton("Settings", "outline")
        self.settings_button.setMaximumWidth(100)
        header_layout.addWidget(self.settings_button)
        
        # Refresh button
        self.refresh_button = StyledButton("Refresh", "primary")
        self.refresh_button.setMaximumWidth(100)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Alert sections
        self._create_alert_sections(layout)
        
        layout.addStretch()
    
    def _create_alert_sections(self, layout):
        """Create alert sections"""
        # Expired medicines section
        self.sections['expired'] = AlertSection("Expired Medicines", "expired")
        layout.addWidget(self.sections['expired'])
        
        # Expiring soon section
        self.sections['expiring_soon'] = AlertSection("Expiring Soon", "expiring_soon")
        layout.addWidget(self.sections['expiring_soon'])
        
        # Low stock section
        self.sections['low_stock'] = AlertSection("Low Stock", "low_stock")
        layout.addWidget(self.sections['low_stock'])
    
    def _connect_signals(self):
        """Connect widget signals"""
        # Button signals
        self.settings_button.clicked.connect(self._show_settings_dialog)
        self.refresh_button.clicked.connect(self.refresh_alerts)
        
        # Section signals
        for section in self.sections.values():
            section.medicine_clicked.connect(self.medicine_selected.emit)
            section.action_requested.connect(self._handle_action_request)
    
    def _handle_action_request(self, action: str, medicine: Medicine):
        """Handle action requests from alert cards"""
        if action == "edit":
            self.edit_requested.emit(medicine)
        elif action == "restock":
            self.restock_requested.emit(medicine)
        elif action == "remove":
            self.remove_requested.emit(medicine)
    
    def _show_settings_dialog(self):
        """Show alert threshold settings dialog"""
        dialog = AlertThresholdDialog(self.settings_repository, self)
        if dialog.exec() == QDialog.Accepted:
            self.settings_changed.emit()
            self.refresh_alerts()
    
    def refresh_alerts(self):
        """Refresh all alert data"""
        try:
            # Get threshold settings
            low_stock_threshold = self.settings_repository.get_int('low_stock_threshold', 10)
            expiry_warning_days = self.settings_repository.get_int('expiry_warning_days', 30)
            
            # Update medicine manager thresholds
            self.medicine_manager.set_low_stock_threshold(low_stock_threshold)
            self.medicine_manager.set_expiry_warning_days(expiry_warning_days)
            
            # Get alert data
            alerts = self.medicine_manager.generate_stock_alerts()
            
            # Update sections
            self.sections['expired'].update_medicines(alerts['expired'])
            self.sections['expiring_soon'].update_medicines(alerts['expiring_soon'])
            self.sections['low_stock'].update_medicines(alerts['low_stock'])
            
            # Log summary
            total_alerts = sum(len(medicines) for medicines in alerts.values())
            self.logger.info(f"Alert system refreshed: {total_alerts} total alerts")
            
        except Exception as e:
            self.logger.error(f"Error refreshing alerts: {e}")
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of current alerts"""
        return {
            'expired': len(self.sections['expired'].medicines),
            'expiring_soon': len(self.sections['expiring_soon'].medicines),
            'low_stock': len(self.sections['low_stock'].medicines)
        }
    
    def set_auto_refresh_enabled(self, enabled: bool):
        """Enable or disable auto-refresh"""
        if enabled:
            self.refresh_timer.start(300000)  # 5 minutes
            self.logger.info("Alert auto-refresh enabled")
        else:
            self.refresh_timer.stop()
            self.logger.info("Alert auto-refresh disabled")