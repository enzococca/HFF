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


def _has_column(engine, table, column):
    """True if ``table.column`` exists (media_uuid/media_sha256 are only
    present after the media-identity migration, issue #58 follow-up)."""
    try:
        if engine.dialect.name == "sqlite":
            with engine.connect() as con:
                rows = con.execute(_sql("PRAGMA table_info(%s)" % table)).fetchall()
            return any(r[1] == column for r in rows)
        with engine.connect() as con:
            row = con.execute(_sql(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = :t AND column_name = :c LIMIT 1"),
                {"t": table, "c": column}).fetchone()
        return row is not None
    except Exception:
        return False


def _load_media_identity(engine):
    """Rows of (id_media, filepath, media_uuid, media_sha256), tolerating
    databases that predate the media-identity columns."""
    cols = ["id_media", "filepath"]
    cols.append("media_uuid" if _has_column(engine, "media_table", "media_uuid")
                else "NULL AS media_uuid")
    cols.append("media_sha256" if _has_column(engine, "media_table", "media_sha256")
                else "NULL AS media_sha256")
    with engine.connect() as con:
        return con.execute(
            _sql("SELECT %s FROM media_table" % ", ".join(cols))).fetchall()


def build_media_id_map(src_engine, dst_engine):
    """Return {source id_media: target id_media}.

    Each source media is matched to a target media by the most stable key
    available, in this order:

      1. ``media_uuid``   -- a stable identity copied verbatim on import;
      2. ``media_sha256`` -- content hash, identical across databases that were
         populated independently (this is what reconciles already-diverged
         databases);
      3. ``filepath``     -- the legacy natural key; still used as a fallback,
         but it breaks when files are moved/renamed or the two databases live
         on machines with different paths.

    Media with no match in the target are simply absent from the map — the
    caller decides how to report them.
    """
    src = _load_media_identity(src_engine)
    dst = _load_media_identity(dst_engine)

    dst_by_uuid, dst_by_sha, dst_by_path = {}, {}, {}
    for r in dst:
        idm = int(r[0])
        path, muuid, msha = r[1], r[2], r[3]
        if muuid:
            dst_by_uuid.setdefault(muuid, idm)
        if msha:
            dst_by_sha.setdefault(msha, idm)
        if path is not None:
            dst_by_path.setdefault(path, idm)

    result = {}
    for r in src:
        idm = int(r[0])
        path, muuid, msha = r[1], r[2], r[3]
        if muuid and muuid in dst_by_uuid:
            result[idm] = dst_by_uuid[muuid]
        elif msha and msha in dst_by_sha:
            result[idm] = dst_by_sha[msha]
        elif path is not None and path in dst_by_path:
            result[idm] = dst_by_path[path]
    return result


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
