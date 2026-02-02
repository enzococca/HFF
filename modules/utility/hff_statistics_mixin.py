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
from datetime import datetime
from collections import Counter

from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog

from .hff_i18n import tr


class StatisticsMixin:
    """Mixin class to add statistics functionality to HFF forms.

    This mixin provides methods for generating and displaying statistics
    using matplotlib charts, compatible with pyarchinit patterns.

    Usage:
        class MyForm(QDialog, StatisticsMixin):
            def __init__(self):
                super().__init__()
                self.init_statistics()
    """

    # Define field configurations per form type
    # Override this in subclasses or set via init_statistics()
    STATS_FIELDS = {}

    def init_statistics(self, fields_config=None):
        """Initialize statistics functionality.

        Args:
            fields_config: Dict mapping display names to field names
                          e.g. {'Site Type': 'site_type', 'Period': 'period'}
        """
        if fields_config:
            self.STATS_FIELDS = fields_config

        self.stats_data = []

        # Connect UI elements if they exist
        if hasattr(self, 'comboBox_stats_field'):
            self.setup_stats_field_combo()

        if hasattr(self, 'pushButton_quant'):
            self.pushButton_quant.clicked.connect(self.on_pushButton_quant_pressed)

        if hasattr(self, 'pushButton_export_stats'):
            self.pushButton_export_stats.clicked.connect(self.on_pushButton_export_stats_pressed)

    def setup_stats_field_combo(self):
        """Populate the statistics field combo box."""
        if not hasattr(self, 'comboBox_stats_field'):
            return

        self.comboBox_stats_field.clear()

        for display_name in self.STATS_FIELDS.keys():
            self.comboBox_stats_field.addItem(display_name)

    def get_stats_records(self):
        """Get records for statistics calculation.

        Override this method in subclasses to return the appropriate records.

        Returns:
            List of records (dicts or objects with field attributes)
        """
        # Default implementation - try to get from DATA_LIST
        if hasattr(self, 'DATA_LIST'):
            return self.DATA_LIST
        return []

    def on_pushButton_quant_pressed(self):
        """Handle the Generate Statistics button click."""
        if not hasattr(self, 'comboBox_stats_field') or not hasattr(self, 'widget_stats'):
            QMessageBox.warning(
                self,
                tr('warning', 'Warning'),
                tr('msg_stats_not_available', 'Statistics not available')
            )
            return

        # Get selected field
        display_name = self.comboBox_stats_field.currentText()
        if not display_name or display_name not in self.STATS_FIELDS:
            QMessageBox.warning(
                self,
                tr('warning', 'Warning'),
                tr('msg_select_field', 'Please select a field')
            )
            return

        field_name = self.STATS_FIELDS[display_name]

        # Get chart type
        chart_type = 'bar'
        if hasattr(self, 'comboBox_stats_type'):
            chart_text = self.comboBox_stats_type.currentText().lower()
            if 'pie' in chart_text:
                chart_type = 'pie'

        # Get records
        records = self.get_stats_records()
        if not records:
            QMessageBox.warning(
                self,
                tr('warning', 'Warning'),
                tr('msg_no_records', 'No records found')
            )
            return

        # Generate statistics
        self.stats_data = self.generate_category_stats(records, field_name)

        if not self.stats_data:
            QMessageBox.warning(
                self,
                tr('warning', 'Warning'),
                tr('msg_no_data', 'No data available for selected field')
            )
            return

        # Display chart
        self.display_chart(self.stats_data, display_name, chart_type)

    def generate_category_stats(self, records, field_name):
        """Generate category statistics from records.

        Args:
            records: List of records
            field_name: Name of field to analyze

        Returns:
            List of tuples [(category, count), ...]
        """
        values = []

        for record in records:
            # Try different ways to access the field
            val = None
            if hasattr(record, field_name):
                val = getattr(record, field_name)
            elif isinstance(record, dict):
                val = record.get(field_name)
            elif hasattr(record, '__getitem__'):
                try:
                    val = record[field_name]
                except (KeyError, IndexError, TypeError):
                    pass

            if val is not None and str(val).strip():
                values.append(str(val).strip())

        if not values:
            return []

        # Count occurrences
        counter = Counter(values)

        # Return as list of tuples sorted by count (descending)
        return counter.most_common()

    def display_chart(self, data, title, chart_type='bar'):
        """Display chart using Mplwidget.

        Args:
            data: List of tuples [(category, count), ...]
            title: Chart title
            chart_type: 'bar' or 'pie'
        """
        if not hasattr(self, 'widget_stats') or not hasattr(self.widget_stats, 'canvas'):
            return

        # Clear previous chart
        self.widget_stats.canvas.ax.clear()

        if not data:
            self.widget_stats.canvas.draw()
            return

        categories, counts = zip(*data)

        if chart_type == 'pie':
            # Pie chart
            self.widget_stats.canvas.ax.pie(
                counts,
                labels=categories,
                autopct='%1.1f%%',
                startangle=90
            )
            self.widget_stats.canvas.ax.axis('equal')
        else:
            # Bar chart
            x = list(range(len(categories)))
            bars = self.widget_stats.canvas.ax.bar(
                x, counts, width=0.6, align='center', alpha=0.7
            )

            # Add labels on bars
            for bar, count, cat in zip(bars, counts, categories):
                height = bar.get_height()
                self.widget_stats.canvas.ax.annotate(
                    f'{cat}\n{count}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=8, rotation=45
                )

            self.widget_stats.canvas.ax.set_ylabel(tr('count', 'Count'))
            self.widget_stats.canvas.ax.set_xticks([])  # Hide x ticks since labels are on bars

        self.widget_stats.canvas.ax.set_title(f"{title} - {tr('statistics', 'Statistics')}")
        self.widget_stats.canvas.fig.tight_layout()
        self.widget_stats.canvas.draw()

    def on_pushButton_export_stats_pressed(self):
        """Export statistics to CSV file."""
        if not self.stats_data:
            QMessageBox.warning(
                self,
                tr('warning', 'Warning'),
                tr('msg_no_stats', 'No statistics to export. Generate statistics first.')
            )
            return

        # Get field name for filename
        display_name = self.comboBox_stats_field.currentText() if hasattr(self, 'comboBox_stats_field') else 'statistics'

        # Get save path
        home = os.environ.get('HFF_HOME', os.path.expanduser('~'))
        default_path = os.path.join(home, 'HFF_stats_export')
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f'stats_{display_name}_{timestamp}.csv'

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            tr('export_csv', 'Export Statistics to CSV'),
            os.path.join(default_path, default_filename),
            'CSV Files (*.csv);;All Files (*)'
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([tr('category', 'Category'), tr('count', 'Count'), tr('percentage', 'Percentage')])

                total = sum(count for _, count in self.stats_data)
                for category, count in self.stats_data:
                    percentage = (count / total) * 100 if total > 0 else 0
                    writer.writerow([category, count, f'{percentage:.2f}%'])

            QMessageBox.information(
                self,
                tr('success', 'Success'),
                tr('msg_export_success', 'Statistics exported successfully') + f'\n{filepath}'
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                tr('error', 'Error'),
                tr('msg_export_failed', 'Export failed') + f': {str(e)}'
            )


# Field configurations for different form types
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

ANCHOR_STATS_FIELDS = {
    'Anchor Type': 'anchor_type',
    'Stone Type': 'stone_type',
    'Metal Type': 'metal_type',
    'Anchor Shape': 'anchor_shape',
    'Folding': 'folding',
    'Area': 'area',
}

ARTEFACT_STATS_FIELDS = {
    'Material': 'material',
    'Object': 'obj',
    'Recovered': 'recovered',
    'Area': 'area',
    'Years': 'years',
}

POTTERY_STATS_FIELDS = {
    'Fabric': 'fabric',
    'Form': 'form',
    'Decoration': 'decoration',
    'Surface': 'surface_treatment',
    'Area': 'area',
}

UW_STATS_FIELDS = {
    'Dive Type': 'dive_type',
    'Task': 'task',
    'Visibility': 'visibility',
    'Current': 'current_',
    'Area': 'area',
}
