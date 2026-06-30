# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import datetime
from importlib.metadata import PackageNotFoundError, version as package_version

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "scenariocompass"
copyright = f"{datetime.now().year}, IIASA"
author = "Scenario Services team, ECE program, IIASA"

try:
    release = package_version("scenariocompass")
except PackageNotFoundError:
    release = "0.0.0"

# The short X.Y version.
version = release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_click",
]

templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
description = "A Python package for working with IAMC-style scenario data"

html_theme_options = {
    "logo": "scenariocompass-logo.png",
    "logo_name": True,
    "description": description,
    "page_width": "1100px",
    "sidebar_width": "240px",
    "github_button": True,
    "github_user": "iamconsortium",
    "github_repo": "scenariocompass",
    "code_bg": "#EEE",
    "note_bg": "#EEE",
    "seealso_bg": "#EEE",
    "admonition_xref_bg": "#EEE",
    "admonition_xref_border": "#444",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pyam": ("https://pyam-iamc.readthedocs.io/en/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# Autodoc configuration
autodoc_typehints = "none"

# Prolog for all rst files
rst_prolog = """

.. |br| raw:: html

    <br>

"""
