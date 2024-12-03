import logging

# Configuration de base du logger
logging.basicConfig(
    level=logging.INFO,  # Niveau minimum des messages à afficher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format du message
    handlers=[
        logging.StreamHandler(),  # Affichage dans la console
        logging.FileHandler("recipe_analysis.log"),  # Enregistrement dans un fichier
    ],
)

# Création d'un logger que les autres modules peuvent importer
logger = logging.getLogger(__name__)
"""
Logger configuré pour l'application.

Ce logger est configuré pour afficher les messages dans la console et les enregistrer dans le fichier
"log/recipe_analysis.log". Les messages incluent le timestamp, le niveau de log et le message.

Usage:
    from logger_config import logger

    logger.info("Message d'information")
    logger.warning("Message d'avertissement")
    logger.error("Message d'erreur")
"""
