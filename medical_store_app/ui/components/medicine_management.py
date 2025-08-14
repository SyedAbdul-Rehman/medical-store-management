"""
Medicine Management Widget for Medical Store Management Application
Integrates medicine form, table, and dialog components for complete medicine management
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMessageBox, QFrame, QDialog
)
from PySide6.QtCore import Qt, Signal

from .medicine_form import MedicineForm
from .medicine_table import MedicineTableWidget
from ..dialogs.medicine_dialog import EditMedicineDialog, DeleteMedicineDialog, MedicineDetailsDialog
from ...models.medicine import Medicine
from ...managers.medicine_manager import MedicineManager


class MedicineManagementWidget(QWidget):
    """Complete medicine management interface"""
    
    # Signals
    medicine_added = Signal(object)      # Emitted when medicine is added
    medicine_updated = Signal(object)    # Emitted when medicine is updated
    medicine_deleted = Signal(int)       # Emitted when medicine is deleted
    
    def __init__(self, medicine_manager: MedicineManager, parent=None):
        super().__init__(parent)
        self.medicine_manager = medicine_manager
        self.logger = logging.getLogger(__name__)
        
        # Current state
        self.current_medicine = None
        self.readonly_mode = False
        
        self._setup_ui()
        self._connect_signals()
        
        # Initial data load
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the management widget UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Create splitter for form and table
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Medicine form
        self.form_frame = QFrame()
        self.form_frame.setFrameStyle(QFrame.StyledPanel)
        self.form_frame.setMaximumWidth(400)
        self.form_frame.setMinimumWidth(350)
        
        form_layout = QVBoxLayout(self.form_frame)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        self.medicine_form = MedicineForm(self.medicine_manager)
        form_layout.addWidget(self.medicine_form)
        
        # Right side - Medicine table
        self.table_frame = QFrame()
        self.table_frame.setFrameStyle(QFrame.StyledPanel)
        
        table_layout = QVBoxLayout(self.table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.medicine_table = MedicineTableWidget(self.medicine_manager)
        table_layout.addWidget(self.medicine_table)
        
        # Add frames to splitter
        self.splitter.addWidget(self.form_frame)
        self.splitter.addWidget(self.table_frame)
        
        # Set splitter proportions (30% form, 70% table)
        self.splitter.setSizes([300, 700])
        
        self.main_layout.addWidget(self.splitter)
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
            }
            
            QSplitter::handle {
                background-color: #E1E5E9;
                width: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #2D9CDB;
            }
        """)
    
    def _connect_signals(self):
        """Connect widget signals"""
        # Form signals
        self.medicine_form.medicine_saved.connect(self._on_medicine_saved)
        self.medicine_form.operation_finished.connect(self._on_form_operation_finished)
        
        # Table signals
        self.medicine_table.medicine_selected.connect(self._on_medicine_selected)
        self.medicine_table.edit_requested.connect(self._on_edit_requested)
        self.medicine_table.delete_requested.connect(self._on_delete_requested)
        self.medicine_table.refresh_requested.connect(self.refresh_data)
    
    def _on_medicine_saved(self, medicine: Medicine):
        """Handle medicine saved from form"""
        if self.medicine_form.is_editing:
            # Update existing medicine in table
            self.medicine_table.update_medicine_in_table(medicine)
            self.medicine_updated.emit(medicine)
            self.logger.info(f"Medicine updated: {medicine.name}")
        else:
            # Add new medicine to table
            self.medicine_table.add_medicine_to_table(medicine)
            self.medicine_added.emit(medicine)
            self.logger.info(f"Medicine added: {medicine.name}")
        
        # Clear form after successful save
        self.medicine_form.clear_form()
        self.current_medicine = None
    
    def _on_form_operation_finished(self, success: bool, message: str):
        """Handle form operation completion"""
        if success:
            self.logger.info(f"Form operation completed: {message}")
        else:
            self.logger.error(f"Form operation failed: {message}")
    
    def _on_medicine_selected(self, medicine: Medicine):
        """Handle medicine selection from table"""
        self.current_medicine = medicine
        if medicine:
            self.logger.debug(f"Medicine selected: {medicine.name} (ID: {medicine.id})")
        else:
            self.logger.debug("Medicine selection cleared")
    
    def _on_edit_requested(self, medicine: Medicine):
        """Handle edit request from table"""
        self.edit_medicine(medicine)
    
    def _on_delete_requested(self, medicine: Medicine):
        """Handle delete request from table"""
        self.delete_medicine(medicine)
    
    def edit_medicine(self, medicine: Medicine):
        """Edit medicine using dialog"""
        try:
            dialog = EditMedicineDialog(medicine, self.medicine_manager, self)
            dialog.medicine_updated.connect(self._on_medicine_updated_from_dialog)
            
            result = dialog.exec()
            if result == QDialog.Accepted:
                self.logger.info(f"Medicine edit dialog completed for: {medicine.name}")
            else:
                self.logger.info(f"Medicine edit dialog cancelled for: {medicine.name}")
                
        except Exception as e:
            error_msg = f"Error opening edit dialog: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def delete_medicine(self, medicine: Medicine):
        """Delete medicine using dialog"""
        try:
            dialog = DeleteMedicineDialog(medicine, self.medicine_manager, self)
            dialog.medicine_deleted.connect(self._on_medicine_deleted_from_dialog)
            
            result = dialog.exec()
            if result == QDialog.Accepted:
                self.logger.info(f"Medicine delete dialog completed for: {medicine.name}")
            else:
                self.logger.info(f"Medicine delete dialog cancelled for: {medicine.name}")
                
        except Exception as e:
            error_msg = f"Error opening delete dialog: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def show_medicine_details(self, medicine: Medicine):
        """Show medicine details using dialog"""
        try:
            dialog = MedicineDetailsDialog(medicine, self)
            dialog.exec()
            self.logger.info(f"Medicine details dialog shown for: {medicine.name}")
            
        except Exception as e:
            error_msg = f"Error opening details dialog: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def _on_medicine_updated_from_dialog(self, medicine: Medicine):
        """Handle medicine update from edit dialog"""
        self.medicine_table.update_medicine_in_table(medicine)
        self.medicine_updated.emit(medicine)
        
        # Clear form if it was showing the updated medicine
        if (self.medicine_form.current_medicine and 
            self.medicine_form.current_medicine.id == medicine.id):
            self.medicine_form.clear_form()
        
        self.logger.info(f"Medicine updated from dialog: {medicine.name}")
    
    def _on_medicine_deleted_from_dialog(self, medicine_id: int):
        """Handle medicine deletion from delete dialog"""
        self.medicine_table.remove_medicine_from_table(medicine_id)
        self.medicine_deleted.emit(medicine_id)
        
        # Clear form if it was showing the deleted medicine
        if (self.medicine_form.current_medicine and 
            self.medicine_form.current_medicine.id == medicine_id):
            self.medicine_form.clear_form()
        
        # Clear current selection
        self.current_medicine = None
        
        self.logger.info(f"Medicine deleted from dialog: ID {medicine_id}")
    
    def refresh_data(self):
        """Refresh all medicine data"""
        try:
            self.medicine_table.refresh_data()
            self.logger.info("Medicine data refreshed")
        except Exception as e:
            error_msg = f"Error refreshing data: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def add_new_medicine(self):
        """Start adding new medicine (clear form and focus)"""
        self.medicine_form.clear_form()
        self.current_medicine = None
        self.medicine_form.name_field.setFocus()
        self.logger.info("Started adding new medicine")
    
    def edit_selected_medicine(self):
        """Edit currently selected medicine"""
        if self.current_medicine:
            self.edit_medicine(self.current_medicine)
        else:
            QMessageBox.information(self, "No Selection", "Please select a medicine to edit.")
    
    def delete_selected_medicine(self):
        """Delete currently selected medicine"""
        if self.current_medicine:
            self.logger.info(f"Attempting to delete selected medicine: {self.current_medicine.name} (ID: {self.current_medicine.id})")
            self.delete_medicine(self.current_medicine)
        else:
            QMessageBox.information(self, "No Selection", "Please select a medicine to delete.")
            self.logger.warning("Delete attempted with no medicine selected")
    
    def show_selected_medicine_details(self):
        """Show details of currently selected medicine"""
        if self.current_medicine:
            self.show_medicine_details(self.current_medicine)
        else:
            QMessageBox.information(self, "No Selection", "Please select a medicine to view details.")
    
    def load_medicine_for_editing(self, medicine: Medicine):
        """Load medicine into form for editing"""
        self.medicine_form.load_medicine(medicine)
        self.current_medicine = medicine
        self.logger.info(f"Loaded medicine for editing: {medicine.name}")
    
    def get_selected_medicine(self) -> Optional[Medicine]:
        """Get currently selected medicine"""
        return self.current_medicine
    
    def search_medicines(self, query: str):
        """Search medicines in table"""
        self.medicine_table.search_field.setText(query)
        self.medicine_table._on_search_changed(query)
    
    def filter_by_category(self, category: str):
        """Filter medicines by category"""
        index = self.medicine_table.category_filter_combo.findText(category)
        if index >= 0:
            self.medicine_table.category_filter_combo.setCurrentIndex(index)
            self.medicine_table._on_category_filter_changed(category)
    
    def filter_by_stock_status(self, status: str):
        """Filter medicines by stock status"""
        index = self.medicine_table.stock_filter_combo.findText(status)
        if index >= 0:
            self.medicine_table.stock_filter_combo.setCurrentIndex(index)
            self.medicine_table._on_stock_filter_changed(status)
    
    def clear_all_filters(self):
        """Clear all search and filter criteria"""
        self.medicine_table.clear_filters()
    
    def get_medicine_statistics(self) -> dict:
        """Get medicine statistics from table"""
        medicines = self.medicine_table.filtered_medicines
        
        return {
            'total_medicines': len(medicines),
            'low_stock_count': sum(1 for m in medicines if m.is_low_stock()),
            'expired_count': sum(1 for m in medicines if m.is_expired()),
            'expiring_soon_count': sum(1 for m in medicines if m.is_expiring_soon()),
            'total_value': sum(m.get_total_value() for m in medicines),
            'total_cost': sum(m.get_total_cost() for m in medicines),
            'categories': list(set(m.category for m in medicines))
        }
    
    def export_medicine_data(self, format_type: str = "csv"):
        """Export medicine data (placeholder for future implementation)"""
        # This would be implemented in a future task
        self.logger.info(f"Export requested in {format_type} format")
        QMessageBox.information(
            self, 
            "Export", 
            f"Export to {format_type.upper()} will be implemented in a future update."
        )
    
    def set_medicine_manager(self, manager: MedicineManager):
        """Set the medicine manager for all components"""
        self.medicine_manager = manager
        self.medicine_form.set_medicine_manager(manager)
        self.medicine_table.medicine_manager = manager
        self.refresh_data()
    
    def enable_auto_refresh(self, enabled: bool):
        """Enable or disable auto-refresh"""
        self.medicine_table.auto_refresh_button.setChecked(enabled)
        self.medicine_table._toggle_auto_refresh(enabled)
    
    def get_form_widget(self) -> MedicineForm:
        """Get the medicine form widget"""
        return self.medicine_form
    
    def get_table_widget(self) -> MedicineTableWidget:
        """Get the medicine table widget"""
        return self.medicine_table
    
    def set_readonly_mode(self, readonly: bool):
        """Set readonly mode for role-based access control"""
        self.readonly_mode = readonly
        
        if readonly:
            # Hide the form for cashiers - they can only view medicines
            self.form_frame.hide()
            self.splitter.setSizes([0, 1000])  # Give all space to table
            
            # Disable editing actions in table
            if hasattr(self.medicine_table, 'set_readonly_mode'):
                self.medicine_table.set_readonly_mode(True)
            
            self.logger.info("Medicine management set to read-only mode")
        else:
            # Show the form for admins
            self.form_frame.show()
            self.splitter.setSizes([300, 700])  # Restore normal proportions
            
            # Enable editing actions in table
            if hasattr(self.medicine_table, 'set_readonly_mode'):
                self.medicine_table.set_readonly_mode(False)
            
            self.logger.info("Medicine management set to full access mode")
    
    def is_readonly_mode(self) -> bool:
        """Check if widget is in readonly mode"""
        return self.readonly_mode