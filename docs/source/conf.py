# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Ajoutez le chemin absolu du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('../../'))  # Chemin vers la racine du projet

project = 'Projet Kit Big Data'
copyright = '2024, HARIRI Safae, NOUNAH Nour, ROQAI CHAOUI Ghalia'
author = 'HARIRI Safae, NOUNAH Nour, ROQAI CHAOUI Ghalia'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Générer la documentation depuis les docstrings
    "sphinx.ext.napoleon",  # Support des docstrings au format Google et NumPy
    "sphinx.ext.viewcode",  # Lien vers le code source
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
