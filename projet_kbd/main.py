"""
Main script for profiling and running the Streamlit application.

This script connects to a SQLite database, ensures all required data files are
downloaded, and runs the Streamlit app while profiling its performance using
the `cProfile` module.
"""

import os
import sqlalchemy
from data_downloader import download_data
from logger_config import logger
import streamlit_app

# Define base directory (KitBigData)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Paths to database and data files
DB_PATH = os.path.join(BASE_DIR, "projet_kbd", "database", "streamlit.db")
DATA_DIR = os.path.join(BASE_DIR, "Data")
RECIPES_FILE = "RAW_recipes.csv"
INTERACTIONS_FILE = "RAW_interactions.csv"

DATA_FILES = {
    "RAW_recipes.csv": (
        "https://drive.google.com/uc?id=1mrct6Jo7PjwHnFpNZ3JKc2g1dvGaeC0w",
        DATA_DIR,
    ),
    "RAW_interactions.csv": (
        "https://drive.google.com/uc?id=1ikGYx3h741P2JIkFwIclhciiIGeBWpTL",
        DATA_DIR,
    ),
    "streamlit.db": (
        "https://drive.google.com/uc?id=1LboRS888bE4EaKGRQosd_4LspGFOADs7",
        os.path.join(BASE_DIR, "projet_kbd", "database"),
    ),
}

# Create SQLAlchemy engine dynamically
engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")


def create_database_if_not_exists(db_path):
    """
    Creates the SQLite database file if it does not already exist.

    Args:
        db_path (str): The path to the SQLite database file.
    """
    if not os.path.exists(db_path):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create the database file
        engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
        engine.connect()  # This will create the database file
        logger.info(f"Database created at {db_path}.")
    else:
        logger.info(f"Database already exists at {db_path}.")


def validate_data_files(data_dir):
    """
    Ensures that the required data files exist after the download step.
    Raises an exception if any file is missing.

    Args:
        data_dir (str): The directory where the data files are expected to be
        located.
    """
    required_files = [RECIPES_FILE, INTERACTIONS_FILE]
    for file_name in required_files:
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required file not found: {file_path}")
        logger.info(f"File validated: {file_path}")


if __name__ == "__main__":
    try:
        # Ensure the database and data files are downloaded and validated
        for file_name, (url, dir) in DATA_FILES.items():
            download_data(file_name, url, dir)

        validate_data_files(DATA_DIR)

        logger.info("Starting the Streamlit application...")
        # Run the Streamlit app
        app = streamlit_app.run(
            DATA_DIR, RECIPES_FILE, INTERACTIONS_FILE, engine
        )

        logger.info("Streamlit application finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
