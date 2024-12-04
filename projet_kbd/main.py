import os
import cProfile
from google.cloud import firestore
from projet_kbd.data_downloader import download_data
from projet_kbd.logger_config import logger
import streamlit_app

# Configuration des clés d'accès à Firebase Firestore
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/ghalia/Desktop/Telecom_IA/Projet KBD/KitBigData/credentials/projet-kbd-firebase-adminsdk-e9vub-2f01ddb3d9.json"

# Initialisation de Firestore
def get_firestore_db():
    engine = firestore.Client()
    return engine

# Define base directory (KitBigData)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "Data")
RECIPES_FILE = "RAW_recipes.csv"
INTERACTIONS_FILE = "RAW_interactions.csv"

def validate_data_files(data_dir):
    required_files = [RECIPES_FILE, INTERACTIONS_FILE]
    for file_name in required_files:
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required file not found: {file_path}")
        logger.info(f"File validated: {file_path}")

if __name__ == "__main__":
    try:
        # Assurer que les fichiers de données sont disponibles et validés
        download_data(DATA_DIR)
        validate_data_files(DATA_DIR)

        # Initialiser Firestore
        engine = get_firestore_db()

        # Initialiser et activer le profiler
        profiler = cProfile.Profile()
        profiler.enable()

        logger.info("Starting the Streamlit application with Firestore...")
        # Exécuter l'application Streamlit avec Firestore comme base de données
        app = streamlit_app.run(
            DATA_DIR, RECIPES_FILE, INTERACTIONS_FILE, engine
        )

        # Désactiver le profiler
        profiler.disable()
        logger.info("Streamlit application finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
