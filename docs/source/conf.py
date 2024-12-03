# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../projet_kbd'))

project = 'Projet Kit Big Data'
copyright = '2024, HARIRI Safae, NOUNAH Nour, ROQAI CHAOUI Ghalia'
author = 'HARIRI Safae, NOUNAH Nour, ROQAI CHAOUI Ghalia'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Générer automatiquement la documentation depuis les docstrings
    "sphinx.ext.napoleon",  # Support des docstrings au format Google et NumPy
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
