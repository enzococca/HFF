# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Theme Manager for Dark/Light Mode
                             -------------------
    begin                : 2024
    copyright            : (C) 2024 by HFF Team
    email                :
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
        from modules.utility.hff_theme_manager import ThemeManager

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
    FONT_SIZE = "12px"
    FONT_SIZE_SMALL = "10px"
    FONT_SIZE_LARGE = "14px"

    # Dark theme colors
    DARK_COLORS = {
        "background": "#2b2b2b",
        "background_alt": "#323232",
        "text": "#ffffff",
        "text_secondary": "#b0b0b0",
        "accent": "#4da6ff",
        "accent_hover": "#66b3ff",
        "input_bg": "#3c3c3c",
        "input_border": "#555555",
        "border": "#555555",
        "button_bg": "#4da6ff",
        "button_text": "#ffffff",
        "button_hover": "#66b3ff",
        "table_header": "#404040",
        "table_alt_row": "#353535",
        "error": "#ff6b6b",
        "success": "#69db7c",
        "warning": "#ffd43b",
    }

    # Light theme colors
    LIGHT_COLORS = {
        "background": "#f5f5f5",
        "background_alt": "#ffffff",
        "text": "#333333",
        "text_secondary": "#666666",
        "accent": "#0078d4",
        "accent_hover": "#106ebe",
        "input_bg": "#ffffff",
        "input_border": "#cccccc",
        "border": "#cccccc",
        "button_bg": "#0078d4",
        "button_text": "#ffffff",
        "button_hover": "#106ebe",
        "table_header": "#e0e0e0",
        "table_alt_row": "#f9f9f9",
        "error": "#dc3545",
        "success": "#28a745",
        "warning": "#ffc107",
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
        /* Base widget styling */
        QWidget {{
            font-family: {self.FONT_FAMILY};
            font-size: {self.FONT_SIZE};
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        /* Dialog and main windows */
        QDialog, QMainWindow {{
            background-color: {colors['background']};
        }}

        /* Labels */
        QLabel {{
            font-size: {self.FONT_SIZE};
            color: {colors['text']};
            background-color: transparent;
        }}

        /* Input fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 4px 8px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {colors['accent']};
        }}

        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {colors['background_alt']};
            color: {colors['text_secondary']};
        }}

        /* ComboBox */
        QComboBox {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 4px 8px;
            min-height: 24px;
        }}

        QComboBox:focus {{
            border: 1px solid {colors['accent']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {colors['input_bg']};
            color: {colors['text']};
            selection-background-color: {colors['accent']};
            selection-color: {colors['button_text']};
        }}

        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 4px;
            padding: 4px 8px;
        }}

        /* Buttons */
        QPushButton {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['button_bg']};
            color: {colors['button_text']};
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
            min-height: 28px;
        }}

        QPushButton:hover {{
            background-color: {colors['button_hover']};
        }}

        QPushButton:pressed {{
            background-color: {colors['accent']};
        }}

        QPushButton:disabled {{
            background-color: {colors['border']};
            color: {colors['text_secondary']};
        }}

        /* Tool buttons (icon-only buttons) */
        QToolButton {{
            font-size: {self.FONT_SIZE};
            background-color: transparent;
            color: {colors['text']};
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 4px;
        }}

        QToolButton:hover {{
            background-color: {colors['background_alt']};
            border: 1px solid {colors['border']};
        }}

        /* Tables */
        QTableWidget, QTableView {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            gridline-color: {colors['border']};
            border: 1px solid {colors['border']};
        }}

        QTableWidget::item, QTableView::item {{
            padding: 4px;
        }}

        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {colors['accent']};
            color: {colors['button_text']};
        }}

        QHeaderView::section {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['table_header']};
            color: {colors['text']};
            padding: 6px;
            border: 1px solid {colors['border']};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background-color: {colors['background']};
        }}

        QTabBar::tab {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['background_alt']};
            color: {colors['text']};
            padding: 8px 16px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['background']};
            border-bottom: 2px solid {colors['accent']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {colors['table_header']};
        }}

        /* Group Box */
        QGroupBox {{
            font-size: {self.FONT_SIZE};
            font-weight: bold;
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 12px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}

        /* Check Box */
        QCheckBox {{
            font-size: {self.FONT_SIZE};
            color: {colors['text']};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {colors['border']};
            border-radius: 3px;
            background-color: {colors['input_bg']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {colors['accent']};
            border-color: {colors['accent']};
        }}

        /* Radio Button */
        QRadioButton {{
            font-size: {self.FONT_SIZE};
            color: {colors['text']};
            spacing: 8px;
        }}

        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {colors['border']};
            border-radius: 9px;
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

        /* Scroll Bar */
        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 12px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}

        QScrollBar:horizontal {{
            background-color: {colors['background']};
            height: 12px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-width: 30px;
            margin: 2px;
        }}

        QScrollBar::add-line, QScrollBar::sub-line {{
            width: 0;
            height: 0;
        }}

        /* Menu */
        QMenu {{
            font-size: {self.FONT_SIZE};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}

        QMenu::item:selected {{
            background-color: {colors['accent']};
            color: {colors['button_text']};
        }}

        /* Message Box */
        QMessageBox {{
            background-color: {colors['background']};
        }}

        /* Progress Bar */
        QProgressBar {{
            font-size: {self.FONT_SIZE_SMALL};
            background-color: {colors['input_bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 3px;
        }}

        /* Status Bar */
        QStatusBar {{
            font-size: {self.FONT_SIZE_SMALL};
            background-color: {colors['background_alt']};
            color: {colors['text']};
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
        toggle_btn.setFixedSize(32, 32)
        toggle_btn.setToolTip("Toggle Dark/Light Mode")

        # Set icon based on current theme
        self._update_toggle_icon(toggle_btn)

        def on_toggle():
            self.toggle_theme()
            self._update_toggle_icon(toggle_btn)
            self.apply_theme(parent_widget)

        toggle_btn.clicked.connect(on_toggle)

        # Style the toggle button to be more subtle
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(128, 128, 128, 0.2);
                border-radius: 16px;
            }
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
