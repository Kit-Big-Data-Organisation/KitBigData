import os
import cProfile
from google.cloud import firestore
from projet_kbd.data_downloader import download_data
from projet_kbd.logger_config import logger
import streamlit_app
import json 

# Recréer le JSON Firebase à partir des secrets
firebase_credentials = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
}
# Sauvegarder les informations dans un fichier temporaire si nécessaire
with open("firebase_credentials.json", "w") as f:
    json.dump(firebase_credentials, f)

# Initialiser Firestore
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firebase_credentials.json"

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
