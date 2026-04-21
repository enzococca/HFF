# -*- coding: utf-8 -*-
"""Centralized OpenAI API key / model management for HFF.

Resolution order for the API key:
    1. QgsSettings key ``HFF/openai_api_key``
    2. Legacy file ``$HFF_HOME/bin/gpt_api_key.txt``
    3. Environment variable ``OPENAI_API_KEY``

Saving via :func:`set_api_key` writes to both QgsSettings and the legacy
file so that older code paths reading the file keep working.
"""
from __future__ import annotations

import os

from qgis.core import QgsSettings

SETTINGS_KEY = 'HFF/openai_api_key'
MODEL_KEY = 'HFF/openai_model'
DEFAULT_MODEL = 'gpt-5.4'
SUPPORTED_MODELS = ('gpt-5.4', 'gpt-4o', 'gpt-4o-mini')


def _legacy_file_path() -> str:
    home = os.environ.get('HFF_HOME') or os.path.expanduser('~/HFF')
    return os.path.join(home, 'bin', 'gpt_api_key.txt')


def get_api_key() -> str:
    """Return the stored OpenAI API key or an empty string."""
    settings = QgsSettings()
    key = settings.value(SETTINGS_KEY, '', type=str)
    if key:
        return key.strip()

    path = _legacy_file_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                key = f.read().strip()
            if key:
                # Migrate silently into QgsSettings for future reads
                settings.setValue(SETTINGS_KEY, key)
                return key
        except OSError:
            pass

    return os.environ.get('OPENAI_API_KEY', '').strip()


def set_api_key(key: str) -> None:
    """Persist the API key to QgsSettings and the legacy file."""
    key = (key or '').strip()
    QgsSettings().setValue(SETTINGS_KEY, key)
    try:
        path = _legacy_file_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(key)
    except OSError:
        pass


def get_model() -> str:
    return QgsSettings().value(MODEL_KEY, DEFAULT_MODEL, type=str) or DEFAULT_MODEL


def set_model(model: str) -> None:
    QgsSettings().setValue(MODEL_KEY, model or DEFAULT_MODEL)


def prompt_and_get_api_key(parent=None) -> str:
    """Return the key; if missing, prompt the user once with QInputDialog."""
    key = get_api_key()
    if key:
        return key
    try:
        from qgis.PyQt.QtWidgets import QInputDialog, QLineEdit
        text, ok = QInputDialog.getText(
            parent, 'OpenAI API key',
            'Insert your OpenAI API key:',
            QLineEdit.Password,
        )
        if ok and text.strip():
            set_api_key(text.strip())
            return text.strip()
    except Exception:
        pass
    return ''
