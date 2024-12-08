"""
Comment Analyzer Module
=======================

This module provides tools for analyzing user comments, including:
- Cleaning comments.
- Performing sentiment analysis.
- Generating word frequencies and analyzing contextual word usage.

Classes
-------
CommentAnalyzer:
    Main class for processing and analyzing user comments.
"""

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer
from textblob import TextBlob
from logger_config import logger
import re


class CommentAnalyzer:
    """
    A class for analyzing user comments in a DataFrame.

    Attributes
    ----------
    comments : pd.DataFrame
        A DataFrame containing user comments with a column named 'review'.
    """

    def __init__(self, comments_df: pd.DataFrame):
        """
        Initialize the CommentAnalyzer with a DataFrame.

        Parameters
        ----------
        comments_df : pd.DataFrame
            A DataFrame containing user comments with a 'review' column.
        """
        self.comments = comments_df

    import re  # Assurez-vous d'importer le module 're'

    def clean_comments(self) -> None:
        """
        Clean comments by converting to lowercase, removing punctuation,
        and stripping whitespace. Ensure all entries are treated as strings.

        The cleaned comments are stored in a new column named 'cleaned'.
        """
        if "review" in self.comments.columns:
            self.comments["cleaned"] = (
                self.comments["review"]
                .fillna("")  # Remplace les valeurs NaN par des chaînes vides
                .astype(str)  # Toutes les entrées sont des chaînes de car.
                .apply(  # Applique une fonction à chaque élément
                    lambda x: re.sub(r"[^\w\s]", "", x.lower()).strip()
                )
            )
            # Afficher les entrées qui ne sont pas des chaînes après le
            # nettoyage
            problematic_entries = self.comments[
                self.comments["cleaned"].apply(
                    lambda x: not isinstance(x, str)
                )
            ]
            if not problematic_entries.empty:
                logger.warn("Problematic entries:", problematic_entries)
            else:
                logger.info("No problematic entries.")
            logger.info("Comments cleaned successfully.")
        else:
            logger.error("Column 'review' not found in the DataFrame.")
            self.comments["cleaned"] = pd.Series([], dtype=str)

    def sentiment_analysis(self) -> pd.DataFrame:
        """
        Perform sentiment analysis on the cleaned comments.

        Returns
        -------
        pd.DataFrame
            The original DataFrame with an additional 'polarity' column
            containing sentiment polarity scores.

        Notes
        -----
        The `clean_comments` method should be called before this one to
        ensure that comments are cleaned.
        """
        self.comments["polarity"] = self.comments["cleaned"].apply(
            lambda x: TextBlob(x).sentiment.polarity
        )
        logger.info("Sentiment analysis completed.")
        return self.comments

    def generate_word_frequencies(
        self, engine, max_features: int = 100
    ) -> dict:
        """
        Compute word frequencies from cleaned comments and save them to a
        database.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.
        max_features : int, optional
            Maximum number of most frequent words to include (default is 100).

        Returns
        -------
        dict
            A dictionary where keys are words and values are their frequencies.

        Notes
        -----
        If a table named "word_frequencies" already exists in the database,
        this method will return the existing data instead of recomputing
        frequencies.
        """
        try:
            stored_data = pd.read_sql_table("word_frequencies", con=engine)
            if not stored_data.empty:
                logger.info("Word frequencies found in database.")
                return dict(zip(stored_data["word"], stored_data["frequency"]))
        except Exception as e:
            logger.warning(f"Table not found or error loading data: {e}")

        custom_stop_words = [
            "recipe",
            "used",
            "thanks",
            "make",
            "just",
            "really",
            "didn",
            "bit",
            "great",
            "good",
            "added",
        ]
        all_stop_words = list(ENGLISH_STOP_WORDS) + custom_stop_words

        vectorizer = CountVectorizer(
            stop_words=all_stop_words, max_features=max_features
        )
        word_matrix = vectorizer.fit_transform(self.comments["cleaned"])
        word_frequencies = dict(
            zip(vectorizer.get_feature_names_out(), word_matrix.sum(axis=0).A1)
        )

        try:
            logger.info("Saving word frequencies to database.")
            word_frequencies_df = pd.DataFrame(
                list(word_frequencies.items()), columns=["word", "frequency"]
            )
            word_frequencies_df.to_sql(
                name="word_frequencies",
                con=engine,
                if_exists="replace",
                index=False,
            )
            logger.info("Word frequencies saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save word frequencies to database: {e}")

        return word_frequencies

    def generate_word_frequencies_associated_to_time(
        self, engine, max_features: int = 10
    ) -> dict:
        """
        Generate word frequencies in contexts associated with the word 'time'.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.
        max_features : int, optional
            Maximum number of top contexts to include (default is 10).

        Returns
        -------
        dict
            A dictionary where keys are n-grams (phrases) and values
            are their frequencies.

        Notes
        -----
        This method extracts contexts around the word 'time' and computes
        word frequencies based on these contexts.
        """
        try:
            stored_data = pd.read_sql_table(
                "word_frequencies_time", con=engine
            )
            if not stored_data.empty:
                logger.info("Word frequencies for 'time' found in database.")
                return dict(
                    zip(stored_data["phrase"], stored_data["frequency"])
                )
        except Exception as e:
            logger.warning(f"Table not found or error loading data: {e}")

        def exclude_phrases_with_words(contexts, words_to_exclude):
            """
            Exclude phrases containing specific words or expressions.

            Parameters
            ----------
            contexts : list
                List of contextual phrases.
            words_to_exclude : list
                List of words or expressions to exclude.

            Returns
            -------
            list
                Filtered list of contextual phrases.
            """
            return [
                context
                for context in contexts
                if not any(
                    word in context.lower() for word in words_to_exclude
                )
            ]

        def extract_context(text, target_word="time", window=6) -> str:
            """
            Extract `window` words before and after the target word in a text.

            Parameters
            ----------
            text : str
                The input text.
            target_word : str, optional
                The target word to extract context around (default is 'time').
            window : int, optional
                The number of words to extract before and after the target word
                (default is 6).

            Returns
            -------
            str
                The extracted context or None if the target word is not found.
            """
            words = text.split()
            if target_word in words:
                index = words.index(target_word)
                start = max(index - window, 0)
                end = min(index + window + 1, len(words))
                return " ".join(words[start:end])
            return None

        self.comments["time_context"] = self.comments["cleaned"].apply(
            lambda x: extract_context(x, target_word="time", window=4)
        )

        time_contexts = self.comments[self.comments["time_context"].notnull()][
            "time_context"
        ]
        words_to_exclude = ["ill", "im going", "think time"]
        filtered_time_contexts = exclude_phrases_with_words(
            time_contexts, words_to_exclude
        )

        custom_stop_words = [
            "recipe",
            "used",
            "thanks",
            "make",
            "just",
            "really",
            "didn",
            "bit",
            "great",
            "good",
            "added",
        ]
        all_stop_words = list(ENGLISH_STOP_WORDS) + custom_stop_words

        vectorizer = CountVectorizer(
            stop_words=all_stop_words, ngram_range=(3, 4), max_features=10
        )
        word_matrix = vectorizer.fit_transform(filtered_time_contexts)

        word_frequencies = dict(
            zip(vectorizer.get_feature_names_out(), word_matrix.sum(axis=0).A1)
        )

        logger.info(f"Generated word frequencies: {word_frequencies}")

        try:
            logger.info("Saving word frequencies to database.")
            word_frequencies_df = pd.DataFrame(
                list(word_frequencies.items()), columns=["phrase", "frequency"]
            )
            word_frequencies_df.to_sql(
                name="word_frequencies_time",
                con=engine,
                if_exists="replace",
                index=False,
            )
            logger.info("Word frequencies saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save word frequencies to database: {e}")

        return word_frequencies

    def sentiment_analysis_over_time(self, engine, period='Y'):
        """
        Calculate the average sentiment polarity of comments over specified
        time periods.

        Parameters
        ----------
        period : str, optional
            The time period to group by ('Y' for year, 'M' for month, etc.),
            default is 'Y'.

        Returns
        -------
        pd.DataFrame
            A DataFrame with time period and average sentiment polarity.

        Notes
        -----
        Assumes the DataFrame has a 'date' column in a recognizable datetime
        format.
        """
        # Check if the table is in the database
        try:
            stored_data = pd.read_sql_table("sentiment_by_period", con=engine)
            if not stored_data.empty:
                logger.info("Sentiment analysis over time found in database.")
                return stored_data
        except Exception as e:
            logger.warning(f"Table not found or error loading data: {e}")

        if 'date' not in self.comments.columns:
            logger.error("Date column missing from DataFrame.")
            return None

        # Ensure 'date' is in datetime format
        self.comments['date'] = pd.to_datetime(self.comments['date'])

        # Perform sentiment analysis if not already done
        if 'polarity' not in self.comments.columns:
            self.sentiment_analysis()

        # Group by the specified period and calculate the average polarity
        self.comments['period'] = self.comments['date'].dt.to_period(period)
        sentiment_by_period = (
            self.comments.groupby('period')['polarity']
            .mean()
            .reset_index()
        )

        sentiment_by_period.columns = ['Period', 'Average Sentiment']

        logger.info("Sentiment analysis over time completed.")

        # Save the results to the database
        try:
            sentiment_by_period.to_sql(
                name="sentiment_by_period",
                con=engine,
                if_exists="replace",
                index=False,
            )
            logger.info("Sentiment analysis over time saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save sentiment analysis over time: {e}")

        return sentiment_by_period
