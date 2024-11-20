import pandas as pd
from collections import Counter
import ast
import functools
import os
import json 
import streamlit as st

class DataAnalyzer:
    
    def __init__(self , data):
        
        self.data = data
        
    """
    def clean_from_outliers(self):

        numerical_features = [column for column in self.data.columns if self.data[column].dtype!='object' and column not in ['id' , 'rating', 'user_id' , 'contributor_id' , 'year']]
        for col in numerical_features:
            IQR = self.data[col].quantile(0.75) - self.data[col].quantile(0.25)
            colmax = self.data[col].quantile(0.75) + 3.5 * IQR
            colmin = self.data[col].quantile(0.25) - 3.5 * IQR
            self.data = self.data[ (self.data[col] < colmax) & (self.data[col] > colmin) ]

        return self.data
    
    """
    def high_rating_nutritions(self):
        
        high_rating_year ={}
        NutriList=['cal', 'totalFat', 'sugar', 'sodium', 'protein', 'satFat', 'carbs']

        for year in range(2002 , 2011):
            high_rating = {}
            merged_year_high = self.data[(self.data['year'] == year) & (self.data['rating']>=3)]
            for col in NutriList:
                high_rating[col] = merged_year_high[col].mean()

            high_rating_year[year] = high_rating

        for year , nutritions in high_rating_year.items():
            total = sum(value for key, value in nutritions.items() if key != 'cal')
            for nutrition, value in nutritions.items():
                if nutrition != "cal":
                    high_rating_year[year][nutrition] = (value / total) * 100
        return high_rating_year 
    
    def analyze_oils(self , engine):

        try:
            data = pd.read_sql_table('oils_dataframe', con=engine)
            if not data.empty:
                print('data found')
                return data
        except Exception as e:
            print(f"Failed to load data from database: {e}")

        self.data.drop_duplicates(subset=['id'], inplace=True)
        
        self.data['ingredients'] = self.data['ingredients'].apply(eval)

        year_oil = {}

        for year in range(2002, 2011):
            oil_types = {
                'olive oil': 0,
                'vegetable oil': 0,
                'canola oil': 0,
                'sesame oil': 0,
                'peanut oil': 0,
                'cooking oil': 0,
                'salad oil': 0,
                'oil' : 0,
                'corn oil' : 0,
                'extra virgin olive oil' : 0
            }
            
            df_year = self.data[self.data['year'] == year]
            number_id = df_year['id'].nunique()
            
            for _, row in df_year.iterrows():
                ingredients_set = set(row['ingredients'])
                for oil_type in oil_types.keys():
                    if oil_type in ingredients_set:
                        oil_types[oil_type] += 1
            
            year_oil[year] = {oil: count / number_id for oil, count in oil_types.items()}

        for year, oils in year_oil.items():
            for oil in oils:
                year_oil[year][oil] =  year_oil[year][oil]/sum(oils.values())

        df_oils = pd.DataFrame(year_oil).T.reset_index().rename(columns={'index': 'Year'})
        df_oils = df_oils.melt(id_vars=['Year'], var_name='Oil Type', value_name='Proportion')
        df_oils.to_sql(name='oils_dataframe', con=engine, if_exists='replace')

        return df_oils 

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

        top_commun_year[year] = tag_year.most_common(100)
        
        
        return top_commun_year
    
    def get_top_tag_per_year(self):

        file_path = 'top_tags.json'
        
        if os.path.exists(file_path) :
            with open(file_path , 'r') as file:
                set_number_tags = json.load(file)
        
        else:

            set_number_tags = {}
            for set_number in range(0 , 10):
                top_tags_years = {}
                for year in range(2002 , 2011):
                    tag_year = self.get_top_tags(year)
                    start_idx = set_number * 10
                    end_idx = start_idx + 10 + 1 
                    labels = [k for (k, _) in tag_year[year]][start_idx:end_idx]
                    sizes = [v for (_, v) in tag_year[year]][start_idx:end_idx]
                    top_tags_years[year] = [labels , sizes]
                        
                set_number_tags[set_number] = top_tags_years

            with open(file_path , 'w') as file:
                json.dump(set_number_tags , file)


        return set_number_tags

