# Configuration file for Arabic Lebanese documentation
# HFF Survey Plugin Documentation - Arabic Lebanese Version

import os
import sys

# -- Project information -----------------------------------------------------

project = 'HFF Survey Plugin - العربية اللبنانية'
copyright = '2024-2026, مؤسسة هونور فروست'
author = 'إنزو كوكا'
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
master_doc = 'index_ar'

# Patterns to exclude
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'tutorials/en/*']

# The name of the Pygments (syntax highlighting) style to use
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for LaTeX/PDF output --------------------------------------------

latex_engine = 'xelatex'  # Required for Arabic support

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'babel': '',  # Disable babel for polyglossia
    'fontpkg': r'''
        \usepackage{fontspec}
        \usepackage{polyglossia}
        \setmainlanguage[numerals=maghrib]{arabic}
        \setotherlanguage{english}
        \newfontfamily\arabicfont[Script=Arabic,Scale=1.2]{Amiri}
        \newfontfamily\englishfont{DejaVu Sans}
    ''',
    'preamble': r'''
        \usepackage{bidi}
        \usepackage{graphicx}
        \usepackage{longtable}
        \usepackage{booktabs}
        \setcounter{tocdepth}{2}
        % Right-to-left text direction for Arabic
        \setRTL
    ''',
    'figure_align': 'htbp',
    'extraclassoptions': 'openany,oneside',
    'maketitle': r'''
        \begin{titlepage}
        \begin{center}
        \vspace*{2cm}
        {\Huge\bfseries HFF Survey Plugin\\[0.5cm]}
        {\Large وثائق البرنامج المساعد\\[2cm]}
        {\large مؤسسة هونور فروست\\[0.3cm]}
        {\large الإصدار 4.1.x\\[3cm]}
        \today
        \end{center}
        \end{titlepage}
    ''',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    ('index_ar', 'HFF_Documentation_AR.tex', 'وثائق HFF Survey Plugin',
     'إنزو كوكا', 'manual'),
]

# -- Language settings -------------------------------------------------------

language = 'ar'

# Locales for translation
locale_dirs = ['locale/']
gettext_compact = False

# -- Custom configuration ----------------------------------------------------

def setup(app):
    app.add_css_file('custom.css')
