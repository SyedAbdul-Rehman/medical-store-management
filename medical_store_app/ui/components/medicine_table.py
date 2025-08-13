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
    QFrame, QSizePolicy, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer
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
        self.category_filter = ""
        self.stock_filter = ""
        
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
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        
        # Search field
        search_label = QLabel("Search:")
        self.search_field = ValidatedLineEdit("Search by name or barcode...")
        self.search_field.setMaximumWidth(250)
        
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_field)
        
        # Category filter
        category_label = QLabel("Category:")
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.setMaximumWidth(150)
        
        filter_layout.addWidget(category_label)
        filter_layout.addWidget(self.category_filter_combo)
        
        # Stock status filter
        stock_label = QLabel("Stock Status:")
        self.stock_filter_combo = QComboBox()
        self.stock_filter_combo.addItems(["All", "In Stock", "Low Stock", "Out of Stock", "Expired", "Expiring Soon"])
        self.stock_filter_combo.setMaximumWidth(120)
        
        filter_layout.addWidget(stock_label)
        filter_layout.addWidget(self.stock_filter_combo)
        
        filter_layout.addStretch()
        
        # Clear filters button
        self.clear_filters_button = StyledButton("Clear Filters", "outline")
        self.clear_filters_button.setMaximumWidth(120)
        filter_layout.addWidget(self.clear_filters_button)
        
        self.main_layout.addWidget(filter_frame)
    
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
        
        # Search and filter signals
        self.search_field.textChanged.connect(self._on_search_changed)
        self.category_filter_combo.currentTextChanged.connect(self._on_category_filter_changed)
        self.stock_filter_combo.currentTextChanged.connect(self._on_stock_filter_changed)
        
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
    
    def _on_category_filter_changed(self, category: str):
        """Handle category filter change"""
        self.category_filter = category if category != "All Categories" else ""
        self._apply_filters()
    
    def _on_stock_filter_changed(self, status: str):
        """Handle stock status filter change"""
        self.stock_filter = status if status != "All" else ""
        self._apply_filters()
    
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
        
        # Apply search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            self.filtered_medicines = [
                medicine for medicine in self.filtered_medicines
                if (query_lower in medicine.name.lower() or 
                    (medicine.barcode and query_lower in medicine.barcode.lower()))
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
        
        self._populate_table()
        self._update_statistics()
    
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
        self.search_field.clear()
        self.category_filter_combo.setCurrentIndex(0)
        self.stock_filter_combo.setCurrentIndex(0)
        self.search_query = ""
        self.category_filter = ""
        self.stock_filter = ""
        self._apply_filters()
        self.logger.info("Filters cleared")
    
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