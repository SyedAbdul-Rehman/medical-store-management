"""
Medicine Form Widget for Medical Store Management Application
Provides form interface for adding and editing medicines
"""

import logging
from typing import Optional, Dict, Any, Callable
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QDate, QThread
from PySide6.QtGui import QFont

from .base_components import (
    FormContainer, ValidatedLineEdit, ValidatedComboBox, 
    ValidatedSpinBox, ValidatedDoubleSpinBox, ValidatedDateEdit,
    StyledButton
)
from ...managers.medicine_manager import MedicineManager


class MedicineFormWorker(QThread):
    """Worker thread for medicine operations to prevent UI blocking"""
    
    finished = Signal(bool, str, object)  # success, message, medicine
    
    def __init__(self, manager: MedicineManager, operation: str, data: Dict[str, Any], medicine_id: Optional[int] = None):
        super().__init__()
        self.manager = manager
        self.operation = operation
        self.data = data
        self.medicine_id = medicine_id
    
    def run(self):
        """Execute the medicine operation"""
        try:
            if self.operation == "add":
                success, message, medicine = self.manager.add_medicine(self.data)
            elif self.operation == "edit":
                success, message, medicine = self.manager.edit_medicine(self.medicine_id, self.data)
            else:
                success, message, medicine = False, "Unknown operation", None
            
            self.finished.emit(success, message, medicine)
        except Exception as e:
            self.finished.emit(False, f"Operation failed: {str(e)}", None)


class MedicineForm(QWidget):
    """Medicine form widget for adding and editing medicines"""
    
    # Signals
    medicine_saved = Signal(object)  # Emitted when medicine is successfully saved
    operation_finished = Signal(bool, str)  # Emitted when operation completes
    
    def __init__(self, medicine_manager: MedicineManager, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.logger = logging.getLogger(__name__)
        
        # Form state
        self.current_medicine = None
        self.is_editing = False
        self.worker_thread = None
        
        # Common medicine categories
        self.medicine_categories = [
            "Pain Relief",
            "Antibiotic",
            "Antiviral",
            "Antifungal",
            "Cardiovascular",
            "Diabetes",
            "Respiratory",
            "Digestive",
            "Neurological",
            "Dermatological",
            "Vitamins & Supplements",
            "First Aid",
            "Other"
        ]
        
        self._setup_ui()
        self._setup_validation()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the form UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        
        # Create form container
        self.form_container = FormContainer("Add Medicine")
        
        # Medicine name field
        self.name_field = ValidatedLineEdit("Enter medicine name")
        self.form_container.add_field("Medicine Name *", self.name_field, "name")
        
        # Category field
        self.category_field = ValidatedComboBox()
        self.category_field.setEditable(True)  # Allow custom categories
        self.category_field.addItems(self.medicine_categories)
        self.category_field.setCurrentIndex(-1)  # No selection initially
        self.category_field.setEditText("")  # Clear text
        self.category_field.lineEdit().setPlaceholderText("Select Category")
        self.form_container.add_field("Category *", self.category_field, "category")
        
        # Batch number field
        self.batch_field = ValidatedLineEdit("Enter batch number")
        self.form_container.add_field("Batch Number *", self.batch_field, "batch_no")
        
        # Expiry date field
        self.expiry_field = ValidatedDateEdit()
        self.expiry_field.setDate(QDate.currentDate().addDays(365))  # Default to 1 year from now
        self.form_container.add_field("Expiry Date *", self.expiry_field, "expiry_date")
        
        # Quantity field
        self.quantity_field = ValidatedSpinBox(0, 999999)
        self.form_container.add_field("Quantity *", self.quantity_field, "quantity")
        
        # Purchase price field
        self.purchase_price_field = ValidatedDoubleSpinBox(0.0, 999999.99, 2)
        self.form_container.add_field("Purchase Price *", self.purchase_price_field, "purchase_price")
        
        # Selling price field
        self.selling_price_field = ValidatedDoubleSpinBox(0.0, 999999.99, 2)
        self.form_container.add_field("Selling Price *", self.selling_price_field, "selling_price")
        
        # Barcode field (optional)
        self.barcode_field = ValidatedLineEdit("Enter barcode (optional)")
        self.form_container.add_field("Barcode", self.barcode_field, "barcode")
        
        self.main_layout.addWidget(self.form_container)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        self.main_layout.addWidget(self.progress_bar)
        
        # Button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        
        # Clear button
        self.clear_button = StyledButton("Clear", "outline")
        self.button_layout.addWidget(self.clear_button)
        
        # Save button
        self.save_button = StyledButton("Save Medicine", "primary")
        self.button_layout.addWidget(self.save_button)
        
        self.main_layout.addLayout(self.button_layout)
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            MedicineForm {
                background-color: white;
                border-radius: 8px;
            }
        """)
    
    def _setup_validation(self):
        """Set up field validation"""
        # Name validation
        self.name_field.add_validator(self._validate_name)
        
        # Category validation
        self.category_field.add_validator(self._validate_category)
        
        # Batch number validation
        self.batch_field.add_validator(self._validate_batch_number)
        
        # Expiry date validation
        self.expiry_field.add_validator(self._validate_expiry_date)
        
        # Quantity validation
        self.quantity_field.add_validator(self._validate_quantity)
        
        # Purchase price validation
        self.purchase_price_field.add_validator(self._validate_purchase_price)
        
        # Selling price validation
        self.selling_price_field.add_validator(self._validate_selling_price)
        
        # Barcode validation (optional)
        self.barcode_field.add_validator(self._validate_barcode)
    
    def _connect_signals(self):
        """Connect widget signals"""
        self.clear_button.clicked.connect(self.clear_form)
        self.save_button.clicked.connect(self.save_medicine)
        
        # Connect validation signals to update save button state
        for field in [self.name_field, self.category_field, self.batch_field, 
                     self.expiry_field, self.quantity_field, self.purchase_price_field, 
                     self.selling_price_field, self.barcode_field]:
            if hasattr(field, 'validation_changed'):
                field.validation_changed.connect(self._update_save_button_state)
        
        # Connect price fields for profit margin calculation
        self.purchase_price_field.valueChanged.connect(self._update_profit_info)
        self.selling_price_field.valueChanged.connect(self._update_profit_info)
    
    def _validate_name(self, value: str) -> tuple[bool, str]:
        """Validate medicine name"""
        if not value or not value.strip():
            return False, "Medicine name is required"
        if len(value.strip()) < 2:
            return False, "Medicine name must be at least 2 characters"
        if len(value.strip()) > 100:
            return False, "Medicine name must be less than 100 characters"
        return True, ""
    
    def _validate_category(self, value: str) -> tuple[bool, str]:
        """Validate category"""
        if not value or not value.strip():
            return False, "Category is required"
        if len(value.strip()) > 50:
            return False, "Category must be less than 50 characters"
        return True, ""
    
    def _validate_batch_number(self, value: str) -> tuple[bool, str]:
        """Validate batch number"""
        if not value or not value.strip():
            return False, "Batch number is required"
        if len(value.strip()) > 50:
            return False, "Batch number must be less than 50 characters"
        return True, ""
    
    def _validate_expiry_date(self, value: QDate) -> tuple[bool, str]:
        """Validate expiry date"""
        if not value.isValid():
            return False, "Invalid expiry date"
        if value.toPython() <= date.today():
            return False, "Expiry date must be in the future"
        return True, ""
    
    def _validate_quantity(self, value: int) -> tuple[bool, str]:
        """Validate quantity"""
        if value < 0:
            return False, "Quantity cannot be negative"
        return True, ""
    
    def _validate_purchase_price(self, value: float) -> tuple[bool, str]:
        """Validate purchase price"""
        if value < 0:
            return False, "Purchase price cannot be negative"
        return True, ""
    
    def _validate_selling_price(self, value: float) -> tuple[bool, str]:
        """Validate selling price"""
        if value < 0:
            return False, "Selling price cannot be negative"
        
        # Check if selling price is less than purchase price
        purchase_price = self.purchase_price_field.value()
        if purchase_price > 0 and value > 0 and value < purchase_price:
            return False, "Selling price should not be less than purchase price"
        
        return True, ""
    
    def _validate_barcode(self, value: str) -> tuple[bool, str]:
        """Validate barcode (optional field)"""
        if not value or not value.strip():
            return True, ""  # Optional field
        
        # Basic barcode validation
        barcode = value.strip()
        if len(barcode) < 8 or len(barcode) > 20:
            return False, "Barcode must be 8-20 characters"
        
        if not barcode.isalnum():
            return False, "Barcode must contain only letters and numbers"
        
        return True, ""
    
    def _update_save_button_state(self):
        """Update save button enabled state based on form validation"""
        is_valid, _ = self.form_container.validate_form()
        self.save_button.setEnabled(is_valid and not self._is_operation_in_progress())
    
    def _update_profit_info(self):
        """Update profit information display"""
        purchase_price = self.purchase_price_field.value()
        selling_price = self.selling_price_field.value()
        
        if purchase_price > 0 and selling_price > 0:
            profit = selling_price - purchase_price
            margin = (profit / purchase_price) * 100
            
            # You could add a label to show profit info
            # For now, just log it
            self.logger.debug(f"Profit: ${profit:.2f}, Margin: {margin:.1f}%")
    
    def _is_operation_in_progress(self) -> bool:
        """Check if an operation is currently in progress"""
        return self.worker_thread is not None and self.worker_thread.isRunning()
    
    def clear_form(self):
        """Clear all form fields"""
        # Clear form fields first
        self.form_container.clear_form()
        
        # Reset specific fields that need special handling
        # Reset expiry date to default
        self.expiry_field.setDate(QDate.currentDate().addDays(365))
        
        # Ensure category dropdown is properly reset and repopulated
        self.category_field.clear()
        self.category_field.addItems(self.medicine_categories)
        self.category_field.setCurrentIndex(-1)  # No selection
        if self.category_field.isEditable():
            self.category_field.setEditText("")
            self.category_field.setPlaceholderText("Select Category")
        
        # Reset form state
        self.current_medicine = None
        self.is_editing = False
        self.form_container.title = "Add Medicine"
        self.save_button.setText("Save Medicine")
        
        # Clear all validation messages without triggering validation
        self._clear_all_validation_messages()
        
        self._update_save_button_state()
        
        self.logger.info("Medicine form cleared")
    
    def _clear_all_validation_messages(self):
        """Clear all validation messages without triggering validation"""
        for field in [self.name_field, self.category_field, self.batch_field, 
                     self.expiry_field, self.quantity_field, self.purchase_price_field, 
                     self.selling_price_field, self.barcode_field]:
            if hasattr(field, 'reset_validation'):
                field.reset_validation()
    
    def load_medicine(self, medicine):
        """Load medicine data into form for editing"""
        if not medicine:
            return
        
        self.current_medicine = medicine
        self.is_editing = True
        self.form_container.title = f"Edit Medicine - {medicine.name}"
        
        # Load data into fields
        self.name_field.setText(medicine.name)
        
        # Set category (add if not in list)
        category_index = self.category_field.findText(medicine.category)
        if category_index >= 0:
            self.category_field.setCurrentIndex(category_index)
        else:
            self.category_field.addItem(medicine.category)
            self.category_field.setCurrentText(medicine.category)
        
        self.batch_field.setText(medicine.batch_no)
        
        # Set expiry date
        try:
            from datetime import datetime
            expiry_date = datetime.strptime(medicine.expiry_date, "%Y-%m-%d").date()
            self.expiry_field.setDate(QDate.fromString(medicine.expiry_date, "yyyy-MM-dd"))
        except ValueError:
            self.logger.warning(f"Invalid expiry date format: {medicine.expiry_date}")
        
        self.quantity_field.setValue(medicine.quantity)
        self.purchase_price_field.setValue(medicine.purchase_price)
        self.selling_price_field.setValue(medicine.selling_price)
        
        if medicine.barcode:
            self.barcode_field.setText(medicine.barcode)
        else:
            self.barcode_field.clear()
        
        self.save_button.setText("Update Medicine")
        self._update_save_button_state()
        
        self.logger.info(f"Loaded medicine for editing: {medicine.name}")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get form data as dictionary"""
        data = {
            'name': self.name_field.text().strip(),
            'category': self.category_field.currentText().strip(),
            'batch_no': self.batch_field.text().strip(),
            'expiry_date': self.expiry_field.date().toString("yyyy-MM-dd"),
            'quantity': self.quantity_field.value(),
            'purchase_price': self.purchase_price_field.value(),
            'selling_price': self.selling_price_field.value(),
            'barcode': self.barcode_field.text().strip() if self.barcode_field.text().strip() else None
        }
        return data
    
    def save_medicine(self):
        """Save medicine (add or update)"""
        # Validate form
        is_valid, errors = self.form_container.validate_form()
        if not is_valid:
            error_msg = "Please fix the following errors:\n" + "\n".join(errors)
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        # Get form data
        form_data = self.get_form_data()
        
        # Disable UI during operation
        self._set_ui_enabled(False)
        self.progress_bar.show()
        
        # Start worker thread
        operation = "edit" if self.is_editing else "add"
        medicine_id = self.current_medicine.id if self.current_medicine else None
        
        self.worker_thread = MedicineFormWorker(
            self.medicine_manager, operation, form_data, medicine_id
        )
        self.worker_thread.finished.connect(self._on_operation_finished)
        self.worker_thread.start()
        
        self.logger.info(f"Started {operation} medicine operation")
    
    def _on_operation_finished(self, success: bool, message: str, medicine):
        """Handle operation completion"""
        # Re-enable UI
        self._set_ui_enabled(True)
        self.progress_bar.hide()
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None
        
        if success:
            # Show success message
            QMessageBox.information(self, "Success", message)
            
            # Emit signals
            self.medicine_saved.emit(medicine)
            self.operation_finished.emit(True, message)
            
            # Clear form after successful operation (both add and edit)
            # This ensures the form is ready for the next operation
            self.clear_form()
            
            self.logger.info(f"Medicine operation completed successfully: {message}")
        else:
            # Show error message
            QMessageBox.critical(self, "Error", message)
            self.operation_finished.emit(False, message)
            self.logger.error(f"Medicine operation failed: {message}")
    
    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        self.form_container.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled and not self._is_operation_in_progress())
    
    def set_medicine_manager(self, manager: MedicineManager):
        """Set the medicine manager"""
        self.medicine_manager = manager
    
    def is_form_dirty(self) -> bool:
        """Check if form has unsaved changes"""
        if not self.current_medicine and self.is_editing:
            return False
        
        if self.is_editing and self.current_medicine:
            current_data = self.get_form_data()
            return (
                current_data['name'] != self.current_medicine.name or
                current_data['category'] != self.current_medicine.category or
                current_data['batch_no'] != self.current_medicine.batch_no or
                current_data['expiry_date'] != self.current_medicine.expiry_date or
                current_data['quantity'] != self.current_medicine.quantity or
                current_data['purchase_price'] != self.current_medicine.purchase_price or
                current_data['selling_price'] != self.current_medicine.selling_price or
                current_data['barcode'] != self.current_medicine.barcode
            )
        
        # For new medicine, check if any field has data
        form_data = self.get_form_data()
        return any([
            form_data['name'],
            form_data['category'] != self.medicine_categories[0],
            form_data['batch_no'],
            form_data['quantity'] > 0,
            form_data['purchase_price'] > 0,
            form_data['selling_price'] > 0,
            form_data['barcode']
        ])