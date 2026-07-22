"""Idempotent media stable-identity migration (issue #58 follow-up).

The integer ``media_table.id_media`` is renumbered by every import
(``max_num_id + 1``), so it cannot be used to recognise "the same media"
across databases -- which is the root of the tagged-photo problems in
issues #57 / #58 (the wrong image gets linked once the numbering drifts).

This migration adds two stable identifiers to ``media_table`` and backfills
them on existing SQLite and PostgreSQL databases:

* ``media_uuid``   -- a random uuid4 (hex), assigned once and copied verbatim
  on export/import, so a media created in one database keeps ONE identity
  everywhere it travels;
* ``media_sha256`` -- the sha256 of the file content, which is deterministic,
  so the SAME photo hashes to the SAME value in two databases even when they
  were populated independently (this is what lets already-diverged databases
  be reconciled). Rows whose file is missing on disk are left NULL.

New databases already get the columns from the table definition; this only
backfills databases that predate the columns. Runs once (version-gated).
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.engine import Engine

_TARGET_VERSION = 1
_COMPONENT = "media_identity"


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
        text("SELECT 1 FROM information_schema.tables "
             "WHERE table_name = :n LIMIT 1"),
        {"n": name},
    ).fetchone()
    return row is not None


def _column_exists(con, table: str, column: str) -> bool:
    if con.dialect.name == "sqlite":
        rows = con.execute(text(f"PRAGMA table_info({table})")).fetchall()
        return any(r[1] == column for r in rows)
    row = con.execute(
        text("SELECT 1 FROM information_schema.columns "
             "WHERE table_name = :t AND column_name = :c LIMIT 1"),
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


def _add_column(con, column: str) -> bool:
    """ADD COLUMN <column> TEXT (nullable) to media_table. Returns True if it
    was added, False if already present or the table is missing."""
    if not _table_exists(con, "media_table"):
        return False
    if _column_exists(con, "media_table", column):
        return False
    con.execute(text("ALTER TABLE media_table ADD COLUMN %s TEXT" % column))
    return True


def _sha256_of_file(path) -> str | None:
    try:
        if not path or not os.path.isfile(path):
            return None
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _backfill(con) -> tuple:
    """Fill media_uuid (always) and media_sha256 (when the file is readable)
    for rows that lack them. Returns (uuid_count, sha_count)."""
    if not _table_exists(con, "media_table"):
        return 0, 0
    rows = con.execute(text(
        "SELECT id_media, filepath, media_uuid, media_sha256 FROM media_table"
    )).fetchall()
    uuid_n = sha_n = 0
    for r in rows:
        id_media, filepath, media_uuid, media_sha256 = r[0], r[1], r[2], r[3]
        new_uuid = media_uuid or uuid.uuid4().hex
        new_sha = media_sha256 or _sha256_of_file(filepath)
        if new_uuid != media_uuid or new_sha != media_sha256:
            try:
                con.execute(
                    text("UPDATE media_table SET media_uuid=:u, media_sha256=:s "
                         "WHERE id_media=:i"),
                    {"u": new_uuid, "s": new_sha, "i": id_media},
                )
                if new_uuid != media_uuid:
                    uuid_n += 1
                if new_sha and new_sha != media_sha256:
                    sha_n += 1
            except Exception:
                # one unreadable/locked file must not abort the whole backfill
                pass
    return uuid_n, sha_n


def ensure_media_identity_columns(engine: Engine) -> None:
    """Idempotent. Safe to call on every connect; cheap when already migrated
    (one SELECT against hff_schema_version)."""
    current = _read_version(engine, _COMPONENT)
    if current >= _TARGET_VERSION:
        return
    with engine.begin() as con:
        _create_version_table(con)
        added = []
        if _add_column(con, "media_uuid"):
            added.append("media_uuid")
        if _add_column(con, "media_sha256"):
            added.append("media_sha256")
        if added:
            print("[hff_media_identity_migration] added media_table columns: %s"
                  % ", ".join(added))
        uuid_n, sha_n = _backfill(con)
        if uuid_n or sha_n:
            print("[hff_media_identity_migration] backfilled %d uuid(s), "
                  "%d sha256 hash(es)" % (uuid_n, sha_n))
        _write_version(con, _COMPONENT, _TARGET_VERSION)
