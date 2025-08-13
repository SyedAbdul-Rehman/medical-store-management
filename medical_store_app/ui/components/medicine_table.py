"""
Medicine Table Widget for Medical Store Management Application
Provides table interface for displaying and managing medicine records
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem,
    QMessageBox, QMenu, QLineEdit, QComboBox, QPushButton, QLabel,
    QFrame, QSizePolicy, QAbstractItemView, QDoubleSpinBox, QSpinBox,
    QDateEdit, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QAction, QFont, QColor, QBrush

from .base_components import StyledTable, StyledButton, ValidatedLineEdit
from ...models.medicine import Medicine
from ...managers.medicine_manager import MedicineManager


class MedicineTableWidget(QWidget):
    """Medicine table widget with search, filter, and management capabilities"""
    
    # Signals
    medicine_selected = Signal(object)  # Emitted when a medicine is selected
    edit_requested = Signal(object)    # Emitted when edit is requested
    delete_requested = Signal(object)  # Emitted when delete is requested
    refresh_requested = Signal()       # Emitted when refresh is requested
    
    def __init__(self, medicine_manager: MedicineManager, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.logger = logging.getLogger(__name__)
        
        # Data
        self.medicines = []
        self.filtered_medicines = []
        self.selected_medicine = None
        
        # Search and filter state
        self.search_query = ""
        self.search_type = "All Fields"
        self.category_filter = ""
        self.stock_filter = ""
        self.min_price = 0.0
        self.max_price = 999999.99
        self.min_quantity = 0
        self.max_quantity = 999999
        self.expiry_filter = "All"
        self.sort_option = "Name (A-Z)"
        self.saved_filters = {}
        
        # Table columns
        self.columns = [
            ("ID", 60),
            ("Name", 200),
            ("Category", 120),
            ("Batch No", 100),
            ("Expiry Date", 100),
            ("Quantity", 80),
            ("Purchase Price", 100),
            ("Selling Price", 100),
            ("Barcode", 120),
            ("Status", 100)
        ]
        
        # Refresh timer for auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        
        self._setup_ui()
        self._connect_signals()
        self._setup_context_menu()
        
        # Initial data load
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the table widget UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)
        
        # Header section
        self._create_header_section()
        
        # Search and filter section
        self._create_search_filter_section()
        
        # Table section
        self._create_table_section()
        
        # Footer section
        self._create_footer_section()
        
        self._setup_styling()
    
    def _create_header_section(self):
        """Create header section with title and actions"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Medicine Inventory")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = StyledButton("Refresh", "outline")
        self.refresh_button.setMaximumWidth(100)
        header_layout.addWidget(self.refresh_button)
        
        # Auto-refresh toggle
        self.auto_refresh_button = StyledButton("Auto-Refresh: OFF", "outline")
        self.auto_refresh_button.setMaximumWidth(150)
        self.auto_refresh_button.setCheckable(True)
        header_layout.addWidget(self.auto_refresh_button)
        
        self.main_layout.addLayout(header_layout)
    
    def _create_search_filter_section(self):
        """Create search and filter controls"""
        # Container frame
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        filter_layout.setSpacing(10)
        
        # First row - Basic search and filters
        first_row = QHBoxLayout()
        
        # Search field with advanced options
        search_label = QLabel("Search:")
        self.search_field = ValidatedLineEdit("Search by name, category, batch, or barcode...")
        self.search_field.setMaximumWidth(300)
        
        # Search type selector
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["All Fields", "Name Only", "Category Only", "Batch Number", "Barcode Only"])
        self.search_type_combo.setMaximumWidth(120)
        
        first_row.addWidget(search_label)
        first_row.addWidget(self.search_field)
        first_row.addWidget(QLabel("in:"))
        first_row.addWidget(self.search_type_combo)
        
        # Category filter
        category_label = QLabel("Category:")
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.setMaximumWidth(150)
        
        first_row.addWidget(category_label)
        first_row.addWidget(self.category_filter_combo)
        
        first_row.addStretch()
        
        filter_layout.addLayout(first_row)
        
        # Second row - Advanced filters
        second_row = QHBoxLayout()
        
        # Stock status filter
        stock_label = QLabel("Stock Status:")
        self.stock_filter_combo = QComboBox()
        self.stock_filter_combo.addItems(["All", "In Stock", "Low Stock", "Out of Stock", "Expired", "Expiring Soon"])
        self.stock_filter_combo.setMaximumWidth(120)
        
        second_row.addWidget(stock_label)
        second_row.addWidget(self.stock_filter_combo)
        
        # Price range filter
        price_label = QLabel("Price Range:")
        self.min_price_spinbox = QDoubleSpinBox()
        self.min_price_spinbox.setRange(0.0, 999999.99)
        self.min_price_spinbox.setPrefix("$")
        self.min_price_spinbox.setMaximumWidth(100)
        
        self.max_price_spinbox = QDoubleSpinBox()
        self.max_price_spinbox.setRange(0.0, 999999.99)
        self.max_price_spinbox.setValue(999999.99)
        self.max_price_spinbox.setPrefix("$")
        self.max_price_spinbox.setMaximumWidth(100)
        
        second_row.addWidget(price_label)
        second_row.addWidget(self.min_price_spinbox)
        second_row.addWidget(QLabel("to"))
        second_row.addWidget(self.max_price_spinbox)
        
        # Quantity range filter
        qty_label = QLabel("Quantity:")
        self.min_qty_spinbox = QSpinBox()
        self.min_qty_spinbox.setRange(0, 999999)
        self.min_qty_spinbox.setMaximumWidth(80)
        
        self.max_qty_spinbox = QSpinBox()
        self.max_qty_spinbox.setRange(0, 999999)
        self.max_qty_spinbox.setValue(999999)
        self.max_qty_spinbox.setMaximumWidth(80)
        
        second_row.addWidget(qty_label)
        second_row.addWidget(self.min_qty_spinbox)
        second_row.addWidget(QLabel("to"))
        second_row.addWidget(self.max_qty_spinbox)
        
        # Expiry date filter
        expiry_label = QLabel("Expiry:")
        self.expiry_filter_combo = QComboBox()
        self.expiry_filter_combo.addItems(["All", "Next 30 Days", "Next 60 Days", "Next 90 Days", "Past Due"])
        self.expiry_filter_combo.setMaximumWidth(120)
        
        second_row.addWidget(expiry_label)
        second_row.addWidget(self.expiry_filter_combo)
        
        second_row.addStretch()
        
        filter_layout.addLayout(second_row)
        
        # Third row - Sort and action buttons
        third_row = QHBoxLayout()
        
        # Sort options
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Name (A-Z)", "Name (Z-A)", 
            "Category (A-Z)", "Category (Z-A)",
            "Quantity (Low-High)", "Quantity (High-Low)",
            "Price (Low-High)", "Price (High-Low)",
            "Expiry (Earliest)", "Expiry (Latest)",
            "Recently Added", "Oldest First"
        ])
        self.sort_combo.setMaximumWidth(150)
        
        third_row.addWidget(sort_label)
        third_row.addWidget(self.sort_combo)
        
        third_row.addStretch()
        
        # Action buttons
        self.clear_filters_button = StyledButton("Clear Filters", "outline")
        self.clear_filters_button.setMaximumWidth(120)
        
        self.save_filter_button = StyledButton("Save Filter", "outline")
        self.save_filter_button.setMaximumWidth(100)
        
        self.advanced_search_button = StyledButton("Advanced", "outline")
        self.advanced_search_button.setMaximumWidth(80)
        self.advanced_search_button.setCheckable(True)
        
        third_row.addWidget(self.clear_filters_button)
        third_row.addWidget(self.save_filter_button)
        third_row.addWidget(self.advanced_search_button)
        
        filter_layout.addLayout(third_row)
        
        # Advanced search panel (initially hidden)
        self._create_advanced_search_panel(filter_layout)
        
        self.main_layout.addWidget(filter_frame)
    
    def _create_advanced_search_panel(self, parent_layout):
        """Create advanced search panel"""
        self.advanced_panel = QFrame()
        self.advanced_panel.setFrameStyle(QFrame.StyledPanel)
        self.advanced_panel.hide()  # Initially hidden
        
        advanced_layout = QVBoxLayout(self.advanced_panel)
        advanced_layout.setContentsMargins(15, 10, 15, 10)
        advanced_layout.setSpacing(10)
        
        # Advanced search title
        title_label = QLabel("Advanced Search Options")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        advanced_layout.addWidget(title_label)
        
        # Multi-criteria search
        criteria_layout = QGridLayout()
        
        # Batch number search
        criteria_layout.addWidget(QLabel("Batch Number:"), 0, 0)
        self.batch_search_field = ValidatedLineEdit("Search by batch number...")
        self.batch_search_field.textChanged.connect(self._apply_filters)
        criteria_layout.addWidget(self.batch_search_field, 0, 1)
        
        # Barcode search
        criteria_layout.addWidget(QLabel("Barcode:"), 0, 2)
        self.barcode_search_field = ValidatedLineEdit("Search by barcode...")
        self.barcode_search_field.textChanged.connect(self._apply_filters)
        criteria_layout.addWidget(self.barcode_search_field, 0, 3)
        
        # Profit margin filter
        criteria_layout.addWidget(QLabel("Profit Margin:"), 1, 0)
        self.min_margin_spinbox = QDoubleSpinBox()
        self.min_margin_spinbox.setRange(-100.0, 1000.0)
        self.min_margin_spinbox.setSuffix("%")
        self.min_margin_spinbox.valueChanged.connect(self._apply_filters)
        criteria_layout.addWidget(self.min_margin_spinbox, 1, 1)
        
        self.max_margin_spinbox = QDoubleSpinBox()
        self.max_margin_spinbox.setRange(-100.0, 1000.0)
        self.max_margin_spinbox.setValue(1000.0)
        self.max_margin_spinbox.setSuffix("%")
        self.max_margin_spinbox.valueChanged.connect(self._apply_filters)
        criteria_layout.addWidget(self.max_margin_spinbox, 1, 3)
        
        criteria_layout.addWidget(QLabel("to"), 1, 2)
        
        # Date range filters
        criteria_layout.addWidget(QLabel("Added After:"), 2, 0)
        self.added_after_date = QDateEdit()
        self.added_after_date.setDate(QDate.currentDate().addDays(-365))
        self.added_after_date.setCalendarPopup(True)
        self.added_after_date.dateChanged.connect(self._apply_filters)
        criteria_layout.addWidget(self.added_after_date, 2, 1)
        
        criteria_layout.addWidget(QLabel("Added Before:"), 2, 2)
        self.added_before_date = QDateEdit()
        self.added_before_date.setDate(QDate.currentDate())
        self.added_before_date.setCalendarPopup(True)
        self.added_before_date.dateChanged.connect(self._apply_filters)
        criteria_layout.addWidget(self.added_before_date, 2, 3)
        
        advanced_layout.addLayout(criteria_layout)
        
        # Saved filters section
        saved_filters_layout = QHBoxLayout()
        saved_filters_layout.addWidget(QLabel("Saved Filters:"))
        
        self.saved_filters_combo = QComboBox()
        self.saved_filters_combo.addItem("Select saved filter...")
        self.saved_filters_combo.currentTextChanged.connect(self._load_saved_filter)
        saved_filters_layout.addWidget(self.saved_filters_combo)
        
        self.delete_filter_button = StyledButton("Delete", "danger")
        self.delete_filter_button.setMaximumWidth(80)
        self.delete_filter_button.clicked.connect(self._delete_saved_filter)
        saved_filters_layout.addWidget(self.delete_filter_button)
        
        saved_filters_layout.addStretch()
        advanced_layout.addLayout(saved_filters_layout)
        
        parent_layout.addWidget(self.advanced_panel)
    
    def _create_table_section(self):
        """Create the main table"""
        # Create table
        self.table = StyledTable()
        self.table.setColumnCount(len(self.columns))
        
        # Set headers
        headers = [col[0] for col in self.columns]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        header = self.table.horizontalHeader()
        for i, (_, width) in enumerate(self.columns):
            header.resizeSection(i, width)
        
        # Configure table behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        
        # Set resize modes
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name column stretches
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        self.main_layout.addWidget(self.table)
    
    def _create_footer_section(self):
        """Create footer with statistics"""
        footer_layout = QHBoxLayout()
        
        # Statistics labels
        self.total_medicines_label = QLabel("Total: 0")
        self.low_stock_label = QLabel("Low Stock: 0")
        self.expired_label = QLabel("Expired: 0")
        self.total_value_label = QLabel("Total Value: $0.00")
        
        # Style statistics labels
        for label in [self.total_medicines_label, self.low_stock_label, 
                     self.expired_label, self.total_value_label]:
            label.setStyleSheet("font-weight: 500; color: #333333;")
        
        footer_layout.addWidget(self.total_medicines_label)
        footer_layout.addWidget(QLabel("|"))
        footer_layout.addWidget(self.low_stock_label)
        footer_layout.addWidget(QLabel("|"))
        footer_layout.addWidget(self.expired_label)
        footer_layout.addWidget(QLabel("|"))
        footer_layout.addWidget(self.total_value_label)
        footer_layout.addStretch()
        
        self.main_layout.addLayout(footer_layout)
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E1E5E9;
                border-radius: 6px;
            }
            
            QLabel {
                color: #333333;
                font-weight: 500;
            }
        """)
    
    def _connect_signals(self):
        """Connect widget signals"""
        # Button signals
        self.refresh_button.clicked.connect(self.refresh_data)
        self.auto_refresh_button.toggled.connect(self._toggle_auto_refresh)
        self.clear_filters_button.clicked.connect(self.clear_filters)
        self.save_filter_button.clicked.connect(self._save_current_filter)
        self.advanced_search_button.toggled.connect(self._toggle_advanced_search)
        
        # Search and filter signals
        self.search_field.textChanged.connect(self._on_search_changed)
        self.search_type_combo.currentTextChanged.connect(self._on_search_type_changed)
        self.category_filter_combo.currentTextChanged.connect(self._on_category_filter_changed)
        self.stock_filter_combo.currentTextChanged.connect(self._on_stock_filter_changed)
        self.min_price_spinbox.valueChanged.connect(self._on_price_filter_changed)
        self.max_price_spinbox.valueChanged.connect(self._on_price_filter_changed)
        self.min_qty_spinbox.valueChanged.connect(self._on_quantity_filter_changed)
        self.max_qty_spinbox.valueChanged.connect(self._on_quantity_filter_changed)
        self.expiry_filter_combo.currentTextChanged.connect(self._on_expiry_filter_changed)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        
        # Table signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _setup_context_menu(self):
        """Set up context menu for table"""
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
    
    def _toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh functionality"""
        if enabled:
            self.refresh_timer.start(30000)  # Refresh every 30 seconds
            self.auto_refresh_button.setText("Auto-Refresh: ON")
            self.logger.info("Auto-refresh enabled")
        else:
            self.refresh_timer.stop()
            self.auto_refresh_button.setText("Auto-Refresh: OFF")
            self.logger.info("Auto-refresh disabled")
    
    def _on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_query = text.strip()
        self._apply_filters()
    
    def _on_search_type_changed(self, search_type: str):
        """Handle search type change"""
        self.search_type = search_type
        self._apply_filters()
    
    def _on_category_filter_changed(self, category: str):
        """Handle category filter change"""
        self.category_filter = category if category != "All Categories" else ""
        self._apply_filters()
    
    def _on_stock_filter_changed(self, status: str):
        """Handle stock status filter change"""
        self.stock_filter = status if status != "All" else ""
        self._apply_filters()
    
    def _on_price_filter_changed(self):
        """Handle price filter change"""
        self.min_price = self.min_price_spinbox.value()
        self.max_price = self.max_price_spinbox.value()
        self._apply_filters()
    
    def _on_quantity_filter_changed(self):
        """Handle quantity filter change"""
        self.min_quantity = self.min_qty_spinbox.value()
        self.max_quantity = self.max_qty_spinbox.value()
        self._apply_filters()
    
    def _on_expiry_filter_changed(self, expiry_filter: str):
        """Handle expiry filter change"""
        self.expiry_filter = expiry_filter
        self._apply_filters()
    
    def _on_sort_changed(self, sort_option: str):
        """Handle sort option change"""
        self.sort_option = sort_option
        self._apply_filters()
    
    def _toggle_advanced_search(self, enabled: bool):
        """Toggle advanced search panel"""
        if enabled:
            self.advanced_panel.show()
            self.advanced_search_button.setText("Hide Advanced")
        else:
            self.advanced_panel.hide()
            self.advanced_search_button.setText("Advanced")
    
    def _save_current_filter(self):
        """Save current filter settings"""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Save Filter", "Enter filter name:")
        if ok and name.strip():
            filter_settings = {
                'search_query': self.search_query,
                'search_type': self.search_type,
                'category_filter': self.category_filter,
                'stock_filter': self.stock_filter,
                'min_price': self.min_price,
                'max_price': self.max_price,
                'min_quantity': self.min_quantity,
                'max_quantity': self.max_quantity,
                'expiry_filter': self.expiry_filter,
                'sort_option': self.sort_option
            }
            
            self.saved_filters[name.strip()] = filter_settings
            self._update_saved_filters_combo()
            self.logger.info(f"Filter saved: {name.strip()}")
    
    def _load_saved_filter(self, filter_name: str):
        """Load saved filter settings"""
        if filter_name in self.saved_filters:
            settings = self.saved_filters[filter_name]
            
            # Apply settings to UI controls
            self.search_field.setText(settings.get('search_query', ''))
            
            # Find and set search type
            search_type_index = self.search_type_combo.findText(settings.get('search_type', 'All Fields'))
            if search_type_index >= 0:
                self.search_type_combo.setCurrentIndex(search_type_index)
            
            # Find and set category
            category_index = self.category_filter_combo.findText(settings.get('category_filter', '') or 'All Categories')
            if category_index >= 0:
                self.category_filter_combo.setCurrentIndex(category_index)
            
            # Find and set stock filter
            stock_index = self.stock_filter_combo.findText(settings.get('stock_filter', '') or 'All')
            if stock_index >= 0:
                self.stock_filter_combo.setCurrentIndex(stock_index)
            
            # Set price range
            self.min_price_spinbox.setValue(settings.get('min_price', 0.0))
            self.max_price_spinbox.setValue(settings.get('max_price', 999999.99))
            
            # Set quantity range
            self.min_qty_spinbox.setValue(settings.get('min_quantity', 0))
            self.max_qty_spinbox.setValue(settings.get('max_quantity', 999999))
            
            # Find and set expiry filter
            expiry_index = self.expiry_filter_combo.findText(settings.get('expiry_filter', 'All'))
            if expiry_index >= 0:
                self.expiry_filter_combo.setCurrentIndex(expiry_index)
            
            # Find and set sort option
            sort_index = self.sort_combo.findText(settings.get('sort_option', 'Name (A-Z)'))
            if sort_index >= 0:
                self.sort_combo.setCurrentIndex(sort_index)
            
            self.logger.info(f"Filter loaded: {filter_name}")
    
    def _delete_saved_filter(self):
        """Delete selected saved filter"""
        current_filter = self.saved_filters_combo.currentText()
        if current_filter in self.saved_filters:
            del self.saved_filters[current_filter]
            self._update_saved_filters_combo()
            self.logger.info(f"Filter deleted: {current_filter}")
    
    def _update_saved_filters_combo(self):
        """Update saved filters combo box"""
        current_selection = self.saved_filters_combo.currentText()
        self.saved_filters_combo.clear()
        self.saved_filters_combo.addItem("Select saved filter...")
        
        for filter_name in sorted(self.saved_filters.keys()):
            self.saved_filters_combo.addItem(filter_name)
        
        # Restore selection if still valid
        index = self.saved_filters_combo.findText(current_selection)
        if index >= 0:
            self.saved_filters_combo.setCurrentIndex(index)
    
    def _on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            if 0 <= row < len(self.filtered_medicines):
                self.selected_medicine = self.filtered_medicines[row]
                self.medicine_selected.emit(self.selected_medicine)
            else:
                self.selected_medicine = None
        else:
            self.selected_medicine = None
    
    def _on_item_double_clicked(self, item: QTableWidgetItem):
        """Handle item double click"""
        if self.selected_medicine:
            self.edit_requested.emit(self.selected_medicine)
    
    def _show_context_menu(self, position):
        """Show context menu"""
        if not self.selected_medicine:
            return
        
        menu = QMenu(self)
        
        # Edit action
        edit_action = QAction("Edit Medicine", self)
        edit_action.triggered.connect(lambda: self.edit_requested.emit(self.selected_medicine))
        menu.addAction(edit_action)
        
        # Delete action
        delete_action = QAction("Delete Medicine", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.selected_medicine))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # View details action
        details_action = QAction("View Details", self)
        details_action.triggered.connect(self._show_medicine_details)
        menu.addAction(details_action)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def _show_medicine_details(self):
        """Show detailed medicine information"""
        if not self.selected_medicine:
            return
        
        medicine = self.selected_medicine
        details = f"""
Medicine Details:

Name: {medicine.name}
Category: {medicine.category}
Batch Number: {medicine.batch_no}
Expiry Date: {medicine.expiry_date}
Quantity: {medicine.quantity}
Purchase Price: ${medicine.purchase_price:.2f}
Selling Price: ${medicine.selling_price:.2f}
Barcode: {medicine.barcode or 'N/A'}
Profit Margin: {medicine.get_profit_margin():.1f}%
Total Value: ${medicine.get_total_value():.2f}
Status: {medicine.get_stock_status()}
        """.strip()
        
        QMessageBox.information(self, f"Medicine Details - {medicine.name}", details)
    
    def refresh_data(self):
        """Refresh medicine data from database"""
        try:
            self.medicines = self.medicine_manager.get_all_medicines()
            self._update_category_filter()
            self._apply_filters()
            self._update_statistics()
            self.logger.info(f"Refreshed medicine data: {len(self.medicines)} medicines loaded")
        except Exception as e:
            self.logger.error(f"Error refreshing medicine data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh data: {str(e)}")
    
    def _update_category_filter(self):
        """Update category filter options"""
        current_selection = self.category_filter_combo.currentText()
        
        # Get unique categories
        categories = ["All Categories"] + sorted(set(medicine.category for medicine in self.medicines))
        
        # Update combo box
        self.category_filter_combo.clear()
        self.category_filter_combo.addItems(categories)
        
        # Restore selection if still valid
        index = self.category_filter_combo.findText(current_selection)
        if index >= 0:
            self.category_filter_combo.setCurrentIndex(index)
    
    def _apply_filters(self):
        """Apply search and filter criteria"""
        self.filtered_medicines = self.medicines.copy()
        
        # Apply search filter based on search type
        if self.search_query:
            query_lower = self.search_query.lower()
            
            if self.search_type == "All Fields":
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if (query_lower in medicine.name.lower() or 
                        query_lower in medicine.category.lower() or
                        query_lower in medicine.batch_no.lower() or
                        (medicine.barcode and query_lower in medicine.barcode.lower()))
                ]
            elif self.search_type == "Name Only":
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if query_lower in medicine.name.lower()
                ]
            elif self.search_type == "Category Only":
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if query_lower in medicine.category.lower()
                ]
            elif self.search_type == "Batch Number":
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if query_lower in medicine.batch_no.lower()
                ]
            elif self.search_type == "Barcode Only":
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if medicine.barcode and query_lower in medicine.barcode.lower()
                ]
        
        # Apply advanced search filters if panel is visible or if fields have values (for testing)
        apply_advanced = (hasattr(self, 'advanced_panel') and 
                         (self.advanced_panel.isVisible() or 
                          (hasattr(self, 'batch_search_field') and self.batch_search_field.text().strip()) or
                          (hasattr(self, 'barcode_search_field') and self.barcode_search_field.text().strip())))
        
        if apply_advanced:
            # Batch number filter
            if hasattr(self, 'batch_search_field') and self.batch_search_field.text().strip():
                batch_query = self.batch_search_field.text().strip().lower()
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if batch_query in medicine.batch_no.lower()
                ]
            
            # Barcode filter
            if hasattr(self, 'barcode_search_field') and self.barcode_search_field.text().strip():
                barcode_query = self.barcode_search_field.text().strip().lower()
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if medicine.barcode and barcode_query in medicine.barcode.lower()
                ]
            
            # Profit margin filter (only if panel is actually visible or values are non-default)
            if (hasattr(self, 'min_margin_spinbox') and hasattr(self, 'max_margin_spinbox') and
                hasattr(self, 'advanced_panel') and self.advanced_panel.isVisible()):
                min_margin = self.min_margin_spinbox.value()
                max_margin = self.max_margin_spinbox.value()
                if min_margin != 0.0 or max_margin != 1000.0:  # Only apply if values changed from defaults
                    self.filtered_medicines = [
                        medicine for medicine in self.filtered_medicines
                        if min_margin <= medicine.get_profit_margin() <= max_margin
                    ]
            
            # Date range filter (only if panel is actually visible)
            if (hasattr(self, 'added_after_date') and hasattr(self, 'added_before_date') and
                hasattr(self, 'advanced_panel') and self.advanced_panel.isVisible()):
                from datetime import datetime
                start_date = self.added_after_date.date().toPython()
                end_date = self.added_before_date.date().toPython()
                
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if medicine.created_at and start_date <= datetime.strptime(medicine.created_at, "%Y-%m-%d").date() <= end_date
                ]
        
        # Apply category filter
        if self.category_filter:
            self.filtered_medicines = [
                medicine for medicine in self.filtered_medicines
                if medicine.category == self.category_filter
            ]
        
        # Apply stock status filter
        if self.stock_filter:
            if self.stock_filter == "In Stock":
                self.filtered_medicines = [m for m in self.filtered_medicines if m.quantity > 10]
            elif self.stock_filter == "Low Stock":
                self.filtered_medicines = [m for m in self.filtered_medicines if 0 < m.quantity <= 10]
            elif self.stock_filter == "Out of Stock":
                self.filtered_medicines = [m for m in self.filtered_medicines if m.quantity == 0]
            elif self.stock_filter == "Expired":
                self.filtered_medicines = [m for m in self.filtered_medicines if m.is_expired()]
            elif self.stock_filter == "Expiring Soon":
                self.filtered_medicines = [m for m in self.filtered_medicines if m.is_expiring_soon()]
        
        # Apply price range filter
        self.filtered_medicines = [
            medicine for medicine in self.filtered_medicines
            if self.min_price <= medicine.selling_price <= self.max_price
        ]
        
        # Apply quantity range filter
        self.filtered_medicines = [
            medicine for medicine in self.filtered_medicines
            if self.min_quantity <= medicine.quantity <= self.max_quantity
        ]
        
        # Apply expiry filter
        if self.expiry_filter != "All":
            from datetime import date, timedelta, datetime
            today = date.today()
            
            if self.expiry_filter == "Next 30 Days":
                future_date = today + timedelta(days=30)
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if today <= datetime.strptime(medicine.expiry_date, "%Y-%m-%d").date() <= future_date
                ]
            elif self.expiry_filter == "Next 60 Days":
                future_date = today + timedelta(days=60)
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if today <= datetime.strptime(medicine.expiry_date, "%Y-%m-%d").date() <= future_date
                ]
            elif self.expiry_filter == "Next 90 Days":
                future_date = today + timedelta(days=90)
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if today <= datetime.strptime(medicine.expiry_date, "%Y-%m-%d").date() <= future_date
                ]
            elif self.expiry_filter == "Past Due":
                self.filtered_medicines = [
                    medicine for medicine in self.filtered_medicines
                    if medicine.is_expired()
                ]
        
        # Apply sorting
        self._sort_medicines()
        
        self._populate_table()
        self._update_statistics()
    
    def _sort_medicines(self):
        """Sort filtered medicines based on selected option"""
        if self.sort_option == "Name (A-Z)":
            self.filtered_medicines.sort(key=lambda m: m.name.lower())
        elif self.sort_option == "Name (Z-A)":
            self.filtered_medicines.sort(key=lambda m: m.name.lower(), reverse=True)
        elif self.sort_option == "Category (A-Z)":
            self.filtered_medicines.sort(key=lambda m: (m.category.lower(), m.name.lower()))
        elif self.sort_option == "Category (Z-A)":
            self.filtered_medicines.sort(key=lambda m: (m.category.lower(), m.name.lower()), reverse=True)
        elif self.sort_option == "Quantity (Low-High)":
            self.filtered_medicines.sort(key=lambda m: m.quantity)
        elif self.sort_option == "Quantity (High-Low)":
            self.filtered_medicines.sort(key=lambda m: m.quantity, reverse=True)
        elif self.sort_option == "Price (Low-High)":
            self.filtered_medicines.sort(key=lambda m: m.selling_price)
        elif self.sort_option == "Price (High-Low)":
            self.filtered_medicines.sort(key=lambda m: m.selling_price, reverse=True)
        elif self.sort_option == "Expiry (Earliest)":
            self.filtered_medicines.sort(key=lambda m: m.expiry_date)
        elif self.sort_option == "Expiry (Latest)":
            self.filtered_medicines.sort(key=lambda m: m.expiry_date, reverse=True)
        elif self.sort_option == "Recently Added":
            self.filtered_medicines.sort(key=lambda m: m.created_at or "", reverse=True)
        elif self.sort_option == "Oldest First":
            self.filtered_medicines.sort(key=lambda m: m.created_at or "")
    
    def _populate_table(self):
        """Populate table with filtered medicine data"""
        self.table.setRowCount(len(self.filtered_medicines))
        
        for row, medicine in enumerate(self.filtered_medicines):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(medicine.id or '')))
            
            # Name
            name_item = QTableWidgetItem(medicine.name)
            name_item.setFont(QFont("", -1, QFont.Bold))
            self.table.setItem(row, 1, name_item)
            
            # Category
            self.table.setItem(row, 2, QTableWidgetItem(medicine.category))
            
            # Batch No
            self.table.setItem(row, 3, QTableWidgetItem(medicine.batch_no))
            
            # Expiry Date
            expiry_item = QTableWidgetItem(medicine.expiry_date)
            if medicine.is_expired():
                expiry_item.setBackground(QBrush(QColor("#FFEBEE")))
                expiry_item.setForeground(QBrush(QColor("#C62828")))
            elif medicine.is_expiring_soon():
                expiry_item.setBackground(QBrush(QColor("#FFF3E0")))
                expiry_item.setForeground(QBrush(QColor("#F57C00")))
            self.table.setItem(row, 4, expiry_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(str(medicine.quantity))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            if medicine.quantity == 0:
                quantity_item.setBackground(QBrush(QColor("#FFEBEE")))
                quantity_item.setForeground(QBrush(QColor("#C62828")))
            elif medicine.is_low_stock():
                quantity_item.setBackground(QBrush(QColor("#FFF3E0")))
                quantity_item.setForeground(QBrush(QColor("#F57C00")))
            self.table.setItem(row, 5, quantity_item)
            
            # Purchase Price
            purchase_item = QTableWidgetItem(f"${medicine.purchase_price:.2f}")
            purchase_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 6, purchase_item)
            
            # Selling Price
            selling_item = QTableWidgetItem(f"${medicine.selling_price:.2f}")
            selling_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 7, selling_item)
            
            # Barcode
            self.table.setItem(row, 8, QTableWidgetItem(medicine.barcode or ''))
            
            # Status
            status_item = QTableWidgetItem(medicine.get_stock_status())
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code status
            status = medicine.get_stock_status()
            if status == "Out of Stock":
                status_item.setBackground(QBrush(QColor("#FFEBEE")))
                status_item.setForeground(QBrush(QColor("#C62828")))
            elif status == "Low Stock":
                status_item.setBackground(QBrush(QColor("#FFF3E0")))
                status_item.setForeground(QBrush(QColor("#F57C00")))
            else:
                status_item.setBackground(QBrush(QColor("#E8F5E8")))
                status_item.setForeground(QBrush(QColor("#2E7D32")))
            
            self.table.setItem(row, 9, status_item)
        
        # Adjust row heights
        self.table.resizeRowsToContents()
    
    def _update_statistics(self):
        """Update footer statistics"""
        total_medicines = len(self.filtered_medicines)
        low_stock_count = sum(1 for m in self.filtered_medicines if m.is_low_stock())
        expired_count = sum(1 for m in self.filtered_medicines if m.is_expired())
        total_value = sum(m.get_total_value() for m in self.filtered_medicines)
        
        self.total_medicines_label.setText(f"Total: {total_medicines}")
        self.low_stock_label.setText(f"Low Stock: {low_stock_count}")
        self.expired_label.setText(f"Expired: {expired_count}")
        self.total_value_label.setText(f"Total Value: ${total_value:.2f}")
        
        # Color code statistics
        if low_stock_count > 0:
            self.low_stock_label.setStyleSheet("font-weight: 500; color: #F57C00;")
        else:
            self.low_stock_label.setStyleSheet("font-weight: 500; color: #333333;")
        
        if expired_count > 0:
            self.expired_label.setStyleSheet("font-weight: 500; color: #C62828;")
        else:
            self.expired_label.setStyleSheet("font-weight: 500; color: #333333;")
    
    def clear_filters(self):
        """Clear all filters and search"""
        # Clear basic filters
        self.search_field.clear()
        self.search_type_combo.setCurrentIndex(0)
        self.category_filter_combo.setCurrentIndex(0)
        self.stock_filter_combo.setCurrentIndex(0)
        
        # Clear price and quantity ranges
        self.min_price_spinbox.setValue(0.0)
        self.max_price_spinbox.setValue(999999.99)
        self.min_qty_spinbox.setValue(0)
        self.max_qty_spinbox.setValue(999999)
        
        # Clear expiry and sort filters
        self.expiry_filter_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        
        # Clear advanced search fields if they exist
        if hasattr(self, 'batch_search_field'):
            self.batch_search_field.clear()
        if hasattr(self, 'barcode_search_field'):
            self.barcode_search_field.clear()
        if hasattr(self, 'min_margin_spinbox'):
            self.min_margin_spinbox.setValue(-100.0)
        if hasattr(self, 'max_margin_spinbox'):
            self.max_margin_spinbox.setValue(1000.0)
        
        # Reset filter state
        self.search_query = ""
        self.search_type = "All Fields"
        self.category_filter = ""
        self.stock_filter = ""
        self.min_price = 0.0
        self.max_price = 999999.99
        self.min_quantity = 0
        self.max_quantity = 999999
        self.expiry_filter = "All"
        self.sort_option = "Name (A-Z)"
        
        # Clear saved filter selection
        if hasattr(self, 'saved_filters_combo'):
            self.saved_filters_combo.setCurrentIndex(0)
        
        self._apply_filters()
        self.logger.info("All filters cleared")
    
    def get_selected_medicine(self) -> Optional[Medicine]:
        """Get currently selected medicine"""
        return self.selected_medicine
    
    def select_medicine_by_id(self, medicine_id: int):
        """Select medicine by ID"""
        for row, medicine in enumerate(self.filtered_medicines):
            if medicine.id == medicine_id:
                self.table.selectRow(row)
                break
    
    def add_medicine_to_table(self, medicine: Medicine):
        """Add new medicine to table (for real-time updates)"""
        self.medicines.append(medicine)
        self._update_category_filter()
        self._apply_filters()
        self.logger.info(f"Added medicine to table: {medicine.name}")
    
    def update_medicine_in_table(self, medicine: Medicine):
        """Update existing medicine in table"""
        for i, existing_medicine in enumerate(self.medicines):
            if existing_medicine.id == medicine.id:
                self.medicines[i] = medicine
                break
        
        self._update_category_filter()
        self._apply_filters()
        self.logger.info(f"Updated medicine in table: {medicine.name}")
    
    def remove_medicine_from_table(self, medicine_id: int):
        """Remove medicine from table"""
        self.medicines = [m for m in self.medicines if m.id != medicine_id]
        self._update_category_filter()
        self._apply_filters()
        self.logger.info(f"Removed medicine from table: ID {medicine_id}")