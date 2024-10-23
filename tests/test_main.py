from unittest.mock import patch
from streamlit_utils.streamlit_app import StreamlitApp

def test_streamlit_app_initialization():
    """
    Teste l'initialisation de la classe StreamlitApp.

    Ce test vérifie que l'objet StreamlitApp est correctement initialisé avec
    les fichiers CSV fournis. Les attributs `recipes_file` et `interactions_file`
    doivent contenir les bons noms de fichiers après l'initialisation.
    """
    app = StreamlitApp("RAW_recipes.csv", "RAW_interactions.csv")
    assert app.recipes_file == "RAW_recipes.csv"
    assert app.interactions_file == "RAW_interactions.csv"

def test_streamlit_app_run():
    """
    Teste l'exécution de la méthode `run()` de StreamlitApp.

    Ce test moque les fonctions `streamlit.title` et `streamlit.write` pour éviter
    d'interagir avec l'interface Streamlit réelle. Il vérifie que la méthode `run()`
    de l'application peut s'exécuter sans lever d'exception.
    """
    app = StreamlitApp("RAW_recipes.csv", "RAW_interactions.csv")

    # Mock Streamlit functions to avoid side effects
    with patch('streamlit.title'), patch('streamlit.write'):
        app.run()
