"""
Data Downloader Module

This module handles the automated download of required dataset files from
Google Drive if they are not already present in the specified data directory.

The `DATA_FILES` dictionary maps filenames to their respective Google Drive
links.
The function `download_data` checks if each file exists in the provided
directory, and if not, downloads it using the `gdown` library.

Attributes:
    DATA_FILES (dict): A dictionary mapping filenames (str) to Google Drive
    links (str).

Functions:
    download_data(data_dir):
        Checks the existence of files specified in `DATA_FILES` and downloads
        missing files from the respective Google Drive links to the specified
        directory.
"""

import os
import gdown
from projet_kbd.logger_config import logger

DATA_FILES = {
    "RAW_recipes.csv": "https://drive.google.com/uc?id=1QyYM5oSH0Rpi91MLpYDfwb8rCvRPFqKR",
    "RAW_interactions.csv": "https://drive.google.com/uc?id=1xAIEvkIreWBI2uQ6-7w9scGnY_ksruy3",
}


def download_data(data_dir):
    """
    Downloads data files from Google Drive links if they are not already
    present in the specified directory.

    This function iterates over the `DATA_FILES` dictionary, checking if each
    file exists in the specified `data_dir`. If a file does not exist, it
    downloads the file from the corresponding Google Drive link using the
    `gdown` library and logs the process using the configured logger.

    Args:
        data_dir (str): The directory where the data files should be saved.

    Logs:
        - Logs a message when a file already exists.
        - Logs a message when a file is being downloaded.
        - Logs any errors encountered during the download process.

    Raises:
        Exception: If the file cannot be downloaded for any reason.

    Example:
        >>> download_data("/path/to/data")
        RAW_recipes.csv already exists. Skipping download.
        Downloading RAW_interactions.csv...
    """
    # Ensure the data directory exists
    os.makedirs(data_dir, exist_ok=True)

    for file_name, url in DATA_FILES.items():
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            logger.info(f"Downloading {file_name} to {file_path}...")
            try:
                gdown.download(url, file_path, quiet=False)
                logger.info(
                    f"{file_name} downloaded successfully to {file_path}."
                )
            except Exception as e:
                logger.error(f"Failed to download {file_name}: {e}")
                raise
        else:
            logger.info(
                f"{file_name} already exists in {file_path}.Skipping download."
            )
