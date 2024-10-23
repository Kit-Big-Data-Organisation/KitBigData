"""
Module DataAnalyzer

Ce module fournit des outils pour analyser des données de type DataFrame,
notamment pour regrouper des interactions ou des recettes par année.
Il permet de compter le nombre d'interactions ou de recettes par année
et retourne les années ainsi que les valeurs correspondantes.

Modules utilisés :
------------------
- pandas : Utilisé pour manipuler les données sous forme de DataFrame et
  effectuer des opérations de regroupement et d'agrégation.

Classes :
---------
- DataAnalyzer : Classe principale pour analyser les données et regrouper
  les interactions ou recettes par année.
"""

# import pandas as pd  # Manipulation des données sous forme de DataFrame


class DataAnalyzer:
    """
    Classe DataAnalyzer pour analyser les données en les regroupant par année.

    Attributs :
    ----------
    data : pd.DataFrame
        Un DataFrame contenant les données à analyser, avec des colonnes comme 'user_id'
        ou 'id' et 'year'.

    Méthodes :
    --------
    group_interactions_year() :
        Regroupe les données par année et compte soit le nombre d'interactions
        (basé sur 'user_id') soit le nombre de recettes (basé sur 'id').
    """

    def __init__(self, data):
        """
        Initialise la classe DataAnalyzer avec un DataFrame.

        Paramètres :
        ----------
        data : pd.DataFrame
            Le DataFrame contenant les données à analyser.
        """
        self.data = data

    def group_interactions_year(self):
        """
        Regroupe les données par année et compte les interactions ou recettes.

        Cette méthode vérifie si la colonne 'user_id' est présente dans le DataFrame
        pour compter les interactions par année. Si la colonne 'id' est présente,
        elle comptera les recettes par année. Les années et les valeurs correspondantes
        sont ensuite retournées.

        Retourne :
        --------
        tuple (indices, values) :
            indices : pd.Index
                Les années correspondant aux regroupements.
            values : np.ndarray
                Le nombre d'interactions ou de recettes par année.

        Remarque :
        --------
        - Si les deux colonnes 'user_id' et 'id' existent, seule la dernière
          (recettes) sera utilisée.
        """
        indices, values = None, None  # Initialisation des variables

        if "user_id" in self.data.columns:
            grouped_interactions = self.data.groupby("year")["user_id"].count()
            indices, values = (
                grouped_interactions.index,
                grouped_interactions.values,
            )

        if "id" in self.data.columns:
            grouped_recipes = self.data.groupby("year")["id"].count()
            indices, values = grouped_recipes.index, grouped_recipes.values

        return indices, values
