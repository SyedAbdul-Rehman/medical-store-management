"""
Medicine Dialog for Medical Store Management Application
Provides dialog interface for editing and deleting medicines
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..components.base_components import StyledButton
from ..components.medicine_form import MedicineForm
from ...models.medicine import Medicine
from ...managers.medicine_manager import MedicineManager


class EditMedicineDialog(QDialog):
    """Dialog for editing medicine information"""
    
    # Signals
    medicine_updated = Signal(object)  # Emitted when medicine is successfully updated
    
    def __init__(self, medicine: Medicine, medicine_manager: MedicineManager, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        self.medicine_manager = medicine_manager
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._connect_signals()
        
        # Load medicine data into form
        self.medicine_form.load_medicine(medicine)
    
    def _setup_ui(self):
        """Set up dialog UI"""
        self.setWindowTitle(f"Edit Medicine - {self.medicine.name}")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        self.resize(600, 700)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2D9CDB;
                border: none;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(f"Edit Medicine")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(f"{self.medicine.name} - {self.medicine.category}")
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Medicine form
        self.medicine_form = MedicineForm(self.medicine_manager)
        layout.addWidget(self.medicine_form)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = StyledButton("Cancel", "outline")
        button_layout.addWidget(self.cancel_button)
        
        # Update button
        self.update_button = StyledButton("Update Medicine", "primary")
        button_layout.addWidget(self.update_button)
        
        layout.addLayout(button_layout)
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up dialog styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
    
    def _connect_signals(self):
        """Connect dialog signals"""
        self.cancel_button.clicked.connect(self.reject)
        self.update_button.clicked.connect(self._update_medicine)
        
        # Connect form signals
        self.medicine_form.medicine_saved.connect(self._on_medicine_updated)
        self.medicine_form.operation_finished.connect(self._on_operation_finished)
    
    def _update_medicine(self):
        """Trigger medicine update"""
        self.medicine_form.save_medicine()
    
    def _on_medicine_updated(self, medicine: Medicine):
        """Handle successful medicine update"""
        self.medicine_updated.emit(medicine)
        self.accept()
    
    def _on_operation_finished(self, success: bool, message: str):
        """Handle operation completion"""
        if success:
            self.logger.info(f"Medicine updated successfully: {message}")
        else:
            self.logger.error(f"Medicine update failed: {message}")
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Check for unsaved changes
        if self.medicine_form.is_form_dirty():
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()


class DeleteMedicineDialog(QDialog):
    """Dialog for confirming medicine deletion"""
    
    # Signals
    medicine_deleted = Signal(int)  # Emitted when medicine is successfully deleted
    
    def __init__(self, medicine: Medicine, medicine_manager: MedicineManager, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        self.medicine_manager = medicine_manager
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up dialog UI"""
        self.setWindowTitle("Delete Medicine")
        self.setModal(True)
        self.setFixedSize(450, 300)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Warning icon and title
        title_layout = QHBoxLayout()
        
        # Warning label
        warning_label = QLabel("⚠️")
        warning_label.setStyleSheet("font-size: 32px;")
        title_layout.addWidget(warning_label)
        
        # Title
        title_label = QLabel("Delete Medicine")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #E74C3C;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Warning message
        warning_text = f"""
Are you sure you want to delete this medicine?

<b>Medicine Details:</b>
• Name: {self.medicine.name}
• Category: {self.medicine.category}
• Batch No: {self.medicine.batch_no}
• Current Stock: {self.medicine.quantity} units
• Value: ${self.medicine.get_total_value():.2f}

<b style="color: #E74C3C;">This action cannot be undone!</b>
        """.strip()
        
        warning_label = QLabel(warning_text)
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            QLabel {
                background-color: #FFF5F5;
                border: 1px solid #FED7D7;
                border-radius: 6px;
                padding: 15px;
                color: #333333;
                line-height: 1.4;
            }
        """)
        layout.addWidget(warning_label)
        
        # Additional warning for medicines with stock
        if self.medicine.quantity > 0:
            stock_warning = QLabel(
                f"⚠️ This medicine has {self.medicine.quantity} units in stock. "
                "Deleting it will remove all inventory records."
            )
            stock_warning.setWordWrap(True)
            stock_warning.setStyleSheet("""
                QLabel {
                    background-color: #FFFBEB;
                    border: 1px solid #FED7AA;
                    border-radius: 6px;
                    padding: 10px;
                    color: #92400E;
                    font-weight: 500;
                }
            """)
            layout.addWidget(stock_warning)
        
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = StyledButton("Cancel", "outline")
        button_layout.addWidget(self.cancel_button)
        
        # Delete button
        self.delete_button = StyledButton("Delete Medicine", "danger")
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up dialog styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
    
    def _connect_signals(self):
        """Connect dialog signals"""
        self.cancel_button.clicked.connect(self.reject)
        self.delete_button.clicked.connect(self._delete_medicine)
    
    def _delete_medicine(self):
        """Delete the medicine"""
        try:
            # Disable buttons during operation
            self.cancel_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.delete_button.setText("Deleting...")
            
            # Perform deletion
            success, message = self.medicine_manager.delete_medicine(self.medicine.id)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.medicine_deleted.emit(self.medicine.id)
                self.accept()
                self.logger.info(f"Medicine deleted successfully: {message}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete medicine: {message}")
                self.logger.error(f"Medicine deletion failed: {message}")
                
                # Re-enable buttons
                self.cancel_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                self.delete_button.setText("Delete Medicine")
                
        except Exception as e:
            error_msg = f"Error deleting medicine: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.logger.error(error_msg)
            
            # Re-enable buttons
            self.cancel_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.delete_button.setText("Delete Medicine")


class MedicineDetailsDialog(QDialog):
    """Dialog for viewing detailed medicine information"""
    
    def __init__(self, medicine: Medicine, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up dialog UI"""
        self.setWindowTitle(f"Medicine Details - {self.medicine.name}")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #27AE60;
                border: none;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(self.medicine.name)
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(f"{self.medicine.category} • Batch: {self.medicine.batch_no}")
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Content
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Basic Information
        self._add_section(content_layout, "Basic Information", [
            ("Medicine Name", self.medicine.name),
            ("Category", self.medicine.category),
            ("Batch Number", self.medicine.batch_no),
            ("Barcode", self.medicine.barcode or "Not specified"),
        ])
        
        # Stock Information
        stock_status = self.medicine.get_stock_status()
        stock_color = "#E74C3C" if stock_status in ["Out of Stock", "Low Stock"] else "#27AE60"
        
        self._add_section(content_layout, "Stock Information", [
            ("Current Quantity", f"{self.medicine.quantity} units"),
            ("Stock Status", f'<span style="color: {stock_color}; font-weight: bold;">{stock_status}</span>'),
            ("Expiry Date", self.medicine.expiry_date),
            ("Days Until Expiry", self._get_days_until_expiry()),
        ])
        
        # Pricing Information
        profit_margin = self.medicine.get_profit_margin()
        margin_color = "#27AE60" if profit_margin > 0 else "#E74C3C"
        
        self._add_section(content_layout, "Pricing Information", [
            ("Purchase Price", f"${self.medicine.purchase_price:.2f}"),
            ("Selling Price", f"${self.medicine.selling_price:.2f}"),
            ("Profit per Unit", f"${self.medicine.get_profit_amount():.2f}"),
            ("Profit Margin", f'<span style="color: {margin_color}; font-weight: bold;">{profit_margin:.1f}%</span>'),
        ])
        
        # Value Information
        self._add_section(content_layout, "Value Information", [
            ("Total Stock Value", f"${self.medicine.get_total_value():.2f}"),
            ("Total Stock Cost", f"${self.medicine.get_total_cost():.2f}"),
            ("Potential Profit", f"${self.medicine.get_total_value() - self.medicine.get_total_cost():.2f}"),
        ])
        
        layout.addWidget(content_frame)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 0, 30, 30)
        button_layout.addStretch()
        
        close_button = StyledButton("Close", "primary")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self._setup_styling()
    
    def _add_section(self, layout: QVBoxLayout, title: str, items: list):
        """Add a section with title and items"""
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 5px;
                border-bottom: 2px solid #E1E5E9;
                padding-bottom: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Section items
        for label, value in items:
            item_layout = QHBoxLayout()
            
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: 500; color: #666666;")
            label_widget.setMinimumWidth(120)
            
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #333333;")
            
            item_layout.addWidget(label_widget)
            item_layout.addWidget(value_widget)
            item_layout.addStretch()
            
            layout.addLayout(item_layout)
    
    def _get_days_until_expiry(self) -> str:
        """Get days until expiry as formatted string"""
        try:
            from datetime import datetime, date
            expiry_date = datetime.strptime(self.medicine.expiry_date, "%Y-%m-%d").date()
            days_diff = (expiry_date - date.today()).days
            
            if days_diff < 0:
                return f'<span style="color: #E74C3C; font-weight: bold;">Expired {abs(days_diff)} days ago</span>'
            elif days_diff == 0:
                return '<span style="color: #E74C3C; font-weight: bold;">Expires today</span>'
            elif days_diff <= 30:
                return f'<span style="color: #F57C00; font-weight: bold;">{days_diff} days</span>'
            else:
                return f"{days_diff} days"
        except ValueError:
            return "Invalid date"
    
    def _setup_styling(self):
        """Set up dialog styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)