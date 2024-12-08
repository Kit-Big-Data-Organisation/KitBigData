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
from collections import Counter
import pandas as pd
import utils
from comment_analyzer import CommentAnalyzer
from logger_config import logger


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
            data = pd.read_sql_table('oils_dataframe', con=engine)
            if not data.empty:
                print('data found')
                return data
        except Exception as e:
            print(f"Failed to load data from database: {e}")

        self.data.drop_duplicates(subset=['id'], inplace=True)
        self.data['ingredients'] = self.data['ingredients'].apply(eval)

        year_oil = {}

        for year in range(2002, 2011):
            oil_types = {
                "olive oil": 0,
                "vegetable oil": 0,
                "canola oil": 0,
                "sesame oil": 0,
                "peanut oil": 0,
                "cooking oil": 0,
                "salad oil": 0,
                "oil": 0,
                "corn oil": 0,
                "extra virgin olive oil": 0,
            }

            df_year = self.data[self.data['year'] == year]
            number_id = df_year['id'].nunique()

            for _, row in df_year.iterrows():
                ingredients_set = set(row["ingredients"])
                for oil_type in oil_types.keys():
                    if oil_type in ingredients_set:
                        oil_types[oil_type] += 1

            year_oil[year] = {
                oil: count / number_id for oil, count in oil_types.items()
            }

            year_oil[year] = {
                oil: count / number_id for oil, count in oil_types.items()
            }

        for year, oils in year_oil.items():
            for oil in oils:
                year_oil[year][oil] = year_oil[year][oil] / sum(oils.values())
                year_oil[year][oil] = year_oil[year][oil] / sum(oils.values())

        df_oils = pd.DataFrame(year_oil).T.reset_index().rename(
            columns={'index': 'Year'}
        )
        df_oils = df_oils.melt(
            id_vars=['Year'],
            var_name='Oil Type',
            value_name='Proportion')
        df_oils.to_sql(name='oils_dataframe',
                       con=engine,
                       if_exists='replace')

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

    def get_top_tag_per_year(self , engine , DB_PATH):
        """
        Extract the top tags for each year in the dataset and store them in
        the top tag database.

        Returns
        -------
        dict
            A dictionary containing the top tags for each year from 2002 to
            2010.
        """
        try:
            data = pd.read_sql_table("top_tags", con=engine)
            if not data.empty:
                logger.info("Table Top tags found in the database.")
                return
        except Exception as e:
            logger.warning(f"Failed to load data from the database: {e}")

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
        logger.info("Creating table top tags ...")
        utils.create_top_tags_database(DB_PATH , set_number_tags)

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
            print('cuisine evolution dataframe', data)
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
            name="cuisine_evolution_dataframe",
            con=engine,
            if_exists="replace",
            index=True,
            index_label='Year'
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

    def analyse_interactions_ratings(self, engine):
        """
        Analyze the average rating, number of ratings, and mean preparation
        time for each recipe.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with aggregated interactions and ratings data.
        """
        try:
            logger.info("Aggregating interaction and rating data.")
            aggregated = (
                self.data.groupby("id")
                .agg(
                    avg_rating=("rating", "mean"),
                    num_ratings=("rating", "count"),
                    mean_minutes=("minutes", "mean"),
                )
                .reset_index()
            )

            logger.info("Data aggregation completed successfully.")
            return aggregated
        except Exception as e:
            logger.error(
                f"Error while aggregating interactions and ratings: {e}"
            )
            return pd.DataFrame()

    def analyse_average_steps_rating(self, engine):
        """
        Analyze the average number of steps and average rating per year.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the average number of steps and average
            rating per year.
        """
        try:
            logger.info(
                "Converting 'submitted' column to datetime and"
                "extracting the year."
            )
            self.data["year"] = pd.to_datetime(self.data["submitted"]).dt.year

            logger.info(
                "Grouping data by year to calculate average steps and ratings."
            )
            grouped = (
                self.data.groupby("year")
                .agg(
                    avg_steps=("n_steps", "mean"),
                    avg_rating=("rating", "mean"),
                )
                .reset_index()
            )

            logger.info("Average steps and ratings calculated successfully.")
            return grouped
        except KeyError as e:
            logger.error(f"Missing required columns in the data: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        # Return an empty DataFrame in case of an error
        return pd.DataFrame()

    def analyse_user_intractions(self, engine):
        """
        Analyze user interactions over time since the submission of recipes.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        pd.DataFrame
            A DataFrame with the number of interactions and"
            "average rating grouped by days since submission."
        """
        try:
            logger.info(
                "Converting 'submitted' and 'date' columns to datetime format."
            )
            self.data["submitted"] = pd.to_datetime(self.data["submitted"])
            self.data["date"] = pd.to_datetime(self.data["date"])

            logger.info(
                "Calculating the number of days since submission for "
                "each interaction."
            )
            self.data["days_since_submission"] = (
                self.data["date"] - self.data["submitted"]
            ).dt.days

            logger.info(
                "Filtering data to include only rows where "
                "'days_since_submission' > 0."
            )
            filtered_data = self.data[self.data["days_since_submission"] > 0]

            logger.info(
                "Grouping data by 'days_since_submission' to calculate"
                "interactions and average ratings."
            )
            aggregated = (
                filtered_data.groupby("days_since_submission")
                .agg(
                    num_interactions=("id", "count"),  # Number of interactions
                    avg_rating=("rating", "mean"),  # Average rating
                )
                .reset_index()
            )

            logger.info("User interactions analysis completed successfully.")
            return aggregated
        except KeyError as e:
            logger.error(f"Missing required columns in the data: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        # Return an empty DataFrame in case of an error
        return pd.DataFrame()

    def word_count_over_time(self, word):
        """
        Count occurrences of a specific word in comments over time.

        Parameters
        ----------
        word : str
            The word to search for in the comments.

        Returns
        -------
        pd.DataFrame
            A DataFrame with years and the count of the word in that year.
        """

        # Assure that comments are cleaned first
        if 'cleaned' not in self.data.columns:
            comment_analyzer = CommentAnalyzer(self.data)
            comment_analyzer.clean_comments()
        print(self.data.head(1))
        print("COLUMNS1 =  ", self.data.columns)

        # Ajout d'une fonction de vérification pour isoler les entrées
        # problématiques
        def count_word(x):
            try:
                return x.split().count(word)
            except AttributeError:
                # Afficher l'entrée qui a causé l'erreur
                print(f"Problematic entry (expected str, got {type(x)}): {x}")
                return 0

        # Appliquer la fonction de comptage en capturant les erreurs
        self.data['word_count'] = self.data['cleaned'].apply(count_word)

        if 'year' in self.data.columns:
            filtered_data = self.data[self.data['year'].between(2002, 2010)]
            word_counts = (
                filtered_data
                .groupby('year')['word_count']
                .sum()
                .reset_index()
            )
            return word_counts
        else:
            print("Column 'year' not found.")
            return pd.DataFrame()

    def word_co_occurrence_over_time(self, words):
        """
        Count co-occurrences of specific words in comments over time
        and calculate the percentage of comments that contain all the
        specified words each year.

        Parameters
        ----------
        words : list of str
            The words to search for co-occurrences.

        Returns
        -------
        pd.DataFrame
            A DataFrame with years and the percentage of co-occurrences per
            year.
        """
        print(self.data['ingredients'].iloc[0])
        # Assure that comments are cleaned first
        if 'cleaned' not in self.data.columns:
            comment_analyzer = CommentAnalyzer(self.data)
            comment_analyzer.clean_comments()
        print(self.data.head(1))
        print("COLUMNS1 =  ", self.data.columns)

        # Function to count co-occurrences
        def count_co_occurrences(comment):
            return all(word in comment for word in words)

        # Apply the counting function
        self.data['co_occurrence'] = (
            self
            .data['cleaned']
            .apply(count_co_occurrences)
        )

        if 'year' in self.data.columns:
            # Calculate the total comments per year
            total_comments_per_year = self.data.groupby('year').size()
            # Filter the data between specific years if needed
            filtered_data = self.data[self.data['year'].between(2002, 2010)]
            # Calculate the number of co-occurrences per year
            co_occurrences_per_year = (
                filtered_data
                .groupby('year')['co_occurrence']
                .sum()
            )
            # Calculate the percentage of co-occurrences
            result = (
                co_occurrences_per_year
                / total_comments_per_year.loc[co_occurrences_per_year.index]
                * 100
            ).reset_index()
            result.columns = ['year', 'Co-occurrence Percentage']
            return result
        else:
            print("Column 'year' not found.")
            return pd.DataFrame()

    def ingredient_co_occurrence_over_time(self, words):
        """
        Count co-occurrences of specific words in ingredients over time
        and calculate the percentage of entries that contain all the
        specified words each year.

        Parameters
        ----------
        words : list of str
            The words to search for co-occurrences in ingredients.

        Returns
        -------
        pd.DataFrame
            A DataFrame with years and the percentage of co-occurrences per
            year.
        """
        # Ensure words are in lowercase to match ingredient lists
        words = [word.lower() for word in words]

        # Function to count co-occurrences in ingredients
        def count_co_occurrences(ingredients_list):
            # Ensure all words in the search list are present in the
            # ingredient list
            return all(word in ingredients_list for word in words)

        # Apply the counting function
        self.data['co_occurrence'] = (
            self
            .data['ingredients']
            .apply(count_co_occurrences)
        )

        if 'year' in self.data.columns:
            # Calculate the total entries per year
            total_entries_per_year = self.data.groupby('year').size()
            # Filter the data between specific years if needed
            filtered_data = self.data[self.data['year'].between(2002, 2010)]
            # Calculate the number of co-occurrences per year
            co_occurrences_per_year = (
                filtered_data
                .groupby('year')['co_occurrence']
                .sum()
            )
            # Calculate the percentage of co-occurrences
            result = (
                co_occurrences_per_year
                / total_entries_per_year
                .loc[co_occurrences_per_year.index]
                * 100
            ).reset_index()
            result.columns = ['year', 'Co-occurrence Percentage']
            return result
        else:
            print("Column 'year' not found.")
            return pd.DataFrame()

    def calculate_rating_evolution(self, engine) -> pd.DataFrame:
        """
        Calculate the evolution of comment ratings over the years, focusing on
        the years 2002 to 2010.

        Returns
        -------
        pd.DataFrame
            A DataFrame with two columns: 'year' and 'average_rating',
            showing the mean rating for each year within the specified range.

        Notes
        -----
        This function assumes that there is a 'date' column in the DataFrame
        containing the dates of the comments in 'YYYY-MM-DD' format, and a
        'rating' column containing the ratings.
        """
        try:
            data = pd.read_sql_table("rating_evolution", con=engine)
            if not data.empty:
                logger.info(
                    "Data found in the database. Filtering for years 2002 to "
                    "2010."
                )
                filtered_data = data[
                    (data['year'] >= 2002) & (data['year'] <= 2010)
                ]
                if not filtered_data.empty:
                    return filtered_data
                else:
                    logger.info(
                        "No data found in the specified year range",
                        "proceeding, with calculation."
                    )
        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")

        # Convert the 'date' column to datetime if not already done
        if self.data['date'].dtype != 'datetime64[ns]':
            self.data['date'] = pd.to_datetime(
                self.data['date'], format='%Y-%m-%d'
            )

        # Extract the year from the 'date' column
        self.data['year'] = self.data['date'].dt.year

        # Filter data for years 2002 to 2010
        filtered_data = self.data[
            (self.data['year'] >= 2002) & (self.data['year'] <= 2010)
        ]

        # Calculate the average rating for each year in the range
        rating_evolution = (
            filtered_data
            .groupby('year')['rating']
            .mean()
            .reset_index()
        )
        rating_evolution.columns = ['year', 'average_rating']

        logger.info(
            "Rating evolution calculation for specified years completed."
        )

        # Save the data to the database
        try:
            logger.info("Saving rating evolution to the database.")
            rating_evolution.to_sql(
                name="rating_evolution",
                con=engine,
                if_exists="replace",
                index=False,
            )
            logger.info("Data successfully saved to the database.")
        except Exception as e:
            logger.error(
                f"Failed to save data to the database: {e}"
            )

        return rating_evolution

    def sentiment_analysis_over_time(self, engine):
        """
        Calculate the average sentiment polarity of comments, grouped by year
        (2002-2010).

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            Database engine used for the connection.

        Returns
        -------
        pd.DataFrame
            A DataFrame with years (2002-2010) and average sentiment polarity.
        """
        try:
            stored_data = pd.read_sql_table("sentiment_by_year", con=engine)
            if not stored_data.empty:
                logger.info("Sentiment analysis over time found in database.")
                # Filter the data for the years 2002 to 2010
                stored_data = stored_data[
                    (stored_data['Year'] >= 2002)
                    & (stored_data['Year'] <= 2010)
                ]
                return stored_data
        except Exception as e:
            logger.warning(f"Table not found or error loading data: {e}")

        if 'date' not in self.data.columns:
            logger.error("Date column missing from DataFrame.")
            return None

        # Ensure 'date' is in datetime format
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data['year'] = self.data['date'].dt.year

        # Perform sentiment analysis if not already done
        if 'polarity' not in self.data.columns:
            comment_analyzer = CommentAnalyzer(self.data)
            comment_analyzer.clean_comments()
            comment_analyzer.sentiment_analysis()

        # Group by the 'year' column and calculate the average polarity
        sentiment_by_year = (
            self.data.groupby('year')['polarity']
            .mean()
            .reset_index()
        )
        sentiment_by_year.columns = ['Year', 'Average Sentiment']

        # Filter for the years 2002 to 2010
        sentiment_by_year = sentiment_by_year[
            (sentiment_by_year['Year'] >= 2002)
            & (sentiment_by_year['Year'] <= 2010)
        ]

        logger.info("Sentiment analysis over time (2002-2010) completed.")

        # Save the results to the database
        try:
            sentiment_by_year.to_sql(
                name="sentiment_by_year",
                con=engine,
                if_exists="replace",
                index=False,
            )
            logger.info("Sentiment analysis over time saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save sentiment analysis over time: {e}")

        return sentiment_by_year
