# Configuration file for the Sphinx documentation builder.
# HFF Survey Plugin Documentation

import os
import sys

# -- Project information -----------------------------------------------------

project = 'HFF Survey Plugin'
copyright = '2024-2026, Honor Frost Foundation'
author = 'Enzo Cocca'
release = '4.1.x'
version = '4.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',           # Support for Markdown
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

# MyST parser configuration for Markdown
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "tasklist",
]

# Templates path
templates_path = ['_templates']

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document
master_doc = 'index'

# Patterns to exclude
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for LaTeX/PDF output --------------------------------------------

latex_engine = 'xelatex'

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'fontpkg': r'''
        \usepackage{fontspec}
    ''',
    'preamble': r'''
        \usepackage{longtable}
        \usepackage{booktabs}
        \setcounter{tocdepth}{2}
    ''',
    'figure_align': 'htbp',
    'extraclassoptions': 'openany,oneside',
}

# Grouping the document tree into LaTeX files
# Default to English - will be overridden in setup() for Arabic builds
latex_documents = [
    ('index', 'HFF_Documentation_EN.tex', 'HFF Survey Plugin Documentation',
     'Enzo Cocca', 'manual'),
]

# -- Options for multilingual support ----------------------------------------

# Language settings
language = 'en'

# Locales for translation
locale_dirs = ['locale/']
gettext_compact = False

# -- Custom configuration for Arabic documentation ---------------------------

def setup(app):
    app.add_css_file('custom.css')

    # Dynamically update latex_documents based on master_doc
    # This runs after Sphinx processes -D options
    def update_latex_docs(app, config):
        if config.master_doc == 'index_ar':
            config.latex_documents = [
                ('index_ar', 'HFF_Documentation_AR.tex', 'وثائق HFF Survey Plugin',
                 'Enzo Cocca', 'manual'),
            ]

    app.connect('config-inited', update_latex_docs)
