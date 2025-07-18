

import os
import logging
from datetime import datetime

def setup_logger(log_dir="logs", log_level="ERROR"):
    """
    Set up logging configuration for the application.
    
    Args:
        log_dir (str): Directory to store log files
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log filename with timestamp
    log_file = os.path.join(log_dir, f"camera_operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    #logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    
    return logger 