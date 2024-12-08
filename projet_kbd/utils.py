import sqlite3
import streamlit as st
relevant_cuisines = [
    "asian",
    "mexican",
    "italian",
    "african",
    "greek",
    "american",
]

oil_types = {
    "olive oil": 0,
    "vegetable oil": 0,
    "canola oil": 0,
    "sesame oil": 0,
    "peanut oil": 0,
    "cooking oil": 0,
    "salad oil": 0,
    "oil": 0,
    "corn oil": 0,
    "extra virgin olive oil": 0,
}

custom_palette = {
    "olive oil": "#8a3ab9",
    "vegetable oil": "#bc2a8d",
    "canola oil": "#e95950",
    "sesame oil": "#fccc63",
    "peanut oil": "#4c68d7",
    "cooking oil": "#30cfd0",
    "salad oil": "#6a67ce",
    "oil": "#48cfad",
    "corn oil": "#a8e063",
    "extra virgin olive oil": "#fd9644",
}


def determine_cuisine(tags):
    """
    Determines the cuisine of a recipe based on tags.

    Parameters:
        tags (list of str): The tags associated with a recipe.

    Returns:
        str: The determined cuisine, or 'other' if no cuisine matches.
    """
    cuisines = {
        "asian": 0,
        "mexican": 0,
        "italian": 0,
        "african": 0,
        "american": 0,
        "french": 0,
        "greek": 0,
        "indian": 0,
    }

    for cuisine in cuisines.keys():
        if cuisine in tags:
            return cuisine
    return "other"


def highlight_cells(val):
    "to highlight specific cells in dataframe figure"

    if val == "parmesan cheese":
        return "background-color: red"
    elif val == "olive oil":
        return "background-color: lightgreen"
    elif val in ["chili powder", "flour tortillas"]:
        return "background-color: orange"
    elif val in ["feta cheese", "dried oregano"]:
        return "background-color: lightblue"
    elif val == "soy sauce":
        return "background-color: lightpink"
    else:
        return ""
    
def create_top_tags_database(DB_PATH , set_number_tags):

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS top_tags (
            set_number INTEGER,
            year INTEGER,
            label TEXT,
            size REAL
        )
        """)

        for set_number, top_tags_years in set_number_tags.items():
            for year, data in top_tags_years.items():
                labels, sizes = data
                for label, size in zip(labels, sizes):
                    cursor.execute("""
                    INSERT INTO top_tags (set_number, year, label, size)
                    VALUES (?, ?, ?, ?)
                    """, (set_number, year, label, size))

        conn.commit()
        conn.close()

# Helper function to render justified content
def render_justified_text(content):
    st.markdown(f"<div class='justified'>{content}</div>", unsafe_allow_html=True)