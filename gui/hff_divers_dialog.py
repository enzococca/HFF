# -*- coding: utf-8 -*-
"""HFF — modal dialogs for adding / editing a diver row and its
segment rows in the divelog form.

Two dialogs:
- AddEditSegmentDialog: a single segment (mix, bar_start, bar_end,
  delta_p). Used both for creating a new segment and editing an
  existing one. Pre-fill via the optional `segment` ctor argument.
- AddEditDiverDialog: a diver (name, role, time_in, time_out,
  max_depth) plus an embedded list of segments. Add / edit / remove
  segments via inline buttons that pop AddEditSegmentDialog.

Both expose `value()` after `exec_() == Accepted` returning a plain
dict the calling form can serialize into the wizard's payload.
"""
from __future__ import annotations

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class AddEditSegmentDialog(QDialog):
    """Modal editor for a single diver segment."""

    def __init__(self, parent=None, segment=None):
        super().__init__(parent)
        self.setWindowTitle("Diver segment")
        self.setModal(True)
        layout = QFormLayout(self)
        seg = segment or {}
        self.mix_edit = QLineEdit(seg.get("mix", "") or "")
        self.bar_start_edit = QLineEdit(seg.get("bar_start", "") or "")
        self.bar_end_edit = QLineEdit(seg.get("bar_end", "") or "")
        self.delta_p_edit = QLineEdit(seg.get("delta_p", "") or "")
        layout.addRow("Breathing mix:", self.mix_edit)
        layout.addRow("Bar start:", self.bar_start_edit)
        layout.addRow("Bar end:", self.bar_end_edit)
        layout.addRow("Delta P (auto):", self.delta_p_edit)

        # Auto-compute Delta P = bar_start - bar_end. textEdited fires only
        # on real user input, so a manual edit of delta_p latches the field
        # and stops auto-fill from clobbering it.
        self._delta_p_user_edited = bool(seg.get("delta_p"))
        self.delta_p_edit.textEdited.connect(self._mark_delta_p_user_edited)
        self.bar_start_edit.textEdited.connect(self._auto_delta_p)
        self.bar_end_edit.textEdited.connect(self._auto_delta_p)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _mark_delta_p_user_edited(self, _text):
        self._delta_p_user_edited = True

    def _auto_delta_p(self, _text=None):
        if self._delta_p_user_edited:
            return
        try:
            start = float(self.bar_start_edit.text().strip())
            end = float(self.bar_end_edit.text().strip())
        except (TypeError, ValueError):
            return
        delta = start - end
        # Trim trailing zeros from int-valued floats: 50.0 -> "50".
        formatted = ("%g" % delta)
        self.delta_p_edit.setText(formatted)

    def value(self):
        return {
            "mix": self.mix_edit.text().strip() or None,
            "bar_start": self.bar_start_edit.text().strip() or None,
            "bar_end": self.bar_end_edit.text().strip() or None,
            "delta_p": self.delta_p_edit.text().strip() or None,
        }


class AddEditDiverDialog(QDialog):
    """Modal editor for a diver row + its embedded segment list."""

    def __init__(self, parent=None, diver=None):
        super().__init__(parent)
        self.setWindowTitle("Diver")
        self.setModal(True)
        self.resize(480, 380)

        outer = QVBoxLayout(self)
        form = QFormLayout()
        d = diver or {}
        self.name_edit = QLineEdit(d.get("name", "") or "")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["", "lead", "buddy", "additional"])
        if d.get("role"):
            idx = self.role_combo.findText(d["role"])
            if idx >= 0:
                self.role_combo.setCurrentIndex(idx)
        self.time_in_edit = QLineEdit(d.get("time_in", "") or "")
        self.time_out_edit = QLineEdit(d.get("time_out", "") or "")
        md = d.get("max_depth")
        self.max_depth_edit = QLineEdit("" if md is None else str(md))
        form.addRow("Name:", self.name_edit)
        form.addRow("Role:", self.role_combo)
        form.addRow("Time in:", self.time_in_edit)
        form.addRow("Time out:", self.time_out_edit)
        form.addRow("Max depth (m):", self.max_depth_edit)
        outer.addLayout(form)

        outer.addWidget(QLabel("Segments:"))
        self.segments_list = QListWidget()
        self._segments = list(d.get("segments", []) or [])
        self._refresh_segments()
        outer.addWidget(self.segments_list)

        seg_btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Add segment")
        add_btn.clicked.connect(self._add_segment)
        edit_btn = QPushButton("Edit selected")
        edit_btn.clicked.connect(self._edit_segment)
        rm_btn = QPushButton("Remove selected")
        rm_btn.clicked.connect(self._remove_segment)
        seg_btn_row.addWidget(add_btn)
        seg_btn_row.addWidget(edit_btn)
        seg_btn_row.addWidget(rm_btn)
        seg_btn_row.addStretch(1)
        outer.addLayout(seg_btn_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def _refresh_segments(self):
        self.segments_list.clear()
        for i, seg in enumerate(self._segments):
            label = (
                "#{i}  {mix}  {start} → {end}  ΔP {dp}"
            ).format(
                i=i,
                mix=seg.get("mix") or "–",
                start=seg.get("bar_start") or "–",
                end=seg.get("bar_end") or "–",
                dp=seg.get("delta_p") or "–",
            )
            item = QListWidgetItem(label)
            item.setData(0x0100, i)  # Qt.UserRole
            self.segments_list.addItem(item)

    def _add_segment(self):
        dlg = AddEditSegmentDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._segments.append(dlg.value())
            self._refresh_segments()

    def _edit_segment(self):
        sel = self.segments_list.currentItem()
        if sel is None:
            return
        idx = sel.data(0x0100)
        if idx is None:
            return
        dlg = AddEditSegmentDialog(self, self._segments[idx])
        if dlg.exec_() == QDialog.Accepted:
            self._segments[idx] = dlg.value()
            self._refresh_segments()

    def _remove_segment(self):
        sel = self.segments_list.currentItem()
        if sel is None:
            return
        idx = sel.data(0x0100)
        if idx is None:
            return
        del self._segments[idx]
        self._refresh_segments()

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Missing", "Diver name is required.")
            return
        self.accept()

    def value(self):
        md_text = self.max_depth_edit.text().strip()
        return {
            "name": self.name_edit.text().strip(),
            "role": self.role_combo.currentText() or None,
            "time_in": self.time_in_edit.text().strip() or None,
            "time_out": self.time_out_edit.text().strip() or None,
            "max_depth": md_text or None,
            "segments": list(self._segments),
        }
