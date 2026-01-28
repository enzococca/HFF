# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Tutorial Viewer Dialog
                             -------------------
    begin                : 2024
    copyright            : (C) 2024 by HFF Team
    email                : enzo.ccc@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import re
from typing import Optional, List, Dict

from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QFont, QDesktopServices
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QWidget,
    QListWidget, QListWidgetItem, QTextBrowser, QPushButton,
    QLineEdit, QComboBox, QLabel, QMessageBox
)
from qgis.core import QgsSettings

from ..modules.utility.hff_theme_manager import ThemeManager
from ..modules.utility.hff_i18n import HffI18n, tr
from ..modules.utility.hff_form_base import apply_i18n_to_form, get_export_translations


class TutorialViewerDialog(QDialog):
    """Dialog for viewing HFF tutorials and documentation.

    Features:
    - Browse tutorials by category
    - Search tutorials by keyword
    - Multi-language support (English, Arabic Lebanese)
    - Markdown rendering
    - Image support
    """

    # Available languages
    LANGUAGES = {
        'en': 'English',
        'ar-lb': 'Arabic (Lebanese)'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HFF - Tutorials & Documentation")
        self.setMinimumSize(900, 600)

        # Get plugin directory
        self.plugin_dir = os.path.dirname(os.path.dirname(__file__))
        self.tutorials_dir = os.path.join(self.plugin_dir, 'docs', 'tutorials')

        # Current state
        self.current_language = self._load_language_preference()
        self.tutorials: List[Dict] = []

        self.setup_ui()
        self.load_tutorials()
        apply_i18n_to_form(self)
        self.i18n = HffI18n.instance()

    def _load_language_preference(self) -> str:
        """Load saved language preference."""
        settings = QgsSettings()
        return settings.value("HFF/tutorial_language", "en")

    def _save_language_preference(self, lang: str):
        """Save language preference."""
        settings = QgsSettings()
        settings.setValue("HFF/tutorial_language", lang)

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Top toolbar
        toolbar = QHBoxLayout()

        # Search
        toolbar.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search tutorials...")
        self.search_edit.textChanged.connect(self.filter_tutorials)
        toolbar.addWidget(self.search_edit)

        toolbar.addStretch()

        # Language selector
        toolbar.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        for code, name in self.LANGUAGES.items():
            self.language_combo.addItem(name, code)

        # Set current language
        index = self.language_combo.findData(self.current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        toolbar.addWidget(self.language_combo)

        layout.addLayout(toolbar)

        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Tutorial list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel("Tutorials:"))

        self.tutorial_list = QListWidget()
        self.tutorial_list.currentItemChanged.connect(self.on_tutorial_selected)
        left_layout.addWidget(self.tutorial_list)

        splitter.addWidget(left_panel)

        # Right panel: Content viewer
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setFont(QFont('Arial', 11))
        self.content_browser.anchorClicked.connect(self.on_link_clicked)
        right_layout.addWidget(self.content_browser)

        splitter.addWidget(right_panel)

        # Set splitter sizes (30% list, 70% content)
        splitter.setSizes([270, 630])

        layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_tutorials)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def load_tutorials(self):
        """Load tutorials from the current language directory."""
        self.tutorials = []
        self.tutorial_list.clear()

        lang_dir = os.path.join(self.tutorials_dir, self.current_language)

        if not os.path.exists(lang_dir):
            # Fallback to English
            lang_dir = os.path.join(self.tutorials_dir, 'en')
            if not os.path.exists(lang_dir):
                self.content_browser.setHtml(
                    "<h2>No tutorials found</h2>"
                    "<p>Tutorials directory not found. Please check installation.</p>"
                )
                return

        # Scan for markdown files
        md_files = []
        for filename in sorted(os.listdir(lang_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(lang_dir, filename)
                md_files.append((filename, filepath))

        # Parse tutorials
        for filename, filepath in md_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract title from first heading
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else filename.replace('.md', '').replace('_', ' ')

                # Extract order from filename (e.g., 01_intro.md)
                order_match = re.match(r'^(\d+)_', filename)
                order = int(order_match.group(1)) if order_match else 99

                self.tutorials.append({
                    'filename': filename,
                    'filepath': filepath,
                    'title': title,
                    'content': content,
                    'order': order
                })
            except Exception as e:
                print(f"Error loading tutorial {filename}: {e}")

        # Sort by order
        self.tutorials.sort(key=lambda x: x['order'])

        # Populate list
        for tutorial in self.tutorials:
            item = QListWidgetItem(tutorial['title'])
            item.setData(Qt.UserRole, tutorial)
            self.tutorial_list.addItem(item)

        # Select first item
        if self.tutorial_list.count() > 0:
            self.tutorial_list.setCurrentRow(0)

    def filter_tutorials(self, search_text: str):
        """Filter tutorials by search text."""
        search_lower = search_text.lower()

        for i in range(self.tutorial_list.count()):
            item = self.tutorial_list.item(i)
            tutorial = item.data(Qt.UserRole)

            # Search in title and content
            visible = (
                search_lower in tutorial['title'].lower() or
                search_lower in tutorial['content'].lower()
            )

            item.setHidden(not visible)

    def on_language_changed(self, index: int):
        """Handle language change."""
        lang = self.language_combo.currentData()
        if lang != self.current_language:
            self.current_language = lang
            self._save_language_preference(lang)
            self.load_tutorials()

    def on_tutorial_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle tutorial selection."""
        if not current:
            return

        tutorial = current.data(Qt.UserRole)
        if tutorial:
            html_content = self.markdown_to_html(tutorial['content'])
            self.content_browser.setHtml(html_content)

    def on_link_clicked(self, url: QUrl):
        """Handle link clicks."""
        url_string = url.toString()

        # Handle internal links (other tutorials)
        if url_string.endswith('.md'):
            # Find and select the tutorial
            for i in range(self.tutorial_list.count()):
                item = self.tutorial_list.item(i)
                tutorial = item.data(Qt.UserRole)
                if tutorial['filename'] == url_string:
                    self.tutorial_list.setCurrentItem(item)
                    return

        # Handle external links
        if url_string.startswith('http://') or url_string.startswith('https://'):
            QDesktopServices.openUrl(url)

    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML.

        This is a simple implementation. For full markdown support,
        consider using the 'markdown' library.
        """
        html = markdown_text

        # Escape HTML (but preserve our converted HTML)
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')

        # Headers
        html = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Code blocks
        html = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

        # Images (convert to base path)
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)

            # Convert relative path to absolute
            if not img_path.startswith(('http://', 'https://', '/')):
                img_path = os.path.join(self.tutorials_dir, 'images', img_path)
                if os.path.exists(img_path):
                    img_path = 'file://' + img_path

            return f'<img src="{img_path}" alt="{alt_text}" style="max-width:100%;">'

        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, html)

        # Bullet lists
        html = re.sub(r'^\* (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'((?:<li>.*</li>\n?)+)', r'<ul>\1</ul>', html)

        # Numbered lists
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Blockquotes
        html = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # Horizontal rules
        html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)

        # Paragraphs (wrap non-tagged lines)
        lines = html.split('\n')
        processed_lines = []
        in_pre = False

        for line in lines:
            if '<pre>' in line:
                in_pre = True
            if '</pre>' in line:
                in_pre = False

            if not in_pre and line.strip() and not line.strip().startswith('<'):
                line = f'<p>{line}</p>'

            processed_lines.append(line)

        html = '\n'.join(processed_lines)

        # Wrap in full HTML
        colors = ThemeManager.instance().get_colors()
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: {colors['text']};
                    background-color: {colors['background']};
                    padding: 20px;
                }}
                h1 {{ color: {colors['accent']}; border-bottom: 2px solid {colors['border']}; padding-bottom: 10px; }}
                h2 {{ color: {colors['accent']}; border-bottom: 1px solid {colors['border']}; padding-bottom: 5px; }}
                h3, h4, h5, h6 {{ color: {colors['text']}; }}
                a {{ color: {colors['accent']}; }}
                code {{
                    background-color: {colors['input_bg']};
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: monospace;
                }}
                pre {{
                    background-color: {colors['input_bg']};
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                blockquote {{
                    border-left: 4px solid {colors['accent']};
                    margin: 10px 0;
                    padding-left: 15px;
                    color: {colors['text_secondary']};
                }}
                ul, ol {{
                    margin-left: 20px;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid {colors['border']};
                    margin: 20px 0;
                }}
                img {{
                    max-width: 100%;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        '''

        return html
