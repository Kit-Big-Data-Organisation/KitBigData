"""
Module Streamlit simple pour tester les fonctionnalités de base de Streamlit.

Ce module affiche un titre, un graphique interactif basé sur des données
aléatoires,
et permet à l'utilisateur d'entrer son nom pour afficher un message
personnalisé.
"""

import numpy as np
import pandas as pd
import streamlit as st

# Titre de la page
st.title("Projet Kit Big Data")

# Texte introductif
st.write(
    """
Ceci est un exemple simple pour tester Streamlit.
Nous allons afficher un graphique ci-dessous :
"""
)


# Générer des données aléatoires
def generate_random_data():
    """
    Génère un DataFrame avec des données aléatoires.

    Le DataFrame contient 50 lignes et 3 colonnes nommées 'Colonne A',
    'Colonne B','Colonne C'.
    Les valeurs sont générées aléatoirement à partir d'une distribution
    normale.

    Returns:
        pd.DataFrame: Un DataFrame avec les données générées aléatoirement.
    """
    return pd.DataFrame(
        np.random.randn(50, 3), columns=["Colonne A", "Colonne B", "Colonne C"]
    )


# Afficher un graphique interactif avec Streamlit
def display_chart(d):
    """
    Affiche un graphique interactif avec Streamlit.

    Le graphique est une ligne représentant les données du DataFrame.

    Args:
        data (pd.DataFrame): Les données à afficher dans le graphique.
    """
    st.line_chart(d)


# Ajouter une interaction utilisateur simple
def get_user_input():
    """
    Affiche une boîte de saisie pour demander le nom de l'utilisateur.

    Si l'utilisateur entre un nom, un message personnalisé lui est affiché.

    Returns:
        str: Le nom de l'utilisateur si fourni, sinon une chaîne vide.
    """
    nom = st.text_input("Quel est ton nom ?")
    if nom:
        st.write(f"Bonjour, {nom} !")
    return nom


# Exécution des différentes parties de l'application
if __name__ == "__main__":
    # Générer et afficher les données
    data = generate_random_data()
    display_chart(data)
    # Interaction avec l'utilisateur
    get_user_input()
