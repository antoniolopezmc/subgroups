# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))
# IMPORTANT: since we added "../../" directory to the first position of the path, 'subgroups' module is the one located in that directory, 
#            not in the python modules directory.
import subgroups
from datetime import date

# -- Project information -----------------------------------------------------

project = 'subgroups'
current_year = date.today().year
copyright = str(current_year) + ', Antonio López Martínez-Carrasco'
author = 'Antonio López Martínez-Carrasco'

# The full version, including alpha/beta/rc tags
release = subgroups.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    #'sphinx.ext.viewcode', # Uncomment to view the button "source" in the generated documentation.
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for 'sphinx_autodoc_typehints'.

typehints_fully_qualified = True
