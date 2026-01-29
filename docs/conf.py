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

    # Dynamically update configuration based on master_doc
    # This runs after Sphinx processes -D options
    def update_config_for_language(app, config):
        if config.master_doc == 'index_ar':
            # Update latex_documents for Arabic
            config.latex_documents = [
                ('index_ar', 'HFF_Documentation_AR.tex', 'وثائق HFF Survey Plugin',
                 'Enzo Cocca', 'manual'),
            ]

            # Update language
            config.language = 'ar'

            # Update latex_elements for Arabic with RTL support
            config.latex_elements = {
                'papersize': 'a4paper',
                'pointsize': '12pt',
                'babel': '',  # Disable babel, use polyglossia instead
                'fontpkg': r'''
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage[numerals=maghrib]{arabic}
\setotherlanguage{english}
% Use Amiri for Arabic text
\newfontfamily\arabicfont[Path=/usr/local/texlive/2024basic/texmf-dist/fonts/truetype/public/amiri/,
    UprightFont=Amiri-Regular.ttf,
    BoldFont=Amiri-Bold.ttf,
    ItalicFont=Amiri-Italic.ttf,
    BoldItalicFont=Amiri-BoldItalic.ttf,
    Script=Arabic,
    Scale=1.2]{Amiri}
% Use system fonts for Latin text
\newfontfamily\englishfont{Helvetica}
\setmainfont[Path=/usr/local/texlive/2024basic/texmf-dist/fonts/truetype/public/amiri/,
    UprightFont=Amiri-Regular.ttf,
    BoldFont=Amiri-Bold.ttf,
    ItalicFont=Amiri-Italic.ttf,
    BoldItalicFont=Amiri-BoldItalic.ttf,
    Script=Arabic]{Amiri}
\setsansfont{Helvetica}
\setmonofont{Menlo}
''',
                'preamble': r'''
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{array}
\setcounter{tocdepth}{2}
% Set text color to black
\color{black}
% RTL support
\usepackage{bidi}
% COMPLETELY disable Sphinx table styling
\sphinxsetup{
  verbatimwithframe=false,
  VerbatimColor={named}{white},
  VerbatimBorderColor={named}{white},
  noteBorderColor={named}{white},
  warningBorderColor={named}{white},
}
% Override ALL table-related macros
\let\sphinxstyletheadfamily\relax
\let\sphinxtableatstartofbodyhook\relax
\let\sphinxtablestrut\relax
\let\sphinxcolorgroupedrow\relax
\makeatletter
\renewcommand{\sphinxstyletheadfamily}{\normalfont\bfseries}
\let\sphinxcolorlatentable\@empty
\let\sphinxcolortabletoggle\@empty
\makeatother
% Ensure black text
\AtBeginDocument{\color{black}}
''',
                'figure_align': 'htbp',
                'extraclassoptions': 'openany,oneside',
                'maketitle': r'''
\begin{titlepage}
\begin{center}
\vspace*{3cm}
{\Huge\bfseries HFF Survey Plugin\\[1cm]}
{\Large وثائق البرنامج المساعد\\[2cm]}
{\large مؤسسة هونور فروست\\[0.5cm]}
{\large الإصدار 4.1.x\\[3cm]}
\today
\end{center}
\end{titlepage}
''',
            }

    app.connect('config-inited', update_config_for_language)
