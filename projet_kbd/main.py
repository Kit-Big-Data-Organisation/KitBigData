from streamlit_app import StreamlitApp
import streamlit as st


# Titre de la page
st.title("Projet Kit Big Data")

# Exécution des différentes parties de l'application
if __name__ == "__main__":

    app = StreamlitApp("RAW_recipes.csv" , "RAW_interactions.csv")
    app.run()
    print('----start running for pull----')
    print('----start running for pull----')

