"""
Export Dialog for Medical Store Management Application
Provides file selection and export progress for reports
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFileDialog, QProgressBar, QTextEdit,
    QGroupBox, QCheckBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QIcon

from ..components.base_components import StyledButton
from ...utils.report_exporter import ReportExporter
from ...managers.report_manager import ReportData


class ExportThread(QThread):
    """Thread for exporting reports without blocking UI"""
    
    # Signals
    export_completed = Signal(bool, str)  # success, message
    progress_updated = Signal(int)  # progress percentage
    
    def __init__(self, exporter: ReportExporter, report_data, format_type: str, file_path: str):
        super().__init__()
        self.exporter = exporter
        self.report_data = report_data
        self.format_type = format_type
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run export in background thread"""
        try:
            self.progress_updated.emit(10)
            
            success = False
            if self.format_type == "csv":
                self.progress_updated.emit(30)
                if isinstance(self.report_data, ReportData):
                    success = self.exporter.export_to_csv(self.report_data, self.file_path)
                else:
                    success = self.exporter.export_inventory_to_csv(self.report_data, self.file_path)
                self.progress_updated.emit(90)
                
            elif self.format_type == "excel":
                self.progress_updated.emit(30)
                if isinstance(self.report_data, ReportData):
                    success = self.exporter.export_to_excel(self.report_data, self.file_path)
                else:
                    # For inventory reports, convert to CSV for now
                    csv_path = self.file_path.replace('.xlsx', '.csv')
                    success = self.exporter.export_inventory_to_csv(self.report_data, csv_path)
                self.progress_updated.emit(90)
                
            elif self.format_type == "pdf":
                self.progress_updated.emit(30)
                if isinstance(self.report_data, ReportData):
                    success = self.exporter.export_to_pdf(self.report_data, self.file_path)
                else:
                    # For inventory reports, convert to CSV for now
                    csv_path = self.file_path.replace('.pdf', '.csv')
                    success = self.exporter.export_inventory_to_csv(self.report_data, csv_path)
                self.progress_updated.emit(90)
            
            self.progress_updated.emit(100)
            
            if success:
                self.export_completed.emit(True, f"Report exported successfully to {self.file_path}")
            else:
                self.export_completed.emit(False, "Export failed. Please check the logs for details.")
                
        except Exception as e:
            self.logger.error(f"Error in export thread: {e}")
            self.export_completed.emit(False, f"Export error: {str(e)}")


class ExportDialog(QDialog):
    """Dialog for exporting reports to various formats"""
    
    def __init__(self, report_data, default_format: str = "csv", parent=None):
        super().__init__(parent)
        self.report_data = report_data
        self.default_format = default_format
        self.exporter = ReportExporter()
        self.export_thread = None
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._setup_connections()
        self._load_format_options()
        
        # Set default values
        self._set_default_filename()
    
    def _setup_ui(self):
        """Set up the export dialog UI"""
        self.setWindowTitle("Export Report")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.resize(600, 450)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Export Report")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Export options group
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(12)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.setMinimumWidth(150)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # File path selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Save to:"))
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)
        
        self.browse_btn = StyledButton("Browse...", button_type="outline")
        file_layout.addWidget(self.browse_btn)
        options_layout.addLayout(file_layout)
        
        # Export options checkboxes
        self.include_summary_cb = QCheckBox("Include Summary")
        self.include_summary_cb.setChecked(True)
        options_layout.addWidget(self.include_summary_cb)
        
        self.include_daily_cb = QCheckBox("Include Daily Breakdown")
        self.include_daily_cb.setChecked(True)
        options_layout.addWidget(self.include_daily_cb)
        
        self.include_medicines_cb = QCheckBox("Include Top Medicines")
        self.include_medicines_cb.setChecked(True)
        options_layout.addWidget(self.include_medicines_cb)
        
        layout.addWidget(options_group)
        
        # Format info
        self.format_info_label = QLabel()
        self.format_info_label.setWordWrap(True)
        self.format_info_label.setStyleSheet("color: #666666; font-size: 11px; padding: 8px;")
        layout.addWidget(self.format_info_label)
        
        # Progress section (initially hidden)
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_label = QLabel("Exporting...")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_frame.setVisible(False)
        layout.addWidget(self.progress_frame)
        
        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = StyledButton("Cancel", button_type="outline")
        button_layout.addWidget(self.cancel_btn)
        
        self.export_btn = StyledButton("Export", button_type="primary")
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        # Apply styling
        self._apply_styling()
    
    def _setup_connections(self):
        """Set up signal connections"""
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        self.browse_btn.clicked.connect(self._browse_file)
        self.export_btn.clicked.connect(self._start_export)
        self.cancel_btn.clicked.connect(self._cancel_export)
    
    def _load_format_options(self):
        """Load available export format options"""
        formats = [
            ("CSV", "csv", "Comma-separated values file. Compatible with Excel and other spreadsheet applications."),
            ("Excel", "excel", "Microsoft Excel workbook with multiple sheets for different data sections."),
            ("PDF", "pdf", "Portable Document Format with formatted tables and professional layout.")
        ]
        
        for display_name, format_code, description in formats:
            if self.exporter.is_format_supported(format_code):
                self.format_combo.addItem(display_name, format_code)
            else:
                # Add disabled item with requirements info
                requirements = self.exporter.get_format_requirements(format_code)
                disabled_text = f"{display_name} (Not Available)"
                self.format_combo.addItem(disabled_text, None)
                # Disable the item
                model = self.format_combo.model()
                item = model.item(self.format_combo.count() - 1)
                item.setEnabled(False)
                item.setToolTip(requirements)
        
        # Set default format
        for i in range(self.format_combo.count()):
            if self.format_combo.itemData(i) == self.default_format:
                self.format_combo.setCurrentIndex(i)
                break
    
    def _on_format_changed(self):
        """Handle format selection change"""
        format_code = self.format_combo.currentData()
        if format_code:
            # Update format info
            format_descriptions = {
                "csv": "CSV format is widely compatible and can be opened in Excel, Google Sheets, and other applications. Best for data analysis and further processing.",
                "excel": "Excel format provides multiple worksheets with formatted data. Ideal for detailed analysis and professional presentation.",
                "pdf": "PDF format creates a professional report with formatted tables and charts. Perfect for sharing and printing."
            }
            
            self.format_info_label.setText(format_descriptions.get(format_code, ""))
            
            # Update default filename
            self._set_default_filename()
    
    def _set_default_filename(self):
        """Set default filename based on format and report data"""
        format_code = self.format_combo.currentData()
        if not format_code:
            return
        
        # Generate filename based on report data
        if isinstance(self.report_data, ReportData):
            base_name = f"sales_report_{self.report_data.period_start}_to_{self.report_data.period_end}"
        else:
            base_name = f"inventory_report_{datetime.now().strftime('%Y-%m-%d')}"
        
        # Add extension
        extensions = {"csv": ".csv", "excel": ".xlsx", "pdf": ".pdf"}
        filename = base_name + extensions.get(format_code, ".csv")
        
        # Set default path (user's Documents folder)
        try:
            from pathlib import Path
            documents_path = Path.home() / "Documents"
            default_path = documents_path / filename
            self.file_path_edit.setText(str(default_path))
        except Exception:
            self.file_path_edit.setText(filename)
    
    def _browse_file(self):
        """Open file browser to select save location"""
        format_code = self.format_combo.currentData()
        if not format_code:
            return
        
        # File dialog filters
        filters = {
            "csv": "CSV Files (*.csv);;All Files (*)",
            "excel": "Excel Files (*.xlsx);;All Files (*)",
            "pdf": "PDF Files (*.pdf);;All Files (*)"
        }
        
        file_filter = filters.get(format_code, "All Files (*)")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report As",
            self.file_path_edit.text(),
            file_filter
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def _start_export(self):
        """Start the export process"""
        format_code = self.format_combo.currentData()
        file_path = self.file_path_edit.text().strip()
        
        if not format_code:
            QMessageBox.warning(self, "Invalid Format", "Please select a valid export format.")
            return
        
        if not file_path:
            QMessageBox.warning(self, "No File Selected", "Please select a file location to save the report.")
            return
        
        # Validate file path
        try:
            path_obj = Path(file_path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Invalid Path", f"Cannot create file at specified location:\n{str(e)}")
            return
        
        # Check if file exists
        if Path(file_path).exists():
            reply = QMessageBox.question(
                self, "File Exists", 
                f"The file '{Path(file_path).name}' already exists. Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Start export
        self._show_progress(True)
        self.export_btn.setEnabled(False)
        
        # Start export thread
        self.export_thread = ExportThread(self.exporter, self.report_data, format_code, file_path)
        self.export_thread.export_completed.connect(self._on_export_completed)
        self.export_thread.progress_updated.connect(self.progress_bar.setValue)
        self.export_thread.finished.connect(self._on_export_finished)
        self.export_thread.start()
    
    def _show_progress(self, show: bool):
        """Show or hide progress indicators"""
        self.progress_frame.setVisible(show)
        self.status_text.setVisible(show)
        
        if show:
            self.progress_bar.setValue(0)
            self.status_text.clear()
    
    def _on_export_completed(self, success: bool, message: str):
        """Handle export completion"""
        self.status_text.append(message)
        
        if success:
            self.status_text.append("Export completed successfully!")
            QMessageBox.information(self, "Export Complete", message)
            self.accept()  # Close dialog
        else:
            self.status_text.append("Export failed!")
            QMessageBox.critical(self, "Export Failed", message)
    
    def _on_export_finished(self):
        """Handle export thread completion"""
        self.export_btn.setEnabled(True)
        
        if self.export_thread:
            self.export_thread.deleteLater()
            self.export_thread = None
    
    def _cancel_export(self):
        """Cancel export operation"""
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.terminate()
            self.export_thread.wait()
        
        self.reject()  # Close dialog
    
    def _apply_styling(self):
        """Apply dialog styling"""
        dialog_style = """
            QDialog {
                background-color: #F8F9FA;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E1E5E9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #F8F9FA;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #E1E5E9;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2D9CDB;
                border-radius: 3px;
                background-color: #2D9CDB;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QTextEdit {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
            QProgressBar {
                border: 1px solid #E1E5E9;
                border-radius: 4px;
                text-align: center;
                background-color: #F8F9FA;
            }
            QProgressBar::chunk {
                background-color: #2D9CDB;
                border-radius: 3px;
            }
        """
        self.setStyleSheet(dialog_style)