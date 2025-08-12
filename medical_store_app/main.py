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
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.database import DatabaseManager
from config.settings import AppSettings
from ui.main_window import MainWindow


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
        
        # Set application properties for high DPI displays
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Initialize database
        logger.info("Initializing database...")
        db_manager = DatabaseManager()
        if not db_manager.initialize():
            logger.error("Failed to initialize database")
            return 1
        
        # Initialize application settings
        logger.info("Loading application settings...")
        settings = AppSettings()
        
        # Create and show main window
        logger.info("Starting main application window...")
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Medical Store Management Application started successfully")
        
        # Start the application event loop
        return app.exec()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())