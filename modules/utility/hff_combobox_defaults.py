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
    ('pottery_table', 'conservation'): [
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
    ('anchor_table', 'typology'): [
        'Composite', 'Stone weight', 'Stone with hole', 'One-hole',
        'Two-hole', 'Three-hole', 'Trapezoidal', 'Triangular', 'Y-shaped',
        'Lead-stocked', 'Wooden', 'Iron', 'Admiralty', 'Stockless',
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


def populate(combo, db_values=None, table=None, field=None,
             defaults=None, editable=True, sort=True):
    """Merge DB-distinct values with curated defaults and load into combo.

    combo:      QComboBox to fill
    db_values:  iterable of strings already pulled via group_by (may be None)
    table:      table name key to look up DEFAULTS (e.g. 'pottery_table')
    field:      field name key (e.g. 'form')
    defaults:   override list — when provided, ignores DEFAULTS[table,field]
    editable:   set the combo to editable so the user can type new values
    sort:       sort merged list alphabetically
    """
    db_values = list(db_values or [])
    if defaults is None and table is not None and field is not None:
        defaults = DEFAULTS.get((table, field), [])
    merged = {v for v in (db_values + list(defaults or [])) if v}
    items = sorted(merged) if sort else list(merged)
    combo.clear()
    combo.setEditable(bool(editable))
    combo.addItems(items)
    return items
