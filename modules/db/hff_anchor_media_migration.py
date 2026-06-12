"""Idempotent normalization of media_to_entity_table.entity_type for
anchor media linked via the Anchor form.

Pre-11.10 the ANC form inserted rows with entity_type='ANC', but the
global Image_viewer, Images_directory_export, and the MEDIAVIEW SQL
all use entity_type='ANCHORS'. Result: media uploaded via the Anchor
form became invisible when navigating back to the record. v11.10 fixes
the form code itself; this migration rewrites pre-existing rows so the
preview also recovers historical uploads.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine

_TARGET_VERSION = 1
_COMPONENT = "anchor_media_entity_type"


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


def _rename_anc_to_anchors(con) -> int:
    """UPDATE media_to_entity_table SET entity_type='ANCHORS'
    WHERE entity_type='ANC' AND table_name='anchor_table'.
    Returns rows affected (0 on a clean DB). Scoped to table_name to
    avoid touching any unrelated 'ANC' rows that may exist for other
    purposes."""
    if not _table_exists(con, "media_to_entity_table"):
        return 0
    res = con.execute(text(
        "UPDATE media_to_entity_table "
        "SET entity_type='ANCHORS' "
        "WHERE entity_type='ANC' AND table_name='anchor_table'"
    ))
    try:
        return int(res.rowcount or 0)
    except Exception:
        return 0


def ensure_anchor_media_entity_type(engine: Engine) -> None:
    """Idempotent. Safe to call on every connect; cheap when already
    migrated (one SELECT against hff_schema_version)."""
    current = _read_version(engine, _COMPONENT)
    if current >= _TARGET_VERSION:
        return
    with engine.begin() as con:
        _create_version_table(con)
        affected = _rename_anc_to_anchors(con)
        if affected:
            print(
                "[hff_anchor_media_migration] normalized %d "
                "media_to_entity_table row(s): 'ANC' -> 'ANCHORS'"
                % affected
            )
        _write_version(con, _COMPONENT, _TARGET_VERSION)
