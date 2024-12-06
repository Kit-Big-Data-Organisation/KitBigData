import streamlit_app
import streamlit as st
import cProfile
import sqlalchemy


# engine = sqlalchemy.create_engine('sqlite:////Users/user/Desktop/KBD Project/KitBigData/database/streamlit.db')
engine = sqlalchemy.create_engine('sqlite:////Users/t/Documents/MasterTelecom/KitBigData/KitBigData/database/streamlit.db')

if __name__ == "__main__":

    profiler = cProfile.Profile()
    profiler.enable()
    app = streamlit_app.run("/Users/t/Documents/MasterTelecom/KitBigData/KitBigData/Data/recipe","RAW_recipes.csv" , "RAW_interactions.csv" , engine)
    profiler.disable()
   
   