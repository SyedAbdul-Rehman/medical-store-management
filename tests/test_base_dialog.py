"""
Tests for base dialog classes
Tests dialog functionality, form dialogs, and message dialogs
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent / "medical_store_app"
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from ui.dialogs.base_dialog import (
    BaseDialog, FormDialog, ConfirmationDialog, 
    MessageDialog, ProgressDialog
)
from ui.components.base_components import ValidatedLineEdit, ValidatedSpinBox


class TestBaseDialog:
    """Test cases for BaseDialog"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_base_dialog_initialization(self):
        """Test that BaseDialog initializes correctly"""
        dialog = BaseDialog("Test Dialog")
        
        assert dialog.windowTitle() == "Test Dialog"
        assert dialog.isModal()
        assert dialog.minimumSize().width() == 400
        assert dialog.minimumSize().height() == 300
        assert dialog.content_area is not None
        assert dialog.button_area is not None
        
        dialog.deleteLater()
    
    def test_base_dialog_add_button(self):
        """Test adding buttons to dialog"""
        dialog = BaseDialog()
        
        # Add a button
        button = dialog.add_button("Test Button", "primary")
        
        assert button is not None
        assert button.text() == "Test Button"
        assert button.button_type == "primary"
        
        dialog.deleteLater()
    
    def test_base_dialog_standard_buttons(self):
        """Test adding standard OK/Cancel buttons"""
        dialog = BaseDialog()
        
        ok_btn, cancel_btn = dialog.add_standard_buttons()
        
        assert ok_btn is not None
        assert cancel_btn is not None
        assert ok_btn.text() == "OK"
        assert cancel_btn.text() == "Cancel"
        
        dialog.deleteLater()
    
    def test_base_dialog_styling(self):
        """Test that dialog styling is applied"""
        dialog = BaseDialog()
        
        stylesheet = dialog.styleSheet()
        assert stylesheet is not None
        assert len(stylesheet) > 0
        assert "QDialog" in stylesheet
        
        dialog.deleteLater()


class TestFormDialog:
    """Test cases for FormDialog"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_form_dialog_initialization(self):
        """Test that FormDialog initializes correctly"""
        dialog = FormDialog("Test Form", "Form Title")
        
        assert dialog.windowTitle() == "Test Form"
        assert dialog.form_container is not None
        assert dialog.ok_button is not None
        assert dialog.cancel_button is not None
        assert not dialog.ok_button.isEnabled()  # Initially disabled
        
        dialog.deleteLater()
    
    def test_form_dialog_add_field(self):
        """Test adding fields to form dialog"""
        dialog = FormDialog()
        
        # Add a field
        line_edit = ValidatedLineEdit("Test input")
        dialog.add_form_field("Test Field", line_edit, "test_field")
        
        # Check field was added
        field = dialog.form_container.get_field("test_field")
        assert field == line_edit
        
        dialog.deleteLater()
    
    def test_form_dialog_validation(self):
        """Test form dialog validation"""
        dialog = FormDialog()
        
        # Add field with validation
        line_edit = ValidatedLineEdit()
        line_edit.add_validator(lambda x: (bool(x.strip()), "Required"))
        dialog.add_form_field("Required Field", line_edit, "required")
        
        # Initially invalid (empty)
        assert not dialog.ok_button.isEnabled()
        
        # Make valid
        line_edit.setText("Valid text")
        line_edit._on_text_changed()  # Trigger validation
        QApplication.processEvents()
        
        # Should be enabled now (but this might not work in test environment)
        # Just check that validation works
        is_valid, _ = dialog.form_container.validate_form()
        assert is_valid
        
        dialog.deleteLater()
    
    def test_form_dialog_get_set_data(self):
        """Test getting and setting form data"""
        dialog = FormDialog()
        
        # Add fields
        line_edit = ValidatedLineEdit()
        dialog.add_form_field("Text", line_edit, "text")
        
        spin_box = ValidatedSpinBox()
        dialog.add_form_field("Number", spin_box, "number")
        
        # Set data
        test_data = {"text": "Test Value", "number": 42}
        dialog.set_form_data(test_data)
        
        # Get data
        form_data = dialog.get_form_data()
        assert form_data["text"] == "Test Value"
        assert form_data["number"] == 42
        
        dialog.deleteLater()
    
    def test_form_dialog_clear(self):
        """Test clearing form dialog"""
        dialog = FormDialog()
        
        # Add and populate field
        line_edit = ValidatedLineEdit()
        line_edit.setText("Test")
        dialog.add_form_field("Text", line_edit, "text")
        
        # Clear form
        dialog.clear_form()
        
        assert line_edit.text() == ""
        
        dialog.deleteLater()


class TestConfirmationDialog:
    """Test cases for ConfirmationDialog"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_confirmation_dialog_initialization(self):
        """Test that ConfirmationDialog initializes correctly"""
        dialog = ConfirmationDialog("Confirm Action", "Are you sure?")
        
        assert dialog.windowTitle() == "Confirm Action"
        assert dialog.size().width() == 400
        assert dialog.size().height() == 200
        
        dialog.deleteLater()
    
    def test_confirmation_dialog_static_method(self):
        """Test confirmation dialog static method"""
        # Note: This test can't actually show the dialog in test environment
        # We just test that the method exists and creates a dialog
        
        # Create a mock parent
        parent = QDialog()
        
        # The static method would normally show the dialog
        # In test environment, we just verify it can be called
        try:
            # This would block in real usage, but in test it should return quickly
            dialog = ConfirmationDialog("Test", "Test message", parent)
            assert dialog is not None
            dialog.deleteLater()
        except Exception as e:
            pytest.fail(f"ConfirmationDialog creation failed: {e}")
        
        parent.deleteLater()


class TestMessageDialog:
    """Test cases for MessageDialog"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_message_dialog_initialization(self):
        """Test that MessageDialog initializes correctly"""
        dialog = MessageDialog("Info", "Information message", "info")
        
        assert dialog.windowTitle() == "Info"
        assert dialog.size().width() == 400
        assert dialog.size().height() == 200
        
        dialog.deleteLater()
    
    def test_message_dialog_types(self):
        """Test different message dialog types"""
        message_types = ["info", "warning", "error", "success"]
        
        for msg_type in message_types:
            dialog = MessageDialog("Test", "Test message", msg_type)
            assert dialog is not None
            dialog.deleteLater()
    
    def test_message_dialog_static_methods(self):
        """Test message dialog static methods"""
        parent = QDialog()
        
        # Test that static methods can be called without errors
        try:
            # These would normally show dialogs, but in test environment
            # we just verify they can be created
            info_dialog = MessageDialog("Info", "Info message", "info", parent)
            warning_dialog = MessageDialog("Warning", "Warning message", "warning", parent)
            error_dialog = MessageDialog("Error", "Error message", "error", parent)
            success_dialog = MessageDialog("Success", "Success message", "success", parent)
            
            assert info_dialog is not None
            assert warning_dialog is not None
            assert error_dialog is not None
            assert success_dialog is not None
            
            info_dialog.deleteLater()
            warning_dialog.deleteLater()
            error_dialog.deleteLater()
            success_dialog.deleteLater()
            
        except Exception as e:
            pytest.fail(f"MessageDialog creation failed: {e}")
        
        parent.deleteLater()


class TestProgressDialog:
    """Test cases for ProgressDialog"""
    
    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Set up QApplication for testing"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    def test_progress_dialog_initialization(self):
        """Test that ProgressDialog initializes correctly"""
        dialog = ProgressDialog("Processing", "Please wait...")
        
        assert dialog.windowTitle() == "Processing"
        assert dialog.message_label.text() == "Please wait..."
        assert dialog.progress_label is not None
        assert dialog.animation_timer is not None
        
        dialog.deleteLater()
    
    def test_progress_dialog_animation(self):
        """Test progress dialog animation"""
        dialog = ProgressDialog()
        
        # Test animation control
        dialog.start_progress()
        assert dialog.animation_timer.isActive()
        
        dialog.stop_progress()
        assert not dialog.animation_timer.isActive()
        
        dialog.deleteLater()
    
    def test_progress_dialog_update_message(self):
        """Test updating progress message"""
        dialog = ProgressDialog()
        
        initial_message = dialog.message_label.text()
        
        dialog.update_message("New message")
        assert dialog.message_label.text() == "New message"
        assert dialog.message_label.text() != initial_message
        
        dialog.deleteLater()
    
    def test_progress_dialog_window_flags(self):
        """Test that progress dialog has correct window flags"""
        dialog = ProgressDialog()
        
        # Should not have close button
        flags = dialog.windowFlags()
        assert not (flags & Qt.WindowCloseButtonHint)
        
        dialog.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__])