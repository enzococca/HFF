# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Base Form Utilities
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

import re
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QMessageBox, QPushButton, QLabel, QGroupBox, QTabWidget,
    QCheckBox, QRadioButton, QToolButton, QAction, QMenu,
    QComboBox, QTableWidget
)

from .hff_i18n import HffI18n, tr
from .hff_theme_manager import ThemeManager


def extract_text_from_html(html_text):
    """Extract plain text from HTML-formatted strings.

    Args:
        html_text: HTML string

    Returns:
        Plain text without HTML tags
    """
    if not html_text:
        return html_text
    # Remove HTML tags
    plain = re.sub(r'<[^>]+>', '', html_text)
    # Decode HTML entities
    plain = plain.replace('&lt;', '<').replace('&gt;', '>')
    plain = plain.replace('&amp;', '&').replace('&quot;', '"')
    return plain.strip()


# Comprehensive dictionary mapping English UI text to translation keys
# This allows automatic translation of .ui file text
UI_TEXT_TO_KEY = {
    # =========================================================================
    # NAVIGATION BUTTONS
    # =========================================================================
    'First': 'first',
    'Prev': 'prev',
    'Previous': 'prev',
    'Next': 'next',
    'Last': 'last',
    'First rec': 'first_rec',
    'Prev rec': 'prev_rec',
    'Next rec': 'next_rec',
    'Last rec': 'last_rec',
    'First Record': 'first_record',
    'Previous Record': 'prev_record',
    'Next Record': 'next_record',
    'Last Record': 'last_record',
    'New record': 'new_record',
    'New Record': 'new_record',
    'Delete record': 'delete_record',
    'record n.': 'record_n',
    'record tot.': 'record_tot',
    'View alls records': 'view_alls_records',
    'Go to form': 'go_to_form',

    # =========================================================================
    # ACTION BUTTONS
    # =========================================================================
    'Save': 'save',
    'Cancel': 'cancel',
    'Close': 'close',
    'Add': 'add',
    'New': 'new',
    'Edit': 'edit',
    'Delete': 'delete',
    'Remove': 'remove',
    'Refresh': 'refresh',
    'Revert': 'revert',
    'Search': 'search',
    'search !!!': 'search_!!!',
    'new search': 'new_search',
    'New Search': 'new_search',
    'Find': 'find',
    'Filter': 'filter',
    'Show All': 'show_all',
    'View All': 'view_all',
    'Sort': 'sort',
    'Order': 'order',
    'Order by': 'order_by',
    'Connect': 'connect',
    'Disconnect': 'disconnect',
    'Test': 'test',
    'Connection test': 'connection_test',
    'Test Connection': 'test_connection',
    'Browse': 'browse',
    'Browse...': 'browse',
    'Open': 'open',
    'Print': 'print',
    'Preview': 'preview',
    'Preview ': 'preview',
    'Convert': 'convert',
    'OK': 'ok',
    'Yes': 'yes',
    'No': 'no',
    'Apply': 'apply',
    'Reset': 'reset',
    'Clear': 'clear',
    'Help': 'help',
    'Insert row': 'insert_row',
    'Delete row': 'delete_row',
    'Removed row': 'removed_row',

    # =========================================================================
    # EXPORT & IMPORT
    # =========================================================================
    'Export': 'export',
    'Import': 'import',
    'Export PDF': 'export_pdf',
    'PDF': 'pdf',
    'Export Excel': 'export_excel',
    'Excel': 'excel',
    'Export CSV': 'export_csv',
    'CSV': 'csv',
    'Export TAB': 'export_tab',
    'Export List': 'export_list',
    'PDF path': 'pdf_path',
    'Pdf2Word': 'pdf2word',
    'choose the pdf convert to word': 'choose_pdf_convert',
    'Report': 'report',
    'Report generator': 'report_generator',
    'Photo list with Thumbnail': 'photo_list_with_thumbnail',
    'Photo list without Thumbnail': 'photo_list_without_thumbnail',
    'Export Photo List (with thumbnails)': 'export_photo_list_thumbnails',
    'Export Photo List (no thumbnails)': 'export_photo_list_no_thumbnails',

    # =========================================================================
    # TAB NAMES
    # =========================================================================
    'General': 'general',
    'Details': 'details',
    'Data': 'data',
    'Settings': 'settings',
    'Options': 'options',
    'Configuration': 'configuration',
    'Properties': 'properties',
    'Information': 'information',
    'Info': 'info',
    'DB Info': 'db_info',
    'Media': 'media',
    'Images': 'images',
    'Photos': 'photos',
    'Documents': 'documents',
    'Attachments': 'attachments',
    'Notes': 'notes',
    'Bibliography': 'bibliography',
    'References': 'references',
    'Storage': 'storage',
    'Storage Location': 'storage_location',
    'Store': 'store',
    'Location': 'location',
    'Coordinates': 'coordinates',
    'GIS': 'gis',
    'GIS View': 'gis_view',
    'GIS View ': 'gis_view',
    'Map': 'map',
    '3D': '3d',
    '3D View': '3d_view',
    'Statistics': 'statistics',
    'Statistic': 'statistic',
    'Charts': 'charts',
    'Reports': 'reports',
    'Tools': 'tools',
    'Comparison': 'comparison',
    'History': 'history',
    'Measurements': 'measurements',

    # =========================================================================
    # COMMON LABELS
    # =========================================================================
    'Site': 'site',
    'Site Name': 'site_name',
    'Name': 'name',
    'Code': 'code',
    'Code ID': 'code_id',
    'ID': 'id',
    'Type': 'type',
    'Category': 'category',
    'Status': 'status',
    'State': 'state',
    'Date': 'date',
    'Year': 'year',
    'Period': 'period',
    'Description': 'description',
    'Description data': 'description_data',
    'Condition': 'condition',
    'Material': 'material',
    'Materials': 'materials',
    'Dimensions': 'dimensions',
    'Length': 'length',
    'Width': 'width',
    'Height': 'height',
    'Depth': 'depth',
    'Depth found': 'depth_found',
    'Thickness': 'thickness',
    'Weight': 'weight',
    'Area': 'area',
    'Volume': 'volume',
    'Quantity': 'quantity',
    'Qty': 'qty',
    'Count': 'count',
    'Total': 'total',
    'Color': 'color',
    'Colour': 'color',
    'Origin': 'origin',
    'Provenance': 'provenance',
    'Dating': 'dating',
    'Chronology': 'chronology',
    'Place': 'place',
    'Position': 'position',
    'Drawings': 'drawings',
    'Draw.': 'draw',
    'Field': 'field',
    'Fig.': 'fig',
    'Pag.': 'pag',
    'Pagg.': 'pagg',
    'Text': 'text',
    'Title': 'title',
    'Author': 'author',
    'Comments': 'comments',
    'Supplements': 'supplements',
    'Nr. Box': 'nr_box',
    'Pieces': 'pieces',
    'table list': 'table_list',
    ' table list': 'table_list',
    'CheckBox': 'checkbox',

    # =========================================================================
    # COORDINATES & GIS
    # =========================================================================
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Northing': 'northing',
    'Easting': 'easting',
    'Elevation': 'elevation',
    'Altitude': 'altitude',
    'X': 'x_coord',
    'Y': 'y_coord',
    'Z': 'z_coord',
    'Layer': 'layer',
    'Show Selcted Features': 'show_selected_features',
    'Import all layers': 'import_all_layers',
    'Import track': 'import_track',

    # =========================================================================
    # DIVE LOG SPECIFIC
    # =========================================================================
    'Dive': 'dive',
    'Dive Log': 'dive_log',
    'Dive Log Form': 'dive_log_form',
    'DIVE ID': 'dive_id',
    'Dive Number': 'dive_number',
    'Diver': 'diver',
    'Diver 1': 'diver_1',
    'Diver 2': 'diver_2',
    'Additional diver': 'additional_diver',
    'Dive Supervisor': 'dive_supervisor',
    'Standby diver': 'standby_diver',
    'Bottom time': 'bottom_time',
    'Bottom Time': 'bottom_time',
    'Max depth': 'max_depth',
    'Max Depth': 'max_depth',
    'Depth max': 'depth_max',
    'Visibility': 'visibility',
    'UW Visibility': 'uw_visibility',
    'Water Temp': 'water_temp',
    'Water Temperature': 'water_temp',
    'UW Temperature': 'uw_temperature',
    'Current': 'current',
    'UW Current dir/str': 'uw_current',
    'Weather': 'weather',
    'Wind': 'wind',
    'Time in': 'time_in',
    'Time out': 'time_out',
    'Entry Time': 'entry_time',
    'Exit Time': 'exit_time',
    'Bar start Diver 1': 'bar_start_diver_1',
    'Bar end Diver 1': 'bar_end_diver_1',
    'Bar start Diver 2': 'bar_start_diver_2',
    'Bar end Diver 2': 'bar_end_diver_2',
    'Δ P Diver 1': 'delta_p_diver_1',
    'Δ P Diver 2': 'delta_p_diver_2',
    'Surface interval': 'surface_interval',
    'Breathing mix': 'breathing_mix',
    'Task': 'task',
    'Camera': 'camera',
    'Photo Environment': 'photo_environment',
    'Sketch': 'sketch',
    'Low': 'low',
    'Medium': 'medium',
    'Strong': 'strong',
    'Result': 'result',
    'HFF Divelog Underwater Survey ': 'hff_divelog',

    # =========================================================================
    # ANCHOR SPECIFIC
    # =========================================================================
    'Anchor': 'anchor',
    'Anchors': 'anchors',
    'Anchor form': 'anchor_form',
    'Anchor list': 'anchor_list',
    'Anchor export pdf': 'anchor_export_pdf',
    'Anchor Type': 'anchor_type',
    'Anchor shape': 'anchor_shape',
    'Anchor Material': 'anchor_material',
    'Stock': 'stock',
    'Shank': 'shank',
    'Arms': 'arms',
    'Arm': 'arm',
    'Flukes': 'flukes',
    'Fluke': 'fluke',
    'Hole Properties': 'hole_properties',
    'Type of hole': 'type_of_hole',
    'No hole': 'no_hole',
    '1 hole': '1_hole',
    '2 hole': '2_hole',
    '3 hole': '3_hole',
    'Diameter': 'diameter',
    'Typology': 'typology',
    'Stone Type': 'stone_type',
    'Petrography': 'petrography',
    'Petrography results': 'petrography_results',
    'Limestone': 'limestone',
    'Sandstone': 'sandstone',
    'Basalt': 'basalt',
    'Rectangular': 'rectangular',
    'Triangular': 'triangular',
    'Trapezoidal': 'trapezoidal',
    'Oval': 'oval',
    'Tubular': 'tubular',
    'Biconical': 'biconical',
    'Basket': 'basket',
    'Inscription': 'inscription',
    'Description of the inscription': 'description_inscription',
    'Tool markings': 'tool_markings',
    ' From Bottom': 'from_bottom',
    ' From Top': 'from_top',
    ' From Left': 'from_left',
    ' From Right': 'from_right',
    'Top': 'top',
    'Bottom': 'bottom',
    'Left': 'left',
    'Right': 'right',
    'HFF Underwater Anchor': 'hff_anchor',

    # =========================================================================
    # ARTEFACT SPECIFIC
    # =========================================================================
    'Artefact': 'artefact',
    'Artifact': 'artefact',
    'Artefact form': 'artefact_form',
    'Artefact list': 'artefact_list',
    'Artefact ID': 'artefact_id',
    'General Finds': 'general_finds',
    'Object': 'object',
    'Shape': 'shape',
    'Fragment': 'fragment',
    'Complete': 'complete',
    'Completeness': 'completeness',
    'Conservation': 'conservation',
    'Conservation completed': 'conservation_completed',
    'Treatment': 'treatment',
    'Recovered': 'recovered',
    'Retrieved': 'retrieved',
    'Photographed': 'photographed',
    'Photogr.': 'photogr',
    'Washed': 'washed',
    'Samples': 'samples',
    'Min': 'min',
    'Max': 'max',
    'HFF Artefacts': 'hff_artefacts',

    # =========================================================================
    # POTTERY SPECIFIC
    # =========================================================================
    'Pottery': 'pottery',
    'Pottery form': 'pottery_form',
    'Pottery list': 'pottery_list',
    'Pottery export pdf': 'pottery_export_pdf',
    'Ceramic': 'ceramic',
    'Ceramics': 'ceramics',
    'Fabric': 'fabric',
    'Form': 'form',
    'Function': 'function',
    'Rim': 'rim',
    'Rim Type': 'rim_type',
    'Base': 'base',
    'Base Type': 'base_type',
    'Base Height': 'base_height',
    'Body': 'body',
    'Upper body': 'upper_body',
    'Wall': 'wall',
    'Neck': 'neck',
    'Handle': 'handle',
    'Handle Type': 'handle_type',
    'Spout': 'spout',
    'Lid': 'lid',
    'Surface': 'surface',
    'Surface treatment': 'surface_treatment',
    'Decoration': 'decoration',
    'Technique': 'technique',
    'Inclusions': 'inclusions',
    'Percentage of the inclusions': 'percentage_inclusions',
    'Munsell colour clay': 'munsell_colour_clay',
    'Munsell colour surf': 'munsell_colour_surf',
    'Diameter Rim': 'diameter_rim',
    'Diameter Max': 'diameter_max',
    'Diameter Bottom': 'diameter_bottom',
    'Total Height': 'total_height',
    'Preserved Height': 'preserved_height',
    'Specific part': 'specific_part',
    # Pottery types
    'Amphora': 'amphora',
    'Jar': 'jar',
    'Jug': 'jug',
    'Juglet': 'juglet',
    'Bowl': 'bowl',
    'Plate': 'plate',
    'Basin': 'basin',
    'Bottle': 'bottle',
    'Cooking pot': 'cooking_pot',
    'Cooking ware': 'cooking_ware',
    'Fine ware': 'fine_ware',
    'Coarse ware': 'coarse_ware',
    'Storage ware': 'storage_ware',
    'Transport containers': 'transport_containers',
    'Slipped red': 'slipped_red',
    'Polished': 'polished',
    'Wheel made': 'wheel_made',
    'Buff': 'buff',
    'HFF Underwater- Pottery': 'hff_pottery',

    # =========================================================================
    # SHIPWRECK SPECIFIC
    # =========================================================================
    'Shipwreck': 'shipwreck',
    'Shipwreck form': 'shipwreck_form',
    'Shipwreck list': 'shipwreck_list',
    'Shipwreck export pdf': 'shipwreck_export_pdf',
    'Wreck': 'wreck',
    'Vessel': 'vessel',
    'Vessel Type': 'vessel_type',
    'Name Vessel': 'name_vessel',
    'Nickname': 'nickname',
    'Hull': 'hull',
    'Hull Type': 'hull_type',
    'Cargo': 'cargo',
    'Nationality': 'nationality',
    'Flag': 'flag',
    'Construction': 'construction',
    'Wood Type': 'wood_type',
    'Estimated Date': 'estimated_date',
    'Date Built': 'date_built',
    'Date Lost': 'date_lost',
    'Builder': 'builder',
    'Owner': 'owner',
    'Yard no./IMO': 'yard_no_imo',
    'Tonnage': 'tonnage',
    'Draught': 'draught',
    'Propulsion': 'propulsion',
    'Purpose': 'purpose',
    'Confidence': 'confidence',
    'Certain': 'certain',
    'Likely': 'likely',
    'Suspect': 'suspect',
    'Inconsistent': 'inconsistent',
    'Unreliable': 'unreliable',
    'Unknow': 'unknow',
    # Position
    'Position of Wreck': 'position_wreck',
    'Position quality': 'position_quality',
    'Depth quality': 'depth_quality',
    'Lying on deck': 'lying_on_deck',
    'Lying on side (port)': 'lying_on_side_port',
    'Lying on side (starboard)': 'lying_on_side_starboard',
    'Lying on underside': 'lying_on_underside',
    'Vertical (bow up)': 'vertical_bow_up',
    'Vertical (stern up)': 'vertical_stern_up',
    'Capsized': 'capsized',
    'Flat': 'flat',
    'Sloping': 'sloping',
    # Causes
    'Cause of lose': 'cause_of_lose',
    'Collision': 'collision',
    'Foundered': 'foundered',
    'Ran aground': 'ran_aground',
    'Fire': 'fire',
    'Explosion': 'explosion',
    'Combat': 'combat',
    'Conflict': 'conflict',
    'Rammed': 'rammed',
    'Scuttled': 'scuttled',
    'Water Leakage': 'water_leakage',
    'Foul': 'foul',
    'Crash': 'crash',
    # Sea bed
    'Sea bed composition': 'sea_bed_composition',
    'Sea bed inclination': 'sea_bed_inclination',
    # Vessel types
    'Battleship': 'battleship',
    'Submarine': 'submarine',
    'Tanker': 'tanker',
    'Passenger ship': 'passenger_ship',
    'Cointainer ship': 'container_ship',
    'Ocean linear': 'ocean_linear',
    'Patrol Boat': 'patrol_boat',
    'Leisure': 'leisure',
    'Transportation': 'transportation',
    # Materials
    'Wood': 'wood',
    'Steel': 'steel',
    'Fiberglass': 'fiberglass',
    # Propulsion
    'Sail': 'sail',
    'Steam': 'steam',
    'Diesel': 'diesel',
    'MV': 'mv',
    # Accessibility
    'Accessibility to divers': 'accessibility_divers',
    'Accessible': 'accessible',
    'Not accessible': 'not_accessible',
    'Obstruction': 'obstruction',
    'Protected': 'protected',
    'Consulties': 'consulties',
    'HFF ModernShipwreck': 'hff_modern_shipwreck',

    # =========================================================================
    # MEDIA & PHOTOS
    # =========================================================================
    'Thumbnail': 'thumbnail',
    'Image': 'image',
    'Photo': 'photo',
    'Photo id': 'photo_id',
    'N Photo': 'n_photo',
    'Video': 'video',
    'Video id': 'video_id',
    'N Video': 'n_video',
    'Audio': 'audio',
    'File': 'file',
    'Path': 'path',
    'URL': 'url',
    'Tags': 'tags',

    # =========================================================================
    # STATUS MESSAGES
    # =========================================================================
    'Loading...': 'loading',
    'Saving...': 'saving',
    'Searching...': 'searching',
    'Processing...': 'processing',
    'Success': 'success',
    'Error': 'error',
    'Warning': 'warning',
    'Failed': 'failed',

    # =========================================================================
    # RECORD NAVIGATION
    # =========================================================================
    'Record': 'record',
    'Records': 'records',
    'of': 'of',
    'to': 'to',
    'Selected': 'selected',
    'No records': 'no_records',
    'No records found': 'no_records_found',

    # =========================================================================
    # USERS & DATABASE
    # =========================================================================
    'User': 'user',
    'Username': 'username',
    'Password': 'password',
    'Email': 'email',
    'Role': 'role',
    'Permissions': 'permissions',
    'Database': 'database',
    'Host': 'host',
    'Port': 'port',
    'Server': 'server',
    'Connection': 'connection',

    # =========================================================================
    # MEASUREMENT ABBREVIATIONS
    # =========================================================================
    'C': 'c',
    'D': 'd',
    'L': 'l',
    'W': 'w',
    'BT': 'bt',
    'BW': 'bw',
    'LL': 'll',
    'LT': 'lt',
    'ML': 'ml',
    'MW': 'mw',
    'RL': 'rl',
    'RT': 'rt',
    'TT': 'tt',
    'TW': 'tw',

    # =========================================================================
    # CONSERVATION STATUS
    # =========================================================================
    'Conserved D': 'conserved_d',
    'Conserved L': 'conserved_l',
    'Conserved W': 'conserved_w',

    # =========================================================================
    # ADDITIONAL SITE / SURVEY FIELDS
    # =========================================================================
    'Survey': 'survey',
    'Survey Type': 'survey_type',
    'Survey site': 'survey_site',
    'Start date': 'start_date',
    'Country name': 'country_name',
    'Definition site': 'definition_site',
    'Administrative subvision': 'admin_subdivision',
    'Administrative subvision type': 'admin_subdivision_type',
    'Address': 'address',
    'Antique name': 'antique_name',
    'Site name': 'site_name',
    'Site Datum Point': 'site_datum_point',
    'Activity type': 'activity_type',

    # =========================================================================
    # ADDITIONAL DIVE LOG FIELDS
    # =========================================================================
    'Dive Supervisor': 'dive_supervisor',
    'Standby diver': 'standby_diver',
    'Additional diver': 'additional_diver',
    'Bar start Diver 1': 'bar_start_diver_1',
    'Bar end Diver 1': 'bar_end_diver_1',
    'Bar start Diver 2': 'bar_start_diver_2',
    'Bar end Diver 2': 'bar_end_diver_2',
    'Δ P Diver 1': 'delta_p_diver_1',
    'Δ P Diver 2': 'delta_p_diver_2',
    'Bottom time': 'bottom_time',
    'Bottom Time': 'bottom_time',
    'Surface interval': 'surface_interval',
    'Breathing mix': 'breathing_mix',
    'Max depth': 'max_depth',
    'UW Visibility': 'uw_visibility',
    'UW Temperature': 'uw_temperature',
    'UW Current dir/str': 'uw_current',
    'Time in': 'time_in',
    'Time out': 'time_out',
    'Task': 'task',
    'Camera': 'camera',
    'Result': 'result',

    # =========================================================================
    # ADDITIONAL ANCHOR FIELDS
    # =========================================================================
    'Anchor ID': 'anchor_id',
    'Anchor con': 'anchor_con',
    'Anchor Conservation': 'anchor_conservation',
    'Anchor Conservation list': 'anchor_conservation_list',
    'Anchor conservation export pdf': 'anchor_conservation_export_pdf',
    'ANCHOR_POINT': 'anchor_point',
    'Stone Type': 'stone_type',
    'Type of hole': 'type_of_hole',
    'No hole': 'no_hole',
    '1 hole': '1_hole',
    '2 hole': '2_hole',
    '3 hole': '3_hole',
    'Bottom Hole': 'bottom_hole',
    'Top Hole': 'top_hole',
    'Petrography': 'petrography',
    'Petrography results': 'petrography_results',
    'Tool markings': 'tool_markings',
    'Inscription': 'inscription',
    'Description of the inscription': 'description_inscription',

    # =========================================================================
    # ADDITIONAL ARTEFACT FIELDS
    # =========================================================================
    'Artefact con': 'artefact_con',
    'Art conservation': 'art_conservation',
    'ARTEFACT_POINT': 'artefact_point',
    'General Finds': 'general_finds',
    'Object': 'object',
    'State of conservation': 'state_of_conservation',
    'Recovered': 'recovered',
    'Photographed': 'photographed',
    'Photogr.': 'photogr',
    'Samples': 'samples',
    'Treatment': 'treatment',
    'Washed': 'washed',
    'Conservation completed': 'conservation_completed',

    # =========================================================================
    # ADDITIONAL POTTERY FIELDS
    # =========================================================================
    'Fabric': 'fabric',
    'Form': 'form',
    'Function': 'function',
    'Rim': 'rim',
    'Rim Type': 'rim_type',
    'Base': 'base',
    'Base Type': 'base_type',
    'Base Height': 'base_height',
    'Body': 'body',
    'Upper body': 'upper_body',
    'Neck': 'neck',
    'Handle': 'handle',
    'Handle Type': 'handle_type',
    'Spout': 'spout',
    'Lid': 'lid',
    'Surface': 'surface',
    'Surface treatment': 'surface_treatment',
    'Decoration': 'decoration',
    'Technique': 'technique',
    'Inclusions': 'inclusions',
    'Percentage of the inclusions': 'percentage_inclusions',
    'Munsell colour clay': 'munsell_colour_clay',
    'Munsell colour surf': 'munsell_colour_surf',
    'Diameter Rim': 'diameter_rim',
    'Diameter Max': 'diameter_max',
    'Diameter Bottom': 'diameter_bottom',
    'Total Height': 'total_height',
    'Preserved Height': 'preserved_height',
    'Specific part': 'specific_part',

    # =========================================================================
    # ADDITIONAL SHIPWRECK FIELDS
    # =========================================================================
    'Accessibility to divers': 'accessibility_divers',
    'Position of Wreck': 'position_wreck',
    'Position quality': 'position_quality',
    'Depth quality': 'depth_quality',
    'Sea bed composition': 'sea_bed_composition',
    'Sea bed inclination': 'sea_bed_inclination',
    'Cause of lose': 'cause_of_lose',
    'Date Built': 'date_built',
    'Date Lost': 'date_lost',
    'Yard no./IMO': 'yard_no_imo',
    'Tonnage': 'tonnage',
    'Draught': 'draught',
    'Consulties': 'consulties',

    # =========================================================================
    # COMBOBOX VALUES - YES/NO
    # =========================================================================
    'yes': 'yes_lower',
    'no': 'no_lower',

    # =========================================================================
    # COMBOBOX VALUES - CONDITION/STATUS
    # =========================================================================
    'Good': 'good',
    'Bad': 'bad',
    'Very Bad': 'very_bad',
    'Very bed': 'very_bad',
    'Unknown': 'unknown',

    # =========================================================================
    # COMBOBOX VALUES - DIRECTION
    # =========================================================================
    'North': 'north',
    'South': 'south',
    'East': 'east',
    'West': 'west',
    'North-East': 'north_east',
    'North-West': 'north_west',
    'South-East': 'south_east',
    'South-West': 'south_west',

    # =========================================================================
    # COMBOBOX VALUES - SHAPES
    # =========================================================================
    'Circular': 'circular',
    'Sub-circular': 'sub_circular',
    'Sub-rectangular': 'sub_rectangular',
    'Irregular': 'irregular',
    'Square': 'square',
    'Round': 'round',
    'Straight': 'straight',
    'Winding': 'winding',
    'Zigzag': 'zigzag',

    # =========================================================================
    # COMBOBOX VALUES - GEOLOGY/TERRAIN
    # =========================================================================
    'Alluvial fan': 'alluvial_fan',
    'Valley bed': 'valley_bed',
    'Valley terrace': 'valley_terrace',
    'Slopes': 'slopes',
    'Summit': 'summit',
    'Watercourse banks': 'watercourse_banks',
    'Watercourse bed': 'watercourse_bed',

    # =========================================================================
    # BUTTON TOOLTIPS & ACTIONS
    # =========================================================================
    'First record': 'first_record',
    'Previus record': 'prev_record',
    'Next record': 'next_record',
    'Last record': 'last_record',
    'Save record': 'save_record',
    'Delete single record': 'delete_single_record',
    'Reload all records': 'reload_all_records',
    'Filter records': 'filter_records',
    'Start query search': 'start_query_search',
    'Export Pdf form': 'export_pdf_form',
    'Export Excel': 'export_excel',
    'Import all layers': 'import_all_layers',
    'Import track': 'import_track',
    'View Layers': 'view_layers',
    'GIS Tools': 'gis_tools',
    'Show Selcted Features': 'show_selected_features',
    'insert the name field': 'insert_name_field',
    'rollback the changed': 'rollback_changed',
    'save record after chanched': 'save_record_changed',
    'write the word to search': 'write_word_search',
    'Select the row and directly go to record into the form': 'select_row_go_record',
    'Active/deactive media view': 'active_deactive_media_view',
    'Upload the photos to the database (link) and view them in the listWidget': 'upload_photos_db',
    'Remove selected thumbnails': 'remove_selected_thumbnails',
    'Assign tag to selected images': 'assign_tag_images',
    'Remove all tags from selected images': 'remove_all_tags_images',
    'Activate/deactivate the display of tags': 'activate_tags_display',
    'Image search bar': 'image_search_bar',

    # =========================================================================
    # ADDITIONAL LABELS
    # =========================================================================
    'Total record.': 'total_record',
    'Total images': 'total_images',
    'Total images ': 'total_images',
    'Tag': 'tag',
    'Tags': 'tags',
    'Tags manager': 'tags_manager',
    'Tags viewer on/off': 'tags_viewer_onoff',
    'Add tags': 'add_tags',
    'Thumbnail path': 'thumbnail_path',
    'Video id': 'video_id',
    'Photo id': 'photo_id',
    'insert row': 'insert_row',
    'remove row': 'remove_row',
    'Supervisor': 'supervisor',
    'Author': 'author',
    'Summary': 'summary',
    'Thesaurus': 'thesaurus',
    'Value': 'value',
    'Backup / Restore HFF DB': 'backup_restore_hff_db',
    'Backup HFF survey DB': 'backup_hff_survey_db',
    'Backup postgres': 'backup_postgres',
    'Backup sqlite': 'backup_sqlite',
    'Tutorials': 'tutorials',
    'Table list': 'table_list',
    'Start': 'start',
    'Abort': 'abort',
}


def log_pdf_export_error(form_name):
    """Log the PDF-export exception currently being handled (full
    traceback plus the installed reportlab version) to the QGIS Log
    Messages panel, tab 'HFF'. The error popups only show str(e); this
    gives users something complete to screenshot when reporting export
    failures (issue #56). Call from inside an except block; never raises."""
    import traceback
    try:
        from qgis.core import QgsMessageLog, Qgis
        try:
            import reportlab
            rl_version = reportlab.Version
        except Exception:
            rl_version = "unknown"
        QgsMessageLog.logMessage(
            "%s PDF export failed (reportlab %s)\n%s"
            % (form_name, rl_version, traceback.format_exc()),
            "HFF", Qgis.Critical)
    except Exception:
        pass


class HffFormMixin:
    """Mixin class providing i18n and theme support for HFF forms.

    Usage:
        class MyForm(QDialog, MAIN_DIALOG_CLASS, HffFormMixin):
            def __init__(self, ...):
                super().__init__()
                self.setupUi(self)
                self.init_hff_features()  # Call this after setupUi
    """

    def init_hff_features(self):
        """Initialize HFF features (i18n, theme, RTL support).

        Call this method after setupUi() in your form's __init__.
        """
        self.i18n = HffI18n.instance()
        self.apply_theme()
        self.apply_rtl_if_needed()
        self.translate_ui()

    def apply_theme(self):
        """Apply the current theme to this form."""
        ThemeManager.instance().apply_theme(self)

    def apply_rtl_if_needed(self):
        """Apply RTL direction to text-only widgets when the language is RTL.

        Many HFF .ui forms position widgets with absolute <geometry>. Setting
        layoutDirection=RightToLeft on the whole form mirrors only layout-based
        children, leaving absolute-positioned widgets in place and causing
        overlaps. We only flip text-containing widgets so Arabic reads right
        while the visual layout stays put.
        """
        _apply_rtl_to_text_widgets(self, self.i18n.is_rtl())

    def translate_ui(self):
        """Translate UI elements.

        Override this method in subclasses to translate specific elements.
        """
        # Translate window title if set
        if hasattr(self, 'MSG_BOX_TITLE'):
            # Keep original for now, can be overridden
            pass

        # Translate common buttons if they exist
        self._translate_buttons()

    def _translate_buttons(self):
        """Translate common button texts."""
        button_translations = {
            'pushButton_save': ('save', 'Save'),
            'pushButton_new_rec': ('new_record', 'New Record'),
            'pushButton_delete': ('delete', 'Delete'),
            'pushButton_search': ('search', 'Search'),
            'pushButton_show_all': ('show_all', 'Show All'),
            'pushButton_sort': ('sort', 'Sort'),
            'pushButton_new_search': ('new_search', 'New Search'),
            'pushButton_close': ('close', 'Close'),
            'pushButton_export_pdf': ('export_pdf', 'Export PDF'),
            'pushButton_export_excel': ('export_excel', 'Export Excel'),
            'pushButton_connect': ('connect', 'Connect'),
            'toolButton_save': ('save', 'Save'),
        }

        for attr_name, (key, default) in button_translations.items():
            if hasattr(self, attr_name):
                btn = getattr(self, attr_name)
                if isinstance(btn, QPushButton):
                    btn.setText(tr(key, default))

    def tr(self, key, default=None):
        """Shortcut for translation."""
        return tr(key, default)

    def show_info(self, message, title=None):
        """Show information message box with translated title."""
        QMessageBox.information(
            self,
            title or tr('info', 'Information'),
            message
        )

    def show_warning(self, message, title=None):
        """Show warning message box with translated title."""
        QMessageBox.warning(
            self,
            title or tr('warning', 'Warning'),
            message
        )

    def show_error(self, message, title=None):
        """Show error message box with translated title."""
        QMessageBox.critical(
            self,
            title or tr('error', 'Error'),
            message
        )

    def show_success(self, message, title=None):
        """Show success message box with translated title."""
        QMessageBox.information(
            self,
            title or tr('success', 'Success'),
            message
        )

    def confirm_action(self, message, title=None):
        """Show confirmation dialog and return True if user confirms."""
        reply = QMessageBox.question(
            self,
            title or tr('confirm', 'Confirm'),
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def standardize_toolbar(self):
        """Standardize the toolbar button layout and tooltips.

        Sets consistent tooltips and tab order for toolbar buttons.
        Standard layout:
            Row 1: Navigation [<<] [<] [Record] [>] [>>]
            Row 2: Actions [New] [Save] [Delete] | [Search] [New Search] [Sort] [View All]
            Row 3: Export [PDF] [Excel] [List] | GIS [GIS View] [Layers] | Media [Photos] [Tags]
        """
        # Define button configurations: (attribute_name, tooltip_key, tooltip_default)
        button_configs = [
            # Navigation buttons
            ('pushButton_first_rec', 'first_record', 'First record'),
            ('pushButton_prev_rec', 'prev_record', 'Previous record'),
            ('pushButton_next_rec', 'next_record', 'Next record'),
            ('pushButton_last_rec', 'last_record', 'Last record'),

            # Record action buttons
            ('pushButton_new_rec', 'new_record', 'New record'),
            ('pushButton_save', 'save_record', 'Save record'),
            ('pushButton_delete', 'delete_single_record', 'Delete record'),

            # Search buttons
            ('pushButton_search_go', 'start_query_search', 'Start search'),
            ('pushButton_new_search', 'new_search', 'New search'),
            ('pushButton_sort', 'sort', 'Sort records'),
            ('pushButton_view_all', 'view_alls_records', 'View all records'),

            # Export buttons
            ('pushButton_form', 'export_pdf_form', 'Export PDF'),
            ('pushButton_exppdf', 'export_pdf_form', 'Export PDF'),
            ('pushButton_print', 'export_pdf_form', 'Export PDF'),
            ('pushButton_list', 'export_list', 'Export list'),
            ('pushButton_explist', 'export_list', 'Export list'),
            ('pushButton_exptab', 'export_tab', 'Export table'),
            ('pushButton_word', 'pdf2word', 'Export to Word'),

            # GIS buttons
            ('pushButton_gisview', 'gis_view', 'GIS View'),
            ('pushButton_showLayer', 'view_layers', 'Show layers'),
            ('pushButton_uw_geometry', 'gis_tools', 'GIS tools'),
            ('pushButton_track', 'import_track', 'Import track'),

            # Media buttons
            ('pushButton_all_images', 'photos', 'View all images'),
            ('pushButton_assigntags', 'assign_tag_images', 'Assign tags to images'),
            ('pushButton_removetags', 'remove_all_tags_images', 'Remove tags from images'),

            # Other buttons
            ('pushButton_connect', 'connection_test', 'Test connection'),
            ('pushButton_filter_uw', 'filter_records', 'Filter records'),
            ('pushButton_report_generator', 'report_generator', 'Generate report'),
            ('pushButton_open_dir', 'open', 'Open directory'),
            ('pushButton_revert', 'revert', 'Revert changes'),
            ('pushButton_submit', 'save', 'Save'),
            ('pushButton_go_to_scheda', 'go_to_form', 'Go to record'),
            ('pushButton_convert', 'convert', 'Convert'),
            ('pushButtonQuant', 'statistics', 'Statistics'),
        ]

        # Apply tooltips
        for attr_name, tooltip_key, tooltip_default in button_configs:
            if hasattr(self, attr_name):
                btn = getattr(self, attr_name)
                if isinstance(btn, (QPushButton, QToolButton)):
                    btn.setToolTip(tr(tooltip_key, tooltip_default))

        # Set tab order for navigation (if buttons exist)
        nav_buttons = ['pushButton_first_rec', 'pushButton_prev_rec',
                       'pushButton_next_rec', 'pushButton_last_rec']
        prev_btn = None
        for btn_name in nav_buttons:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if prev_btn:
                    self.setTabOrder(prev_btn, btn)
                prev_btn = btn


def translate_widget_text(text, preserve_html=False):
    """Translate a single text string if it has a translation key.

    Args:
        text: The text to translate
        preserve_html: If True, preserve HTML formatting around translated text

    Returns:
        Translated text or original if no translation found
    """
    if not text:
        return text

    # Check if text contains HTML
    is_html = '<' in text and '>' in text

    # Extract plain text if HTML
    if is_html:
        plain_text = extract_text_from_html(text)
    else:
        plain_text = text

    # Clean the text (preserve leading/trailing spaces for matching)
    clean_text = plain_text

    # Look up in UI_TEXT_TO_KEY mapping
    translated = None
    if clean_text in UI_TEXT_TO_KEY:
        key = UI_TEXT_TO_KEY[clean_text]
        translated = tr(key, plain_text)
    else:
        # Try stripped version
        stripped_text = plain_text.strip()
        if stripped_text in UI_TEXT_TO_KEY:
            key = UI_TEXT_TO_KEY[stripped_text]
            translated = tr(key, plain_text)
        else:
            # Try lowercase
            lower_text = stripped_text.lower()
            for ui_text, key in UI_TEXT_TO_KEY.items():
                if ui_text.lower() == lower_text:
                    translated = tr(key, plain_text)
                    break

    if translated and translated != plain_text:
        if is_html and preserve_html:
            # Replace the plain text within the HTML with the translation
            return text.replace(plain_text, translated)
        return translated

    return text


def translate_all_widgets(form):
    """Recursively translate all translatable widgets in a form.

    Args:
        form: The form/dialog to translate
    """
    i18n = HffI18n.instance()

    # Translate window/dialog title
    if hasattr(form, 'windowTitle'):
        title = form.windowTitle()
        if title:
            translated = translate_widget_text(title)
            if translated != title:
                form.setWindowTitle(translated)

    # Get all QLabel widgets
    for widget in form.findChildren(QLabel):
        text = widget.text()
        if text:
            # Handle HTML-formatted labels
            translated = translate_widget_text(text, preserve_html=True)
            if translated != text:
                widget.setText(translated)

    # Translate push buttons
    for widget in form.findChildren(QPushButton):
        text = widget.text()
        if text:
            translated = translate_widget_text(text)
            if translated != text:
                widget.setText(translated)
        # Also translate tooltip
        tooltip = widget.toolTip()
        if tooltip:
            translated = translate_widget_text(tooltip)
            if translated != tooltip:
                widget.setToolTip(translated)

    # Translate tool buttons
    for widget in form.findChildren(QToolButton):
        text = widget.text()
        if text:
            translated = translate_widget_text(text)
            if translated != text:
                widget.setText(translated)
        tooltip = widget.toolTip()
        if tooltip:
            translated = translate_widget_text(tooltip)
            if translated != tooltip:
                widget.setToolTip(translated)

    # Translate group boxes
    for widget in form.findChildren(QGroupBox):
        text = widget.title()
        if text:
            translated = translate_widget_text(text)
            if translated != text:
                widget.setTitle(translated)

    # Translate tab widgets
    for tab_widget in form.findChildren(QTabWidget):
        for i in range(tab_widget.count()):
            text = tab_widget.tabText(i)
            if text:
                translated = translate_widget_text(text)
                if translated != text:
                    tab_widget.setTabText(i, translated)

    # Translate checkboxes
    for widget in form.findChildren(QCheckBox):
        text = widget.text()
        if text:
            translated = translate_widget_text(text)
            if translated != text:
                widget.setText(translated)

    # Translate radio buttons
    for widget in form.findChildren(QRadioButton):
        text = widget.text()
        if text:
            translated = translate_widget_text(text)
            if translated != text:
                widget.setText(translated)

    # Translate QComboBox items
    for widget in form.findChildren(QComboBox):
        for i in range(widget.count()):
            text = widget.itemText(i)
            if text:
                translated = translate_widget_text(text)
                if translated != text:
                    widget.setItemText(i, translated)

    # Translate QTableWidget headers
    for widget in form.findChildren(QTableWidget):
        # Horizontal headers
        header = widget.horizontalHeader()
        if header:
            for i in range(widget.columnCount()):
                item = widget.horizontalHeaderItem(i)
                if item:
                    text = item.text()
                    if text:
                        translated = translate_widget_text(text)
                        if translated != text:
                            item.setText(translated)
        # Vertical headers
        vheader = widget.verticalHeader()
        if vheader:
            for i in range(widget.rowCount()):
                item = widget.verticalHeaderItem(i)
                if item:
                    text = item.text()
                    if text:
                        translated = translate_widget_text(text)
                        if translated != text:
                            item.setText(translated)

    # Translate QAction items (menus)
    for action in form.findChildren(QAction):
        text = action.text()
        if text:
            translated = translate_widget_text(text)
            if translated != text:
                action.setText(translated)
        tooltip = action.toolTip()
        if tooltip:
            translated = translate_widget_text(tooltip)
            if translated != tooltip:
                action.setToolTip(translated)


def apply_i18n_to_form(form):
    """Apply i18n features to any form.

    Usage:
        apply_i18n_to_form(self)  # In form's __init__ after setupUi
    """
    i18n = HffI18n.instance()

    # Apply RTL only to text-holding widgets (see apply_rtl_if_needed docstring
    # in HffFormBase for rationale — absolute-geometry widgets would overlap).
    _apply_rtl_to_text_widgets(form, i18n.is_rtl())

    # Apply theme
    ThemeManager.instance().apply_theme(form)

    # Translate all widgets
    translate_all_widgets(form)

    # Bump input widget font size for readability (issue #45 point 1)
    _apply_log_font(form)

    # English autocorrect / spellcheck on text inputs (issue #45 point 4).
    # Only activates when the current i18n language is English and the
    # pyenchant native lib is available; silently degrades otherwise.
    try:
        if i18n.get_current_language() == 'en':
            from .hff_spellcheck import attach_spellcheck
            attach_spellcheck(form, 'en_US')
    except Exception:
        pass


def _apply_log_font(form, size_pt: int = 11):
    """Increase the font size on log-form input widgets.

    Targeted on QLineEdit / QTextEdit / QPlainTextEdit / QComboBox /
    QSpinBox / QDoubleSpinBox / QDateEdit / QTimeEdit / QDateTimeEdit.
    Labels and buttons keep the QGIS default so toolbars stay compact.
    """
    from qgis.PyQt.QtWidgets import (
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox,
        QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit,
    )
    qss = (
        "QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, "
        "QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit "
        "{ font-size: %dpt; }" % size_pt
    )
    try:
        current = form.styleSheet() or ""
        if "QLineEdit, QTextEdit, QPlainTextEdit" not in current:
            form.setStyleSheet(current + "\n" + qss)
    except Exception:
        pass


def _apply_rtl_to_text_widgets(root, rtl: bool):
    """Set layoutDirection on text widgets only, leaving containers LTR."""
    from qgis.PyQt.QtWidgets import (
        QLabel, QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QComboBox,
    )
    direction = Qt.RightToLeft if rtl else Qt.LeftToRight
    text_classes = (QLabel, QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QComboBox)
    root.setLayoutDirection(Qt.LeftToRight)
    for w in root.findChildren(text_classes):
        w.setLayoutDirection(direction)


# Export common translated strings for PDF/Excel exports
def get_export_translations():
    """Get common translations for export documents."""
    return {
        # Headers
        'site': tr('site', 'Site'),
        'location': tr('location', 'Location'),
        'area': tr('area', 'Area'),
        'date': tr('date', 'Date'),
        'description': tr('description', 'Description'),
        'notes': tr('notes', 'Notes'),
        'status': tr('status', 'Status'),
        'type': tr('type', 'Type'),
        'condition': tr('condition', 'Condition'),
        'material': tr('material', 'Material'),
        'dimensions': tr('dimensions', 'Dimensions'),
        'length': tr('length', 'Length'),
        'width': tr('width', 'Width'),
        'height': tr('height', 'Height'),
        'depth': tr('depth', 'Depth'),
        'weight': tr('weight', 'Weight'),
        'coordinates': tr('coordinates', 'Coordinates'),
        'photos': tr('photos', 'Photos'),

        # Dive log
        'dive_log': tr('dive_log', 'Dive Log'),
        'diver': tr('diver', 'Diver'),
        'dive_number': tr('dive_number', 'Dive Number'),
        'dive_date': tr('dive_date', 'Dive Date'),
        'bottom_time': tr('bottom_time', 'Bottom Time'),
        'max_depth': tr('max_depth', 'Max Depth'),
        'visibility': tr('visibility', 'Visibility'),
        'water_temp': tr('water_temp', 'Water Temperature'),
        'current': tr('current', 'Current'),
        'weather': tr('weather', 'Weather'),

        # Anchor
        'anchor': tr('anchor', 'Anchor'),
        'anchor_type': tr('anchor_type', 'Anchor Type'),
        'anchor_material': tr('anchor_material', 'Anchor Material'),

        # Artefact
        'artefact': tr('artefact', 'Artefact'),
        'artefact_id': tr('artefact_id', 'Artefact ID'),
        'category': tr('category', 'Category'),
        'function': tr('function', 'Function'),
        'period': tr('period', 'Period'),
        'dating': tr('dating', 'Dating'),

        # Pottery
        'pottery': tr('pottery', 'Pottery'),
        'fabric': tr('fabric', 'Fabric'),
        'form': tr('form', 'Form'),
        'rim_type': tr('rim_type', 'Rim Type'),
        'base_type': tr('base_type', 'Base Type'),
        'decoration': tr('decoration', 'Decoration'),

        # Shipwreck
        'shipwreck': tr('shipwreck', 'Shipwreck'),
        'vessel_type': tr('vessel_type', 'Vessel Type'),
        'hull_type': tr('hull_type', 'Hull Type'),
        'cargo': tr('cargo', 'Cargo'),
        'nationality': tr('nationality', 'Nationality'),

        # Document info
        'generated_by': tr('generated_by', 'Generated by HFF'),
        'page': tr('page', 'Page'),
        'of': tr('of', 'of'),
        'report_date': tr('report_date', 'Report Date'),
        'printed_on': tr('printed_on', 'Printed on'),

        # Table headers
        'name': tr('name', 'Name'),
        'code': tr('code', 'Code'),
        'id': tr('id', 'ID'),
        'year': tr('year', 'Year'),
        'quantity': tr('quantity', 'Quantity'),
        'total': tr('total', 'Total'),
        'latitude': tr('latitude', 'Latitude'),
        'longitude': tr('longitude', 'Longitude'),
    }


# =============================================================================
# STANDALONE MESSAGE BOX HELPER FUNCTIONS
# =============================================================================
# These functions can be used anywhere in the code to show translated messages

def show_info_message(parent, message_key, default_message, title_key='info', default_title='Information'):
    """Show translated information message box.

    Args:
        parent: Parent widget
        message_key: Translation key for the message
        default_message: Default message if key not found
        title_key: Translation key for the title
        default_title: Default title if key not found
    """
    QMessageBox.information(
        parent,
        tr(title_key, default_title),
        tr(message_key, default_message)
    )


def show_warning_message(parent, message_key, default_message, title_key='warning', default_title='Warning'):
    """Show translated warning message box.

    Args:
        parent: Parent widget
        message_key: Translation key for the message
        default_message: Default message if key not found
        title_key: Translation key for the title
        default_title: Default title if key not found
    """
    QMessageBox.warning(
        parent,
        tr(title_key, default_title),
        tr(message_key, default_message)
    )


def show_error_message(parent, message_key, default_message, title_key='error', default_title='Error'):
    """Show translated error message box.

    Args:
        parent: Parent widget
        message_key: Translation key for the message
        default_message: Default message if key not found
        title_key: Translation key for the title
        default_title: Default title if key not found
    """
    QMessageBox.critical(
        parent,
        tr(title_key, default_title),
        tr(message_key, default_message)
    )


def show_confirm_dialog(parent, message_key, default_message, title_key='confirm', default_title='Confirm'):
    """Show translated confirmation dialog.

    Args:
        parent: Parent widget
        message_key: Translation key for the message
        default_message: Default message if key not found
        title_key: Translation key for the title
        default_title: Default title if key not found

    Returns:
        True if user clicked Yes, False otherwise
    """
    reply = QMessageBox.question(
        parent,
        tr(title_key, default_title),
        tr(message_key, default_message),
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes


def show_info_message_raw(parent, message, title='Information'):
    """Show information message box with raw message (already translated or dynamic).

    Args:
        parent: Parent widget
        message: The message to display
        title: The title (will be translated if matching key exists)
    """
    QMessageBox.information(parent, translate_widget_text(title), message)


def show_warning_message_raw(parent, message, title='Warning'):
    """Show warning message box with raw message (already translated or dynamic).

    Args:
        parent: Parent widget
        message: The message to display
        title: The title (will be translated if matching key exists)
    """
    QMessageBox.warning(parent, translate_widget_text(title), message)


def show_error_message_raw(parent, message, title='Error'):
    """Show error message box with raw message (already translated or dynamic).

    Args:
        parent: Parent widget
        message: The message to display
        title: The title (will be translated if matching key exists)
    """
    QMessageBox.critical(parent, translate_widget_text(title), message)


# =============================================================================
# COMMON MESSAGE TRANSLATIONS
# =============================================================================
# Dictionary of common messages used in the codebase

COMMON_MESSAGES = {
    # Record navigation
    'first_record_reached': 'msg_first_record',
    'last_record_reached': 'msg_last_record',
    'record_saved': 'msg_record_saved',
    'record_deleted': 'msg_record_deleted',
    'confirm_delete': 'msg_delete_confirm',
    'no_records': 'msg_no_records',
    'duplicate_record': 'msg_duplicate_record',
    'fill_required': 'msg_fill_required_fields',

    # Connection
    'connection_success': 'msg_connection_success',
    'connection_failed': 'msg_connection_failed',
    'database_error': 'msg_database_error',
    'restart_qgis': 'msg_restart_qgis',

    # Export
    'pdf_exported': 'msg_pdf_exported',
    'excel_exported': 'msg_excel_exported',
    'select_records': 'msg_select_records',
    'no_data_export': 'msg_no_data_export',

    # GIS
    'layer_not_found': 'msg_layer_not_found',
    'select_layer': 'msg_select_layer',
    'no_geometry': 'msg_no_geometry',
    'coordinates_updated': 'msg_coordinates_updated',

    # Media
    'image_not_found': 'msg_image_not_found',
    'no_images': 'msg_no_images',
    'select_images': 'msg_select_images',

    # Search
    'search_mode': 'msg_search_mode',
    'browse_mode': 'msg_browse_mode',
    'no_search_results': 'msg_no_search_results',

    # Validation
    'invalid_data': 'msg_invalid_data',
    'missing_field': 'msg_missing_field',
    'numeric_required': 'msg_numeric_required',
}


def standardize_toolbar(form):
    """Standardize the toolbar button layout and tooltips for a form.

    Sets consistent tooltips for toolbar buttons across all forms.
    Standard layout:
        Row 1: Navigation [<<] [<] [Record] [>] [>>]
        Row 2: Actions [New] [Save] [Delete] | [Search] [New Search] [Sort] [View All]
        Row 3: Export [PDF] [Excel] [List] | GIS [GIS View] [Layers] | Media [Photos] [Tags]

    Args:
        form: The form/dialog to standardize
    """
    # Define button configurations: (attribute_name, tooltip_key, tooltip_default)
    button_configs = [
        # Navigation buttons
        ('pushButton_first_rec', 'first_record', 'First record'),
        ('pushButton_prev_rec', 'prev_record', 'Previous record'),
        ('pushButton_next_rec', 'next_record', 'Next record'),
        ('pushButton_last_rec', 'last_record', 'Last record'),

        # Record action buttons
        ('pushButton_new_rec', 'new_record', 'New record'),
        ('pushButton_save', 'save_record', 'Save record'),
        ('pushButton_delete', 'delete_single_record', 'Delete record'),

        # Search buttons
        ('pushButton_search_go', 'start_query_search', 'Start search'),
        ('pushButton_new_search', 'new_search', 'New search'),
        ('pushButton_sort', 'sort', 'Sort records'),
        ('pushButton_view_all', 'view_alls_records', 'View all records'),

        # Export buttons
        ('pushButton_form', 'export_pdf_form', 'Export PDF'),
        ('pushButton_exppdf', 'export_pdf_form', 'Export PDF'),
        ('pushButton_print', 'export_pdf_form', 'Export PDF'),
        ('pushButton_list', 'export_list', 'Export list'),
        ('pushButton_explist', 'export_list', 'Export list'),
        ('pushButton_exptab', 'export_tab', 'Export table'),
        ('pushButton_word', 'pdf2word', 'Export to Word'),

        # GIS buttons
        ('pushButton_gisview', 'gis_view', 'GIS View'),
        ('pushButton_showLayer', 'view_layers', 'Show layers'),
        ('pushButton_uw_geometry', 'gis_tools', 'GIS tools'),
        ('pushButton_track', 'import_track', 'Import track'),

        # Media buttons
        ('pushButton_all_images', 'photos', 'View all images'),
        ('pushButton_assigntags', 'assign_tag_images', 'Assign tags to images'),
        ('pushButton_removetags', 'remove_all_tags_images', 'Remove tags from images'),

        # Other buttons
        ('pushButton_connect', 'connection_test', 'Test connection'),
        ('pushButton_filter_uw', 'filter_records', 'Filter records'),
        ('pushButton_report_generator', 'report_generator', 'Generate report'),
        ('pushButton_open_dir', 'open', 'Open directory'),
        ('pushButton_revert', 'revert', 'Revert changes'),
        ('pushButton_submit', 'save', 'Save'),
        ('pushButton_go_to_scheda', 'go_to_form', 'Go to record'),
        ('pushButton_convert', 'convert', 'Convert'),
        ('pushButtonQuant', 'statistics', 'Statistics'),
    ]

    # Apply tooltips
    for attr_name, tooltip_key, tooltip_default in button_configs:
        if hasattr(form, attr_name):
            btn = getattr(form, attr_name)
            if isinstance(btn, (QPushButton, QToolButton)):
                btn.setToolTip(tr(tooltip_key, tooltip_default))

    # Set consistent icon sizes (30x30)
    from qgis.PyQt.QtCore import QSize
    icon_size = QSize(30, 30)
    nav_buttons = ['pushButton_first_rec', 'pushButton_prev_rec',
                   'pushButton_next_rec', 'pushButton_last_rec',
                   'pushButton_new_rec', 'pushButton_save', 'pushButton_delete',
                   'pushButton_search_go', 'pushButton_new_search', 'pushButton_sort']
    for btn_name in nav_buttons:
        if hasattr(form, btn_name):
            btn = getattr(form, btn_name)
            if isinstance(btn, (QPushButton, QToolButton)):
                btn.setIconSize(icon_size)
