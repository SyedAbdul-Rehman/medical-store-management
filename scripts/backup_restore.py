#!/usr/bin/env python3
"""
Backup and Restore Script for Medical Store Management System
Provides easy backup creation and restoration to any development step
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

class BackupRestoreManager:
    """Manages backup and restore operations for the project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_config_file = self.project_root / "scripts" / "backup_config.json"
        self.restore_points = self.load_restore_points()
    
    def load_restore_points(self):
        """Load predefined restore points"""
        return {
            "foundation": {
                "commit": "732fa9a",
                "description": "Complete foundation with core components",
                "date": "2025-01-13",
                "features": [
                    "Database models and repositories",
                    "Business logic managers", 
                    "Main window with sidebar",
                    "Reusable UI components",
             