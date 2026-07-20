"""Centralized default vocabularies for free-text comboboxes.

Free-text combos in Pottery / Anchor / Artefact / Dive log / Shipwreck used to
be populated only from `DISTINCT` DB values (`DB_MANAGER.group_by`). On a fresh
DB they were empty.

`populate()` merges the DB values with a curated default list and makes the
combobox editable so the user can also type free text. The merged list is
de-duplicated, empty/None stripped, sorted.

Intended migration path: when the per-project Thesaurus dialog ships
(`hff_system__thesaurus_sigle`), `populate()` will additionally read the
thesaurus rows for `(table, field)` and merge them with these baked defaults.
"""

DEFAULTS = {
    # ---- Pottery ---------------------------------------------------------
    ('pottery_table', 'form'): [
        'Bowl', 'Cup', 'Plate', 'Dish', 'Amphora', 'Jug', 'Jar', 'Bottle',
        'Pitcher', 'Krater', 'Lekythos', 'Pyxis', 'Cooking pot', 'Lamp',
        'Storage jar', 'Pithos', 'Basin',
    ],
    # issue #57: conservation is a yes/no flag ("is it in conservation?",
    # the column is even a String(4)); the preservation vocabulary that
    # used to sit here belongs to the State of Preservation field below.
    ('pottery_table', 'conservation'): [
        'Yes', 'No',
    ],
    ('pottery_table', 'state'): [
        'Excellent', 'Good', 'Fair', 'Poor', 'Fragmentary',
    ],
    ('pottery_table', 'samples'): [
        'Macroscopic', 'Petrographic', 'Chemical', 'Residue',
        'Radiocarbon', 'Thermoluminescence',
    ],

    # ---- Anchor ----------------------------------------------------------
    ('anchor_table', 'origin'): [
        'Local', 'Imported', 'Mediterranean', 'Eastern Mediterranean',
        'Aegean', 'Levantine', 'Egyptian', 'Phoenician', 'Unknown',
    ],
    # Per-field anchor vocabularies (issue from WhatsApp video 2026-05-14):
    # previously the typology list merged stone materials, anchor shapes and
    # hole counts into one chaotic combobox. Split into proper categories so
    # each combo only offers its own kind of value.
    ('anchor_table', 'stone_type'): [
        'Basalt', 'Conglomerate', 'Granite', 'Limestone', 'Marble',
        'Sandstone', 'Schist', 'Other',
    ],
    ('anchor_table', 'anchor_type'): [
        'Admiralty', 'Composite', 'Iron', 'Lead-stocked', 'Stockless',
        'Wooden',
    ],
    ('anchor_table', 'anchor_shape'): [
        'Cylindrical', 'Pyramidal', 'Spherical', 'Trapezoidal',
        'Triangular', 'Y-shaped',
    ],
    ('anchor_table', 'type_hole'): [
        'No-hole', 'One-hole', 'Two-hole', 'Three-hole',
    ],
    # typology is now the high-level "what kind of anchor object" category,
    # not a dump for every other field's vocabulary.
    ('anchor_table', 'typology'): [
        'Composite', 'Metal', 'Stone weight', 'Stone with hole',
    ],

    # ---- Artefact --------------------------------------------------------
    ('artefact_log', 'material'): [
        'Pottery', 'Glass', 'Metal', 'Stone', 'Bone', 'Ivory', 'Wood',
        'Leather', 'Textile', 'Bronze', 'Iron', 'Lead', 'Copper', 'Tin',
        'Gold', 'Silver', 'Faience', 'Stucco', 'Plaster', 'Shell', 'Coral',
    ],
    ('artefact_log', 'treatment'): [
        'Cleaned', 'Conserved', 'Restored', 'Untreated', 'Desalinated',
        'Consolidated', 'Stabilized',
    ],
    ('artefact_log', 'obj'): [
        'Vessel', 'Tool', 'Weapon', 'Ornament', 'Jewelry',
        'Architectural element', 'Sculpture', 'Coin', 'Bead', 'Bottle',
        'Lamp', 'Pin', 'Needle', 'Ring', 'Bracelet', 'Hook', 'Nail',
        'Anchor', 'Cargo',
    ],
    ('artefact_log', 'shape'): [
        'Round', 'Square', 'Rectangular', 'Triangular', 'Cylindrical',
        'Conical', 'Spherical', 'Oval', 'Irregular', 'Linear', 'Curved',
        'Angular', 'Polygonal',
    ],

    # ---- Dive log (UW) --------------------------------------------------
    ('dive_log', 'wind'): [
        'Calm', 'Light air', 'Light breeze', 'Gentle breeze',
        'Moderate breeze', 'Fresh breeze', 'Strong breeze', 'Near gale',
        'Gale', 'Strong gale', 'Storm', 'Violent storm', 'Hurricane',
    ],

    # ---- Shipwreck ------------------------------------------------------
    ('shipwreck_table', 'confidence'): [
        'High', 'Medium', 'Low', 'Uncertain',
    ],
    ('shipwreck_table', 'nationality'): [
        'Phoenician', 'Greek', 'Roman', 'Byzantine', 'Arab', 'Ottoman',
        'Venetian', 'Crusader', 'British', 'French', 'Italian', 'Egyptian',
        'Lebanese', 'Syrian', 'Cypriot', 'Spanish', 'Portuguese', 'Dutch',
        'American', 'Unknown',
    ],
    ('shipwreck_table', 'purpose'): [
        'Cargo', 'Military', 'Fishing', 'Passenger', 'Cargo and passenger',
        'Trade', 'War', 'Patrol', 'Transport', 'Unknown',
    ],
    ('shipwreck_table', 'depth_quality'): [
        'Measured', 'Estimated', 'Reported', 'Unknown',
    ],
    ('shipwreck_table', 'position_quality_1'): [
        'GPS', 'Surveyed', 'Estimated', 'Reported', 'Unknown',
    ],
    ('shipwreck_table', 'status'): [
        'Identified', 'Unidentified', 'Under investigation', 'Surveyed',
        'Excavated', 'Salvaged', 'Lost', 'Protected', 'At risk',
    ],
}


def _query_thesaurus(db_manager, table, field, locale=None):
    """Pull `sigla_estesa` rows from `hff_system__thesaurus_sigle` filtered by
    (nome_tabella=table, tipologia_sigla=field). Locale is ignored on purpose:
    if a project lead curates the vocabulary in English, we still want it
    visible to a user running QGIS in Italian or Arabic. Locale-specific
    behavior can be reintroduced later via a setting.

    Best-effort: on any error (legacy DB without the thesaurus table, no DB
    connection, ORM mapping race during plugin load, etc.) return an empty
    list so the caller falls back to in-code DEFAULTS.
    """
    if db_manager is None or table is None or field is None:
        return []
    search = {
        'nome_tabella': "'" + str(table) + "'",
        'tipologia_sigla': "'" + str(field) + "'",
    }
    try:
        rows = db_manager.query_bool(search, 'HFF_THESAURUS_SIGLE')
    except Exception:
        return []
    out = []
    for r in rows or []:
        v = getattr(r, 'sigla_estesa', None)
        if v:
            out.append(v)
    return out


def populate(combo, db_values=None, table=None, field=None,
             defaults=None, editable=True, sort=True,
             db_manager=None, locale=None):
    """Merge thesaurus + DB-distinct + in-code defaults, load into combo.

    Lookup order (each merged in):
      1. thesaurus rows for (table, field, locale)        — if db_manager
      2. db_values                                         — caller-provided
      3. DEFAULTS[(table, field)]                          — in-code seed

    combo:       QComboBox to fill
    db_values:   iterable of strings already pulled via group_by (may be None)
    table:       table name key (e.g. 'pottery_table')
    field:       field name key (e.g. 'form')
    defaults:    override the in-code seed for this call
    editable:    setEditable so the user can also type free text
    sort:        sort the merged list alphabetically
    db_manager:  Hff_db_management instance, used to query the thesaurus
    locale:      'en', 'ar-lb', 'it' — None means any-language
    """
    db_values = list(db_values or [])
    thes_values = _query_thesaurus(db_manager, table, field, locale)
    if defaults is None and table is not None and field is not None:
        defaults = DEFAULTS.get((table, field), [])
    merged = {v for v in (thes_values + db_values + list(defaults or [])) if v}
    items = sorted(merged) if sort else list(merged)
    combo.clear()
    combo.setEditable(bool(editable))
    combo.addItems(items)
    return items
