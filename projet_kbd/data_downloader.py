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
from logger_config import logger

def download_data(file_name, url, data_dir):
    """
    Download a file from a Google Drive link to a specified directory if it
    does not already exist.

    Parameters:
    ----------
    file_name : str
        The name of the file to download.
    url : str
        The Google Drive link to the file.
    data_dir : str
        The directory to save the downloaded file.

    Raises:
    -------
    Exception
        If the download fails.
    """
    # Ensure the data directory exists
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, file_name)
    if not os.path.exists(file_path):
        logger.info(f"Downloading {file_name} to {file_path}...")
        try:
            gdown.download(url, file_path, quiet=False)
            logger.info(f"{file_name} downloaded successfully to {file_path}.")
        except Exception as e:
            logger.error(f"Failed to download {file_name}: {e}")
            raise
    else:
        logger.info(f"{file_name} already exists in {file_path}. Skipping download.")