#!/usr/bin/env python3
"""
Test script to verify login fixes
Run this to test the login functionality
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from PySide6.QtWidgets import QApplication
from medical_store_app.ui.main_window import MainWindow

def setup_logging():
    """Set up logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main test function"""
    print("Testing Medical Store Management Application Login Fixes")
    print("=" * 60)
    
    # Set up logging
    setup_logging()
    
    # Create application
    app = QApplication(sys.argv)
    
    print("\nDefault Login Credentials:")
    print("Administrator:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nCashier:")
    print("  Username: cashier") 
    print("  Password: cashier123")
    print("\nTest Instructions:")
    print("1. Try logging in with admin credentials")
    print("2. Try logging in with cashier credentials")
    print("3. Try clicking 'Cancel' on login dialog (app should exit)")
    print("4. Try logging out (should return to login dialog)")
    print("5. Verify admin can access User Management")
    print("6. Verify cashier cannot access User Management")
    print("=" * 60)
    
    try:
        # Create main window (but don't show it yet)
        window = MainWindow()
        
        # Start the application with login process
        if window.start_application():
            # Login successful, show the main window
            window.show()
            
            # Run application
            sys.exit(app.exec())
        else:
            # Login cancelled or failed, exit application
            print("Login cancelled - Application exiting cleanly")
            return 0
        
    except Exception as e:
        print(f"Error running application: {e}")
        return 1

if __name__ == "__main__":
    main()