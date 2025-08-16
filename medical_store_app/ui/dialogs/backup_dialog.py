"""
Backup and Restore Dialog for Medical Store Management Application
Provides UI for database backup and restore operations
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal

from ...utils.backup import BackupManager
from ...config.database import DatabaseManager

class BackupWorker(QThread):
    """Worker thread for backup/restore operations"""
    finished = Signal(bool, str)

    def __init__(self, backup_manager, operation, path):
        super().__init__()
        self.backup_manager = backup_manager
        self.operation = operation
        self.path = path

    def run(self):
        if self.operation == "backup":
            success = self.backup_manager.backup_database(self.path)
            self.finished.emit(success, "Backup")
        elif self.operation == "restore":
            success = self.backup_manager.restore_database(self.path)
            self.finished.emit(success, "Restore")

class BackupDialog(QDialog):
    """Dialog for database backup and restore"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        db_manager = DatabaseManager()
        self.backup_manager = BackupManager(db_manager.db_path)
        
        self.setWindowTitle("Backup and Restore")
        self.setMinimumWidth(400)
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        description = QLabel(
            "Backup your database to a safe location or restore it from a previous backup."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        button_layout = QHBoxLayout()
        
        self.backup_button = QPushButton("Backup Database")
        self.backup_button.clicked.connect(self.backup_database)
        button_layout.addWidget(self.backup_button)
        
        self.restore_button = QPushButton("Restore Database")
        self.restore_button.clicked.connect(self.restore_database)
        button_layout.addWidget(self.restore_button)
        
        layout.addLayout(button_layout)

    def backup_database(self):
        """Handle backup database button click"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup", "", "SQLite Database (*.db)"
        )
        
        if file_path:
            self.run_operation("backup", file_path)

    def restore_database(self):
        """Handle restore database button click"""
        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            "Restoring the database will overwrite all current data. "
            "It is recommended to create a backup first.\n\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Backup", "", "SQLite Database (*.db)"
            )
            
            if file_path:
                self.run_operation("restore", file_path)

    def run_operation(self, operation, path):
        """Run backup/restore operation in a worker thread"""
        self.progress_dialog = QProgressDialog(
            f"{operation.capitalize()} in progress...", "Cancel", 0, 0, self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        
        self.worker = BackupWorker(self.backup_manager, operation, path)
        self.worker.finished.connect(self.on_operation_finished)
        self.progress_dialog.canceled.connect(self.worker.terminate)
        
        self.worker.start()
        self.progress_dialog.exec()

    def on_operation_finished(self, success, operation):
        """Handle finished signal from worker thread"""
        self.progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self, "Success", f"Database {operation.lower()} completed successfully."
            )
            if operation == "Restore":
                QMessageBox.information(
                    self, "Restart Required", "Please restart the application for the changes to take effect."
                )
                self.accept()
        else:
            QMessageBox.critical(
                self, "Error", f"Database {operation.lower()} failed. Check logs for details."
            )
