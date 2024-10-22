from data_analyzer import DataAnalyzer
from data_plotter import DataPlotter
import streamlit as st
from data_loader import Dataloader

class StreamlitApp:
    def __init__(self, recipe_file, interaction_file):
        self.recipe_file = recipe_file
        self.interaction_file = interaction_file

    def load_and_analyze_data(self, filename):
        loader = Dataloader(filename)
        data = loader.loader()
        analyzer = DataAnalyzer(data)
        return analyzer

    def create_plots(self):

        # Creating plot for recipes
        recipe_analyzer = self.load_and_analyze_data(self.recipe_file)
        recipe_plot = DataPlotter(recipe_analyzer)
        recipe_fig = recipe_plot.plot_nb_recipes_per_year()

        # Creating plot for interactions
        interaction_analyzer = self.load_and_analyze_data(self.interaction_file)
        interaction_plot = DataPlotter(interaction_analyzer)
        interaction_fig = interaction_plot.plot_nb_interactions_per_year()

        return recipe_fig, interaction_fig

    def run(self):

        recipe_fig, interaction_fig = self.create_plots()

        st.write("## Recipe Data")
        st.plotly_chart(recipe_fig)

        st.write("## Interaction Data")
        st.plotly_chart(interaction_fig)
