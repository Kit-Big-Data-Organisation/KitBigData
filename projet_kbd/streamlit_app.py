from data_analyzer import DataAnalyzer
from data_plotter import DataPlotter
import streamlit as st
from data_loader import Dataloader


class StreamlitApp:

    def __init__(self, path_file , recipe_file, interaction_file):

        self.recipe_file = recipe_file
        self.interaction_file = interaction_file
        self.path_file = path_file

    def load_recipe_data(self):
        recipes_loader = Dataloader(self.path_file , self.recipe_file)
        recipes = recipes_loader.load()
        recipes = recipes_loader.add_year(recipes)
        recipe_analyzer = DataAnalyzer(recipes)
        recipe_analyzer.clean_from_outliers()
        return recipe_analyzer
    

    def load_interactions_data(self):
        interactions_loader = Dataloader(self.path_file , self.interaction_file)
        interactions = interactions_loader.load()
        interactions = interactions_loader.add_year(interactions)
        interaction_analyzer = DataAnalyzer(interactions)
        interaction_analyzer.clean_from_outliers()
        return interaction_analyzer


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
    
    def create_recepies_tags_histogram(self, selected_tags):
        recipe_analyzer = self.load_recipe_data() 
        recipe_plot = DataPlotter(recipe_analyzer)
        recipe_histo = recipe_plot.plot_recipe_histo_filter_tags(selected_tags)
        return recipe_histo


    def create_interactions_tags_histogram(self, selected_tags):
        recipe_interaction_analyzer = self.load_and_analyze_data()
        recipe_interaction_plot = DataPlotter(recipe_interaction_analyzer)
        recipe_interaction_histo = recipe_interaction_plot.plot_recipe_histo_filter_tags(selected_tags)
        return recipe_interaction_histo

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

        st.write("## Tags Analysis Recipes")
        available_tags = ["healthy", "low-in-something", "low-cholesterol", "low-calorie", "healthy-2", "low-fat", "low-saturated-fat", "low-sugar", "vegan"]
        selected_tags = [tag for tag in available_tags if st.checkbox(tag, key=f"recipes_{tag}")]
        if selected_tags:
            recepies_tags_fig = self.create_recepies_tags_histogram(selected_tags)
            st.plotly_chart(recepies_tags_fig)
        else:
            st.write("No tags selected yet")

        st.write("## Tags Analysis Interactions")
        available_tags_interactions = ["healthy", "low-in-something", "low-cholesterol", "low-calorie", "healthy-2", "low-fat", "low-saturated-fat", "low-sugar", "vegan"]
        selected_tags_interactions = [tag for tag in available_tags_interactions if st.checkbox(tag, key=f"interactions_{tag}")]
        if selected_tags_interactions:
            interactions_tags_fig = self.create_interactions_tags_histogram(selected_tags_interactions)
            st.plotly_chart(interactions_tags_fig)
        else:
            st.write("No tags selected yet")

