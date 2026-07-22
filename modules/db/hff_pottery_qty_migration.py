"""Idempotent addition of pottery_table.qty column.

v11.12 introduces a Quantity field on the Pottery form (issue #48).
The Python layer (POTTERY entity, POTTERY_table mapper, insert_pottery_values,
TABLE_FIELDS, lineEdit_qty in the .ui) has been carrying `qty` for a while,
and the bundled SQLite template already had the column — but databases
created from schema.sql before v11.12 (and live user databases on either
SQLite or PostgreSQL) do not. This migration adds it.

v2 (issue #57): the column must also accept NULL. The shipped SQLite
template declares it `not null DEFAULT 1`, so a Quantity left empty was
stored as 1 — the reason every record in the field databases reads
Quantity 1. The NOT NULL is dropped here, and the column is no longer
added with a DEFAULT/backfill of 1 on databases that still lack it.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine

# v2 (issue #57): the column must also be NULLABLE — an empty Quantity
# has to stay empty instead of falling back to the DEFAULT 1.
# v3 (issue #57 follow-up): the v2 SQLite rebuild renamed pottery_table
# without legacy_alter_table=ON and so left pyarchinit_pot_view dangling;
# v3 rebuilds view-safely and repairs any view already broken by v2.
_TARGET_VERSION = 3
_COMPONENT = "pottery_qty_column"


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


def _add_qty_column(con) -> bool:
    """ADD COLUMN qty INTEGER to pottery_table. Returns True if the
    column was added, False if it was already present or the table is
    missing.

    No DEFAULT and no backfill (changed for issue #57): records written
    before the Quantity field existed have an UNKNOWN quantity, and
    stamping 1 on them made every historical record read as "one item".
    """
    if not _table_exists(con, "pottery_table"):
        return False
    if _column_exists(con, "pottery_table", "qty"):
        return False
    con.execute(text("ALTER TABLE pottery_table ADD COLUMN qty INTEGER"))
    return True


def _qty_is_not_null(con) -> bool:
    if con.dialect.name == "sqlite":
        rows = con.execute(text("PRAGMA table_info(pottery_table)")).fetchall()
        return any(r[1] == "qty" and r[3] for r in rows)
    row = con.execute(
        text(
            "SELECT is_nullable FROM information_schema.columns "
            "WHERE table_name='pottery_table' AND column_name='qty'"
        )
    ).fetchone()
    return bool(row) and str(row[0]).upper() == "NO"


def _make_qty_nullable(con) -> bool:
    """Drop the NOT NULL on pottery_table.qty (issue #57).

    The shipped SQLite template declares `qty INTEGER not null DEFAULT 1`,
    so a Quantity the user leaves empty cannot be stored: it either fails
    or silently falls back to 1 — which is why every record in the field
    databases carries Quantity 1. SQLite cannot relax a column constraint
    in place, so the table is rebuilt from its own DDL with the NOT NULL
    removed (column order, types and the unique constraint are preserved
    verbatim; pottery_table carries no user index nor trigger).
    """
    if not _table_exists(con, "pottery_table"):
        return False
    if not _qty_is_not_null(con):
        return False
    if con.dialect.name != "sqlite":
        con.execute(text(
            "ALTER TABLE pottery_table ALTER COLUMN qty DROP NOT NULL"))
        return True
    ddl = con.execute(text(
        "SELECT sql FROM sqlite_master WHERE type='table' "
        "AND name='pottery_table'"
    )).scalar_one()
    new_ddl, subs = re.subn(
        r"(\bqty\b\s+INTEGER)\s+NOT\s+NULL", r"\1", ddl, flags=re.IGNORECASE)
    if not subs:
        return False
    columns = ", ".join(
        '"%s"' % r[1]
        for r in con.execute(text("PRAGMA table_info(pottery_table)")))
    # Modern SQLite (legacy_alter_table=OFF, the default) rewrites the
    # table name inside dependent views/triggers when a table is RENAMEd.
    # Renaming pottery_table to a temp and dropping it would therefore
    # leave pyarchinit_pot_view pointing at the dropped temp table. With
    # legacy_alter_table=ON the rewrite is disabled, so the view keeps
    # referencing pottery_table, which exists again after the rebuild.
    con.execute(text("PRAGMA legacy_alter_table=ON"))
    try:
        con.execute(text("ALTER TABLE pottery_table RENAME TO _hff_qty_old"))
        con.execute(text(new_ddl))
        con.execute(text(
            "INSERT INTO pottery_table (%s) SELECT %s FROM _hff_qty_old"
            % (columns, columns)))
        con.execute(text("DROP TABLE _hff_qty_old"))
    finally:
        con.execute(text("PRAGMA legacy_alter_table=OFF"))
    return True


def _repair_rebuild_views(con) -> bool:
    """Heal views/triggers broken by the v2 rebuild (issue #57).

    v2 rebuilt pottery_table without legacy_alter_table=ON, so on SQLite
    the RENAME rewrote pyarchinit_pot_view to reference the temporary
    ``_hff_qty_old`` table, which was then dropped — leaving the view
    dangling ("no such table: _hff_qty_old"). A dangling view is silent
    until the next ALTER TABLE ... RENAME, which then fails. Rewrite the
    stale reference back to pottery_table and recreate the object.
    """
    if con.dialect.name != "sqlite":
        return False
    rows = con.execute(text(
        "SELECT type, name, sql FROM sqlite_master "
        "WHERE type IN ('view', 'trigger') "
        "AND sql LIKE '%_hff_qty_old%'"
    )).fetchall()
    repaired = False
    for typ, name, sql_text in rows:
        fixed = re.sub(r"\b_hff_qty_old\b", "pottery_table", sql_text or "")
        con.execute(text('DROP %s IF EXISTS "%s"' % (typ.upper(), name)))
        con.execute(text(fixed))
        repaired = True
        print(
            "[hff_pottery_qty_migration] repaired %s %s broken by the v2 "
            "rebuild" % (typ, name)
        )
    return repaired


def ensure_pottery_qty_column(engine: Engine) -> None:
    """Idempotent. Safe to call on every connect; cheap when already
    migrated (one SELECT against hff_schema_version)."""
    current = _read_version(engine, _COMPONENT)
    if current >= _TARGET_VERSION:
        return
    with engine.begin() as con:
        _create_version_table(con)
        added = _add_qty_column(con)
        if added:
            print(
                "[hff_pottery_qty_migration] added pottery_table.qty "
                "INTEGER DEFAULT 1"
            )
        if _make_qty_nullable(con):
            print(
                "[hff_pottery_qty_migration] pottery_table.qty is now "
                "nullable (empty Quantity stays empty)"
            )
        # heal pyarchinit_pot_view if the v2 rebuild left it dangling
        _repair_rebuild_views(con)
        _write_version(con, _COMPONENT, _TARGET_VERSION)
