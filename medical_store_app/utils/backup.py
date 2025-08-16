"""
Backup and Restore Utilities for Medical Store Management Application
Handles database backup and restore operations
"""

import logging
import shutil
import sqlite3
from pathlib import Path
from typing import Optional

class BackupManager:
    """Manages database backup and restore operations"""

    def __init__(self, db_path: str):
        """
        Initialize BackupManager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)

    def backup_database(self, destination_path: str) -> bool:
        """
        Create a backup of the database file
        
        Args:
            destination_path: Path to save the backup file
            
        Returns:
            True if backup is successful, False otherwise
        """
        try:
            if not self.db_path.exists():
                self.logger.error(f"Database file not found at {self.db_path}")
                return False
            
            destination = Path(destination_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(self.db_path, destination)
            self.logger.info(f"Database backup created successfully at {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create database backup: {e}")
            return False

    def restore_database(self, source_path: str) -> bool:
        """
        Restore the database from a backup file
        
        Args:
            source_path: Path to the backup file
            
        Returns:
            True if restore is successful, False otherwise
        """
        try:
            source = Path(source_path)
            if not source.exists():
                self.logger.error(f"Backup file not found at {source}")
                return False
            
            # Validate the backup file
            if not self._is_valid_database(source):
                self.logger.error(f"Invalid backup file: {source}")
                return False
            
            # Close existing connection if any before replacing the file
            # This should be handled by the application logic before calling restore
            
            shutil.copy2(source, self.db_path)
            self.logger.info(f"Database restored successfully from {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore database: {e}")
            return False

    def _is_valid_database(self, file_path: Path) -> bool:
        """
        Check if a file is a valid SQLite database
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is a valid SQLite database, False otherwise
        """
        try:
            conn = sqlite3.connect(file_path)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            conn.close()
            return True
        except sqlite3.DatabaseError:
            return False
