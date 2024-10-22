import pandas as pd


class DataAnalyzer:
    
    def __init__(self , data):
        
        self.data = data

    def group_interactions_year(self):
        
        if  'user_id' in self.data.columns:
            grouped_interactions = self.data.groupby('year')['user_id'].count()
            indices , values = grouped_interactions.index , grouped_interactions.values


        if  'id' in self.data.columns:
            grouped_recipes = self.data.groupby('year')['id'].count()
            indices , values = grouped_recipes.index , grouped_recipes.values

        return indices , values