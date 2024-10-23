"""
Module StreamlitApp

Ce module contient une application Streamlit permettant de charger, analyser
et visualiser des données relatives aux recettes et aux interactions. Il utilise
des classes définies dans d'autres modules, comme `DataAnalyzer` pour l'analyse
et `DataPlotter` pour la visualisation. Les données sont chargées à partir de
fichiers externes via la classe `Dataloader`.

Modules utilisés :
------------------
- data_analyzer : Contient la classe `DataAnalyzer` pour analyser les données.
- data_plotter : Contient la classe `DataPlotter` pour visualiser les données.
- streamlit : Utilisé pour construire l'interface utilisateur de l'application.
- data_loader : Contient la classe `Dataloader` pour charger les données.

Classes :
---------
- StreamlitApp : Classe principale pour gérer le chargement des données,
  l'analyse, et la création de visualisations dans une application Streamlit.
"""

import streamlit_utils as st
from utils_data.data_analyzer import DataAnalyzer
from utils_data.data_plotter import DataPlotter
from utils_data.data_loader import Dataloader


class StreamlitApp:
    """
    Classe StreamlitApp pour gérer l'application de visualisation Streamlit.

    Attributs :
    ----------
    recipe_file : str
        Le chemin vers le fichier contenant les données sur les recettes.
    interaction_file : str
        Le chemin vers le fichier contenant les données sur les interactions.

    Méthodes :
    --------
    load_and_analyze_data(filename) :
        Charge et analyse les données à partir d'un fichier CSV donné.

    create_plots() :
        Crée des graphiques pour les recettes et les interactions par année.

    run() :
        Lance l'application Streamlit et affiche les visualisations.
    """

    def __init__(self, recipe_file, interaction_file):
        """
        Initialise l'application Streamlit avec les chemins des fichiers
        de recettes et d'interactions.

        Paramètres :
        ----------
        recipe_file : str
            Le chemin vers le fichier des recettes.
        interaction_file : str
            Le chemin vers le fichier des interactions.
        """
        self.recipe_file = recipe_file
        self.interaction_file = interaction_file

    def load_and_analyze_data(self, filename):
        """
        Charge et analyse les données à partir d'un fichier donné.

        Cette méthode utilise la classe `Dataloader` pour charger les
        données, puis la classe `DataAnalyzer` pour effectuer l'analyse
        sur les données chargées.

        Paramètres :
        ----------
        filename : str
            Le chemin vers le fichier de données à charger.

        Retourne :
        --------
        DataAnalyzer :
            Un objet `DataAnalyzer` contenant les données analysées.
        """
        loader = Dataloader(filename)
        data = loader.loader()
        analyzer = DataAnalyzer(data)
        return analyzer

    def create_plots(self):
        """
        Crée des graphiques pour les recettes et les interactions par année.

        Cette méthode génère deux visualisations interactives : une pour
        le nombre de recettes par année et une pour le nombre d'interactions
        par année. Les données sont chargées et analysées via `DataAnalyzer`,
        et les graphiques sont créés via `DataPlotter`.

        Retourne :
        --------
        tuple (recipe_fig, interaction_fig) :
            recipe_fig : plotly.graph_objects.Figure
                Un graphique interactif des recettes par année.
            interaction_fig : plotly.graph_objects.Figure
                Un graphique interactif des interactions par année.
        """
        # Création du graphique pour les recettes
        recipe_analyzer = self.load_and_analyze_data(self.recipe_file)
        recipe_plot = DataPlotter(recipe_analyzer)
        recipe_fig = recipe_plot.plot_nb_recipes_per_year()

        # Création du graphique pour les interactions
        interaction_analyzer = self.load_and_analyze_data(self.interaction_file)
        interaction_plot = DataPlotter(interaction_analyzer)
        interaction_fig = interaction_plot.plot_nb_interactions_per_year()

        return recipe_fig, interaction_fig

    def run(self):
        """
        Lance l'application Streamlit et affiche les graphiques.

        Cette méthode affiche les graphiques interactifs pour les données
        de recettes et d'interactions directement dans l'application Streamlit.
        Elle appelle `create_plots()` pour générer les visualisations.
        """
        recipe_fig, interaction_fig = self.create_plots()

        st.write("## Recipe Data")
        st.plotly_chart(recipe_fig)

        st.write("## Interaction Data")
        st.plotly_chart(interaction_fig)
