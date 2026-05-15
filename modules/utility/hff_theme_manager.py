# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Theme Manager for Dark/Light Mode
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

from qgis.PyQt.QtWidgets import QWidget, QPushButton, QApplication
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.core import QgsSettings


class ThemeManager(QObject):
    """Singleton class to manage dark/light theme switching for HFF plugin.

    Usage:
        from ..modules.utility.hff_theme_manager import ThemeManager  # from tabs/
        from .hff_theme_manager import ThemeManager                   # from modules/utility/

        # In form __init__:
        ThemeManager.instance().apply_theme(self)

        # To add toggle button:
        ThemeManager.instance().add_theme_toggle(self, layout, row, col)
    """

    _instance = None
    theme_changed = pyqtSignal(str)  # Emits 'dark' or 'light'

    DARK = "dark"
    LIGHT = "light"

    # Cross-platform font stack
    FONT_FAMILY = '"Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif'
    FONT_SIZE = "11px"
    FONT_SIZE_SMALL = "10px"
    FONT_SIZE_LARGE = "13px"

    # Dark theme colors
    DARK_COLORS = {
        "background": "#2b2b2b",
        "background_alt": "#323232",
        "background_widget": "#3c3c3c",
        "text": "#e0e0e0",
        "text_secondary": "#a0a0a0",
        "text_disabled": "#707070",
        "accent": "#4da6ff",
        "accent_hover": "#66b3ff",
        "input_bg": "#3c3c3c",
        "input_border": "#555555",
        "input_border_focus": "#4da6ff",
        "border": "#555555",
        "button_bg": "#4da6ff",
        "button_text": "#ffffff",
        "button_hover": "#66b3ff",
        "button_secondary_bg": "#505050",
        "button_secondary_text": "#e0e0e0",
        "table_header": "#404040",
        "table_alt_row": "#353535",
        "table_cell_bg": "#3c3c3c",
        "table_highlight": "#5c5c00",
        "selection_bg": "#4da6ff",
        "selection_text": "#ffffff",
        "error": "#ff6b6b",
        "success": "#69db7c",
        "warning": "#ffd43b",
        "link": "#66b3ff",
    }

    # Light theme colors
    LIGHT_COLORS = {
        "background": "#f5f5f5",
        "background_alt": "#ffffff",
        "background_widget": "#ffffff",
        "text": "#1a1a1a",
        "text_secondary": "#505050",
        "text_disabled": "#909090",
        "accent": "#0078d4",
        "accent_hover": "#106ebe",
        "input_bg": "#ffffff",
        "input_border": "#c0c0c0",
        "input_border_focus": "#0078d4",
        "border": "#d0d0d0",
        "button_bg": "#0078d4",
        "button_text": "#ffffff",
        "button_hover": "#106ebe",
        "button_secondary_bg": "#e8e8e8",
        "button_secondary_text": "#1a1a1a",
        "table_header": "#e8e8e8",
        "table_alt_row": "#fafafa",
        "table_cell_bg": "#ffffff",
        "table_highlight": "#ffff99",
        "selection_bg": "#0078d4",
        "selection_text": "#ffffff",
        "error": "#dc3545",
        "success": "#28a745",
        "warning": "#ffc107",
        "link": "#0078d4",
    }

    @classmethod
    def instance(cls):
        """Get the singleton instance of ThemeManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        if ThemeManager._instance is not None:
            raise RuntimeError("Use ThemeManager.instance() instead of direct instantiation")
        self._current_theme = self._load_theme_preference()

    def _load_theme_preference(self):
        """Load theme preference from QGIS settings."""
        settings = QgsSettings()
        return settings.value("HFF/ui_theme", self.LIGHT)

    def _save_theme_preference(self, theme):
        """Save theme preference to QGIS settings."""
        settings = QgsSettings()
        settings.setValue("HFF/ui_theme", theme)

    def get_current_theme(self):
        """Get the current theme ('dark' or 'light')."""
        return self._current_theme

    def get_colors(self, theme=None):
        """Get color dictionary for the specified or current theme."""
        if theme is None:
            theme = self._current_theme
        return self.DARK_COLORS if theme == self.DARK else self.LIGHT_COLORS

    def get_table_header_color(self):
        """Get QColor for table header background."""
        from qgis.PyQt.QtGui import QColor
        return QColor(self.get_colors()["table_header"])

    def get_table_cell_color(self):
        """Get QColor for table cell background."""
        from qgis.PyQt.QtGui import QColor
        return QColor(self.get_colors()["table_cell_bg"])

    def get_table_highlight_color(self):
        """Get QColor for highlighted table cell (e.g., yellow)."""
        from qgis.PyQt.QtGui import QColor
        return QColor(self.get_colors()["table_highlight"])

    def get_table_alt_row_color(self):
        """Get QColor for alternate row background."""
        from qgis.PyQt.QtGui import QColor
        return QColor(self.get_colors()["table_alt_row"])

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        new_theme = self.LIGHT if self._current_theme == self.DARK else self.DARK
        self.set_theme(new_theme)
        return new_theme

    def set_theme(self, theme):
        """Set the theme and save preference."""
        if theme not in (self.DARK, self.LIGHT):
            theme = self.LIGHT
        self._current_theme = theme
        self._save_theme_preference(theme)
        self.theme_changed.emit(theme)

    def get_stylesheet(self, theme=None):
        """Generate stylesheet for the specified or current theme."""
        colors = self.get_colors(theme)

        stylesheet = f"""
        /* ============================================== */
        /* HFF Theme Stylesheet - Comprehensive Styling   */
        /* ============================================== */

        /* Base widget styling - IMPORTANT: explicit color for all */
        QWidget {{
            font-family: {self.FONT_FAMILY};
            font-size: {self.FONT_SIZE};
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        /* Dialog and main windows */
        QDialog, QMainWindow, QDockWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        QDockWidget::title {{
            background-color: {colors['background_alt']};
            color: {colors['text']};
            padding: 6px;
            font-weight: bold;
        }}

        /* Frame styling */
        QFrame {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        /* Labels - CRITICAL: explicit colors to fix white-on-white */
        QLabel {{
            font-size: {self.FONT_SIZE};
            color: {colors['text']};
            background-color: transparent;
            padding: 2px;
        }}

        QLabel:disabled {{
            color: {colors['text_disabled']};
        }}

        /* Input fields */
        QLineEdit {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            padding: 4px 6px;
            min-height: 20px;
        }}

        QLineEdit:focus {{
            border: 1px solid {colors['input_border_focus']};
        }}

        QLineEdit:disabled {{
            background-color: {colors['background_alt']};
            color: {colors['text_disabled']};
        }}

        QLineEdit:read-only {{
            background-color: {colors['background_alt']};
        }}

        /* Text Edit */
        QTextEdit, QPlainTextEdit {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            padding: 4px;
        }}

        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {colors['input_border_focus']};
        }}

        QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors['background_alt']};
            color: {colors['text_disabled']};
        }}

        /* ComboBox - with proper dropdown styling */
        QComboBox {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            padding: 4px 6px;
            min-height: 20px;
        }}

        QComboBox:focus {{
            border: 1px solid {colors['input_border_focus']};
        }}

        QComboBox:disabled {{
            background-color: {colors['background_alt']};
            color: {colors['text_disabled']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
            subcontrol-origin: padding;
            subcontrol-position: right center;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            selection-background-color: {colors['selection_bg']};
            selection-color: {colors['selection_text']};
        }}

        QComboBox QAbstractItemView::item {{
            padding: 4px 8px;
            min-height: 24px;
        }}

        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            padding: 4px 6px;
            min-height: 20px;
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {colors['input_border_focus']};
        }}

        QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {colors['background_alt']};
            color: {colors['text_disabled']};
        }}

        /* Date/Time Edit */
        QDateEdit, QTimeEdit, QDateTimeEdit {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            padding: 4px 6px;
            min-height: 20px;
        }}

        QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
            border: 1px solid {colors['input_border_focus']};
        }}

        /* Push Buttons - PRIMARY style */
        QPushButton {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['button_bg']};
            color: {colors['button_text']};
            border: none;
            border-radius: 3px;
            padding: 5px 12px;
            min-height: 24px;
            min-width: 70px;
        }}

        QPushButton:hover {{
            background-color: {colors['button_hover']};
        }}

        QPushButton:pressed {{
            background-color: {colors['accent']};
        }}

        QPushButton:disabled {{
            background-color: {colors['border']};
            color: {colors['text_disabled']};
        }}

        QPushButton:flat {{
            background-color: transparent;
            color: {colors['accent']};
            border: none;
        }}

        QPushButton:flat:hover {{
            background-color: {colors['background_alt']};
        }}

        /* Tool buttons */
        QToolButton {{
            font-size: {self.FONT_SIZE};
            background-color: transparent;
            color: {colors['text']};
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 4px;
        }}

        QToolButton:hover {{
            background-color: {colors['background_alt']};
            border: 1px solid {colors['border']};
        }}

        QToolButton:pressed {{
            background-color: {colors['border']};
        }}

        QToolButton:checked {{
            background-color: {colors['accent']};
            color: {colors['button_text']};
        }}

        /* Tables - with alternating rows and proper text color */
        QTableWidget, QTableView {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_widget']};
            color: {colors['text']};
            gridline-color: {colors['border']};
            border: 1px solid {colors['border']};
            alternate-background-color: {colors['table_alt_row']};
        }}

        QTableWidget::item, QTableView::item {{
            padding: 4px;
            color: {colors['text']};
            background-color: {colors['background_widget']};
        }}

        QTableWidget::item:alternate, QTableView::item:alternate {{
            background-color: {colors['table_alt_row']};
        }}

        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {colors['selection_bg']};
            color: {colors['selection_text']};
        }}

        QHeaderView {{
            background-color: {colors['table_header']};
        }}

        QHeaderView::section {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['table_header']};
            color: {colors['text']};
            padding: 6px;
            border: none;
            border-right: 1px solid {colors['border']};
            border-bottom: 1px solid {colors['border']};
        }}

        QHeaderView::section:hover {{
            background-color: {colors['border']};
        }}

        /* List Widget */
        QListWidget, QListView {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_widget']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            alternate-background-color: {colors['table_alt_row']};
        }}

        QListWidget::item, QListView::item {{
            padding: 4px;
            color: {colors['text']};
        }}

        QListWidget::item:selected, QListView::item:selected {{
            background-color: {colors['selection_bg']};
            color: {colors['selection_text']};
        }}

        QListWidget::item:hover, QListView::item:hover {{
            background-color: {colors['background_alt']};
        }}

        /* Tree Widget */
        QTreeWidget, QTreeView {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_widget']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            alternate-background-color: {colors['table_alt_row']};
        }}

        QTreeWidget::item, QTreeView::item {{
            padding: 4px;
            color: {colors['text']};
        }}

        QTreeWidget::item:selected, QTreeView::item:selected {{
            background-color: {colors['selection_bg']};
            color: {colors['selection_text']};
        }}

        /* Tab Widget - clean modern tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background-color: {colors['background']};
            top: -1px;
        }}

        QTabBar {{
            background-color: {colors['background']};
        }}

        QTabBar::tab {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_alt']};
            color: {colors['text']};
            padding: 6px 14px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['background']};
            border-bottom: 2px solid {colors['accent']};
            color: {colors['accent']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {colors['table_header']};
        }}

        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}

        /* Group Box */
        QGroupBox {{
            font-size: {self.FONT_SIZE};
            font-weight: bold;
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: {colors['text']};
        }}

        /* Check Box */
        QCheckBox {{
            font-size: {self.FONT_SIZE};
            color: {colors['text']};
            spacing: 6px;
        }}

        QCheckBox:disabled {{
            color: {colors['text_disabled']};
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            background-color: {colors['input_bg']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {colors['accent']};
            border-color: {colors['accent']};
        }}

        QCheckBox::indicator:disabled {{
            background-color: {colors['background_alt']};
            border-color: {colors['border']};
        }}

        /* Radio Button */
        QRadioButton {{
            font-size: {self.FONT_SIZE};
            color: {colors['text']};
            spacing: 6px;
        }}

        QRadioButton:disabled {{
            color: {colors['text_disabled']};
        }}

        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors['input_border']};
            border-radius: 8px;
            background-color: {colors['input_bg']};
        }}

        QRadioButton::indicator:checked {{
            background-color: {colors['accent']};
            border-color: {colors['accent']};
        }}

        /* Scroll Area */
        QScrollArea {{
            border: none;
            background-color: {colors['background']};
        }}

        QScrollArea > QWidget > QWidget {{
            background-color: {colors['background']};
        }}

        /* Scroll Bar */
        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 10px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 5px;
            min-height: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}

        QScrollBar:horizontal {{
            background-color: {colors['background']};
            height: 10px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 5px;
            min-width: 30px;
            margin: 2px;
        }}

        QScrollBar::add-line, QScrollBar::sub-line {{
            width: 0;
            height: 0;
        }}

        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}

        /* Menu */
        QMenu {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_widget']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QMenu::item {{
            padding: 6px 20px;
        }}

        QMenu::item:selected {{
            background-color: {colors['selection_bg']};
            color: {colors['selection_text']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {colors['border']};
            margin: 4px 10px;
        }}

        QMenuBar {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        QMenuBar::item {{
            padding: 4px 8px;
            background-color: transparent;
        }}

        QMenuBar::item:selected {{
            background-color: {colors['selection_bg']};
            color: {colors['selection_text']};
        }}

        /* Message Box */
        QMessageBox {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        QMessageBox QLabel {{
            color: {colors['text']};
        }}

        /* Progress Bar */
        QProgressBar {{
            font-size: {self.FONT_SIZE_SMALL};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 3px;
            text-align: center;
            min-height: 18px;
        }}

        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 2px;
        }}

        /* Status Bar */
        QStatusBar {{
            font-size: {self.FONT_SIZE_SMALL};
            background-color: {colors['background_alt']};
            color: {colors['text']};
            border-top: 1px solid {colors['border']};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}

        QSplitter::handle:horizontal {{
            width: 4px;
        }}

        QSplitter::handle:vertical {{
            height: 4px;
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            border: 1px solid {colors['border']};
            height: 4px;
            background-color: {colors['input_bg']};
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background-color: {colors['accent']};
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}

        QSlider::groove:vertical {{
            border: 1px solid {colors['border']};
            width: 4px;
            background-color: {colors['input_bg']};
            border-radius: 2px;
        }}

        QSlider::handle:vertical {{
            background-color: {colors['accent']};
            height: 14px;
            margin: 0 -5px;
            border-radius: 7px;
        }}

        /* ToolTip */
        QToolTip {{
            font-size: {self.FONT_SIZE_SMALL};
            background-color: {colors['background_widget']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            padding: 4px 8px;
        }}

        /* Text Browser (for tutorials/docs) */
        QTextBrowser {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_widget']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QTextBrowser a {{
            color: {colors['link']};
        }}

        /* Calendar Widget */
        QCalendarWidget {{
            background-color: {colors['background']};
        }}

        QCalendarWidget QWidget {{
            alternate-background-color: {colors['table_alt_row']};
        }}

        QCalendarWidget QAbstractItemView:enabled {{
            color: {colors['text']};
            background-color: {colors['background_widget']};
            selection-background-color: {colors['selection_bg']};
            selection-color: {colors['selection_text']};
        }}

        QCalendarWidget QToolButton {{
            color: {colors['text']};
            background-color: {colors['background']};
            border: none;
        }}

        QCalendarWidget QSpinBox {{
            color: {colors['text']};
            background-color: {colors['input_bg']};
        }}

        /* ============================================== */
        /* Icon-only Buttons (navigation, actions)        */
        /* Standard size: 30x30 for consistency           */
        /* ============================================== */

        /* Icon buttons - detected by having max-width set */
        QPushButton[maximumWidth="30"] {{
            min-width: 28px;
            max-width: 30px;
            min-height: 28px;
            max-height: 30px;
            padding: 3px;
            background-color: {colors['button_secondary_bg']};
            color: {colors['button_secondary_text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QPushButton[maximumWidth="30"]:hover {{
            background-color: {colors['accent']};
            color: {colors['button_text']};
            border-color: {colors['accent']};
        }}

        QPushButton[maximumWidth="30"]:pressed {{
            background-color: {colors['accent_hover']};
        }}

        /* Small icon buttons (20x20) */
        QPushButton[maximumWidth="20"] {{
            min-width: 18px;
            max-width: 20px;
            min-height: 18px;
            max-height: 20px;
            padding: 2px;
            background-color: {colors['button_secondary_bg']};
            color: {colors['button_secondary_text']};
            border: 1px solid {colors['border']};
            border-radius: 3px;
        }}

        QPushButton[maximumWidth="20"]:hover {{
            background-color: {colors['accent']};
            color: {colors['button_text']};
        }}

        /* Navigation buttons - uniform styling */
        QPushButton#pushButton_first_rec,
        QPushButton#pushButton_prev_rec,
        QPushButton#pushButton_next_rec,
        QPushButton#pushButton_last_rec {{
            min-width: 28px;
            max-width: 30px;
            min-height: 28px;
            max-height: 30px;
            background-color: {colors['button_secondary_bg']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QPushButton#pushButton_first_rec:hover,
        QPushButton#pushButton_prev_rec:hover,
        QPushButton#pushButton_next_rec:hover,
        QPushButton#pushButton_last_rec:hover {{
            background-color: {colors['accent']};
            color: {colors['button_text']};
        }}

        /* Action buttons - uniform styling */
        QPushButton#pushButton_new_rec,
        QPushButton#pushButton_save,
        QPushButton#pushButton_delete {{
            min-width: 28px;
            max-width: 30px;
            min-height: 28px;
            max-height: 30px;
            background-color: {colors['button_secondary_bg']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QPushButton#pushButton_save:hover {{
            background-color: {colors['success']};
            color: white;
        }}

        QPushButton#pushButton_delete:hover {{
            background-color: {colors['error']};
            color: white;
        }}

        QPushButton#pushButton_new_rec:hover {{
            background-color: {colors['accent']};
            color: white;
        }}

        /* Search and filter buttons */
        QPushButton#pushButton_new_search,
        QPushButton#pushButton_search_go,
        QPushButton#pushButton_view_all,
        QPushButton#pushButton_sort {{
            min-width: 28px;
            max-width: 30px;
            min-height: 28px;
            max-height: 30px;
            background-color: {colors['button_secondary_bg']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QPushButton#pushButton_new_search:hover,
        QPushButton#pushButton_search_go:hover,
        QPushButton#pushButton_view_all:hover,
        QPushButton#pushButton_sort:hover {{
            background-color: {colors['accent']};
            color: white;
        }}

        /* Export and tool buttons */
        QPushButton#pushButton_form,
        QPushButton#pushButton_list,
        QPushButton#toolButtonGis,
        QPushButton#pushButton_open_dir {{
            min-width: 28px;
            max-width: 30px;
            min-height: 28px;
            max-height: 30px;
            background-color: {colors['button_secondary_bg']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
        }}

        QPushButton#pushButton_form:hover,
        QPushButton#pushButton_list:hover,
        QPushButton#toolButtonGis:hover,
        QPushButton#pushButton_open_dir:hover {{
            background-color: {colors['accent']};
            color: white;
        }}

        /* Dialog button box - standard sizing */
        QDialogButtonBox QPushButton {{
            min-width: 80px;
            min-height: 28px;
            padding: 5px 15px;
        }}
        """

        return stylesheet

    def apply_theme(self, widget, theme=None):
        """Apply the current or specified theme to a widget.

        Args:
            widget: QWidget to apply theme to
            theme: Optional theme override ('dark' or 'light')
        """
        if theme is None:
            theme = self._current_theme
        stylesheet = self.get_stylesheet(theme)
        widget.setStyleSheet(stylesheet)

    def add_theme_toggle(self, parent_widget, layout=None, row=0, col=0):
        """Add a theme toggle button to a widget.

        Args:
            parent_widget: Parent widget for the button
            layout: Optional layout to add button to (if None, button is created but not added)
            row: Row position in grid layout
            col: Column position in grid layout

        Returns:
            QPushButton: The created toggle button
        """
        toggle_btn = QPushButton(parent_widget)
        toggle_btn.setFixedSize(28, 28)
        toggle_btn.setToolTip("Toggle Dark/Light Mode")

        # Set icon based on current theme
        self._update_toggle_icon(toggle_btn)

        def on_toggle():
            self.toggle_theme()
            self._update_toggle_icon(toggle_btn)
            self.apply_theme(parent_widget)

        toggle_btn.clicked.connect(on_toggle)

        # Style the toggle button
        colors = self.get_colors()
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {colors['border']};
                border-radius: 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {colors['background_alt']};
            }}
        """)

        if layout is not None:
            layout.addWidget(toggle_btn, row, col)

        return toggle_btn

    def _update_toggle_icon(self, button):
        """Update the toggle button icon based on current theme."""
        if self._current_theme == self.DARK:
            button.setText("\u2600")  # Sun symbol for switching to light
        else:
            button.setText("\U0001F319")  # Moon symbol for switching to dark
