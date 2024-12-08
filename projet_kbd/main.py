"""
Main script for profiling and running the Streamlit application.

This script connects to a SQLite database, ensures all required data files are
downloaded, and runs the Streamlit app while profiling its performance using
the `cProfile` module.
"""

import os
import cProfile
import sqlalchemy
from data_downloader import download_data
from logger_config import logger
import streamlit_app
from config import DB_PATH , DATA_DIR , RECIPES_FILE , INTERACTIONS_FILE


# Create SQLAlchemy engine dynamically
engine = sqlalchemy.create_engine(f'sqlite:///{DB_PATH}')


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
        # Ensure the database exists
        create_database_if_not_exists(DB_PATH)

        # Ensure data files are available and validated
        download_data(DATA_DIR)
        validate_data_files(DATA_DIR)

        # Initialize and enable the profiler
        profiler = cProfile.Profile()
        profiler.enable()

        logger.info("Starting the Streamlit application...")
        # Run the Streamlit app
        app = streamlit_app.run(
            DATA_DIR, RECIPES_FILE, INTERACTIONS_FILE, engine
        )

        # Disable the profiler
        profiler.disable()
        logger.info("Streamlit application finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
