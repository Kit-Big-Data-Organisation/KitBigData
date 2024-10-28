import pandas as pd
from collections import Counter
import ast

class DataAnalyzer:
    
    def __init__(self , data):
        
        self.data = data
        

    def clean_from_outliers(self):

        numerical_features = [column for column in self.data.columns if self.data[column].dtype!='object' and column not in ['id' , 'rating', 'user_id' , 'contributor_id' , 'year']]
        for col in numerical_features:
            IQR = self.data[col].quantile(0.75) - self.data[col].quantile(0.25)
            colmax = self.data[col].quantile(0.75) + 1.5 * IQR
            colmin = self.data[col].quantile(0.25) - 1.5 * IQR
            self.data = self.data[ (self.data[col] < colmax) & (self.data[col] > colmin) ]

        return self.data
    

    def group_interactions_year(self):
        
        grouped_interactions = self.data.groupby('year')['review'].count()
        indices , values = grouped_interactions.index , grouped_interactions.values

        return indices ,values

    def group_recipes_year(self):

        grouped_recipes = self.data.groupby('year')['id'].nunique()
        indices , values = grouped_recipes.index , grouped_recipes.values

        return indices , values


    def get_tags(self , year):

        tags = Counter()
        current = self.data
        current = current[current['year'] == year]
        tags_df = current['tags']

        for row in tags_df:
            row = ast.literal_eval(row)   
            tags += Counter(row)
            
        return tags


    def get_top_tags(self , year):

        top_commun_year = {}

        tag_year = self.get_tags(year)

        top_commun_year[year] = tag_year.most_common(40)
        
        
        return top_commun_year
    

    def get_top_tag_per_year(self):

        top_tags_years = {}
        for year in range(2002 , 2011):
            tag_year = self.get_top_tags(year)
            labels = [k for (k, _) in tag_year[year]][11:21]
            sizes = [v for (_, v) in tag_year[year]][11:21]
            top_tags_years[year] = [labels , sizes]
        
        return top_tags_years