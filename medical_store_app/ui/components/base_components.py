"""
Base UI components for Medical Store Management Application
Provides reusable form components, validation widgets, and common UI elements
"""

import logging
from typing import Optional, Callable, Any, List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateEdit, QTextEdit, QCheckBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QSizePolicy, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QDate, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator, QDoubleValidator, QIntValidator


class ValidationMixin:
    """Mixin class for input validation functionality"""
    
    def __init__(self):
        self.validators = []
        self.error_label = None
    
    def add_validator(self, validator_func: Callable[[Any], tuple[bool, str]]):
        """Add a validation function"""
        self.validators.append(validator_func)
    
    def validate_input(self) -> tuple[bool, str]:
        """Run all validators and return result"""
        for validator in self.validators:
            is_valid, error_message = validator(self.get_value())
            if not is_valid:
                return False, error_message
        return True, ""
    
    def get_value(self):
        """Override in subclasses to return the widget value"""
        raise NotImplementedError
    
    def show_error(self, message: str):
        """Show error message"""
        if self.error_label:
            self.error_label.setText(message)
            self.error_label.setStyleSheet("color: #E74C3C; font-size: 11px;")
            self.error_label.show()
    
    def clear_error(self):
        """Clear error message"""
        if self.error_label:
            self.error_label.clear()
            self.error_label.hide()


class ValidatedLineEdit(QLineEdit, ValidationMixin):
    """Line edit with built-in validation"""
    
    validation_changed = Signal(bool)  # Emitted when validation state changes
    
    def __init__(self, placeholder: str = "", parent=None):
        QLineEdit.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        self.setPlaceholderText(placeholder)
        self.textChanged.connect(self._on_text_changed)
        
        # Create error label
        self.error_label = QLabel()
        self.error_label.hide()
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #2D9CDB;
                outline: none;
            }
            
            QLineEdit[error="true"] {
                border-color: #E74C3C;
            }
        """)
    
    def _on_text_changed(self):
        """Handle text change and validate"""
        is_valid, error_message = self.validate_input()
        
        if is_valid:
            self.clear_error()
            self.setProperty("error", False)
        else:
            self.show_error(error_message)
            self.setProperty("error", True)
        
        # Update styling
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.validation_changed.emit(is_valid)
    
    def get_value(self):
        """Get the current text value"""
        return self.text()
    
    def get_error_label(self):
        """Get the error label widget"""
        return self.error_label


class ValidatedComboBox(QComboBox, ValidationMixin):
    """Combo box with built-in validation"""
    
    validation_changed = Signal(bool)
    
    def __init__(self, items: List[str] = None, parent=None):
        QComboBox.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        if items:
            self.addItems(items)
        
        self.currentTextChanged.connect(self._on_selection_changed)
        
        # Create error label
        self.error_label = QLabel()
        self.error_label.hide()
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-width: 120px;
            }
            
            QComboBox:focus {
                border-color: #2D9CDB;
            }
            
            QComboBox[error="true"] {
                border-color: #E74C3C;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #666;
                width: 6px;
                height: 6px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
            }
        """)
    
    def _on_selection_changed(self):
        """Handle selection change and validate"""
        is_valid, error_message = self.validate_input()
        
        if is_valid:
            self.clear_error()
            self.setProperty("error", False)
        else:
            self.show_error(error_message)
            self.setProperty("error", True)
        
        # Update styling
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.validation_changed.emit(is_valid)
    
    def get_value(self):
        """Get the current selected value"""
        return self.currentText()
    
    def get_error_label(self):
        """Get the error label widget"""
        return self.error_label


class ValidatedSpinBox(QSpinBox, ValidationMixin):
    """Spin box with built-in validation"""
    
    validation_changed = Signal(bool)
    
    def __init__(self, min_value: int = 0, max_value: int = 999999, parent=None):
        QSpinBox.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        self.setRange(min_value, max_value)
        self.valueChanged.connect(self._on_value_changed)
        
        # Create error label
        self.error_label = QLabel()
        self.error_label.hide()
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QSpinBox {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-width: 80px;
            }
            
            QSpinBox:focus {
                border-color: #2D9CDB;
            }
            
            QSpinBox[error="true"] {
                border-color: #E74C3C;
            }
        """)
    
    def _on_value_changed(self):
        """Handle value change and validate"""
        is_valid, error_message = self.validate_input()
        
        if is_valid:
            self.clear_error()
            self.setProperty("error", False)
        else:
            self.show_error(error_message)
            self.setProperty("error", True)
        
        # Update styling
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.validation_changed.emit(is_valid)
    
    def get_value(self):
        """Get the current value"""
        return self.value()
    
    def get_error_label(self):
        """Get the error label widget"""
        return self.error_label


class ValidatedDoubleSpinBox(QDoubleSpinBox, ValidationMixin):
    """Double spin box with built-in validation"""
    
    validation_changed = Signal(bool)
    
    def __init__(self, min_value: float = 0.0, max_value: float = 999999.99, decimals: int = 2, parent=None):
        QDoubleSpinBox.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        self.setRange(min_value, max_value)
        self.setDecimals(decimals)
        self.valueChanged.connect(self._on_value_changed)
        
        # Create error label
        self.error_label = QLabel()
        self.error_label.hide()
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-width: 100px;
            }
            
            QDoubleSpinBox:focus {
                border-color: #2D9CDB;
            }
            
            QDoubleSpinBox[error="true"] {
                border-color: #E74C3C;
            }
        """)
    
    def _on_value_changed(self):
        """Handle value change and validate"""
        is_valid, error_message = self.validate_input()
        
        if is_valid:
            self.clear_error()
            self.setProperty("error", False)
        else:
            self.show_error(error_message)
            self.setProperty("error", True)
        
        # Update styling
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.validation_changed.emit(is_valid)
    
    def get_value(self):
        """Get the current value"""
        return self.value()
    
    def get_error_label(self):
        """Get the error label widget"""
        return self.error_label


class ValidatedDateEdit(QDateEdit, ValidationMixin):
    """Date edit with built-in validation"""
    
    validation_changed = Signal(bool)
    
    def __init__(self, parent=None):
        QDateEdit.__init__(self, parent)
        ValidationMixin.__init__(self)
        
        self.setDate(QDate.currentDate())
        self.setCalendarPopup(True)
        self.dateChanged.connect(self._on_date_changed)
        
        # Create error label
        self.error_label = QLabel()
        self.error_label.hide()
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up widget styling"""
        self.setStyleSheet("""
            QDateEdit {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-width: 120px;
            }
            
            QDateEdit:focus {
                border-color: #2D9CDB;
            }
            
            QDateEdit[error="true"] {
                border-color: #E74C3C;
            }
        """)
    
    def _on_date_changed(self):
        """Handle date change and validate"""
        is_valid, error_message = self.validate_input()
        
        if is_valid:
            self.clear_error()
            self.setProperty("error", False)
        else:
            self.show_error(error_message)
            self.setProperty("error", True)
        
        # Update styling
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.validation_changed.emit(is_valid)
    
    def get_value(self):
        """Get the current date value"""
        return self.date()
    
    def get_error_label(self):
        """Get the error label widget"""
        return self.error_label


class StyledButton(QPushButton):
    """Styled button with consistent appearance"""
    
    def __init__(self, text: str = "", button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up button styling based on type"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
        """
        
        if self.button_type == "primary":
            style = base_style + """
                QPushButton {
                    background-color: #2D9CDB;
                    color: white;
                }
                
                QPushButton:hover {
                    background-color: #1E88E5;
                }
                
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                }
            """
        elif self.button_type == "secondary":
            style = base_style + """
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                }
                
                QPushButton:hover {
                    background-color: #229954;
                }
                
                QPushButton:pressed {
                    background-color: #1E8449;
                }
                
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                }
            """
        elif self.button_type == "danger":
            style = base_style + """
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                }
                
                QPushButton:hover {
                    background-color: #C0392B;
                }
                
                QPushButton:pressed {
                    background-color: #A93226;
                }
                
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                }
            """
        else:  # outline
            style = base_style + """
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #E1E5E9;
                    color: #333333;
                }
                
                QPushButton:hover {
                    background-color: #F1F3F4;
                    border-color: #2D9CDB;
                    color: #2D9CDB;
                }
                
                QPushButton:pressed {
                    background-color: #E3F2FD;
                }
                
                QPushButton:disabled {
                    background-color: transparent;
                    border-color: #BDBDBD;
                    color: #BDBDBD;
                }
            """
        
        self.setStyleSheet(style)


class StyledTable(QTableWidget):
    """Styled table widget with consistent appearance"""
    
    def __init__(self, rows: int = 0, columns: int = 0, parent=None):
        super().__init__(rows, columns, parent)
        self._setup_styling()
        self._setup_behavior()
    
    def _setup_styling(self):
        """Set up table styling"""
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E1E5E9;
                border-radius: 6px;
                background-color: white;
                gridline-color: #F1F3F4;
                font-size: 13px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F3F4;
            }
            
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
            }
            
            QTableWidget::item:hover {
                background-color: #F8F9FA;
            }
            
            QHeaderView::section {
                background-color: #F8F9FA;
                border: none;
                border-bottom: 2px solid #E1E5E9;
                border-right: 1px solid #E1E5E9;
                padding: 10px 8px;
                font-weight: 600;
                color: #333333;
            }
            
            QHeaderView::section:hover {
                background-color: #F1F3F4;
            }
        """)
    
    def _setup_behavior(self):
        """Set up table behavior"""
        # Set selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Set resize mode for headers
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Alternate row colors
        self.setAlternatingRowColors(True)


class FormContainer(QWidget):
    """Container widget for forms with consistent layout and validation"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.form_fields = {}
        self.validators = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the form container UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Add title if provided
        if self.title:
            title_label = QLabel(self.title)
            title_label.setObjectName("formTitle")
            font = QFont()
            font.setPointSize(16)
            font.setBold(True)
            title_label.setFont(font)
            self.main_layout.addWidget(title_label)
        
        # Create form layout
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        form_widget = QWidget()
        form_widget.setLayout(self.form_layout)
        self.main_layout.addWidget(form_widget)
        
        # Add stretch
        self.main_layout.addStretch()
        
        self._setup_styling()
    
    def _setup_styling(self):
        """Set up form container styling"""
        self.setStyleSheet("""
            #formTitle {
                color: #333333;
                margin-bottom: 10px;
            }
            
            QLabel {
                color: #333333;
                font-weight: 500;
            }
        """)
    
    def add_field(self, label: str, widget: QWidget, field_name: str = None):
        """Add a field to the form"""
        if field_name is None:
            field_name = label.lower().replace(" ", "_")
        
        # Create label
        label_widget = QLabel(label)
        
        # Create container for widget and error label
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        
        container_layout.addWidget(widget)
        
        # Add error label if widget has validation
        if hasattr(widget, 'get_error_label'):
            error_label = widget.get_error_label()
            container_layout.addWidget(error_label)
        
        # Add to form layout
        self.form_layout.addRow(label_widget, container)
        
        # Store field reference
        self.form_fields[field_name] = widget
    
    def get_field(self, field_name: str):
        """Get a field widget by name"""
        return self.form_fields.get(field_name)
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get all form data as a dictionary"""
        data = {}
        for field_name, widget in self.form_fields.items():
            if hasattr(widget, 'get_value'):
                data[field_name] = widget.get_value()
            elif hasattr(widget, 'text'):
                data[field_name] = widget.text()
            elif hasattr(widget, 'value'):
                data[field_name] = widget.value()
            elif hasattr(widget, 'currentText'):
                data[field_name] = widget.currentText()
        return data
    
    def validate_form(self) -> tuple[bool, List[str]]:
        """Validate all form fields"""
        errors = []
        is_valid = True
        
        for field_name, widget in self.form_fields.items():
            if hasattr(widget, 'validate_input'):
                field_valid, error_message = widget.validate_input()
                if not field_valid:
                    is_valid = False
                    errors.append(f"{field_name}: {error_message}")
        
        return is_valid, errors
    
    def clear_form(self):
        """Clear all form fields"""
        for widget in self.form_fields.values():
            if hasattr(widget, 'clear') and not hasattr(widget, 'setValue'):
                # For line edits and text edits
                widget.clear()
            elif hasattr(widget, 'setValue') and hasattr(widget, 'minimum'):
                # For spin boxes
                widget.setValue(widget.minimum())
            elif hasattr(widget, 'setCurrentIndex'):
                # For combo boxes
                widget.setCurrentIndex(0)
            elif hasattr(widget, 'setDate'):
                # For date edits
                from PySide6.QtCore import QDate
                widget.setDate(QDate.currentDate())