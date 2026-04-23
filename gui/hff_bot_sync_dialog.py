# -*- coding: utf-8 -*-
"""HFF Bot Media Sync dialog.

Mirrors the hff-telegram-bot /data/media/<alias>/ tree from a Railway
(or other) deployment to a local directory the plugin's ``THUMB_PATH``
points at. No changes to the existing display path — the plugin still
reads media via the normal local-filesystem code. This dialog only adds
a sync button and a background worker.

Network stack: urllib only, to avoid adding plugin dependencies.
Persistence: QgsSettings under ``HFF/bot_sync/``.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)
from qgis.core import QgsSettings


class BotSyncSettings:
    """QgsSettings wrapper for bot-sync configuration. Bearer token is
    stored base64-encoded (same trick the remote-storage dialog uses —
    mild obfuscation, NOT encryption)."""

    PREFIX = "HFF/bot_sync"

    @classmethod
    def _encode(cls, v: str) -> str:
        if not v:
            return ""
        return base64.b64encode(v.encode("utf-8")).decode("utf-8")

    @classmethod
    def _decode(cls, enc: str) -> str:
        if not enc:
            return ""
        try:
            return base64.b64decode(enc.encode("utf-8")).decode("utf-8")
        except Exception:
            return enc

    @classmethod
    def load(cls) -> dict:
        s = QgsSettings()
        return {
            "url": s.value(f"{cls.PREFIX}/url", "") or "",
            "token": cls._decode(s.value(f"{cls.PREFIX}/token", "") or ""),
            "alias": s.value(f"{cls.PREFIX}/alias", "") or "",
            "local_dir": s.value(f"{cls.PREFIX}/local_dir", "") or "",
        }

    @classmethod
    def save(cls, url: str, token: str, alias: str, local_dir: str) -> None:
        s = QgsSettings()
        s.setValue(f"{cls.PREFIX}/url", url)
        s.setValue(f"{cls.PREFIX}/token", cls._encode(token))
        s.setValue(f"{cls.PREFIX}/alias", alias)
        s.setValue(f"{cls.PREFIX}/local_dir", local_dir)


class BotSyncWorker(QThread):
    """Background thread that fetches the bot's media manifest then
    downloads missing / size-changed files to the local directory.
    Emits progress per file; finished/failed at the end.
    """

    progress = pyqtSignal(int, int, str)   # current, total, message
    finished = pyqtSignal(int, int, int)   # synced, skipped, errors
    failed = pyqtSignal(str)               # unrecoverable error

    def __init__(self, url: str, token: str, alias: str, local_dir: str,
                 parent=None):
        super().__init__(parent)
        self._url = url.rstrip("/")
        self._token = token
        self._alias = alias
        self._local_dir = Path(local_dir).expanduser()
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def _req(self, url: str, timeout: float = 30.0) -> bytes:
        req = Request(url, headers={"Authorization": f"Bearer {self._token}"})
        with urlopen(req, timeout=timeout) as r:
            return r.read()

    def run(self) -> None:
        try:
            list_url = f"{self._url}/media/list"
            if self._alias:
                list_url += f"?alias={self._alias}"
            manifest = json.loads(self._req(list_url))
            files = manifest.get("files", [])
        except HTTPError as e:
            self.failed.emit(f"Manifest HTTP {e.code}: {e.reason}")
            return
        except URLError as e:
            self.failed.emit(f"Manifest connection error: {e.reason}")
            return
        except Exception as e:
            self.failed.emit(f"Manifest error: {e}")
            return

        if not files:
            self.finished.emit(0, 0, 0)
            return

        self._local_dir.mkdir(parents=True, exist_ok=True)
        synced = skipped = errors = 0
        total = len(files)

        for idx, entry in enumerate(files, 1):
            if self._cancelled:
                break
            remote_rel = entry["path"]
            size = int(entry.get("size", 0))
            # When filtered by alias, drop the alias prefix so the plugin's
            # per-alias THUMB_PATH sees the expected <site_slug>/... layout.
            local_rel = remote_rel
            if self._alias and local_rel.startswith(f"{self._alias}/"):
                local_rel = local_rel[len(self._alias) + 1:]
            local_path = self._local_dir / local_rel
            if local_path.is_file() and local_path.stat().st_size == size:
                skipped += 1
                self.progress.emit(idx, total, f"skip  {local_rel}")
                continue
            try:
                content = self._req(
                    f"{self._url}/media/{remote_rel}", timeout=120.0
                )
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(content)
                synced += 1
                self.progress.emit(
                    idx, total, f"ok    {local_rel}  ({size} B)"
                )
            except HTTPError as e:
                errors += 1
                self.progress.emit(
                    idx, total, f"ERR   {remote_rel}: HTTP {e.code} {e.reason}"
                )
            except URLError as e:
                errors += 1
                self.progress.emit(
                    idx, total, f"ERR   {remote_rel}: {e.reason}"
                )
            except Exception as e:
                errors += 1
                self.progress.emit(idx, total, f"ERR   {remote_rel}: {e}")

        self.finished.emit(synced, skipped, errors)


class BotSyncDialog(QDialog):
    """Config + run UI for bot media sync. One-shot operation — the user
    clicks 'Run sync now' and waits; a thread does the work so the
    QGIS UI stays responsive. Closing the dialog mid-sync cancels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HFF — Bot Media Sync")
        self.resize(640, 520)
        self._worker: BotSyncWorker | None = None
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QLabel(
            "Pull media files from the HFF Telegram bot to a local "
            "directory. Set the Bot URL, Bearer token, optionally an "
            "alias to filter, and the local THUMB_PATH destination. "
            "Settings persist across sessions."
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        form = QFormLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(
            "https://hff-telegram-bot-production.up.railway.app"
        )
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText("MEDIA_BEARER_TOKEN from Railway")
        self.alias_edit = QLineEdit()
        self.alias_edit.setPlaceholderText("optional — e.g. hff-database01")

        local_row = QHBoxLayout()
        self.local_edit = QLineEdit()
        self.local_edit.setPlaceholderText(
            "must match THUMB_PATH in config.cfg (trailing slash OK)"
        )
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._pick_dir)
        local_row.addWidget(self.local_edit)
        local_row.addWidget(browse_btn)

        form.addRow("Bot URL:", self.url_edit)
        form.addRow("Bearer token:", self.token_edit)
        form.addRow("Alias (filter):", self.alias_edit)
        form.addRow("Local directory:", local_row)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save settings")
        self.save_btn.clicked.connect(self._save_settings)
        self.run_btn = QPushButton("Run sync now")
        self.run_btn.setDefault(True)
        self.run_btn.clicked.connect(self._start_sync)
        self.cancel_btn = QPushButton("Cancel sync")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_sync)
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.run_btn)
        layout.addLayout(btn_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Sync log will appear here.")
        layout.addWidget(self.log)

        close_row = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_row.addStretch(1)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

    def _pick_dir(self) -> None:
        start = self.local_edit.text().strip() or os.path.expanduser("~")
        d = QFileDialog.getExistingDirectory(
            self, "Select local THUMB_PATH directory", start
        )
        if d:
            self.local_edit.setText(d)

    def _load_settings(self) -> None:
        s = BotSyncSettings.load()
        self.url_edit.setText(s["url"])
        self.token_edit.setText(s["token"])
        self.alias_edit.setText(s["alias"])
        self.local_edit.setText(s["local_dir"])

    def _save_settings(self) -> None:
        BotSyncSettings.save(
            url=self.url_edit.text().strip(),
            token=self.token_edit.text().strip(),
            alias=self.alias_edit.text().strip(),
            local_dir=self.local_edit.text().strip(),
        )
        QMessageBox.information(self, "Saved", "Bot sync settings saved.")

    def _start_sync(self) -> None:
        url = self.url_edit.text().strip()
        token = self.token_edit.text().strip()
        alias = self.alias_edit.text().strip()
        local = self.local_edit.text().strip()
        if not url or not token or not local:
            QMessageBox.warning(
                self,
                "Missing fields",
                "Bot URL, Bearer token and Local directory are all required.",
            )
            return
        # Persist whatever the user typed before kicking off the worker.
        BotSyncSettings.save(url, token, alias, local)
        self.progress_bar.setValue(0)
        self.log.clear()
        self.run_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self._worker = BotSyncWorker(url, token, alias, local, parent=self)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _cancel_sync(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            self.log.appendPlainText("— cancel requested —")
            self.cancel_btn.setEnabled(False)

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        pct = int(current * 100 / total) if total else 0
        self.progress_bar.setValue(pct)
        self.log.appendPlainText(msg)

    def _on_finished(self, synced: int, skipped: int, errors: int) -> None:
        self.log.appendPlainText(
            f"— done. synced={synced} skipped={skipped} errors={errors}"
        )
        self.run_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None

    def _on_failed(self, err: str) -> None:
        QMessageBox.critical(self, "Sync failed", err)
        self.log.appendPlainText(f"FAILED: {err}")
        self.run_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None

    def closeEvent(self, event) -> None:
        # If a sync is in flight, cancel it so we don't leak a QThread.
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)
        super().closeEvent(event)
