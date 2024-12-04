"""
Logging configuration module for the project.

This module sets up the logging configuration for the application,
allowing logs to be displayed in the console and saved to a rotating log file.
The log file rotates when it reaches a specified size, and a fixed number of
backup log files are kept to manage disk usage efficiently.

Log messages are formatted with timestamps, log levels, and messages.
"""

import logging
from logging.handlers import RotatingFileHandler

# Log file path and configuration for rotation
log_file = "recipe_analysis.log"
max_file_size = 5 * 1024 * 1024  # Maximum size per log file: 5 MB
backup_count = 3  # Number of backup log files to keep

# Create a rotating file handler
rotating_handler = RotatingFileHandler(
    log_file, maxBytes=max_file_size, backupCount=backup_count
)

# Set up the logging configuration
logging.basicConfig(
    level=logging.INFO,  # Minimum log level to display
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    handlers=[
        logging.StreamHandler(),  # Display logs in the console
        rotating_handler,  # Save logs to a rotating file
    ],
)

# Create a logger instance
logger = logging.getLogger(__name__)
