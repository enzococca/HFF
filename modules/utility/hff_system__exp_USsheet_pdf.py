
from datetime import date

from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
from .hff_system__OS_utility import *
from .hff_pdf_base import (
    safe_eval_list, HFF_BLUE, HFF_BLUE_LIGHT, HFF_GRAY, HFF_GRAY_DARK, HFF_WHITE
)
from ..db.hff_system__conn_strings import Connection as _DiversConnection


def _fetch_divers_for_dive(site, divelog_id, years):
    """Query divers + diver_segments for one dive. Returns a list of
    dicts: [{"name", "role", "time_in", "time_out", "bottom_time",
    "segments": [{"mix","bar_start","bar_end","delta_p"}, ...]}, ...].
    Empty list when the new tables are absent or have no rows."""
    if not (site and divelog_id is not None and years is not None):
        return []
    try:
        from sqlalchemy import create_engine, text
        conn = _DiversConnection()
        engine = create_engine(conn.conn_str())
    except Exception:
        return []
    out = []
    try:
        with engine.connect() as con:
            # bottom_time was added in migration v2; on older DBs the
            # column may be missing — fall back to a query without it.
            try:
                rows = con.execute(text(
                    "SELECT id, diver_name, role, time_in, time_out, "
                    "bottom_time FROM divers WHERE site=:s AND "
                    "divelog_id=:d AND years=:y ORDER BY id"
                ), {"s": str(site), "d": int(divelog_id),
                    "y": int(years)}).fetchall()
            except Exception:
                rows = con.execute(text(
                    "SELECT id, diver_name, role, time_in, time_out, "
                    "NULL FROM divers WHERE site=:s AND "
                    "divelog_id=:d AND years=:y ORDER BY id"
                ), {"s": str(site), "d": int(divelog_id),
                    "y": int(years)}).fetchall()
            for r in rows:
                segs = con.execute(text(
                    "SELECT seq, breathing_mix, bar_start, bar_end, "
                    "delta_p FROM diver_segments WHERE diver_id=:i "
                    "ORDER BY seq"
                ), {"i": int(r[0])}).fetchall()
                out.append({
                    "name": r[1] or "",
                    "role": r[2] or "",
                    "time_in": r[3] or "",
                    "time_out": r[4] or "",
                    "bottom_time": "" if r[5] is None else str(r[5]),
                    "segments": [
                        {
                            "mix": s[1] or "",
                            "bar_start": s[2] or "",
                            "bar_end": s[3] or "",
                            "delta_p": s[4] or "",
                        }
                        for s in segs
                    ],
                })
    except Exception as exc:
        print("[divers PDF] fetch failed: {}".format(exc))
        return []
    return out


def _split_pipeish(value):
    """Split a legacy pipe-style string like 'EAN28 - EAN50 - EAN100'
    or '200 - 140 - 110' into a list of trimmed parts. Empty / None
    becomes ['']. Single-value strings come back as a 1-element list.
    Used to expand legacy single-row segments (where the user crammed
    multiple gas changes into one VARCHAR field) into multiple visual
    seg rows in the PDF."""
    if value is None:
        return [""]
    s = str(value).strip()
    if not s:
        return [""]
    # split on " - " (with surrounding spaces) but tolerate " -" / "- "
    import re
    parts = re.split(r"\s*-\s*", s)
    parts = [p.strip() for p in parts if p.strip() != ""]
    return parts or [""]


def _expand_segments(segments):
    """Walk each persisted segment and, when its fields contain pipe-
    style ' - ' delimiters, expand into multiple visual rows. Returns a
    flat list of dicts with single-value fields, ready for direct PDF
    table rendering. Single-value segments pass through unchanged."""
    out = []
    for s in segments or []:
        mixes = _split_pipeish(s.get("mix"))
        starts = _split_pipeish(s.get("bar_start"))
        ends = _split_pipeish(s.get("bar_end"))
        dps = _split_pipeish(s.get("delta_p"))
        n = max(len(mixes), len(starts), len(ends), len(dps), 1)

        def _pick(arr, i):
            if i < len(arr):
                return arr[i]
            return arr[-1] if arr else ""

        for i in range(n):
            out.append({
                "mix": _pick(mixes, i),
                "bar_start": _pick(starts, i),
                "bar_end": _pick(ends, i),
                "delta_p": _pick(dps, i),
            })
    return out


def _strip_unit_suffix(value):
    """Trim a trailing 'm' or 'meter(s)' so headers render 'max 32.6 m'
    even when the legacy column already had the unit baked in (avoids
    'max 32.6 m m')."""
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    low = s.lower()
    for suffix in (" meters", " meter", " m"):
        if low.endswith(suffix):
            return s[: -len(suffix)].strip()
    return s


def _render_divers_inline_table(divers, styles_normal, styles_header):
    """Build a single ReportLab Table flowable containing the diver +
    segment data, sized to fit inside a cell of the main divelog Table.
    When `divers` is empty, returns a small Paragraph saying 'No
    normalized diver data.' rather than an empty Table."""
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.lib import colors as _colors
    if not divers:
        return Paragraph("<i>No normalized diver data.</i>", styles_normal)

    rows = [["Diver", "Role", "Time in", "Time out", "Bottom time",
             "Mix", "Start", "End", "ΔP"]]
    for d in divers:
        name = d.get("name") or "—"
        role = d.get("role") or "no role"
        ti = d.get("time_in") or "–"
        to = d.get("time_out") or "–"
        bt = d.get("bottom_time") or "–"
        # First row per diver: identity columns + first segment.
        expanded = _expand_segments(d.get("segments", []))
        if not expanded:
            rows.append([name, role, ti, to, bt,
                         "–", "–", "–", "–"])
            continue
        first = expanded[0]
        rows.append([name, role, ti, to, bt,
                     first.get("mix") or "–",
                     first.get("bar_start") or "–",
                     first.get("bar_end") or "–",
                     first.get("delta_p") or "–"])
        # Continuation rows for additional segments — leave the diver
        # identity cells blank so the eye groups them visually.
        for seg in expanded[1:]:
            rows.append(["", "", "", "", "",
                         seg.get("mix") or "–",
                         seg.get("bar_start") or "–",
                         seg.get("bar_end") or "–",
                         seg.get("delta_p") or "–"])

    nested = Table(rows, hAlign="LEFT")
    nested.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, _colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), _colors.HexColor("#dcdcdc")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return nested


class NumberedCanvas_USsheet(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def define_position(self, pos):
        self.page_position(pos)
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(200*mm, 20*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm
class NumberedCanvas_USindex(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    def define_position(self, pos):
        self.page_position(pos)
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(270*mm, 10*mm, "Page %d of %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm
class single_US_pdf_sheet:
    def __init__(self, data):
        #self.id_dive=[0]
        self.divelog_id=data[0]
        self.area_id=data[1]
        self.diver_1=data[2]
        self.diver_2=data[3]
        self.diver_3=data[4]
        self.standby_diver=data[5]
        self.task=data[6]
        self.result=data[7]
        self.tender=data[8]
        self.bar_start=data[9]
        self.bar_end=data[10]
        self.temperature=data[11]
        self.visibility=data[12]
        self.current_=data[13]
        self.wind=data[14]
        self.breathing_mix=data[15]
        self.max_depth=data[16]
        self.surface_interval=data[17]
        self.comments_=data[18]
        self.bottom_time=data[19]
        self.photo_nbr=data[20]
        self.video_nbr=data[21]
        self.camera_of=data[22]
        self.time_in=data[23]
        self.time_out=data[24]
        self.date_=data[25]
        self.years=data[26]
        self.dp=data[27]
        self.photo_id=data[28]
        self.video_id=data[29]
        self.sito=data[30]
        self.layer=data[31]
        self.bar_start_2=data[32]
        self.bar_end_2=data[33]
        self.dp_2=data[34]
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def create_sheet(self):
        # Use improved font sizes for better readability
        styleSheet = getSampleStyleSheet()
        stylogo = styleSheet['Normal']
        stylogo.spaceBefore = 20
        stylogo.spaceAfter = 20
        stylogo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styInt = styleSheet['Normal']
        styInt.spaceBefore = 20
        styInt.spaceAfter = 20
        styInt.fontSize = 12  # Increased from 8
        styInt.alignment = 1  # CENTER
        styInt.textColor = HFF_BLUE  # Professional blue color

        # Banner title sits on the HFF_BLUE band: needs white text (the
        # Paragraph's own textColor wins over the table's TEXTCOLOR).
        styleSheet = getSampleStyleSheet()
        styBanner = styleSheet['Normal']
        styBanner.spaceBefore = 20
        styBanner.spaceAfter = 20
        styBanner.fontSize = 12
        styBanner.alignment = 1  # CENTER
        styBanner.textColor = colors.white

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 9  # Increased from 6
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 9  # Increased from 6
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER
        styUnitaTipo.textColor = HFF_BLUE

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 9  # Increased from 6
        styTitoloComponenti.alignment = 1  # CENTER
        intestazione = Paragraph("<b>Archaeological Underwater Survey - DIVELOG FORM<br/>" + "</b>", styBanner)
        home = os.environ['HFF_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.png')
        logo = Image(logo_path)
        ##      if test_image.drawWidth < 800:
        logo.drawHeight = 0.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 0.5*inch
        logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo2.png')
        logo2 = Image(logo_path2)
        ##      if test_image.drawWidth < 800:
        logo2.drawHeight = 0.5*inch*logo2.drawHeight / logo2.drawWidth
        logo2.drawWidth = 0.5*inch
        logo.hAlign = "CENTER"
        logo2.hAlign = "CENTER"
        #1 row
        divelog = Paragraph("<b>Dive log number:  </b>"  + str(self.divelog_id), styNormal)
        area_id = Paragraph("<b>Area</b><br/>"  + str(self.area_id), styNormal)
        years = Paragraph("<b>Year</b><br/>"  + str(self.years), styNormal)
        # Legacy per-diver paragraphs (diver_1/2, additional_diver,
        # bar_start/end_diver1/2, dp_diver1/2, breathing_mix, time_in,
        # time_out, bottom_time) are intentionally blanked: the canonical
        # source of diver info is now the "Divers" block appended below
        # by _render_divers_block(). The cell_schema slots they used to
        # occupy stay empty so the existing layout grid is preserved.
        # Issue #45/#56: bottom_time is per-diver (divers.bottom_time,
        # rendered inside the Divers table), while max_depth is a
        # dive-level field shown in the summary rows below.
        diver_1 = ''
        diver_2 = ''
        diver_3 = ''
        standby = Paragraph("<b>Standby Diver</b><br/>"  + self.standby_diver, styNormal)
        tender = Paragraph("<b>Dive Supervisor</b><br/>" + self.tender,styNormal)
        bar_start = ''
        bar_end = ''
        bottom_time = ''
        temperature = Paragraph("<b>UW Temperature</b><br/>"+ self.temperature,styNormal)
        visibility = Paragraph("<b>UW Visibility</b><br/>" + self.visibility,styNormal)
        current = Paragraph("<b>UW Current direction & strength</b><br/>" + self.current_,styNormal)
        wind = Paragraph("<b>Wind</b><br/>"+ self.wind,styNormal)
        breathing_mix = ''
        _md = _strip_unit_suffix(self.max_depth)
        if _md in ("None", "NULL"):
            _md = ""
        max_depth = Paragraph(
            "<b>Max Depth</b><br/>" + ("{} m".format(_md) if _md else ""),
            styNormal)
        surface_interval = Paragraph("<b>Surface Interval</b><br/>"+ self.surface_interval,styNormal)
        time_in = ''
        time_out = ''
        date_ = Paragraph("<b>Date</b><br/>"  + self.date_, styNormal)
        dp = ''
        # photos_taken = Paragraph("<b>Photos Taken</b><br/>"  , styInt)
        # videos_taken = Paragraph("<b>Videos taken</b><br/>"  , styInt)
        conditions = Paragraph("<b>U/W Conditions</b><br/>"  , styInt)
        camera_of = Paragraph("<b>Camera: </b>"  + self.camera_of, styNormal)
        photo_nbr = Paragraph("<b>Number of pictures: </b>"  + str(self.photo_nbr), styNormal)
        video_nbr = Paragraph("<b>Number of videos: </b>"  + str(self.video_nbr), styNormal)
        sito = Paragraph("<b>Location: </b>" + str(self.sito), styNormal)
        layer = Paragraph("<b>Layer</b><br/>"  + str(self.layer), styNormal)
        
      
        task = ''
        try:
            task = Paragraph("<b>Task</b><br/>" + self.task, styDescrizione)
        except:
            pass
        result = ''
        try:
            result = Paragraph("<b>Result</b><br/>" + self.result,styDescrizione)
        except:
            pass
        comments_ = ''
        try:
            comments_ = Paragraph("<b>Comments</b><br/>" + self.comments_,styDescrizione)
        except:
            pass
        # ----------------------------------------------------------------
        # Build a nested divers sub-Table that gets embedded as the LAST
        # row of the main cell_schema so it inherits the same styling.
        # ----------------------------------------------------------------
        try:
            _divers = _fetch_divers_for_dive(
                self.sito, self.divelog_id, self.years
            )
        except Exception as _exc:
            print("[divers PDF] fetch skipped: {}".format(_exc))
            _divers = []

        divers_flowable = _render_divers_inline_table(
            _divers, styNormal, styInt
        )

        # ----------------------------------------------------------------
        # Compact 13-row layout — the legacy per-diver paragraphs (which
        # were turned to '' earlier) are gone entirely. The "Divers"
        # row at the bottom hosts a nested Table whose contents come from
        # the divers + diver_segments tables (or a placeholder when empty).
        # ----------------------------------------------------------------
        years_p = Paragraph(
            "<b>Year</b><br/>" + str(self.years or ""), styNormal
        )
        surf_int_p = Paragraph(
            "<b>Surface Interval</b><br/>" + str(self.surface_interval or ""),
            styNormal,
        )
        divers_label = Paragraph("<b>Divers</b>", styInt)

        cell_schema = [
            # Row 0 — banner
            [logo2, '', intestazione, '', '', '', '', '', '', '',
             '', '', '', '', '', '', logo, ''],
            # Row 1 — location | dive log number
            [sito, '', '', '', '', '', '', '', '',
             divelog, '', '', '', '', '', '', '', ''],
            # Row 2 — date | area | year
            [date_, '', '', '', '', '',
             area_id, '', '', '', '', '',
             years_p, '', '', '', '', ''],
            # Row 3 — standby | dive supervisor | wind
            [standby, '', '', '', '', '',
             tender, '', '', '', '', '',
             wind, '', '', '', '', ''],
            # Row 4 — max depth | surface interval | (empty)
            [max_depth, '', '', '', '', '',
             surf_int_p, '', '', '', '', '',
             '', '', '', '', '', ''],
            # Row 5 — photo count | video count | camera
            [photo_nbr, '', '', '', '', '',
             video_nbr, '', '', '', '', '',
             camera_of, '', '', '', '', ''],
            # Row 6 — task (full width)
            [task, '', '', '', '', '', '', '', '', '',
             '', '', '', '', '', '', '', ''],
            # Row 7 — result (full width)
            [result, '', '', '', '', '', '', '', '', '',
             '', '', '', '', '', '', '', ''],
            # Row 8 — comments (full width)
            [comments_, '', '', '', '', '', '', '', '', '',
             '', '', '', '', '', '', '', ''],
            # Row 9 — U/W Conditions header
            [conditions, '', '', '', '', '', '', '', '', '',
             '', '', '', '', '', '', '', ''],
            # Row 10 — current | visibility | temperature
            [current, '', '', '', '', '',
             visibility, '', '', '', '', '',
             temperature, '', '', '', '', ''],
            # Row 11 — Divers label
            [divers_label, '', '', '', '', '', '', '', '', '',
             '', '', '', '', '', '', '', ''],
            # Row 12 — Divers nested Table (or placeholder)
            [divers_flowable, '', '', '', '', '', '', '', '', '',
             '', '', '', '', '', '', '', ''],
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, HFF_GRAY_DARK),
            # Header row blue band
            ('BACKGROUND', (0, 0), (-1, 0), HFF_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            # Alternating row backgrounds for the body
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HFF_GRAY]),
            # Cell padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Row 0 — banner
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (2, 0), (15, 0)),
            ('SPAN', (16, 0), (17, 0)),
            # Row 1 — sito | divelog
            ('SPAN', (0, 1), (8, 1)),
            ('SPAN', (9, 1), (17, 1)),
            # Rows 2-5 — three cells per row, each spanning 6 columns
            ('SPAN', (0, 2), (5, 2)),
            ('SPAN', (6, 2), (11, 2)),
            ('SPAN', (12, 2), (17, 2)),
            ('SPAN', (0, 3), (5, 3)),
            ('SPAN', (6, 3), (11, 3)),
            ('SPAN', (12, 3), (17, 3)),
            ('SPAN', (0, 4), (5, 4)),
            ('SPAN', (6, 4), (11, 4)),
            ('SPAN', (12, 4), (17, 4)),
            ('SPAN', (0, 5), (5, 5)),
            ('SPAN', (6, 5), (11, 5)),
            ('SPAN', (12, 5), (17, 5)),
            # Rows 6-9 — full width
            ('SPAN', (0, 6), (17, 6)),
            ('SPAN', (0, 7), (17, 7)),
            ('SPAN', (0, 8), (17, 8)),
            ('SPAN', (0, 9), (17, 9)),
            # Row 10 — three cells per row
            ('SPAN', (0, 10), (5, 10)),
            ('SPAN', (6, 10), (11, 10)),
            ('SPAN', (12, 10), (17, 10)),
            # Row 11 — Divers label
            ('SPAN', (0, 11), (17, 11)),
            ('BACKGROUND', (0, 11), (-1, 11), HFF_BLUE_LIGHT),
            # Row 12 — Divers nested Table
            ('SPAN', (0, 12), (17, 12)),
            ('LEFTPADDING', (0, 12), (-1, 12), 8),
            ('RIGHTPADDING', (0, 12), (-1, 12), 8),
        ]
        colWidths = (15, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                     30, 30, 30, 30, 30, 30, 30, 30)
        rowHeights = None
        t = Table(
            cell_schema, colWidths=colWidths, rowHeights=rowHeights,
            style=table_style,
        )
        return [t]
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles


class Photo_index_pdf(object):
    
    
    def __init__(self, data):
        self.divelog_id=data[0]
        self.area_id=data[1]
        self.photo_id=data[28]
        self.video_id=data[29]
        self.sito=data[30]
    
    def getintestazione(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        #1 row
        
        
        divelog1 = Paragraph("DIVEID", styNormal)
        area_id1 = Paragraph("Area", styNormal)
        photo_id1 = Paragraph("PhotoID", styNormal)
        description_p1 = Paragraph("Description", styNormal)
        video_id1 = Paragraph("VideoID", styNormal)
        description_v1 = Paragraph("Description", styNormal)
    
    
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9
        #1 row
        
        
        
        
        
        
        divelog = Paragraph("<b>DIVEID: </b><br/>"+str(self.divelog_id), styNormal)
        area_id = Paragraph( "<b>Area</b><br/>"+str(self.area_id), styNormal)
        
        sito = Paragraph( str(self.sito), styNormal)
        
        
        photos = safe_eval_list(self.photo_id)
        photo_id = ''
        description_p = ''
        
        for i in photos:
            if photo_id == '':
                try:
                    photo_id += str(i[0])+ "<br/>"
                    description_p += str(i[1])+ "<br/>"
                except:
                    pass
            else:
                try:
                    photo_id += ' ' + str(i[0])+ "<br/>"
                    description_p += ' ' + str(i[1])+ "<br/>"
                except:
                    pass
        photo_id = Paragraph("<b>PhotoID</b><br/>"+ photo_id, styNormal)
        description_p = Paragraph( "<b>Description</b><br/>"+ description_p, styNormal)
        
        videos = safe_eval_list(self.video_id)
        video_id = ''
        description_v= ''
        
        for i in videos:
            if video_id == '':
                try:
                    video_id += ' ' + str(i[0])+ "<br/>"
                    description_v += str(i[1])+ "<br/>"
                except:
                    pass
            else:
                try:
                    video_id += ' ' +str(i[0])+ "<br/>"
                    description_v += ' ' + str(i[1])+ "<br/>"
                except:
                    pass
        video_id = Paragraph( "<b>VideoID</b><br/>"+video_id, styNormal)
        description_v = Paragraph( "<b>Description</b><br/>"+ description_v, styNormal)
        
        
        data =[
            
            divelog,
            area_id,
            photo_id,
            description_p,
            video_id,
            description_v 
            ]
        return data
        
       
        
        
    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
        ])  #finale
        return styles


class generate_US_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def build_US_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_US_sheet = single_US_pdf_sheet(records[i])
            elements.extend(single_US_sheet.create_sheet())
            elements.append(PageBreak())
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'Divelog_forms.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A3)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)
        f.close()
        
class generate_photo_pdf:
    HOME = os.environ['HFF_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "HFF_PDF_folder")
    # @staticmethod
    # def _header_footer(canvas, doc):

        # # Save the state of our canvas so we can draw on it

        # canvas.saveState()

        # styles = getSampleStyleSheet()

 

        # # Header

        # header = Paragraph('' , styles['Normal'])

        # w, h = header.wrap(doc.width, doc.topMargin)

        # header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

 

        # # Footer

        # footer = Paragraph('' , styles['Normal'])

        # w, h = footer.wrap(doc.width, doc.bottomMargin)

        # footer.drawOn(canvas, doc.leftMargin, h)

 

        # # Release the canvas

        # canvas.restoreState()
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    
    def build_P_sheets(self,records,sito):
        home = os.environ['HFF_HOME']
        self.width, self.height = (A3)

        home_DB_path = '{}{}{}'.format(home, os.sep, 'HFF_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'banner.png')
        
        
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"
        
       
        
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()
        list=[]
        list.append(logo)
        
        list.append(Paragraph("<b>HFF Archaeological Survey UW - Photo Index</b><br/><br/><b>Location: %s,  Date: %s</b><br/>" % (sito, data), styH1))
     
       
        table_data = [] 
       
        
        
        for i in range(len(records)):
            exp_index = Photo_index_pdf(records[i])
            
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [50, 100, 120, 190, 120, 190]

        table_data_formatted = Table( table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        list.append(table_data_formatted)
        list.append(Spacer(0, 0))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Photo_index_UW.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A2, showBoundary=0, topMargin=15, bottomMargin=40,
                                leftMargin=30, rightMargin=30)
        doc.build(list, canvasmaker=NumberedCanvas_USindex)

        f.close()  
