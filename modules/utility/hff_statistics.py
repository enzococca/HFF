# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Statistics Utility Module
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
from statistics import mean, median, stdev

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.units import mm, inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from .hff_i18n import tr


class UTILITY:
    """Utility class with helper functions for statistics."""

    @staticmethod
    def sum_list_of_tuples_for_value(data_list):
        """Sum values for duplicate categories in a list of tuples.

        Args:
            data_list: List of tuples [(category, value), ...]

        Returns:
            List of tuples with summed values for each unique category
        """
        result_dict = {}
        for category, value in data_list:
            if category in result_dict:
                result_dict[category] += value
            else:
                result_dict[category] = value
        return [(k, v) for k, v in result_dict.items()]


class HffStatistics:
    """Statistics generator for HFF archaeological data.

    Provides methods to generate category counts, measurement statistics,
    charts, and export functionality. Compatible with pyarchinit patterns.
    """

    # Color palette for charts (archaeological theme)
    COLORS = [
        '#8B4513',  # SaddleBrown
        '#CD853F',  # Peru
        '#D2691E',  # Chocolate
        '#A0522D',  # Sienna
        '#BC8F8F',  # RosyBrown
        '#F4A460',  # SandyBrown
        '#DEB887',  # BurlyWood
        '#D2B48C',  # Tan
        '#C4A484',  # Fawn
        '#B8860B',  # DarkGoldenrod
        '#DAA520',  # Goldenrod
        '#808000',  # Olive
    ]

    def __init__(self, db_manager=None, widget=None):
        """Initialize statistics generator.

        Args:
            db_manager: Optional database manager for querying data
            widget: Optional Mplwidget for chart display
        """
        self.db_manager = db_manager
        self.widget = widget
        self.data_list = []

    def generate_category_stats(self, data, field_name):
        """Generate statistics for a categorical field.

        Args:
            data: List of records/dicts containing the field
            field_name: Name of the field to analyze

        Returns:
            List of tuples: [(category, count, percentage), ...]
        """
        if not data:
            return []

        # Extract values
        values = []
        for record in data:
            if hasattr(record, field_name):
                val = getattr(record, field_name)
            elif isinstance(record, dict):
                val = record.get(field_name)
            else:
                continue

            if val is not None and str(val).strip():
                values.append(str(val).strip())

        if not values:
            return []

        # Count occurrences
        counter = Counter(values)
        total = len(values)

        # Calculate percentages
        stats = []
        for category, count in counter.most_common():
            percentage = (count / total) * 100
            stats.append((category, count, percentage))

        return stats

    def generate_measurement_stats(self, data, field_names):
        """Generate statistics for numeric measurement fields.

        Args:
            data: List of records/dicts containing the fields
            field_names: List of field names to analyze

        Returns:
            Dict: {field_name: {min, max, mean, median, stdev, count}, ...}
        """
        if not data or not field_names:
            return {}

        stats = {}
        for field_name in field_names:
            values = []
            for record in data:
                if hasattr(record, field_name):
                    val = getattr(record, field_name)
                elif isinstance(record, dict):
                    val = record.get(field_name)
                else:
                    continue

                # Try to convert to float
                if val is not None:
                    try:
                        num_val = float(val)
                        values.append(num_val)
                    except (ValueError, TypeError):
                        continue

            if values:
                stats[field_name] = {
                    'min': min(values),
                    'max': max(values),
                    'mean': mean(values),
                    'median': median(values),
                    'stdev': stdev(values) if len(values) > 1 else 0,
                    'count': len(values)
                }

        return stats

    def plot_chart(self, d, t, yl):
        """Generate bar chart (pyarchinit compatible method).

        Args:
            d: List of tuples [(category, value), ...]
            t: Chart title
            yl: Y-axis label
        """
        self.data_list = d

        if not self.widget or not HAS_MATPLOTLIB:
            return

        self.widget.canvas.ax.clear()

        if isinstance(self.data_list, list) and len(self.data_list) > 0:
            teams, values = zip(*self.data_list)
            x = list(range(len(teams)))

            bars = self.widget.canvas.ax.bar(
                x, height=values, width=0.5,
                align='center', alpha=0.4, picker=5
            )

            self.widget.canvas.ax.set_title(t)
            self.widget.canvas.ax.set_ylabel(yl)

            # Add value labels on bars
            for bar, val, team in zip(bars, values, teams):
                height = bar.get_height()
                self.widget.canvas.ax.annotate(
                    f'{team}\n{val}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8,
                    rotation=90
                )

        self.widget.canvas.fig.tight_layout()
        self.widget.canvas.draw()

    def torta_chart(self, d, t, yl):
        """Generate pie chart (pyarchinit compatible method).

        Args:
            d: List of tuples [(category, value), ...]
            t: Chart title
            yl: Y-axis label (not used for pie)
        """
        self.data_list = d

        if not self.widget or not HAS_MATPLOTLIB:
            return

        self.widget.canvas.ax.clear()

        if isinstance(self.data_list, list) and len(self.data_list) > 0:
            # Convert to dict for pie chart
            data_dict = dict(self.data_list)

            labels = list(data_dict.keys())
            sizes = list(data_dict.values())

            self.widget.canvas.ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90
            )
            self.widget.canvas.ax.axis('equal')
            self.widget.canvas.ax.set_title(t)

        self.widget.canvas.fig.tight_layout()
        self.widget.canvas.draw()

    def matrice_chart(self, d, t, yl):
        """Generate correlation matrix (pyarchinit compatible method).

        Args:
            d: List of numeric values
            t: Chart title
            yl: Y-axis label
        """
        if not self.widget or not HAS_MATPLOTLIB:
            return

        try:
            import numpy as np

            self.widget.canvas.ax.clear()

            if isinstance(d, list) and len(d) > 0:
                # Convert to numpy array
                data_array = np.array(d).reshape(-1, 1)
                corr_matrix = np.corrcoef(data_array.T)

                im = self.widget.canvas.ax.imshow(
                    corr_matrix,
                    cmap='coolwarm',
                    aspect='auto'
                )
                self.widget.canvas.fig.colorbar(im, ax=self.widget.canvas.ax)
                self.widget.canvas.ax.set_title(t)

            self.widget.canvas.fig.tight_layout()
            self.widget.canvas.draw()
        except ImportError:
            pass

    def create_bar_chart(self, ax, data, title, xlabel='', ylabel=None):
        """Create a bar chart on the given axes.

        Args:
            ax: Matplotlib axes object
            data: List of tuples (category, count, percentage)
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        """
        if ylabel is None:
            ylabel = tr('count', 'Count')

        if not HAS_MATPLOTLIB or not data:
            return

        categories = [item[0][:20] for item in data]  # Truncate long labels
        counts = [item[1] for item in data]
        colors = self.COLORS[:len(categories)]

        bars = ax.bar(range(len(categories)), counts, color=colors)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=8)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)

        # Add count labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.annotate(f'{count}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def create_pie_chart(self, ax, data, title):
        """Create a pie chart on the given axes.

        Args:
            ax: Matplotlib axes object
            data: List of tuples (category, count, percentage)
            title: Chart title
        """
        if not HAS_MATPLOTLIB or not data:
            return

        # Limit to top 10 categories, group rest as "Other"
        if len(data) > 10:
            top_data = data[:9]
            other_count = sum(item[1] for item in data[9:])
            other_pct = sum(item[2] for item in data[9:])
            top_data.append((tr('other', 'Other'), other_count, other_pct))
            data = top_data

        labels = [f"{item[0][:15]}\n({item[2]:.1f}%)" for item in data]
        sizes = [item[1] for item in data]
        colors = self.COLORS[:len(data)]

        wedges, texts = ax.pie(sizes, labels=labels, colors=colors,
                               startangle=90, labeldistance=1.1)

        ax.set_title(title, fontsize=10, fontweight='bold')

        # Make labels smaller
        for text in texts:
            text.set_fontsize(7)

    def create_histogram(self, ax, values, title, xlabel='', ylabel=tr('frequency', 'Frequency'), bins=20):
        """Create a histogram on the given axes.

        Args:
            ax: Matplotlib axes object
            values: List of numeric values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            bins: Number of bins
        """
        if not HAS_MATPLOTLIB or not values:
            return

        ax.hist(values, bins=bins, color=self.COLORS[0], edgecolor='white', alpha=0.8)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def export_to_csv(self, stats, filepath, stat_type='category'):
        """Export statistics to CSV file.

        Args:
            stats: Statistics data (list of tuples for category, dict for measurements)
            filepath: Output file path
            stat_type: 'category' or 'measurement'
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                if stat_type == 'category':
                    writer.writerow([tr('category', 'Category'),
                                     tr('count', 'Count'),
                                     tr('percentage', 'Percentage')])
                    for item in stats:
                        writer.writerow([item[0], item[1], f'{item[2]:.2f}%'])
                else:
                    writer.writerow([tr('field', 'Field'),
                                     tr('min', 'Min'),
                                     tr('max', 'Max'),
                                     tr('mean', 'Mean'),
                                     tr('median', 'Median'),
                                     tr('std_dev', 'Std Dev'),
                                     tr('count', 'Count')])
                    for field, data in stats.items():
                        writer.writerow([
                            field,
                            f'{data["min"]:.2f}',
                            f'{data["max"]:.2f}',
                            f'{data["mean"]:.2f}',
                            f'{data["median"]:.2f}',
                            f'{data["stdev"]:.2f}',
                            data["count"]
                        ])

            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False

    def export_to_pdf(self, stats, filepath, title='Statistics Report',
                      stat_type='category', chart_path=None):
        """Export statistics to PDF file.

        Args:
            stats: Statistics data
            filepath: Output file path
            title: Report title
            stat_type: 'category' or 'measurement'
            chart_path: Optional path to chart image to include
        """
        if not HAS_REPORTLAB:
            return False

        try:
            doc = SimpleDocTemplate(filepath, pagesize=A4,
                                    leftMargin=15*mm, rightMargin=15*mm,
                                    topMargin=15*mm, bottomMargin=15*mm)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a5276'),
                spaceAfter=20
            )
            elements.append(Paragraph(title, title_style))

            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray,
                spaceAfter=20
            )
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            elements.append(Paragraph(f"Generated: {date_str}", date_style))

            # Add chart if provided
            if chart_path and os.path.exists(chart_path):
                elements.append(Image(chart_path, width=160*mm, height=100*mm))
                elements.append(Spacer(1, 10*mm))

            # Create table
            if stat_type == 'category':
                table_data = [[tr('category', 'Category'),
                               tr('count', 'Count'),
                               tr('percentage', 'Percentage')]]
                for item in stats:
                    table_data.append([item[0], str(item[1]), f'{item[2]:.2f}%'])
            else:
                table_data = [[tr('field', 'Field'),
                               tr('min', 'Min'), tr('max', 'Max'),
                               tr('mean', 'Mean'), tr('median', 'Median'),
                               tr('count', 'Count')]]
                for field, data in stats.items():
                    table_data.append([
                        field,
                        f'{data["min"]:.2f}',
                        f'{data["max"]:.2f}',
                        f'{data["mean"]:.2f}',
                        f'{data["median"]:.2f}',
                        str(data["count"])
                    ])

            # Style table
            table = Table(table_data)
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('PADDING', (0, 0), (-1, -1), 8),
            ])
            table.setStyle(table_style)
            elements.append(table)

            doc.build(elements)
            return True

        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False


class StatisticsWidget:
    """Widget helper for displaying statistics in forms.

    Provides methods to create and update statistics displays
    in form dialogs.
    """

    def __init__(self, form, stats_generator=None):
        """Initialize statistics widget.

        Args:
            form: Parent form dialog
            stats_generator: HffStatistics instance
        """
        self.form = form
        self.stats = stats_generator or HffStatistics()
        self.figure = None
        self.canvas = None

    def setup_statistics_tab(self, tab_widget, tab_name=None):
        """Setup or get the statistics tab.

        Args:
            tab_widget: QTabWidget to add statistics tab to
            tab_name: Name for the tab

        Returns:
            The statistics tab widget
        """
        from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout

        # Check if tab already exists
        tab_name = tab_name or tr('statistics', 'Statistics')
        for i in range(tab_widget.count()):
            if tab_widget.tabText(i) == tab_name:
                return tab_widget.widget(i)

        # Create new tab
        stats_tab = QWidget()
        layout = QVBoxLayout(stats_tab)
        tab_widget.addTab(stats_tab, tab_name)

        return stats_tab

    def create_chart_canvas(self, parent_widget, figsize=(8, 6)):
        """Create a matplotlib canvas for displaying charts.

        Args:
            parent_widget: Parent widget to add canvas to
            figsize: Figure size (width, height) in inches

        Returns:
            Tuple of (figure, canvas) or (None, None) if matplotlib not available
        """
        if not HAS_MATPLOTLIB:
            return None, None

        from qgis.PyQt.QtWidgets import QVBoxLayout

        self.figure = Figure(figsize=figsize, dpi=100)
        self.canvas = FigureCanvas(self.figure)

        # Add to layout if parent has one
        layout = parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(parent_widget)
        layout.addWidget(self.canvas)

        return self.figure, self.canvas

    def update_chart(self, data, chart_type='bar', title='', field_name=''):
        """Update the chart with new data.

        Args:
            data: List of tuples (category, count, percentage)
            chart_type: 'bar' or 'pie'
            title: Chart title
            field_name: Field name for labels
        """
        if not self.figure or not data:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if chart_type == 'bar':
            self.stats.create_bar_chart(ax, data, title)
        elif chart_type == 'pie':
            self.stats.create_pie_chart(ax, data, title)

        self.figure.tight_layout()
        self.canvas.draw()

    def clear_chart(self):
        """Clear the chart."""
        if self.figure:
            self.figure.clear()
            if self.canvas:
                self.canvas.draw()


# Utility functions for quick statistics generation

def get_category_stats_from_table(table_widget, column_index):
    """Extract category statistics from a QTableWidget.

    Args:
        table_widget: QTableWidget with data
        column_index: Column index to analyze

    Returns:
        List of tuples (category, count, percentage)
    """
    values = []
    for row in range(table_widget.rowCount()):
        item = table_widget.item(row, column_index)
        if item and item.text().strip():
            values.append(item.text().strip())

    if not values:
        return []

    counter = Counter(values)
    total = len(values)

    stats = []
    for category, count in counter.most_common():
        percentage = (count / total) * 100
        stats.append((category, count, percentage))

    return stats


def get_numeric_stats_from_table(table_widget, column_index):
    """Extract numeric statistics from a QTableWidget.

    Args:
        table_widget: QTableWidget with data
        column_index: Column index to analyze

    Returns:
        Dict with min, max, mean, median, stdev, count
    """
    values = []
    for row in range(table_widget.rowCount()):
        item = table_widget.item(row, column_index)
        if item and item.text().strip():
            try:
                values.append(float(item.text()))
            except ValueError:
                continue

    if not values:
        return None

    return {
        'min': min(values),
        'max': max(values),
        'mean': mean(values),
        'median': median(values),
        'stdev': stdev(values) if len(values) > 1 else 0,
        'count': len(values)
    }
