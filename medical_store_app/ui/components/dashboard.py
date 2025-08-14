"""
Dashboard Widget for Medical Store Management Application
Provides overview cards with key metrics and real-time data display
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QSizePolicy, QSpacerItem, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPen

from .base_components import StyledButton
from .sales_chart import SalesChartCard
from ...managers.medicine_manager import MedicineManager
from ...managers.sales_manager import SalesManager


class MetricCard(QFrame):
    """Individual metric card widget for dashboard overview"""
    
    # Signals
    card_clicked = Signal(str)  # Emitted when card is clicked
    
    def __init__(self, title: str, value: str, subtitle: str = "", 
                 card_type: str = "default", clickable: bool = False, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.card_type = card_type
        self.clickable = clickable
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._setup_styling()
        
        if self.clickable:
            self.setCursor(Qt.PointingHandCursor)
    
    def _setup_ui(self):
        """Set up the metric card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setWeight(QFont.Medium)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(self.value)
        value_label.setObjectName("cardValue")
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setWeight(QFont.Bold)
        value_label.setFont(value_font)
        layout.addWidget(value_label)
        
        # Subtitle (optional)
        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setObjectName("cardSubtitle")
            subtitle_font = QFont()
            subtitle_font.setPointSize(9)
            subtitle_label.setFont(subtitle_font)
            layout.addWidget(subtitle_label)
        
        # Store references for updates
        self.title_label = title_label
        self.value_label = value_label
        self.subtitle_label = subtitle_label if self.subtitle else None
    
    def _setup_styling(self):
        """Set up card styling based on type"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        # Base styling
        base_style = """
            QFrame {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #2D9CDB;
                box-shadow: 0 2px 8px rgba(45, 156, 219, 0.1);
            }
            QLabel#cardTitle {
                color: #666666;
                font-weight: 500;
            }
            QLabel#cardValue {
                color: #333333;
                font-weight: bold;
            }
            QLabel#cardSubtitle {
                color: #888888;
            }
        """
        
        # Type-specific styling
        if self.card_type == "success":
            type_style = """
                QLabel#cardValue { color: #27AE60; }
                QFrame:hover { border-color: #27AE60; }
            """
        elif self.card_type == "warning":
            type_style = """
                QLabel#cardValue { color: #F2C94C; }
                QFrame:hover { border-color: #F2C94C; }
            """
        elif self.card_type == "danger":
            type_style = """
                QLabel#cardValue { color: #E74C3C; }
                QFrame:hover { border-color: #E74C3C; }
            """
        else:
            type_style = """
                QLabel#cardValue { color: #2D9CDB; }
            """
        
        self.setStyleSheet(base_style + type_style)
    
    def update_value(self, new_value: str, new_subtitle: str = None):
        """Update card value and subtitle"""
        self.value = new_value
        self.value_label.setText(new_value)
        
        if new_subtitle is not None and self.subtitle_label:
            self.subtitle = new_subtitle
            self.subtitle_label.setText(new_subtitle)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for clickable cards"""
        if self.clickable and event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.card_type)
        super().mousePressEvent(event)


class DashboardWidget(QWidget):
    """Main dashboard widget with overview cards and metrics"""
    
    # Signals
    navigate_to = Signal(str)  # Emitted when navigation is requested
    
    def __init__(self, medicine_manager: MedicineManager, sales_manager: SalesManager, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.sales_manager = sales_manager
        self.logger = logging.getLogger(__name__)
        
        # Data refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        self._setup_ui()
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create scroll area for responsive design
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Dashboard Overview")
        title_label.setObjectName("dashboardTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Refresh button
        refresh_btn = StyledButton("Refresh", button_type="secondary")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        
        # Overview cards section
        self._create_overview_cards(content_layout)
        
        # Sales chart section
        self._create_sales_chart_section(content_layout)
        
        # Quick actions section
        self._create_quick_actions_section(content_layout)
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Apply styling
        self._apply_styling()
    
    def _create_overview_cards(self, parent_layout):
        """Create overview cards section"""
        # Cards section header
        cards_header = QLabel("Key Metrics")
        cards_header.setObjectName("sectionHeader")
        cards_font = QFont()
        cards_font.setPointSize(14)
        cards_font.setWeight(QFont.Medium)
        cards_header.setFont(cards_font)
        parent_layout.addWidget(cards_header)
        
        # Cards grid layout
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)
        
        # Create metric cards
        self.total_sales_card = MetricCard(
            title="Total Sales Today",
            value="$0.00",
            subtitle="0 transactions",
            card_type="success",
            clickable=True
        )
        self.total_sales_card.card_clicked.connect(lambda: self.navigate_to.emit("reports"))
        
        self.total_medicines_card = MetricCard(
            title="Total Medicines",
            value="0",
            subtitle="0 categories",
            card_type="default",
            clickable=True
        )
        self.total_medicines_card.card_clicked.connect(lambda: self.navigate_to.emit("inventory"))
        
        self.low_stock_card = MetricCard(
            title="Low Stock Items",
            value="0",
            subtitle="Requires attention",
            card_type="warning",
            clickable=True
        )
        self.low_stock_card.card_clicked.connect(lambda: self.navigate_to.emit("inventory"))
        
        self.expired_stock_card = MetricCard(
            title="Expired Items",
            value="0",
            subtitle="Immediate action needed",
            card_type="danger",
            clickable=True
        )
        self.expired_stock_card.card_clicked.connect(lambda: self.navigate_to.emit("inventory"))
        
        # Add cards to grid (2x2 layout)
        cards_grid.addWidget(self.total_sales_card, 0, 0)
        cards_grid.addWidget(self.total_medicines_card, 0, 1)
        cards_grid.addWidget(self.low_stock_card, 1, 0)
        cards_grid.addWidget(self.expired_stock_card, 1, 1)
        
        # Make cards responsive
        for i in range(2):
            cards_grid.setColumnStretch(i, 1)
        
        parent_layout.addLayout(cards_grid)
        
        # Store card references
        self.metric_cards = [
            self.total_sales_card,
            self.total_medicines_card,
            self.low_stock_card,
            self.expired_stock_card
        ]
    
    def _create_sales_chart_section(self, parent_layout):
        """Create sales chart section"""
        # Chart section header
        chart_header = QLabel("Sales Performance")
        chart_header.setObjectName("sectionHeader")
        chart_font = QFont()
        chart_font.setPointSize(14)
        chart_font.setWeight(QFont.Medium)
        chart_header.setFont(chart_font)
        parent_layout.addWidget(chart_header)
        
        # Create sales chart card
        self.sales_chart_card = SalesChartCard()
        self.sales_chart_card.card_clicked.connect(lambda: self.navigate_to.emit("reports"))
        
        parent_layout.addWidget(self.sales_chart_card)
    
    def _create_quick_actions_section(self, parent_layout):
        """Create quick actions section with navigation buttons"""
        # Quick actions section header
        actions_header = QLabel("Quick Actions")
        actions_header.setObjectName("sectionHeader")
        actions_font = QFont()
        actions_font.setPointSize(14)
        actions_font.setWeight(QFont.Medium)
        actions_header.setFont(actions_font)
        parent_layout.addWidget(actions_header)
        
        # Quick actions container
        actions_container = QFrame()
        actions_container.setFrameStyle(QFrame.Box)
        actions_container.setLineWidth(1)
        actions_container.setObjectName("quickActionsContainer")
        
        actions_layout = QGridLayout(actions_container)
        actions_layout.setContentsMargins(20, 20, 20, 20)
        actions_layout.setSpacing(16)
        
        # Create quick action buttons
        self.quick_action_buttons = []
        
        # Add Medicine button
        add_medicine_btn = StyledButton("Add Medicine", button_type="primary")
        add_medicine_btn.setObjectName("quickActionButton")
        add_medicine_btn.clicked.connect(lambda: self.navigate_to.emit("medicine"))
        add_medicine_btn.setToolTip("Add new medicine to inventory")
        self.quick_action_buttons.append(add_medicine_btn)
        actions_layout.addWidget(add_medicine_btn, 0, 0)
        
        # Process Sale button
        process_sale_btn = StyledButton("Process Sale", button_type="secondary")
        process_sale_btn.setObjectName("quickActionButton")
        process_sale_btn.clicked.connect(lambda: self.navigate_to.emit("billing"))
        process_sale_btn.setToolTip("Start a new sale transaction")
        self.quick_action_buttons.append(process_sale_btn)
        actions_layout.addWidget(process_sale_btn, 0, 1)
        
        # View Inventory button
        view_inventory_btn = StyledButton("View Inventory", button_type="outline")
        view_inventory_btn.setObjectName("quickActionButton")
        view_inventory_btn.clicked.connect(lambda: self.navigate_to.emit("inventory"))
        view_inventory_btn.setToolTip("View and manage medicine inventory")
        self.quick_action_buttons.append(view_inventory_btn)
        actions_layout.addWidget(view_inventory_btn, 0, 2)
        
        # Low Stock Alert button (conditional styling based on alerts)
        low_stock_btn = StyledButton("Low Stock Items", button_type="outline")
        low_stock_btn.setObjectName("quickActionButton")
        low_stock_btn.clicked.connect(lambda: self.navigate_to.emit("inventory"))
        low_stock_btn.setToolTip("View medicines with low stock")
        self.quick_action_buttons.append(low_stock_btn)
        actions_layout.addWidget(low_stock_btn, 1, 0)
        
        # Expired Items button (conditional styling based on alerts)
        expired_items_btn = StyledButton("Expired Items", button_type="outline")
        expired_items_btn.setObjectName("quickActionButton")
        expired_items_btn.clicked.connect(lambda: self.navigate_to.emit("inventory"))
        expired_items_btn.setToolTip("View expired medicines")
        self.quick_action_buttons.append(expired_items_btn)
        actions_layout.addWidget(expired_items_btn, 1, 1)
        
        # Reports button
        reports_btn = StyledButton("View Reports", button_type="outline")
        reports_btn.setObjectName("quickActionButton")
        reports_btn.clicked.connect(lambda: self.navigate_to.emit("reports"))
        reports_btn.setToolTip("View sales and inventory reports")
        self.quick_action_buttons.append(reports_btn)
        actions_layout.addWidget(reports_btn, 1, 2)
        
        # Store references for dynamic updates
        self.low_stock_btn = low_stock_btn
        self.expired_items_btn = expired_items_btn
        
        parent_layout.addWidget(actions_container)
    
    def _update_quick_action_buttons(self, inventory_summary: Dict[str, Any]):
        """Update quick action buttons based on current data"""
        try:
            # Update low stock button
            if hasattr(self, 'low_stock_btn'):
                low_stock_count = inventory_summary.get('low_stock_count', 0)
                if low_stock_count > 0:
                    self.low_stock_btn.setText(f"Low Stock ({low_stock_count})")
                    # Change to warning style
                    self.low_stock_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #F2C94C;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 10px 20px;
                            font-size: 13px;
                            font-weight: 600;
                            min-width: 140px;
                            min-height: 40px;
                        }
                        QPushButton:hover {
                            background-color: #E6B800;
                        }
                        QPushButton:pressed {
                            background-color: #D4A300;
                        }
                    """)
                else:
                    self.low_stock_btn.setText("Low Stock Items")
                    # Reset to outline style
                    self.low_stock_btn.setStyleSheet("")  # Use default outline style
            
            # Update expired items button
            if hasattr(self, 'expired_items_btn'):
                expired_count = inventory_summary.get('expired_count', 0)
                if expired_count > 0:
                    self.expired_items_btn.setText(f"Expired ({expired_count})")
                    # Change to danger style
                    self.expired_items_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #E74C3C;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 10px 20px;
                            font-size: 13px;
                            font-weight: 600;
                            min-width: 140px;
                            min-height: 40px;
                        }
                        QPushButton:hover {
                            background-color: #C0392B;
                        }
                        QPushButton:pressed {
                            background-color: #A93226;
                        }
                    """)
                else:
                    self.expired_items_btn.setText("Expired Items")
                    # Reset to outline style
                    self.expired_items_btn.setStyleSheet("")  # Use default outline style
                    
        except Exception as e:
            self.logger.error(f"Error updating quick action buttons: {str(e)}")
    
    def _apply_styling(self):
        """Apply dashboard styling"""
        dashboard_style = """
            QWidget {
                background-color: #F8F9FA;
            }
            QLabel#dashboardTitle {
                color: #333333;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QLabel#sectionHeader {
                color: #555555;
                font-weight: 500;
                margin: 10px 0px 5px 0px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QFrame#quickActionsContainer {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                margin: 4px;
            }
            QPushButton#quickActionButton {
                min-width: 140px;
                min-height: 40px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#quickActionButton:hover {
                transform: translateY(-1px);
            }
        """
        self.setStyleSheet(dashboard_style)
    
    def refresh_data(self):
        """Refresh dashboard data and update cards"""
        try:
            self.logger.info("Refreshing dashboard data")
            
            # Get current date for today's sales
            today = date.today().isoformat()
            
            # Get sales data for today
            daily_sales = self.sales_manager.get_daily_sales(today)
            total_sales_today = sum(sale.total for sale in daily_sales)
            transaction_count = len(daily_sales)
            
            # Get inventory summary
            inventory_summary = self.medicine_manager.get_inventory_summary()
            
            # Update cards with real-time data
            self.total_sales_card.update_value(
                f"${total_sales_today:.2f}",
                f"{transaction_count} transactions"
            )
            
            self.total_medicines_card.update_value(
                str(inventory_summary['total_medicines']),
                f"{len(inventory_summary['categories'])} categories"
            )
            
            self.low_stock_card.update_value(
                str(inventory_summary['low_stock_count']),
                "Requires attention" if inventory_summary['low_stock_count'] > 0 else "All good"
            )
            
            self.expired_stock_card.update_value(
                str(inventory_summary['expired_count']),
                "Immediate action needed" if inventory_summary['expired_count'] > 0 else "All good"
            )
            
            # Update sales chart
            if hasattr(self, 'sales_chart_card'):
                chart_data = self.sales_manager.get_last_7_days_sales_data()
                self.sales_chart_card.update_chart_data(chart_data)
            
            # Update quick action buttons based on alerts
            self._update_quick_action_buttons(inventory_summary)
            
            self.logger.info(f"Dashboard data refreshed - Sales: ${total_sales_today:.2f}, "
                           f"Medicines: {inventory_summary['total_medicines']}, "
                           f"Low Stock: {inventory_summary['low_stock_count']}, "
                           f"Expired: {inventory_summary['expired_count']}")
            
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard data: {str(e)}")
            # Update cards with error state
            for card in self.metric_cards:
                if hasattr(card, 'value_label'):
                    card.value_label.setText("Error")
            
            # Update chart with empty data
            if hasattr(self, 'sales_chart_card'):
                self.sales_chart_card.update_chart_data({})
            
            # Reset quick action buttons to default state
            if hasattr(self, 'low_stock_btn'):
                self.low_stock_btn.setText("Low Stock Items")
                self.low_stock_btn.setStyleSheet("")
            if hasattr(self, 'expired_items_btn'):
                self.expired_items_btn.setText("Expired Items")
                self.expired_items_btn.setStyleSheet("")
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get current dashboard metrics for testing"""
        try:
            today = date.today().isoformat()
            daily_sales = self.sales_manager.get_daily_sales(today)
            inventory_summary = self.medicine_manager.get_inventory_summary()
            
            return {
                'total_sales_today': sum(sale.total for sale in daily_sales),
                'transaction_count': len(daily_sales),
                'total_medicines': inventory_summary['total_medicines'],
                'categories_count': len(inventory_summary['categories']),
                'low_stock_count': inventory_summary['low_stock_count'],
                'expired_count': inventory_summary['expired_count']
            }
        except Exception as e:
            self.logger.error(f"Error getting dashboard metrics: {str(e)}")
            return {
                'total_sales_today': 0.0,
                'transaction_count': 0,
                'total_medicines': 0,
                'categories_count': 0,
                'low_stock_count': 0,
                'expired_count': 0
            }
    
    def set_refresh_interval(self, seconds: int):
        """Set data refresh interval"""
        if seconds > 0:
            self.refresh_timer.setInterval(seconds * 1000)
            self.logger.info(f"Dashboard refresh interval set to {seconds} seconds")
    
    def stop_refresh(self):
        """Stop automatic data refresh"""
        self.refresh_timer.stop()
        self.logger.info("Dashboard auto-refresh stopped")
    
    def start_refresh(self):
        """Start automatic data refresh"""
        self.refresh_timer.start()
        self.logger.info("Dashboard auto-refresh started")