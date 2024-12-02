import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import re


class CommentAnalyzer:
    def __init__(self, comments_df):
        self.comments = comments_df

    def clean_comments(self):
        """
        Nettoyer les commentaires pour faciliter les analyses textuelles.
        """
        self.comments['cleaned'] = self.comments['review'].str.lower().str.replace(r'[^\w\s]', '', regex=True).str.strip()

    def sentiment_analysis(self):
        """
        Analyse des sentiments pour les commentaires.
        """
        self.comments['polarity'] = self.comments['cleaned'].apply(lambda x: TextBlob(x).sentiment.polarity)
        return self.comments

    def generate_word_frequencies(self, engine, max_features=100):
        """
        Calcule les fréquences des mots dans les commentaires.
        :param stop_words: Liste des mots à ignorer (par défaut en anglais).
        :param max_features: Nombre maximum de mots fréquents à retenir.
        :return: Un dictionnaire avec les mots et leurs fréquences.
        """
        # Vérifier si les données existent déjà dans la base de données
        try:
            stored_data = pd.read_sql_table('word_frequencies', con=engine)
            if not stored_data.empty:
                print("Word frequencies found in database.")
                return dict(zip(stored_data['word'], stored_data['frequency']))
        except Exception as e:
            print(f"Table not found or error loading data: {e}")

        # Stop words personnalisés
        custom_stop_words = ['recipe', 'used', 'thanks', 'make', 'just', 'really', 'didn', 'bit', 'great', 'good', 'added']
        # Fusionner 'english' (stop words par défaut) avec les stop words personnalisés
        all_stop_words = list(ENGLISH_STOP_WORDS) + custom_stop_words
        vectorizer = CountVectorizer(stop_words=all_stop_words, max_features=max_features)
        word_matrix = vectorizer.fit_transform(self.comments['cleaned'])
        word_frequencies = dict(zip(vectorizer.get_feature_names_out(), word_matrix.sum(axis=0).A1))

        # Enregistrer les résultats dans la base de données
        try:
            print("Saving word frequencies to database.")
            word_frequencies_df = pd.DataFrame(list(word_frequencies.items()), columns=['word', 'frequency'])
            word_frequencies_df.to_sql(name='word_frequencies', con=engine, if_exists='replace', index=False)
            print("Word frequencies saved successfully.")
        except Exception as e:
            print(f"Failed to save word frequencies to database: {e}")
            
        return word_frequencies
    
    

    def generate_word_frequencies_associated_to_time(self, engine, max_features=10):

        # Vérifier si les données existent déjà dans la base de données
        try:
            stored_data = pd.read_sql_table('word_frequencies_time', con=engine)
            if not stored_data.empty:
                print("Word frequencies for 'time' found in database.")
                return dict(zip(stored_data['phrase'], stored_data['frequency']))
        except Exception as e:
            print(f"Table not found or error loading data: {e}")

        def exclude_phrases_with_words(contexts, words_to_exclude):
            """
            Exclut les phrases contenant des mots ou expressions spécifiques.
            
            :param contexts: Liste de phrases contextuelles.
            :param words_to_exclude: Liste de mots ou expressions à exclure.
            :return: Liste filtrée.
            """
            return [
                context for context in contexts
                if not any(word in context.lower() for word in words_to_exclude)
            ]

        def extract_context(text, target_word="time", window=6):
            """
            Extrait les `window` mots avant et après le mot cible dans un texte.
            """
            words = text.split()
            if target_word in words:
                index = words.index(target_word)
                start = max(index - window, 0)
                end = min(index + window + 1, len(words))
                return ' '.join(words[start:end])
            return None

        # Appliquer la fonction pour extraire le contexte
        self.comments['time_context'] = self.comments['cleaned'].apply(
            lambda x: extract_context(x, target_word="time", window=4)
        )

        # Filtrer les lignes où un contexte a été trouvé
        time_contexts = self.comments[self.comments['time_context'].notnull()]['time_context']

        # Exclure les phrases contenant 'ill' ou 'im going'
        words_to_exclude = ["ill", "im going", "think time"]
        filtered_time_contexts = exclude_phrases_with_words(time_contexts, words_to_exclude)

        custom_stop_words = ['recipe', 'used', 'thanks', 'make', 'just', 'really', 'didn', 'bit', 'great', 'good', 'added']
        # Fusionner 'english' (stop words par défaut) avec les stop words personnalisés
        all_stop_words = list(ENGLISH_STOP_WORDS) + custom_stop_words

        # Initialiser le vectorizer avec les phrases filtrées
        vectorizer = CountVectorizer(stop_words=all_stop_words, ngram_range=(3, 4), max_features=10)
        word_matrix = vectorizer.fit_transform(filtered_time_contexts)

        # Associer les mots et leurs fréquences
        word_frequencies = dict(zip(vectorizer.get_feature_names_out(), word_matrix.sum(axis=0).A1))

        # Afficher pour validation
        print(word_frequencies)
        print(type(word_frequencies))

        # Trier les mots les plus fréquents
        sorted_contexts = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
        top_contexts = dict(sorted_contexts[:max_features])

        # Enregistrer les résultats dans la base de données
        try:
            print("Saving word frequencies to database.")
            word_frequencies_df = pd.DataFrame(list(word_frequencies.items()), columns=['phrase', 'frequency'])
            word_frequencies_df.to_sql(name='word_frequencies_time', con=engine, if_exists='replace', index=False)
            print("Word frequencies saved successfully.")
        except Exception as e:
            print(f"Failed to save word frequencies to database: {e}")

        # Retourner les n mots les plus fréquents (au format liste de tuples)
        return top_contexts

