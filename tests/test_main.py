from unittest.mock import patch

def test_main_execution():
    """
    Teste que le fichier main.py s'exécute sans erreurs.

    Ce test moque les fonctions de Streamlit pour éviter tout affichage réel et vérifie
    que le script peut être exécuté sans problème.
    """
    with patch('streamlit.title'), patch('streamlit.write'):
        # Importation et exécution du module principal
        import main
