'''

Created on 16/07/2026

@author: Enzo Cocca

Idempotent creation of tables that older HFF databases lack (issue #40).

The SQLAlchemy structure modules create their tables only on the
connection that is ACTIVE when they are first imported, so a database
used as the TARGET of the Import data / Import Geometry tab — or any
database created before a feature existed — can miss entire tables:
the conservation tables (pottery_con / anchor_con / artefact_con,
added for issue #54) and the geometry tables (site_point,
pottery_point, artefact_point, ...). Every INSERT of the import then
dies with "(sqlite3.OperationalError) no such table: ...".

Running this on every connection guarantees the import INSERTs find
their tables, on new and old databases alike, for both SQLite and
PostgreSQL targets.

'''
import importlib

from sqlalchemy import inspect as _sqla_inspect
from sqlalchemy import text as _sqla_text

# (module in .structures, class name). Each class owns a MetaData that
# contains just its own table, so create_all is a cheap checkfirst.
_STRUCTURES = (
    # conservation forms (issue #54 / #40)
    ('POT_con', 'POT_con'),
    ('ANC_con', 'ANC_con'),
    ('ART_con', 'ART_con'),
    # geometry tables (issue #40)
    ('Site_point_table', 'Site_point_table'),
    ('Site_line_table', 'Site_line_table'),
    ('Site_polygon_table', 'Site_polygon_table'),
    ('anchor_point_table', 'anchor_point_table'),
    ('artefact_point_table', 'artefact_point_table'),
    ('pottery_point_table', 'pottery_point_table'),
    ('features_point_table', 'features_point_table'),
    ('features_line_table', 'features_line_table'),
    ('features_poligon_table', 'features_poligon_table'),
    ('grabspot_point_table', 'grabspot_point_table'),
    ('shipwreck_point_table', 'shipwreck_point_table'),
    ('transect_poligon_table', 'transect_poligon_table'),
)


def _add_missing_columns(engine, table):
    """ALTER TABLE ADD COLUMN for every column the live table lacks.

    Old databases can have the table but an older shape — e.g. a
    postgres artefact_point/pottery_point without x, y, rotation,
    "Layer" (issue #40): every SELECT the mapper builds then dies with
    psycopg2 UndefinedColumn. Adding the missing columns (NULL for the
    existing rows) realigns the schema on sqlite and postgres alike.
    """
    try:
        inspector = _sqla_inspect(engine)
        if not inspector.has_table(table.name):
            return
        existing = {c['name'] for c in inspector.get_columns(table.name)}
    except Exception as exc:
        print('[hff_import_tables_migration] inspect %s skipped: %s'
              % (table.name, exc))
        return
    preparer = engine.dialect.identifier_preparer
    for column in table.columns:
        if column.name in existing:
            continue
        try:
            ddl = 'ALTER TABLE %s ADD COLUMN %s %s' % (
                preparer.quote(table.name),
                preparer.quote(column.name),
                column.type.compile(engine.dialect))
            with engine.begin() as con:
                con.execute(_sqla_text(ddl))
        except Exception as exc:
            print('[hff_import_tables_migration] add column %s.%s '
                  'skipped: %s' % (table.name, column.name, exc))


def ensure_import_target_tables(engine):
    """Create on `engine` any HFF table an old database may lack, and
    add any column an existing table is missing.

    Uses the same SQLAlchemy Table definitions the plugin writes
    through, so the created tables match exactly what the insert
    functions expect. Idempotent (checkfirst) and per-table fault
    tolerant: one broken structure never blocks the others.
    """
    for module_name, class_name in _STRUCTURES:
        try:
            mod = importlib.import_module(
                '.structures.' + module_name, __package__)
            metadata = getattr(mod, class_name).metadata
            metadata.create_all(engine, checkfirst=True)
            for table in metadata.tables.values():
                _add_missing_columns(engine, table)
        except Exception as exc:
            print('[hff_import_tables_migration] %s skipped: %s'
                  % (module_name, exc))
