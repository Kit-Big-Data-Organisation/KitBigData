import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


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
    
    def plot_recipe_histo_filter_tags(self, selected_tags):
        summary_df = self.data_analyzer.filter_data_by_tags(selected_tags)
        df = pd.DataFrame({
        'Year': summary_df['year'],
        'Percentage': summary_df['percentage']
        })
    
        fig = px.bar(
            df,
            x='Year',
            y='Percentage',
            title='Percentage of Recipes with Selected Tags per Year',
            labels={'Percentage': 'Percentage (%)', 'Year': 'Year'},
            text='Percentage'
        )
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Percentage (%)",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )
        return fig
        