import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
    
    def plot_pie_chart_tags(self , set_number):

        figs = []
        top_tags_years = self.data_analyzer.get_top_tag_per_year()
        for year in range(2001, 2023):
            if str(year) in top_tags_years[str(set_number)]:
                labels, values = top_tags_years[str(set_number)][str(year)]
                fig = px.pie(values=values, names=labels, title=f'Top 10 tags for Year {year}', 
                             labels={'names': 'Tags', 'values': 'Count'})
                figs.append(fig)
        
        return figs


    def plot_high_rating_nutrition(self):

        high_rating_year  = self.data_analyzer.high_rating_nutritions()
        NutriList=['cal', 'totalFat', 'sugar', 'sodium', 'protein', 'satFat', 'carbs']

        fig = make_subplots(rows=len(NutriList), cols=1, shared_xaxes=True, vertical_spacing=0.02, subplot_titles=NutriList)

        for i, nutrient in enumerate(NutriList):
            years = sorted(high_rating_year.keys())
            fig.add_trace(
                go.Bar(x=years, y=[high_rating_year[year][nutrient] for year in years], name='High Rating', marker_color='blue'),
                row=i + 1, col=1
            )
        fig.update_layout(
            height=300 * len(NutriList),  
            showlegend=True,
            title_text="Comparaison annuelle des valeurs nutritionnelles"
        )

        return fig

    def plot_oil_analysis(self , engine):

        custom_palette = {
            'olive oil': '#8a3ab9', 
            'vegetable oil': '#bc2a8d',
            'canola oil': '#e95950',
            'sesame oil': '#fccc63',
            'peanut oil': '#4c68d7',
            'cooking oil': '#30cfd0',
            'salad oil': '#6a67ce',
            'oil': '#48cfad',
            'corn oil': '#a8e063',
            'extra virgin olive oil': '#fd9644'
        }

        df_oils = self.data_analyzer.analyze_oils(engine)
        df_oils['color'] = df_oils['Oil Type'].map(custom_palette)

        fig = px.bar(df_oils, x='Year', y='Proportion', color='Oil Type',
                    color_discrete_map=custom_palette,
                    title='Proportion of Different Oils by Year, Ordered by Total Proportion')
        
        fig.update_layout(xaxis_title='Year',
                        yaxis_title='Proportion',
                        legend_title='Oil Type')
        return fig

    def plot_cuisines_analysis(self , engine):

        df_cuisine = self.data_analyzer.analyze_cuisines(engine)

        labels , sizes = df_cuisine['Cuisine'].tolist() , df_cuisine['Proportion'].tolist()

        fig = px.pie(values=sizes, names=labels)

        return fig
    
    def plot_cuisines_evolution(self , engine):

        df_cuisine_evolution = self.data_analyzer.cuisine_evolution(engine)
        num_rows = 2
        num_cols = 4
        fig = make_subplots(rows=num_rows, cols=num_cols, subplot_titles=[f'{cuisine} Cuisine' for cuisine in df_cuisine_evolution.columns if cuisine != 'Year'])

        idx = 1

        for cuisine in df_cuisine_evolution.columns:
             
            if cuisine != 'Year':
           
                row = (idx - 1) // num_cols + 1
                col = (idx - 1) % num_cols + 1

                trace = go.Scatter(x=df_cuisine_evolution.index, y=df_cuisine_evolution[cuisine], mode='lines', name=cuisine)
                fig.add_trace(trace, row=row, col=col)

                idx += 1

        fig.update_layout(height=900, width=1200)
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Proportion")

        return fig
    
    def plot_top_ingredients(self , engine):

        df_top_ingredients = self.data_analyzer.top_commun_ingredients(engine)
        print(df_top_ingredients)
        return df_top_ingredients