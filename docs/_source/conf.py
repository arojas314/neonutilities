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
import neonutilities

sys.path.insert(0, os.path.abspath('../../..'))


# -- Project information -----------------------------------------------------

project = 'neonutilities'
copyright = '2022, Alex Rojas'
author = 'Alex Rojas'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx_automodapi.automodapi",
    "sphinx_design",
    "autodocsumm",
    "sphinx_markdown_tables",
    "myst_parser",
]
numpydoc_show_class_members = False

autosummary_generate = True  # Turn on sphinx.ext.autosummary

# MyST Docs: https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "colon_fence",
    "linkify",  # Autodetects URL links in Markdown files
]

# Set up mapping for other projects' docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None)
}

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".ipynb_checkpoints", ".vscode", ".git"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_show_sourcelink = False

html_theme_options = {
    "github_url": "https://github.com/arojas314",
    "twitter_url": "https://twitter.com/arojas314",
    "navbar_end": ["navbar-icon-links.html", "search-field.html"],
    "show_toc_level": 1
    # "navigation_with_keys": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static'] # "../images"
html_css_files = ["custom.css"]

# ---------------------
html_sidebars = {}
html_logo = "_static/NEON_image.png"

## Adding Markdown Capability
from recommonmark.parser import CommonMarkParser

source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']

# Set autodoc defaults
autodoc_default_options = {
    "autosummary": True,  # Include a members "table of contents"
    "members": True,  # Document all functions/members
    "special-members": "__init__",
}

"""
IMPORTANT NOTES ABOUT PUBLISHING TO GITHUB PAGES
-----------------------------------------------
1. Must have an empty file called .nojekyll in this directory.
2. Include an index.html file to redirect to the actual html build
   Something like this in that file (yes, only one line)...
        <meta http-equiv="Refresh" content="0;url=_build/html/"/>
3.
"""