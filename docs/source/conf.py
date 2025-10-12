# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

print("PYTHONPATH used by Sphinx:", sys.path[0])


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DHNpype'
copyright = '2025, Marko Keber'
author = 'Marko Keber'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.napoleon',                                                     # For Google/NumPy-style docstrings
    'sphinx_autodoc_typehints',                                                # Show type hints in docs
    'myst_parser',                                                             # For Markdown files like README.md
    'sphinx.ext.viewcode'
    #'nbsphinx',                                                                # For Jupyter notebooks (optional)
]

templates_path = ['_templates']
exclude_patterns = []

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


#html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']