"""
Base dialog classes for Medical Store Management Application
Provides consistent dialog patterns and behavior
"""

import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget, QScrollArea, QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from ..components.base_components import StyledButton, FormContainer


class BaseDialog(QDialog):
    """Base dialog class with consistent styling and behavior"""
    
    def __init__(self, title: str = "Dialog", parent=None, modal: bool = True):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Dialog properties
        self.setWindowTitle(title)
        self.setModal(modal)
        self.setMinimumSize(400, 300)
        
        # Initialize UI components
        self.main_layout = None
        self.content_area = None
        self.button_area = None
        
        # Set up UI
        self._setup_ui()
        self._setup_styling()
        
        self.logger.info(f"Base dialog initialized: {title}")
    
    def _setup_ui(self):
        """Set up the dialog UI structure"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Content area
        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        self.main_layout.addWidget(self.content_area)
        
        # Button area
        self._create_button_area()
    
    def _create_button_area(self):
        """Create the button area at the bottom of the dialog"""
        self.button_area = QFrame()
        self.button_area.setObjectName("buttonArea")
        self.button_area.setFixedHeight(60)
        
        self.button_layout = QHBoxLayout(self.button_area)
        self.button_layout.setContentsMargins(20, 10, 20, 10)
        self.button_layout.addStretch()  # Push buttons to the right
        
        self.main_layout.addWidget(self.button_area)
    
    def _setup_styling(self):
        """Set up dialog styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
            
            #contentArea {
                background-color: white;
                border-bottom: 1px solid #E1E5E9;
            }
            
            #buttonArea {
                background-color: #F8F9FA;
                border-top: 1px solid #E1E5E9;
            }
        """)
    
    def add_button(self, text: str, button_type: str = "outline", callback=None) -> StyledButton:
        """Add a button to the button area"""
        button = StyledButton(text, button_type)
        
        if callback:
            button.clicked.connect(callback)
        
        self.button_layout.addWidget(button)
        return button
    
    def add_standard_buttons(self, ok_callback=None, cancel_callback=None):
        """Add standard OK and Cancel buttons"""
        # Cancel button
        cancel_btn = self.add_button("Cancel", "outline", cancel_callback or self.reject)
        
        # OK button
        ok_btn = self.add_button("OK", "primary", ok_callback or self.accept)
        
        return ok_btn, cancel_btn
    
    def set_content_widget(self, widget: QWidget):
        """Set the main content widget"""
        # Clear existing content
        if self.content_area.layout():
            while self.content_area.layout().count():
                child = self.content_area.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout(self.content_area)
            layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_area.layout().addWidget(widget)
    
    def center_on_parent(self):
        """Center the dialog on its parent window"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            dialog_geometry = self.geometry()
            
            x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2
            
            self.move(x, y)
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.center_on_parent()


class FormDialog(BaseDialog):
    """Dialog with form functionality"""
    
    # Signals
    form_submitted = Signal(dict)  # Emitted when form is successfully submitted
    
    def __init__(self, title: str = "Form Dialog", form_title: str = "", parent=None):
        self.form_container = None
        self.ok_button = None
        self.cancel_button = None
        
        super().__init__(title, parent)
        
        # Create form container
        self.form_container = FormContainer(form_title)
        self.set_content_widget(self.form_container)
        
        # Add standard buttons
        self.ok_button, self.cancel_button = self.add_standard_buttons(
            ok_callback=self._on_ok_clicked
        )
        
        # Initially disable OK button
        self.ok_button.setEnabled(False)
    
    def _on_ok_clicked(self):
        """Handle OK button click"""
        # Validate form
        is_valid, errors = self.form_container.validate_form()
        
        if is_valid:
            # Get form data
            form_data = self.form_container.get_form_data()
            
            # Emit signal
            self.form_submitted.emit(form_data)
            
            # Accept dialog
            self.accept()
        else:
            # Show validation errors
            error_message = "Please fix the following errors:\n\n" + "\n".join(errors)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", error_message)
    
    def add_form_field(self, label: str, widget, field_name: str = None):
        """Add a field to the form"""
        self.form_container.add_field(label, widget, field_name)
        
        # Connect validation signal if available
        if hasattr(widget, 'validation_changed'):
            widget.validation_changed.connect(self._on_validation_changed)
    
    def _on_validation_changed(self):
        """Handle validation state change"""
        # Check if all fields are valid
        is_valid, _ = self.form_container.validate_form()
        self.ok_button.setEnabled(is_valid)
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get form data"""
        return self.form_container.get_form_data()
    
    def set_form_data(self, data: Dict[str, Any]):
        """Set form data"""
        for field_name, value in data.items():
            field = self.form_container.get_field(field_name)
            if field:
                if hasattr(field, 'setText'):
                    field.setText(str(value))
                elif hasattr(field, 'setValue'):
                    field.setValue(value)
                elif hasattr(field, 'setCurrentText'):
                    field.setCurrentText(str(value))
    
    def clear_form(self):
        """Clear all form fields"""
        self.form_container.clear_form()


class ConfirmationDialog(BaseDialog):
    """Dialog for confirmation prompts"""
    
    def __init__(self, title: str = "Confirm", message: str = "", parent=None):
        super().__init__(title, parent)
        self.setFixedSize(400, 200)
        
        # Create content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 20)
        
        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        
        font = QFont()
        font.setPointSize(12)
        message_label.setFont(font)
        
        content_layout.addWidget(message_label)
        content_layout.addStretch()
        
        self.set_content_widget(content_widget)
        
        # Add buttons
        self.add_standard_buttons()
    
    @staticmethod
    def confirm(parent, title: str, message: str) -> bool:
        """Show confirmation dialog and return result"""
        dialog = ConfirmationDialog(title, message, parent)
        return dialog.exec() == QDialog.Accepted


class MessageDialog(BaseDialog):
    """Dialog for displaying messages"""
    
    def __init__(self, title: str = "Message", message: str = "", message_type: str = "info", parent=None):
        super().__init__(title, parent)
        self.setFixedSize(400, 200)
        
        # Create content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 20)
        
        # Icon and message layout
        message_layout = QHBoxLayout()
        
        # Icon label (using text icons for simplicity)
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        
        if message_type == "error":
            icon_label.setText("❌")
            icon_label.setStyleSheet("color: #E74C3C; font-size: 20px;")
        elif message_type == "warning":
            icon_label.setText("⚠️")
            icon_label.setStyleSheet("color: #F39C12; font-size: 20px;")
        elif message_type == "success":
            icon_label.setText("✅")
            icon_label.setStyleSheet("color: #27AE60; font-size: 20px;")
        else:  # info
            icon_label.setText("ℹ️")
            icon_label.setStyleSheet("color: #2D9CDB; font-size: 20px;")
        
        message_layout.addWidget(icon_label)
        
        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        
        font = QFont()
        font.setPointSize(11)
        message_label.setFont(font)
        
        message_layout.addWidget(message_label)
        
        content_layout.addLayout(message_layout)
        content_layout.addStretch()
        
        self.set_content_widget(content_widget)
        
        # Add OK button only
        self.add_button("OK", "primary", self.accept)
    
    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show info message dialog"""
        dialog = MessageDialog(title, message, "info", parent)
        dialog.exec()
    
    @staticmethod
    def show_warning(parent, title: str, message: str):
        """Show warning message dialog"""
        dialog = MessageDialog(title, message, "warning", parent)
        dialog.exec()
    
    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show error message dialog"""
        dialog = MessageDialog(title, message, "error", parent)
        dialog.exec()
    
    @staticmethod
    def show_success(parent, title: str, message: str):
        """Show success message dialog"""
        dialog = MessageDialog(title, message, "success", parent)
        dialog.exec()


class ProgressDialog(BaseDialog):
    """Dialog for showing progress of long-running operations"""
    
    def __init__(self, title: str = "Progress", message: str = "Please wait...", parent=None):
        super().__init__(title, parent, modal=True)
        self.setFixedSize(400, 150)
        
        # Remove close button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        
        # Create content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 20)
        
        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        
        font = QFont()
        font.setPointSize(11)
        self.message_label.setFont(font)
        
        content_layout.addWidget(self.message_label)
        
        # Progress indicator (simple animated text)
        self.progress_label = QLabel("●○○○○")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #2D9CDB; font-size: 16px;")
        
        content_layout.addWidget(self.progress_label)
        
        self.set_content_widget(content_widget)
        
        # Animation timer for progress indicator
        from PySide6.QtCore import QTimer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_progress)
        self.animation_step = 0
        
    def _animate_progress(self):
        """Animate the progress indicator"""
        patterns = ["●○○○○", "○●○○○", "○○●○○", "○○○●○", "○○○○●"]
        self.progress_label.setText(patterns[self.animation_step % len(patterns)])
        self.animation_step += 1
    
    def start_progress(self):
        """Start the progress animation"""
        self.animation_timer.start(200)  # Update every 200ms
    
    def stop_progress(self):
        """Stop the progress animation"""
        self.animation_timer.stop()
    
    def update_message(self, message: str):
        """Update the progress message"""
        self.message_label.setText(message)
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.start_progress()
    
    def closeEvent(self, event):
        """Handle close event"""
        self.stop_progress()
        super().closeEvent(event)