"""
Main script for profiling and running the Streamlit application.

This script connects to a SQLite database and runs the Streamlit app while
profiling
its performance using the `cProfile` module. It uses SQLAlchemy to manage the database
connection and imports the Streamlit application logic from `streamlit_app`.
"""

import cProfile
import sqlalchemy
import streamlit_app

engine = sqlalchemy.create_engine('sqlite:////Users/ghalia/Desktop/Telecom_IA/Projet KBD/KitBigData/projet_kbd/database/streamlit.db')
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    app = streamlit_app.run('/Users/ghalia/Desktop/Telecom_rm -rf docsIA/Projet KBD/KitBigData/Data', 'RAW_recipes.csv', 'RAW_interactions.csv', engine)
    profiler.disable()
