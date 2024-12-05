"""
Main script for profiling and running the Streamlit application.

This script connects to a SQLite database, ensures all required data files are
downloaded, and runs the Streamlit app while profiling its performance using
the `cProfile` module.
"""

import os
import cProfile
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from streamlit_sqlalchemy import StreamlitAlchemyMixin
import streamlit as st
from projet_kbd.data_downloader import download_data
from projet_kbd.logger_config import logger
import streamlit_app
from sqlalchemy.engine import Engine

# Define base directory (KitBigData)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Paths to database and data files
DB_PATH = os.path.join(BASE_DIR, "projet_kbd", "database", "streamlit.db")
DATA_DIR = os.path.join(BASE_DIR, "Data")
RECIPES_FILE = "RAW_recipes.csv"
INTERACTIONS_FILE = "RAW_interactions.csv"


# Streamlit SQLAlchemy mixin class
class DatabaseManager(StreamlitAlchemyMixin):
    def __init__(self):
        self.engine = None  # Placeholder for the SQLAlchemy engine

    def attach_engine(self, engine):
        """Attach an SQLAlchemy engine to the manager."""
        self.engine = engine

    def get_engine(self):
        """Get the attached SQLAlchemy engine."""
        if not self.engine:
            raise ValueError("No engine attached to the DatabaseManager.")
        return self.engine


db_manager = DatabaseManager()


@st.cache_resource
def create_database_and_verify_table(db_path, table_name):
    """
    Ensures the SQLite database and a specific table exist. If the database
    or table does not exist, it creates them.

    Args:
        db_path (str): The path to the SQLite database file.
        table_name (str): The name of the table to verify or create.

    Returns:
        sqlalchemy.engine.Engine: The SQLAlchemy engine connected to the database.
    """
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        logger.info(f"Database path: {db_path}")

        # Create database engine
        engine = create_engine(f"sqlite:///{db_path}")
        logger.info("Database connection established.")

        # Check if the database file exists
        if not os.path.exists(db_path):
            engine.connect().close()
            logger.info(f"✅ Database file successfully created at {db_path}")
        else:
            logger.info(f"ℹ️ Database already exists at {db_path}")

        # Check if the table exists
        inspector = inspect(engine)
        if table_name in inspector.get_table_names():
            logger.info(f"✅ Table '{table_name}' already exists in the database.")
        else:
            logger.info(f"ℹ️ Table '{table_name}' does not exist. Creating it now...")
            create_table_query = text(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                test_col TEXT
            );
            """)
            with engine.connect() as conn:
                conn.execute(create_table_query)
            logger.info(f"✅ Table '{table_name}' created successfully.")
        # Close the engine connection
        engine.dispose()
        logger.info("Database connection closed.")
        return engine

    except SQLAlchemyError as e:
        logger.error(f"❌ SQLAlchemy error occurred while working with the database: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error occurred: {e}")
        raise


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
        # Ensure the database exists and get the engine
        engine = create_database_and_verify_table(DB_PATH, "test_table")
        
        if not isinstance(engine, Engine):
            raise ValueError("Le paramètre `_engine` n'est pas un objet SQLAlchemy Engine valide.")
        logger.info("Le paramètre `_engine` est un objet SQLAlchemy Engine valide.")
        # Attach the engine to the DatabaseManager
        db_manager.attach_engine(engine)

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
