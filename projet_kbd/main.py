"""
Main script for profiling and running the Streamlit application.

This script connects to a SQLite database, ensures all required data files are
downloaded, and runs the Streamlit app while profiling its performance using
the `cProfile` module.
"""

import os
import cProfile
import sqlalchemy
from projet_kbd.data_downloader import download_data
from projet_kbd.logger_config import logger
import streamlit_app
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError


# Define base directory (KitBigData)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Paths to database and data files
DB_PATH = os.path.join(BASE_DIR, "projet_kbd", "database", "streamlit.db")
DATA_DIR = os.path.join(BASE_DIR, "Data")
RECIPES_FILE = "RAW_recipes.csv"
INTERACTIONS_FILE = "RAW_interactions.csv"

# Create SQLAlchemy engine dynamically
#engine = sqlalchemy.create_engine(f'sqlite:///{DB_PATH}')


def create_database_and_verify_table(db_path, table_name):
    """
    Ensures the SQLite database and a specific table exist. If the database
    or table does not exist, it creates them.

    Args:
        db_path (str): The path to the SQLite database file.
        table_name (str): The name of the table to verify or create.
    """
    try:
        # Assure-toi que le répertoire contenant le fichier existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Crée une connexion avec la base de données
        engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

        # Vérifie si le fichier de la base existe
        if not os.path.exists(db_path):
            engine.connect().close()
            print(f"✅ Database file successfully created at {db_path}")
        else:
            print(f"ℹ️ Database already exists at {db_path}")

        # Vérifie si la table existe
        inspector = inspect(engine)
        if table_name in inspector.get_table_names():
            print(f"✅ Table '{table_name}' already exists in the database.")
        else:
            print(f"ℹ️ Table '{table_name}' does not exist. Creating it now...")
            # Exemple de création de table
            with engine.connect() as conn:
                conn.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, test_col TEXT);")
            print(f"✅ Table '{table_name}' created successfully.")

    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error occurred while working with the database: {e}")
    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")


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
        create_database_and_verify_table(DB_PATH)

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
