"""Idempotent addition of pottery_table.qty column.

v11.12 introduces a Quantity field on the Pottery form (issue #48).
The Python layer (POTTERY entity, POTTERY_table mapper, insert_pottery_values,
TABLE_FIELDS, lineEdit_qty in the .ui) has been carrying `qty` for a while,
and the bundled SQLite template already had the column — but databases
created from schema.sql before v11.12 (and live user databases on either
SQLite or PostgreSQL) do not. This migration adds it with DEFAULT 1 so
historical rows get a sensible value and the form's empty-text fallback
(qty = 1) stays consistent.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine

_TARGET_VERSION = 1
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
    """ADD COLUMN qty INTEGER DEFAULT 1 to pottery_table. Returns True
    if the column was added, False if it was already present or the
    table is missing. Safe on both SQLite and PostgreSQL: SQLite ALTER
    rewrites every row with the default; PostgreSQL is metadata-only."""
    if not _table_exists(con, "pottery_table"):
        return False
    if _column_exists(con, "pottery_table", "qty"):
        return False
    con.execute(text(
        "ALTER TABLE pottery_table ADD COLUMN qty INTEGER DEFAULT 1"
    ))
    con.execute(text(
        "UPDATE pottery_table SET qty = 1 WHERE qty IS NULL"
    ))
    return True


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
        _write_version(con, _COMPONENT, _TARGET_VERSION)
