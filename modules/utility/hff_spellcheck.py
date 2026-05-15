# -*- coding: utf-8 -*-
"""English spellcheck overlay for HFF data-entry forms (issue #45).

Uses pyenchant + a QSyntaxHighlighter to draw red underlines on
misspelled words in QTextEdit / QPlainTextEdit widgets, and a custom
right-click menu on QLineEdit / QTextEdit with suggested corrections.

Graceful degradation: when pyenchant or its native enchant library
is unavailable, `attach_spellcheck()` is a no-op and the form keeps
working without spellcheck.
"""
from __future__ import annotations

import re

from qgis.PyQt.QtCore import Qt, QEvent, QPoint
from qgis.PyQt.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QTextCursor, QColor,
)
from qgis.PyQt.QtWidgets import (
    QApplication, QLineEdit, QMenu, QPlainTextEdit, QTextEdit,
)

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def _get_dict(lang: str = "en_US"):
    """Return a pyenchant dict or None when enchant is unavailable.
    Cached on the module so we pay the load cost once per process."""
    cached = getattr(_get_dict, "_cache", {})
    if lang in cached:
        return cached[lang]
    try:
        import enchant
        d = enchant.Dict(lang)
    except Exception:
        d = None
    cached[lang] = d
    _get_dict._cache = cached
    return d


class SpellHighlighter(QSyntaxHighlighter):
    """Underline misspelled English words in red. Attach to a QTextDocument."""

    def __init__(self, document, lang: str = "en_US"):
        super().__init__(document)
        self._dict = _get_dict(lang)
        self._fmt = QTextCharFormat()
        self._fmt.setUnderlineColor(QColor("#cc0000"))
        # SpellCheckUnderline = 4 (squiggly). Falls back to SingleUnderline
        # on older Qt; both render as a visible red mark.
        try:
            self._fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        except AttributeError:
            self._fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)

    def highlightBlock(self, text: str) -> None:
        if self._dict is None or not text:
            return
        for m in _WORD_RE.finditer(text):
            word = m.group(0)
            # Skip ALL_CAPS tokens (likely acronyms/SU codes).
            if word.isupper():
                continue
            try:
                ok = self._dict.check(word)
            except Exception:
                continue
            if not ok:
                self.setFormat(m.start(), len(word), self._fmt)


class _LineEditSpellMenu:
    """Event filter that injects spell suggestions into QLineEdit's
    context menu. Installed via eventFilter on the QLineEdit."""

    def __init__(self, parent, lang: str = "en_US"):
        self._parent = parent
        self._lang = lang

    def eventFilter(self, obj, event):
        if event.type() != QEvent.ContextMenu:
            return False
        if not isinstance(obj, QLineEdit):
            return False
        d = _get_dict(self._lang)
        if d is None:
            return False
        # Identify word under cursor.
        text = obj.text()
        pos = obj.cursorPositionAt(event.pos())
        word, w_start, w_end = _word_at(text, pos)
        menu = obj.createStandardContextMenu()
        if word and not word.isupper():
            try:
                misspelled = not d.check(word)
            except Exception:
                misspelled = False
            if misspelled:
                try:
                    sugg = d.suggest(word)[:7]
                except Exception:
                    sugg = []
                if sugg:
                    menu.addSeparator()
                    sub = menu.addMenu(f"Spell: {word}")
                    for s in sugg:
                        act = sub.addAction(s)
                        act.triggered.connect(
                            lambda _checked=False, repl=s,
                            le=obj, a=w_start, b=w_end:
                            _replace_le(le, a, b, repl)
                        )
        menu.exec_(event.globalPos())
        menu.deleteLater()
        return True


def _word_at(text: str, pos: int):
    """Return (word, start, end) for the word at character offset `pos`,
    or ("", pos, pos) if cursor is not on a word."""
    if not text or pos < 0 or pos > len(text):
        return "", pos, pos
    for m in _WORD_RE.finditer(text):
        if m.start() <= pos <= m.end():
            return m.group(0), m.start(), m.end()
    return "", pos, pos


def _replace_le(line_edit: QLineEdit, start: int, end: int, repl: str):
    text = line_edit.text()
    line_edit.setText(text[:start] + repl + text[end:])
    line_edit.setCursorPosition(start + len(repl))


def attach_spellcheck(form, lang: str = "en_US") -> int:
    """Walk `form`'s descendants and enable English spellcheck on text
    widgets. Returns the number of widgets that received a highlighter
    / context-menu filter. No-op when enchant is unavailable."""
    if _get_dict(lang) is None:
        return 0
    count = 0
    # QTextEdit / QPlainTextEdit: attach the highlighter to the document.
    for w in form.findChildren((QTextEdit, QPlainTextEdit)):
        # Avoid double-attaching when apply_i18n_to_form runs twice.
        if getattr(w, "_hff_spell_highlighter", None) is not None:
            continue
        try:
            w._hff_spell_highlighter = SpellHighlighter(w.document(), lang)
            count += 1
        except Exception:
            pass
    # QLineEdit: install an event filter for the context menu.
    for w in form.findChildren(QLineEdit):
        if getattr(w, "_hff_spell_filter", None) is not None:
            continue
        try:
            filt = _LineEditSpellMenu(w, lang)
            w.installEventFilter(filt)
            w._hff_spell_filter = filt
            count += 1
        except Exception:
            pass
    return count
