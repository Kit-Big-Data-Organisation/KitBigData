from streamlit_app import StreamlitApp
import streamlit as st


# Titre de la page
st.title("Projet Kit Big Data")

# Exécution des différentes parties de l'application
if __name__ == "__main__":

    app = StreamlitApp("/Users/user/Desktop/KBD Project/KitBigData/Data","RAW_recipes.csv" , "RAW_interactions.csv")
    app.run()
   

