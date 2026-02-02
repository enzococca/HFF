# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - PDF Base Module
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

Base module for PDF generation with professional styling.
Provides consistent formatting, colors, and layouts for all PDF exports.
"""

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image, PageBreak, KeepTogether, Frame, PageTemplate
)
from reportlab.pdfgen import canvas


# =============================================================================
# COLOR DEFINITIONS - Professional Archaeological Theme
# =============================================================================

# Primary colors
HFF_BLUE = colors.HexColor('#1a5276')          # Dark blue for headers
HFF_BLUE_LIGHT = colors.HexColor('#2980b9')    # Light blue for accents
HFF_GRAY = colors.HexColor('#f5f5f5')          # Light gray for alternate rows
HFF_GRAY_DARK = colors.HexColor('#bdc3c7')     # Dark gray for borders
HFF_WHITE = colors.white

# Secondary colors
HFF_BROWN = colors.HexColor('#8B4513')         # Archaeological brown
HFF_SAND = colors.HexColor('#F4A460')          # Sandy color
HFF_TERRACOTTA = colors.HexColor('#CD5C5C')    # Terracotta/pottery color

# Status colors
HFF_SUCCESS = colors.HexColor('#27ae60')       # Green for success/good condition
HFF_WARNING = colors.HexColor('#f39c12')       # Orange for warnings
HFF_DANGER = colors.HexColor('#e74c3c')        # Red for danger/poor condition


# =============================================================================
# FONT DEFINITIONS
# =============================================================================

FONT_HEADER = 'Helvetica-Bold'
FONT_NORMAL = 'Helvetica'
FONT_ITALIC = 'Helvetica-Oblique'

FONT_SIZE_TITLE = 14
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_HEADER = 10
FONT_SIZE_NORMAL = 9
FONT_SIZE_SMALL = 8
FONT_SIZE_FOOTER = 7


# =============================================================================
# PAGE SETTINGS
# =============================================================================

PAGE_MARGIN_LEFT = 15 * mm
PAGE_MARGIN_RIGHT = 15 * mm
PAGE_MARGIN_TOP = 20 * mm
PAGE_MARGIN_BOTTOM = 20 * mm

CELL_PADDING = 8


# =============================================================================
# TABLE STYLES
# =============================================================================

class HffPdfStyles:
    """Factory class for creating consistent PDF table styles."""

    @staticmethod
    def get_header_style():
        """Get style for table headers.

        Returns:
            TableStyle with blue background, white text, bold font
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HFF_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), HFF_WHITE),
            ('FONTNAME', (0, 0), (-1, 0), FONT_HEADER),
            ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_HEADER),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), CELL_PADDING),
            ('BOTTOMPADDING', (0, 0), (-1, 0), CELL_PADDING),
            ('LEFTPADDING', (0, 0), (-1, 0), CELL_PADDING),
            ('RIGHTPADDING', (0, 0), (-1, 0), CELL_PADDING),
        ])

    @staticmethod
    def get_data_style(with_alternating_rows=True):
        """Get style for table data rows.

        Args:
            with_alternating_rows: If True, alternate row colors

        Returns:
            TableStyle for data rows
        """
        style = [
            ('FONTNAME', (0, 1), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_NORMAL),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 1), (-1, -1), CELL_PADDING),
            ('RIGHTPADDING', (0, 1), (-1, -1), CELL_PADDING),
            ('GRID', (0, 0), (-1, -1), 0.5, HFF_GRAY_DARK),
        ]

        if with_alternating_rows:
            style.append(
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HFF_WHITE, HFF_GRAY])
            )

        return TableStyle(style)

    @staticmethod
    def get_full_table_style(with_alternating_rows=True):
        """Get combined header and data style for a complete table.

        Args:
            with_alternating_rows: If True, alternate row colors

        Returns:
            TableStyle for complete table
        """
        style_list = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), HFF_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), HFF_WHITE),
            ('FONTNAME', (0, 0), (-1, 0), FONT_HEADER),
            ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_HEADER),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), CELL_PADDING),
            ('BOTTOMPADDING', (0, 0), (-1, 0), CELL_PADDING),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 1), (-1, -1), FONT_SIZE_NORMAL),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), CELL_PADDING),
            ('RIGHTPADDING', (0, 0), (-1, -1), CELL_PADDING),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, HFF_GRAY_DARK),
        ]

        if with_alternating_rows:
            style_list.append(
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HFF_WHITE, HFF_GRAY])
            )

        return TableStyle(style_list)

    @staticmethod
    def get_label_value_style():
        """Get style for label-value pair tables (2 columns).

        Returns:
            TableStyle for label-value tables
        """
        return TableStyle([
            # Label column (first column)
            ('BACKGROUND', (0, 0), (0, -1), HFF_BLUE),
            ('TEXTCOLOR', (0, 0), (0, -1), HFF_WHITE),
            ('FONTNAME', (0, 0), (0, -1), FONT_HEADER),
            ('FONTSIZE', (0, 0), (0, -1), FONT_SIZE_NORMAL),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),

            # Value column (second column)
            ('FONTNAME', (1, 0), (1, -1), FONT_NORMAL),
            ('FONTSIZE', (1, 0), (1, -1), FONT_SIZE_NORMAL),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BACKGROUND', (1, 0), (1, -1), HFF_WHITE),

            # Common
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), CELL_PADDING),
            ('RIGHTPADDING', (0, 0), (-1, -1), CELL_PADDING),
            ('GRID', (0, 0), (-1, -1), 0.5, HFF_GRAY_DARK),
        ])

    @staticmethod
    def get_section_header_style():
        """Get style for section header rows within a table.

        Returns:
            TableStyle for section headers
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HFF_BLUE_LIGHT),
            ('TEXTCOLOR', (0, 0), (-1, 0), HFF_WHITE),
            ('FONTNAME', (0, 0), (-1, 0), FONT_HEADER),
            ('FONTSIZE', (0, 0), (-1, 0), FONT_SIZE_NORMAL),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('SPAN', (0, 0), (-1, 0)),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('LEFTPADDING', (0, 0), (-1, 0), CELL_PADDING),
        ])


# =============================================================================
# PARAGRAPH STYLES
# =============================================================================

def get_paragraph_styles():
    """Get custom paragraph styles for HFF documents.

    Returns:
        Dict of ParagraphStyle objects
    """
    styles = getSampleStyleSheet()

    custom_styles = {
        'HFF_Title': ParagraphStyle(
            'HFF_Title',
            parent=styles['Heading1'],
            fontSize=FONT_SIZE_TITLE,
            textColor=HFF_BLUE,
            spaceAfter=12,
            fontName=FONT_HEADER,
        ),
        'HFF_Subtitle': ParagraphStyle(
            'HFF_Subtitle',
            parent=styles['Heading2'],
            fontSize=FONT_SIZE_SUBTITLE,
            textColor=HFF_BLUE,
            spaceAfter=8,
            fontName=FONT_HEADER,
        ),
        'HFF_SectionHeader': ParagraphStyle(
            'HFF_SectionHeader',
            parent=styles['Heading3'],
            fontSize=FONT_SIZE_HEADER,
            textColor=HFF_BLUE,
            spaceAfter=6,
            spaceBefore=12,
            fontName=FONT_HEADER,
        ),
        'HFF_Normal': ParagraphStyle(
            'HFF_Normal',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_NORMAL,
            fontName=FONT_NORMAL,
            spaceAfter=4,
        ),
        'HFF_Small': ParagraphStyle(
            'HFF_Small',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_SMALL,
            fontName=FONT_NORMAL,
            textColor=colors.gray,
        ),
        'HFF_Footer': ParagraphStyle(
            'HFF_Footer',
            parent=styles['Normal'],
            fontSize=FONT_SIZE_FOOTER,
            fontName=FONT_NORMAL,
            textColor=colors.gray,
        ),
    }

    return custom_styles


# =============================================================================
# NUMBERED CANVAS - For Page X of Y
# =============================================================================

class HffNumberedCanvas(canvas.Canvas):
    """Custom canvas that adds page numbers and headers/footers.

    Usage:
        doc = SimpleDocTemplate(...)
        doc.build(elements, canvasmaker=HffNumberedCanvas)
    """

    def __init__(self, *args, **kwargs):
        """Initialize the canvas."""
        self.logo_path = kwargs.pop('logo_path', None)
        self.doc_title = kwargs.pop('doc_title', 'HFF Report')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        """Save page state before moving to next page."""
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to all pages, then save the document."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_header()
            self.draw_page_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_header(self):
        """Draw header on each page."""
        page_width, page_height = A4

        # Draw logo if available
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                self.drawImage(self.logo_path, PAGE_MARGIN_LEFT, page_height - 15*mm,
                               width=20*mm, height=10*mm, preserveAspectRatio=True)
            except:
                pass

        # Draw title
        self.setFont(FONT_HEADER, FONT_SIZE_HEADER)
        self.setFillColor(HFF_BLUE)
        self.drawString(PAGE_MARGIN_LEFT + 25*mm, page_height - 12*mm, self.doc_title)

        # Draw separator line
        self.setStrokeColor(HFF_BLUE)
        self.setLineWidth(0.5)
        self.line(PAGE_MARGIN_LEFT, page_height - 18*mm,
                  page_width - PAGE_MARGIN_RIGHT, page_height - 18*mm)

    def draw_page_footer(self, page_count):
        """Draw footer with page number and date on each page."""
        page_width, page_height = A4

        # Draw separator line
        self.setStrokeColor(HFF_GRAY_DARK)
        self.setLineWidth(0.5)
        self.line(PAGE_MARGIN_LEFT, PAGE_MARGIN_BOTTOM - 5*mm,
                  page_width - PAGE_MARGIN_RIGHT, PAGE_MARGIN_BOTTOM - 5*mm)

        # Draw date on left
        self.setFont(FONT_NORMAL, FONT_SIZE_FOOTER)
        self.setFillColor(colors.gray)
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.drawString(PAGE_MARGIN_LEFT, PAGE_MARGIN_BOTTOM - 10*mm, date_str)

        # Draw page number on right
        page_num = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_width - PAGE_MARGIN_RIGHT,
                             PAGE_MARGIN_BOTTOM - 10*mm, page_num)

        # Draw HFF credit in center
        self.drawCentredString(page_width / 2, PAGE_MARGIN_BOTTOM - 10*mm,
                               "Generated by HFF Survey")


# =============================================================================
# DOCUMENT BUILDER HELPERS
# =============================================================================

def create_hff_document(filepath, title='HFF Report', pagesize=A4):
    """Create a SimpleDocTemplate with HFF styling.

    Args:
        filepath: Output file path
        title: Document title
        pagesize: Page size (A4 or LETTER)

    Returns:
        SimpleDocTemplate configured for HFF styling
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=pagesize,
        leftMargin=PAGE_MARGIN_LEFT,
        rightMargin=PAGE_MARGIN_RIGHT,
        topMargin=PAGE_MARGIN_TOP + 5*mm,  # Extra space for header
        bottomMargin=PAGE_MARGIN_BOTTOM + 5*mm,  # Extra space for footer
        title=title,
    )
    return doc


def create_title_block(title, subtitle=None, record_id=None):
    """Create a title block for the document.

    Args:
        title: Main title
        subtitle: Optional subtitle
        record_id: Optional record ID to display

    Returns:
        List of flowable elements
    """
    elements = []
    styles = get_paragraph_styles()

    # Main title
    elements.append(Paragraph(title, styles['HFF_Title']))

    # Subtitle if provided
    if subtitle:
        elements.append(Paragraph(subtitle, styles['HFF_Subtitle']))

    # Record ID if provided
    if record_id:
        elements.append(Paragraph(f"Record ID: {record_id}", styles['HFF_Small']))

    elements.append(Spacer(1, 10*mm))

    return elements


def create_section_header(text):
    """Create a section header.

    Args:
        text: Section title

    Returns:
        Paragraph element
    """
    styles = get_paragraph_styles()
    return Paragraph(text, styles['HFF_SectionHeader'])


def create_data_table(data, col_widths=None, first_row_header=True):
    """Create a styled data table.

    Args:
        data: List of lists containing table data
        col_widths: Optional list of column widths
        first_row_header: If True, style first row as header

    Returns:
        Table element with HFF styling
    """
    if not data:
        return None

    table = Table(data, colWidths=col_widths)

    if first_row_header:
        table.setStyle(HffPdfStyles.get_full_table_style())
    else:
        table.setStyle(HffPdfStyles.get_data_style())

    return table


def create_label_value_table(data, label_width=50*mm, value_width=None):
    """Create a label-value pair table (2 columns).

    Args:
        data: List of (label, value) tuples
        label_width: Width of label column
        value_width: Width of value column (auto if None)

    Returns:
        Table element with label-value styling
    """
    if not data:
        return None

    # Convert tuples to list format
    table_data = [[label, str(value) if value else ''] for label, value in data]

    col_widths = [label_width]
    if value_width:
        col_widths.append(value_width)

    table = Table(table_data, colWidths=col_widths if len(col_widths) > 1 else None)
    table.setStyle(HffPdfStyles.get_label_value_style())

    return table


def add_image_to_elements(elements, image_path, max_width=160*mm, max_height=100*mm):
    """Add an image to the elements list, scaled appropriately.

    Args:
        elements: List to add image to
        image_path: Path to image file
        max_width: Maximum image width
        max_height: Maximum image height
    """
    if not image_path or not os.path.exists(image_path):
        return

    try:
        img = Image(image_path)

        # Scale image to fit within max dimensions while preserving aspect ratio
        img_width, img_height = img.imageWidth, img.imageHeight

        # Calculate scaling factors
        width_ratio = max_width / img_width
        height_ratio = max_height / img_height
        scale = min(width_ratio, height_ratio, 1.0)  # Don't upscale

        img.drawWidth = img_width * scale
        img.drawHeight = img_height * scale

        elements.append(img)
        elements.append(Spacer(1, 5*mm))

    except Exception as e:
        print(f"Error adding image to PDF: {e}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def safe_eval_list(value, default=None):
    """Safely evaluate a string as a Python list.

    This function replaces the unsafe eval() usage for parsing list data
    stored as strings in the database.

    Args:
        value: String representation of a list, or the list itself, or plain text
        default: Default value if parsing fails (None returns empty list)

    Returns:
        Parsed list, or empty list if parsing fails

    Examples:
        >>> safe_eval_list("[['item1', 'desc1'], ['item2', 'desc2']]")
        [['item1', 'desc1'], ['item2', 'desc2']]
        >>> safe_eval_list("Plain text that is not a list")
        []
        >>> safe_eval_list(None)
        []
        >>> safe_eval_list("")
        []
    """
    import ast

    if default is None:
        default = []

    # Handle None or empty string
    if value is None or value == '' or value == 'None':
        return default

    # If already a list, return it
    if isinstance(value, list):
        return value

    # Convert to string if needed
    value_str = str(value).strip()

    # Check if it looks like a list (starts with '[')
    if not value_str.startswith('['):
        return default

    try:
        # Use ast.literal_eval for safe parsing
        result = ast.literal_eval(value_str)
        if isinstance(result, list):
            return result
        return default
    except (ValueError, SyntaxError, TypeError):
        # Not a valid Python literal
        return default


def safe_str(value, default=''):
    """Safely convert value to string.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        String representation of value
    """
    if value is None:
        return default
    try:
        return str(value)
    except:
        return default


def truncate_text(text, max_length=50):
    """Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if not text:
        return ''
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def format_date(date_value, output_format='%Y-%m-%d'):
    """Format date value to string.

    Args:
        date_value: Date to format (string or datetime)
        output_format: Output date format

    Returns:
        Formatted date string
    """
    if not date_value:
        return ''

    if isinstance(date_value, str):
        # Try to parse common date formats
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
            try:
                dt = datetime.strptime(date_value, fmt)
                return dt.strftime(output_format)
            except:
                continue
        return date_value

    try:
        return date_value.strftime(output_format)
    except:
        return str(date_value)
