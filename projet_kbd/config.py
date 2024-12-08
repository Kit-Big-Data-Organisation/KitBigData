import os

# Define base directory (KitBigData)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Paths to database and data files
DB_PATH = os.path.join(BASE_DIR, "projet_kbd", "database", "streamlit.db")
DATA_DIR = os.path.join(BASE_DIR, "Data")
RECIPES_FILE = "RAW_recipes.csv"
INTERACTIONS_FILE = "RAW_interactions.csv"
