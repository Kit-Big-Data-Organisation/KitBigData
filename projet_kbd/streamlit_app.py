import pandas as pd
import streamlit as st
import utils
from comment_analyzer import CommentAnalyzer
from data_analyzer import DataAnalyzer
from data_loader import Dataloader
from data_plotter import DataPlotter
from streamlit_option_menu import option_menu
from logger_config import logger
from sqlalchemy import SQLAlchemyError



@st.cache_data
def load_and_analyze_data(path_file, recipe_file, interaction_file, _engine):

    try:
        logger.info("Attempting to load data from the database.")
        data = pd.read_sql_table("recipe_interaction", con=_engine)
        if not data.empty:
            logger.info("Data successfully loaded from the database.")
            return DataAnalyzer(data)
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}", exc_info=True)

    try:
        logger.info("Loading data from files.")
        data_loader = Dataloader(path_file, recipe_file)
        interactions_loader = Dataloader(path_file, interaction_file)
        data = data_loader.processed_recipe_interaction(interactions_loader)
        analyzer = DataAnalyzer(data)

        logger.info("Cleaning data from outliers.")
        analyzer.clean_from_outliers()

        try:
            logger.info("Writing processed data back to the database.")
            analyzer.data.to_sql(name="recipe_interaction", con=_engine, if_exists="replace", index=False)
            logger.info("Data successfully written to the database.")
        except SQLAlchemyError as e:
            logger.error("An error occurred while writing to the database.", exc_info=True)
            # Gérer ou relancer l'erreur selon le besoin de l'application
            raise
        except Exception as e:
            logger.error("An unexpected error occurred during database operations.", exc_info=True)
            raise

        logger.info("Data processing complete.")
        return analyzer
    except Exception as e:
        logger.error(f"Error during data processing: {e}", exc_info=True)
        raise


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_plots(analyzer):
    plotter = DataPlotter(analyzer)
    recipe_fig = plotter.plot_nb_recipes_per_year()
    interaction_fig = plotter.plot_nb_interactions_per_year()
    return recipe_fig, interaction_fig


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_charts(analyzer, set_number):
    plotter = DataPlotter(analyzer)
    return plotter.plot_pie_chart_tags(set_number)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_oils_stacked_histograms(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_oil_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_cuisine_charts(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisines_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_cuisine_evolution_charts(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisines_evolution(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_top_ingredients_table(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_top_ingredients(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_cuisine_calories(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_calories_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_cuisine_minutes(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisine_time_analysis(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def analyze_cuisine_nutritions(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisine_nutritions(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_proportion_quick_recipe_charts(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_quick_recipes_evolution(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_rate_interactions_quick_recipe_charts(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_rate_interactions_quick_recipe(_engine)


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_categories_quick_recipe_chart(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_categories_quick_recipe(_engine)


@st.cache_data
def create_wordcloud_plot(_analyzer, _engine):
    comment_analyzer = CommentAnalyzer(_analyzer.data[["review"]].dropna())
    comment_analyzer.clean_comments()
    word_frequencies = comment_analyzer.generate_word_frequencies(_engine)
    return DataPlotter.plot_wordcloud(word_frequencies)


@st.cache_data
def create_time_wordcloud_plot(_analyzer, _engine):
    comment_analyzer = CommentAnalyzer(_analyzer.data[["review"]].dropna())
    comment_analyzer.clean_comments()
    word_frequencies_time = (
        comment_analyzer.generate_word_frequencies_associated_to_time(_engine)
    )
    return DataPlotter.plot_time_wordcloud(word_frequencies_time)


def run(path_file, recipe_file, interaction_file, engine):

    st.set_page_config(layout="wide")

    analyzer = load_and_analyze_data(
        path_file, recipe_file, interaction_file, engine
    )
    with st.sidebar:
        selected = option_menu(
            "Dashboard",
            [
                "Presentation",
                "Nutrition Analysis",
                "Cuisine Analysis",
                "Sociological Insight",
                "Free Visualisation",
            ],
            menu_icon="cast",
        )

    if selected == "Presentation":

        st.write("## Presentation")

        # Texte indiquant la période d'analyse
        st.write(
            """
            Based on the graphs above, we observe that both the number of
            recipes and the number of interactions peak between
            2002 and 2010.
            \nBefore 2002, the data is sparse, with significantly fewer
            recipes and interactions recorded.
            \nAfter 2010, there is a noticeable decline in both metrics. To
            ensure a meaningful analysis, we will focus on the period between
            2002 and 2010, where the data is most abundant and representative
            of user engagement.
            """
        )

        # Création des colonnes et affichage des graphiques
        col = st.columns([0.5, 0.5])
        recipe_fig, interaction_fig = create_plots(
            analyzer
        )  # Fonction qui génère les figures Plotly

        with col[0]:
            st.plotly_chart(recipe_fig, use_container_width=True)

        with col[1]:
            st.plotly_chart(interaction_fig, use_container_width=True)

    elif selected == "Nutrition Analysis":

        st.write("## Nutrition Analysis")

        col = st.columns([0.5, 0.5])
        oils_analysis = create_oils_stacked_histograms(analyzer, engine)
        with col[0]:
            st.plotly_chart(oils_analysis)

    elif selected == "Cuisine Analysis":

        col = st.columns([0.3, 0.7])

        with col[0]:
            st.markdown("#### Cuisine Analysis")
            cuisine_analysis = create_cuisine_charts(analyzer, engine)
            st.plotly_chart(cuisine_analysis, use_container_width=True)

        with col[1]:
            st.markdown("#### Cuisine Evolution")
            cuisine_evolution = create_cuisine_evolution_charts(
                analyzer, engine
            )
            st.plotly_chart(cuisine_evolution, use_container_width=True)
            st.markdown("#### Cuisine nutrition analysis")
            cuisine_calories = analyze_cuisine_calories(analyzer, engine)
            st.plotly_chart(cuisine_calories, use_container_width=True)

            cuisine_minutes = analyze_cuisine_minutes(analyzer, engine)
            st.plotly_chart(cuisine_minutes, use_container_width=True)

            cuisine_nutritions = analyze_cuisine_nutritions(analyzer, engine)
            st.plotly_chart(cuisine_nutritions, use_container_width=True)

            st.markdown("#### Top ingredients")
            top_ingredients_cuisine = create_top_ingredients_table(
                analyzer, engine
            )
            styled_df = top_ingredients_cuisine.style.applymap(
                utils.highlight_cells
            )
            st.dataframe(styled_df, hide_index=True, use_container_width=True)

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

        st.write(
            """
            The graphs illustrate a steady rise in both the **proportion
            of quick recipes** 🍳 and the **engagement with these recipes**
            💬 between 2002 and 2010.

            This reflects a societal shift toward **convenience** and
            **time efficiency** 🕒 in cooking, driven by:
            - **Busier schedules**: As lifestyles became more fast-paced, less
              time was available for traditional cooking.
            - **Dual-income households**: With more families having both
            partners working, the demand for quick meal solutions increased.
            - **Work-life balance**: The emphasis on balancing professional and
              personal lives encouraged time-saving habits in the kitchen.

            As a result, cooking evolved from being a **traditional,
            time-intensive activity** to a **functional necessity** ⚡,
            catering to individuals seeking fast and practical meal
            preparation.
            """
        )

        # Analuse Quick recipe categories
        categories_quick_recipe_fig = create_categories_quick_recipe_chart(
            analyzer, engine
        )
        st.plotly_chart(
            categories_quick_recipe_fig,
            use_container_width=True,
            caption="Distribution of Quick Recipe Categories (2002-2010)",
        )
        st.write(
            """
            Building on our previous analysis, this graph further supports the
            observation that the rise in quick recipes primarily targets **main
            dishes**, which are traditionally more time-intensive to prepare
            compared to categories like snacks or soups.

            The dominance of main dishes among quick recipes highlights how
            this shift toward **convenience and time efficiency** 🕒 is not
            limited to inherently fast-to-make foods, but extends to the
            cornerstone of a meal: the **main course**.

            This reinforces the idea that individuals are seeking practical
            solutions to maintain **structured and complete meals**, even with
            busier schedules and dual-income households. By focusing on
            simplifying main dish preparation, this trend reflects a societal
            adaptation to modern lifestyles, validating our analysis of cooking
            evolving into a **functional yet fulfilling necessity** ⚡.
            """
        )

        # Analyse des commentaires (Word Cloud général)
        st.write("### Word Cloud: Frequent Terms in Comments 📝")
        wordcloud_fig = create_wordcloud_plot(analyzer, engine)
        st.pyplot(wordcloud_fig)
        st.write(
            """
            Frequent terms like **"easy"** and **"quick"** highlight a focus on
            **efficiency** in cooking, reinforcing the trend toward simpler
            meals.
            """
        )

        # Analyse des termes associés à "time"
        st.write("### Word Cloud: Context Around 'Time' ⏱️")
        time_wordcloud_fig = create_time_wordcloud_plot(analyzer, engine)
        st.pyplot(time_wordcloud_fig)
        st.write(
            """
            This word cloud emphasizes how "time" in user comments often refers
            to cooking efficiency. Phrases like **"cut cooking time"** show a
            desire for quicker meals, while **"long time ago"** reflects
            frustrations with time-consuming recipes.
            """
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
            tags_chart = create_charts(analyzer, set_number)
            with st.container():
                for i in range(0, 8, 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(tags_chart):
                            with cols[j]:
                                st.plotly_chart(
                                    tags_chart[i + j], use_container_width=True
                                )
