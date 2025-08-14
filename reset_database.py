#!/usr/bin/env python3
"""
Script to reset the database for testing
This will delete the existing database and recreate it with default users
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from medical_store_app.config.database import DatabaseManager

def main():
    """Reset the database"""
    print("Resetting Medical Store Management Database...")
    
    try:
        # Get database path
        app_dir = Path(__file__).parent / "medical_store_app"
        data_dir = app_dir / "data"
        db_path = data_dir / "medical_store.db"
        
        # Remove existing database if it exists
        if db_path.exists():
            db_path.unlink()
            print(f"Removed existing database: {db_path}")
        
        # Create new database manager (this will create tables and default users)
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        print("Database reset successfully!")
        print("\nDefault users created:")
        print("  Admin - username: admin, password: admin123")
        print("  Cashier - username: cashier, password: cashier123")
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())