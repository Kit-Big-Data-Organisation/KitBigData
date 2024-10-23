"""
Module principal de l'application Streamlit pour le Projet Kit Big Data.

Ce fichier exécute l'application Streamlit en important la classe `StreamlitApp`
et en passant les fichiers de données (recettes et interactions) à l'application.
L'interface utilisateur est gérée avec `streamlit` pour afficher les visualisations
et analyser les données.

Fonctionnalités :
----------------
- Affiche le titre de l'application Streamlit.
- Charge et exécute les méthodes de l'application pour visualiser les données
  des fichiers CSV.
- L'application est déclenchée uniquement si le fichier est exécuté directement
  (`__main__`).

Modules utilisés :
------------------
- streamlit : Utilisé pour l'interface utilisateur de l'application.
- StreamlitApp : Classe personnalisée pour charger, analyser et visualiser
  les données des fichiers CSV.
"""

import streamlit as st
from streamlit_utils.streamlit_app import StreamlitApp

# Titre de la page
st.title("Projet Kit Big Data")

# Exécution des différentes parties de l'application
if __name__ == "__main__":

    app = StreamlitApp("RAW_recipes.csv", "RAW_interactions.csv")
    app.run()
