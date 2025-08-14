#!/usr/bin/env python3
"""
Test script to verify login cancel behavior
This script tests that clicking Cancel on login dialog properly exits the application
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from PySide6.QtWidgets import QApplication
from medical_store_app.ui.main_window import MainWindow

def main():
    """Test the login cancel behavior"""
    print("Testing Login Cancel Behavior")
    print("=" * 40)
    print("Instructions:")
    print("1. The login dialog should appear")
    print("2. Click 'Cancel' button")
    print("3. The application should exit completely")
    print("4. No main window should be visible")
    print("=" * 40)
    
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Create application
    app = QApplication(sys.argv)
    
    try:
        # Create main window (but don't show it yet)
        main_window = MainWindow()
        
        # Start the application with login process
        if main_window.start_application():
            # Login successful, show the main window
            main_window.show()
            print("Login successful - Main window shown")
            
            # Start the application event loop
            return app.exec()
        else:
            # Login cancelled or failed, exit application
            print("Login cancelled - Application exiting")
            return 0
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())