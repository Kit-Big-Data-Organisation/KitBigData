import pandas as pd
from collections import Counter
import ast
from logger_config import logger
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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
        indices , values = grouped_interactions.index, grouped_interactions.values

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

    def get_rate_of_quick_recipes_per_year(self):
        """
        Calcule le taux de recettes rapides par année.

        Cette méthode calcule le pourcentage de recettes rapides pour chaque année dans les données.
        Une recette est considérée comme "rapide" si elle contient au moins un des tags fournis dans
        `quick_tags`. Le taux est calculé en divisant le nombre de recettes rapides par le nombre total
        de recettes pour l'année, puis multiplié par 100 pour obtenir un pourcentage.

        Args:
            quick_tags (list of str): Liste de tags considérés comme représentant des recettes rapides
                                      (par exemple, '15-minutes-or-less', 'easy', etc.).

        Returns:
            dict: Un dictionnaire où les clés sont les années et les valeurs sont les taux de recettes
                  rapides pour chaque année, exprimés en pourcentage.

        Raises:
            ValueError: Si le format des tags n'est pas une liste.
            SyntaxError: Si les tags ne peuvent pas être évalués correctement avec `ast.literal_eval`.

        """
        quick_tags = ['15-minutes-or-less', '30-minutes-or-less', 'easy', 'weeknight', 'one-dish-meal', '3-steps-or-less']
        quick_recipes_rate_per_year = {}
        logger.info("Calcul du taux de recettes rapides en cours")

        for year in self.data['year'].unique():
            yearly_data = self.data[self.data['year'] == year]
            total_recipes = len(yearly_data)  # Nombre total de recettes pour l'année
            quick_recipe_count = 0

            for tags in yearly_data['tags']:
                try:
                    tags_list = ast.literal_eval(tags)
                    if not isinstance(tags_list, list):
                        raise ValueError("Le format des tags n'est pas une liste")

                    # Compte les recettes rapides
                    if any(tag in tags_list for tag in quick_tags):
                        quick_recipe_count += 1

                except (ValueError, SyntaxError) as e:
                    logger.error(f"Erreur de format de tags pour l'année {year}: {e}")
                except Exception as e:
                    logger.error(f"Erreur inattendue lors du traitement des tags pour l'année {year}: {e}")

            # Calcul du taux de recettes rapides
            quick_recipe_rate = (quick_recipe_count / total_recipes * 100) if total_recipes > 0 else 0
            quick_recipes_rate_per_year[year] = quick_recipe_rate

        logger.info("Calcul du taux de recettes rapides terminé avec succès")

        return quick_recipes_rate_per_year

    def get_top_recipes_by_interactions(self, start_year: int = 2010, end_year: int = 2015, top_n: int = 10):
        top_recipes_per_year = {}

        for year in range(start_year, end_year + 1):
            yearly_data = self.data[self.data['year'] == year]
            if 'interactions' in yearly_data.columns:
                top_recipes = yearly_data.nlargest(top_n, 'interactions')[['id', 'interactions']]
                top_recipes_per_year[year] = top_recipes.set_index('id')['interactions'].to_dict()
            else:
                logger.warning(f"La colonne 'interactions' n'est pas présente dans les données pour l'année {year}")

        return top_recipes_per_year

    # Comments analysis

    def clean_comment(comment):
        return comment.lower()

    def analyze_sentiment(comment):
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(comment)
        return scores['neg']  # Retourne le score de négativité

    def analyze_comments(dataframe, comment_column):
        dataframe['cleaned_comment'] = dataframe[comment_column].apply(clean_comment)
        dataframe['negativity_score'] = dataframe['cleaned_comment'].apply(analyze_sentiment)
        return dataframe