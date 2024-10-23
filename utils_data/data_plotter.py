"""
Module DataPlotter

Ce module fournit des outils pour visualiser les données analysées en utilisant
`pandas`, `matplotlib.pyplot`, et `plotly.express`. Il prend en entrée un objet
`DataAnalyzer` qui fournit les données agrégées pour chaque année. Les méthodes de 
ce module génèrent des graphiques interactifs pour visualiser les interactions 
et les recettes par année.

Modules utilisés :
------------------
- pandas : Manipulation des données sous forme de DataFrame.
- matplotlib.pyplot : Visualisation statique des données (non utilisé directement).
- plotly.express : Génération de graphiques interactifs pour les visualisations.

Classes :
---------
- DataPlotter : Classe qui permet de générer des visualisations interactives à partir
  des résultats d'un `DataAnalyzer`.

"""

import pandas as pd  # Manipulation des données sous forme de DataFrame
import matplotlib.pyplot as plt  # Visualisation statique (importé si nécessaire)
import plotly.express as px  # Visualisation interactive


class DataPlotter:
    """
    Classe DataPlotter pour visualiser les données analysées par un DataAnalyzer.

    Attributs :
    ----------
    data_analyzer : DataAnalyzer
        Un objet de type DataAnalyzer qui contient les méthodes pour extraire et
        regrouper les données par année.

    Méthodes :
    --------
    plot_nb_interactions_per_year() :
        Crée un graphique linéaire du nombre d'interactions par année.

    plot_nb_recipes_per_year() :
        Crée un graphique linéaire du nombre de recettes par année.
    """

    def __init__(self, data_analyzer):
        """
        Initialise le DataPlotter avec un objet DataAnalyzer.
        
        Paramètres :
        ----------
        data_analyzer : DataAnalyzer
            L'objet DataAnalyzer contenant les méthodes pour regrouper
            les données et effectuer les analyses nécessaires.
        """
        self.data_analyzer = data_analyzer

    def plot_nb_interactions_per_year(self):
        """
        Génère un graphique interactif montrant le nombre d'interactions par année.
        
        Utilise les méthodes de DataAnalyzer pour obtenir les valeurs
        des interactions par année et utilise Plotly Express pour
        générer un graphique linéaire interactif.
        
        Retourne :
        --------
        plotly.graph_objects.Figure
            Un graphique linéaire interactif avec les années sur l'axe des x
            et le nombre d'interactions sur l'axe des y.
        """
        x_values, y_values = self.data_analyzer.group_interactions_year()

        df = pd.DataFrame({
            'Year': x_values,
            'Interactions': y_values
        })
        fig = px.line(df, x='Year', y='Interactions', title='Number of Interactions per Year')
        return fig

    def plot_nb_recipes_per_year(self):
        """
        Génère un graphique interactif montrant le nombre de recettes par année.

        Utilise les méthodes de DataAnalyzer pour obtenir les valeurs
        des recettes par année et utilise Plotly Express pour
        générer un graphique linéaire interactif.

        Retourne :
        --------
        plotly.graph_objects.Figure
            Un graphique linéaire interactif avec les années sur l'axe des x
            et le nombre de recettes sur l'axe des y.
        """
        x_values, y_values = self.data_analyzer.group_interactions_year()

        df = pd.DataFrame({
            'Year': x_values,
            'Recipes': y_values
        })
        fig = px.line(df, x='Year', y='Recipes', title='Number of Recipes per Year')
        return fig
