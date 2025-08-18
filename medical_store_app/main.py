#!/usr/bin/env python3
"""
Medical Store Management Application
Main entry point for the PySide6 desktop application
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from medical_store_app.config.database import DatabaseManager
from medical_store_app.config.settings import AppSettings
from medical_store_app.ui.main_window import MainWindow


def setup_logging():
    """Configure application logging"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "medical_store.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main application entry point"""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create QApplication instance
        app = QApplication(sys.argv)
        app.setApplicationName("Medical Store Management")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Medical Store Solutions")
        
        # Set application icon
        icon_path = project_root / "medical_store_app" / "resources" / "icon.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Set application properties for high DPI displays
        # Note: These attributes are deprecated in Qt 6 as high DPI is enabled by default
        # Only set them if they exist and we're not using Qt 6
        try:
            from PySide6 import __version__ as pyside_version
            major_version = int(pyside_version.split('.')[0])
            
            if major_version < 6:
                if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
                if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        except (ImportError, ValueError, AttributeError):
            # Fallback for older versions or if version detection fails
            pass
        
        # Initialize database
        logger.info("Initializing database...")
        db_manager = DatabaseManager()
        if not db_manager.initialize():
            logger.error("Failed to initialize database")
            return 1
        
        # Initialize application settings
        logger.info("Loading application settings...")
        settings = AppSettings()
        
        # Create main window (but don't show it yet)
        logger.info("Creating main application window...")
        main_window = MainWindow()
        
        # Start the application with login process
        logger.info("Starting login process...")
        if main_window.start_application():
            # Login successful, show the main window
            main_window.show()
            logger.info("Medical Store Management Application started successfully")
            
            # Start the application event loop
            return app.exec()
        else:
            # Login cancelled or failed, exit application
            logger.info("Application startup cancelled by user")
            return 0
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
