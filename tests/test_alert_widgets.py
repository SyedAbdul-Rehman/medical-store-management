"""
Tests for Alert Widgets
"""

import pytest
import sys
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# Add the project root to the path
sys.path.insert(0, '.')

from medical_store_app.ui.components.alert_widgets import (
    AlertCard, AlertSection, AlertThresholdDialog, AlertSystemWidget
)
from medical_store_app.models.medicine import Medicine
from medical_store_app.managers.medicine_manager import MedicineManager
from medical_store_app.repositories.settings_repository import SettingsRepository


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def sample_medicines():
    """Create sample medicines for testing"""
    today = date.today()
    
    # Low stock medicine
    low_stock_medicine = Medicine(
        id=1,
        name="Low Stock Medicine",
        category="Test Category",
        batch_no="LS001",
        expiry_date=(today + timedelta(days=100)).isoformat(),
        quantity=5,  # Below default threshold of 10
        purchase_price=10.0,
        selling_price=15.0,
        barcode="LS001"
    )
    
    # Expired medicine
    expired_medicine = Medicine(
        id=2,
        name="Expired Medicine",
        category="Test Category",
        batch_no="EXP001",
        expiry_date=(today - timedelta(days=10)).isoformat(),
        quantity=20,
        purchase_price=8.0,
        selling_price=12.0,
        barcode="EXP001"
    )
    
    # Expiring soon medicine
    expiring_soon_medicine = Medicine(
        id=3,
        name="Expiring Soon Medicine",
        category="Test Category",
        batch_no="ES001",
        expiry_date=(today + timedelta(days=15)).isoformat(),
        quantity=30,
        purchase_price=12.0,
        selling_price=18.0,
        barcode="ES001"
    )
    
    return {
        'low_stock': low_stock_medicine,
        'expired': expired_medicine,
        'expiring_soon': expiring_soon_medicine
    }


@pytest.fixture
def mock_medicine_manager():
    """Create mock medicine manager"""
    manager = Mock(spec=MedicineManager)
    manager.get_low_stock_threshold.return_value = 10
    manager.get_expiry_warning_days.return_value = 30
    manager.set_low_stock_threshold.return_value = True
    manager.set_expiry_warning_days.return_value = True
    return manager


@pytest.fixture
def mock_settings_repository():
    """Create mock settings repository"""
    repo = Mock(spec=SettingsRepository)
    repo.get_int.side_effect = lambda key, default: {
        'low_stock_threshold': 10,
        'expiry_warning_days': 30
    }.get(key, default)
    repo.set_int.return_value = True
    return repo


class TestAlertCard:
    """Test AlertCard widget"""
    
    def test_alert_card_creation(self, app, sample_medicines):
        """Test alert card creation"""
        medicine = sample_medicines['low_stock']
        card = AlertCard(medicine, "low_stock")
        
        assert card.medicine == medicine
        assert card.alert_type == "low_stock"
        assert card.isVisible()
    
    def test_alert_card_styling_low_stock(self, app, sample_medicines):
        """Test alert card styling for low stock"""
        medicine = sample_medicines['low_stock']
        card = AlertCard(medicine, "low_stock")
        
        # Check that styling is applied (basic check)
        assert card.styleSheet() != ""
    
    def test_alert_card_styling_expired(self, app, sample_medicines):
        """Test alert card styling for expired medicine"""
        medicine = sample_medicines['expired']
        card = AlertCard(medicine, "expired")
        
        # Check that styling is applied
        assert card.styleSheet() != ""
    
    def test_alert_card_styling_expiring_soon(self, app, sample_medicines):
        """Test alert card styling for expiring soon medicine"""
        medicine = sample_medicines['expiring_soon']
        card = AlertCard(medicine, "expiring_soon")
        
        # Check that styling is applied
        assert card.styleSheet() != ""
    
    def test_alert_card_signals(self, app, sample_medicines):
        """Test alert card signal emissions"""
        medicine = sample_medicines['low_stock']
        card = AlertCard(medicine, "low_stock")
        
        # Test signal connections exist
        assert card.medicine_clicked is not None
        assert card.action_requested is not None
    
    def test_severity_text_generation(self, app, sample_medicines):
        """Test severity text generation"""
        low_stock_card = AlertCard(sample_medicines['low_stock'], "low_stock")
        expired_card = AlertCard(sample_medicines['expired'], "expired")
        expiring_card = AlertCard(sample_medicines['expiring_soon'], "expiring_soon")
        
        assert low_stock_card._get_severity_text() == "LOW"
        assert expired_card._get_severity_text() == "EXPIRED"
        assert expiring_card._get_severity_text() == "EXPIRING"


class TestAlertSection:
    """Test AlertSection widget"""
    
    def test_alert_section_creation(self, app):
        """Test alert section creation"""
        section = AlertSection("Test Alerts", "low_stock")
        
        assert section.title == "Test Alerts"
        assert section.alert_type == "low_stock"
        assert len(section.medicines) == 0
        assert len(section.cards) == 0
    
    def test_update_medicines_empty(self, app):
        """Test updating section with empty medicine list"""
        section = AlertSection("Test Alerts", "low_stock")
        section.update_medicines([])
        
        assert len(section.medicines) == 0
        assert len(section.cards) == 0
        assert section.empty_label.isVisible()
    
    def test_update_medicines_with_data(self, app, sample_medicines):
        """Test updating section with medicine data"""
        section = AlertSection("Low Stock Alerts", "low_stock")
        medicines = [sample_medicines['low_stock']]
        
        section.update_medicines(medicines)
        
        assert len(section.medicines) == 1
        assert len(section.cards) == 1
        assert section.medicines[0] == sample_medicines['low_stock']
    
    def test_toggle_section_expand_collapse(self, app):
        """Test section expand/collapse functionality"""
        section = AlertSection("Test Alerts", "low_stock")
        
        # Initially expanded
        assert section.toggle_button.isChecked()
        assert section.scroll_area.isVisible()
        
        # Collapse
        section.toggle_button.click()
        assert not section.toggle_button.isChecked()
        assert not section.scroll_area.isVisible()
        
        # Expand again
        section.toggle_button.click()
        assert section.toggle_button.isChecked()
        assert section.scroll_area.isVisible()
    
    def test_count_update(self, app, sample_medicines):
        """Test count badge update"""
        section = AlertSection("Test Alerts", "low_stock")
        
        # Initially zero
        assert section.count_label.text() == "0"
        
        # Add medicines
        medicines = [sample_medicines['low_stock'], sample_medicines['expired']]
        section.update_medicines(medicines)
        
        assert section.count_label.text() == "2"


class TestAlertThresholdDialog:
    """Test AlertThresholdDialog"""
    
    def test_dialog_creation(self, app, mock_settings_repository):
        """Test dialog creation"""
        dialog = AlertThresholdDialog(mock_settings_repository)
        
        assert dialog.windowTitle() == "Alert Threshold Settings"
        assert dialog.isModal()
        assert dialog.low_stock_spinbox.value() == 10
        assert dialog.expiry_days_spinbox.value() == 30
    
    def test_load_current_settings(self, app, mock_settings_repository):
        """Test loading current settings"""
        mock_settings_repository.get_int.side_effect = lambda key, default: {
            'low_stock_threshold': 15,
            'expiry_warning_days': 45
        }.get(key, default)
        
        dialog = AlertThresholdDialog(mock_settings_repository)
        
        assert dialog.low_stock_spinbox.value() == 15
        assert dialog.expiry_days_spinbox.value() == 45
    
    def test_save_settings(self, app, mock_settings_repository):
        """Test saving settings"""
        dialog = AlertThresholdDialog(mock_settings_repository)
        
        # Change values
        dialog.low_stock_spinbox.setValue(20)
        dialog.expiry_days_spinbox.setValue(60)
        
        # Save settings
        dialog._save_settings()
        
        # Verify settings were saved
        mock_settings_repository.set_int.assert_any_call(
            'low_stock_threshold', 20, 'Low stock alert threshold'
        )
        mock_settings_repository.set_int.assert_any_call(
            'expiry_warning_days', 60, 'Days before expiry to show warning'
        )
    
    def test_spinbox_ranges(self, app, mock_settings_repository):
        """Test spinbox value ranges"""
        dialog = AlertThresholdDialog(mock_settings_repository)
        
        # Low stock threshold range
        assert dialog.low_stock_spinbox.minimum() == 1
        assert dialog.low_stock_spinbox.maximum() == 1000
        
        # Expiry days range
        assert dialog.expiry_days_spinbox.minimum() == 1
        assert dialog.expiry_days_spinbox.maximum() == 365


class TestAlertSystemWidget:
    """Test AlertSystemWidget"""
    
    def test_alert_system_creation(self, app, mock_medicine_manager, mock_settings_repository):
        """Test alert system widget creation"""
        widget = AlertSystemWidget(mock_medicine_manager, mock_settings_repository)
        
        assert len(widget.sections) == 3
        assert 'expired' in widget.sections
        assert 'expiring_soon' in widget.sections
        assert 'low_stock' in widget.sections
    
    def test_refresh_alerts(self, app, mock_medicine_manager, mock_settings_repository, sample_medicines):
        """Test alert refresh functionality"""
        # Setup mock data
        mock_alerts = {
            'expired': [sample_medicines['expired']],
            'expiring_soon': [sample_medicines['expiring_soon']],
            'low_stock': [sample_medicines['low_stock']]
        }
        mock_medicine_manager.generate_stock_alerts.return_value = mock_alerts
        
        widget = AlertSystemWidget(mock_medicine_manager, mock_settings_repository)
        widget.refresh_alerts()
        
        # Verify manager methods were called
        mock_medicine_manager.set_low_stock_threshold.assert_called_with(10)
        mock_medicine_manager.set_expiry_warning_days.assert_called_with(30)
        mock_medicine_manager.generate_stock_alerts.assert_called()
        
        # Verify sections were updated
        assert len(widget.sections['expired'].medicines) == 1
        assert len(widget.sections['expiring_soon'].medicines) == 1
        assert len(widget.sections['low_stock'].medicines) == 1
    
    def test_get_alert_summary(self, app, mock_medicine_manager, mock_settings_repository, sample_medicines):
        """Test alert summary generation"""
        # Setup mock data
        mock_alerts = {
            'expired': [sample_medicines['expired']],
            'expiring_soon': [sample_medicines['expiring_soon']],
            'low_stock': [sample_medicines['low_stock']]
        }
        mock_medicine_manager.generate_stock_alerts.return_value = mock_alerts
        
        widget = AlertSystemWidget(mock_medicine_manager, mock_settings_repository)
        widget.refresh_alerts()
        
        summary = widget.get_alert_summary()
        
        assert summary['expired'] == 1
        assert summary['expiring_soon'] == 1
        assert summary['low_stock'] == 1
    
    def test_auto_refresh_toggle(self, app, mock_medicine_manager, mock_settings_repository):
        """Test auto-refresh enable/disable"""
        widget = AlertSystemWidget(mock_medicine_manager, mock_settings_repository)
        
        # Initially enabled (started in constructor)
        assert widget.refresh_timer.isActive()
        
        # Disable
        widget.set_auto_refresh_enabled(False)
        assert not widget.refresh_timer.isActive()
        
        # Enable
        widget.set_auto_refresh_enabled(True)
        assert widget.refresh_timer.isActive()
    
    def test_settings_dialog_integration(self, app, mock_medicine_manager, mock_settings_repository):
        """Test settings dialog integration"""
        widget = AlertSystemWidget(mock_medicine_manager, mock_settings_repository)
        
        # Test that settings button exists and is connected
        assert widget.settings_button is not None
        
        # Test signal connections
        assert widget.settings_changed is not None
    
    def test_action_handling(self, app, mock_medicine_manager, mock_settings_repository, sample_medicines):
        """Test action request handling"""
        widget = AlertSystemWidget(mock_medicine_manager, mock_settings_repository)
        medicine = sample_medicines['low_stock']
        
        # Test edit action
        with patch.object(widget.edit_requested, 'emit') as mock_emit:
            widget._handle_action_request("edit", medicine)
            mock_emit.assert_called_once_with(medicine)
        
        # Test restock action
        with patch.object(widget.restock_requested, 'emit') as mock_emit:
            widget._handle_action_request("restock", medicine)
            mock_emit.assert_called_once_with(medicine)
        
        # Test remove action
        with patch.object(widget.remove_requested, 'emit') as mock_emit:
            widget._handle_action_request("remove", medicine)
            mock_emit.assert_called_once_with(medicine)


class TestAlertIntegration:
    """Integration tests for alert system"""
    
    def test_alert_generation_flow(self, app, sample_medicines):
        """Test complete alert generation flow"""
        # Create mock managers
        medicine_manager = Mock(spec=MedicineManager)
        settings_repository = Mock(spec=SettingsRepository)
        
        # Setup mock responses
        settings_repository.get_int.side_effect = lambda key, default: {
            'low_stock_threshold': 10,
            'expiry_warning_days': 30
        }.get(key, default)
        
        medicine_manager.generate_stock_alerts.return_value = {
            'expired': [sample_medicines['expired']],
            'expiring_soon': [sample_medicines['expiring_soon']],
            'low_stock': [sample_medicines['low_stock']]
        }
        
        # Create widget and test flow
        widget = AlertSystemWidget(medicine_manager, settings_repository)
        widget.refresh_alerts()
        
        # Verify complete flow
        settings_repository.get_int.assert_called()
        medicine_manager.set_low_stock_threshold.assert_called_with(10)
        medicine_manager.set_expiry_warning_days.assert_called_with(30)
        medicine_manager.generate_stock_alerts.assert_called()
        
        # Verify UI updates
        summary = widget.get_alert_summary()
        assert summary['expired'] == 1
        assert summary['expiring_soon'] == 1
        assert summary['low_stock'] == 1
    
    def test_threshold_configuration_flow(self, app):
        """Test threshold configuration flow"""
        settings_repository = Mock(spec=SettingsRepository)
        settings_repository.get_int.return_value = 10
        settings_repository.set_int.return_value = True
        
        dialog = AlertThresholdDialog(settings_repository)
        
        # Change thresholds
        dialog.low_stock_spinbox.setValue(25)
        dialog.expiry_days_spinbox.setValue(45)
        
        # Save
        dialog._save_settings()
        
        # Verify settings were saved
        settings_repository.set_int.assert_any_call(
            'low_stock_threshold', 25, 'Low stock alert threshold'
        )
        settings_repository.set_int.assert_any_call(
            'expiry_warning_days', 45, 'Days before expiry to show warning'
        )


if __name__ == '__main__':
    pytest.main([__file__])