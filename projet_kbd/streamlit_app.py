from data_analyzer import DataAnalyzer
from data_plotter import DataPlotter
import streamlit as st
from data_loader import Dataloader
import functools
import pandas as pd
import sqlalchemy
from streamlit_option_menu import option_menu



@st.cache_data
def load_and_analyze_data(path_file, recipe_file, interaction_file, _engine):
    try:
        data = pd.read_sql_table('recipe_interaction', con=_engine)
        if not data.empty:
            print('data found')
            return DataAnalyzer(data)
    except Exception as e:
        print(f"Failed to load data from database: {e}")

    data_loader = Dataloader(path_file, recipe_file)
    interactions_loader = Dataloader(path_file, interaction_file)
    data = data_loader.processed_recipe_interaction(interactions_loader)
    analyzer = DataAnalyzer(data)
    analyzer.clean_from_outliers()
    analyzer.data.to_sql(name='recipe_interaction', con=_engine, if_exists='replace')
    return analyzer

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
def create_nutrition_histograms(analyzer):
    plotter = DataPlotter(analyzer)
    return plotter.plot_high_rating_nutrition()

@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_oils_stacked_histograms(analyzer, _engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_oil_analysis(_engine)

@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_cuisine_charts(analyzer,_engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisines_analysis(_engine)

@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_cuisine_evolution_charts(analyzer,_engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_cuisines_evolution(_engine)

@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_top_ingredients_table(analyzer,_engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_top_ingredients(_engine)

@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_proportion_quick_recipe_charts(analyzer,_engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_quick_recipes_evolution(_engine)

@st.cache_data(hash_funcs={DataAnalyzer: id})
def create_rate_interactions_quick_recipe_charts(analyzer,_engine):
    plotter = DataPlotter(analyzer)
    return plotter.plot_rate_interactions_quick_recipe(_engine)

def run(path_file , recipe_file , interaction_file , engine):
        
        st.set_page_config(layout="wide")

        analyzer = load_and_analyze_data(path_file,recipe_file, interaction_file, engine)
        with st.sidebar:
            selected = option_menu("Dashboard", ["Presentation", 'Nutrition Analysis', 'Cuisine Analysis', 'Quick recipe analysis', 'Free Visualisation']
                , menu_icon="cast")

        if selected == 'Presentation':

            st.write("## Presentation")

            col = st.columns([0.5 , 0.5])
            recipe_fig, interaction_fig = create_plots(analyzer)

            with col[0]:
                st.plotly_chart(recipe_fig ,use_container_width=True)

            with col[1]:
                st.plotly_chart(interaction_fig, use_container_width=True)

        elif selected == 'Nutrition Analysis':

            st.write("## Nutrition Analysis")

            col = st.columns([0.5 , 0.5])
            oils_analysis = create_oils_stacked_histograms(analyzer , engine)
            cluster_charts_fig = create_nutrition_histograms(analyzer)
            with col[0]:
                st.plotly_chart(oils_analysis)
            with col[1]:
                st.plotly_chart(cluster_charts_fig, use_container_width=True)

        elif selected == 'Cuisine Analysis':

            col = st.columns([0.3, 0.7])

            with col[0]:
                st.markdown('#### Cuisine Analysis')
                cuisine_analysis = create_cuisine_charts(analyzer , engine)
                st.plotly_chart(cuisine_analysis,use_container_width=True)

                st.markdown('#### Top ingredients')
                top_ingredients_cuisine = create_top_ingredients_table(analyzer , engine)
                st.dataframe(top_ingredients_cuisine,use_container_width=True)
            
            with col[1]:
                st.markdown('#### Cuisine Evolution')
                cuisine_evolution = create_cuisine_evolution_charts(analyzer , engine)
                st.plotly_chart(cuisine_evolution,use_container_width=True)
        elif selected == 'Quick recipe analysis':

            st.write("## Quick recipe analysis")

            col = st.columns([0.5 , 0.5])
            quick_recipe_fig = create_proportion_quick_recipe_charts(analyzer, engine)
            interactions_quick_recipe_fig = create_rate_interactions_quick_recipe_charts(analyzer, engine)
            with col[0]:
                st.plotly_chart(quick_recipe_fig, use_container_width=True)
            with col[1]:
                st.plotly_chart(interactions_quick_recipe_fig, use_container_width=True)

        elif selected == 'Free Visualisation':
            st.write("## Tags Analysis")
            col = st.columns([0.8,0.2])
            
            with col[0]:
                set_number = st.slider('Select set of top 10 tags (0 for 1-10, 1 for 11-20, etc.)', 0, 9, 0)
                tags_chart = create_charts(analyzer, set_number)
                with st.container():
                    for i in range(0, 8, 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j < len(tags_chart):
                                with cols[j]:
                                    st.plotly_chart(tags_chart[i+j], use_container_width=True)