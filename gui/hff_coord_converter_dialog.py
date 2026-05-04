# -*- coding: utf-8 -*-
"""HFF Coordinate Converter dialog.

Convert coordinates between DDM (Garmin), DMS, decimal degrees and UTM
using the shared pure module ``modules.utility.coord_converter``.

Built with ``qgis.PyQt`` — works on both Qt5 (current QGIS LTR) and
Qt6 (QGIS 3.99+/QGIS 4) without source changes.
"""
from __future__ import annotations

from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from modules.utility.coord_converter import (
    HAS_PYPROJ,
    convert_all,
)


class CoordConverterDialog(QDialog):
    """DDM / DMS / DD / UTM converter. All fields read-only output;
    one Convert button + one Copy button per output row."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HFF — Coordinate Converter")
        self.resize(660, 520)
        self._outputs: dict[str, QLineEdit] = {}
        self._last_result: dict | None = None
        self._build_ui()
        self.lat_input.setText("N 34 01.825")
        self.lon_input.setText("E 035 37.349")
        self._convert()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        # ---- Input ----
        in_box = QGroupBox("Input")
        form = QFormLayout()
        self.lat_input = QLineEdit()
        self.lon_input = QLineEdit()
        form.addRow("Latitude:", self.lat_input)
        form.addRow("Longitude:", self.lon_input)
        info = QLabel(
            "Accepted formats: <code>N 34 01.825</code> (DDM Garmin) · "
            "<code>34°1'49.5\"N</code> (DMS) · <code>34.030417</code> (DD)"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: gray;")
        form.addRow(info)
        in_box.setLayout(form)
        root.addWidget(in_box)

        # ---- UTM options ----
        utm_box = QGroupBox("UTM options")
        utm_h = QHBoxLayout()
        utm_h.addWidget(QLabel("Zone:"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItem("Auto")
        for z in range(1, 61):
            self.zone_combo.addItem(str(z))
        utm_h.addWidget(self.zone_combo)
        engine_label = QLabel(
            f"  Engine: {'pyproj' if HAS_PYPROJ else 'pure-python (no pyproj)'}"
        )
        engine_label.setStyleSheet("color: gray;")
        utm_h.addWidget(engine_label)
        utm_h.addStretch(1)
        utm_box.setLayout(utm_h)
        root.addWidget(utm_box)

        # ---- Buttons ----
        btn_row = QHBoxLayout()
        convert_btn = QPushButton("Convert")
        clear_btn = QPushButton("Clear")
        copy_dd_btn = QPushButton("Copy DD")
        copy_utm_btn = QPushButton("Copy UTM (X, Y)")
        btn_row.addWidget(convert_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(copy_dd_btn)
        btn_row.addWidget(copy_utm_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)

        # ---- Output ----
        out_box = QGroupBox("Results")
        out_form = QFormLayout()
        for label, key in [
            ("DD (lat, lon):", "dd"),
            ("DDM (Garmin):", "ddm"),
            ("DMS:", "dms"),
            ("GIS (lon, lat):", "gis"),
            ("UTM:", "utm_text"),
            ("EPSG:", "epsg_text"),
            ("Google Maps:", "gmaps_url"),
        ]:
            entry = QLineEdit()
            entry.setReadOnly(True)
            self._outputs[key] = entry
            out_form.addRow(label, entry)
        out_box.setLayout(out_form)
        root.addWidget(out_box)

        # ---- Wiring ----
        convert_btn.clicked.connect(self._convert)
        clear_btn.clicked.connect(self._clear)
        copy_dd_btn.clicked.connect(self._copy_dd)
        copy_utm_btn.clicked.connect(self._copy_utm)
        self.lat_input.returnPressed.connect(self._convert)
        self.lon_input.returnPressed.connect(self._convert)
        self.zone_combo.currentIndexChanged.connect(self._convert)

    # ---- Actions ----

    def _convert(self) -> None:
        lat_text = self.lat_input.text()
        lon_text = self.lon_input.text()
        if not lat_text.strip() or not lon_text.strip():
            return
        zone_sel = self.zone_combo.currentText()
        forced_zone = None if zone_sel == "Auto" else int(zone_sel)
        try:
            r = convert_all(lat_text, lon_text, zone=forced_zone)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid coordinate", str(e))
            return
        self._last_result = r

        utm_extra = ""
        if forced_zone is not None and forced_zone != r["auto_zone"]:
            utm_extra = f"  (auto zone: {r['auto_zone']}{r['utm_hemi']})"
        for key in ("dd", "ddm", "dms", "gis", "epsg_text", "gmaps_url"):
            self._outputs[key].setText(r[key])
        self._outputs["utm_text"].setText(r["utm_text"] + utm_extra)

    def _clear(self) -> None:
        self.lat_input.clear()
        self.lon_input.clear()
        for entry in self._outputs.values():
            entry.clear()
        self._last_result = None
        self.lat_input.setFocus()

    def _copy_dd(self) -> None:
        if self._last_result is None:
            return
        QApplication.clipboard().setText(self._last_result["dd"])

    def _copy_utm(self) -> None:
        if self._last_result is None:
            return
        # X, Y form for pasting into QGIS coordinate input
        text = (
            f"{self._last_result['utm_easting']:.0f}, "
            f"{self._last_result['utm_northing']:.0f}"
        )
        QApplication.clipboard().setText(text)
