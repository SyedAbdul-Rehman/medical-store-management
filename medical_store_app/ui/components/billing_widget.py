"""
Billing system UI components for Medical Store Management Application
Implements product search, cart management, and transaction processing
"""

import logging
from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox,
    QMessageBox, QSplitter, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette

from ...managers.medicine_manager import MedicineManager
from ...managers.sales_manager import SalesManager
from ...models.medicine import Medicine
from ...models.sale import SaleItem


class ProductSearchWidget(QWidget):
    """Widget for searching and selecting products for billing"""
    
    # Signal emitted when a product is selected for adding to cart
    product_selected = Signal(Medicine, int)  # medicine, quantity
    
    def __init__(self, medicine_manager: MedicineManager, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.logger = logging.getLogger(__name__)
        
        # Search timer for delayed search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Search section
        search_group = QGroupBox("Product Search")
        search_layout = QVBoxLayout(search_group)
        
        # Search input
        search_input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or barcode...")
        self.search_input.setMinimumHeight(35)
        
        self.search_button = QPushButton("Search")
        self.search_button.setMinimumHeight(35)
        self.search_button.setMinimumWidth(80)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.setMinimumWidth(80)
        
        search_input_layout.addWidget(QLabel("Search:"))
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_input_layout.addWidget(self.clear_button)
        
        search_layout.addLayout(search_input_layout)
        
        # Search results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Name", "Category", "Batch No", "Stock", "Price", "Expiry", "Action"
        ])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Batch No
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Stock
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Price
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Expiry
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Action
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setMinimumHeight(300)
        
        search_layout.addWidget(self.results_table)
        
        # Quick add section
        quick_add_layout = QHBoxLayout()
        
        quick_add_layout.addWidget(QLabel("Quick Add:"))
        
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setMaximum(9999)
        self.quantity_spinbox.setValue(1)
        self.quantity_spinbox.setMinimumHeight(30)
        
        self.add_to_cart_button = QPushButton("Add to Cart")
        self.add_to_cart_button.setMinimumHeight(30)
        self.add_to_cart_button.setEnabled(False)
        
        quick_add_layout.addWidget(QLabel("Quantity:"))
        quick_add_layout.addWidget(self.quantity_spinbox)
        quick_add_layout.addWidget(self.add_to_cart_button)
        quick_add_layout.addStretch()
        
        search_layout.addLayout(quick_add_layout)
        
        layout.addWidget(search_group)
        
        # Status label
        self.status_label = QLabel("Enter search term to find products")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Store selected medicine
        self.selected_medicine: Optional[Medicine] = None
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._perform_search)
        self.search_button.clicked.connect(self._perform_search)
        self.clear_button.clicked.connect(self.clear_search)
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.add_to_cart_button.clicked.connect(self._add_selected_to_cart)
        self.results_table.cellDoubleClicked.connect(self._on_cell_double_clicked)
    
    def _on_search_text_changed(self):
        """Handle search text changes with delay"""
        self.search_timer.stop()
        if self.search_input.text().strip():
            self.search_timer.start(500)  # 500ms delay
        else:
            self.clear_results()
    
    def _perform_search(self):
        """Perform product search"""
        query = self.search_input.text().strip()
        if not query:
            self.clear_results()
            return
        
        try:
            self.status_label.setText("Searching...")
            
            # Search medicines
            medicines = self.medicine_manager.search_medicines(query)
            
            # Filter out medicines with no stock
            available_medicines = [m for m in medicines if m.quantity > 0]
            
            self._populate_results(available_medicines)
            
            if available_medicines:
                self.status_label.setText(f"Found {len(available_medicines)} product(s)")
            else:
                self.status_label.setText("No products found or all out of stock")
                
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            self.status_label.setText("Error occurred during search")
            QMessageBox.warning(self, "Search Error", f"Error searching products: {str(e)}")
    
    def _populate_results(self, medicines: List[Medicine]):
        """Populate search results table"""
        self.results_table.setRowCount(len(medicines))
        
        for row, medicine in enumerate(medicines):
            # Name
            name_item = QTableWidgetItem(medicine.name)
            name_item.setData(Qt.ItemDataRole.UserRole, medicine)
            self.results_table.setItem(row, 0, name_item)
            
            # Category
            self.results_table.setItem(row, 1, QTableWidgetItem(medicine.category))
            
            # Batch No
            self.results_table.setItem(row, 2, QTableWidgetItem(medicine.batch_no))
            
            # Stock
            stock_item = QTableWidgetItem(str(medicine.quantity))
            if medicine.is_low_stock():
                stock_item.setBackground(QPalette().color(QPalette.ColorRole.Base))
                stock_item.setForeground(QPalette().color(QPalette.ColorRole.Text))
            self.results_table.setItem(row, 3, stock_item)
            
            # Price - use currency formatting from parent billing widget
            price_text = f"${medicine.selling_price:.2f}"  # Default formatting
            try:
                # Try to get currency formatting from parent
                parent_widget = self.parent()
                while parent_widget and not hasattr(parent_widget, 'sales_manager'):
                    parent_widget = parent_widget.parent()
                if parent_widget and hasattr(parent_widget, 'sales_manager'):
                    price_text = parent_widget.sales_manager.format_currency(medicine.selling_price)
            except:
                pass  # Use default formatting
            price_item = QTableWidgetItem(price_text)
            self.results_table.setItem(row, 4, price_item)
            
            # Expiry
            expiry_item = QTableWidgetItem(medicine.expiry_date)
            if medicine.is_expired():
                expiry_item.setBackground(QPalette().color(QPalette.ColorRole.Base))
                expiry_item.setForeground(QPalette().color(QPalette.ColorRole.Text))
            elif medicine.is_expiring_soon():
                expiry_item.setBackground(QPalette().color(QPalette.ColorRole.Base))
                expiry_item.setForeground(QPalette().color(QPalette.ColorRole.Text))
            self.results_table.setItem(row, 5, expiry_item)
            
            # Action button
            add_button = QPushButton("Add")
            add_button.setMinimumHeight(25)
            add_button.clicked.connect(lambda checked, m=medicine: self._add_medicine_to_cart(m))
            self.results_table.setCellWidget(row, 6, add_button)
    
    def _on_selection_changed(self):
        """Handle table selection changes"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            name_item = self.results_table.item(current_row, 0)
            if name_item:
                self.selected_medicine = name_item.data(Qt.ItemDataRole.UserRole)
                self.add_to_cart_button.setEnabled(True)
            else:
                self.selected_medicine = None
                self.add_to_cart_button.setEnabled(False)
        else:
            self.selected_medicine = None
            self.add_to_cart_button.setEnabled(False)
    
    def _on_cell_double_clicked(self, row: int, column: int):
        """Handle cell double click to add to cart"""
        name_item = self.results_table.item(row, 0)
        if name_item:
            medicine = name_item.data(Qt.ItemDataRole.UserRole)
            self._add_medicine_to_cart(medicine)
    
    def _add_selected_to_cart(self):
        """Add selected medicine to cart"""
        if self.selected_medicine:
            quantity = self.quantity_spinbox.value()
            self._add_medicine_to_cart(self.selected_medicine, quantity)
    
    def _add_medicine_to_cart(self, medicine: Medicine, quantity: int = 1):
        """Add medicine to cart with specified quantity"""
        try:
            # Validate stock availability
            if not medicine.can_sell(quantity):
                QMessageBox.warning(
                    self, 
                    "Insufficient Stock", 
                    f"Cannot add {quantity} units of {medicine.name}.\n"
                    f"Available stock: {medicine.quantity}"
                )
                return
            
            # Emit signal to parent widget
            self.product_selected.emit(medicine, quantity)
            
            # Reset quantity spinbox
            self.quantity_spinbox.setValue(1)
            
            self.logger.info(f"Added {quantity} units of {medicine.name} to cart")
            
        except Exception as e:
            self.logger.error(f"Error adding medicine to cart: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error adding product to cart: {str(e)}")
    
    def clear_search(self):
        """Clear search input and results"""
        self.search_input.clear()
        self.clear_results()
    
    def clear_results(self):
        """Clear search results"""
        self.results_table.setRowCount(0)
        self.selected_medicine = None
        self.add_to_cart_button.setEnabled(False)
        self.status_label.setText("Enter search term to find products")
    
    def focus_search(self):
        """Set focus to search input"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def refresh_results(self):
        """Refresh search results with updated settings (e.g., currency formatting)"""
        try:
            # If there are current results, refresh them to update currency formatting
            if self.results_table.rowCount() > 0:
                current_query = self.search_input.text().strip()
                if current_query:
                    self._perform_search()
        except Exception as e:
            self.logger.error(f"Error refreshing search results: {str(e)}")


class CartWidget(QWidget):
    """Widget for displaying and managing shopping cart"""
    
    # Signals
    cart_updated = Signal()  # Emitted when cart contents change
    
    def __init__(self, sales_manager: SalesManager, parent=None):
        super().__init__(parent)
        self.sales_manager = sales_manager
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_connections()
        self.refresh_cart()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Cart header
        header_layout = QHBoxLayout()
        
        cart_title = QLabel("Shopping Cart")
        cart_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.cart_count_label = QLabel("0 items")
        self.cart_count_label.setStyleSheet("color: #666; font-style: italic;")
        
        self.clear_cart_button = QPushButton("Clear All")
        self.clear_cart_button.setMaximumWidth(80)
        self.clear_cart_button.setEnabled(False)
        
        header_layout.addWidget(cart_title)
        header_layout.addStretch()
        header_layout.addWidget(self.cart_count_label)
        header_layout.addWidget(self.clear_cart_button)
        
        layout.addLayout(header_layout)
        
        # Cart items table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels([
            "Item", "Qty", "Unit Price", "Total", "Actions", ""
        ])
        
        # Configure table
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Item name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Quantity
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Unit Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Total
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Remove button
        
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cart_table.setMinimumHeight(200)
        self.cart_table.setMaximumHeight(300)
        
        layout.addWidget(self.cart_table)
        
        # Empty cart message
        self.empty_cart_label = QLabel("Cart is empty\nAdd products from the search panel")
        self.empty_cart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_cart_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
        layout.addWidget(self.empty_cart_label)
        
        # Discount and tax section
        adjustments_group = QGroupBox("Adjustments")
        adjustments_layout = QGridLayout(adjustments_group)
        
        # Discount
        adjustments_layout.addWidget(QLabel("Discount ($):"), 0, 0)
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0.0)
        self.discount_input.setMaximum(99999.99)
        self.discount_input.setDecimals(2)
        self.discount_input.setValue(0.0)
        self.discount_input.setMinimumHeight(30)
        adjustments_layout.addWidget(self.discount_input, 0, 1)
        
        # Tax rate
        adjustments_layout.addWidget(QLabel("Tax Rate (%):"), 1, 0)
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setMinimum(0.0)
        self.tax_rate_input.setMaximum(100.0)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setValue(0.0)
        self.tax_rate_input.setMinimumHeight(30)
        adjustments_layout.addWidget(self.tax_rate_input, 1, 1)
        
        layout.addWidget(adjustments_group)
        
        # Totals section
        totals_group = QGroupBox("Order Summary")
        totals_layout = QGridLayout(totals_group)
        
        # Subtotal
        totals_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.subtotal_label.setStyleSheet("font-weight: bold;")
        totals_layout.addWidget(self.subtotal_label, 0, 1)
        
        # Discount amount
        totals_layout.addWidget(QLabel("Discount:"), 1, 0)
        self.discount_amount_label = QLabel("$0.00")
        self.discount_amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.discount_amount_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        totals_layout.addWidget(self.discount_amount_label, 1, 1)
        
        # Tax amount
        totals_layout.addWidget(QLabel("Tax:"), 2, 0)
        self.tax_amount_label = QLabel("$0.00")
        self.tax_amount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.tax_amount_label.setStyleSheet("font-weight: bold;")
        totals_layout.addWidget(self.tax_amount_label, 2, 1)
        
        # Total
        total_frame = QFrame()
        total_frame.setFrameStyle(QFrame.Shape.Box)
        total_frame.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        total_layout = QHBoxLayout(total_frame)
        
        total_label = QLabel("TOTAL:")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.total_label = QLabel("$0.00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #2D9CDB;")
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        
        totals_layout.addWidget(total_frame, 3, 0, 1, 2)
        
        layout.addWidget(totals_group)
        
        # Payment method section
        payment_group = QGroupBox("Payment & Checkout")
        payment_layout = QVBoxLayout(payment_group)
        
        # Payment method selection
        payment_method_layout = QHBoxLayout()
        payment_method_layout.addWidget(QLabel("Payment Method:"))
        
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "Card", "UPI", "Cheque", "Bank Transfer"])
        self.payment_method_combo.setCurrentText("Cash")
        self.payment_method_combo.setMinimumHeight(30)
        payment_method_layout.addWidget(self.payment_method_combo)
        payment_method_layout.addStretch()
        
        payment_layout.addLayout(payment_method_layout)
        
        # Customer details (optional)
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Customer Name:"))
        
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Optional")
        self.customer_name_input.setMinimumHeight(30)
        customer_layout.addWidget(self.customer_name_input)
        
        payment_layout.addLayout(customer_layout)
        
        # Transaction buttons
        button_layout = QHBoxLayout()
        
        self.complete_sale_button = QPushButton("Complete Sale")
        self.complete_sale_button.setMinimumHeight(40)
        self.complete_sale_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        self.complete_sale_button.setEnabled(False)
        
        self.cancel_sale_button = QPushButton("Cancel Sale")
        self.cancel_sale_button.setMinimumHeight(40)
        self.cancel_sale_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        
        button_layout.addWidget(self.complete_sale_button)
        button_layout.addWidget(self.cancel_sale_button)
        
        payment_layout.addLayout(button_layout)
        
        layout.addWidget(payment_group)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.clear_cart_button.clicked.connect(self.clear_cart)
        self.discount_input.valueChanged.connect(self._on_discount_changed)
        self.tax_rate_input.valueChanged.connect(self._on_tax_rate_changed)
        self.payment_method_combo.currentTextChanged.connect(self._on_payment_method_changed)
        self.complete_sale_button.clicked.connect(self._complete_sale)
        self.cancel_sale_button.clicked.connect(self._cancel_sale)
    
    def add_product(self, medicine: Medicine, quantity: int):
        """Add product to cart"""
        try:
            success, message, sale_item = self.sales_manager.add_to_cart(medicine.id, quantity)
            
            if success:
                self.refresh_cart()
                self.logger.info(f"Added {quantity} units of {medicine.name} to cart")
            else:
                QMessageBox.warning(self, "Cannot Add to Cart", message)
                
        except Exception as e:
            self.logger.error(f"Error adding product to cart: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error adding product to cart: {str(e)}")
    
    def refresh_cart(self):
        """Refresh cart display"""
        try:
            cart_items = self.sales_manager.get_cart_items()
            
            # Update cart count
            item_count = len(cart_items)
            total_quantity = sum(item.quantity for item in cart_items)
            
            if item_count == 0:
                self.cart_count_label.setText("0 items")
                self.empty_cart_label.show()
                self.cart_table.hide()
                self.clear_cart_button.setEnabled(False)
                self.complete_sale_button.setEnabled(False)
            else:
                self.cart_count_label.setText(f"{item_count} items ({total_quantity} units)")
                self.empty_cart_label.hide()
                self.cart_table.show()
                self.clear_cart_button.setEnabled(True)
                self.complete_sale_button.setEnabled(True)
            
            # Populate cart table
            self._populate_cart_table(cart_items)
            
            # Update totals
            self._update_totals()
            
            # Emit signal
            self.cart_updated.emit()
            
        except Exception as e:
            self.logger.error(f"Error refreshing cart: {str(e)}")
    
    def _populate_cart_table(self, cart_items: List[SaleItem]):
        """Populate cart table with items"""
        self.cart_table.setRowCount(len(cart_items))
        
        for row, item in enumerate(cart_items):
            # Item name
            name_item = QTableWidgetItem(item.name)
            name_item.setData(Qt.ItemDataRole.UserRole, item.medicine_id)
            self.cart_table.setItem(row, 0, name_item)
            
            # Quantity with spinbox
            quantity_spinbox = QSpinBox()
            quantity_spinbox.setMinimum(1)
            quantity_spinbox.setMaximum(9999)
            quantity_spinbox.setValue(item.quantity)
            quantity_spinbox.setMinimumHeight(25)
            quantity_spinbox.valueChanged.connect(
                lambda value, med_id=item.medicine_id: self._on_quantity_changed(med_id, value)
            )
            self.cart_table.setCellWidget(row, 1, quantity_spinbox)
            
            # Unit price
            unit_price_item = QTableWidgetItem(self.sales_manager.format_currency(item.unit_price))
            unit_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.cart_table.setItem(row, 2, unit_price_item)
            
            # Total price
            total_price_item = QTableWidgetItem(self.sales_manager.format_currency(item.total_price))
            total_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_price_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.cart_table.setItem(row, 3, total_price_item)
            
            # Actions (placeholder for future features)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            # For now, just add a spacer
            actions_layout.addStretch()
            
            self.cart_table.setCellWidget(row, 4, actions_widget)
            
            # Remove button
            remove_button = QPushButton("×")
            remove_button.setMaximumSize(25, 25)
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            remove_button.clicked.connect(
                lambda checked, med_id=item.medicine_id: self._remove_item(med_id)
            )
            self.cart_table.setCellWidget(row, 5, remove_button)
    
    def _on_quantity_changed(self, medicine_id: int, new_quantity: int):
        """Handle quantity change in cart"""
        try:
            success, message = self.sales_manager.update_cart_item_quantity(medicine_id, new_quantity)
            
            if success:
                self.refresh_cart()
            else:
                # Revert the spinbox value
                self.refresh_cart()
                QMessageBox.warning(self, "Cannot Update Quantity", message)
                
        except Exception as e:
            self.logger.error(f"Error updating quantity: {str(e)}")
            self.refresh_cart()
            QMessageBox.critical(self, "Error", f"Error updating quantity: {str(e)}")
    
    def _remove_item(self, medicine_id: int):
        """Remove item from cart"""
        try:
            success, message = self.sales_manager.remove_from_cart(medicine_id)
            
            if success:
                self.refresh_cart()
                self.logger.info(f"Removed item {medicine_id} from cart")
            else:
                QMessageBox.warning(self, "Cannot Remove Item", message)
                
        except Exception as e:
            self.logger.error(f"Error removing item from cart: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error removing item from cart: {str(e)}")
    
    def _on_discount_changed(self, discount: float):
        """Handle discount change"""
        try:
            success, message = self.sales_manager.set_discount(discount)
            
            if success:
                self._update_totals()
            else:
                # Revert discount input
                self.discount_input.setValue(self.sales_manager.get_current_discount())
                QMessageBox.warning(self, "Invalid Discount", message)
                
        except Exception as e:
            self.logger.error(f"Error setting discount: {str(e)}")
            self.discount_input.setValue(self.sales_manager.get_current_discount())
    
    def _on_tax_rate_changed(self, tax_rate: float):
        """Handle tax rate change"""
        try:
            success, message = self.sales_manager.set_tax_rate(tax_rate)
            
            if success:
                self._update_totals()
            else:
                # Revert tax rate input
                self.tax_rate_input.setValue(self.sales_manager.get_current_tax_rate())
                QMessageBox.warning(self, "Invalid Tax Rate", message)
                
        except Exception as e:
            self.logger.error(f"Error setting tax rate: {str(e)}")
            self.tax_rate_input.setValue(self.sales_manager.get_current_tax_rate())
    
    def _on_payment_method_changed(self, payment_method: str):
        """Handle payment method change"""
        try:
            success, message = self.sales_manager.set_payment_method(payment_method.lower())
            
            if not success:
                # Revert payment method selection
                self.payment_method_combo.setCurrentText(self.sales_manager.get_current_payment_method().title())
                QMessageBox.warning(self, "Invalid Payment Method", message)
                
        except Exception as e:
            self.logger.error(f"Error setting payment method: {str(e)}")
            self.payment_method_combo.setCurrentText(self.sales_manager.get_current_payment_method().title())
    

    
    def _cancel_sale(self):
        """Cancel the current sale"""
        if self.sales_manager.get_cart_count() > 0:
            reply = QMessageBox.question(
                self,
                "Cancel Sale",
                "Are you sure you want to cancel this sale? All items will be removed from the cart.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.clear_cart()
                self.customer_name_input.clear()
                self.logger.info("Sale cancelled by user")
    
    def _update_totals(self):
        """Update all total displays"""
        try:
            totals = self.sales_manager.calculate_cart_totals()
            
            # Update total labels with currency formatting
            self.subtotal_label.setText(self.sales_manager.format_currency(totals['subtotal']))
            self.discount_amount_label.setText(f"-{self.sales_manager.format_currency(totals['discount'])}")
            self.tax_amount_label.setText(self.sales_manager.format_currency(totals['tax']))
            self.total_label.setText(self.sales_manager.format_currency(totals['total']))
            
        except Exception as e:
            self.logger.error(f"Error updating totals: {str(e)}")
            # Set default values
            self.subtotal_label.setText("$0.00")
            self.discount_amount_label.setText("$0.00")
            self.tax_amount_label.setText("$0.00")
            self.total_label.setText("$0.00")
    
    def clear_cart(self):
        """Clear the shopping cart"""
        try:
            if self.sales_manager.clear_cart():
                self.refresh_cart()
                self.logger.info("Cart cleared")
            else:
                QMessageBox.warning(self, "Error", "Failed to clear cart")
                
        except Exception as e:
            self.logger.error(f"Error clearing cart: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error clearing cart: {str(e)}")
    
    def refresh_settings(self):
        """Refresh settings-dependent components"""
        try:
            # Refresh sales manager settings
            if hasattr(self.sales_manager, 'refresh_settings'):
                self.sales_manager.refresh_settings()
            
            # Update tax rate from settings if cart is empty
            if self.sales_manager.is_cart_empty():
                default_tax_rate = self.sales_manager.get_current_tax_rate()
                self.tax_rate_input.setValue(default_tax_rate)
            
            # Refresh totals to update currency formatting
            self._update_totals()
            
            # Refresh cart display to update currency formatting
            self.refresh_cart()
            
            self.logger.info("Billing widget settings refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing billing settings: {str(e)}")
    
    def _complete_sale(self):
        """Complete the current sale transaction"""
        try:
            # Validate cart is not empty
            if self.sales_manager.is_cart_empty():
                QMessageBox.warning(self, "Empty Cart", "Cannot complete sale with empty cart.")
                return
            
            # Get cart summary for confirmation
            cart_summary = self.sales_manager.get_current_cart_summary()
            
            # Show confirmation dialog
            confirmation_msg = (
                f"Complete sale with {cart_summary['item_count']} items?\n\n"
                f"Subtotal: {self.sales_manager.format_currency(cart_summary['subtotal'])}\n"
                f"Discount: {self.sales_manager.format_currency(cart_summary['discount'])}\n"
                f"Tax: {self.sales_manager.format_currency(cart_summary['tax'])}\n"
                f"Total: {self.sales_manager.format_currency(cart_summary['total'])}\n"
                f"Payment: {self.payment_method_combo.currentText()}"
            )
            
            reply = QMessageBox.question(
                self,
                "Complete Sale",
                confirmation_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Process the sale
            customer_name = self.customer_name_input.text().strip() if self.customer_name_input.text().strip() else None
            # Get cashier_id from current user
            cashier_id = getattr(self.parent(), 'current_user', None) and getattr(self.parent(), 'current_user').id
            success, message, sale = self.sales_manager.complete_sale(cashier_id=cashier_id, customer_name=customer_name)
            
            if success and sale:
                # Show success message with receipt option
                self._show_transaction_success(sale)
                
                # Clear customer name input
                self.customer_name_input.clear()
                
                # Reset payment method to cash
                self.payment_method_combo.setCurrentText("Cash")
                
                self.logger.info(f"Sale completed successfully: ID {sale.id}, Total: {self.sales_manager.format_currency(sale.total)}")
                
            else:
                # Show error message
                QMessageBox.critical(
                    self,
                    "Transaction Failed",
                    f"Failed to complete sale:\n{message}"
                )
                self.logger.error(f"Sale completion failed: {message}")
                
        except Exception as e:
            error_msg = f"Error completing sale: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Transaction Error", error_msg)
    
    def _cancel_sale(self):
        """Cancel the current sale"""
        if self.sales_manager.get_cart_count() > 0:
            reply = QMessageBox.question(
                self,
                "Cancel Sale",
                "Are you sure you want to cancel this sale? All items will be removed from the cart.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.clear_cart()
                self.customer_name_input.clear()
                self.logger.info("Sale cancelled by user")
    
    def _show_transaction_success(self, sale):
        """Show transaction success dialog with receipt option"""
        try:
            # Create success dialog
            success_dialog = QMessageBox(self)
            success_dialog.setWindowTitle("Transaction Completed")
            success_dialog.setIcon(QMessageBox.Icon.Information)
            
            # Format success message
            success_msg = (
                f"Sale completed successfully!\n\n"
                f"Transaction ID: {sale.id}\n"
                f"Date: {sale.date}\n"
                f"Items: {len(sale.items)}\n"
                f"Total: {self.sales_manager.format_currency(sale.total)}\n"
                f"Payment: {sale.payment_method.title()}"
            )
            
            if self.customer_name_input.text().strip():
                success_msg += f"\nCustomer: {self.customer_name_input.text().strip()}"
            
            success_dialog.setText(success_msg)
            
            # Add custom buttons
            print_receipt_button = success_dialog.addButton("Print Receipt", QMessageBox.ButtonRole.ActionRole)
            view_receipt_button = success_dialog.addButton("View Receipt", QMessageBox.ButtonRole.ActionRole)
            ok_button = success_dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            
            success_dialog.setDefaultButton(ok_button)
            
            # Show dialog and handle response
            success_dialog.exec()
            clicked_button = success_dialog.clickedButton()
            
            if clicked_button == print_receipt_button:
                self._print_receipt(sale)
            elif clicked_button == view_receipt_button:
                self._show_receipt_dialog(sale)
                
        except Exception as e:
            self.logger.error(f"Error showing transaction success: {str(e)}")
            # Fallback to simple message box
            QMessageBox.information(
                self,
                "Transaction Completed",
                f"Sale completed successfully!\nTransaction ID: {sale.id}\nTotal: {self.sales_manager.format_currency(sale.total)}"
            )
    
    def _show_receipt_dialog(self, sale):
        """Show receipt in a dialog"""
        try:
            from ...ui.dialogs.receipt_dialog import ReceiptDialog
            receipt_dialog = ReceiptDialog(sale, self.sales_manager, self)
            receipt_dialog.exec()
        except ImportError:
            # Fallback to simple text display
            receipt_text = self._generate_receipt_text(sale)
            
            receipt_dialog = QMessageBox(self)
            receipt_dialog.setWindowTitle(f"Receipt - Transaction {sale.id}")
            receipt_dialog.setText(receipt_text)
            receipt_dialog.setDetailedText(receipt_text)
            receipt_dialog.exec()
    
    def _print_receipt(self, sale):
        """Print receipt (placeholder implementation)"""
        try:
            # For now, just show a message that printing would happen here
            QMessageBox.information(
                self,
                "Print Receipt",
                f"Receipt for Transaction {sale.id} would be printed here.\n"
                f"This feature will be fully implemented in a future update."
            )
            self.logger.info(f"Print receipt requested for sale {sale.id}")
        except Exception as e:
            self.logger.error(f"Error printing receipt: {str(e)}")
            QMessageBox.warning(self, "Print Error", "Failed to print receipt.")
    
    def _generate_receipt_text(self, sale) -> str:
        """Generate receipt text"""
        try:
            receipt_lines = []
            receipt_lines.append("=" * 40)
            receipt_lines.append("MEDICAL STORE RECEIPT")
            receipt_lines.append("=" * 40)
            receipt_lines.append(f"Transaction ID: {sale.id}")
            receipt_lines.append(f"Date: {sale.date}")
            receipt_lines.append(f"Payment Method: {sale.payment_method.title()}")
            
            if self.customer_name_input.text().strip():
                receipt_lines.append(f"Customer: {self.customer_name_input.text().strip()}")
            
            receipt_lines.append("-" * 40)
            receipt_lines.append("ITEMS:")
            receipt_lines.append("-" * 40)
            
            for item in sale.items:
                receipt_lines.append(f"{item.name}")
                receipt_lines.append(f"  Qty: {item.quantity} x {self.sales_manager.format_currency(item.unit_price)} = {self.sales_manager.format_currency(item.total_price)}")
                if item.batch_no:
                    receipt_lines.append(f"  Batch: {item.batch_no}")
                receipt_lines.append("")
            
            receipt_lines.append("-" * 40)
            receipt_lines.append(f"Subtotal: {self.sales_manager.format_currency(sale.subtotal)}")
            if sale.discount > 0:
                receipt_lines.append(f"Discount: -{self.sales_manager.format_currency(sale.discount)}")
            if sale.tax > 0:
                receipt_lines.append(f"Tax: {self.sales_manager.format_currency(sale.tax)}")
            receipt_lines.append(f"TOTAL: {self.sales_manager.format_currency(sale.total)}")
            receipt_lines.append("=" * 40)
            receipt_lines.append("Thank you for your business!")
            receipt_lines.append("Please keep this receipt for your records.")
            
            return "\n".join(receipt_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating receipt text: {str(e)}")
            return f"Error generating receipt: {str(e)}"


class BillingWidget(QWidget):
    """Main billing widget combining product search and cart management"""
    
    def __init__(self, medicine_manager: MedicineManager, sales_manager: SalesManager, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.sales_manager = sales_manager
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_connections()
        
        # Initialize with settings
        self.refresh_display()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Product search
        self.search_widget = ProductSearchWidget(self.medicine_manager)
        self.search_widget.setMinimumWidth(400)
        splitter.addWidget(self.search_widget)
        
        # Right panel - Cart
        self.cart_widget = CartWidget(self.sales_manager)
        self.cart_widget.setMinimumWidth(450)
        splitter.addWidget(self.cart_widget)
        
        # Set initial splitter sizes (60% search, 40% cart)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect product selection to cart
        self.search_widget.product_selected.connect(self.cart_widget.add_product)
        
        # Connect cart updates to search refresh (for stock updates)
        self.cart_widget.cart_updated.connect(self._on_cart_updated)
    
    def _on_cart_updated(self):
        """Handle cart updates"""
        # Refresh search results to show updated stock levels
        self.search_widget.refresh_results()
    
    def refresh_display(self):
        """Refresh the entire billing display with current settings"""
        try:
            # Refresh settings in sales manager
            if hasattr(self.sales_manager, 'refresh_settings'):
                self.sales_manager.refresh_settings()
            
            # Refresh cart widget settings
            if hasattr(self.cart_widget, 'refresh_settings'):
                self.cart_widget.refresh_settings()
            
            # Refresh search widget to update currency formatting
            if hasattr(self.search_widget, 'refresh_results'):
                self.search_widget.refresh_results()
            
            self.logger.info("Billing display refreshed with current settings")
            
        except Exception as e:
            self.logger.error(f"Error refreshing billing display: {str(e)}")
    
    def focus_search(self):
        """Set focus to product search"""
        self.search_widget.focus_search()
    
    def get_cart_summary(self):
        """Get current cart summary"""
        return self.sales_manager.get_current_cart_summary()
    
    def _update_totals(self):
        """Update totals display"""
        try:
            totals = self.sales_manager.calculate_cart_totals()
            
            # Use settings-aware currency formatting
            self.subtotal_label.setText(self.sales_manager.format_currency(totals['subtotal']))
            self.discount_amount_label.setText(f"-{self.sales_manager.format_currency(totals['discount'])}")
            self.tax_amount_label.setText(self.sales_manager.format_currency(totals['tax']))
            self.total_label.setText(self.sales_manager.format_currency(totals['total']))
            
        except Exception as e:
            self.logger.error(f"Error updating totals: {str(e)}")
            # Set default values using currency formatting
            currency_symbol = self.sales_manager.get_currency_symbol()
            self.subtotal_label.setText(f"{currency_symbol}0.00")
            self.discount_amount_label.setText(f"{currency_symbol}0.00")
            self.tax_amount_label.setText(f"{currency_symbol}0.00")
            self.total_label.setText(f"{currency_symbol}0.00")
    
    def clear_cart(self):
        """Clear all items from cart"""
        try:
            if self.sales_manager.is_cart_empty():
                return
            
            reply = QMessageBox.question(
                self,
                "Clear Cart",
                "Are you sure you want to clear all items from the cart?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.sales_manager.clear_cart():
                    self.refresh_cart()
                    self.logger.info("Cart cleared")
                else:
                    QMessageBox.warning(self, "Error", "Failed to clear cart")
                    
        except Exception as e:
            self.logger.error(f"Error clearing cart: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error clearing cart: {str(e)}")
    
    def _on_payment_method_changed(self, payment_method: str):
        """Handle payment method change"""
        try:
            # Convert display name to internal format
            method_mapping = {
                "Cash": "cash",
                "Card": "card", 
                "UPI": "upi",
                "Cheque": "cheque",
                "Bank Transfer": "bank_transfer"
            }
            
            internal_method = method_mapping.get(payment_method, "cash")
            success, message = self.sales_manager.set_payment_method(internal_method)
            
            if not success:
                self.logger.warning(f"Failed to set payment method: {message}")
                # Revert to previous selection
                self.payment_method_combo.setCurrentText("Cash")
                
        except Exception as e:
            self.logger.error(f"Error setting payment method: {str(e)}")
            self.payment_method_combo.setCurrentText("Cash")
    
    def _complete_sale(self):
        """Complete the current sale transaction"""
        try:
            # Validate cart is not empty
            if self.sales_manager.is_cart_empty():
                QMessageBox.warning(self, "Empty Cart", "Cannot complete sale with empty cart.")
                return
            
            # Get cart summary for confirmation
            cart_summary = self.sales_manager.get_current_cart_summary()
            
            # Show confirmation dialog
            confirmation_msg = (
                f"Complete sale with {cart_summary['item_count']} items?\n\n"
                f"Subtotal: ${cart_summary['subtotal']:.2f}\n"
                f"Discount: ${cart_summary['discount']:.2f}\n"
                f"Tax: ${cart_summary['tax']:.2f}\n"
                f"Total: ${cart_summary['total']:.2f}\n"
                f"Payment: {self.payment_method_combo.currentText()}"
            )
            
            reply = QMessageBox.question(
                self,
                "Complete Sale",
                confirmation_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Process the sale
            customer_name = self.customer_name_input.text().strip() if self.customer_name_input.text().strip() else None
            # Get cashier_id from current user
            cashier_id = getattr(self.parent(), 'current_user', None) and getattr(self.parent(), 'current_user').id
            success, message, sale = self.sales_manager.complete_sale(cashier_id=cashier_id, customer_name=customer_name)
            
            if success and sale:
                # Show success message with receipt option
                self._show_transaction_success(sale)
                
                # Clear customer name input
                self.customer_name_input.clear()
                
                # Reset payment method to cash
                self.payment_method_combo.setCurrentText("Cash")
                
                self.logger.info(f"Sale completed successfully: ID {sale.id}, Total: ${sale.total:.2f}")
                
            else:
                # Show error message
                QMessageBox.critical(
                    self,
                    "Transaction Failed",
                    f"Failed to complete sale:\n{message}"
                )
                self.logger.error(f"Sale completion failed: {message}")
                
        except Exception as e:
            error_msg = f"Error completing sale: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Transaction Error", error_msg)
    
    def _cancel_sale(self):
        """Cancel the current sale and clear cart"""
        try:
            if self.sales_manager.is_cart_empty():
                return
            
            reply = QMessageBox.question(
                self,
                "Cancel Sale",
                "Are you sure you want to cancel this sale and clear the cart?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.clear_cart()
                self.customer_name_input.clear()
                self.payment_method_combo.setCurrentText("Cash")
                self.logger.info("Sale cancelled and cart cleared")
                
        except Exception as e:
            self.logger.error(f"Error cancelling sale: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error cancelling sale: {str(e)}")
    
    def _show_transaction_success(self, sale):
        """Show transaction success dialog with receipt option"""
        try:
            # Create success dialog
            success_dialog = QMessageBox(self)
            success_dialog.setWindowTitle("Transaction Completed")
            success_dialog.setIcon(QMessageBox.Icon.Information)
            
            # Format success message
            success_msg = (
                f"Sale completed successfully!\n\n"
                f"Transaction ID: {sale.id}\n"
                f"Date: {sale.date}\n"
                f"Items: {len(sale.items)}\n"
                f"Total: {self.sales_manager.format_currency(sale.total)}\n"
                f"Payment: {sale.payment_method.title()}"
            )
            
            if self.customer_name_input.text().strip():
                success_msg += f"\nCustomer: {self.customer_name_input.text().strip()}"
            
            success_dialog.setText(success_msg)
            
            # Add custom buttons
            print_receipt_button = success_dialog.addButton("Print Receipt", QMessageBox.ButtonRole.ActionRole)
            view_receipt_button = success_dialog.addButton("View Receipt", QMessageBox.ButtonRole.ActionRole)
            ok_button = success_dialog.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
            
            success_dialog.setDefaultButton(ok_button)
            
            # Show dialog and handle response
            success_dialog.exec()
            clicked_button = success_dialog.clickedButton()
            
            if clicked_button == print_receipt_button:
                self._print_receipt(sale)
            elif clicked_button == view_receipt_button:
                self._show_receipt_dialog(sale)
                
        except Exception as e:
            self.logger.error(f"Error showing transaction success: {str(e)}")
            # Fallback to simple message box
            QMessageBox.information(
                self,
                "Transaction Completed",
                f"Sale completed successfully!\nTransaction ID: {sale.id}\nTotal: {self.sales_manager.format_currency(sale.total)}"
            )
    
    def _show_receipt_dialog(self, sale):
        """Show receipt in a dialog"""
        try:
            from ...ui.dialogs.receipt_dialog import ReceiptDialog
            receipt_dialog = ReceiptDialog(sale, self.sales_manager, self)
            receipt_dialog.exec()
        except ImportError:
            # Fallback to simple text display
            receipt_text = self._generate_receipt_text(sale)
            
            receipt_dialog = QMessageBox(self)
            receipt_dialog.setWindowTitle(f"Receipt - Transaction {sale.id}")
            receipt_dialog.setText(receipt_text)
            receipt_dialog.setDetailedText(receipt_text)
            receipt_dialog.exec()
    
    def _print_receipt(self, sale):
        """Print receipt (placeholder implementation)"""
        try:
            # For now, just show a message that printing would happen here
            QMessageBox.information(
                self,
                "Print Receipt",
                f"Receipt for Transaction {sale.id} would be printed here.\n"
                f"This feature will be fully implemented in a future update."
            )
            self.logger.info(f"Print receipt requested for sale {sale.id}")
        except Exception as e:
            self.logger.error(f"Error printing receipt: {str(e)}")
            QMessageBox.warning(self, "Print Error", "Failed to print receipt.")
    
    def _generate_receipt_text(self, sale) -> str:
        """Generate receipt text"""
        try:
            receipt_lines = []
            receipt_lines.append("=" * 40)
            receipt_lines.append("MEDICAL STORE RECEIPT")
            receipt_lines.append("=" * 40)
            receipt_lines.append(f"Transaction ID: {sale.id}")
            receipt_lines.append(f"Date: {sale.date}")
            receipt_lines.append(f"Payment Method: {sale.payment_method.title()}")
            
            if self.customer_name_input.text().strip():
                receipt_lines.append(f"Customer: {self.customer_name_input.text().strip()}")
            
            receipt_lines.append("-" * 40)
            receipt_lines.append("ITEMS:")
            receipt_lines.append("-" * 40)
            
            for item in sale.items:
                receipt_lines.append(f"{item.name}")
                receipt_lines.append(f"  Qty: {item.quantity} x ${item.unit_price:.2f} = ${item.total_price:.2f}")
                if item.batch_no:
                    receipt_lines.append(f"  Batch: {item.batch_no}")
                receipt_lines.append("")
            
            receipt_lines.append("-" * 40)
            receipt_lines.append(f"Subtotal: ${sale.subtotal:.2f}")
            if sale.discount > 0:
                receipt_lines.append(f"Discount: -${sale.discount:.2f}")
            if sale.tax > 0:
                receipt_lines.append(f"Tax: ${sale.tax:.2f}")
            receipt_lines.append(f"TOTAL: ${sale.total:.2f}")
            receipt_lines.append("=" * 40)
            receipt_lines.append("Thank you for your business!")
            receipt_lines.append("=" * 40)
            
            return "\n".join(receipt_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating receipt text: {str(e)}")
            return f"Receipt for Transaction {sale.id}\nTotal: ${sale.total:.2f}"

    def get_cart_summary(self) -> Dict[str, Any]:
        """Get current cart summary"""
        return self.sales_manager.get_current_cart_summary()
    
    def on_settings_updated(self, settings: dict):
        """Handle settings updates"""
        try:
            # Refresh cart display to update currency formatting
            self.refresh_cart()
            
            # Update tax rate from settings if cart is empty (new transaction)
            if self.sales_manager.is_cart_empty():
                tax_rate = settings.get('tax_rate', '0.0')
                try:
                    tax_rate_float = float(tax_rate)
                    self.tax_rate_input.setValue(tax_rate_float)
                    self.sales_manager.set_tax_rate(tax_rate_float)
                except (ValueError, TypeError):
                    pass  # Keep current tax rate if conversion fails
            
            self.logger.info("Cart widget updated with new settings")
        except Exception as e:
            self.logger.error(f"Error updating cart widget with settings: {str(e)}")
            self.refresh_display()
            self.logger.info("Billing widget updated with new settings")
        except Exception as e:
            self.logger.error(f"Error updating billing widget with settings: {str(e)}")
    
    def get_cart_summary(self):
        """Get cart summary from cart widget"""
        if hasattr(self.cart_widget, 'get_cart_summary'):
            return self.cart_widget.get_cart_summary()
        return {'item_count': 0, 'total': 0.0}