from data_loader import Dataloader
from data_analyzer import DataAnalyzer
from streamlit_app import StreamlitApp
from data_plotter import DataPlotter
import streamlit as st


# Titre de la page
st.title("Projet Kit Big Data")

# Exécution des différentes parties de l'application
if __name__ == "__main__":

    app = StreamlitApp("RAW_recipes.csv" , "RAW_interactions.csv")
    app.run()