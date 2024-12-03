"""
Logging configuration module for the project.

This module sets up the basic logging configuration for the application,
allowing logs to be displayed in the console and saved to a file. It creates
a logger that can be imported and used by other modules in the project.

Log messages are formatted with timestamps, log levels, and messages.
"""
import logging

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            "recipe_analysis.log"
        ),  
    ],
)

logger = logging.getLogger(__name__)
