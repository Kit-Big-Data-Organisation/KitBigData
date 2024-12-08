"""
This module integrates functionalities to analyze and visualize culinary
trends using pandas, streamlit, and plotly.

Features:
- Data loading and preprocessing with custom utilities.
- Advanced analysis via the DataAnalyzer class, ensuring quality insights.
- Interactive visualizations with Plotly, managed by DataPlotter, to explore
  trends in recipes and interactions.
- Streamlit's caching integration enhances performance by minimizing data
  reloads and reprocessing.
- The streamlit_option_menu allows navigable dashboard creation for various
  analytical views.
- CommentAnalyzer extracts sentiments and key terms from user reviews.

The structure supports expansion and integration of more data sources and
analytical techniques, aiming to provide a comprehensive sociological tool
for exploring eating habits and culinary preferences.

Dependencies:
- pandas: For data manipulation.
- streamlit: For the interactive web application.
- plotly.express: For interactive and dynamic visual charts.
- SQLAlchemy: For database interactions.
- Custom modules like utils, analysis_text, and logger_config enhance
  functionality and user experience.

Intended for a web application environment, this script provides an interactive
dashboard for exploring culinary data.
"""

import pandas as pd
import streamlit as st
import utils
import analysis_text
import plotly.express as px
from comment_analyzer import CommentAnalyzer
from data_analyzer import DataAnalyzer
from data_loader import Dataloader
from data_plotter import DataPlotter
from logger_config import logger
from streamlit_option_menu import option_menu
from main import DB_PATH


@st.cache_data
def load_and_analyze_data(path_file, recipe_file, interaction_file, _engine):
    """
    Loads and analyzes recipe interaction data from a database or files if
    not available in the database.

    This function first tries to load the recipe interaction data from a
    database using a provided SQL engine. If data exists, it returns a
    DataAnalyzer object initialized with this data. If no data is found, it
    processes data from specified files, cleans it from outliers, and saves
    the cleaned data back to the database. The function caches its results
    to avoid redundant data processing.

    Parameters
    ----------
    path_file : str
        The file path where the data files are located.
    recipe_file : str
        The filename for the recipe data.
    interaction_file : str
        The filename for the interaction data.
    engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    DataAnalyzer
        An instance of the DataAnalyzer class initialized with the loaded
        and processed data.

    Raises
    ------
    Exception
        If the data fails to load from the database or files, an error
        message is printed.
    """
    try:
        data = pd.read_sql_table("recipe_interaction", con=_engine)
        if not data.empty:
            print("data found")
            return DataAnalyzer(data)
    except Exception as e:
        print(f"Failed to load data from database: {e}")

    data_loader = Dataloader(path_file, recipe_file)
    interactions_loader = Dataloader(path_file, interaction_file)
    data = data_loader.processed_recipe_interaction(interactions_loader)
    analyzer = DataAnalyzer(data)
    analyzer.clean_from_outliers()

    analyzer.data.to_sql(
        name="recipe_interaction", con=_engine, if_exists="replace"
    )
    return analyzer


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_plots(analyzer):
    """
    Creates and returns the plotly figures for the number of recipes and
    interactions per year.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

        Returns
        -------
        plotly.graph_objs.Figure
            A plotly figure showing the number of recipes per year.
            plotly.graph_objs.Figure
            A plotly figure showing the number of interactions per year.
    """
    plotter = DataPlotter(analyzer)
    recipe_fig = plotter.plot_nb_recipes_per_year()
    interaction_fig = plotter.plot_nb_interactions_per_year()
    return recipe_fig, interaction_fig


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_charts(analyzer, set_number, _engine, _DB_PATH):
    """
    Creates and returns the plotly figures for the tags distribution.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
    set_number : int
        The set of top 10 tags to display (0 for 1-10, 1 for 11-20, etc.).

    Returns
    -------
    list
        A list of plotly figures showing the distribution of tags.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_pie_chart_tags(set_number, _engine, _DB_PATH)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_oils_stacked_histograms(analyzer, _engine):
    """
    Creates and returns the plotly figure for the oil analysis.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the oil analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_oil_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_cuisine_charts(analyzer, _engine):
    """
    Creates and returns the plotly figure for the cuisine analysis.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the cuisine analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisines_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_cuisine_evolution_charts(analyzer, _engine):
    """
    Creates and returns the plotly figure for the cuisine evolution analysis.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the cuisine evolution analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisines_evolution(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_top_ingredients_table(analyzer, _engine):
    """
    Creates and returns the top ingredients table.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    pandas.DataFrame
        A DataFrame showing the top ingredients.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_top_ingredients(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_cuisine_calories(analyzer, _engine):
    """
    Analyzes the calories by cuisine and returns the plotly figure.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the calories by cuisine analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_calories_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_cuisine_time(analyzer, _engine):
    """
    Analyzes the time by cuisine and returns the plotly figure.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the time by cuisine analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisine_time_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_cuisine_nutritions(analyzer, _engine):
    """
    Analyzes the nutritional content by cuisine and returns the plotly figure.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the nutritional content by cuisine analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisine_nutritions(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_proportion_quick_recipe_charts(analyzer, _engine):
    """
    Creates and returns the plotly figure for the proportion of quick recipes.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the proportion of quick recipes.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_quick_recipes_evolution(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_rate_interactions_quick_recipe_charts(analyzer, _engine):
    """
    Creates and returns the plotly figure for the rate of interactions for
    quick recipes.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the rate of interactions for quick recipes.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_rate_interactions_quick_recipe(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_categories_quick_recipe_chart(analyzer, _engine):
    """
    Creates and returns the plotly figure for the distribution of quick recipe
    categories.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the distribution of quick recipe categories.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_categories_quick_recipe(_engine)


@st.cache_data
def create_wordcloud_plot(_analyzer, _Comment_analyzer, _engine):
    """
    Creates and returns the wordcloud plot for the comments.

    Parameters
    ----------
    _analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _Comment_analyzer : CommentAnalyzer
        An instance of the CommentAnalyzer class containing the cleaned
        comments.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    matplotlib.figure.Figure
        A matplotlib figure showing the wordcloud plot.
    """
    plotter = DataPlotter(_analyzer , _Comment_analyzer)
    return plotter.plot_wordcloud(_engine)


@st.cache_data
def create_time_wordcloud_plot(_analyzer, _Comment_analyzer, _engine):
    """
    Creates and returns the wordcloud plot for the comments containing the
    word "time".

    Parameters
    ----------
    _analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _Comment_analyzer : CommentAnalyzer
        An instance of the CommentAnalyzer class containing the cleaned
        comments.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    matplotlib.figure.Figure
        A matplotlib figure showing the wordcloud plot.
    """
    plotter = DataPlotter(_analyzer , _Comment_analyzer)
    return plotter.plot_time_wordcloud(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_plot_rating_evolution(_analyzer, _engine):
    """
    Creates and returns the plotly figure for the rating evolution.

    Parameters
    ----------
    _analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the rating evolution.
    """
    plotter = DataPlotter(_analyzer)
    return plotter.plot_rating_evolution(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_plot_sentiment_evolution(_analyzer, _engine):
    """
    Creates and returns the plotly figure for the sentiment evolution.

    Parameters
    ----------
    _analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the sentiment evolution.
    """
    plotter = DataPlotter(_analyzer)
    return plotter.plot_sentiment_over_time(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_interactions_ratings(analyzer, _engine):
    """
    Analyzes the interactions ratings and returns the plotly figure.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the interactions ratings analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_interactions_ratings(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_user_interactions(analyzer, _engine):
    """
    Analyzes the user interactions and returns the plotly figure.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the user interactions analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_user_interactions(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyse_average_steps_rating(analyzer, _engine):
    """
    Analyzes the average steps rating and returns the plotly figure.

    Parameters
    ----------
    analyzer : DataAnalyzer
        An instance of the DataAnalyzer class containing the recipe and
        interaction data.
        _engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.

    Returns
    -------
    plotly.graph_objs.Figure
        A plotly figure showing the average steps rating analysis.
    """
    plotter = DataPlotter(analyzer)
    return plotter.plot_average_steps_rating(_engine)


def run(path_file, recipe_file, interaction_file, engine):
    """
    Main function to run the Streamlit application.

    Parameters
    ----------
    path_file : str
        The file path where the data files are located.
    recipe_file : str
        The filename for the recipe data.
    interaction_file : str
        The filename for the interaction data.
    engine : sqlalchemy.engine.Engine
        SQLAlchemy engine for database interactions.
    """

    st.set_page_config(layout="wide")

    analyzer = load_and_analyze_data(
        path_file, recipe_file, interaction_file, engine
    )
    comment_analyzer = CommentAnalyzer(analyzer.data[["review"]].dropna())

    with st.sidebar:
        selected = option_menu(
            "Dashboard",
            [
                "Presentation",
                "Eating habits",
                "Cuisine Analysis",
                "Sociological Insight",
                "Interaction with the reviews",
                "Free Visualisation",
            ],
            menu_icon="cast",
        )

    st.markdown(
        """
            <style>
                .justified {
                    text-align: justify;
                    text-justify: inter-word;
                }
            </style>
            """,
        unsafe_allow_html=True,
    )
    if selected == "Presentation":

        st.write("## Presentation")

        # Texte indiquant la période d'analyse

        utils.render_justified_text(analysis_text.presentation)

        # Création des colonnes et affichage des graphiques
        col = st.columns([0.5, 0.5])
        recipe_fig, interaction_fig = create_plots(
            analyzer
        )  # Fonction qui génère les figures Plotly

        average_steps_rating = analyse_average_steps_rating(analyzer, engine)
        interaction_ratings = analyze_interactions_ratings(analyzer, engine)
        user_interactions = analyze_user_interactions(analyzer, engine)

        st.plotly_chart(recipe_fig, use_container_width=True)

        st.plotly_chart(interaction_fig, use_container_width=True)

        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        utils.render_justified_text(analysis_text.average_steps_rating)

        st.plotly_chart(average_steps_rating, use_container_width=True)

        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        utils.render_justified_text(analysis_text.interaction_ratings)

        st.plotly_chart(interaction_ratings, use_container_width=True)

        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        utils.render_justified_text(analysis_text.user_interactions)

        st.plotly_chart(user_interactions, use_container_width=True)

    elif selected == "Eating habits":

        st.write("## Eating habits")
        utils.render_justified_text(analysis_text.eating_habit_presentation)
        oils_analysis = create_oils_stacked_histograms(analyzer, engine)
        st.plotly_chart(oils_analysis)
        utils.render_justified_text(analysis_text.oil_analysis)

    elif selected == "Cuisine Analysis":

        st.markdown("## Cuisine Analysis")
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        utils.render_justified_text(analysis_text.cuisine_presentation)

        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        st.markdown("#### Distribution of Cuisine Types")
        cuisine_analysis = create_cuisine_charts(analyzer, engine)
        st.plotly_chart(cuisine_analysis, use_container_width=True)

        utils.render_justified_text(analysis_text.cuisine_distribtuion)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        st.markdown("#### Cuisine Evolution over the years")
        cuisine_evolution = create_cuisine_evolution_charts(analyzer, engine)
        st.plotly_chart(cuisine_evolution, use_container_width=True)

        utils.render_justified_text(analysis_text.cuisine_evolution)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        st.markdown("#### Cuisine Calories analysis")

        cuisine_calories = analyze_cuisine_calories(analyzer, engine)
        st.plotly_chart(cuisine_calories, use_container_width=False)
        utils.render_justified_text(analysis_text.cuisine_calories)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        st.markdown("#### Cuisine time analysis")
        cuisine_time = analyze_cuisine_time(analyzer, engine)
        st.plotly_chart(cuisine_time, use_container_width=False)
        utils.render_justified_text(analysis_text.cuisine_time_analysis)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        st.markdown("#### Nutritional content by Cuisine in PDV")
        utils.render_justified_text(analysis_text.cuisine_nutritions)
        cuisine_nutritions = analyze_cuisine_nutritions(analyzer, engine)
        st.plotly_chart(cuisine_nutritions, use_container_width=False)
        utils.render_justified_text(analysis_text.cuisine_nutritions)
        st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)

        st.markdown("#### Top ingredients")
        top_ingredients_cuisine = create_top_ingredients_table(
            analyzer, engine
        )
        styled_df = top_ingredients_cuisine.style.map(utils.highlight_cells)
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
        utils.render_justified_text(analysis_text.cuisine_top_ingredients)

    elif selected == "Sociological Insight":

        st.write("### 🌟 Sociological Insight")

        col = st.columns([0.5, 0.5])
        quick_recipe_fig = create_proportion_quick_recipe_charts(
            analyzer, engine
        )
        interactions_quick_recipe_fig = (
            create_rate_interactions_quick_recipe_charts(analyzer, engine)
        )

        # Affichage des graphiques dans les colonnes
        with col[0]:
            st.plotly_chart(
                quick_recipe_fig,
                use_container_width=True,
                caption="Proportion of Quick Recipes (2002-2010)",
            )

        with col[1]:
            st.plotly_chart(
                interactions_quick_recipe_fig,
                use_container_width=True,
                caption="Rate of Interactions for Quick Recipes (2002-2010)",
            )

        # Ajouter une séparation pour une meilleure lisibilité
        st.write("---")

        # Ajout de l'analyse sociologique

        utils.render_justified_text(analysis_text.quick_recipes_analysis)

        # Analuse Quick recipe categories
        categories_quick_recipe_fig = create_categories_quick_recipe_chart(
            analyzer, engine
        )
        st.plotly_chart(
            categories_quick_recipe_fig,
            use_container_width=True,
            caption="Distribution of Quick Recipe Categories (2002-2010)",
        )
        utils.render_justified_text(analysis_text.main_dishes_analysis)

        # Analyse des commentaires (Word Cloud général)
        st.write("### Word Cloud: Frequent Terms in Comments 📝")
        wordcloud_fig = create_wordcloud_plot(
            analyzer, comment_analyzer, engine
        )
        st.pyplot(wordcloud_fig)
        utils.render_justified_text(analysis_text.efficiency_focus_analysis)

        # Analyse des termes associés à "time"
        st.write("### Word Cloud: Context Around 'Time' ⏱️")
        time_wordcloud_fig = create_time_wordcloud_plot(
            analyzer, comment_analyzer, engine
        )
        st.pyplot(time_wordcloud_fig)
        utils.render_justified_text(analysis_text.time_efficiency_analysis)

    elif selected == "Interaction with the reviews":
        st.title("📈 Rate Evolution and Sentiment Analysis Over Time")

        logger.info("Rate evolution...")
        rate_evolution = create_plot_rating_evolution(analyzer, engine)
        st.plotly_chart(rate_evolution, use_container_width=True)
        utils.render_justified_text(analysis_text.comment_ratings_analysis)

        logger.info("Sentiment analysis...")
        sentiment_evolution = create_plot_sentiment_evolution(analyzer, engine)
        st.plotly_chart(sentiment_evolution, use_container_width=True)
        utils.render_justified_text(analysis_text.sentiment_trend_analysis)

        utils.render_justified_text(analysis_text.word_frequency_analysis)

        words_input = st.text_input(
            "Enter words to search for co-occurrence, separated by commas:", ""
        )
        words = (
            [word.strip() for word in words_input.split(",")]
            if words_input
            else []
        )

        if words:
            word_counts = DataAnalyzer.word_co_occurrence_over_time(
                analyzer, words
            )

            if not word_counts.empty:
                fig = px.line(
                    word_counts,
                    x="year",
                    y="Co-occurrence Percentage",
                    title=(
                        "Proportion of Comments Containing the "
                        "Specified Words Over Time"
                    ),
                    labels={
                        "year": "Year",
                        "Co-occurrence Percentage": (
                            "Percentage of Comments (%)"
                        ),
                    },
                )
                fig.update_layout(
                    xaxis=dict(
                        tickmode="linear",
                        tickformat="d",  # Afficher les années sans virgules
                    ),
                    yaxis=dict(range=[0, 100]),
                    yaxis_title="Percentage of Comments (%)",
                    xaxis_title="Year",
                    legend_title="Words",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(
                    "No co-occurrence data found for the specified words."
                )
    elif selected == "Free Visualisation":
        st.write("## Tags Analysis")
        col = st.columns([0.8, 0.2])

        with col[0]:
            set_number = st.slider(
                "Select set of top 10 tags (0 for 1-10, 1 for 11-20, etc.)",
                0,
                9,
                0,
            )
            tags_chart = create_charts(analyzer, set_number, engine, DB_PATH)
            with st.container():
                for i in range(0, 8, 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(tags_chart):
                            with cols[j]:
                                st.plotly_chart(
                                    tags_chart[i + j], use_container_width=True
                                )
