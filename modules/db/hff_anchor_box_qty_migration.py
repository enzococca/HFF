"""Idempotent Anchor Nr. Box / Quantity schema fix.

Issue #57 follow-up: Elissa asked for the same Storage attributes the
Pottery form has — Nr. Box and Quantity — on the Anchor form. The Anchor
form already carried ``qty`` but had no ``box`` column, and (exactly like
pottery_table.qty) the ``qty`` column was added on live databases as
``INTEGER not null DEFAULT 1``, so a Quantity left empty could not be
stored and silently became 1.

This migration:

* adds ``anchor_table.box`` (INTEGER, NULLABLE, no default) when missing;
* drops the NOT NULL on ``anchor_table.qty`` so an empty Quantity stays
  empty. SQLite cannot relax a column constraint in place, so the table
  is rebuilt from its own DDL with the NOT NULL removed (column order,
  types and the unique constraint are preserved verbatim).

No backfill of ``box``/``qty``: records written before these fields
existed have an UNKNOWN value, and stamping a number on them would read
as real data.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine

_TARGET_VERSION = 1
_COMPONENT = "anchor_box_qty_column"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _table_exists(con, name: str) -> bool:
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


def _column_exists(con, table: str, column: str) -> bool:
    if con.dialect.name == "sqlite":
        rows = con.execute(text(f"PRAGMA table_info({table})")).fetchall()
        return any(r[1] == column for r in rows)
    row = con.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :t AND column_name = :c LIMIT 1"
        ),
        {"t": table, "c": column},
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


def _add_box_column(con) -> bool:
    """ADD COLUMN box INTEGER (nullable, no default) to anchor_table.

    Returns True if the column was added, False if it was already present
    or the table is missing.
    """
    if not _table_exists(con, "anchor_table"):
        return False
    if _column_exists(con, "anchor_table", "box"):
        return False
    con.execute(text("ALTER TABLE anchor_table ADD COLUMN box INTEGER"))
    return True


def _qty_is_not_null(con) -> bool:
    if con.dialect.name == "sqlite":
        rows = con.execute(text("PRAGMA table_info(anchor_table)")).fetchall()
        return any(r[1] == "qty" and r[3] for r in rows)
    row = con.execute(
        text(
            "SELECT is_nullable FROM information_schema.columns "
            "WHERE table_name='anchor_table' AND column_name='qty'"
        )
    ).fetchone()
    return bool(row) and str(row[0]).upper() == "NO"


def _make_qty_nullable(con) -> bool:
    """Drop the NOT NULL on anchor_table.qty (issue #57).

    Live databases got ``qty`` as ``INTEGER not null DEFAULT 1`` from the
    legacy DB_update path, so a Quantity the user leaves empty cannot be
    stored: it either fails or silently falls back to 1. SQLite cannot
    relax a column constraint in place, so the table is rebuilt from its
    own DDL with the NOT NULL removed (column order, types and the unique
    constraint are preserved verbatim).
    """
    if not _table_exists(con, "anchor_table"):
        return False
    if not _column_exists(con, "anchor_table", "qty"):
        return False
    if not _qty_is_not_null(con):
        return False
    if con.dialect.name != "sqlite":
        con.execute(text(
            "ALTER TABLE anchor_table ALTER COLUMN qty DROP NOT NULL"))
        return True
    ddl = con.execute(text(
        "SELECT sql FROM sqlite_master WHERE type='table' "
        "AND name='anchor_table'"
    )).scalar_one()
    new_ddl, subs = re.subn(
        r"(\bqty\b\s+INTEGER)\s+NOT\s+NULL", r"\1", ddl, flags=re.IGNORECASE)
    if not subs:
        return False
    columns = ", ".join(
        '"%s"' % r[1]
        for r in con.execute(text("PRAGMA table_info(anchor_table)")))
    # Modern SQLite (legacy_alter_table=OFF, the default) rewrites the
    # table name inside dependent views/triggers when a table is RENAMEd.
    # Renaming anchor_table to a temp and dropping it would therefore
    # leave pyarchinit_anchor_view pointing at the dropped temp table.
    # legacy_alter_table=ON disables the rewrite so the view keeps
    # referencing anchor_table, which exists again after the rebuild; it
    # also lets the RENAME proceed if an unrelated view is already broken.
    con.execute(text("PRAGMA legacy_alter_table=ON"))
    try:
        con.execute(text(
            "ALTER TABLE anchor_table RENAME TO _hff_anc_qty_old"))
        con.execute(text(new_ddl))
        con.execute(text(
            "INSERT INTO anchor_table (%s) SELECT %s FROM _hff_anc_qty_old"
            % (columns, columns)))
        con.execute(text("DROP TABLE _hff_anc_qty_old"))
    finally:
        con.execute(text("PRAGMA legacy_alter_table=OFF"))
    return True


def ensure_anchor_box_qty_column(engine: Engine) -> None:
    """Idempotent. Safe to call on every connect; cheap when already
    migrated (one SELECT against hff_schema_version)."""
    current = _read_version(engine, _COMPONENT)
    if current >= _TARGET_VERSION:
        return
    with engine.begin() as con:
        _create_version_table(con)
        if _add_box_column(con):
            print(
                "[hff_anchor_box_qty_migration] added anchor_table.box "
                "INTEGER (Nr. Box)"
            )
        if _make_qty_nullable(con):
            print(
                "[hff_anchor_box_qty_migration] anchor_table.qty is now "
                "nullable (empty Quantity stays empty)"
            )
        _write_version(con, _COMPONENT, _TARGET_VERSION)
