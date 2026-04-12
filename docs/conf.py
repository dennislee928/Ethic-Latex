# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../simulation'))

# -- Project information -----------------------------------------------------

project = 'Ethical Riemann Hypothesis (ERH) SDK'
copyright = '2024, Ethical AI Research Team'
author = 'Ethical AI Research Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

# Napoleon settings for NumPy-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

rst_prolog = """
.. |Δ| replace:: ``|Δ|``
.. |E(x)| replace:: ``|E(x)|``
.. |α - 0.5| replace:: ``|α - 0.5|``
.. |E(x,t)| replace:: ``|E(x,t)|``
.. |Δ(a)| replace:: ``|Δ(a)|``
"""
