"""
Data Plotter Module
===================

This module provides functionality for visualizing recipe data, including:
- Time-series plots for interactions and recipes.
- Pie charts for tags and cuisines.
- Bar plots for nutritional analysis and other metrics.

Classes
-------
DataPlotter:
    A class to generate plots and visualizations from analyzed recipe data.
"""

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import utils
from logger_config import logger
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import sqlite3


class DataPlotter:
    """
    A class for creating visualizations based on recipe data analysis.

    Attributes
    ----------
    data_analyzer : object
        An instance of the DataAnalyzer class for accessing analyzed data.
    """
    def __init__(self, data_analyzer , comment_analyzer=None):
        """
        Initialize the DataPlotter object.

        Parameters
        ----------
        data_analyzer : object
            An instance of the DataAnalyzer class for accessing analyzed data.
        """

        self.data_analyzer = data_analyzer
        self.comment_analyzer = comment_analyzer

    def plot_nb_interactions_per_year(self):
        """
        Plot the number of interactions per year as a line chart.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object.
        """
        logger.info("Generating plot for number of interactions per year.")
        x_values, y_values = self.data_analyzer.group_interactions_year()

        df = pd.DataFrame({"Year": x_values, "Interactions": y_values})
        fig = px.line(
            df,
            x="Year",
            y="Interactions",
            title="Number of Interactions per Year",
        )
        logger.info("Plot for interactions per year generated successfully.")
        return fig

    def plot_nb_recipes_per_year(self):
        """
        Plot the number of recipes per year as a line chart.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object.
        """
        logger.info("Generating plot for number of recipes per year.")
        x_values, y_values = self.data_analyzer.group_recipes_year()

        df = pd.DataFrame({"Year": x_values, "Recipes": y_values})
        fig = px.line(
            df, x="Year", y="Recipes", title="Number of recipes per Year"
        )
        logger.info("Plot for recipes per year generated successfully.")
        return fig

    def plot_pie_chart_tags(self, set_number, engine, db_path):
        """
        Generate pie charts for the top tags per year from the database.

        Parameters
        ----------
        db_path : str
            Path to the SQLite database.
        set_number : int
            The tag set number to plot.

        Returns
        -------
        list
            A list of Plotly pie chart figures.
        """
        logger.info(f"Generating pie charts for tag set {set_number}.")
        figs = []

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='top_tags';"
        )
        table_exists = cursor.fetchone() is not None
        if not table_exists:
            logger.info("Creating 'top_tags' table...")
            self.data_analyzer.get_top_tag_per_year(engine, db_path)

        # Query data for the specified set_number
        query = """
        SELECT year, label, size
        FROM top_tags
        WHERE set_number = ?
        """
        cursor.execute(query, (set_number,))
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Organize data by year
        data_by_year = {}
        for year, label, size in rows:
            if year not in data_by_year:
                data_by_year[year] = {"labels": [], "sizes": []}
            data_by_year[year]["labels"].append(label)
            data_by_year[year]["sizes"].append(size)

        # Generate pie charts for each year
        for year, data in data_by_year.items():
            labels = data["labels"]
            sizes = data["sizes"]
            fig = px.pie(
                values=sizes,
                names=labels,
                title=f"Top tags for Year {year}",
                labels={"names": "Tags", "values": "Count"},
            )
            figs.append(fig)

        logger.info(f"Pie charts for tag set {set_number} generated.")
        return figs

    def plot_oil_analysis(self, engine):
        """
        Generate a bar chart for the analysis of oil types over the years.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly bar chart figure.
        """
        logger.info("Generating bar chart for oil analysis.")
        custom_palette = utils.custom_palette

        df_oils = self.data_analyzer.analyze_oils(engine)
        df_oils["color"] = df_oils["Oil Type"].map(custom_palette)

        fig = px.bar(
            df_oils,
            x="Year",
            y="Proportion",
            color="Oil Type",
            color_discrete_map=custom_palette
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Proportion",
            legend_title="Oil Type",
        )
        return fig

    def plot_cuisines_analysis(self, engine):
        """
        Generate a pie chart for the analysis of cuisine types.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly pie chart figure.
        """
        logger.info("Generating pie chart for cuisine analysis.")
        df_cuisine = self.data_analyzer.analyze_cuisines(engine)

        labels, sizes = (
            df_cuisine["Cuisine"].tolist(),
            df_cuisine["Proportion"].tolist(),
        )

        fig = px.pie(values=sizes, names=labels)
        logger
        return fig

    def plot_cuisines_evolution(self, engine):
        """
        Generate a line chart for the evolution of cuisine proportions
        over time.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly line chart figure.
        """
        logger.info("Generating line chart for cuisine evolution.")
        df_cuisine_evolution = self.data_analyzer.cuisine_evolution(engine)
        num_rows = 2
        num_cols = 4
        fig = make_subplots(
            rows=num_rows,
            cols=num_cols,
            subplot_titles=[
                f"{cuisine} Cuisine"
                for cuisine in df_cuisine_evolution.columns
                if cuisine != "Year"
            ],
            vertical_spacing=0.18,
            horizontal_spacing=0.08,
        )

        idx = 1
        
        for cuisine in df_cuisine_evolution.columns:

            if cuisine != "Year":

                row = (idx - 1) // num_cols + 1
                col = (idx - 1) % num_cols + 1

                trace = go.Scatter(
                    x=df_cuisine_evolution['Year'],
                    y=df_cuisine_evolution[cuisine],
                    mode="lines",
                    name=cuisine,
                )
                fig.add_trace(trace, row=row, col=col)

                idx += 1

        fig.update_layout(
            height=800,
            #width=2000,
            showlegend=False,
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Proportion (%)")
        logger.info("Line chart for cuisine evolution generated.")
        return fig

    def plot_top_ingredients(self, engine):
        """
        Generate a bar chart for the top ingredients used in recipes.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly bar chart figure.

        """
        logger.info("Generating bar chart for top ingredients.")
        df_top_ingredients = self.data_analyzer.top_commun_ingredients(engine)
        df_top_ingredients.drop(columns = {'index'} , inplace = True)
        logger.info("Top ingredients generated.")
        return df_top_ingredients[1:]

    def plot_calories_analysis(self, engine):
        """
        Generate a bar chart for the analysis of calories by cuisine.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly bar chart figure.
        """
        logger.info("Generating bar chart for calories analysis.")
        df_calories = self.data_analyzer.analyse_cuisine_nutritions(engine)
        df_calories.sort_values(by="cal", inplace=True)
        fig = px.bar(
            df_calories,
            x="cal",
            y=df_calories["cuisine"],
            orientation="h",
            color=df_calories["cuisine"],
            labels={"cal": "Calories Mean", "cuisine": "Cuisine"},
        )
        logger.info("Bar chart for calories analysis generated.")
        return fig

    def plot_cuisine_time_analysis(self, engine):
        """
        Generate a bar chart for the analysis of recipe times by cuisine.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly bar chart figure.
        """
        logger.info("Generating bar chart for cuisine time analysis.")
        df_times = self.data_analyzer.analyse_cuisine_nutritions(engine)
        df_times.sort_values(by="minutes", inplace=True)

        fig = px.bar(
            df_times,
            x=df_times["cuisine"],
            y="minutes",
            color=df_times["cuisine"],
            labels={"minutes": "Mean minutes", "cuisine": "Cuisine"},
        )
        logger.info("Bar chart for cuisine time analysis generated.")
        return fig

    def plot_cuisine_nutritions(self, engine):
        """
        Generate a bar chart for the nutritional content by cuisine.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly bar chart figure.
        """
        logger.info("Generating bar chart for nutritional content by cuisine.")
        df_nutritions = self.data_analyzer.analyse_cuisine_nutritions(engine)
        nutritions = [
            column
            for column in df_nutritions.columns
            if column not in ["minutes", "cal"]
        ]
        df_nutritions = df_nutritions[nutritions]
        final_long = df_nutritions.reset_index(drop=True).melt(
            id_vars="cuisine", var_name="nutrient", value_name="value"
        )
        print('final long')
        print(final_long)
        print(final_long.columns)

        fig = px.bar(
            final_long,
            x="cuisine",
            y="value",
            color="nutrient",
            labels={"value": "PDV(%)", "nutrient": "Nutrient Type"},
            barmode="group",
        )
        logger.info("Bar chart for nutritional content by cuisine generated.")
        return fig

    def plot_quick_recipes_evolution(self, engine):
        """
        Plot the evolution of the proportion of quick recipes over the years.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly line chart figure.
        """
        logger.info(
            "Attempting to plot the evolution of quick recipes proportions."
        )
        try:
            proportions_df = self.data_analyzer.proportion_quick_recipe(engine)
            if proportions_df is not None and not proportions_df.empty:
                logger.info("Data retrieved successfully, plotting.")
                fig = px.line(
                    proportions_df,
                    x="Year",
                    y="Proportion",
                    title='''
                    Evolution of the Proportion of Quick Recipes Over the Years
                    ''',
                    labels={"Proportion": "Proportion (%)", "Year": "Year"},
                    markers=True,
                )
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Proportion of Quick Recipes (%)",
                    showlegend=False,
                )
                return fig
            else:
                logger.warning("No data available to plot.")
                return None
        except Exception as e:
            logger.error(f"Failed to plot quick recipes evolution: {e}")
            return None

    def plot_rate_interactions_quick_recipe(self, engine):
        """
        Plot the rate of interactions for quick-tagged recipes over the years.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly line chart figure.
        """
        logger.info(
            '''Attempting to plot the evolution of the rate of the interactions
            for quick recipes.'''
        )
        try:
            rate_inter_quick_recipe = (
                self.data_analyzer.get_quick_recipe_interaction_rate(engine)
            )
            if (
                rate_inter_quick_recipe is not None
                and not rate_inter_quick_recipe.empty
            ):
                logger.info("Data retrieved successfully, plotting.")
                fig = px.line(
                    rate_inter_quick_recipe,
                    x="year",
                    y="Proportion",
                    title='''Proportion of Interactions for Quick-Tagged
                    Recipes by Year''',
                    labels={"Proportion": "Proportion (%)", "year": "year"},
                    markers=True,
                )
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Rate of interactions for quick recipe (%)",
                    showlegend=False,
                )
                return fig
            else:
                logger.warning("No data available to plot.")
                return None
        except Exception as e:
            logger.error(
                f"Failed to plot rate interaction quick recipes evolution: {e}"
            )
            return None

    def plot_categories_quick_recipe(self, engine):
        """
        Plot the distribution of categories for quick recipes.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly bar chart figure.
        """
        logger.info("Attempting to plot categories for quick recipes.")
        try:
            # Charger les données des catégories
            category_df = self.data_analyzer.get_categories_quick_recipe(
                engine
            )

            # Vérifier que les données ne sont pas vides et bien formatées
            if (
                category_df is not None
                and not category_df.empty
                and "Category" in category_df.columns
            ):
                logger.info("Data retrieved successfully, plotting.")

                # Création du graphique
                fig = px.bar(
                    category_df,
                    x="Category",
                    y="Count",
                    title="Distribution of Categories for Quick Recipes",
                    labels={
                        "Count": "Number of Recipes",
                        "Category": "Recipe Category",
                    },
                    text="Count",
                )

                # Mise en forme
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Number of Recipes",
                    showlegend=False,
                )

                return fig
            else:
                logger.warning(
                    "No data available or improperly formatted for plotting."
                )
                return None
        except Exception as e:
            logger.error(f"Failed to plot categories for quick recipes: {e}")
            return None

    # Analyse des commentaires


    def plot_wordcloud(self , engine):
        """
        Plot a Word Cloud based on word frequencies.

        Parameters
        ----------
        word_frequencies : dict
            A dictionary containing word frequencies.
        title : str, optional
            The title of the Word Cloud plot.

        Returns
        -------
        matplotlib.figure.Figure
            A Matplotlib figure object.
        """
        comment_analyzer = self.comment_analyzer
        comment_analyzer.clean_comments()
        word_frequencies = comment_analyzer.generate_word_frequencies(engine)
        logger.info("Generating Word Cloud plot.")
        wordcloud = WordCloud(
            width=800, height=400, background_color="white"
        ).generate_from_frequencies(word_frequencies)
        # Générer la figure Matplotlib
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        logger.info("Word Cloud plot generated successfully.")
        return fig

    def plot_time_wordcloud(self , engine):
        """
        Plot a Word Cloud based on word frequencies.

        Parameters
        ----------
        word_frequencies_time : dict
            A dictionary containing word frequencies.

        Returns
        -------
        matplotlib.figure.Figure
            A Matplotlib figure object.
        """
        comment_analyzer = self.comment_analyzer
        comment_analyzer.clean_comments()
        word_frequencies_time = (
            comment_analyzer.generate_word_frequencies_associated_to_time(engine)
        )
        logger.info("Generating Word Cloud plot for time.")
        wordcloud = WordCloud(
            width=800, height=400, background_color="white"
        ).generate_from_frequencies(word_frequencies_time)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout()
        logger.info("Word Cloud plot for time generated successfully.")
        return fig

    def plot_rating_evolution(self, engine):
        """
        Plot the evolution of comment ratings over the years using a Plotly
        line graph.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            SQLAlchemy engine for database interactions.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly line chart figure.
        """
        # Calculate the rating evolution if not already done
        rating_evolution_df = self.data_analyzer.calculate_rating_evolution(
            engine
        )

        # Check if the DataFrame is not empty and proceed with plotting
        if not rating_evolution_df.empty:
            logger.info("Data retrieved successfully, plotting.")
            fig = px.line(
                rating_evolution_df,
                x="year",
                y="average_rating",
                title='Evolution of Comment Ratings Over the Years',
                labels={"average_rating": "Average Rating", "year": "Year"},
                markers=True,
            )
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Average Rating",
                yaxis=dict(range=[4, 5]),
                showlegend=False
            )
            fig.update_traces(line=dict(color="blue"))
            return fig
        else:
            logger.warning("No data available to plot.")
            return None

    def plot_sentiment_over_time(self, engine):
        """
        Visualize the average sentiment polarity of comments over the years.

        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            Database engine used for the connection.

        Returns
        -------
        plotly.graph_objects.Figure
            A Plotly figure object displaying the sentiment over time.
        """
        logger.info("Attempting to plot sentiment analysis over time.")

        try:
            # Retrieve sentiment data
            sentiment_over_time_df = (
                self
                .data_analyzer
                .sentiment_analysis_over_time(engine)
            )
            # Check if the DataFrame is not empty
            if sentiment_over_time_df is not None and \
               not sentiment_over_time_df.empty:
                # Ensure the column names are correct
                if 'Year' not in sentiment_over_time_df.columns or \
                   'Average Sentiment' not in sentiment_over_time_df.columns:
                    logger.error(
                        "Required columns are missing in the DataFrame."
                    )
                    return None

                # Plotting the sentiment analysis over time
                fig = px.line(
                    sentiment_over_time_df,
                    x='Year',
                    y='Average Sentiment',
                    title='Evolution of Average Sentiment Over Time',
                    labels={
                        "Year": "Year",
                        "Average Sentiment": "Average Sentiment Polarity"
                    },
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Average Sentiment Polarity",
                    yaxis=dict(range=[-1, 1]),
                    xaxis=dict(tickmode='linear'),
                    showlegend=False
                )

                # Add a horizontal line at y=0 to indicate neutral sentiment
                fig.add_shape(
                    type="line",
                    x0=sentiment_over_time_df['Year'].min(),
                    x1=sentiment_over_time_df['Year'].max(),
                    y0=0,
                    y1=0,
                    line=dict(color="red", dash="dash"),
                )

                # Add annotations to indicate positive and negative sentiment
                fig.add_annotation(
                    x=sentiment_over_time_df['Year'].mean(),
                    y=0.5,
                    text="Positive Sentiment",
                    showarrow=False,
                    font=dict(size=12, color="green"),
                )
                fig.add_annotation(
                    x=sentiment_over_time_df['Year'].mean(),
                    y=-0.5,
                    text="Negative Sentiment",
                    showarrow=False,
                    font=dict(size=12, color="red"),
                )

                logger.info(
                    "Sentiment analysis over time plot generated successfully."
                )
                return fig
            else:
                logger.warning("No data available to plot.")
                return None
        except Exception as e:
            logger.error(
                f"An error occurred while plotting sentiment analysis: {e}"
            )
            return None
