from data_analyzer import DataAnalyzer
from data_plotter import DataPlotter
import streamlit as st
from data_loader import Dataloader


class StreamlitApp:

    def __init__(self, path_file , recipe_file, interaction_file):

        self.recipe_file = recipe_file
        self.interaction_file = interaction_file
        self.path_file = path_file

    def load_and_analyze_data(self):

        recipes_loader = Dataloader(self.path_file , self.recipe_file)
        interactions_loader = Dataloader(self.path_file , self.interaction_file)
        data = recipes_loader.merge_recipe_interaction(interactions_loader)
        analyzer = DataAnalyzer(data)
        analyzer.clean_from_outliers()
        return analyzer

    def create_plots(self):

        recipe_interaction_analyzer = self.load_and_analyze_data()
        recipe_interaction_plot = DataPlotter(recipe_interaction_analyzer)
        recipe_fig = recipe_interaction_plot.plot_nb_recipes_per_year()
        interaction_fig = recipe_interaction_plot.plot_nb_interactions_per_year()

        return recipe_fig, interaction_fig
    
    def create_charts(self):

        recipe_interaction_analyzer = self.load_and_analyze_data()
        recipe_plot = DataPlotter(recipe_interaction_analyzer)
        recipe_charts = recipe_plot.plot_pie_chart_tags()
        return recipe_charts

    def run(self):

        recipe_fig, interaction_fig = self.create_plots()

        st.plotly_chart(recipe_fig)

        st.plotly_chart(interaction_fig)

        st.write("## Tags Analysis")

        tags_chart = self.create_charts()

        with st.container():
            for i in range(0, 8, 2):
                cols = st.columns(2)
                for j in range(2):
                    if i+j < len(tags_chart):
                        with cols[j]:
                            st.plotly_chart(tags_chart[i+j], use_container_width=True)