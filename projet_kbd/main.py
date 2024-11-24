import streamlit_app
import streamlit as st
import cProfile
import sqlalchemy


engine = sqlalchemy.create_engine('sqlite:////Users/ghalia/Desktop/Telecom IA/P1/Kit Big Data/Projet/projet_KBD/KitBigData/database/streamlit.db')

if __name__ == "__main__":

    profiler = cProfile.Profile()
    profiler.enable()
    app = streamlit_app.run("/Users/ghalia/Desktop/Telecom IA/P1/Kit Big Data/Projet/projet_KBD/KitBigData/Data","RAW_recipes.csv" , "RAW_interactions.csv" , engine)
    profiler.disable()


