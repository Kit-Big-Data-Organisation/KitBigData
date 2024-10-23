"""
Module Dataloader

Ce module contient la classe `Dataloader`, qui permet de charger, lire et pré-traiter des
données à partir d'un fichier CSV.

Fonctionnalités :
- Lecture de fichiers CSV.
- Pré-traitement des données pour extraire l'année à partir de colonnes spécifiques.
- Chargement et préparation des données pour des analyses ou des visualisations ultérieures.

Classes :
---------
- Dataloader : Classe principale pour le chargement et le pré-traitement des données.

Modules utilisés :
------------------
- pandas : Manipulation des données sous forme de DataFrame.
- matplotlib.pyplot : Visualisation des données (non utilisé directement dans cette classe).
"""

import pandas as pd  # Manipulation des données sous forme de DataFrame
import matplotlib.pyplot as plt  # Visualisation (importé si nécessaire)

class Dataloader:
    """
    Classe Dataloader pour charger et pré-traiter des données à partir d'un fichier CSV.

    Attributs:
    ----------
    filename : str
        Le nom du fichier à charger (avec l'extension .csv).
    path : str
        Le chemin absolu vers le fichier spécifié.

    Méthodes :
    --------
    read() :
        Lit le fichier CSV et retourne un DataFrame.

    preprocess_data() :
        Applique un pré-traitement aux données, notamment l'extraction de l'année à partir
        des colonnes 'date' ou 'submitted' si elles existent.

    loader() :
        Fonction principale qui charge et pré-traite les données en appelant preprocess_data().
    """

    def __init__(self, filename):
        """
        Initialise le Dataloader avec le nom du fichier et définit le chemin absolu.

        Paramètres :
        ----------
        filename : str
            Le nom du fichier à charger (ex: 'data.csv').
        """
        self.filename = filename
        self.path = "/Users/ghalia/Desktop/Telecom IA/Kit Big Data/Projet/projet_KBD/KitBigData/Data/" + filename

    def read(self):
        """
        Lit le fichier CSV spécifié et retourne un DataFrame pandas.

        Retourne :
        --------
        pd.DataFrame
            Le DataFrame contenant les données du fichier CSV.
        """
        return pd.read_csv(self.path)

    def preprocess_data(self):
        """
        Pré-traite les données en ajoutant une colonne 'year' si une colonne 'date' ou 
        'submitted' existe.
        
        Si la colonne 'date' est présente, l'année est extraite des quatre premiers caractères.
        Si la colonne 'submitted' est présente, l'année est extraite de manière similaire.
        
        Retourne :
        --------
        pd.DataFrame
            Le DataFrame pré-traité avec une colonne 'year' ajoutée si applicable.
        """
        data = self.read()

        if 'date' in data.columns:
            data['year'] = data['date'].apply(lambda x: x[:4])

        if 'submitted' in data.columns:
            data['year'] = data['submitted'].apply(lambda x: int(x[:4]))

        return data

    def loader(self):
        """
        Charge et pré-traite les données en appelant la méthode preprocess_data().

        Retourne :
        --------
        pd.DataFrame
            Le DataFrame final prêt à être utilisé pour des analyses ou visualisations.
        """
        return self.preprocess_data()
