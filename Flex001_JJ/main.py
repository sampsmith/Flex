
import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from gui.main_window import ParallelDetectorGUI
from utils.logger import setup_logger
from config.settings import Settings

import logging

def main():
    """Main application entry point."""
    try:
        app = QApplication(sys.argv)
        
        settings = Settings()
        logger = setup_logger(settings.log_dir, settings.log_level)
        
        logger.info("Starting Flex001 application")
        
        window = ParallelDetectorGUI()
        window.show()
        
        logger.info("Flex001 application started successfully")
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        if 'app' in locals():
            QMessageBox.critical(None, "Startup Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 