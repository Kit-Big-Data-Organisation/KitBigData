"""
Data Analyzer Module
====================

This module provides functionalities for analyzing and processing recipe
data, including cleaning data, generating insights, and interacting with
databases.

Classes
-------
DataAnalyzer:
    Main class for data processing and analysis.
"""

import ast
import json
import os
from collections import Counter
import pandas as pd
import utils
from projet_kbd.logger_config import logger


class DataAnalyzer:
    """
    A class for analyzing and processing recipe data.

    Attributes
    ----------
    data : pd.DataFrame
        The DataFrame containing recipe data.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the DataAnalyzer with a DataFrame.

        Parameters
        ----------
        data : pd.DataFrame
            The DataFrame containing recipe data.
        """
        self.data = data

    def clean_from_outliers(self) -> pd.DataFrame:
        """
        Remove outliers from numerical features based on the interquartile
        range (IQR).

        Numerical features cleaned:
        - `minutes`: The time required to prepare a recipe.
        - `cal`: The calorie count of a recipe.

        Returns
        -------
        pd.DataFrame
            The DataFrame with outliers removed.
        """
        numerical_features = ["minutes", "cal"]
        for col in numerical_features:
            IQR = self.data[col].quantile(0.75) - self.data[col].quantile(0.25)
            colmax = self.data[col].quantile(0.75) + 1.5 * IQR
            colmin = self.data[col].quantile(0.25) - 1.5 * IQR
            self.data = self.data[
                (self.data[col] < colmax) & (self.data[col] > colmin)
            ]

        return self.data

    def analyze_oils(self, engine):
        """
        Analyze the proportions of oil types used in recipes over the years.

        If the data is not found in the database, it calculates proportions
        for each oil type by year and saves the results.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with oil type proportions for each year.
        """

        try:
            data = pd.read_sql_table("oils_dataframe", con=engine)
            if not data.empty:
                logger.info("Data found in the database.")
                return data
        except Exception as e:
            logger.warning(f"Failed to load data from the database: {e}")

        self.data.drop_duplicates(subset=["id"], inplace=True)
        self.data["ingredients"] = self.data["ingredients"].apply(eval)

        year_oil = {}
        for year in range(2002, 2011):
            oil_types = {
                'olive oil': 0,
                'vegetable oil': 0,
                'canola oil': 0,
                'sesame oil': 0,
                'peanut oil': 0,
                'cooking oil': 0,
                'salad oil': 0,
                'oil' : 0,
                'corn oil' : 0,
                'extra virgin olive oil' : 0
            }
            
            df_year = self.data[self.data['year'] == year]
            number_id = df_year['id'].nunique()
            
            for _, row in df_year.iterrows():
                ingredients_set = set(row['ingredients'])
                for oil_type in oil_types.keys():
                    if oil_type in ingredients_set:
                        oil_types[oil_type] += 1
            
            year_oil[year] = {oil: count / number_id for oil, count in oil_types.items()}

        for year, oils in year_oil.items():
            for oil in oils:
                year_oil[year][oil] =  year_oil[year][oil]/sum(oils.values())

        df_oils = pd.DataFrame(year_oil).T.reset_index().rename(columns={'index': 'Year'})
        df_oils = df_oils.melt(id_vars=['Year'], var_name='Oil Type', value_name='Proportion')
        df_oils.to_sql(name='oils_dataframe', con=engine, if_exists='replace')

        return df_oils

    def group_interactions_year(self) -> tuple:
        """
        Count the number of interactions (reviews) grouped by year.

        Returns
        -------
        tuple
            A tuple containing the indices (years) and the values (review
            counts).
        """
        grouped_interactions = self.data.groupby("year")["review"].count()
        indices, values = (
            grouped_interactions.index,
            grouped_interactions.values,
        )

        return indices, values

    def group_recipes_year(self) -> tuple:
        """
        Count the number of unique recipes grouped by year.

        Returns
        -------
        tuple
            A tuple containing the indices (years) and the values (recipe
            counts).
        """
        grouped_recipes = self.data.groupby("year")["id"].nunique()
        indices, values = grouped_recipes.index, grouped_recipes.values

        return indices, values

    def get_tags(self, year: int) -> Counter:
        """
        Extract all tags used in recipes for a given year.

        Parameters
        ----------
        year : int
            The year to filter recipes by.

        Returns
        -------
        Counter
            A Counter object containing the frequency of each tag.
        """
        tags = Counter()
        current = self.data[self.data["year"] == year]
        tags_df = current["tags"]

        for row in tags_df:
            row = ast.literal_eval(row)
            tags += Counter(row)

        return tags

    def get_top_tags(self, year: int) -> dict:
        """
        Get the top 100 tags for a specific year.

        Parameters
        ----------
        year : int
            The year to filter recipes by.

        Returns
        -------
        dict
            A dictionary where the year is the key and the top tags are the
            values.
        """
        top_commun_year = {}
        tag_year = self.get_tags(year)
        top_commun_year[year] = tag_year.most_common(100)

        return top_commun_year

    def get_top_tag_per_year(self) -> dict:
        """
        Extract the top tags for each year in the dataset.

        Returns
        -------
        dict
            A dictionary containing the top tags for each year from 2002 to
            2010.
        """
        file_path = "top_tags.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                set_number_tags = json.load(file)
        else:
            set_number_tags = {}
            for set_number in range(0, 10):
                top_tags_years = {}
                for year in range(2002, 2011):
                    tag_year = self.get_top_tags(year)
                    start_idx = set_number * 10
                    end_idx = start_idx + 10 + 1
                    labels = [k for (k, _) in tag_year[year]][
                        start_idx:end_idx
                    ]
                    sizes = [v for (_, v) in tag_year[year]][start_idx:end_idx]
                    top_tags_years[year] = [labels, sizes]

                set_number_tags[set_number] = top_tags_years

            with open(file_path, "w") as file:
                json.dump(set_number_tags, file)

        return set_number_tags

    def analyze_cuisines(self, engine):
        """
        Analyze the proportions of cuisines in the dataset and save the results
        in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with cuisine proportions.

        """
        try:
            data = pd.read_sql_table("cuisine_data", con=engine)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Failed to load data from database: {e}")

        self.data = self.data.drop_duplicates(subset=["id"])
        id_count = self.data["id"].nunique()

        year_ingredients = {}
        for cuisine in self.data["cuisine"].unique():
            if cuisine != "other":
                df_cuisine = self.data[self.data["cuisine"] == cuisine]
                proportion = df_cuisine.shape[0] / id_count
                if proportion <= 0.008:
                    year_ingredients["others"] = (
                        year_ingredients.get("others", 0) + proportion
                    )
                else:
                    year_ingredients[cuisine] = proportion

        labels = year_ingredients.keys()
        sizes = year_ingredients.values()

        cuisine_df = pd.DataFrame({"Cuisine": labels, "Proportion": sizes})

        cuisine_df.to_sql(name="cuisine_data", con=engine, if_exists="replace")

        return cuisine_df

    def cuisine_evolution(self, engine):
        """
        Analyze the evolution of cuisine proportions over the years and save
        the results in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

            Returns
            -------
            pd.DataFrame
                A DataFrame with cuisine proportions for each year.
        """
        try:
            data = pd.read_sql_table("cuisine_evolution_dataframe", con=engine)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Failed to load data from database: {e}")
        df_filtered = self.data[
            self.data["cuisine"].isin(utils.relevant_cuisines)
        ]
        cuisine_counts = df_filtered.groupby(["year", "cuisine"])[
            "id"
        ].nunique()
        year_counts = df_filtered.groupby(["year"])["id"].nunique()
        proportion = cuisine_counts.div(year_counts, level="year")
        proportion_df = proportion.reset_index()
        proportion_df.columns = ["Year", "Cuisine", "Proportion"]
        cuisine_df = (
            proportion_df.pivot(
                index="Year", columns="Cuisine", values="Proportion"
            )
            .reindex(range(2002, 2011))
            .fillna(0)
            * 100
        )
        cuisine_df.to_sql(
            name="cuisine_evolution_dataframe", con=engine, if_exists="replace"
        )

        return cuisine_df

    def top_commun_ingredients(self, engine):
        """
        Analyze the top common ingredients for each cuisine and save the
        results
        in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the top common ingredients for each cuisine.
        """
        try:
            data = pd.read_sql_table("cuisine_top_ingredients", con=engine)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Failed to load data from database: {e}")

        self.data["ingredients"] = self.data["ingredients"].apply(eval)
        self.data = self.data[
            self.data["cuisine"].isin(utils.relevant_cuisines)
        ]
        df_cuisine = self.data.groupby("cuisine")
        ingredients_counts = df_cuisine["ingredients"].apply(
            lambda x: Counter(
                [item for sublist in x for item in sublist]
            ).most_common(5)
        )
        ingredients_counts = ingredients_counts.apply(
            lambda x: [k for (k, _) in x]
        )
        top_ingredients = pd.DataFrame(ingredients_counts).reset_index(
            "cuisine"
        )
        ingredients_expanded = pd.DataFrame(
            top_ingredients["ingredients"].apply(pd.Series)
        )
        ingredients_expanded.columns = [
            f"Top ingredient {i+1}"
            for i in range(ingredients_expanded.shape[1])
        ]
        final_ingredients = pd.concat(
            [
                top_ingredients.drop(columns=["ingredients"]),
                ingredients_expanded,
            ],
            axis=1,
        ).astype("string")
        final_ingredients.drop
        final_ingredients.to_sql(
            name="cuisine_top_ingredients", con=engine, if_exists="replace"
        )
        return final_ingredients

    def analyse_cuisine_nutritions(self, engine):
        """
        Analyze the median nutrition values for each cuisine and save the
        results in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the median nutrition values for each cuisine.
        """
        try:
            data = pd.read_sql_table("cuisines_nutritions", con=engine)
            if not data.empty:
                return data
        except Exception as e:
            print(f"Failed to load data from database: {e}")

        self.data = self.data[
            self.data["cuisine"].isin(utils.relevant_cuisines)
        ]
        cuisines = self.data.groupby("cuisine")
        cuisines_nutritions = pd.DataFrame()
        for name, group in cuisines:
            if name != "other":
                nutrition_medians = group[
                    [
                        "sugar",
                        "protein",
                        "carbs",
                        "totalFat",
                        "satFat",
                        "sodium",
                        "cal",
                        "minutes",
                    ]
                ].median()
                nutrition_medians = pd.DataFrame(nutrition_medians).T
                nutrition_medians["cuisine"] = name
                cuisines_nutritions = pd.concat(
                    [cuisines_nutritions, nutrition_medians], axis=0
                )

        cuisines_nutritions = cuisines_nutritions.set_index("cuisine")
        cuisines_nutritions.to_sql(
            name="cuisines_nutritions", con=engine, if_exists="replace"
        )

        return cuisines_nutritions

    def proportion_quick_recipe(self, engine):
        """
        Calculate the proportion of quick recipes (30 minutes or less) over the
        years and save the results in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the proportion of quick recipes for each year.
        """
        try:
            data = pd.read_sql_table(
                "quick_recipe_proportion_table", con=engine
            )
            if not data.empty:
                logger.info("Data found in the database.")
                return data
            else:
                logger.info(
                    "No data found in the table, calculating proportions."
                )
        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")

        def contains_any_tag(tag_string, target_tags):
            try:
                # Safely evaluate the string to a list
                tags_list = ast.literal_eval(tag_string)
                # Check if any target tag is in the list of tags
                return any(tag in target_tags for tag in tags_list)
            except (ValueError, SyntaxError):
                # In case of any error during evaluation, return False
                return False

        # Suppression des doublons basée sur 'id'
        unique_recipes = self.data.drop_duplicates(subset="id")
        # Filter the data to include only years 2002 to 2010
        unique_recipes = unique_recipes[
            unique_recipes["year"].between(2002, 2010)
        ]

        logger.info(
            "Duplicates removed from data and data between 2002 and 2010."
        )

        # Définition des tags cibles et pertinents
        target_tags = ["30-minutes-or-less", "15-minutes-or-less"]
        all_relevant_tags = [
            "30-minutes-or-less",
            "15-minutes-or-less",
            "4-hours-or-less",
            "60-minutes-or-less",
        ]
        logger.info("Tags for filtering set.")

        # Filtrer les recettes contenant au moins un des tags cibles
        # Filtrer les recettes avec au moins un des target_tags
        df_target = unique_recipes[
            unique_recipes["tags"].apply(
                lambda tags: contains_any_tag(tags, target_tags)
            )
        ]
        df_relevant = unique_recipes[
            unique_recipes["tags"].apply(
                lambda tags: contains_any_tag(tags, all_relevant_tags)
            )
        ]
        logger.info("Recipes filtered based on tags.")

        # Compter les recettes par année pour chaque groupe
        target_counts = df_target.groupby("year").size()
        relevant_counts = df_relevant.groupby("year").size()
        logger.info("Recipes counted by year.")

        # Calculer la proportion en pourcentage
        proportions = (target_counts / relevant_counts) * 100
        proportions_df = proportions.reset_index()
        proportions_df.columns = ["Year", "Proportion"]
        proportions_df = proportions_df.fillna(0.0)
        logger.info("Proportions calculated.")

        # Sauvegarde des données dans la base de données
        proportions_df.to_sql(
            name="quick_recipe_proportion_table",
            con=engine,
            if_exists="replace",
        )
        logger.info("Data saved to the database.")

        return proportions_df

    def get_quick_recipe_interaction_rate(self, engine):
        """
        Calculate the rate of interactions for quick recipes (30 minutes or
        less) over the years and save the results in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the rate of interactions for quick recipes.
        """
        try:
            existing_data = pd.read_sql_table(
                "rate_interactions_for_quick_recipe", con=engine
            )
            if not existing_data.empty:
                logger.info("Data found in the database.")
                return existing_data
            else:
                logger.info(
                    """ No data found in the table, calculation of the number
                    of interaction for quick recipe per year.
                    """
                )
        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")

        def contains_any_tag(tag_string, target_tags):
            try:
                # Safely evaluate the string to a list
                tags_list = ast.literal_eval(tag_string)
                # Check if any target tag is in the list of tags
                return any(tag in target_tags for tag in tags_list)
            except (ValueError, SyntaxError):
                # In case of any error during evaluation, return False
                return False

        # Quick tags à filtrer
        quick_tags = ["30-minutes-or-less", "15-minutes-or-less"]

        # Filtrer les recettes avec des quick tags
        quick_recipes = self.data[
            self.data["tags"].apply(lambda x: contains_any_tag(x, quick_tags))
        ]

        # Compter les interactions totales par année
        total_interactions_by_year = (
            self.data.groupby("year")
            .size()
            .reset_index(name="Total_Interactions")
        )

        # Compter les interactions pour les quicks recipe par année
        quick_interactions_by_year = (
            quick_recipes.groupby("year")
            .size()
            .reset_index(name="Quick_Tag_Interactions")
        )

        # Fusionner les interactions totales et celles avec quick tags
        rate_quick_recipe = pd.merge(
            quick_interactions_by_year,
            total_interactions_by_year,
            on="year",
            how="left",
        )

        # Calculer la proportion des interactions des quick tags
        rate_quick_recipe["Proportion"] = (
            rate_quick_recipe["Quick_Tag_Interactions"]
            / rate_quick_recipe["Total_Interactions"]
        ) * 100
        # Filter the data to include only years 2002 to 2010
        rate_quick_recipe = rate_quick_recipe[
            rate_quick_recipe["year"].between(2002, 2010)
        ]

        # Sauvegarde des données dans la base de données
        rate_quick_recipe.to_sql(
            name="rate_interactions_for_quick_recipe",
            con=engine,
            if_exists="replace",
        )
        logger.info("Data saved to the database.")

        return rate_quick_recipe

    def get_categories_quick_recipe(self, engine):
        """
        Calculate the categories of quick recipes (30 minutes or less) and save
        the results in the database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the categories of quick recipes.
        """
        logger.info(
            "Starting the process to calculate quick recipe categories."
        )

        # Tenter de charger les données existantes depuis la base de données
        try:
            data = pd.read_sql_table("categories_quick_recipe", con=engine)
            if not data.empty:
                logger.info(
                    "Data found in the database. Returning existing data."
                )
                return data
            else:
                logger.info(
                    "No data found in the table, proceeding with calculation."
                )
        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")

        def contains_any_tag(tag_string, target_tags):
            try:
                # Safely evaluate the string to a list
                tags_list = ast.literal_eval(tag_string)
                # Check if any target tag is in the list of tags
                return any(tag in target_tags for tag in tags_list)
            except Exception as e:
                logger.error(f"Error evaluating tags: {e}")
                # In case of any error during evaluation, return False
                return False

        # Suppression des doublons basée sur 'id'
        logger.info("Removing duplicates based on 'id'.")
        unique_recipes = self.data.drop_duplicates(subset="id")
        logger.info(
            f"""Number of unique recipes after
            removing duplicates: {len(unique_recipes)}.
            """
        )

        # Filtrer les données entre 2002 et 2010
        logger.info("Filtering recipes between the years 2002 and 2010.")
        unique_recipes = unique_recipes[
            unique_recipes["year"].between(2002, 2010)
        ]
        logger.info(
            f"""Number of recipes after
            filtering by year: {len(unique_recipes)}.
            """
        )

        # Définition des tags cibles et pertinents
        target_tags = ["30-minutes-or-less", "15-minutes-or-less"]
        logger.info(
            f"Filtering recipes containing target tags: {target_tags}."
        )

        # Filtrer les recettes contenant au moins un des tags cibles
        quick_recipes = unique_recipes[
            unique_recipes["tags"].apply(
                lambda tags: contains_any_tag(tags, target_tags)
            )
        ]
        logger.info(
            f"Number of quick recipes identified: {len(quick_recipes)}."
        )

        # Extraire les tags associés aux types de plats
        main_categories = [
            "main-dish",
            "desserts",
            "appetizers",
            "soups-stews",
            "salads",
            "side-dishes",
            "snacks",
        ]
        logger.info(
            f"Extracting categories from quick recipes: {main_categories}."
        )

        category_count = {
            category: quick_recipes["tags"]
            .apply(lambda x: category in x)
            .sum()
            for category in main_categories
        }
        logger.info(f"Category counts calculated: {category_count}")

        category_df = pd.DataFrame(
            list(category_count.items()), columns=["Category", "Count"]
        )

        # Sauvegarde des données dans la base de données
        try:
            logger.info("Saving category counts to the database.")
            category_df.to_sql(
                name="categories_quick_recipe",
                con=engine,
                if_exists="replace",
                index=False,
            )
            logger.info("Data successfully saved to the database.")
        except Exception as e:
            logger.error(
                f"Failed to save category counts to the database: {e}"
            )

        return category_df
