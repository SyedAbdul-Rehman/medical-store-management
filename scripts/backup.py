#!/usr/bin/env python3
"""
Simple backup script for Medical Store Management System
Quick backup creation with timestamp
"""

import subprocess
import sys
from datetime import datetime


def create_quick_backup(description=""):
    """Create a quick backup with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if description:
        # Sanitize description
        safe_desc = "".join(c for c in description if c.isalnum() or c in '-_').lower()
        branch_name = f"backup_{timestamp}_{safe_desc}"
    else:
        branch_name = f"backup_{timestamp}"
    
    try:
        # Add all changes
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit changes
        commit_msg = f"Backup: {description}" if description else f"Backup {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Create backup branch
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        
        # Push backup branch
        subprocess.run(["git", "push", "origin", branch_name], check=True)
        
        # Return to main
        subprocess.run(["git", "checkout", "main"], check=True)
        
        print(f"✅ Quick backup created: {branch_name}")
        print(f"📝 Commit message: {commit_msg}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")


if __name__ == "__main__":
    description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    create_quick_backup(description)