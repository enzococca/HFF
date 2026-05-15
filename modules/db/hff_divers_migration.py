"""Idempotent schema migration that adds the divers + diver_segments
tables to the HFF target DB and populates them from the legacy dive_log
columns. Mirror of bot/sync/divers_schema.py — keep in sync.

Adapted for the QGIS plugin's Python environment (3.9):
- uses `datetime.now(timezone.utc)` instead of the 3.11+ `UTC` alias
- uses `last_insert_rowid()` on SQLite instead of `RETURNING id`
  (`RETURNING` requires SQLite 3.35+ which QGIS bundling may lag).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine

_TARGET_VERSION = 2


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _table_exists(con, name: str) -> bool:
    """Portable existence check across sqlite + postgres."""
    if con.dialect.name == "sqlite":
        row = con.execute(
            text("SELECT 1 FROM sqlite_master WHERE type='table' AND name=:n"),
            {"n": name},
        ).fetchone()
        return row is not None
    row = con.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = :n LIMIT 1"
        ),
        {"n": name},
    ).fetchone()
    return row is not None


def _create_version_table(con) -> None:
    con.execute(text(
        "CREATE TABLE IF NOT EXISTS hff_schema_version ("
        "  component TEXT PRIMARY KEY,"
        "  version INTEGER NOT NULL,"
        "  applied_at TEXT NOT NULL"
        ")"
    ))


def _read_version(engine: Engine, component: str) -> int:
    with engine.connect() as con:
        if not _table_exists(con, "hff_schema_version"):
            return 0
        row = con.execute(
            text("SELECT version FROM hff_schema_version WHERE component=:c"),
            {"c": component},
        ).fetchone()
        return int(row[0]) if row else 0


def _write_version(con, component: str, version: int) -> None:
    con.execute(
        text(
            "INSERT INTO hff_schema_version (component, version, applied_at) "
            "VALUES (:c, :v, :t) "
            "ON CONFLICT(component) DO UPDATE SET version = :v, applied_at = :t"
        ),
        {"c": component, "v": version, "t": _now_iso()},
    )


def _create_divers_tables(con) -> None:
    if con.dialect.name == "sqlite":
        divers_pk = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        seg_pk = "id INTEGER PRIMARY KEY AUTOINCREMENT"
    else:
        divers_pk = "id SERIAL PRIMARY KEY"
        seg_pk = "id SERIAL PRIMARY KEY"
    con.execute(text(
        f"CREATE TABLE IF NOT EXISTS divers ("
        f"  {divers_pk},"
        "  site TEXT NOT NULL,"
        "  divelog_id INTEGER NOT NULL,"
        "  years INTEGER NOT NULL,"
        "  diver_name TEXT NOT NULL,"
        "  role TEXT,"
        "  time_in TEXT,"
        "  time_out TEXT,"
        "  max_depth NUMERIC(5,2),"
        "  bottom_time TEXT,"
        "  UNIQUE(site, divelog_id, years, diver_name),"
        "  FOREIGN KEY(site, divelog_id, years) "
        "    REFERENCES dive_log(site, divelog_id, years)"
        ")"
    ))
    con.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_divers_dive "
        "ON divers(site, divelog_id, years)"
    ))
    con.execute(text(
        f"CREATE TABLE IF NOT EXISTS diver_segments ("
        f"  {seg_pk},"
        "  diver_id INTEGER NOT NULL,"
        "  seq INTEGER NOT NULL,"
        "  breathing_mix TEXT,"
        "  bar_start TEXT,"
        "  bar_end TEXT,"
        "  delta_p TEXT,"
        "  UNIQUE(diver_id, seq),"
        "  FOREIGN KEY(diver_id) REFERENCES divers(id) ON DELETE CASCADE"
        ")"
    ))
    con.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_segments_diver "
        "ON diver_segments(diver_id, seq)"
    ))


def _dive_log_has_diver_columns(con) -> bool:
    """Defensive guard: skip the data migration when dive_log lacks the
    legacy columns (e.g. a fresh schema that was never written by an old
    plugin). This makes ensure_divers_schema safe to run on any DB."""
    if con.dialect.name == "sqlite":
        rows = con.execute(text("PRAGMA table_info(dive_log)")).fetchall()
        names = {r[1] for r in rows}
    else:
        rows = con.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='dive_log'"
        )).fetchall()
        names = {r[0] for r in rows}
    required = {
        "diver_1", "diver_2", "breathing_mix",
        "time_in", "time_out", "max_depth",
        "bar_start_diver1", "bar_end_diver1", "dp_diver1",
        "bar_start_diver2", "bar_end_diver2", "dp_diver2",
    }
    return required.issubset(names)


def _insert_diver_returning_id(con, params: dict) -> int:
    """Dialect-aware INSERT. SQLite RETURNING needs 3.35+; use
    last_insert_rowid() instead so the plugin works against older
    sqlite bundles."""
    if con.dialect.name == "sqlite":
        con.execute(text(
            "INSERT INTO divers (site, divelog_id, years, diver_name, "
            "role, time_in, time_out, max_depth) "
            "VALUES (:s, :d, :y, :n, :r, :ti, :to, :md)"
        ), params)
        return int(con.execute(
            text("SELECT last_insert_rowid()")
        ).scalar_one())
    res = con.execute(text(
        "INSERT INTO divers (site, divelog_id, years, diver_name, "
        "role, time_in, time_out, max_depth) "
        "VALUES (:s, :d, :y, :n, :r, :ti, :to, :md) RETURNING id"
    ), params)
    return int(res.scalar_one())


def _migrate_dive_log_to_divers(con) -> None:
    """For each dive_log row with non-null diver_1 / diver_2, INSERT
    one row into divers (with role='lead'/'buddy') and one segment row
    pulling per-slot bar_*/dp_* values plus dive-level breathing_mix.
    additional_diver is intentionally ignored per spec.
    Idempotent via the UNIQUE on (site, divelog_id, years, diver_name)."""
    if not _dive_log_has_diver_columns(con):
        return
    rows = con.execute(text(
        "SELECT site, divelog_id, years, diver_1, diver_2, "
        "breathing_mix, time_in, time_out, max_depth, "
        "bar_start_diver1, bar_end_diver1, dp_diver1, "
        "bar_start_diver2, bar_end_diver2, dp_diver2 "
        "FROM dive_log"
    )).fetchall()
    for r in rows:
        site, dl, yr = r[0], r[1], r[2]
        if site is None or dl is None or yr is None:
            continue
        slots = [
            ("lead", r[3], r[9], r[10], r[11]),
            ("buddy", r[4], r[12], r[13], r[14]),
        ]
        for role, name, bs, be, dp in slots:
            if not name:
                continue
            existing = con.execute(text(
                "SELECT id FROM divers WHERE site=:s AND divelog_id=:d "
                "AND years=:y AND diver_name=:n"
            ), {"s": site, "d": dl, "y": yr, "n": name}).fetchone()
            if existing:
                continue
            diver_id = _insert_diver_returning_id(con, {
                "s": site, "d": dl, "y": yr, "n": name, "r": role,
                "ti": r[6], "to": r[7], "md": r[8],
            })
            con.execute(text(
                "INSERT INTO diver_segments (diver_id, seq, breathing_mix, "
                "bar_start, bar_end, delta_p) "
                "VALUES (:i, 0, :m, :bs, :be, :dp)"
            ), {"i": diver_id, "m": r[5], "bs": bs, "be": be, "dp": dp})


def _add_bottom_time_column(con) -> None:
    """v2 migration: add divers.bottom_time TEXT column for the
    issue-#45 swap (bottom_time per-diver, max_depth at dive level).
    Idempotent — silently no-ops if the column already exists."""
    if con.dialect.name == "sqlite":
        cols = {r[1] for r in con.execute(text(
            "PRAGMA table_info(divers)"
        )).fetchall()}
    else:
        cols = {r[0] for r in con.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='divers'"
        )).fetchall()}
    if "bottom_time" in cols:
        return
    try:
        con.execute(text("ALTER TABLE divers ADD COLUMN bottom_time TEXT"))
    except Exception as exc:
        print(f"[divers] add bottom_time skipped: {exc}")


def ensure_divers_schema(engine: Engine) -> None:
    """Idempotent. Safe to call on every connect; cheap when already
    migrated (one SELECT against hff_schema_version). Creates the
    divers + diver_segments tables and migrates any existing
    dive_log diver columns into the new tables on first call."""
    current = _read_version(engine, "divers")
    if current >= _TARGET_VERSION:
        return
    with engine.begin() as con:
        _create_version_table(con)
        if current < 1:
            _create_divers_tables(con)
            _migrate_dive_log_to_divers(con)
        if current < 2:
            # v1 → v2: add bottom_time column on pre-existing schemas.
            _add_bottom_time_column(con)
        _write_version(con, "divers", _TARGET_VERSION)
