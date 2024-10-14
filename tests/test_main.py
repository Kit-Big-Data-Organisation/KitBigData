"""
This module contains unit tests for the main module of the projet_kbd project.

The primary test in this module verifies that the main function prints the
expected success message when executed.
"""

from projet_kbd import main


def test_main_function(capsys):
    """
    Test the main function of the main module.

    This test captures the output of the `main.main()` function and verifies
    that it prints the correct message: "Project is running successfully!".

    Parameters:
    capsys (fixture): Pytest fixture to capture standard output and error
    streams.
    """
    # Exécute la fonction main()
    main.main()

    # Capture l'output imprimé par la fonction
    captured = capsys.readouterr()

    # Vérifie que l'output correspond au message attendu
    assert captured.out == "Project is running successfully!\n"
