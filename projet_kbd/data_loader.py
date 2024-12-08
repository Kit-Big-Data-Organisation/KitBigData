"""
DataLoader Module
=================

This module provides functionality for loading, preprocessing, and enhancing
recipe data. It includes methods for merging datasets, adding derived features
(such as year and cuisines), and preparing data for analysis.

Classes
-------
Dataloader:
    A class to handle data loading and preprocessing tasks.
"""

import pandas as pd
import utils
from logger_config import logger


class Dataloader:
    """
    A class to handle data loading and preprocessing tasks.

    Attributes
    ----------
    filename : str
        The name of the file to load.
    directory : str
        The directory where the file is located.
    path : str
        The full path to the file.
    """

    def __init__(self, directory: str, filename: str):
        """
        Initialize the DataLoader with a directory and filename.

        Parameters
        ----------
        directory : str
            The directory where the file is located.
        filename : str
            The name of the file to load.
        """
        self.filename = filename
        self.directory = directory
        self.path = f"{directory}/{filename}"
        logger.info(f"Initialized DataLoader for file: {self.path}")

    def read(self) -> pd.DataFrame:
        """
        Read a CSV file from the specified path.

        Returns
        -------
        pd.DataFrame or None
            The loaded data as a DataFrame, or None if the file is not found.

        Raises
        ------
        FileNotFoundError
            If the file is not found at the specified path.
        """
        try:
            logger.info(f"Attempting to read file: {self.path}")
            return pd.read_csv(self.path)
        except FileNotFoundError:
            logger.error(f"File not found: {self.path}")
            return None

    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the loaded data by renaming specific columns.

        Returns
        -------
        pd.DataFrame or None
            The preprocessed data, or None if loading failed.
        """
        data = self.read()
        if data is not None:
            logger.info("Renaming 'recipe_id' to 'id' in the data.")
            data.rename(columns={"recipe_id": "id"}, inplace=True)
        else:
            logger.warning("No data to preprocess.")
        return data

    def load(self) -> pd.DataFrame:
        """
        Load and preprocess the data.

        Returns
        -------
        pd.DataFrame or None
            The preprocessed data, or None if loading failed.
        """
        logger.info("Loading and preprocessing data.")
        return self.preprocess_data()

    def add_year(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add a 'year' column to the data based on the 'submitted' column.

        Parameters
        ----------
        data : pd.DataFrame
            The input data containing a 'submitted' column.

        Returns
        -------
        pd.DataFrame
            The updated DataFrame with the 'year' column added.
        """
        if data is not None and "submitted" in data.columns:
            logger.info("Adding 'year' column based on 'submitted' column.")
            data["year"] = data["submitted"].apply(lambda x: int(x[:4]))
        else:
            logger.warning("'submitted' column not found or data is None.")
        return data

    def merge_recipe_interaction(self, interaction_loader) -> pd.DataFrame:
        """
        Merge recipe data with interaction data based on the 'id' column.

        Parameters
        ----------
        interaction_loader : Dataloader
            Another DataLoader instance for loading interaction data.

        Returns
        -------
        pd.DataFrame or None
            The merged DataFrame with interaction data, or None if loading
            failed.
        """
        logger.info("Merging recipe data with interaction data.")
        data_recipes = self.load()
        interaction = interaction_loader.load()
        if data_recipes is not None and interaction is not None:
            merged_recipe_inter = pd.merge(
                data_recipes, interaction, how="left", on="id"
            )
            logger.info(
                "Merge successful. Adding 'year' column to the mergeddata."
            )
            self.add_year(merged_recipe_inter)
            return merged_recipe_inter
        logger.warning("Failed to merge data: one or both datasets are None.")
        return None

    def adding_nutrition(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add individual nutritional columns from the 'nutrition' column.

        Parameters
        ----------
        data : pd.DataFrame
            The input data containing a 'nutrition' column with lists of
            values.

        Returns
        -------
        pd.DataFrame
            The updated DataFrame with nutritional columns added.
        """
        logger.info("Adding nutritional columns to the data.")
        NutriList = [
            "cal",
            "totalFat",
            "sugar",
            "sodium",
            "protein",
            "satFat",
            "carbs",
        ]
        nutrition_df = pd.DataFrame(
            data["nutrition"].apply(eval).tolist(), columns=NutriList
        )
        merged_recipe_inter = pd.concat([data, nutrition_df], axis=1)
        logger.info("Nutritional columns added successfully.")
        return merged_recipe_inter

    def adding_cuisines(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add a 'cuisine' column to the data based on tags.

        Parameters
        ----------
        data : pd.DataFrame
            The input data containing a 'tags' column.

        Returns
        -------
        pd.DataFrame
            The updated DataFrame with the 'cuisine' column added.
        """
        logger.info("Determining cuisines from tags.")
        data["cuisine"] = data["tags"].apply(utils.determine_cuisine)
        logger.info("Cuisine column added successfully.")
        return data

    def processed_recipe_interaction(self, interaction_loader) -> pd.DataFrame:
        """
        Process recipe and interaction data by merging and adding derived
        features.

        This method performs the following steps:
        - Merges recipe and interaction data.
        - Adds the 'year' column.
        - Adds the 'cuisine' column.
        - Adds individual nutritional columns.

        Parameters
        ----------
        interaction_loader : Dataloader
            Another DataLoader instance for loading interaction data.

        Returns
        -------
        pd.DataFrame
            The fully processed recipe-interaction DataFrame.
        """
        logger.info("Processing recipe and interaction data.")
        return (
            self.merge_recipe_interaction(interaction_loader)
            .pipe(self.add_year)
            .pipe(self.adding_cuisines)
            .pipe(self.adding_nutrition)
        )
