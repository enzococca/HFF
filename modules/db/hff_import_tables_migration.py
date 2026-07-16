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


def ensure_import_target_tables(engine):
    """Create on `engine` any HFF table an old database may lack.

    Uses the same SQLAlchemy Table definitions the plugin writes
    through, so the created tables match exactly what the insert
    functions expect. Idempotent (checkfirst) and per-table fault
    tolerant: one broken structure never blocks the others.
    """
    for module_name, class_name in _STRUCTURES:
        try:
            mod = importlib.import_module(
                '.structures.' + module_name, __package__)
            getattr(mod, class_name).metadata.create_all(
                engine, checkfirst=True)
        except Exception as exc:
            print('[hff_import_tables_migration] %s skipped: %s'
                  % (module_name, exc))
