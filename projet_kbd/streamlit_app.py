import pandas as pd
import streamlit as st
import utils
from projet_kbd.comment_analyzer import CommentAnalyzer
from projet_kbd.data_analyzer import DataAnalyzer
from projet_kbd.data_loader import Dataloader
from projet_kbd.data_plotter import DataPlotter
from streamlit_option_menu import option_menu
from streamlit_sqlalchemy import StreamlitAlchemyMixin
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from projet_kbd.logger_config import logger

# Configuration Streamlit (doit être appelée en premier)
st.set_page_config(layout="wide")


# Classe pour gérer la base de données avec StreamlitAlchemyMixin
class DatabaseManager(StreamlitAlchemyMixin):
    def __init__(self):
        self.engine = None  # Placeholder for the SQLAlchemy engine

    def attach_engine(self, engine):
        """Attach an SQLAlchemy engine to the manager."""
        self.engine = engine

    def get_engine(self):
        """Get the attached SQLAlchemy engine."""
        if not self.engine:
            raise ValueError("No engine attached to the DatabaseManager.")
        return self.engine


# Instance de DatabaseManager
db_manager = DatabaseManager()


@st.cache_data(hash_funcs={DataAnalyzer: id})
def load_and_analyze_data(path_file, recipe_file, interaction_file, _engine):

    # Charger les données depuis les fichiers si la base est vide
    data_loader = Dataloader(path_file, recipe_file)
    interactions_loader = Dataloader(path_file, interaction_file)
    data = data_loader.processed_recipe_interaction(interactions_loader)
    logger.info("📂 Data loaded successfully from files.")
    try:
        analyzer = DataAnalyzer(data)
        logger.info("📊 Data analyzed successfully.")
    except Exception as e:
        logger.error(f"❌ Error while analyzing data: {e}")
        return None
    
    try:
        analyzer.clean_from_outliers()
        logger.info("🧹 Data cleaned successfully.")
    except Exception as e:
        logger.error(f"❌ Error while cleaning data: {e}")
        return None

    logger.info("📊 Adding data to the database")
    if not isinstance(_engine, Engine):
        raise ValueError("Le paramètre `_engine` n'est pas un objet SQLAlchemy Engine valide.")
    logger.info("✅ Le paramètre `_engine` est un objet SQLAlchemy Engine valide.")
    
    try:
        # Tente d'exécuter une requête simple
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connexion réussie à la base de données.")
    except Exception as e:
        logger.error(f"❌ Échec de connexion à la base de données : {e}")

    def batch_insert_to_sql(df, table_name, engine, chunk_size=1000):
        """
        Insère un DataFrame dans une base SQL par lots.

        Args:
            df (pd.DataFrame): Le DataFrame à insérer.
            table_name (str): Le nom de la table SQL.
            engine (sqlalchemy.engine.Engine): Connexion SQLAlchemy.
            chunk_size (int): Taille des lots pour l'insertion.

        Returns:
            int: Nombre total de lignes insérées.
        """
        total_rows = 0
        with engine.connect() as conn:
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i : i + chunk_size]
                try:
                    chunk.to_sql(name=table_name, con=conn, if_exists="append", index=False)
                    total_rows += len(chunk)
                    print(f"✅ {len(chunk)} lignes insérées (batch {i // chunk_size + 1}).")
                except Exception as e:
                    print(f"❌ Erreur lors de l'insertion du batch {i // chunk_size + 1}: {e}")
        return total_rows
    
    table_name = "recipe_interaction"
    # Check if the table exists
    inspector = inspect(_engine)
    if table_name in inspector.get_table_names():
        logger.info(f"✅ Table '{table_name}' already exists in the database.")
    else:
        logger.info(f"ℹ️ Table '{table_name}' does not exist. Creating it now...")
        try: 
            rows_inserted = batch_insert_to_sql(data, table_name, _engine, chunk_size=1)
            print(f"Total des lignes insérées : {rows_inserted}")
        except Exception as e:
            logger.error(f"❌ Error while writing data to the database: {e}")
            return None
    
        logger.info(f"✅ Table '{table_name}' created successfully.")

    return analyzer


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_plots(analyzer):
    plotter = DataPlotter(analyzer)
    return plotter.plot_nb_recipes_per_year(), plotter.plot_nb_interactions_per_year()


@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_charts(analyzer, set_number):
    plotter = DataPlotter(analyzer)
    return plotter.plot_pie_chart_tags(set_number)


@st.cache_data
def create_wordcloud_plot(_analyzer, _engine):
    comment_analyzer = CommentAnalyzer(_analyzer.data[["review"]].dropna())
    comment_analyzer.clean_comments()
    word_frequencies = comment_analyzer.generate_word_frequencies(_engine)
    return DataPlotter.plot_wordcloud(word_frequencies)


def run(path_file, recipe_file, interaction_file, engine):

    analyzer = load_and_analyze_data(path_file, recipe_file, interaction_file, engine)

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
        col = st.columns([0.5, 0.5])
        recipe_fig, interaction_fig = create_plots(analyzer)
        with col[0]:
            st.plotly_chart(recipe_fig, use_container_width=True)
        with col[1]:
            st.plotly_chart(interaction_fig, use_container_width=True)

    elif selected == "Nutrition Analysis":
        st.write("## Nutrition Analysis")
        oils_analysis = create_oils_stacked_histograms(analyzer, engine)
        st.plotly_chart(oils_analysis, use_container_width=True)

    elif selected == "Sociological Insight":
        st.write("### 🌟 Sociological Insight")
        quick_recipe_fig = create_proportion_quick_recipe_charts(analyzer, engine)
        st.plotly_chart(quick_recipe_fig, use_container_width=True)

    elif selected == "Free Visualisation":
        st.write("## Tags Analysis")
        set_number = st.slider(
            "Select set of top 10 tags (0 for 1-10, 1 for 11-20, etc.)", 0, 9, 0
        )
        tags_chart = create_charts(analyzer, set_number)
        for chart in tags_chart:
            st.plotly_chart(chart, use_container_width=True)
