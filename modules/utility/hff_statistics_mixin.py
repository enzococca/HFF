# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Statistics Mixin for Forms
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
import csv
import statistics as _stats
import tempfile
from datetime import datetime
from collections import Counter

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QMessageBox, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QComboBox, QLabel, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QHeaderView,
)
from qgis.core import QgsSettings

from .hff_i18n import tr


class StatisticsMixin:
    """Mixin class that adds a pyarchinit-style statistics tab to HFF forms.

    Usage:
        class MyForm(QDialog, StatisticsMixin):
            def __init__(self):
                super().__init__()
                self.init_statistics(MY_STATS_FIELDS)
    """

    STATS_FIELDS = {}
    NUMERIC_FIELDS = ()

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------
    def init_statistics(self, fields_config=None, numeric_fields=None):
        if fields_config:
            self.STATS_FIELDS = fields_config
        if numeric_fields:
            self.NUMERIC_FIELDS = tuple(numeric_fields)

        self.stats_data = []
        self.stats_summary_data = []
        self.stats_measures_data = []

        if hasattr(self, 'comboBox_stats_field'):
            self.setup_stats_field_combo()

        self.setup_statistics_tab_pyarchinit_style()

    def setup_stats_field_combo(self):
        if not hasattr(self, 'comboBox_stats_field'):
            return
        self.comboBox_stats_field.clear()
        for display_name in self.STATS_FIELDS.keys():
            self.comboBox_stats_field.addItem(display_name)

    # ------------------------------------------------------------------
    # UI builder (pyarchinit pattern)
    # ------------------------------------------------------------------
    def _find_statistics_tab(self):
        """Locate the statistics tab, tolerating different objectNames across forms."""
        # Direct well-known names
        for name in ('tab_statistics', 'tabWidgetPage_Statistics',
                     'tabWidgetPage_statistics', 'tab_statistic'):
            tab = self.findChild(QWidget, name)
            if tab is not None:
                return tab
        # Fallback: walk up from widget_stats until we find the tab page
        chart = self.findChild(QWidget, 'widget_stats')
        if chart is None:
            return None
        # Climb parents until we hit the widget that is a direct child of a QTabWidget
        from qgis.PyQt.QtWidgets import QTabWidget
        w = chart
        while w is not None:
            parent = w.parentWidget()
            if isinstance(parent, QTabWidget):
                return w
            w = parent
        return None

    def setup_statistics_tab_pyarchinit_style(self):
        tab = self._find_statistics_tab()
        if tab is None:
            return

        # Preserve existing chart widget; we'll reparent it into the new splitter.
        chart_widget = self.findChild(QWidget, 'widget_stats')

        # Hide the legacy controls — they are replaced by the new ones
        for name in (
            'comboBox_stats_field', 'comboBox_stats_type',
            'pushButton_quant', 'pushButton_export_stats',
        ):
            w = self.findChild(QWidget, name)
            if w is not None:
                w.hide()

        # Purge the existing layout of tab_statistics (if any)
        old_layout = tab.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                w = item.widget()
                if w is not None and w is not chart_widget:
                    w.hide()
            # Replace layout: Qt doesn't let us delete a set layout, so add to it
            main_layout = old_layout
        else:
            main_layout = QVBoxLayout(tab)

        splitter = QSplitter(Qt.Horizontal)

        # ---------------- LEFT PANEL ----------------
        left = QWidget()
        left_layout = QVBoxLayout(left)

        controls = QHBoxLayout()
        self.pushButton_refresh_stats = QPushButton(tr('refresh_statistics', 'Refresh Statistics'))
        self.pushButton_refresh_stats.setMaximumWidth(180)
        self.pushButton_refresh_stats.clicked.connect(self.calculate_statistics)
        controls.addWidget(self.pushButton_refresh_stats)

        controls.addWidget(QLabel(tr('analysis_type', 'Analysis:')))
        self.comboBox_stats_analysis = QComboBox()
        for display_name in self.STATS_FIELDS.keys():
            self.comboBox_stats_analysis.addItem(display_name)
        self.comboBox_stats_analysis.currentIndexChanged.connect(self.on_stats_analysis_changed)
        controls.addWidget(self.comboBox_stats_analysis)

        self.comboBox_chart_type = QComboBox()
        self.comboBox_chart_type.addItems([
            tr('chart_bar', 'Bar'),
            tr('chart_pie', 'Pie'),
        ])
        self.comboBox_chart_type.currentIndexChanged.connect(self.on_stats_analysis_changed)
        controls.addWidget(self.comboBox_chart_type)
        controls.addStretch()
        left_layout.addLayout(controls)

        self.stats_subtabs = QTabWidget()

        # --- Summary tab ---
        summary = QWidget()
        sl = QVBoxLayout(summary)
        self.tableWidget_stats_summary = QTableWidget()
        self.tableWidget_stats_summary.setColumnCount(3)
        self.tableWidget_stats_summary.setHorizontalHeaderLabels([
            tr('category', 'Category'),
            tr('count', 'Count'),
            tr('percentage', 'Percentage'),
        ])
        self.tableWidget_stats_summary.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_stats_summary.setAlternatingRowColors(True)
        sl.addWidget(self.tableWidget_stats_summary)
        self.stats_subtabs.addTab(summary, tr('summary', 'Summary'))

        # --- Measures tab ---
        measures = QWidget()
        ml = QVBoxLayout(measures)
        self.tableWidget_stats_measures = QTableWidget()
        self.tableWidget_stats_measures.setColumnCount(5)
        self.tableWidget_stats_measures.setHorizontalHeaderLabels([
            tr('measure', 'Measure'),
            tr('min', 'Min'),
            tr('max', 'Max'),
            tr('mean', 'Mean'),
            tr('median', 'Median'),
        ])
        self.tableWidget_stats_measures.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_stats_measures.setAlternatingRowColors(True)
        ml.addWidget(self.tableWidget_stats_measures)
        self.stats_subtabs.addTab(measures, tr('statistics', 'Statistics'))

        # --- AI Report tab ---
        ai = QWidget()
        al = QVBoxLayout(ai)
        ai_buttons = QHBoxLayout()
        self.pushButton_generate_ai_report = QPushButton(tr('generate_ai_report', 'Generate AI Report'))
        self.pushButton_generate_ai_report.clicked.connect(self.generate_ai_report)
        ai_buttons.addWidget(self.pushButton_generate_ai_report)
        self.pushButton_export_stats_pdf = QPushButton(tr('export_pdf', 'Export PDF'))
        self.pushButton_export_stats_pdf.clicked.connect(self.export_statistics_pdf)
        ai_buttons.addWidget(self.pushButton_export_stats_pdf)
        self.pushButton_export_stats_csv = QPushButton(tr('export_csv', 'Export CSV'))
        self.pushButton_export_stats_csv.clicked.connect(self.on_pushButton_export_stats_pressed)
        ai_buttons.addWidget(self.pushButton_export_stats_csv)
        ai_buttons.addStretch()
        al.addLayout(ai_buttons)

        self.textEdit_ai_report = QTextEdit()
        self.textEdit_ai_report.setPlaceholderText(
            tr('ai_placeholder', 'AI report will be displayed here after generation…')
        )
        al.addWidget(self.textEdit_ai_report)
        self.stats_subtabs.addTab(ai, tr('ai_report', 'AI Report'))

        left_layout.addWidget(self.stats_subtabs)
        splitter.addWidget(left)

        # ---------------- RIGHT PANEL (chart) ----------------
        if chart_widget is not None:
            chart_widget.setParent(None)
            splitter.addWidget(chart_widget)
        else:
            splitter.addWidget(QWidget())

        splitter.setSizes([450, 550])
        main_layout.addWidget(splitter)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def get_stats_records(self):
        if hasattr(self, 'DATA_LIST'):
            return self.DATA_LIST
        return []

    def _field_value(self, record, field_name):
        if record is None:
            return None
        if hasattr(record, field_name):
            return getattr(record, field_name)
        if isinstance(record, dict):
            return record.get(field_name)
        try:
            return record[field_name]
        except (KeyError, IndexError, TypeError):
            return None

    def generate_category_stats(self, records, field_name):
        values = []
        for record in records:
            v = self._field_value(record, field_name)
            if v is not None and str(v).strip():
                values.append(str(v).strip())
        return Counter(values).most_common()

    def _numeric_stats(self, records, field_name):
        nums = []
        for record in records:
            v = self._field_value(record, field_name)
            if v is None or v == '':
                continue
            try:
                nums.append(float(str(v).replace(',', '.')))
            except (ValueError, TypeError):
                continue
        if not nums:
            return None
        return {
            'min': min(nums),
            'max': max(nums),
            'mean': _stats.fmean(nums),
            'median': _stats.median(nums),
            'count': len(nums),
        }

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def calculate_statistics(self):
        records = self.get_stats_records()
        if not records:
            QMessageBox.warning(
                self, tr('warning', 'Warning'),
                tr('msg_no_records', 'No records found'),
            )
            return

        # Summary: use the currently selected analysis field
        display_name = (
            self.comboBox_stats_analysis.currentText()
            if hasattr(self, 'comboBox_stats_analysis') else ''
        )
        field_name = self.STATS_FIELDS.get(display_name)
        if field_name:
            self.stats_summary_data = self.generate_category_stats(records, field_name)
            self._fill_summary_table(self.stats_summary_data)
            self.stats_data = self.stats_summary_data  # backward compat
            self._update_chart(display_name)

        # Measures: compute for every numeric field declared
        self.stats_measures_data = []
        for mf in self.NUMERIC_FIELDS:
            s = self._numeric_stats(records, mf)
            if s:
                self.stats_measures_data.append((mf, s))
        self._fill_measures_table(self.stats_measures_data)

    def on_stats_analysis_changed(self, *_):
        if hasattr(self, 'stats_summary_data'):
            self.calculate_statistics()

    def _fill_summary_table(self, data):
        t = getattr(self, 'tableWidget_stats_summary', None)
        if t is None:
            return
        t.setRowCount(len(data))
        total = sum(c for _, c in data) or 1
        for r, (cat, cnt) in enumerate(data):
            t.setItem(r, 0, QTableWidgetItem(str(cat)))
            t.setItem(r, 1, QTableWidgetItem(str(cnt)))
            t.setItem(r, 2, QTableWidgetItem(f'{(cnt / total) * 100:.1f}%'))
        t.resizeColumnsToContents()
        t.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def _fill_measures_table(self, data):
        t = getattr(self, 'tableWidget_stats_measures', None)
        if t is None:
            return
        t.setRowCount(len(data))
        for r, (field_name, s) in enumerate(data):
            t.setItem(r, 0, QTableWidgetItem(str(field_name)))
            t.setItem(r, 1, QTableWidgetItem(f'{s["min"]:.2f}'))
            t.setItem(r, 2, QTableWidgetItem(f'{s["max"]:.2f}'))
            t.setItem(r, 3, QTableWidgetItem(f'{s["mean"]:.2f}'))
            t.setItem(r, 4, QTableWidgetItem(f'{s["median"]:.2f}'))
        t.resizeColumnsToContents()
        t.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    # ------------------------------------------------------------------
    # Chart
    # ------------------------------------------------------------------
    def _update_chart(self, title):
        widget_stats = self.findChild(QWidget, 'widget_stats')
        if widget_stats is None or not hasattr(widget_stats, 'canvas'):
            return
        canvas = widget_stats.canvas
        canvas.ax.clear()
        data = self.stats_summary_data
        if not data:
            canvas.draw()
            return
        categories, counts = zip(*data)
        chart_type = (
            self.comboBox_chart_type.currentText().lower()
            if hasattr(self, 'comboBox_chart_type') else 'bar'
        )
        if 'pie' in chart_type:
            canvas.ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
            canvas.ax.axis('equal')
        else:
            x = list(range(len(categories)))
            bars = canvas.ax.bar(x, counts, width=0.6, align='center', alpha=0.75)
            for bar, cnt, cat in zip(bars, counts, categories):
                canvas.ax.annotate(
                    f'{cat}\n{cnt}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords='offset points',
                    ha='center', va='bottom', fontsize=8, rotation=45,
                )
            canvas.ax.set_ylabel(tr('count', 'Count'))
            canvas.ax.set_xticks([])
        canvas.ax.set_title(f"{title} — {tr('statistics', 'Statistics')}")
        canvas.fig.tight_layout()
        canvas.draw()

    # backward-compat alias used by legacy code paths
    def display_chart(self, data, title, chart_type='bar'):
        self.stats_summary_data = data
        self._update_chart(title)

    def on_pushButton_quant_pressed(self):
        self.calculate_statistics()

    # ------------------------------------------------------------------
    # Export CSV (pre-existing)
    # ------------------------------------------------------------------
    def on_pushButton_export_stats_pressed(self):
        if not self.stats_summary_data:
            QMessageBox.warning(
                self, tr('warning', 'Warning'),
                tr('msg_no_stats', 'No statistics to export. Generate statistics first.'),
            )
            return
        display_name = (
            self.comboBox_stats_analysis.currentText()
            if hasattr(self, 'comboBox_stats_analysis') else 'statistics'
        )
        home = os.environ.get('HFF_HOME', os.path.expanduser('~'))
        out_dir = os.path.join(home, 'HFF_stats_export')
        os.makedirs(out_dir, exist_ok=True)
        default_path = os.path.join(
            out_dir,
            f'stats_{display_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        )
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr('export_csv', 'Export Statistics to CSV'),
            default_path, 'CSV Files (*.csv);;All Files (*)',
        )
        if not filepath:
            return
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow([tr('category', 'Category'), tr('count', 'Count'), tr('percentage', 'Percentage')])
                total = sum(c for _, c in self.stats_summary_data) or 1
                for cat, cnt in self.stats_summary_data:
                    w.writerow([cat, cnt, f'{(cnt / total) * 100:.2f}%'])
            QMessageBox.information(
                self, tr('success', 'Success'),
                tr('msg_export_success', 'Statistics exported successfully') + f'\n{filepath}',
            )
        except Exception as e:
            QMessageBox.warning(
                self, tr('error', 'Error'),
                tr('msg_export_failed', 'Export failed') + f': {e}',
            )

    # ------------------------------------------------------------------
    # AI Report
    # ------------------------------------------------------------------
    def _build_stats_prompt(self):
        lines = [f"Form: {type(self).__name__}"]
        display_name = (
            self.comboBox_stats_analysis.currentText()
            if hasattr(self, 'comboBox_stats_analysis') else ''
        )
        lines.append(f"Analysis field: {display_name}")
        lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
        lines.append("")
        if self.stats_summary_data:
            total = sum(c for _, c in self.stats_summary_data) or 1
            lines.append("Category distribution:")
            for cat, cnt in self.stats_summary_data:
                lines.append(f"  - {cat}: {cnt} ({(cnt / total) * 100:.1f}%)")
            lines.append("")
        if self.stats_measures_data:
            lines.append("Numeric measures:")
            for name, s in self.stats_measures_data:
                lines.append(
                    f"  - {name}: min={s['min']:.2f}, max={s['max']:.2f}, "
                    f"mean={s['mean']:.2f}, median={s['median']:.2f}, n={s['count']}"
                )
            lines.append("")
        lines.append(
            "Please produce a concise, academic-style descriptive report "
            "(5–10 sentences) summarising the dominant categories, outliers, "
            "and any observations that an archaeologist would find useful."
        )
        return "\n".join(lines)

    def _get_openai_api_key(self):
        from .hff_openai import get_api_key
        return get_api_key()

    def generate_ai_report(self):
        if not self.stats_summary_data and not self.stats_measures_data:
            QMessageBox.warning(
                self, tr('warning', 'Warning'),
                tr('msg_run_stats_first', 'Run the statistics first.'),
            )
            return

        api_key = self._get_openai_api_key()
        if not api_key:
            QMessageBox.information(
                self, tr('info', 'Info'),
                tr('msg_no_openai_key',
                   'OpenAI API key missing. Set it under QgsSettings key '
                   '"HFF/openai_api_key" or the OPENAI_API_KEY environment variable.'),
            )
            return

        try:
            import openai
        except ImportError:
            QMessageBox.warning(
                self, tr('error', 'Error'),
                tr('msg_openai_missing', 'openai package is not installed'),
            )
            return

        self.textEdit_ai_report.setPlainText(tr('generating', 'Generating…'))
        try:
            client = openai.OpenAI(api_key=api_key)
            from .hff_openai import get_model
            model = get_model()
            # Newer OpenAI models (gpt-5.x / o-series) use max_completion_tokens
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content':
                        'You are an archaeologist describing survey statistics.'},
                    {'role': 'user', 'content': self._build_stats_prompt()},
                ],
                max_completion_tokens=1000,
            )
            self.textEdit_ai_report.setPlainText(response.choices[0].message.content)
        except Exception as e:
            self.textEdit_ai_report.setPlainText('')
            QMessageBox.warning(
                self, tr('error', 'Error'),
                tr('msg_ai_failed', 'AI report failed') + f': {e}',
            )

    # ------------------------------------------------------------------
    # PDF export (reportlab)
    # ------------------------------------------------------------------
    def export_statistics_pdf(self):
        if not self.stats_summary_data and not self.stats_measures_data:
            QMessageBox.warning(
                self, tr('warning', 'Warning'),
                tr('msg_run_stats_first', 'Run the statistics first.'),
            )
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
            )
        except ImportError:
            QMessageBox.warning(
                self, tr('error', 'Error'),
                tr('msg_reportlab_missing', 'reportlab is not installed'),
            )
            return

        home = os.environ.get('HFF_HOME', os.path.expanduser('~'))
        out_dir = os.path.join(home, 'HFF_stats_export')
        os.makedirs(out_dir, exist_ok=True)
        default_path = os.path.join(
            out_dir,
            f'stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        )
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr('export_pdf', 'Export Statistics to PDF'),
            default_path, 'PDF Files (*.pdf);;All Files (*)',
        )
        if not filepath:
            return

        # Save chart as a temporary PNG
        chart_png = None
        widget_stats = self.findChild(QWidget, 'widget_stats')
        if widget_stats is not None and hasattr(widget_stats, 'canvas'):
            try:
                fd, chart_png = tempfile.mkstemp(suffix='.png')
                os.close(fd)
                widget_stats.canvas.fig.savefig(chart_png, dpi=150, bbox_inches='tight')
            except Exception:
                chart_png = None

        try:
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            story.append(Paragraph(
                f"HFF Statistics Report — {type(self).__name__}",
                styles['Title'],
            ))
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                styles['Normal'],
            ))
            story.append(Spacer(1, 12))

            # Summary table
            if self.stats_summary_data:
                story.append(Paragraph('Summary', styles['Heading2']))
                rows = [['Category', 'Count', '%']]
                total = sum(c for _, c in self.stats_summary_data) or 1
                for cat, cnt in self.stats_summary_data:
                    rows.append([str(cat), str(cnt), f'{(cnt / total) * 100:.1f}%'])
                tbl = Table(rows, repeatRows=1)
                tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#aa0000')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(tbl)
                story.append(Spacer(1, 12))

            # Measures table
            if self.stats_measures_data:
                story.append(Paragraph('Numeric measures', styles['Heading2']))
                rows = [['Measure', 'Min', 'Max', 'Mean', 'Median']]
                for name, s in self.stats_measures_data:
                    rows.append([
                        str(name), f'{s["min"]:.2f}', f'{s["max"]:.2f}',
                        f'{s["mean"]:.2f}', f'{s["median"]:.2f}',
                    ])
                tbl = Table(rows, repeatRows=1)
                tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#aa0000')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(tbl)
                story.append(Spacer(1, 12))

            if chart_png:
                story.append(Paragraph('Chart', styles['Heading2']))
                story.append(Image(chart_png, width=480, height=300))
                story.append(Spacer(1, 12))

            if self.textEdit_ai_report.toPlainText().strip():
                story.append(Paragraph('AI Report', styles['Heading2']))
                for para in self.textEdit_ai_report.toPlainText().split('\n'):
                    if para.strip():
                        story.append(Paragraph(para, styles['Normal']))
                        story.append(Spacer(1, 4))

            doc.build(story)
            QMessageBox.information(
                self, tr('success', 'Success'),
                tr('msg_export_success', 'Statistics exported successfully') + f'\n{filepath}',
            )
        except Exception as e:
            QMessageBox.warning(
                self, tr('error', 'Error'),
                tr('msg_export_failed', 'Export failed') + f': {e}',
            )
        finally:
            if chart_png and os.path.exists(chart_png):
                try:
                    os.remove(chart_png)
                except OSError:
                    pass


# ---------------------------------------------------------------------------
# Field configurations
# ---------------------------------------------------------------------------
SITE_STATS_FIELDS = {
    'Site Type': 'site_type',
    'Survey Type': 'survey_type',
    'Condition': 'condition',
    'Period': 'period',
    'Country': 'country',
    'Region': 'region',
}

SHIPWRECK_STATS_FIELDS = {
    'Wreck Type': 'type_of_wreck',
    'Nationality': 'nationality',
    'Propulsion': 'propulsion',
    'Condition': 'condition',
    'Hull Material': 'type_hull',
    'Area': 'area',
}
SHIPWRECK_NUMERIC = ('length', 'width', 'depth')

ANCHOR_STATS_FIELDS = {
    'Anchor Type': 'anchor_type',
    'Stone Type': 'stone_type',
    'Metal Type': 'metal_type',
    'Anchor Shape': 'anchor_shape',
    'Folding': 'folding',
    'Area': 'area',
}
ANCHOR_NUMERIC = ('length', 'width', 'thickness', 'weight')

ARTEFACT_STATS_FIELDS = {
    'Material': 'material',
    'Object': 'obj',
    'Recovered': 'recovered',
    'Area': 'area',
    'Years': 'years',
}
ARTEFACT_NUMERIC = ('length', 'width', 'thickness', 'weight')

POTTERY_STATS_FIELDS = {
    'Fabric': 'fabric',
    'Form': 'form',
    'Decoration': 'decoration',
    'Surface': 'surface_treatment',
    'Area': 'area',
}
POTTERY_NUMERIC = ('rim_diameter', 'base_diameter', 'height', 'weight')

UW_STATS_FIELDS = {
    'Task':            'task',
    'Site':            'site',
    'Area':            'area_id',
    'Year':            'years',
    'UW visibility':   'uw_visibility',
    'UW current':      'uw_current_',
    'UW temperature':  'uw_temperature',
    'Wind':            'wind',
    'Dive supervisor': 'dive_supervisor',
    'Standby diver':   'standby_diver',
    'Breathing mix':   'breathing_mix',
    'Max depth':       'max_depth',
    'Bottom time':     'bottom_time',
}
UW_NUMERIC = ('max_depth', 'bottom_time', 'uw_temperature')
