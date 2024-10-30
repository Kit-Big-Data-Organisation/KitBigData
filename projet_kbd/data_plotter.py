import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


class DataPlotter:

    def __init__(self, data_analyzer):
        self.data_analyzer = data_analyzer

    def plot_nb_interactions_per_year(self):

        x_values, y_values = self.data_analyzer.group_interactions_year()

        df = pd.DataFrame({
            'Year': x_values,
            'Interactions': y_values
        })
        fig = px.line(df, x='Year', y='Interactions', title='Number of Interactions per Year')
        return fig

    def plot_nb_recipes_per_year(self):

        x_values , y_values = self.data_analyzer.group_recipes_year()

        df = pd.DataFrame({
            'Year': x_values,
            'Recipes': y_values
        })
        fig = px.line(df, x='Year', y='Recipes', title='Number of recipes per Year')
        return fig

    def plot_pie_chart_tags(self):

        figs = []
        top_tags_years = self.data_analyzer.get_top_tag_per_year()
        for year in range(2001, 2023):
            if year in top_tags_years:
                labels, values = top_tags_years[year]
                fig = px.pie(values=values, names=labels, title=f'Top 10 tags for Year {year}',
                             labels={'names': 'Tags', 'values': 'Count'})
                figs.append(fig)

        return figs

    def plot_rate_easy_recipes_per_year(self):
        """
    Trace le taux de recettes faciles par année en utilisant Plotly.

    Utilise les données du taux de recettes faciles pour chaque année et crée un graphique interactif
    montrant l'évolution de ce taux.

    Returns:
        plotly.graph_objs._figure.Figure: Le graphique du taux de recettes faciles par année.
    """
        # Récupère le nombre de recettes faciles par année
        easy_recipes_per_year = self.data_analyzer.get_rate_of_quick_recipes_per_year()

        # Prépare les données pour le graphique
        years = sorted(easy_recipes_per_year.keys())
        counts = [easy_recipes_per_year[year] for year in years]

        df = pd.DataFrame({
            'Year': years,
            'Easy Recipes': counts
        })

        # Création du graphique avec Plotly
        fig = px.line(df, x='Year', y='Easy Recipes', title='Number of Easy Recipes per Year')
        return fig