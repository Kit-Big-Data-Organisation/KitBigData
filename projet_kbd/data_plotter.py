import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


class DataPlotter:

    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer

    def plot_nb_interactions_per_year(self):

        x_values , y_values = self.data_analyzer.group_interactions_year()

        df = pd.DataFrame({
            'Year': x_values,
            'Interactions': y_values
        })
        fig = px.line(df, x='Year', y='Interactions', title='Number of Interactions per Year')
        return fig
    
    def plot_nb_recipes_per_year(self):

        x_values , y_values = self.data_analyzer.group_interactions_year()

        df = pd.DataFrame({
            'Year': x_values,
            'Recipes': y_values
        })
        fig = px.line(df, x='Year', y='Recipes', title='Number of recipes per Year')
        return fig