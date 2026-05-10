"""HFF Thesaurus management dialog.

Edits `hff_system__thesaurus_sigle` rows. Each row maps a (nome_tabella, tipologia_sigla,
lingua) tuple to a `sigla_estesa` value that will appear as a dropdown item in the
form combobox for that field. See modules/utility/hff_combobox_defaults.py for the
in-code seed values that are auto-imported into this table on first open.

The dialog is built programmatically — no .ui file — because the layout is simple
and a hand-coded form keeps the file small (~350 lines vs the 2920-line pyarchinit
equivalent).
"""
from __future__ import absolute_import
import csv
import os

from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLabel,
    QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QFileDialog, QWidget,
    QSizePolicy,
)
from qgis.core import QgsSettings

from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.entities.HFF_THESAURUS_SIGLE import HFF_THESAURUS_SIGLE
from ..modules.utility.hff_combobox_defaults import DEFAULTS

ANY = "(all)"
TABLE_NAME = 'hff_system__thesaurus_sigle'
ID_COLUMN = 'id_thesaurus_sigle'
COLUMNS = ('ID', 'Table', 'Field', 'Value', 'Language', 'Description')


class HffThesaurusDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HFF — Thesaurus")
        self.resize(900, 600)
        try:
            self.setWindowIcon(QIcon(os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'resources', 'icons', 'thesaurusicon.png')))
        except Exception:
            pass

        self.DB_MANAGER = None
        try:
            conn_str = Connection().conn_str()
            self.DB_MANAGER = Hff_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as exc:
            QMessageBox.critical(self, "Thesaurus",
                                 "Cannot connect to the database:\n%s" % exc)
            self.DB_MANAGER = None

        self.L = QgsSettings().value("locale/userLocale", "en", type=str)[:2]

        self._build_ui()
        if self.DB_MANAGER is not None:
            self._maybe_seed()
            self._reload_filters()
            self._reload_rows()

    # ---------- UI ------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)

        # Filter row -------------------------------------------------------
        filt = QGroupBox("Filter")
        flayout = QFormLayout(filt)
        self.cb_table = QComboBox()
        self.cb_table.setEditable(False)
        self.cb_table.currentIndexChanged.connect(self._reload_rows)
        flayout.addRow("Table:", self.cb_table)

        self.cb_lang = QComboBox()
        self.cb_lang.setEditable(False)
        self.cb_lang.currentIndexChanged.connect(self._reload_rows)
        flayout.addRow("Language:", self.cb_lang)

        self.cb_field = QComboBox()
        self.cb_field.setEditable(False)
        self.cb_field.currentIndexChanged.connect(self._reload_rows)
        flayout.addRow("Field:", self.cb_field)

        root.addWidget(filt)

        # Table -----------------------------------------------------------
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked
                                   | QAbstractItemView.EditKeyPressed
                                   | QAbstractItemView.AnyKeyPressed)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self.table)

        # Buttons ---------------------------------------------------------
        btnrow = QHBoxLayout()
        for label, slot in [
            ("Add row",      self._on_add),
            ("Delete row",   self._on_delete),
            ("Save changes", self._on_save),
            ("Reload",       self._reload_rows),
            ("Import CSV",   self._on_import_csv),
            ("Export CSV",   self._on_export_csv),
            ("Re-seed defaults", self._on_reseed),
            ("Close",        self.accept),
        ]:
            b = QPushButton(label)
            b.clicked.connect(slot)
            btnrow.addWidget(b)
        root.addLayout(btnrow)

        # Status ----------------------------------------------------------
        self.status = QLabel()
        self.status.setStyleSheet("color: #666;")
        root.addWidget(self.status)

        # State -----------------------------------------------------------
        self._suspend_change_signal = False
        self._dirty_ids = set()
        self._new_rows = []  # row indices for not-yet-persisted entries

    # ---------- Helpers --------------------------------------------------

    def _set_status(self, text, ok=True):
        self.status.setStyleSheet(
            "color: %s;" % ("#2a7a2a" if ok else "#a14545"))
        self.status.setText(text)

    def _reload_filters(self):
        self._suspend_change_signal = True
        try:
            tables = sorted({t for (t, _f) in DEFAULTS.keys()})
            for entry in [ANY] + tables:
                self.cb_table.addItem(entry)
            for lang in [ANY, 'en', 'ar-lb', 'it']:
                self.cb_lang.addItem(lang)
            self.cb_field.addItem(ANY)
        finally:
            self._suspend_change_signal = False

    def _refresh_field_combo(self):
        """Field combo depends on the selected table."""
        self._suspend_change_signal = True
        try:
            self.cb_field.clear()
            self.cb_field.addItem(ANY)
            sel_table = self.cb_table.currentText()
            fields = sorted({f for (t, f) in DEFAULTS.keys()
                             if sel_table in (ANY, t)})
            for f in fields:
                self.cb_field.addItem(f)
        finally:
            self._suspend_change_signal = False

    def _all_rows(self):
        """Fetch every row in the thesaurus table via direct ORM session."""
        if self.DB_MANAGER is None:
            return []
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=self.DB_MANAGER.engine)
        session = Session()
        try:
            return session.query(HFF_THESAURUS_SIGLE).all()
        except Exception as exc:
            self._set_status("Read failed: %s" % exc, ok=False)
            return []
        finally:
            session.close()

    def _filtered_rows(self):
        rows = self._all_rows()
        sel_table = self.cb_table.currentText()
        sel_lang = self.cb_lang.currentText()
        sel_field = self.cb_field.currentText()
        out = []
        for r in rows:
            if sel_table != ANY and (r.nome_tabella or '') != sel_table:
                continue
            if sel_lang != ANY and (r.lingua or '') != sel_lang:
                continue
            if sel_field != ANY and (r.tipologia_sigla or '') != sel_field:
                continue
            out.append(r)
        return out

    def _reload_rows(self):
        if self._suspend_change_signal:
            return
        # Refresh dependent dropdown when table filter changes
        self._refresh_field_combo()

        self._suspend_change_signal = True
        try:
            self.table.setRowCount(0)
            self._dirty_ids = set()
            self._new_rows = []
            rows = self._filtered_rows()
            for r in rows:
                self._append_table_row(
                    r.id_thesaurus_sigle,
                    r.nome_tabella or '',
                    r.tipologia_sigla or '',
                    r.sigla_estesa or '',
                    r.lingua or '',
                    r.descrizione or '',
                )
            self._set_status("%d row(s)." % len(rows))
        finally:
            self._suspend_change_signal = False

    def _append_table_row(self, id_, nome_tabella, tipologia, sigla_estesa, lingua, descrizione):
        r = self.table.rowCount()
        self.table.insertRow(r)
        items = [
            QTableWidgetItem("" if id_ is None else str(id_)),
            QTableWidgetItem(nome_tabella),
            QTableWidgetItem(tipologia),
            QTableWidgetItem(sigla_estesa),
            QTableWidgetItem(lingua),
            QTableWidgetItem(descrizione),
        ]
        # ID column not editable
        items[0].setFlags(items[0].flags() & ~Qt.ItemIsEditable)
        for c, it in enumerate(items):
            self.table.setItem(r, c, it)

    # ---------- Slots ----------------------------------------------------

    def _on_item_changed(self, item):
        if self._suspend_change_signal:
            return
        row = item.row()
        id_text = self.table.item(row, 0).text()
        if id_text:
            try:
                self._dirty_ids.add(int(id_text))
            except ValueError:
                pass
        # if no ID, this is a brand-new row — already in self._new_rows

    def _on_add(self):
        sel_table = self.cb_table.currentText()
        sel_field = self.cb_field.currentText()
        sel_lang = self.cb_lang.currentText()
        self._suspend_change_signal = True
        try:
            self._append_table_row(
                None,
                '' if sel_table == ANY else sel_table,
                '' if sel_field == ANY else sel_field,
                '',
                'en' if sel_lang == ANY else sel_lang,
                '',
            )
            self._new_rows.append(self.table.rowCount() - 1)
        finally:
            self._suspend_change_signal = False
        self._set_status("New row added (not saved yet).")

    def _on_delete(self):
        rows = sorted({i.row() for i in self.table.selectedItems()}, reverse=True)
        if not rows:
            return
        if QMessageBox.question(
                self, "Delete",
                "Delete %d selected row(s)?" % len(rows),
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        deleted = 0
        for r in rows:
            id_text = self.table.item(r, 0).text() if self.table.item(r, 0) else ''
            if id_text:
                try:
                    self.DB_MANAGER.delete_one_record(
                        TABLE_NAME, ID_COLUMN, int(id_text))
                    deleted += 1
                except Exception as exc:
                    self._set_status(
                        "Delete failed for ID %s: %s" % (id_text, exc),
                        ok=False)
                    return
            self.table.removeRow(r)
        self._set_status("Deleted %d row(s)." % deleted)

    def _on_save(self):
        if self.DB_MANAGER is None:
            return
        saved = 0
        # Persist NEW rows
        for r in list(self._new_rows):
            vals = self._row_values(r)
            if not vals['nome_tabella'] or not vals['tipologia_sigla'] or not vals['sigla_estesa']:
                self._set_status(
                    "Skipped row %d: Table, Field and Value are required." % (r + 1),
                    ok=False)
                continue
            try:
                ent = HFF_THESAURUS_SIGLE(
                    None,
                    vals['nome_tabella'],
                    self._derive_sigla(vals['sigla_estesa']),
                    vals['sigla_estesa'],
                    vals['descrizione'],
                    vals['tipologia_sigla'],
                    vals['lingua'] or 'en',
                )
                self.DB_MANAGER.insert_data_session(ent)
                saved += 1
            except Exception as exc:
                self._set_status(
                    "Insert failed: %s" % exc, ok=False)
                return
        # Persist UPDATES
        for id_ in list(self._dirty_ids):
            r = self._find_row_by_id(id_)
            if r < 0:
                continue
            vals = self._row_values(r)
            try:
                self.DB_MANAGER.update(
                    'HFF_THESAURUS_SIGLE', ID_COLUMN, [id_],
                    ['nome_tabella', 'sigla', 'sigla_estesa',
                     'descrizione', 'tipologia_sigla', 'lingua'],
                    [vals['nome_tabella'],
                     self._derive_sigla(vals['sigla_estesa']),
                     vals['sigla_estesa'],
                     vals['descrizione'],
                     vals['tipologia_sigla'],
                     vals['lingua'] or 'en'])
                saved += 1
            except Exception as exc:
                self._set_status(
                    "Update failed for ID %s: %s" % (id_, exc), ok=False)
                return
        self._set_status("Saved %d row(s)." % saved)
        self._reload_rows()

    def _derive_sigla(self, sigla_estesa):
        """Build a 3-char sigla from the value (legacy column, mostly ignored)."""
        s = (sigla_estesa or '').strip().upper()
        return (s[:3] or 'XXX')

    def _row_values(self, r):
        def _g(c):
            it = self.table.item(r, c)
            return it.text() if it else ''
        return {
            'nome_tabella':    _g(1).strip(),
            'tipologia_sigla': _g(2).strip(),
            'sigla_estesa':    _g(3).strip(),
            'lingua':          _g(4).strip(),
            'descrizione':     _g(5).strip(),
        }

    def _find_row_by_id(self, id_):
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if it and it.text() == str(id_):
                return r
        return -1

    def _on_import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV files (*.csv);;All files (*)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', newline='') as fh:
                reader = csv.DictReader(fh)
                added = 0
                for row in reader:
                    nome_tabella = (row.get('nome_tabella') or row.get('table') or '').strip()
                    tipologia = (row.get('tipologia_sigla') or row.get('field') or '').strip()
                    valore = (row.get('sigla_estesa') or row.get('value') or '').strip()
                    lingua = (row.get('lingua') or row.get('language') or 'en').strip()
                    descrizione = (row.get('descrizione') or row.get('description') or '').strip()
                    if not (nome_tabella and tipologia and valore):
                        continue
                    ent = HFF_THESAURUS_SIGLE(
                        None, nome_tabella, self._derive_sigla(valore),
                        valore, descrizione, tipologia, lingua)
                    self.DB_MANAGER.insert_data_session(ent)
                    added += 1
        except Exception as exc:
            self._set_status("Import failed: %s" % exc, ok=False)
            return
        self._set_status("Imported %d row(s) from %s." % (added, path))
        self._reload_rows()

    def _on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "thesaurus.csv", "CSV files (*.csv)")
        if not path:
            return
        rows = self._filtered_rows()
        try:
            with open(path, 'w', encoding='utf-8', newline='') as fh:
                w = csv.writer(fh)
                w.writerow(['id_thesaurus_sigle', 'nome_tabella', 'tipologia_sigla',
                            'sigla_estesa', 'lingua', 'descrizione'])
                for r in rows:
                    w.writerow([r.id_thesaurus_sigle, r.nome_tabella,
                                r.tipologia_sigla, r.sigla_estesa,
                                r.lingua, r.descrizione or ''])
        except Exception as exc:
            self._set_status("Export failed: %s" % exc, ok=False)
            return
        self._set_status("Exported %d row(s) to %s." % (len(rows), path))

    def _on_reseed(self):
        if QMessageBox.question(
                self, "Re-seed",
                "Re-insert any default entries that are missing? "
                "Existing values are not touched.",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        added = self._seed_defaults(force=True)
        self._set_status("Seeded %d new entries." % added)
        self._reload_rows()

    # ---------- Seed -----------------------------------------------------

    def _maybe_seed(self):
        """If the table is empty (likely a fresh DB), seed it from DEFAULTS."""
        rows = self._all_rows()
        if rows:
            return 0
        return self._seed_defaults(force=False)

    def _seed_defaults(self, force=False):
        """Insert DEFAULTS values that are not already present (en locale).

        force=False: only seeds when the table is empty (used at first open).
        force=True : always inserts the missing ones (used by Re-seed button).
        """
        if self.DB_MANAGER is None:
            return 0
        existing = set()
        if force:
            for r in self._all_rows():
                existing.add((r.nome_tabella or '',
                              r.tipologia_sigla or '',
                              r.sigla_estesa or '',
                              r.lingua or ''))
        added = 0
        for (table, field), values in DEFAULTS.items():
            for v in values:
                key = (table, field, v, 'en')
                if force and key in existing:
                    continue
                ent = HFF_THESAURUS_SIGLE(
                    None, table, self._derive_sigla(v), v, '', field, 'en')
                try:
                    self.DB_MANAGER.insert_data_session(ent)
                    added += 1
                except Exception:
                    # already there? skip silently
                    continue
        return added
