# -*- coding: utf-8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - Internationalization (i18n) Manager
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

from qgis.core import QgsSettings


class HffI18n:
    """Internationalization manager for HFF plugin.

    Provides translation support for UI elements and messages.
    Supports: English (en), Arabic Lebanese (ar-lb)
    """

    # Singleton instance
    _instance = None

    # Available languages
    LANGUAGES = {
        'en': 'English',
        'ar-lb': 'العربية اللبنانية'  # Arabic Lebanese
    }

    # RTL languages
    RTL_LANGUAGES = ['ar-lb']

    # Comprehensive Translations Dictionary
    TRANSLATIONS = {
        # =====================================================================
        # NAVIGATION & RECORD MANAGEMENT
        # =====================================================================
        'first': {'en': 'First', 'ar-lb': 'الأول'},
        'prev': {'en': 'Previous', 'ar-lb': 'السابق'},
        'next': {'en': 'Next', 'ar-lb': 'التالي'},
        'last': {'en': 'Last', 'ar-lb': 'الأخير'},
        'first_rec': {'en': 'First rec', 'ar-lb': 'السجل الأول'},
        'prev_rec': {'en': 'Prev rec', 'ar-lb': 'السجل السابق'},
        'next_rec': {'en': 'Next rec', 'ar-lb': 'السجل التالي'},
        'last_rec': {'en': 'Last rec', 'ar-lb': 'السجل الأخير'},
        'first_record': {'en': 'First Record', 'ar-lb': 'السجل الأول'},
        'prev_record': {'en': 'Previous Record', 'ar-lb': 'السجل السابق'},
        'next_record': {'en': 'Next Record', 'ar-lb': 'السجل التالي'},
        'last_record': {'en': 'Last Record', 'ar-lb': 'السجل الأخير'},
        'new_record': {'en': 'New record', 'ar-lb': 'سجل جديد'},
        'delete_record': {'en': 'Delete record', 'ar-lb': 'حذف السجل'},
        'record_n': {'en': 'record n.', 'ar-lb': 'سجل رقم'},
        'record_tot': {'en': 'record tot.', 'ar-lb': 'إجمالي السجلات'},
        'view_alls_records': {'en': 'View alls records', 'ar-lb': 'عرض جميع السجلات'},
        'go_to_form': {'en': 'Go to form', 'ar-lb': 'انتقل إلى النموذج'},

        # =====================================================================
        # ACTION BUTTONS
        # =====================================================================
        'save': {'en': 'Save', 'ar-lb': 'حفظ'},
        'cancel': {'en': 'Cancel', 'ar-lb': 'إلغاء'},
        'close': {'en': 'Close', 'ar-lb': 'إغلاق'},
        'add': {'en': 'Add', 'ar-lb': 'إضافة'},
        'new': {'en': 'New', 'ar-lb': 'جديد'},
        'edit': {'en': 'Edit', 'ar-lb': 'تعديل'},
        'delete': {'en': 'Delete', 'ar-lb': 'حذف'},
        'remove': {'en': 'Remove', 'ar-lb': 'إزالة'},
        'refresh': {'en': 'Refresh', 'ar-lb': 'تحديث'},
        'revert': {'en': 'Revert', 'ar-lb': 'التراجع'},
        'search': {'en': 'Search', 'ar-lb': 'بحث'},
        'search_!!!': {'en': 'search !!!', 'ar-lb': 'بحث !!!'},
        'new_search': {'en': 'new search', 'ar-lb': 'بحث جديد'},
        'find': {'en': 'Find', 'ar-lb': 'بحث'},
        'filter': {'en': 'Filter', 'ar-lb': 'تصفية'},
        'show_all': {'en': 'Show All', 'ar-lb': 'عرض الكل'},
        'view_all': {'en': 'View All', 'ar-lb': 'عرض الكل'},
        'sort': {'en': 'Sort', 'ar-lb': 'ترتيب'},
        'order': {'en': 'Order', 'ar-lb': 'ترتيب'},
        'order_by': {'en': 'Order by', 'ar-lb': 'ترتيب حسب'},
        'connect': {'en': 'Connect', 'ar-lb': 'اتصال'},
        'disconnect': {'en': 'Disconnect', 'ar-lb': 'قطع الاتصال'},
        'test': {'en': 'Test', 'ar-lb': 'اختبار'},
        'connection_test': {'en': 'Connection test', 'ar-lb': 'اختبار الاتصال'},
        'test_connection': {'en': 'Test Connection', 'ar-lb': 'اختبار الاتصال'},
        'browse': {'en': 'Browse...', 'ar-lb': 'تصفح...'},
        'open': {'en': 'Open', 'ar-lb': 'فتح'},
        'print': {'en': 'Print', 'ar-lb': 'طباعة'},
        'preview': {'en': 'Preview', 'ar-lb': 'معاينة'},
        'convert': {'en': 'Convert', 'ar-lb': 'تحويل'},
        'ok': {'en': 'OK', 'ar-lb': 'موافق'},
        'yes': {'en': 'Yes', 'ar-lb': 'نعم'},
        'no': {'en': 'No', 'ar-lb': 'لا'},
        'apply': {'en': 'Apply', 'ar-lb': 'تطبيق'},
        'reset': {'en': 'Reset', 'ar-lb': 'إعادة تعيين'},
        'clear': {'en': 'Clear', 'ar-lb': 'مسح'},
        'help': {'en': 'Help', 'ar-lb': 'مساعدة'},
        'insert_row': {'en': 'Insert row', 'ar-lb': 'إدراج صف'},
        'delete_row': {'en': 'Delete row', 'ar-lb': 'حذف صف'},
        'removed_row': {'en': 'Removed row', 'ar-lb': 'صف محذوف'},

        # =====================================================================
        # EXPORT & IMPORT
        # =====================================================================
        'export': {'en': 'Export', 'ar-lb': 'تصدير'},
        'import': {'en': 'Import', 'ar-lb': 'استيراد'},
        'export_pdf': {'en': 'Export PDF', 'ar-lb': 'تصدير PDF'},
        'pdf': {'en': 'PDF', 'ar-lb': 'PDF'},
        'export_excel': {'en': 'Export Excel', 'ar-lb': 'تصدير Excel'},
        'excel': {'en': 'Excel', 'ar-lb': 'Excel'},
        'export_csv': {'en': 'Export CSV', 'ar-lb': 'تصدير CSV'},
        'csv': {'en': 'CSV', 'ar-lb': 'CSV'},
        'export_tab': {'en': 'Export TAB', 'ar-lb': 'تصدير TAB'},
        'export_list': {'en': 'Export List', 'ar-lb': 'تصدير القائمة'},
        'pdf_path': {'en': 'PDF path', 'ar-lb': 'مسار PDF'},
        'pdf2word': {'en': 'Pdf2Word', 'ar-lb': 'PDF إلى Word'},
        'choose_pdf_convert': {'en': 'choose the pdf convert to word', 'ar-lb': 'اختر ملف PDF للتحويل'},
        'report': {'en': 'Report', 'ar-lb': 'تقرير'},
        'report_generator': {'en': 'Report generator', 'ar-lb': 'مولد التقارير'},

        # =====================================================================
        # TAB NAMES
        # =====================================================================
        'general': {'en': 'General', 'ar-lb': 'عام'},
        'details': {'en': 'Details', 'ar-lb': 'التفاصيل'},
        'data': {'en': 'Data', 'ar-lb': 'البيانات'},
        'settings': {'en': 'Settings', 'ar-lb': 'الإعدادات'},
        'options': {'en': 'Options', 'ar-lb': 'الخيارات'},
        'configuration': {'en': 'Configuration', 'ar-lb': 'التكوين'},
        'properties': {'en': 'Properties', 'ar-lb': 'الخصائص'},
        'information': {'en': 'Information', 'ar-lb': 'المعلومات'},
        'info': {'en': 'Info', 'ar-lb': 'معلومات'},
        'db_info': {'en': 'DB Info', 'ar-lb': 'معلومات قاعدة البيانات'},
        'media': {'en': 'Media', 'ar-lb': 'الوسائط'},
        'images': {'en': 'Images', 'ar-lb': 'الصور'},
        'photos': {'en': 'Photos', 'ar-lb': 'الصور'},
        'documents': {'en': 'Documents', 'ar-lb': 'المستندات'},
        'attachments': {'en': 'Attachments', 'ar-lb': 'المرفقات'},
        'notes': {'en': 'Notes', 'ar-lb': 'ملاحظات'},
        'bibliography': {'en': 'Bibliography', 'ar-lb': 'المراجع'},
        'references': {'en': 'References', 'ar-lb': 'المراجع'},
        'storage': {'en': 'Storage', 'ar-lb': 'التخزين'},
        'storage_location': {'en': 'Storage Location', 'ar-lb': 'موقع التخزين'},
        'store': {'en': 'Store', 'ar-lb': 'مخزن'},
        'gis': {'en': 'GIS', 'ar-lb': 'نظم المعلومات الجغرافية'},
        'gis_view': {'en': 'GIS View', 'ar-lb': 'عرض GIS'},
        'map': {'en': 'Map', 'ar-lb': 'الخريطة'},
        '3d': {'en': '3D', 'ar-lb': '3D'},
        '3d_view': {'en': '3D View', 'ar-lb': 'عرض ثلاثي الأبعاد'},
        'statistics': {'en': 'Statistics', 'ar-lb': 'الإحصائيات'},
        'statistic': {'en': 'Statistic', 'ar-lb': 'إحصاء'},
        'charts': {'en': 'Charts', 'ar-lb': 'الرسوم البيانية'},
        'reports': {'en': 'Reports', 'ar-lb': 'التقارير'},
        'tools': {'en': 'Tools', 'ar-lb': 'الأدوات'},
        'comparison': {'en': 'Comparison', 'ar-lb': 'المقارنة'},
        'history': {'en': 'History', 'ar-lb': 'التاريخ'},
        'measurements': {'en': 'Measurements', 'ar-lb': 'القياسات'},

        # =====================================================================
        # COMMON LABELS
        # =====================================================================
        'site': {'en': 'Site', 'ar-lb': 'الموقع'},
        'site_name': {'en': 'Site Name', 'ar-lb': 'اسم الموقع'},
        'name': {'en': 'Name', 'ar-lb': 'الاسم'},
        'code': {'en': 'Code', 'ar-lb': 'الرمز'},
        'code_id': {'en': 'Code ID', 'ar-lb': 'معرف الرمز'},
        'id': {'en': 'ID', 'ar-lb': 'المعرف'},
        'type': {'en': 'Type', 'ar-lb': 'النوع'},
        'category': {'en': 'Category', 'ar-lb': 'الفئة'},
        'status': {'en': 'Status', 'ar-lb': 'الحالة'},
        'state': {'en': 'State', 'ar-lb': 'الحالة'},
        'date': {'en': 'Date', 'ar-lb': 'التاريخ'},
        'year': {'en': 'Year', 'ar-lb': 'السنة'},
        'period': {'en': 'Period', 'ar-lb': 'الفترة'},
        'description': {'en': 'Description', 'ar-lb': 'الوصف'},
        'description_data': {'en': 'Description data', 'ar-lb': 'بيانات الوصف'},
        'condition': {'en': 'Condition', 'ar-lb': 'الحالة'},
        'material': {'en': 'Material', 'ar-lb': 'المادة'},
        'materials': {'en': 'Materials', 'ar-lb': 'المواد'},
        'dimensions': {'en': 'Dimensions', 'ar-lb': 'الأبعاد'},
        'length': {'en': 'Length', 'ar-lb': 'الطول'},
        'width': {'en': 'Width', 'ar-lb': 'العرض'},
        'height': {'en': 'Height', 'ar-lb': 'الارتفاع'},
        'depth': {'en': 'Depth', 'ar-lb': 'العمق'},
        'depth_found': {'en': 'Depth found', 'ar-lb': 'عمق الاكتشاف'},
        'thickness': {'en': 'Thickness', 'ar-lb': 'السمك'},
        'weight': {'en': 'Weight', 'ar-lb': 'الوزن'},
        'area': {'en': 'Area', 'ar-lb': 'المنطقة'},
        'volume': {'en': 'Volume', 'ar-lb': 'الحجم'},
        'quantity': {'en': 'Quantity', 'ar-lb': 'الكمية'},
        'qty': {'en': 'Qty', 'ar-lb': 'الكمية'},
        'count': {'en': 'Count', 'ar-lb': 'العدد'},
        'total': {'en': 'Total', 'ar-lb': 'المجموع'},
        'color': {'en': 'Color', 'ar-lb': 'اللون'},
        'origin': {'en': 'Origin', 'ar-lb': 'الأصل'},
        'provenance': {'en': 'Provenance', 'ar-lb': 'المصدر'},
        'dating': {'en': 'Dating', 'ar-lb': 'التأريخ'},
        'chronology': {'en': 'Chronology', 'ar-lb': 'التسلسل الزمني'},
        'location': {'en': 'Location', 'ar-lb': 'الموقع'},
        'place': {'en': 'Place', 'ar-lb': 'المكان'},
        'position': {'en': 'Position', 'ar-lb': 'الموضع'},
        'coordinates': {'en': 'Coordinates', 'ar-lb': 'الإحداثيات'},
        'drawings': {'en': 'Drawings', 'ar-lb': 'الرسومات'},
        'draw': {'en': 'Draw.', 'ar-lb': 'رسم'},
        'field': {'en': 'Field', 'ar-lb': 'حقل'},
        'fig': {'en': 'Fig.', 'ar-lb': 'شكل'},
        'pag': {'en': 'Pag.', 'ar-lb': 'صفحة'},
        'pagg': {'en': 'Pagg.', 'ar-lb': 'صفحات'},
        'text': {'en': 'Text', 'ar-lb': 'نص'},
        'title': {'en': 'Title', 'ar-lb': 'العنوان'},
        'author': {'en': 'Author', 'ar-lb': 'المؤلف'},
        'comments': {'en': 'Comments', 'ar-lb': 'التعليقات'},
        'supplements': {'en': 'Supplements', 'ar-lb': 'الملحقات'},
        'nr_box': {'en': 'Nr. Box', 'ar-lb': 'رقم الصندوق'},
        'pieces': {'en': 'Pieces', 'ar-lb': 'القطع'},
        'table_list': {'en': 'table list', 'ar-lb': 'قائمة الجدول'},
        'checkbox': {'en': 'CheckBox', 'ar-lb': 'خانة اختيار'},

        # =====================================================================
        # COORDINATES & GIS
        # =====================================================================
        'latitude': {'en': 'Latitude', 'ar-lb': 'خط العرض'},
        'longitude': {'en': 'Longitude', 'ar-lb': 'خط الطول'},
        'northing': {'en': 'Northing', 'ar-lb': 'الإحداثي الشمالي'},
        'easting': {'en': 'Easting', 'ar-lb': 'الإحداثي الشرقي'},
        'elevation': {'en': 'Elevation', 'ar-lb': 'الارتفاع'},
        'altitude': {'en': 'Altitude', 'ar-lb': 'الارتفاع'},
        'x_coord': {'en': 'X', 'ar-lb': 'س'},
        'y_coord': {'en': 'Y', 'ar-lb': 'ص'},
        'z_coord': {'en': 'Z', 'ar-lb': 'ع'},
        'layer': {'en': 'Layer', 'ar-lb': 'الطبقة'},
        'show_selected_features': {'en': 'Show Selcted Features', 'ar-lb': 'عرض المعالم المحددة'},
        'import_all_layers': {'en': 'Import all layers', 'ar-lb': 'استيراد جميع الطبقات'},
        'import_track': {'en': 'Import track', 'ar-lb': 'استيراد المسار'},

        # =====================================================================
        # DIVE LOG SPECIFIC
        # =====================================================================
        'dive': {'en': 'Dive', 'ar-lb': 'الغطسة'},
        'dive_log': {'en': 'Dive Log', 'ar-lb': 'سجل الغطس'},
        'dive_log_form': {'en': 'Dive Log Form', 'ar-lb': 'نموذج سجل الغطس'},
        'dive_id': {'en': 'DIVE ID', 'ar-lb': 'معرف الغطسة'},
        'dive_number': {'en': 'Dive Number', 'ar-lb': 'رقم الغطسة'},
        'diver': {'en': 'Diver', 'ar-lb': 'الغواص'},
        'diver_1': {'en': 'Diver 1', 'ar-lb': 'الغواص 1'},
        'diver_2': {'en': 'Diver 2', 'ar-lb': 'الغواص 2'},
        'additional_diver': {'en': 'Additional diver', 'ar-lb': 'غواص إضافي'},
        'dive_supervisor': {'en': 'Dive Supervisor', 'ar-lb': 'مشرف الغطس'},
        'standby_diver': {'en': 'Standby diver', 'ar-lb': 'غواص احتياطي'},
        'bottom_time': {'en': 'Bottom time', 'ar-lb': 'وقت القاع'},
        'max_depth': {'en': 'Max depth', 'ar-lb': 'أقصى عمق'},
        'depth_max': {'en': 'Depth max', 'ar-lb': 'أقصى عمق'},
        'visibility': {'en': 'Visibility', 'ar-lb': 'الرؤية'},
        'uw_visibility': {'en': 'UW Visibility', 'ar-lb': 'الرؤية تحت الماء'},
        'water_temp': {'en': 'Water Temperature', 'ar-lb': 'درجة حرارة الماء'},
        'uw_temperature': {'en': 'UW Temperature', 'ar-lb': 'درجة الحرارة تحت الماء'},
        'current': {'en': 'Current', 'ar-lb': 'التيار'},
        'uw_current': {'en': 'UW Current dir/str', 'ar-lb': 'اتجاه/قوة التيار'},
        'weather': {'en': 'Weather', 'ar-lb': 'الطقس'},
        'wind': {'en': 'Wind', 'ar-lb': 'الرياح'},
        'time_in': {'en': 'Time in', 'ar-lb': 'وقت الدخول'},
        'time_out': {'en': 'Time out', 'ar-lb': 'وقت الخروج'},
        'entry_time': {'en': 'Entry Time', 'ar-lb': 'وقت الدخول'},
        'exit_time': {'en': 'Exit Time', 'ar-lb': 'وقت الخروج'},
        'bar_start_diver_1': {'en': 'Bar start Diver 1', 'ar-lb': 'ضغط البداية غواص 1'},
        'bar_end_diver_1': {'en': 'Bar end Diver 1', 'ar-lb': 'ضغط النهاية غواص 1'},
        'bar_start_diver_2': {'en': 'Bar start Diver 2', 'ar-lb': 'ضغط البداية غواص 2'},
        'bar_end_diver_2': {'en': 'Bar end Diver 2', 'ar-lb': 'ضغط النهاية غواص 2'},
        'delta_p_diver_1': {'en': 'Δ P Diver 1', 'ar-lb': 'فرق الضغط غواص 1'},
        'delta_p_diver_2': {'en': 'Δ P Diver 2', 'ar-lb': 'فرق الضغط غواص 2'},
        'surface_interval': {'en': 'Surface interval', 'ar-lb': 'فترة السطح'},
        'breathing_mix': {'en': 'Breathing mix', 'ar-lb': 'خليط التنفس'},
        'task': {'en': 'Task', 'ar-lb': 'المهمة'},
        'camera': {'en': 'Camera', 'ar-lb': 'الكاميرا'},
        'photo_environment': {'en': 'Photo Environment', 'ar-lb': 'بيئة التصوير'},
        'sketch': {'en': 'Sketch', 'ar-lb': 'رسم تخطيطي'},
        'low': {'en': 'Low', 'ar-lb': 'ضعيف'},
        'medium': {'en': 'Medium', 'ar-lb': 'متوسط'},
        'strong': {'en': 'Strong', 'ar-lb': 'قوي'},
        'result': {'en': 'Result', 'ar-lb': 'النتيجة'},

        # =====================================================================
        # ANCHOR SPECIFIC
        # =====================================================================
        'anchor': {'en': 'Anchor', 'ar-lb': 'المرساة'},
        'anchors': {'en': 'Anchors', 'ar-lb': 'المراسي'},
        'anchor_form': {'en': 'Anchor form', 'ar-lb': 'نموذج المرساة'},
        'anchor_list': {'en': 'Anchor list', 'ar-lb': 'قائمة المراسي'},
        'anchor_export_pdf': {'en': 'Anchor export pdf', 'ar-lb': 'تصدير المرساة PDF'},
        'anchor_type': {'en': 'Anchor Type', 'ar-lb': 'نوع المرساة'},
        'anchor_shape': {'en': 'Anchor shape', 'ar-lb': 'شكل المرساة'},
        'anchor_material': {'en': 'Anchor Material', 'ar-lb': 'مادة المرساة'},
        'stock': {'en': 'Stock', 'ar-lb': 'العارضة'},
        'shank': {'en': 'Shank', 'ar-lb': 'الساق'},
        'arms': {'en': 'Arms', 'ar-lb': 'الأذرع'},
        'arm': {'en': 'Arm', 'ar-lb': 'الذراع'},
        'flukes': {'en': 'Flukes', 'ar-lb': 'الشفرات'},
        'fluke': {'en': 'Fluke', 'ar-lb': 'الشفرة'},
        'hole_properties': {'en': 'Hole Properties', 'ar-lb': 'خصائص الثقب'},
        'type_of_hole': {'en': 'Type of hole', 'ar-lb': 'نوع الثقب'},
        'no_hole': {'en': 'No hole', 'ar-lb': 'بدون ثقب'},
        '1_hole': {'en': '1 hole', 'ar-lb': 'ثقب واحد'},
        '2_hole': {'en': '2 hole', 'ar-lb': 'ثقبين'},
        '3_hole': {'en': '3 hole', 'ar-lb': 'ثلاثة ثقوب'},
        'diameter': {'en': 'Diameter', 'ar-lb': 'القطر'},
        'typology': {'en': 'Typology', 'ar-lb': 'التصنيف'},
        'stone_type': {'en': 'Stone Type', 'ar-lb': 'نوع الحجر'},
        'petrography': {'en': 'Petrography', 'ar-lb': 'البتروغرافيا'},
        'petrography_results': {'en': 'Petrography results', 'ar-lb': 'نتائج البتروغرافيا'},
        'limestone': {'en': 'Limestone', 'ar-lb': 'الحجر الجيري'},
        'sandstone': {'en': 'Sandstone', 'ar-lb': 'الحجر الرملي'},
        'basalt': {'en': 'Basalt', 'ar-lb': 'البازلت'},
        'rectangular': {'en': 'Rectangular', 'ar-lb': 'مستطيل'},
        'triangular': {'en': 'Triangular', 'ar-lb': 'مثلث'},
        'trapezoidal': {'en': 'Trapezoidal', 'ar-lb': 'شبه منحرف'},
        'oval': {'en': 'Oval', 'ar-lb': 'بيضاوي'},
        'tubular': {'en': 'Tubular', 'ar-lb': 'أنبوبي'},
        'biconical': {'en': 'Biconical', 'ar-lb': 'مخروطي مزدوج'},
        'basket': {'en': 'Basket', 'ar-lb': 'سلة'},
        'inscription': {'en': 'Inscription', 'ar-lb': 'النقش'},
        'description_inscription': {'en': 'Description of the inscription', 'ar-lb': 'وصف النقش'},
        'tool_markings': {'en': 'Tool markings', 'ar-lb': 'علامات الأدوات'},
        'from_bottom': {'en': 'From Bottom', 'ar-lb': 'من الأسفل'},
        'from_top': {'en': 'From Top', 'ar-lb': 'من الأعلى'},
        'from_left': {'en': 'From Left', 'ar-lb': 'من اليسار'},
        'from_right': {'en': 'From Right', 'ar-lb': 'من اليمين'},
        'top': {'en': 'Top', 'ar-lb': 'أعلى'},
        'bottom': {'en': 'Bottom', 'ar-lb': 'أسفل'},
        'left': {'en': 'Left', 'ar-lb': 'يسار'},
        'right': {'en': 'Right', 'ar-lb': 'يمين'},

        # =====================================================================
        # ARTEFACT SPECIFIC
        # =====================================================================
        'artefact': {'en': 'Artefact', 'ar-lb': 'القطعة الأثرية'},
        'artefact_form': {'en': 'Artefact form', 'ar-lb': 'نموذج القطعة الأثرية'},
        'artefact_list': {'en': 'Artefact list', 'ar-lb': 'قائمة القطع الأثرية'},
        'artefact_id': {'en': 'Artefact ID', 'ar-lb': 'معرف القطعة'},
        'general_finds': {'en': 'General Finds', 'ar-lb': 'اللقى العامة'},
        'object': {'en': 'Object', 'ar-lb': 'الكائن'},
        'shape': {'en': 'Shape', 'ar-lb': 'الشكل'},
        'fragment': {'en': 'Fragment', 'ar-lb': 'الشظية'},
        'complete': {'en': 'Complete', 'ar-lb': 'كامل'},
        'completeness': {'en': 'Completeness', 'ar-lb': 'الاكتمال'},
        'conservation': {'en': 'Conservation', 'ar-lb': 'الترميم'},
        'conservation_completed': {'en': 'Conservation completed', 'ar-lb': 'اكتمل الترميم'},
        'treatment': {'en': 'Treatment', 'ar-lb': 'المعالجة'},
        'recovered': {'en': 'Recovered', 'ar-lb': 'مستعاد'},
        'retrieved': {'en': 'Retrieved', 'ar-lb': 'مسترجع'},
        'photographed': {'en': 'Photographed', 'ar-lb': 'تم تصويره'},
        'photogr': {'en': 'Photogr.', 'ar-lb': 'صور'},
        'washed': {'en': 'Washed', 'ar-lb': 'مغسول'},
        'samples': {'en': 'Samples', 'ar-lb': 'العينات'},
        'min': {'en': 'Min', 'ar-lb': 'الحد الأدنى'},
        'max': {'en': 'Max', 'ar-lb': 'الحد الأقصى'},

        # =====================================================================
        # POTTERY SPECIFIC
        # =====================================================================
        'pottery': {'en': 'Pottery', 'ar-lb': 'الفخار'},
        'pottery_form': {'en': 'Pottery form', 'ar-lb': 'نموذج الفخار'},
        'pottery_list': {'en': 'Pottery list', 'ar-lb': 'قائمة الفخار'},
        'pottery_export_pdf': {'en': 'Pottery export pdf', 'ar-lb': 'تصدير الفخار PDF'},
        'ceramic': {'en': 'Ceramic', 'ar-lb': 'السيراميك'},
        'ceramics': {'en': 'Ceramics', 'ar-lb': 'السيراميك'},
        'fabric': {'en': 'Fabric', 'ar-lb': 'النسيج'},
        'form': {'en': 'Form', 'ar-lb': 'الشكل'},
        'function': {'en': 'Function', 'ar-lb': 'الوظيفة'},
        'rim': {'en': 'Rim', 'ar-lb': 'الحافة'},
        'rim_type': {'en': 'Rim Type', 'ar-lb': 'نوع الحافة'},
        'base': {'en': 'Base', 'ar-lb': 'القاعدة'},
        'base_type': {'en': 'Base Type', 'ar-lb': 'نوع القاعدة'},
        'base_height': {'en': 'Base Height', 'ar-lb': 'ارتفاع القاعدة'},
        'body': {'en': 'Body', 'ar-lb': 'الجسم'},
        'upper_body': {'en': 'Upper body', 'ar-lb': 'الجسم العلوي'},
        'wall': {'en': 'Wall', 'ar-lb': 'الجدار'},
        'neck': {'en': 'Neck', 'ar-lb': 'الرقبة'},
        'handle': {'en': 'Handle', 'ar-lb': 'المقبض'},
        'handle_type': {'en': 'Handle Type', 'ar-lb': 'نوع المقبض'},
        'spout': {'en': 'Spout', 'ar-lb': 'الصنبور'},
        'lid': {'en': 'Lid', 'ar-lb': 'الغطاء'},
        'surface': {'en': 'Surface', 'ar-lb': 'السطح'},
        'surface_treatment': {'en': 'Surface treatment', 'ar-lb': 'معالجة السطح'},
        'decoration': {'en': 'Decoration', 'ar-lb': 'الزخرفة'},
        'technique': {'en': 'Technique', 'ar-lb': 'التقنية'},
        'inclusions': {'en': 'Inclusions', 'ar-lb': 'الشوائب'},
        'percentage_inclusions': {'en': 'Percentage of the inclusions', 'ar-lb': 'نسبة الشوائب'},
        'munsell_colour_clay': {'en': 'Munsell colour clay', 'ar-lb': 'لون الطين (مونسيل)'},
        'munsell_colour_surf': {'en': 'Munsell colour surf', 'ar-lb': 'لون السطح (مونسيل)'},
        'diameter_rim': {'en': 'Diameter Rim', 'ar-lb': 'قطر الحافة'},
        'diameter_max': {'en': 'Diameter Max', 'ar-lb': 'القطر الأقصى'},
        'diameter_bottom': {'en': 'Diameter Bottom', 'ar-lb': 'قطر القاعدة'},
        'total_height': {'en': 'Total Height', 'ar-lb': 'الارتفاع الكلي'},
        'preserved_height': {'en': 'Preserved Height', 'ar-lb': 'الارتفاع المحفوظ'},
        'specific_part': {'en': 'Specific part', 'ar-lb': 'الجزء المحدد'},
        # Pottery types
        'amphora': {'en': 'Amphora', 'ar-lb': 'أمفورا'},
        'jar': {'en': 'Jar', 'ar-lb': 'جرة'},
        'jug': {'en': 'Jug', 'ar-lb': 'إبريق'},
        'juglet': {'en': 'Juglet', 'ar-lb': 'إبريق صغير'},
        'bowl': {'en': 'Bowl', 'ar-lb': 'وعاء'},
        'plate': {'en': 'Plate', 'ar-lb': 'طبق'},
        'basin': {'en': 'Basin', 'ar-lb': 'حوض'},
        'bottle': {'en': 'Bottle', 'ar-lb': 'زجاجة'},
        'cooking_pot': {'en': 'Cooking pot', 'ar-lb': 'قدر الطبخ'},
        'cooking_ware': {'en': 'Cooking ware', 'ar-lb': 'أواني الطبخ'},
        'fine_ware': {'en': 'Fine ware', 'ar-lb': 'أواني فاخرة'},
        'coarse_ware': {'en': 'Coarse ware', 'ar-lb': 'أواني خشنة'},
        'storage_ware': {'en': 'Storage ware', 'ar-lb': 'أواني التخزين'},
        'transport_containers': {'en': 'Transport containers', 'ar-lb': 'حاويات النقل'},
        'slipped_red': {'en': 'Slipped red', 'ar-lb': 'مطلي أحمر'},
        'polished': {'en': 'Polished', 'ar-lb': 'مصقول'},
        'wheel_made': {'en': 'Wheel made', 'ar-lb': 'صنع بالعجلة'},
        'buff': {'en': 'Buff', 'ar-lb': 'بيج'},

        # =====================================================================
        # SHIPWRECK SPECIFIC
        # =====================================================================
        'shipwreck': {'en': 'Shipwreck', 'ar-lb': 'حطام السفينة'},
        'shipwreck_form': {'en': 'Shipwreck form', 'ar-lb': 'نموذج الحطام'},
        'shipwreck_list': {'en': 'Shipwreck list', 'ar-lb': 'قائمة الحطام'},
        'shipwreck_export_pdf': {'en': 'Shipwreck export pdf', 'ar-lb': 'تصدير الحطام PDF'},
        'wreck': {'en': 'Wreck', 'ar-lb': 'الحطام'},
        'vessel': {'en': 'Vessel', 'ar-lb': 'السفينة'},
        'vessel_type': {'en': 'Vessel Type', 'ar-lb': 'نوع السفينة'},
        'name_vessel': {'en': 'Name Vessel', 'ar-lb': 'اسم السفينة'},
        'nickname': {'en': 'Nickname', 'ar-lb': 'اللقب'},
        'hull': {'en': 'Hull', 'ar-lb': 'الهيكل'},
        'hull_type': {'en': 'Hull Type', 'ar-lb': 'نوع الهيكل'},
        'cargo': {'en': 'Cargo', 'ar-lb': 'الحمولة'},
        'nationality': {'en': 'Nationality', 'ar-lb': 'الجنسية'},
        'flag': {'en': 'Flag', 'ar-lb': 'العلم'},
        'construction': {'en': 'Construction', 'ar-lb': 'البناء'},
        'wood_type': {'en': 'Wood Type', 'ar-lb': 'نوع الخشب'},
        'estimated_date': {'en': 'Estimated Date', 'ar-lb': 'التاريخ المقدر'},
        'date_built': {'en': 'Date Built', 'ar-lb': 'تاريخ البناء'},
        'date_lost': {'en': 'Date Lost', 'ar-lb': 'تاريخ الغرق'},
        'builder': {'en': 'Builder', 'ar-lb': 'الباني'},
        'owner': {'en': 'Owner', 'ar-lb': 'المالك'},
        'yard_no_imo': {'en': 'Yard no./IMO', 'ar-lb': 'رقم الحوض/IMO'},
        'tonnage': {'en': 'Tonnage', 'ar-lb': 'الحمولة الطنية'},
        'draught': {'en': 'Draught', 'ar-lb': 'الغاطس'},
        'propulsion': {'en': 'Propulsion', 'ar-lb': 'الدفع'},
        'purpose': {'en': 'Purpose', 'ar-lb': 'الغرض'},
        'confidence': {'en': 'Confidence', 'ar-lb': 'الثقة'},
        'certain': {'en': 'Certain', 'ar-lb': 'مؤكد'},
        'likely': {'en': 'Likely', 'ar-lb': 'محتمل'},
        'suspect': {'en': 'Suspect', 'ar-lb': 'مشتبه'},
        'inconsistent': {'en': 'Inconsistent', 'ar-lb': 'غير متسق'},
        'unreliable': {'en': 'Unreliable', 'ar-lb': 'غير موثوق'},
        'unknow': {'en': 'Unknow', 'ar-lb': 'غير معروف'},
        # Position
        'position_wreck': {'en': 'Position of Wreck', 'ar-lb': 'موقع الحطام'},
        'position_quality': {'en': 'Position quality', 'ar-lb': 'جودة الموقع'},
        'depth_quality': {'en': 'Depth quality', 'ar-lb': 'جودة العمق'},
        'lying_on_deck': {'en': 'Lying on deck', 'ar-lb': 'مستلقٍ على السطح'},
        'lying_on_side_port': {'en': 'Lying on side (port)', 'ar-lb': 'مستلقٍ على الجانب (يسار)'},
        'lying_on_side_starboard': {'en': 'Lying on side (starboard)', 'ar-lb': 'مستلقٍ على الجانب (يمين)'},
        'lying_on_underside': {'en': 'Lying on underside', 'ar-lb': 'مستلقٍ على البطن'},
        'vertical_bow_up': {'en': 'Vertical (bow up)', 'ar-lb': 'عمودي (المقدمة للأعلى)'},
        'vertical_stern_up': {'en': 'Vertical (stern up)', 'ar-lb': 'عمودي (المؤخرة للأعلى)'},
        'capsized': {'en': 'Capsized', 'ar-lb': 'منقلب'},
        'flat': {'en': 'Flat', 'ar-lb': 'مسطح'},
        'sloping': {'en': 'Sloping', 'ar-lb': 'منحدر'},
        # Causes
        'cause_of_lose': {'en': 'Cause of lose', 'ar-lb': 'سبب الغرق'},
        'collision': {'en': 'Collision', 'ar-lb': 'تصادم'},
        'foundered': {'en': 'Foundered', 'ar-lb': 'غرق'},
        'ran_aground': {'en': 'Ran aground', 'ar-lb': 'جنوح'},
        'fire': {'en': 'Fire', 'ar-lb': 'حريق'},
        'explosion': {'en': 'Explosion', 'ar-lb': 'انفجار'},
        'combat': {'en': 'Combat', 'ar-lb': 'قتال'},
        'conflict': {'en': 'Conflict', 'ar-lb': 'صراع'},
        'rammed': {'en': 'Rammed', 'ar-lb': 'صدم'},
        'scuttled': {'en': 'Scuttled', 'ar-lb': 'أغرق عمداً'},
        'water_leakage': {'en': 'Water Leakage', 'ar-lb': 'تسرب مياه'},
        'foul': {'en': 'Foul', 'ar-lb': 'خطأ'},
        'crash': {'en': 'Crash', 'ar-lb': 'تحطم'},
        # Sea bed
        'sea_bed_composition': {'en': 'Sea bed composition', 'ar-lb': 'تكوين قاع البحر'},
        'sea_bed_inclination': {'en': 'Sea bed inclination', 'ar-lb': 'ميل قاع البحر'},
        # Vessel types
        'battleship': {'en': 'Battleship', 'ar-lb': 'سفينة حربية'},
        'submarine': {'en': 'Submarine', 'ar-lb': 'غواصة'},
        'tanker': {'en': 'Tanker', 'ar-lb': 'ناقلة'},
        'passenger_ship': {'en': 'Passenger ship', 'ar-lb': 'سفينة ركاب'},
        'container_ship': {'en': 'Cointainer ship', 'ar-lb': 'سفينة حاويات'},
        'ocean_linear': {'en': 'Ocean linear', 'ar-lb': 'عابرة محيطات'},
        'patrol_boat': {'en': 'Patrol Boat', 'ar-lb': 'قارب دورية'},
        'leisure': {'en': 'Leisure', 'ar-lb': 'ترفيهية'},
        'transportation': {'en': 'Transportation', 'ar-lb': 'نقل'},
        # Materials
        'wood': {'en': 'Wood', 'ar-lb': 'خشب'},
        'steel': {'en': 'Steel', 'ar-lb': 'فولاذ'},
        'fiberglass': {'en': 'Fiberglass', 'ar-lb': 'ألياف زجاجية'},
        # Propulsion
        'sail': {'en': 'Sail', 'ar-lb': 'شراع'},
        'steam': {'en': 'Steam', 'ar-lb': 'بخار'},
        'diesel': {'en': 'Diesel', 'ar-lb': 'ديزل'},
        'mv': {'en': 'MV', 'ar-lb': 'سفينة آلية'},
        # Accessibility
        'accessibility_divers': {'en': 'Accessibility to divers', 'ar-lb': 'إمكانية وصول الغواصين'},
        'accessible': {'en': 'Accessible', 'ar-lb': 'يمكن الوصول'},
        'not_accessible': {'en': 'Not accessible', 'ar-lb': 'لا يمكن الوصول'},
        'obstruction': {'en': 'Obstruction', 'ar-lb': 'عائق'},
        'protected': {'en': 'Protected', 'ar-lb': 'محمي'},
        'consulties': {'en': 'Consulties', 'ar-lb': 'مستشارون'},

        # =====================================================================
        # MEDIA & PHOTOS
        # =====================================================================
        'thumbnail': {'en': 'Thumbnail', 'ar-lb': 'الصورة المصغرة'},
        'image': {'en': 'Image', 'ar-lb': 'صورة'},
        'photo': {'en': 'Photo', 'ar-lb': 'صورة'},
        'photo_id': {'en': 'Photo id', 'ar-lb': 'معرف الصورة'},
        'n_photo': {'en': 'N Photo', 'ar-lb': 'عدد الصور'},
        'video': {'en': 'Video', 'ar-lb': 'فيديو'},
        'video_id': {'en': 'Video id', 'ar-lb': 'معرف الفيديو'},
        'n_video': {'en': 'N Video', 'ar-lb': 'عدد الفيديو'},
        'audio': {'en': 'Audio', 'ar-lb': 'صوت'},
        'file': {'en': 'File', 'ar-lb': 'ملف'},
        'path': {'en': 'Path', 'ar-lb': 'المسار'},
        'url': {'en': 'URL', 'ar-lb': 'الرابط'},
        'tags': {'en': 'Tags', 'ar-lb': 'الوسوم'},
        'photo_list_with_thumbnail': {'en': 'Photo list with Thumbnail', 'ar-lb': 'قائمة الصور مع المصغرات'},
        'photo_list_without_thumbnail': {'en': 'Photo list without Thumbnail', 'ar-lb': 'قائمة الصور بدون مصغرات'},
        'export_photo_list_thumbnails': {'en': 'Export Photo List (with thumbnails)', 'ar-lb': 'تصدير قائمة الصور (مع المصغرات)'},
        'export_photo_list_no_thumbnails': {'en': 'Export Photo List (no thumbnails)', 'ar-lb': 'تصدير قائمة الصور (بدون مصغرات)'},

        # =====================================================================
        # STATUS & MESSAGES
        # =====================================================================
        'loading': {'en': 'Loading...', 'ar-lb': 'جاري التحميل...'},
        'saving': {'en': 'Saving...', 'ar-lb': 'جاري الحفظ...'},
        'searching': {'en': 'Searching...', 'ar-lb': 'جاري البحث...'},
        'processing': {'en': 'Processing...', 'ar-lb': 'جاري المعالجة...'},
        'success': {'en': 'Success', 'ar-lb': 'نجاح'},
        'error': {'en': 'Error', 'ar-lb': 'خطأ'},
        'warning': {'en': 'Warning', 'ar-lb': 'تحذير'},
        'failed': {'en': 'Failed', 'ar-lb': 'فشل'},
        'record': {'en': 'Record', 'ar-lb': 'سجل'},
        'records': {'en': 'Records', 'ar-lb': 'السجلات'},
        'of': {'en': 'of', 'ar-lb': 'من'},
        'to': {'en': 'to', 'ar-lb': 'إلى'},
        'selected': {'en': 'Selected', 'ar-lb': 'المحدد'},
        'no_records': {'en': 'No records', 'ar-lb': 'لا توجد سجلات'},
        'no_records_found': {'en': 'No records found', 'ar-lb': 'لم يتم العثور على سجلات'},
        'no_data': {'en': 'No data available', 'ar-lb': 'لا توجد بيانات'},
        'confirm': {'en': 'Confirm', 'ar-lb': 'تأكيد'},
        'connection_successful': {'en': 'Connection successful!', 'ar-lb': 'تم الاتصال بنجاح!'},
        'connection_failed': {'en': 'Connection failed', 'ar-lb': 'فشل الاتصال'},
        'saved_successfully': {'en': 'Saved successfully', 'ar-lb': 'تم الحفظ بنجاح'},
        'deleted_successfully': {'en': 'Deleted successfully', 'ar-lb': 'تم الحذف بنجاح'},
        'please_select': {'en': 'Please select an item', 'ar-lb': 'يرجى اختيار عنصر'},
        'confirm_delete': {'en': 'Are you sure you want to delete?', 'ar-lb': 'هل أنت متأكد من الحذف؟'},
        'dbms_toolbar': {'en': 'DBMS Toolbar', 'ar-lb': 'شريط أدوات قاعدة البيانات'},
        'insert_name_field': {'en': 'insert the name field', 'ar-lb': 'أدخل اسم الحقل'},
        'rollback_changed': {'en': 'rollback the changed', 'ar-lb': 'التراجع عن التغييرات'},
        'save_record_changed': {'en': 'save record after chanched', 'ar-lb': 'حفظ السجل بعد التغيير'},
        'write_word_search': {'en': 'write the word to search', 'ar-lb': 'اكتب الكلمة للبحث'},
        'select_row_go_record': {'en': 'Select the row and directly go to record into the form', 'ar-lb': 'حدد الصف وانتقل مباشرة إلى السجل'},

        # =====================================================================
        # USER MANAGEMENT
        # =====================================================================
        'user': {'en': 'User', 'ar-lb': 'المستخدم'},
        'user_management': {'en': 'User Management', 'ar-lb': 'إدارة المستخدمين'},
        'users': {'en': 'Users', 'ar-lb': 'المستخدمين'},
        'permissions': {'en': 'Permissions', 'ar-lb': 'الصلاحيات'},
        'access_log': {'en': 'Access Log', 'ar-lb': 'سجل الوصول'},
        'add_user': {'en': 'Add User', 'ar-lb': 'إضافة مستخدم'},
        'edit_user': {'en': 'Edit User', 'ar-lb': 'تعديل مستخدم'},
        'deactivate': {'en': 'Deactivate', 'ar-lb': 'تعطيل'},
        'username': {'en': 'Username', 'ar-lb': 'اسم المستخدم'},
        'password': {'en': 'Password', 'ar-lb': 'كلمة المرور'},
        'full_name': {'en': 'Full Name', 'ar-lb': 'الاسم الكامل'},
        'email': {'en': 'Email', 'ar-lb': 'البريد الإلكتروني'},
        'role': {'en': 'Role', 'ar-lb': 'الدور'},
        'active': {'en': 'Active', 'ar-lb': 'نشط'},
        'created': {'en': 'Created', 'ar-lb': 'تاريخ الإنشاء'},
        'last_login': {'en': 'Last Login', 'ar-lb': 'آخر دخول'},
        'select_user': {'en': 'Select User:', 'ar-lb': 'اختر المستخدم:'},
        'save_permissions': {'en': 'Save Permissions', 'ar-lb': 'حفظ الصلاحيات'},
        'filter_by_user': {'en': 'Filter by User:', 'ar-lb': 'تصفية حسب المستخدم:'},
        'all_users': {'en': 'All Users', 'ar-lb': 'جميع المستخدمين'},
        'limit': {'en': 'Limit:', 'ar-lb': 'الحد:'},
        'role_admin': {'en': 'Administrator', 'ar-lb': 'مدير'},
        'role_archaeologist': {'en': 'Archaeologist', 'ar-lb': 'عالم آثار'},
        'role_student': {'en': 'Student', 'ar-lb': 'طالب'},
        'role_guest': {'en': 'Guest', 'ar-lb': 'ضيف'},

        # =====================================================================
        # CONNECTION SETTINGS
        # =====================================================================
        'connection_settings': {'en': 'Connection Settings', 'ar-lb': 'إعدادات الاتصال'},
        'saved_connections': {'en': 'Saved Connections', 'ar-lb': 'الاتصالات المحفوظة'},
        'connection_name': {'en': 'Connection Name:', 'ar-lb': 'اسم الاتصال:'},
        'server_type': {'en': 'Server Type:', 'ar-lb': 'نوع الخادم:'},
        'host': {'en': 'Host:', 'ar-lb': 'المضيف:'},
        'port': {'en': 'Port:', 'ar-lb': 'المنفذ:'},
        'database': {'en': 'Database:', 'ar-lb': 'قاعدة البيانات:'},
        'server': {'en': 'Server', 'ar-lb': 'الخادم'},
        'connection': {'en': 'Connection', 'ar-lb': 'الاتصال'},
        'save_password': {'en': 'Save password', 'ar-lb': 'حفظ كلمة المرور'},
        'set_as_default': {'en': 'Set as Default', 'ar-lb': 'تعيين كافتراضي'},
        'postgresql_settings': {'en': 'PostgreSQL Settings', 'ar-lb': 'إعدادات PostgreSQL'},
        'sqlite_settings': {'en': 'SQLite Settings', 'ar-lb': 'إعدادات SQLite'},
        'database_file': {'en': 'Database File:', 'ar-lb': 'ملف قاعدة البيانات:'},
        'new_connection': {'en': 'New Connection', 'ar-lb': 'اتصال جديد'},
        'edit_connection': {'en': 'Edit Connection', 'ar-lb': 'تعديل الاتصال'},

        # =====================================================================
        # REMOTE STORAGE
        # =====================================================================
        'remote_storage': {'en': 'Remote Storage Settings', 'ar-lb': 'إعدادات التخزين البعيد'},
        'enable_remote_storage': {'en': 'Enable Remote Storage', 'ar-lb': 'تفعيل التخزين البعيد'},
        'storage_type': {'en': 'Storage Type:', 'ar-lb': 'نوع التخزين:'},
        'cloud_name': {'en': 'Cloud Name:', 'ar-lb': 'اسم السحابة:'},
        'api_key': {'en': 'API Key:', 'ar-lb': 'مفتاح API:'},
        'api_secret': {'en': 'API Secret:', 'ar-lb': 'سر API:'},
        'folder': {'en': 'Folder:', 'ar-lb': 'المجلد:'},
        'bucket_name': {'en': 'Bucket Name:', 'ar-lb': 'اسم الحاوية:'},
        'region': {'en': 'Region:', 'ar-lb': 'المنطقة:'},
        'access_key_id': {'en': 'Access Key ID:', 'ar-lb': 'معرف مفتاح الوصول:'},
        'secret_access_key': {'en': 'Secret Access Key:', 'ar-lb': 'مفتاح الوصول السري:'},
        'key_prefix': {'en': 'Key Prefix:', 'ar-lb': 'بادئة المفتاح:'},
        'server_url': {'en': 'Server URL:', 'ar-lb': 'عنوان الخادم:'},
        'base_url': {'en': 'Base URL:', 'ar-lb': 'العنوان الأساسي:'},
        'upload_endpoint': {'en': 'Upload Endpoint:', 'ar-lb': 'نقطة الرفع:'},
        'download_endpoint': {'en': 'Download Endpoint:', 'ar-lb': 'نقطة التنزيل:'},
        'credentials_file': {'en': 'Credentials File:', 'ar-lb': 'ملف الاعتمادات:'},
        'folder_id': {'en': 'Folder ID:', 'ar-lb': 'معرف المجلد:'},
        'access_token': {'en': 'Access Token:', 'ar-lb': 'رمز الوصول:'},

        # =====================================================================
        # TUTORIALS
        # =====================================================================
        'tutorials': {'en': 'Tutorials & Documentation', 'ar-lb': 'الدروس والوثائق'},
        'language': {'en': 'Language:', 'ar-lb': 'اللغة:'},
        'search_tutorials': {'en': 'Search tutorials...', 'ar-lb': 'البحث في الدروس...'},
        'no_tutorials': {'en': 'No tutorials found', 'ar-lb': 'لم يتم العثور على دروس'},

        # =====================================================================
        # TABLE HEADERS
        # =====================================================================
        'table': {'en': 'Table', 'ar-lb': 'الجدول'},
        'view': {'en': 'View', 'ar-lb': 'عرض'},
        'insert': {'en': 'Insert', 'ar-lb': 'إدراج'},
        'update': {'en': 'Update', 'ar-lb': 'تحديث'},
        'action': {'en': 'Action', 'ar-lb': 'الإجراء'},
        'timestamp': {'en': 'Timestamp', 'ar-lb': 'الوقت'},
        'record_id': {'en': 'Record ID', 'ar-lb': 'معرف السجل'},

        # =====================================================================
        # THEME
        # =====================================================================
        'theme': {'en': 'Theme', 'ar-lb': 'المظهر'},
        'dark_mode': {'en': 'Dark Mode', 'ar-lb': 'الوضع الداكن'},
        'light_mode': {'en': 'Light Mode', 'ar-lb': 'الوضع الفاتح'},
        'toggle_theme': {'en': 'Toggle Dark/Light Mode', 'ar-lb': 'تبديل الوضع الداكن/الفاتح'},

        # =====================================================================
        # DOCUMENT EXPORTS
        # =====================================================================
        'generated_by': {'en': 'Generated by HFF', 'ar-lb': 'تم إنشاؤه بواسطة HFF'},
        'page': {'en': 'Page', 'ar-lb': 'صفحة'},
        'report_date': {'en': 'Report Date', 'ar-lb': 'تاريخ التقرير'},
        'printed_on': {'en': 'Printed on', 'ar-lb': 'طُبع في'},

        # =====================================================================
        # FORM TITLES
        # =====================================================================
        'hff_divelog': {'en': 'HFF Divelog Underwater Survey', 'ar-lb': 'HFF سجل الغطس - المسح تحت الماء'},
        'hff_anchor': {'en': 'HFF Underwater Anchor', 'ar-lb': 'HFF المراسي تحت الماء'},
        'hff_artefacts': {'en': 'HFF Artefacts', 'ar-lb': 'HFF القطع الأثرية'},
        'hff_pottery': {'en': 'HFF Underwater- Pottery', 'ar-lb': 'HFF الفخار تحت الماء'},
        'hff_modern_shipwreck': {'en': 'HFF ModernShipwreck', 'ar-lb': 'HFF حطام السفن الحديثة'},

        # =====================================================================
        # MEASUREMENT ABBREVIATIONS
        # =====================================================================
        'c': {'en': 'C', 'ar-lb': 'م'},
        'd': {'en': 'D', 'ar-lb': 'ق'},
        'l': {'en': 'L', 'ar-lb': 'ط'},
        'w': {'en': 'W', 'ar-lb': 'ع'},
        'bt': {'en': 'BT', 'ar-lb': 'قا'},
        'bw': {'en': 'BW', 'ar-lb': 'عق'},
        'll': {'en': 'LL', 'ar-lb': 'طي'},
        'lt': {'en': 'LT', 'ar-lb': 'طع'},
        'ml': {'en': 'ML', 'ar-lb': 'وط'},
        'mw': {'en': 'MW', 'ar-lb': 'وع'},
        'rl': {'en': 'RL', 'ar-lb': 'يط'},
        'rt': {'en': 'RT', 'ar-lb': 'يع'},
        'tt': {'en': 'TT', 'ar-lb': 'فط'},
        'tw': {'en': 'TW', 'ar-lb': 'فع'},

        # =====================================================================
        # ADDITIONAL SITE / SURVEY FIELDS
        # =====================================================================
        'survey': {'en': 'Survey', 'ar-lb': 'المسح'},
        'survey_type': {'en': 'Survey Type', 'ar-lb': 'نوع المسح'},
        'survey_site': {'en': 'Survey site', 'ar-lb': 'موقع المسح'},
        'start_date': {'en': 'Start date', 'ar-lb': 'تاريخ البدء'},
        'country_name': {'en': 'Country name', 'ar-lb': 'اسم البلد'},
        'definition_site': {'en': 'Definition site', 'ar-lb': 'تعريف الموقع'},
        'admin_subdivision': {'en': 'Administrative subvision', 'ar-lb': 'التقسيم الإداري'},
        'admin_subdivision_type': {'en': 'Administrative subvision type', 'ar-lb': 'نوع التقسيم الإداري'},
        'address': {'en': 'Address', 'ar-lb': 'العنوان'},
        'antique_name': {'en': 'Antique name', 'ar-lb': 'الاسم القديم'},
        'site_datum_point': {'en': 'Site Datum Point', 'ar-lb': 'نقطة مرجع الموقع'},
        'activity_type': {'en': 'Activity type', 'ar-lb': 'نوع النشاط'},

        # =====================================================================
        # ADDITIONAL BUTTON TOOLTIPS & ACTIONS
        # =====================================================================
        'first_record': {'en': 'First record', 'ar-lb': 'السجل الأول'},
        'prev_record': {'en': 'Previous record', 'ar-lb': 'السجل السابق'},
        'next_record': {'en': 'Next record', 'ar-lb': 'السجل التالي'},
        'last_record': {'en': 'Last record', 'ar-lb': 'السجل الأخير'},
        'save_record': {'en': 'Save record', 'ar-lb': 'حفظ السجل'},
        'delete_single_record': {'en': 'Delete single record', 'ar-lb': 'حذف سجل واحد'},
        'reload_all_records': {'en': 'Reload all records', 'ar-lb': 'إعادة تحميل جميع السجلات'},
        'filter_records': {'en': 'Filter records', 'ar-lb': 'تصفية السجلات'},
        'start_query_search': {'en': 'Start query search', 'ar-lb': 'بدء البحث'},
        'export_pdf_form': {'en': 'Export Pdf form', 'ar-lb': 'تصدير نموذج PDF'},
        'view_layers': {'en': 'View Layers', 'ar-lb': 'عرض الطبقات'},
        'gis_tools': {'en': 'GIS Tools', 'ar-lb': 'أدوات GIS'},
        'active_deactive_media_view': {'en': 'Active/deactive media view', 'ar-lb': 'تفعيل/إلغاء عرض الوسائط'},
        'upload_photos_db': {'en': 'Upload photos to database', 'ar-lb': 'رفع الصور إلى قاعدة البيانات'},
        'remove_selected_thumbnails': {'en': 'Remove selected thumbnails', 'ar-lb': 'إزالة الصور المصغرة المحددة'},
        'assign_tag_images': {'en': 'Assign tag to selected images', 'ar-lb': 'تعيين وسم للصور المحددة'},
        'remove_all_tags_images': {'en': 'Remove all tags from selected images', 'ar-lb': 'إزالة جميع الوسوم من الصور المحددة'},
        'activate_tags_display': {'en': 'Activate/deactivate tags display', 'ar-lb': 'تفعيل/إلغاء عرض الوسوم'},
        'image_search_bar': {'en': 'Image search bar', 'ar-lb': 'شريط بحث الصور'},

        # =====================================================================
        # ADDITIONAL LABELS
        # =====================================================================
        'total_record': {'en': 'Total record', 'ar-lb': 'إجمالي السجلات'},
        'total_images': {'en': 'Total images', 'ar-lb': 'إجمالي الصور'},
        'tag': {'en': 'Tag', 'ar-lb': 'الوسم'},
        'tags_manager': {'en': 'Tags manager', 'ar-lb': 'مدير الوسوم'},
        'tags_viewer_onoff': {'en': 'Tags viewer on/off', 'ar-lb': 'عارض الوسوم تشغيل/إيقاف'},
        'add_tags': {'en': 'Add tags', 'ar-lb': 'إضافة وسوم'},
        'thumbnail_path': {'en': 'Thumbnail path', 'ar-lb': 'مسار الصورة المصغرة'},
        'supervisor': {'en': 'Supervisor', 'ar-lb': 'المشرف'},
        'summary': {'en': 'Summary', 'ar-lb': 'الملخص'},
        'thesaurus': {'en': 'Thesaurus', 'ar-lb': 'قاموس المترادفات'},
        'value': {'en': 'Value', 'ar-lb': 'القيمة'},
        'backup_restore_hff_db': {'en': 'Backup / Restore HFF DB', 'ar-lb': 'نسخ احتياطي / استعادة قاعدة بيانات HFF'},
        'backup_hff_survey_db': {'en': 'Backup HFF survey DB', 'ar-lb': 'نسخ احتياطي لقاعدة بيانات المسح'},
        'backup_postgres': {'en': 'Backup postgres', 'ar-lb': 'نسخ احتياطي PostgreSQL'},
        'backup_sqlite': {'en': 'Backup sqlite', 'ar-lb': 'نسخ احتياطي SQLite'},
        'start': {'en': 'Start', 'ar-lb': 'بدء'},
        'abort': {'en': 'Abort', 'ar-lb': 'إلغاء'},

        # =====================================================================
        # ADDITIONAL COMBOBOX VALUES
        # =====================================================================
        'yes_lower': {'en': 'yes', 'ar-lb': 'نعم'},
        'no_lower': {'en': 'no', 'ar-lb': 'لا'},
        'good': {'en': 'Good', 'ar-lb': 'جيد'},
        'bad': {'en': 'Bad', 'ar-lb': 'سيء'},
        'very_bad': {'en': 'Very Bad', 'ar-lb': 'سيء جداً'},
        'north': {'en': 'North', 'ar-lb': 'شمال'},
        'south': {'en': 'South', 'ar-lb': 'جنوب'},
        'east': {'en': 'East', 'ar-lb': 'شرق'},
        'west': {'en': 'West', 'ar-lb': 'غرب'},
        'north_east': {'en': 'North-East', 'ar-lb': 'شمال شرق'},
        'north_west': {'en': 'North-West', 'ar-lb': 'شمال غرب'},
        'south_east': {'en': 'South-East', 'ar-lb': 'جنوب شرق'},
        'south_west': {'en': 'South-West', 'ar-lb': 'جنوب غرب'},
        'circular': {'en': 'Circular', 'ar-lb': 'دائري'},
        'sub_circular': {'en': 'Sub-circular', 'ar-lb': 'شبه دائري'},
        'sub_rectangular': {'en': 'Sub-rectangular', 'ar-lb': 'شبه مستطيل'},
        'irregular': {'en': 'Irregular', 'ar-lb': 'غير منتظم'},
        'square': {'en': 'Square', 'ar-lb': 'مربع'},
        'round': {'en': 'Round', 'ar-lb': 'مستدير'},
        'straight': {'en': 'Straight', 'ar-lb': 'مستقيم'},
        'winding': {'en': 'Winding', 'ar-lb': 'متعرج'},
        'zigzag': {'en': 'Zigzag', 'ar-lb': 'متعرج'},
        'alluvial_fan': {'en': 'Alluvial fan', 'ar-lb': 'مروحة طميية'},
        'valley_bed': {'en': 'Valley bed', 'ar-lb': 'قاع الوادي'},
        'valley_terrace': {'en': 'Valley terrace', 'ar-lb': 'مصطبة الوادي'},
        'slopes': {'en': 'Slopes', 'ar-lb': 'المنحدرات'},
        'summit': {'en': 'Summit', 'ar-lb': 'القمة'},
        'watercourse_banks': {'en': 'Watercourse banks', 'ar-lb': 'ضفاف المجرى المائي'},
        'watercourse_bed': {'en': 'Watercourse bed', 'ar-lb': 'قاع المجرى المائي'},

        # =====================================================================
        # ADDITIONAL ANCHOR FIELDS
        # =====================================================================
        'anchor_id': {'en': 'Anchor ID', 'ar-lb': 'معرف المرساة'},
        'anchor_con': {'en': 'Anchor conservation', 'ar-lb': 'ترميم المرساة'},
        'anchor_conservation': {'en': 'Anchor Conservation', 'ar-lb': 'ترميم المرساة'},
        'anchor_conservation_list': {'en': 'Anchor Conservation list', 'ar-lb': 'قائمة ترميم المراسي'},
        'anchor_conservation_export_pdf': {'en': 'Anchor conservation export pdf', 'ar-lb': 'تصدير ترميم المرساة PDF'},
        'anchor_point': {'en': 'Anchor Point', 'ar-lb': 'نقطة المرساة'},
        'bottom_hole': {'en': 'Bottom Hole', 'ar-lb': 'الثقب السفلي'},
        'top_hole': {'en': 'Top Hole', 'ar-lb': 'الثقب العلوي'},

        # =====================================================================
        # ADDITIONAL ARTEFACT FIELDS
        # =====================================================================
        'artefact_con': {'en': 'Artefact conservation', 'ar-lb': 'ترميم القطعة الأثرية'},
        'art_conservation': {'en': 'Art conservation', 'ar-lb': 'ترميم القطعة الفنية'},
        'artefact_point': {'en': 'Artefact Point', 'ar-lb': 'نقطة القطعة الأثرية'},
        'state_of_conservation': {'en': 'State of conservation', 'ar-lb': 'حالة الترميم'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - COMMON
        # =====================================================================
        'alert': {'en': 'Alert', 'ar-lb': 'تنبيه'},
        'attention': {'en': 'Attention', 'ar-lb': 'انتباه'},
        'system_message': {'en': 'System', 'ar-lb': 'النظام'},
        'connection_system': {'en': 'Connection System', 'ar-lb': 'نظام الاتصال'},
        'data_entry_error': {'en': 'Data entry error', 'ar-lb': 'خطأ في إدخال البيانات'},
        'warning_data_entry': {'en': 'Warning Data Entry', 'ar-lb': 'تحذير إدخال البيانات'},
        'search_error': {'en': 'Search error', 'ar-lb': 'خطأ في البحث'},
        'export_error': {'en': 'Export error', 'ar-lb': 'خطأ في التصدير'},
        'operation_completed': {'en': 'Operation completed', 'ar-lb': 'اكتملت العملية'},
        'operation_failed': {'en': 'Operation failed', 'ar-lb': 'فشلت العملية'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - RECORDS
        # =====================================================================
        'msg_no_records': {'en': 'No records found', 'ar-lb': 'لم يتم العثور على سجلات'},
        'msg_record_saved': {'en': 'Record saved successfully', 'ar-lb': 'تم حفظ السجل بنجاح'},
        'msg_record_deleted': {'en': 'Record deleted successfully', 'ar-lb': 'تم حذف السجل بنجاح'},
        'msg_delete_confirm': {'en': 'Are you sure you want to delete this record?', 'ar-lb': 'هل أنت متأكد من حذف هذا السجل؟'},
        'msg_first_record': {'en': 'You are at the first record', 'ar-lb': 'أنت في السجل الأول'},
        'msg_last_record': {'en': 'You are at the last record', 'ar-lb': 'أنت في السجل الأخير'},
        'msg_record_exists': {'en': 'Record already exists', 'ar-lb': 'السجل موجود بالفعل'},
        'msg_duplicate_record': {'en': 'Duplicate record found', 'ar-lb': 'تم العثور على سجل مكرر'},
        'msg_insert_site_value': {'en': 'Please insert a site value', 'ar-lb': 'الرجاء إدخال قيمة الموقع'},
        'msg_fill_required_fields': {'en': 'Please fill in all required fields', 'ar-lb': 'الرجاء ملء جميع الحقول المطلوبة'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - CONNECTION
        # =====================================================================
        'msg_connection_success': {'en': 'Connection successful', 'ar-lb': 'تم الاتصال بنجاح'},
        'msg_connection_failed': {'en': 'Connection failed', 'ar-lb': 'فشل الاتصال'},
        'msg_database_error': {'en': 'Database error', 'ar-lb': 'خطأ في قاعدة البيانات'},
        'msg_restart_qgis': {'en': 'You must restart QGIS', 'ar-lb': 'يجب إعادة تشغيل QGIS'},
        'msg_no_table': {'en': 'Table not found', 'ar-lb': 'الجدول غير موجود'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - EXPORT
        # =====================================================================
        'msg_pdf_exported': {'en': 'PDF exported successfully', 'ar-lb': 'تم تصدير PDF بنجاح'},
        'msg_excel_exported': {'en': 'Excel exported successfully', 'ar-lb': 'تم تصدير Excel بنجاح'},
        'msg_export_path': {'en': 'File exported to', 'ar-lb': 'تم تصدير الملف إلى'},
        'msg_select_records': {'en': 'Please select records to export', 'ar-lb': 'الرجاء تحديد السجلات للتصدير'},
        'msg_no_data_export': {'en': 'No data available for export', 'ar-lb': 'لا توجد بيانات للتصدير'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - GIS
        # =====================================================================
        'msg_layer_not_found': {'en': 'Layer not found', 'ar-lb': 'الطبقة غير موجودة'},
        'msg_select_layer': {'en': 'Please select a layer', 'ar-lb': 'الرجاء تحديد طبقة'},
        'msg_no_geometry': {'en': 'No geometry to display', 'ar-lb': 'لا توجد هندسة للعرض'},
        'msg_feature_not_found': {'en': 'Feature not found', 'ar-lb': 'المعلم غير موجود'},
        'msg_coordinates_updated': {'en': 'Coordinates updated', 'ar-lb': 'تم تحديث الإحداثيات'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - MEDIA
        # =====================================================================
        'msg_image_not_found': {'en': 'Image not found', 'ar-lb': 'الصورة غير موجودة'},
        'msg_no_images': {'en': 'No images available', 'ar-lb': 'لا توجد صور متاحة'},
        'msg_select_images': {'en': 'Please select images', 'ar-lb': 'الرجاء تحديد الصور'},
        'msg_tags_assigned': {'en': 'Tags assigned successfully', 'ar-lb': 'تم تعيين الوسوم بنجاح'},
        'msg_tags_removed': {'en': 'Tags removed successfully', 'ar-lb': 'تم إزالة الوسوم بنجاح'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - SEARCH
        # =====================================================================
        'msg_search_mode': {'en': 'Search mode activated', 'ar-lb': 'تم تفعيل وضع البحث'},
        'msg_browse_mode': {'en': 'Browse mode activated', 'ar-lb': 'تم تفعيل وضع التصفح'},
        'msg_no_search_results': {'en': 'No results found for your search', 'ar-lb': 'لم يتم العثور على نتائج لبحثك'},
        'msg_results_found': {'en': 'results found', 'ar-lb': 'نتائج وجدت'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - VALIDATION
        # =====================================================================
        'msg_invalid_data': {'en': 'Invalid data entered', 'ar-lb': 'البيانات المدخلة غير صالحة'},
        'msg_missing_field': {'en': 'Required field is missing', 'ar-lb': 'الحقل المطلوب مفقود'},
        'msg_numeric_required': {'en': 'Please enter a numeric value', 'ar-lb': 'الرجاء إدخال قيمة رقمية'},
        'msg_date_invalid': {'en': 'Invalid date format', 'ar-lb': 'تنسيق التاريخ غير صالح'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - BACKUP & RESTORE
        # =====================================================================
        'msg_backup_success': {'en': 'Backup completed successfully', 'ar-lb': 'تم النسخ الاحتياطي بنجاح'},
        'msg_backup_failed': {'en': 'Backup failed', 'ar-lb': 'فشل النسخ الاحتياطي'},
        'msg_restore_success': {'en': 'Restore completed successfully', 'ar-lb': 'تمت الاستعادة بنجاح'},
        'msg_restore_failed': {'en': 'Restore failed', 'ar-lb': 'فشلت الاستعادة'},
        'msg_action_cancelled': {'en': 'Action cancelled', 'ar-lb': 'تم إلغاء الإجراء'},
        'msg_action_deleted': {'en': 'Action deleted', 'ar-lb': 'تم حذف الإجراء'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - WELCOME & INITIALIZATION
        # =====================================================================
        'msg_welcome': {'en': 'Welcome in HFF survey', 'ar-lb': 'مرحباً بك في نظام HFF'},
        'msg_db_empty': {'en': 'The DB is empty. Push Ok and Good Work!', 'ar-lb': 'قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_hff_user': {'en': 'WELCOME HFF user', 'ar-lb': 'مرحباً بمستخدم HFF'},
        'msg_form_ready': {'en': 'Form ready', 'ar-lb': 'النموذج جاهز'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - VIDEO PLAYER & MEDIA
        # =====================================================================
        'msg_frame_saved': {'en': 'Frame saved to database', 'ar-lb': 'تم حفظ الإطار في قاعدة البيانات'},
        'msg_image_saved_db': {'en': 'Image saved to database', 'ar-lb': 'تم حفظ الصورة في قاعدة البيانات'},
        'msg_media_insert_failed': {'en': 'Failed to insert media record', 'ar-lb': 'فشل إدراج سجل الوسائط'},
        'msg_db_manager_not_available': {'en': 'Database manager not available', 'ar-lb': 'مدير قاعدة البيانات غير متوفر'},
        'msg_no_images_show': {'en': 'There are no images to show', 'ar-lb': 'لا توجد صور لعرضها'},
        'msg_select_images_tag': {'en': 'You must select one or more images to tag', 'ar-lb': 'يجب تحديد صورة واحدة أو أكثر لوضع علامة'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - DATABASE OPERATIONS
        # =====================================================================
        'msg_data_loaded': {'en': 'Data Loaded', 'ar-lb': 'تم تحميل البيانات'},
        'msg_update_done': {'en': 'Update Done', 'ar-lb': 'تم التحديث'},
        'msg_db_updated': {'en': 'The database has been updated', 'ar-lb': 'تم تحديث قاعدة البيانات'},
        'msg_db_exists': {'en': 'The Database exists already', 'ar-lb': 'قاعدة البيانات موجودة بالفعل'},
        'msg_connect_new_db': {'en': 'Successful installation, do you want to connect to the new DB?', 'ar-lb': 'تم التثبيت بنجاح، هل تريد الاتصال بقاعدة البيانات الجديدة؟'},
        'msg_insert_password': {'en': "Don't forget to insert the password", 'ar-lb': 'لا تنسَ إدخال كلمة المرور'},
        'msg_db_connection_problem': {'en': 'Database connection problem. Check the parameters inserted', 'ar-lb': 'مشكلة في الاتصال بقاعدة البيانات. تحقق من المعلمات المدخلة'},
        'msg_connect_postgres_first': {'en': 'You need to connect to PostgreSQL first', 'ar-lb': 'تحتاج للاتصال بـ PostgreSQL أولاً'},
        'msg_connection_ok': {'en': 'Connection ok', 'ar-lb': 'الاتصال ناجح'},
        'msg_successfully_connected': {'en': 'Successfully connected', 'ar-lb': 'تم الاتصال بنجاح'},
        'msg_connection_error': {'en': 'Connection error', 'ar-lb': 'خطأ في الاتصال'},
        'msg_db_version_low': {'en': 'You cannot update the db postgres because your version is lower than 9.4', 'ar-lb': 'لا يمكنك تحديث قاعدة بيانات postgres لأن إصدارك أقل من 9.4'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - IMPORT/EXPORT
        # =====================================================================
        'msg_import_completed': {'en': 'Import completed', 'ar-lb': 'اكتمل الاستيراد'},
        'msg_export_completed': {'en': 'Export completed', 'ar-lb': 'اكتمل التصدير'},
        'msg_duplicates_warning': {'en': 'If there are duplicates the import will be aborted. If you want to ignore the duplicates or update with new data check one of the options ignore or replace', 'ar-lb': 'إذا كانت هناك نسخ مكررة سيتم إلغاء الاستيراد. إذا أردت تجاهل النسخ المكررة أو التحديث ببيانات جديدة، حدد أحد خياري التجاهل أو الاستبدال'},
        'msg_new_data_copied': {'en': 'Only new data will be copied', 'ar-lb': 'سيتم نسخ البيانات الجديدة فقط'},
        'msg_data_update_existing': {'en': 'New data will be copied and existing data will be updated', 'ar-lb': 'سيتم نسخ البيانات الجديدة وتحديث البيانات الموجودة'},
        'msg_update_geometries': {'en': 'The system will update the geometries with the imported data. Press Cancel to abort otherwise press Ok to continue.', 'ar-lb': 'سيقوم النظام بتحديث الأشكال الهندسية بالبيانات المستوردة. اضغط إلغاء للإيقاف أو موافق للمتابعة.'},
        'msg_update_tables': {'en': 'The system will update the tables with the imported data. Press Cancel to abort otherwise press Ok to continue.', 'ar-lb': 'سيقوم النظام بتحديث الجداول بالبيانات المستوردة. اضغط إلغاء للإيقاف أو موافق للمتابعة.'},
        'msg_list_export_warning': {'en': "List can't be exported, you must fill the form first", 'ar-lb': 'لا يمكن تصدير القائمة، يجب ملء النموذج أولاً'},
        'msg_photo_list_export_warning': {'en': "Photo list can't be exported, you must tag the pics first", 'ar-lb': 'لا يمكن تصدير قائمة الصور، يجب وضع علامات على الصور أولاً'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - CONFIG & SETTINGS
        # =====================================================================
        'msg_path_set_success': {'en': 'The path has been set successful', 'ar-lb': 'تم تعيين المسار بنجاح'},
        'msg_directory_not_found': {'en': 'Directory not found', 'ar-lb': 'المجلد غير موجود'},
        'msg_query_activated': {'en': 'Query system activated. Select a site and click on save parameters', 'ar-lb': 'تم تفعيل نظام الاستعلام. اختر موقعاً وانقر على حفظ المعلمات'},
        'msg_query_deactivated': {'en': 'Query system deactivated', 'ar-lb': 'تم إلغاء تفعيل نظام الاستعلام'},
        'set_env_variable': {'en': 'Set Environmental Variable', 'ar-lb': 'تعيين متغير البيئة'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - SEARCH & NAVIGATION
        # =====================================================================
        'msg_no_search_set': {'en': 'No search has been set!!!', 'ar-lb': 'لم يتم تعيين أي بحث!!!'},
        'msg_new_search_click': {'en': 'To perform a new search click on the new search button', 'ar-lb': 'لإجراء بحث جديد انقر على زر بحث جديد'},
        'msg_no_row_selected': {'en': "You didn't select any row", 'ar-lb': 'لم تحدد أي صف'},
        'msg_save_changes_warning': {'en': 'If you have modified the record and have not saved it you will lose the data. Save?', 'ar-lb': 'إذا قمت بتعديل السجل ولم تحفظه ستفقد البيانات. هل تريد الحفظ؟'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - RECORD OPERATIONS
        # =====================================================================
        'msg_record_deleted': {'en': 'Record deleted!', 'ar-lb': 'تم حذف السجل!'},
        'msg_delete_warning': {'en': 'Do you really want to delete the record? The action is irreversible', 'ar-lb': 'هل تريد حقاً حذف السجل؟ الإجراء لا يمكن التراجع عنه'},
        'msg_unique_field_empty': {'en': 'ID Unique - The field must not be empty', 'ar-lb': 'المعرف الفريد - الحقل يجب ألا يكون فارغاً'},
        'msg_type_of_error': {'en': 'Type of Error', 'ar-lb': 'نوع الخطأ'},
        'msg_n_results_found': {'en': 'results found', 'ar-lb': 'نتائج وجدت'},
        'msg_no_results_filter': {'en': 'No records match the selected filters', 'ar-lb': 'لا توجد سجلات تطابق المرشحات المحددة'},

        # =====================================================================
        # QMESSAGEBOX MESSAGES - GIS & LAYERS
        # =====================================================================
        'msg_layer_error': {'en': 'Layer Error', 'ar-lb': 'خطأ في الطبقة'},
        'msg_layer_available': {'en': 'Layer available', 'ar-lb': 'الطبقة متوفرة'},
        'msg_layer_not_available': {'en': 'Layer not available', 'ar-lb': 'الطبقة غير متوفرة'},
        'msg_no_geometries_display': {'en': 'There are no geometries to display', 'ar-lb': 'لا توجد أشكال هندسية للعرض'},
        'msg_no_periods_interval': {'en': 'There are no Periods in this time interval', 'ar-lb': 'لا توجد فترات في هذا النطاق الزمني'},
        'msg_internet_slow': {'en': 'Internet slow or absent. The base map will not be loaded', 'ar-lb': 'الإنترنت بطيء أو غير موجود. لن يتم تحميل الخريطة الأساسية'},

        # =====================================================================
        # QMESSAGEBOX TITLES
        # =====================================================================
        'title_warning': {'en': 'Warning', 'ar-lb': 'تحذير'},
        'title_message': {'en': 'Message', 'ar-lb': 'رسالة'},
        'title_info': {'en': 'INFO', 'ar-lb': 'معلومات'},
        'title_alert': {'en': 'Alert', 'ar-lb': 'تنبيه'},
        'title_error': {'en': 'Error', 'ar-lb': 'خطأ'},
        'title_success': {'en': 'Success', 'ar-lb': 'نجاح'},
        'title_tester': {'en': 'TESTER', 'ar-lb': 'اختبار'},
        'title_hff': {'en': 'HFF', 'ar-lb': 'HFF'},
        'title_hff_system': {'en': 'HFF system', 'ar-lb': 'نظام HFF'},
        'title_no_results': {'en': 'No Results', 'ar-lb': 'لا توجد نتائج'},

        # =====================================================================
        # FORM-SPECIFIC WELCOME MESSAGES
        # =====================================================================
        'welcome_site_form': {'en': 'Welcome in HFF survey: Site form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج الموقع. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_shipwreck_form': {'en': 'Welcome in HFF survey: Shipwreck form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج حطام السفينة. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_anchor_form': {'en': 'Welcome in HFF survey: Anchor form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج المرساة. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_artefact_form': {'en': 'Welcome in HFF survey: Artefact form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج القطعة الأثرية. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_pottery_form': {'en': 'Welcome in HFF survey: Pottery form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج الفخار. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_divelog_form': {'en': 'Welcome in HFF survey: Dive Log form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج سجل الغطس. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},
        'welcome_eamena_form': {'en': 'Welcome in HFF survey: Eamena form. The DB is empty. Push Ok and Good Work!', 'ar-lb': 'مرحباً في مسح HFF: نموذج EAMENA. قاعدة البيانات فارغة. اضغط موافق وعمل سعيد!'},

        # =====================================================================
        # TOOLBAR BUTTON TOOLTIPS
        # =====================================================================
        'first_record': {'en': 'First record', 'ar-lb': 'السجل الأول'},
        'prev_record': {'en': 'Previous record', 'ar-lb': 'السجل السابق'},
        'next_record': {'en': 'Next record', 'ar-lb': 'السجل التالي'},
        'last_record': {'en': 'Last record', 'ar-lb': 'السجل الأخير'},
        'new_record': {'en': 'New record', 'ar-lb': 'سجل جديد'},
        'save_record': {'en': 'Save record', 'ar-lb': 'حفظ السجل'},
        'delete_single_record': {'en': 'Delete record', 'ar-lb': 'حذف السجل'},
        'start_query_search': {'en': 'Start search', 'ar-lb': 'بدء البحث'},
        'view_alls_records': {'en': 'View all records', 'ar-lb': 'عرض جميع السجلات'},
        'export_pdf_form': {'en': 'Export PDF', 'ar-lb': 'تصدير PDF'},
        'export_list': {'en': 'Export list', 'ar-lb': 'تصدير القائمة'},
        'export_tab': {'en': 'Export table', 'ar-lb': 'تصدير الجدول'},
        'gis_view': {'en': 'GIS View', 'ar-lb': 'عرض GIS'},
        'view_layers': {'en': 'Show layers', 'ar-lb': 'عرض الطبقات'},
        'gis_tools': {'en': 'GIS tools', 'ar-lb': 'أدوات GIS'},
        'import_track': {'en': 'Import track', 'ar-lb': 'استيراد المسار'},
        'assign_tag_images': {'en': 'Assign tags to images', 'ar-lb': 'تعيين علامات للصور'},
        'remove_all_tags_images': {'en': 'Remove tags from images', 'ar-lb': 'إزالة العلامات من الصور'},
        'connection_test': {'en': 'Test connection', 'ar-lb': 'اختبار الاتصال'},
        'filter_records': {'en': 'Filter records', 'ar-lb': 'تصفية السجلات'},
        'report_generator': {'en': 'Generate report', 'ar-lb': 'إنشاء تقرير'},
        'convert': {'en': 'Convert', 'ar-lb': 'تحويل'},
        'revert': {'en': 'Revert changes', 'ar-lb': 'التراجع عن التغييرات'},
        'go_to_form': {'en': 'Go to record', 'ar-lb': 'الذهاب إلى السجل'},
        'pdf2word': {'en': 'Export to Word', 'ar-lb': 'تصدير إلى Word'},

        # =====================================================================
        # DATABASE MANAGER MESSAGES
        # =====================================================================
        'db_manager': {'en': 'HFF - Database Manager', 'ar-lb': 'HFF - مدير قاعدة البيانات'},
        'msg_backup_starting': {'en': 'Starting backup...', 'ar-lb': 'بدء النسخ الاحتياطي...'},
        'msg_backup_progress': {'en': 'Backing up...', 'ar-lb': 'جاري النسخ الاحتياطي...'},
        'msg_backup_complete': {'en': 'Backup complete', 'ar-lb': 'اكتمل النسخ الاحتياطي'},
        'msg_backup_cancelled': {'en': 'Backup cancelled', 'ar-lb': 'تم إلغاء النسخ الاحتياطي'},
        'msg_backup_cancelling': {'en': 'Cancelling backup...', 'ar-lb': 'جاري إلغاء النسخ الاحتياطي...'},
        'msg_db_not_found': {'en': 'Database file not found', 'ar-lb': 'ملف قاعدة البيانات غير موجود'},
        'msg_config_not_found': {'en': 'Configuration file not found', 'ar-lb': 'ملف الإعدادات غير موجود'},
        'msg_select_backup_first': {'en': 'Please select a backup file first', 'ar-lb': 'يرجى تحديد ملف النسخ الاحتياطي أولاً'},
        'msg_unknown_backup_format': {'en': 'Unknown backup format', 'ar-lb': 'تنسيق النسخ الاحتياطي غير معروف'},
        'msg_confirm_restore': {'en': 'Do you want to restore this backup?', 'ar-lb': 'هل تريد استعادة هذا النسخ الاحتياطي؟'},
        'msg_confirm_delete_backup': {'en': 'Do you want to delete this backup file?', 'ar-lb': 'هل تريد حذف ملف النسخ الاحتياطي هذا؟'},
        'msg_backup_deleted': {'en': 'Backup file deleted', 'ar-lb': 'تم حذف ملف النسخ الاحتياطي'},
        'msg_backup_running': {'en': 'A backup is in progress. Cancel it?', 'ar-lb': 'يوجد نسخ احتياطي قيد التقدم. هل تريد إلغاؤه؟'},
        'confirm_restore': {'en': 'Confirm Restore', 'ar-lb': 'تأكيد الاستعادة'},
        'confirm_delete': {'en': 'Confirm Delete', 'ar-lb': 'تأكيد الحذف'},
        'select_backup': {'en': 'Select backup file', 'ar-lb': 'اختر ملف النسخ الاحتياطي'},
        'filename': {'en': 'Filename', 'ar-lb': 'اسم الملف'},
        'path': {'en': 'Path', 'ar-lb': 'المسار'},
        'size': {'en': 'Size', 'ar-lb': 'الحجم'},

        # =====================================================================
        # STATISTICS MODULE MESSAGES
        # =====================================================================
        'statistics': {'en': 'Statistics', 'ar-lb': 'الإحصائيات'},
        'category': {'en': 'Category', 'ar-lb': 'الفئة'},
        'count': {'en': 'Count', 'ar-lb': 'العدد'},
        'percentage': {'en': 'Percentage', 'ar-lb': 'النسبة المئوية'},
        'field': {'en': 'Field', 'ar-lb': 'الحقل'},
        'min': {'en': 'Min', 'ar-lb': 'الحد الأدنى'},
        'max': {'en': 'Max', 'ar-lb': 'الحد الأقصى'},
        'mean': {'en': 'Mean', 'ar-lb': 'المتوسط'},
        'median': {'en': 'Median', 'ar-lb': 'الوسيط'},
        'std_dev': {'en': 'Std Dev', 'ar-lb': 'الانحراف المعياري'},
        'frequency': {'en': 'Frequency', 'ar-lb': 'التكرار'},
        'other': {'en': 'Other', 'ar-lb': 'أخرى'},
        'generate_stats': {'en': 'Generate Statistics', 'ar-lb': 'إنشاء الإحصائيات'},
        'export_stats': {'en': 'Export Statistics', 'ar-lb': 'تصدير الإحصائيات'},
        'select_category': {'en': 'Select Category', 'ar-lb': 'اختر الفئة'},
        'chart_type': {'en': 'Chart Type', 'ar-lb': 'نوع الرسم البياني'},
        'bar_chart': {'en': 'Bar Chart', 'ar-lb': 'رسم بياني شريطي'},
        'pie_chart': {'en': 'Pie Chart', 'ar-lb': 'رسم بياني دائري'},
        'histogram': {'en': 'Histogram', 'ar-lb': 'مخطط توزيع'},
        'stats_by': {'en': 'Statistics by', 'ar-lb': 'إحصائيات حسب'},
        'no_data_stats': {'en': 'No data available for statistics', 'ar-lb': 'لا توجد بيانات متاحة للإحصائيات'},
        'stats_exported': {'en': 'Statistics exported successfully', 'ar-lb': 'تم تصدير الإحصائيات بنجاح'},
    }

    @classmethod
    def instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the i18n manager."""
        self._current_language = self._load_language()

    def _load_language(self) -> str:
        """Load language preference from settings."""
        settings = QgsSettings()
        return settings.value("HFF/language", "en")

    def _save_language(self, lang: str):
        """Save language preference."""
        settings = QgsSettings()
        settings.setValue("HFF/language", lang)

    def get_current_language(self) -> str:
        """Get the current language code."""
        return self._current_language

    def set_language(self, lang: str):
        """Set the current language."""
        if lang in self.LANGUAGES:
            self._current_language = lang
            self._save_language(lang)

    def is_rtl(self) -> bool:
        """Check if current language is RTL."""
        return self._current_language in self.RTL_LANGUAGES

    def tr(self, key: str, default: str = None) -> str:
        """Translate a key to the current language.

        Args:
            key: Translation key
            default: Default value if key not found

        Returns:
            Translated string
        """
        if key in self.TRANSLATIONS:
            translations = self.TRANSLATIONS[key]
            if self._current_language in translations:
                return translations[self._current_language]
            elif 'en' in translations:
                return translations['en']

        return default if default is not None else key

    def get_available_languages(self) -> dict:
        """Get dictionary of available languages."""
        return self.LANGUAGES.copy()

    def add_translation(self, key: str, translations: dict):
        """Add a custom translation.

        Args:
            key: Translation key
            translations: Dict with lang codes as keys
        """
        self.TRANSLATIONS[key] = translations


# Convenience function
def tr(key: str, default: str = None) -> str:
    """Shortcut for HffI18n.instance().tr()"""
    return HffI18n.instance().tr(key, default)
