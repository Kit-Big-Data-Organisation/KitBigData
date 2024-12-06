import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils


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
        

    def plot_oil_analysis(self , engine):

        custom_palette = utils.custom_palette

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
        fig = make_subplots(rows=num_rows, cols=num_cols, 
                            subplot_titles=[f'{cuisine} Cuisine' for cuisine in df_cuisine_evolution.columns if cuisine != 'Year'],
                            vertical_spacing = 0.12,
                            horizontal_spacing = 0.1)

        idx = 1

        for cuisine in df_cuisine_evolution.columns:
             
            if cuisine != 'Year':
           
                row = (idx - 1) // num_cols + 1
                col = (idx - 1) % num_cols + 1

                trace = go.Scatter(x=df_cuisine_evolution['Year'], y=df_cuisine_evolution[cuisine], mode='lines', name=cuisine)
                fig.add_trace(trace, row=row, col=col)

                idx += 1

        fig.update_layout(
            height=800,
            width=800,
            showlegend=False,
            title_text="Cuisine Proportions Over Time"
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Proportion")

        return fig
    
    def plot_top_ingredients(self , engine):

        df_top_ingredients = self.data_analyzer.top_commun_ingredients(engine)
        print('top ingredients')
        print(df_top_ingredients)
        return df_top_ingredients
    
    def plot_calories_analysis(self , engine):
    
        df_calories = self.data_analyzer.analyse_cuisine_nutritions(engine)
        df_calories.sort_values(by = 'cal' ,inplace = True)        
        fig = px.bar(
            df_calories,
            x= 'cal',  
            y= df_calories['cuisine'],   
            orientation='h',
            color = df_calories['cuisine'],
            title="Calories Mean by Cuisine",
            labels={'cal': 'Calories Mean', 'cuisine': 'Cuisine'} 
        )    
        return fig
    
    def plot_cuisine_time_analysis(self , engine):
        df_times = self.data_analyzer.analyse_cuisine_nutritions(engine)
        df_times.sort_values(by = 'minutes' ,inplace = True)
        
        fig = px.bar(
            df_times,
            x=df_times['cuisine'],  
            y='minutes',
            color = df_times['cuisine'],
            title="Mean time of recipes by Cuisine in minutes",
            labels={'minutes': 'Mean minutes', 'cuisine': 'Cuisine'} 
        )    
        return fig
    
    def plot_cuisine_nutritions(self , engine):
        df_nutritions = self.data_analyzer.analyse_cuisine_nutritions(engine)
        nutritions = [column for column in df_nutritions.columns if column not in ['minutes' , 'cal']]
        df_nutritions = df_nutritions[nutritions]
        final_long = df_nutritions.reset_index().melt(id_vars='cuisine', var_name='nutrient', value_name='value')
        fig = px.bar(
            final_long,
            x ='cuisine',
            y = 'value',
            color = 'nutrient',
            title= "Nutritional content by Cuisine in PDV",
            labels={'value': 'PDV(%)', 'nutrient': 'Nutrient Type'},
            barmode = 'group'
        )    
        return fig

    def plot_inractions_ratings(self, engine):
        aggregated = self.data_analyzer.analyse_interactions_ratings(engine)
        fig = px.scatter(
        aggregated,
        x='avg_rating',
        y='num_ratings',
        color='mean_minutes',
        title="Average Rating vs Number of Ratings",
        labels={'avg_rating': 'Average Rating Score', 'num_ratings': 'Number of Ratings', 'mean_minutes': 'Cooking Time (minutes)'},
        color_continuous_scale='Turbo',
        size_max=10
    )
        fig.update_traces(marker=dict(size=8))
        return fig 
    
    def plot_user_interactions(self, engine):
        fig = go.Figure()
        aggregated = self.data_analyzer.analyse_user_intractions(engine)
        fig.add_trace(go.Scatter(
            x=aggregated['days_since_submission'],
            y=aggregated['num_interactions'],
            mode='markers',
            name='Number of Interactions',
            marker=dict(color='skyblue', size=10),
            xaxis='x1',
            yaxis='y1'
        ))

        fig.add_trace(go.Scatter(
            x=aggregated['days_since_submission'],
            y=aggregated['avg_rating'],
            mode='markers',
            name='Average Rating',
            marker=dict(color='orange', size=10),
            xaxis='x2',
            yaxis='y2'
        ))

        fig.update_layout(
            title="Interaction Analysis Over Time",
            xaxis=dict(title="Days Since Submission", domain=[0, 1], anchor='y1'),
            xaxis2=dict(title="Days Since Submission", domain=[0, 1], anchor='y2'),
            yaxis=dict(title="Number of Interactions", anchor='x1'),
            yaxis2=dict(title="Average Rating", anchor='x2'),
            grid=dict(rows=2, columns=1, pattern="independent"),
            height=600  
        )

        return fig
    
    def plot_average_steps_rating(self, engine):
        grouped = self.data_analyzer.analyse_average_steps_rating(engine)
        fig = go.Figure()

        # Bar plot for average steps
        fig.add_trace(go.Bar(
            x=grouped['year'],
            y=grouped['avg_steps'],
            name='Average Steps',
            marker=dict(color='skyblue'),
            text=grouped['avg_rating'].round(2),  # Add average rating as text on top of each bar
            textposition='outside',
            hoverinfo='x+y+text'
        ))

        # Layout configuration
        fig.update_layout(
            title="Average Steps and Rating per Year",
            xaxis_title="Year",
            yaxis_title="Average Number of Steps",
            yaxis=dict(title="Average Steps"),
            xaxis=dict(
                tickmode='array',
                tickvals=grouped['year'],  # Set x-axis tick values to the years
                ticktext=grouped['year'].astype(str),  # Display the years as labels
                title_text='Year'  # Label for the x-axis
            ),
            showlegend=False,
            height=600
        )
        return fig

    
