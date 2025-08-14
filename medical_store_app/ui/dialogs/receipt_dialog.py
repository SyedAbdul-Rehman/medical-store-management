"""
Receipt Dialog for Medical Store Management Application
Displays transaction receipt in a formatted dialog
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QFrame, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...models.sale import Sale


class ReceiptDialog(QDialog):
    """Dialog for displaying transaction receipt"""
    
    def __init__(self, sale: Sale, parent=None):
        super().__init__(parent)
        self.sale = sale
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.populate_receipt()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(f"Receipt - Transaction {self.sale.id}")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Transaction Receipt")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2D9CDB; padding: 10px;")
        layout.addWidget(header_label)
        
        # Receipt content area
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setFont(QFont("Courier New", 10))
        self.receipt_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.receipt_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.print_button = QPushButton("Print")
        self.print_button.setMinimumHeight(35)
        self.print_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.close_button = QPushButton("Close")
        self.close_button.setMinimumHeight(35)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.print_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.print_button.clicked.connect(self._print_receipt)
        self.close_button.clicked.connect(self.accept)
    
    def populate_receipt(self):
        """Populate receipt with transaction data"""
        try:
            receipt_text = self._generate_receipt_text()
            self.receipt_text.setPlainText(receipt_text)
        except Exception as e:
            self.logger.error(f"Error populating receipt: {str(e)}")
            self.receipt_text.setPlainText(f"Error loading receipt data: {str(e)}")
    
    def _generate_receipt_text(self) -> str:
        """Generate formatted receipt text"""
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append("MEDICAL STORE MANAGEMENT SYSTEM")
        lines.append("=" * 50)
        lines.append("")
        
        # Transaction details
        lines.append(f"Transaction ID: {self.sale.id}")
        lines.append(f"Date: {self.sale.date}")
        lines.append(f"Payment Method: {self.sale.payment_method.title()}")
        
        if self.sale.cashier_id:
            lines.append(f"Cashier ID: {self.sale.cashier_id}")
        
        if hasattr(self.sale, 'customer_name') and self.sale.customer_name:
            lines.append(f"Customer: {self.sale.customer_name}")
        
        lines.append("")
        lines.append("-" * 50)
        lines.append("ITEMS PURCHASED")
        lines.append("-" * 50)
        
        # Items
        for i, item in enumerate(self.sale.items, 1):
            lines.append(f"{i}. {item.name}")
            lines.append(f"   Quantity: {item.quantity}")
            lines.append(f"   Unit Price: ${item.unit_price:.2f}")
            lines.append(f"   Total: ${item.total_price:.2f}")
            
            if item.batch_no:
                lines.append(f"   Batch No: {item.batch_no}")
            
            lines.append("")
        
        # Totals
        lines.append("-" * 50)
        lines.append("PAYMENT SUMMARY")
        lines.append("-" * 50)
        lines.append(f"Subtotal: ${self.sale.subtotal:.2f}")
        
        if self.sale.discount > 0:
            lines.append(f"Discount: -${self.sale.discount:.2f}")
        
        if self.sale.tax > 0:
            lines.append(f"Tax: ${self.sale.tax:.2f}")
        
        lines.append("-" * 50)
        lines.append(f"TOTAL AMOUNT: ${self.sale.total:.2f}")
        lines.append("=" * 50)
        lines.append("")
        lines.append("Thank you for your business!")
        lines.append("Please keep this receipt for your records.")
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _print_receipt(self):
        """Print the receipt"""
        try:
            # For now, just show a placeholder message
            QMessageBox.information(
                self,
                "Print Receipt",
                f"Receipt for Transaction {self.sale.id} would be printed here.\n"
                f"This feature will be fully implemented with printer integration."
            )
            
            self.logger.info(f"Print receipt requested for transaction {self.sale.id}")
            
        except Exception as e:
            self.logger.error(f"Error printing receipt: {str(e)}")
            QMessageBox.warning(self, "Print Error", "Failed to print receipt.")