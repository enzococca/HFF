'''

Created on 20/07/2026

@author: Enzo Cocca

Cross-database id remapping for the Import data tab (issue #57).

Every import branch renumbers the primary key of the rows it writes
(max_num_id + 1), so the numeric ids of the TARGET database never match
the ids of the SOURCE database — as soon as the source has a gap in its
numbering (deleted records) or the target is not empty, the two
sequences diverge. media_to_entity_table and media_thumb_table rows
carry those numeric ids (id_media, id_entity) as plain integers: copied
verbatim they end up pointing at the wrong media / the wrong form, which
is exactly what issue #57 reports (tagged images under the wrong dive
logs, Environment videos gone).

The remedy is to translate the ids through the NATURAL key of each
table, which survives the renumbering:

  media_table         filepath (UniqueConstraint ID_media_unico)
  dive_log            divelog_id + years + site
  site_table          name_site + type_class
  anchor_table        anchors_id
  artefact_log        artefact_id
  pottery_table       artefact_id
  shipwreck_table     code_id
  pottery_con         pottery_id
  anchor_con          anchor_id
  artefact_con        artefact_id

'''
from sqlalchemy import text as _sql


def _quoted(engine, identifier):
    return engine.dialect.identifier_preparer.quote(identifier)


def build_media_id_map(src_engine, dst_engine):
    """Return {source id_media: target id_media}, matched on filepath.

    Media whose filepath does not exist in the target (record skipped or
    not yet imported) are simply absent from the map — the caller
    decides how to report them.
    """
    with src_engine.connect() as con:
        src = con.execute(
            _sql("SELECT id_media, filepath FROM media_table")).fetchall()
    with dst_engine.connect() as con:
        dst = con.execute(
            _sql("SELECT id_media, filepath FROM media_table")).fetchall()
    by_path = {r[1]: int(r[0]) for r in dst if r[1] is not None}
    return {int(r[0]): by_path[r[1]] for r in src
            if r[1] is not None and r[1] in by_path}


# entity_type value (as written by the tagging code all over the forms)
# -> (table, id column, natural key columns). Several entity types point
# to the same table: the dive log alone is tagged as DIVELOG, DOC, PE
# (Photo/Video Environment) and US depending on which section of the
# form created the link.
ENTITY_NATURAL_KEYS = {
    'DIVELOG':   ('dive_log', 'id_dive', ('divelog_id', 'years', 'site')),
    'DOC':       ('dive_log', 'id_dive', ('divelog_id', 'years', 'site')),
    'PE':        ('dive_log', 'id_dive', ('divelog_id', 'years', 'site')),
    'US':        ('dive_log', 'id_dive', ('divelog_id', 'years', 'site')),
    'SITE':      ('site_table', 'id_sito', ('name_site', 'type_class')),
    'SPM':       ('site_table', 'id_sito', ('name_site', 'type_class')),
    'ANCHORS':   ('anchor_table', 'id_anc', ('anchors_id',)),
    'ANC':       ('anchor_table', 'id_anc', ('anchors_id',)),
    'ARTEFACT':  ('artefact_log', 'id_art', ('artefact_id',)),
    'ART':       ('artefact_log', 'id_art', ('artefact_id',)),
    'POTTERY':   ('pottery_table', 'id_rep', ('artefact_id',)),
    'SHIPWRECK': ('shipwreck_table', 'id_shipwreck', ('code_id',)),
    'POT_CON':   ('pottery_con', 'id_pot', ('pottery_id',)),
    'ANC_CON':   ('anchor_con', 'id_anc', ('anchor_id',)),
    'ART_CON':   ('artefact_con', 'id_art', ('artefact_id',)),
}


class EntityIdRemapper:
    """Translate (entity_type, source id) -> target id via natural keys.

    Loads each involved table at most once per database and caches the
    translation, so remapping thousands of media_to_entity rows costs a
    handful of SELECTs.
    """

    def __init__(self, src_engine, dst_engine):
        self.src_engine = src_engine
        self.dst_engine = dst_engine
        self._maps = {}

    def _load_table_map(self, table, id_col, key_cols):
        """{source id: target id} for one entity table."""
        def _rows(engine):
            cols = ', '.join(
                [_quoted(engine, id_col)]
                + [_quoted(engine, c) for c in key_cols])
            with engine.connect() as con:
                return con.execute(_sql(
                    'SELECT %s FROM %s' % (cols, _quoted(engine, table))
                )).fetchall()
        src = _rows(self.src_engine)
        dst = _rows(self.dst_engine)
        # keys normalized to str so that 2019 (int) == '2019' (text)
        # across backends with drifting column affinities
        def _key(row):
            return tuple('' if v is None else str(v).strip()
                         for v in row[1:])
        dst_by_key = {_key(r): int(r[0]) for r in dst}
        return {int(r[0]): dst_by_key[_key(r)] for r in src
                if _key(r) in dst_by_key}

    def remap(self, entity_type, src_id):
        """Target id for a source id, or None if it cannot be resolved
        (unknown entity_type, record missing on either side)."""
        spec = ENTITY_NATURAL_KEYS.get(str(entity_type))
        try:
            src_id = int(src_id)
        except (TypeError, ValueError):
            return None
        if spec is None:
            return None
        if spec[0] not in self._maps:
            try:
                self._maps[spec[0]] = self._load_table_map(*spec)
            except Exception:
                self._maps[spec[0]] = {}
        return self._maps[spec[0]].get(src_id)
