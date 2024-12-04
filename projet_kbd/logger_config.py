import logging

# Configuration de base du logger
logging.basicConfig(
    level=logging.INFO,  # Niveau minimum des messages à afficher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format du message
    handlers=[
        logging.StreamHandler(),  # Affichage dans la console
        logging.FileHandler(
            "recipe_analysis.log"
        ),  # Enregistrement dans un fichier
    ],
)

# Création d'un logger que les autres modules peuvent importer
logger = logging.getLogger(__name__)
"""
Logger configured for the application.

This logger is configured to display messages in the console and save them in
the file "log/recipe_analysis.log". The messages include the timestamp, log
level, and message.

Usage:
    from logger_config import logger

    logger.info("Information message")
    logger.warning("Warning message")
    logger.error("Error message")
"""
