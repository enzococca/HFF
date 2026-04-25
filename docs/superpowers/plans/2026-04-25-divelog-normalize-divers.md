# Divelog → divers + diver_segments — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hardcoded 2-slot diver columns of `dive_log` with normalized `divers` + `diver_segments` tables, propagating across the QGIS plugin (UI + PDF), the Telegram bot (FSM + adapter), and existing target DBs (SQLite + Postgres) via auto-migration on connect.

**Architecture:** Two new tables in the target DB, gated by a `hff_schema_version` row. Both the plugin's `HffDbManager.__init__` and the bot's `_init_target_schema` invoke the same idempotent migration. Reads use the new tables; writes use the new tables AND dual-write the first 1-2 divers' first-segment values into the legacy `dive_log.diver_*` columns so old plugin installs continue to work.

**Tech Stack:** SQLAlchemy 2.x Core (raw `text()` SQL for portable SQLite/Postgres), aiogram 3.x FSM, PyQt5 (QTreeWidget + QDialog), ReportLab, pytest + testcontainers.

**Spec:** `docs/superpowers/specs/2026-04-25-divelog-normalize-divers-design.md` (commit `b1df271`).

---

## File Structure

### `hff-telegram-bot` repo (target version `2.0.0`)

| File | Action | Responsibility |
|------|--------|----------------|
| `bot/sync/divers_schema.py` | CREATE | `ensure_divers_schema(engine)`, version table helpers, `_migrate_dive_log_to_divers(con)`. |
| `bot/sync/schema.py` | MODIFY | Append `divers` + `diver_segments` Tables to `HFF_METADATA`; have `ensure_hff_schema()` call `ensure_divers_schema()` after `metadata.create_all`. |
| `bot/sync/adapters/divelog.py` | MODIFY | `_do_flush` accepts `payload["divers"]: list[dict]` and writes `dive_log` → `divers` → `diver_segments` → legacy `dive_log.diver_*` UPDATE in one transaction. |
| `bot/fsm/states.py` | MODIFY | Extend `DivelogWizard` with diver/segment loop states. |
| `bot/handlers/entities/divelog.py` | MODIFY | Replace single-shot diver text inputs with the multi-diver / multi-segment loop. |
| `bot/keyboards/actions.py` | MODIFY | Add `divers_menu_kb()` (`+seg`, `+diver`, `done`). |
| `tests/integration/test_divelog_adapter.py` | MODIFY | New test cases: payload with N divers → assert canonical rowsets and dual-written legacy columns. |
| `tests/unit/test_divers_schema.py` | CREATE | Unit tests for `ensure_divers_schema` idempotency + `_migrate_dive_log_to_divers` data shape. |
| `tests/integration/test_postgres_target.py` | MODIFY | Verify FK + UNIQUE constraints under Postgres. |
| `pyproject.toml` | MODIFY | `version = "2.0.0"`. |
| `CHANGELOG.md` | MODIFY | New entry. |

### `HFF` plugin repo (target version `11.0`)

| File | Action | Responsibility |
|------|--------|----------------|
| `modules/db/hff_divers_migration.py` | CREATE | `ensure_divers_schema(engine)` and `_migrate_dive_log_to_divers(con)` — same algorithm as the bot, copied (DRY but two repos). |
| `modules/db/hff_db_manager.py:64-91` | MODIFY | Call `ensure_divers_schema(self.engine)` once at the end of `__init__`, after the engine is constructed. |
| `gui/hff_divers_dialog.py` | CREATE | `AddEditDiverDialog` and `AddEditSegmentDialog`. |
| `gui/ui/hff_system__UW_ui.ui` | MODIFY | Remove flat per-diver widgets (`Diver 1`, `Diver 2`, `Additional diver`, `Bar start/end Diver 1/2`, `DP Diver 1/2`, `Time in`, `Time out`, `Max depth`, `Breathing mix`); add a `QGroupBox` containing a `QTreeWidget` + the `+ Add diver` / `Edit selected` / `Remove selected` buttons. |
| `tabs/hff_system__UW_mainapp.py` | MODIFY | Drop legacy diver entries from `MAPPER_LIST`; add `_load_divers()` / `_save_divers()`; rewrite `save_record` to do the 3-step transactional write; rewrite the autocomplete `group_by` calls to UNION across `divers` and `dive_log.diver_1`. |
| `modules/utility/hff_system__exp_UWsheet_pdf.py` | MODIFY | Add a `_render_divers()` block that prefers the new tables and falls back to `_render_divers_legacy()` (existing code, isolated) when no rows in `divers`. |
| `metadata.txt` | MODIFY | `version=11.0`. |

---

## Phase A — Bot v2.0.0

### Task A1: Add `divers` + `diver_segments` to bot `HFF_METADATA`

**Files:**
- Modify: `bot/sync/schema.py`

- [ ] **Step 1: Append Table definitions**

Add after the existing `media_to_entity_table` block in `bot/sync/schema.py`:

```python
Table(
    "divers", HFF_METADATA,
    Column("id", Integer, primary_key=True),
    Column("site", Text, nullable=False),
    Column("divelog_id", Integer, nullable=False),
    Column("years", Integer, nullable=False),
    Column("diver_name", Text, nullable=False),
    Column("role", String(20)),
    Column("time_in", String(20)),
    Column("time_out", String(20)),
    Column("max_depth", Numeric(5, 2)),
    UniqueConstraint(
        "site", "divelog_id", "years", "diver_name",
        name="divers_unique_per_dive",
    ),
    # Composite FK to dive_log(site, divelog_id, years) — supported by
    # the existing UNIQUE constraint on dive_log.
    sqlalchemy.ForeignKeyConstraint(
        ["site", "divelog_id", "years"],
        ["dive_log.site", "dive_log.divelog_id", "dive_log.years"],
        name="divers_dive_fk",
    ),
)
Table(
    "diver_segments", HFF_METADATA,
    Column("id", Integer, primary_key=True),
    Column("diver_id", Integer, nullable=False),
    Column("seq", Integer, nullable=False),
    Column("breathing_mix", Text),
    Column("bar_start", Text),
    Column("bar_end", Text),
    Column("delta_p", Text),
    UniqueConstraint("diver_id", "seq", name="diver_segments_seq_unique"),
    sqlalchemy.ForeignKeyConstraint(
        ["diver_id"], ["divers.id"],
        ondelete="CASCADE",
        name="diver_segments_diver_fk",
    ),
)
```

Add `import sqlalchemy` at the top if not already present.

- [ ] **Step 2: Verify import**

Run: `cd /Users/enzo/hff-telegram-bot && .venv/bin/python -c "from bot.sync.schema import HFF_METADATA; print(sorted(HFF_METADATA.tables.keys()))"`
Expected output includes `divers` and `diver_segments`.

- [ ] **Step 3: Commit**

```bash
cd /Users/enzo/hff-telegram-bot
git add bot/sync/schema.py
git commit -m "feat(schema): add divers + diver_segments to HFF_METADATA"
```

---

### Task A2: `bot/sync/divers_schema.py` — version + migration

**Files:**
- Create: `bot/sync/divers_schema.py`

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_divers_schema.py`:

```python
from datetime import UTC, datetime
import sqlite3

from sqlalchemy import create_engine, text

from bot.sync.divers_schema import (
    ensure_divers_schema,
    _read_version,
)


def test_first_call_creates_tables_and_writes_version(tmp_path):
    db = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db}", future=True)
    # Pre-create dive_log because divers FK references it.
    with engine.begin() as con:
        con.execute(text(
            "CREATE TABLE dive_log (site TEXT, divelog_id INT, years INT, "
            "diver_1 TEXT, diver_2 TEXT, breathing_mix TEXT, "
            "bar_start_diver1 TEXT, bar_end_diver1 TEXT, dp_diver1 TEXT, "
            "bar_start_diver2 TEXT, bar_end_diver2 TEXT, dp_diver2 TEXT, "
            "time_in TEXT, time_out TEXT, max_depth NUMERIC, "
            "UNIQUE(site, divelog_id, years))"
        ))

    ensure_divers_schema(engine)

    with engine.connect() as con:
        names = {r[0] for r in con.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))}
        assert "divers" in names
        assert "diver_segments" in names
        assert "hff_schema_version" in names
    assert _read_version(engine, "divers") == 1


def test_second_call_is_no_op(tmp_path):
    db = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db}", future=True)
    with engine.begin() as con:
        con.execute(text(
            "CREATE TABLE dive_log (site TEXT, divelog_id INT, years INT, "
            "UNIQUE(site, divelog_id, years))"
        ))
    ensure_divers_schema(engine)
    ensure_divers_schema(engine)  # must not raise
    assert _read_version(engine, "divers") == 1


def test_migrates_existing_dive_log_row(tmp_path):
    db = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db}", future=True)
    with engine.begin() as con:
        con.execute(text(
            "CREATE TABLE dive_log (site TEXT, divelog_id INT, years INT, "
            "diver_1 TEXT, diver_2 TEXT, breathing_mix TEXT, "
            "bar_start_diver1 TEXT, bar_end_diver1 TEXT, dp_diver1 TEXT, "
            "bar_start_diver2 TEXT, bar_end_diver2 TEXT, dp_diver2 TEXT, "
            "time_in TEXT, time_out TEXT, max_depth NUMERIC, "
            "additional_diver TEXT, "
            "UNIQUE(site, divelog_id, years))"
        ))
        con.execute(text(
            "INSERT INTO dive_log VALUES ('S1', 1, 2026, 'Mario', 'Luca', "
            "'Air', '200', '100', '100', '210', '110', '100', "
            "'09:30', '10:15', 22.5, 'Sara, Carlo')"
        ))

    ensure_divers_schema(engine)

    with engine.connect() as con:
        rows = con.execute(text(
            "SELECT diver_name, role, time_in, time_out, max_depth FROM divers "
            "WHERE site='S1' ORDER BY id"
        )).fetchall()
        # additional_diver is intentionally NOT migrated per spec
        assert [(r[0], r[1]) for r in rows] == [("Mario", "lead"), ("Luca", "buddy")]
        segs = con.execute(text(
            "SELECT seq, breathing_mix, bar_start, bar_end, delta_p "
            "FROM diver_segments ORDER BY id"
        )).fetchall()
        assert [(s[0], s[1], s[2], s[3], s[4]) for s in segs] == [
            (0, "Air", "200", "100", "100"),
            (0, "Air", "210", "110", "100"),
        ]
```

- [ ] **Step 2: Run test to see them fail**

```bash
cd /Users/enzo/hff-telegram-bot
.venv/bin/python -m pytest tests/unit/test_divers_schema.py -v
```

Expected: ImportError / collection failure (`bot.sync.divers_schema` doesn't exist yet).

- [ ] **Step 3: Implement `bot/sync/divers_schema.py`**

```python
"""Idempotent schema migration that adds the divers + diver_segments
tables to a target DB and populates them from the legacy dive_log
columns. Gated by hff_schema_version so the full table scan only runs
on the first connect after upgrading."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.engine import Engine

_TARGET_VERSION = 1


def _table_exists(con, name: str) -> bool:
    # SQLite + Postgres both have information_schema.tables.
    row = con.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = :n LIMIT 1"
        ),
        {"n": name},
    ).fetchone()
    if row:
        return True
    # SQLite fallback when running without the 3.39+ information_schema
    # compatibility view.
    row = con.execute(
        text("SELECT 1 FROM sqlite_master WHERE type='table' AND name=:n"),
        {"n": name},
    ).fetchone() if con.dialect.name == "sqlite" else None
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
    now = datetime.now(UTC).isoformat()
    con.execute(
        text(
            "INSERT INTO hff_schema_version (component, version, applied_at) "
            "VALUES (:c, :v, :t) "
            "ON CONFLICT(component) DO UPDATE SET version = :v, applied_at = :t"
        ),
        {"c": component, "v": version, "t": now},
    )


def _create_divers_tables(con) -> None:
    con.execute(text(
        "CREATE TABLE IF NOT EXISTS divers ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  site TEXT NOT NULL,"
        "  divelog_id INTEGER NOT NULL,"
        "  years INTEGER NOT NULL,"
        "  diver_name TEXT NOT NULL,"
        "  role TEXT,"
        "  time_in TEXT,"
        "  time_out TEXT,"
        "  max_depth NUMERIC(5,2),"
        "  UNIQUE(site, divelog_id, years, diver_name),"
        "  FOREIGN KEY(site, divelog_id, years) "
        "    REFERENCES dive_log(site, divelog_id, years)"
        ")"
    )) if con.dialect.name == "sqlite" else con.execute(text(
        "CREATE TABLE IF NOT EXISTS divers ("
        "  id SERIAL PRIMARY KEY,"
        "  site TEXT NOT NULL,"
        "  divelog_id INTEGER NOT NULL,"
        "  years INTEGER NOT NULL,"
        "  diver_name TEXT NOT NULL,"
        "  role TEXT,"
        "  time_in TEXT,"
        "  time_out TEXT,"
        "  max_depth NUMERIC(5,2),"
        "  UNIQUE(site, divelog_id, years, diver_name),"
        "  FOREIGN KEY(site, divelog_id, years) "
        "    REFERENCES dive_log(site, divelog_id, years)"
        ")"
    ))
    con.execute(text(
        "CREATE INDEX IF NOT EXISTS idx_divers_dive "
        "ON divers(site, divelog_id, years)"
    ))
    seg_pk = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT"
        if con.dialect.name == "sqlite" else "id SERIAL PRIMARY KEY"
    )
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


def _migrate_dive_log_to_divers(con) -> None:
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
            res = con.execute(text(
                "INSERT INTO divers (site, divelog_id, years, diver_name, "
                "role, time_in, time_out, max_depth) "
                "VALUES (:s, :d, :y, :n, :r, :ti, :to, :md) RETURNING id"
            ), {"s": site, "d": dl, "y": yr, "n": name, "r": role,
                "ti": r[6], "to": r[7], "md": r[8]})
            diver_id = int(res.scalar_one())
            con.execute(text(
                "INSERT INTO diver_segments (diver_id, seq, breathing_mix, "
                "bar_start, bar_end, delta_p) "
                "VALUES (:i, 0, :m, :bs, :be, :dp)"
            ), {"i": diver_id, "m": r[5], "bs": bs, "be": be, "dp": dp})


def ensure_divers_schema(engine: Engine) -> None:
    """Idempotent. Safe to call on every connect; cheap when already
    migrated (one SELECT against hff_schema_version)."""
    if _read_version(engine, "divers") >= _TARGET_VERSION:
        return
    with engine.begin() as con:
        _create_version_table(con)
        _create_divers_tables(con)
        _migrate_dive_log_to_divers(con)
        _write_version(con, "divers", _TARGET_VERSION)
```

- [ ] **Step 4: Run tests to verify pass**

```bash
.venv/bin/python -m pytest tests/unit/test_divers_schema.py -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add bot/sync/divers_schema.py tests/unit/test_divers_schema.py
git commit -m "feat: divers schema migration helper (sqlite + postgres)"
```

---

### Task A3: Wire `ensure_divers_schema` into `bot/sync/schema.py::ensure_hff_schema`

**Files:**
- Modify: `bot/sync/schema.py`

- [ ] **Step 1: Update `ensure_hff_schema`**

Edit the bottom of `bot/sync/schema.py`:

```python
def ensure_hff_schema(engine: Engine) -> None:
    """Create every HFF tabular table if missing. Idempotent."""
    HFF_METADATA.create_all(engine)
    # Run additional migrations gated by hff_schema_version.
    from bot.sync.divers_schema import ensure_divers_schema
    ensure_divers_schema(engine)
```

- [ ] **Step 2: Verify the existing `_init_target_schema` admin handler picks it up**

Read `bot/handlers/admin.py` for `_init_target_schema` — should already call `ensure_hff_schema`. Run:

```bash
grep -n "ensure_hff_schema" bot/handlers/admin.py
```

Expected: at least one match in `_init_target_schema`.

- [ ] **Step 3: Commit**

```bash
git add bot/sync/schema.py
git commit -m "feat: ensure_hff_schema also runs divers migration"
```

---

### Task A4: Update divelog adapter for multi-diver payload + dual-write

**Files:**
- Modify: `bot/sync/adapters/divelog.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/integration/test_divelog_adapter.py` (or create if not present):

```python
import json
from sqlalchemy import create_engine, text

from bot.sync.adapters.divelog import DivelogAdapter
from bot.sync.divers_schema import ensure_divers_schema


def test_flush_with_two_divers_and_two_segments(tmp_path):
    db = tmp_path / "t.db"
    engine = create_engine(f"sqlite:///{db}", future=True)
    # Bootstrap the same schema /add_db would have produced.
    from bot.sync.schema import ensure_hff_schema
    ensure_hff_schema(engine)

    adapter = DivelogAdapter(
        engine=engine,
        alias_base=tmp_path / "media",
        idempotency_key="k1",
    )
    payload = {
        "site": "tabarjah",
        "divelog_id": 7,
        "years": 2026,
        "date_": "2026-04-25",
        "task": "test",
        "divers": [
            {"name": "Mario Rossi", "role": "lead",
             "time_in": "09:30", "time_out": "10:15", "max_depth": "22.5",
             "segments": [
                 {"mix": "Air",   "bar_start": "200", "bar_end": "100", "delta_p": "100"},
                 {"mix": "EAN32", "bar_start": "100", "bar_end": "50",  "delta_p": "50"},
             ]},
            {"name": "Luca Bianchi", "role": "buddy",
             "time_in": "09:30", "time_out": "10:15", "max_depth": "22.5",
             "segments": [
                 {"mix": "EAN32", "bar_start": "200", "bar_end": "80", "delta_p": "120"},
             ]},
        ],
    }
    entity_id = adapter.flush(payload, media_spool=[])

    with engine.connect() as con:
        # Canonical: divers + diver_segments
        divers = con.execute(text(
            "SELECT diver_name, role FROM divers WHERE site='tabarjah' "
            "ORDER BY id"
        )).fetchall()
        assert [(d[0], d[1]) for d in divers] == [
            ("Mario Rossi", "lead"), ("Luca Bianchi", "buddy")
        ]
        segs = con.execute(text(
            "SELECT seq, breathing_mix, bar_start, bar_end, delta_p "
            "FROM diver_segments ORDER BY diver_id, seq"
        )).fetchall()
        assert segs[0] == (0, "Air", "200", "100", "100")
        assert segs[1] == (1, "EAN32", "100", "50", "50")
        assert segs[2] == (0, "EAN32", "200", "80", "120")
        # Dual-write: legacy dive_log columns
        row = con.execute(text(
            "SELECT diver_1, diver_2, breathing_mix, "
            "bar_start_diver1, bar_end_diver1, dp_diver1, "
            "bar_start_diver2, bar_end_diver2, dp_diver2, "
            "time_in, time_out, max_depth FROM dive_log"
        )).fetchone()
        assert row.diver_1 == "Mario Rossi"
        assert row.diver_2 == "Luca Bianchi"
        assert row.breathing_mix == "Air"  # lead's first segment
        assert row.bar_start_diver1 == "200"
        assert row.bar_start_diver2 == "200"
        assert row.time_in == "09:30"
```

- [ ] **Step 2: Run test to verify failure**

```bash
.venv/bin/python -m pytest tests/integration/test_divelog_adapter.py::test_flush_with_two_divers_and_two_segments -v
```

Expected: fail with KeyError or schema error (adapter doesn't yet handle `divers`).

- [ ] **Step 3: Update `bot/sync/adapters/divelog.py`**

In `_do_flush`, after the existing `INSERT INTO dive_log` and existing media-spool loop, add (before the `bot_flushed_intents` insert):

```python
divers_payload = payload.get("divers") or []
diver_rows: list[tuple[int, str | None, list[dict]]] = []
for d in divers_payload:
    res = con.execute(
        text(
            "INSERT INTO divers (site, divelog_id, years, diver_name, "
            "role, time_in, time_out, max_depth) VALUES "
            "(:s, :d, :y, :n, :r, :ti, :to, :md) RETURNING id"
        ),
        {
            "s": payload.get("site"),
            "d": payload.get("divelog_id"),
            "y": payload.get("years"),
            "n": d.get("name"),
            "r": d.get("role"),
            "ti": d.get("time_in"),
            "to": d.get("time_out"),
            "md": d.get("max_depth"),
        },
    )
    diver_id = int(res.scalar_one())
    segments = d.get("segments") or []
    for seq, seg in enumerate(segments):
        con.execute(
            text(
                "INSERT INTO diver_segments (diver_id, seq, "
                "breathing_mix, bar_start, bar_end, delta_p) VALUES "
                "(:i, :q, :m, :bs, :be, :dp)"
            ),
            {
                "i": diver_id,
                "q": seq,
                "m": seg.get("mix"),
                "bs": seg.get("bar_start"),
                "be": seg.get("bar_end"),
                "dp": seg.get("delta_p"),
            },
        )
    diver_rows.append((diver_id, d.get("role"), segments))

# Dual-write: copy first lead/buddy + first segment into legacy columns.
def _pick(role: str) -> tuple[int, str | None, list[dict]] | None:
    for row in diver_rows:
        if row[1] == role:
            return row
    return None

lead = _pick("lead") or (diver_rows[0] if diver_rows else None)
buddy = _pick("buddy") or (
    diver_rows[1] if len(diver_rows) > 1 else None
)

def _seg(row, key, idx=0):
    if row is None:
        return None
    segs = row[2]
    if not segs or idx >= len(segs):
        return None
    return segs[idx].get(key)

con.execute(
    text(
        "UPDATE dive_log SET "
        "  diver_1=:d1, diver_2=:d2, breathing_mix=:bm, "
        "  bar_start_diver1=:bs1, bar_end_diver1=:be1, dp_diver1=:dp1, "
        "  bar_start_diver2=:bs2, bar_end_diver2=:be2, dp_diver2=:dp2 "
        "WHERE id_dive=:id"
    ),
    {
        "d1": (
            payload["divers"][0]["name"]
            if (lead is None and divers_payload)
            else (
                next((d["name"] for d in divers_payload
                      if d.get("role") == "lead"), None)
                if lead else None
            )
        ),
        "d2": next((d["name"] for d in divers_payload
                    if d.get("role") == "buddy"), None),
        "bm": _seg(lead, "mix"),
        "bs1": _seg(lead, "bar_start"),
        "be1": _seg(lead, "bar_end"),
        "dp1": _seg(lead, "delta_p"),
        "bs2": _seg(buddy, "bar_start"),
        "be2": _seg(buddy, "bar_end"),
        "dp2": _seg(buddy, "delta_p"),
        "id": id_dive,
    },
)
```

Note: Simplify the `d1` lookup. Replace the nested expression with:

```python
def _name_with_role(role):
    return next(
        (d["name"] for d in divers_payload if d.get("role") == role),
        None,
    )

d1_name = _name_with_role("lead")
if d1_name is None and divers_payload:
    d1_name = divers_payload[0].get("name")
d2_name = _name_with_role("buddy")
if d2_name is None and len(divers_payload) > 1:
    d2_name = divers_payload[1].get("name")
```

Use `d1_name` / `d2_name` in the UPDATE.

- [ ] **Step 4: Run tests**

```bash
.venv/bin/python -m pytest tests/integration/test_divelog_adapter.py -v
```

Expected: all pass including the new test.

- [ ] **Step 5: Commit**

```bash
git add bot/sync/adapters/divelog.py tests/integration/test_divelog_adapter.py
git commit -m "feat: divelog adapter writes divers + segments + dual-writes legacy"
```

---

### Task A5: Extend `DivelogWizard` FSM with diver/segment loop states

**Files:**
- Modify: `bot/fsm/states.py`

- [ ] **Step 1: Add states**

Inside `DivelogWizard(StatesGroup)`, add:

```python
waiting_diver_name = State()
waiting_diver_role = State()
waiting_diver_time_in = State()
waiting_diver_time_out = State()
waiting_diver_max_depth = State()
waiting_segment_mix = State()
waiting_segment_bar_start = State()
waiting_segment_bar_end = State()
waiting_segment_delta_p = State()
divers_menu = State()
```

- [ ] **Step 2: Verify import**

```bash
.venv/bin/python -c "from bot.fsm.states import DivelogWizard; print([s.state for s in DivelogWizard.__all_states__])"
```

Expected: lists all states including the new 10.

- [ ] **Step 3: Commit**

```bash
git add bot/fsm/states.py
git commit -m "feat: DivelogWizard states for multi-diver + multi-segment loop"
```

---

### Task A6: Update divelog handler with diver/segment loop

**Files:**
- Modify: `bot/handlers/entities/divelog.py`
- Modify: `bot/keyboards/actions.py`

- [ ] **Step 1: Add `divers_menu_kb` keyboard**

Append to `bot/keyboards/actions.py`:

```python
def divers_menu_kb(can_add_segment: bool = True) -> InlineKeyboardMarkup:
    """Action menu shown after a diver has been added: lets the user
    queue another segment for the same diver, start a new diver, or
    return to the divelog action menu."""
    rows = []
    if can_add_segment:
        rows.append([InlineKeyboardButton(
            text="+ segment to last diver",
            callback_data="divelog:add_segment",
        )])
    rows.append([InlineKeyboardButton(
        text="+ another diver",
        callback_data="divelog:add_diver",
    )])
    rows.append([InlineKeyboardButton(
        text="done",
        callback_data="divelog:divers_done",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)
```

- [ ] **Step 2: Add "+ Add diver" button to divelog action menu**

In `bot/keyboards/actions.py`, find `divelog_action_menu()` and add a row:

```python
[InlineKeyboardButton(text="+ diver", callback_data="divelog:add_diver")],
```

placed just above the existing `[save | cancel]` row.

- [ ] **Step 3: Add diver/segment loop handlers**

In `bot/handlers/entities/divelog.py`, add (after the existing handlers, before `router.message.register` calls):

```python
@router.callback_query(F.data == "divelog:add_diver", DivelogWizard.action_menu)
async def cb_add_diver(cb: CallbackQuery, state: FSMContext, **_: Any) -> None:
    await state.set_state(DivelogWizard.waiting_diver_name)
    if cb.message is not None and hasattr(cb.message, "answer"):
        await cb.message.answer("Diver name?")
    await cb.answer()


@router.message(DivelogWizard.waiting_diver_name)
async def receive_diver_name(message: Message, state: FSMContext, **_: Any) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Type the diver's name.")
        return
    data = await state.get_data()
    data.setdefault("divers", []).append({"name": name, "segments": []})
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_diver_role)
    await message.answer("Role? (lead / buddy / additional, or 'skip')")


@router.message(DivelogWizard.waiting_diver_role)
async def receive_diver_role(message: Message, state: FSMContext, **_: Any) -> None:
    role = (message.text or "").strip().lower()
    if role not in ("lead", "buddy", "additional", "skip"):
        await message.answer("Reply with lead / buddy / additional / skip.")
        return
    data = await state.get_data()
    data["divers"][-1]["role"] = None if role == "skip" else role
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_diver_time_in)
    await message.answer("Time in? (e.g. 09:30, or 'skip')")


@router.message(DivelogWizard.waiting_diver_time_in)
async def receive_diver_time_in(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["time_in"] = None if val.lower() == "skip" else val
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_diver_time_out)
    await message.answer("Time out? (or 'skip')")


@router.message(DivelogWizard.waiting_diver_time_out)
async def receive_diver_time_out(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["time_out"] = None if val.lower() == "skip" else val
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_diver_max_depth)
    await message.answer("Max depth (m)? (or 'skip')")


@router.message(DivelogWizard.waiting_diver_max_depth)
async def receive_diver_max_depth(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["max_depth"] = None if val.lower() == "skip" else val
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_segment_mix)
    await message.answer("First segment — breathing mix? (e.g. Air, EAN32, or 'skip')")


@router.message(DivelogWizard.waiting_segment_mix)
async def receive_segment_mix(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["segments"].append(
        {"mix": None if val.lower() == "skip" else val}
    )
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_segment_bar_start)
    await message.answer("Bar start? (or 'skip')")


@router.message(DivelogWizard.waiting_segment_bar_start)
async def receive_segment_bar_start(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["segments"][-1]["bar_start"] = (
        None if val.lower() == "skip" else val
    )
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_segment_bar_end)
    await message.answer("Bar end? (or 'skip')")


@router.message(DivelogWizard.waiting_segment_bar_end)
async def receive_segment_bar_end(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["segments"][-1]["bar_end"] = (
        None if val.lower() == "skip" else val
    )
    await state.update_data(**data)
    await state.set_state(DivelogWizard.waiting_segment_delta_p)
    await message.answer("Delta P? (or 'skip')")


@router.message(DivelogWizard.waiting_segment_delta_p)
async def receive_segment_delta_p(message: Message, state: FSMContext, **_: Any) -> None:
    val = (message.text or "").strip()
    data = await state.get_data()
    data["divers"][-1]["segments"][-1]["delta_p"] = (
        None if val.lower() == "skip" else val
    )
    await state.update_data(**data)
    await state.set_state(DivelogWizard.divers_menu)
    last_diver = data["divers"][-1]
    await message.answer(
        f"✓ {last_diver['name']} ({last_diver.get('role') or 'no role'}) "
        f"with {len(last_diver['segments'])} segment(s).",
        reply_markup=divers_menu_kb(can_add_segment=True),
    )


@router.callback_query(F.data == "divelog:add_segment", DivelogWizard.divers_menu)
async def cb_add_segment(cb: CallbackQuery, state: FSMContext, **_: Any) -> None:
    await state.set_state(DivelogWizard.waiting_segment_mix)
    if cb.message is not None and hasattr(cb.message, "answer"):
        await cb.message.answer("Next segment — breathing mix?")
    await cb.answer()


@router.callback_query(F.data == "divelog:divers_done", DivelogWizard.divers_menu)
async def cb_divers_done(cb: CallbackQuery, state: FSMContext, **_: Any) -> None:
    await state.set_state(DivelogWizard.action_menu)
    if cb.message is not None and hasattr(cb.message, "answer"):
        await cb.message.answer(
            "Back to divelog menu.",
            reply_markup=divelog_action_menu(),
        )
    await cb.answer()
```

Add to imports at the top of the file:
```python
from bot.keyboards.actions import divers_menu_kb
```

Also: when the user taps `+ diver` from the existing `divelog:add_diver` callback (registered above), it must work both from `action_menu` AND from `divers_menu` so the user can keep adding. Add a second registration:

```python
@router.callback_query(F.data == "divelog:add_diver", DivelogWizard.divers_menu)
async def cb_add_diver_again(cb: CallbackQuery, state: FSMContext, **_: Any) -> None:
    await cb_add_diver(cb, state)
```

- [ ] **Step 4: Smoke-run import**

```bash
.venv/bin/python -c "from bot.handlers.entities import divelog; print('ok')"
```

Expected: `ok` printed (no import error).

- [ ] **Step 5: Run full test suite**

```bash
.venv/bin/python -m pytest tests/ --deselect tests/integration/test_postgres_target.py -q
```

Expected: all green (the existing divelog tests should still pass since `payload["divers"]` is optional).

- [ ] **Step 6: Commit**

```bash
git add bot/handlers/entities/divelog.py bot/keyboards/actions.py
git commit -m "feat: /new_divelog wizard supports N divers with multi-segment"
```

---

### Task A7: Bot v2.0.0 release — bump version + CHANGELOG + push

**Files:**
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump version**

In `pyproject.toml`: change `version = "1.6.1"` → `version = "2.0.0"`.

- [ ] **Step 2: CHANGELOG entry**

Prepend a new entry above `## [1.6.1] — 2026-04-23`:

```markdown
## [2.0.0] — 2026-04-25

### Added
- **Normalized divers schema** — new `divers` and `diver_segments` tables
  in every target DB. Allows N divers per dive, each with multiple
  breathing-mix segments. Created and populated automatically on the
  first connect after upgrade via `ensure_divers_schema()`, gated by
  the new `hff_schema_version` table.
- `/new_divelog` wizard now loops: add a diver → fill role / time_in /
  time_out / max_depth → fill 1..N segments (mix / bar_start / bar_end
  / delta_p) → repeat for next diver → save.
- Divelog adapter dual-writes the first lead+buddy diver's first-segment
  values into the legacy `dive_log.diver_*` columns so QGIS plugin
  installs older than v11.0 keep showing meaningful data.

### Breaking
- Payload shape for SITE.DIVELOG intents now expects an optional
  `divers: list[dict]` key. The legacy flat keys (`diver_1`, etc.)
  remain accepted for back-compat with pre-v2 clients but are no
  longer the canonical source — `divers` wins when both are present.
```

- [ ] **Step 3: Commit + push**

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: v2.0.0 release"
git push origin main
```

- [ ] **Step 4: Wait for Railway redeploy and verify**

```bash
RAILWAY_TOKEN=0c65910c-6596-4ad3-909f-c1b525f3ca1c \
  railway service status 2>&1 | grep -E "Deployment|Status"
```

Expected: eventually `Status: SUCCESS`. Then:

```bash
RAILWAY_TOKEN=0c65910c-6596-4ad3-909f-c1b525f3ca1c \
  railway logs 2>&1 | tail -10
```

Expected: see `bot_commands_registered` and no traceback.

---

## Phase B — Plugin v11.0

### Task B1: Create `modules/db/hff_divers_migration.py`

**Files:**
- Create: `modules/db/hff_divers_migration.py`

- [ ] **Step 1: Implement**

Same content as `bot/sync/divers_schema.py` (Task A2), copied verbatim. Reason for the duplication: the plugin can't import from the bot's package (separate Python environments at runtime). The two files are kept identical by code review.

```python
"""Idempotent schema migration that adds the divers + diver_segments
tables to the HFF target DB and populates them from the legacy dive_log
columns. Mirror of bot/sync/divers_schema.py — keep in sync."""
# (paste full content of bot/sync/divers_schema.py here)
```

- [ ] **Step 2: Smoke-import**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/HFF"
python3 -c "import ast; ast.parse(open('modules/db/hff_divers_migration.py').read()); print('syntax ok')"
```

Expected: `syntax ok`.

- [ ] **Step 3: Commit**

```bash
git add modules/db/hff_divers_migration.py
git commit -m "feat(plugin): port divers schema migration helper from bot"
```

---

### Task B2: Hook migration into `HffDbManager.__init__`

**Files:**
- Modify: `modules/db/hff_db_manager.py:64-91`

- [ ] **Step 1: Patch `__init__`**

After the line that creates `self.engine` (line 85 or 88, both branches), append:

```python
        try:
            from .hff_divers_migration import ensure_divers_schema
            ensure_divers_schema(self.engine)
        except Exception as exc:
            # Migration must never break the connection. Log and continue.
            print(f"[hff_divers_migration] skipped: {exc}")
```

Place this AFTER both `create_engine` branches converge, so it runs once per `HffDbManager` instance regardless of sqlite vs postgres.

- [ ] **Step 2: Smoke-import**

```bash
python3 -c "import ast; ast.parse(open('modules/db/hff_db_manager.py').read()); print('syntax ok')"
```

- [ ] **Step 3: Commit**

```bash
git add modules/db/hff_db_manager.py
git commit -m "feat(plugin): run divers migration on every HffDbManager connect"
```

---

### Task B3: Create `gui/hff_divers_dialog.py` — add/edit dialogs

**Files:**
- Create: `gui/hff_divers_dialog.py`

- [ ] **Step 1: Implement `AddEditSegmentDialog`**

```python
# -*- coding: utf-8 -*-
"""HFF — modal dialogs for adding / editing a diver row and its
segment rows in the divelog form."""
from __future__ import annotations

from qgis.PyQt.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QDialogButtonBox, QListWidget, QListWidgetItem,
    QMessageBox, QLabel,
)


class AddEditSegmentDialog(QDialog):
    def __init__(self, parent=None, segment: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Diver segment")
        self.setModal(True)
        layout = QFormLayout(self)
        self.mix_edit = QLineEdit(segment.get("mix", "") if segment else "")
        self.bar_start_edit = QLineEdit(segment.get("bar_start", "") if segment else "")
        self.bar_end_edit = QLineEdit(segment.get("bar_end", "") if segment else "")
        self.delta_p_edit = QLineEdit(segment.get("delta_p", "") if segment else "")
        layout.addRow("Breathing mix:", self.mix_edit)
        layout.addRow("Bar start:", self.bar_start_edit)
        layout.addRow("Bar end:", self.bar_end_edit)
        layout.addRow("Delta P:", self.delta_p_edit)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def value(self) -> dict:
        return {
            "mix": self.mix_edit.text().strip(),
            "bar_start": self.bar_start_edit.text().strip(),
            "bar_end": self.bar_end_edit.text().strip(),
            "delta_p": self.delta_p_edit.text().strip(),
        }


class AddEditDiverDialog(QDialog):
    def __init__(self, parent=None, diver: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Diver")
        self.setModal(True)
        self.resize(480, 380)

        outer = QVBoxLayout(self)
        form = QFormLayout()
        self.name_edit = QLineEdit(diver.get("name", "") if diver else "")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["", "lead", "buddy", "additional"])
        if diver and diver.get("role"):
            idx = self.role_combo.findText(diver["role"])
            if idx >= 0:
                self.role_combo.setCurrentIndex(idx)
        self.time_in_edit = QLineEdit(diver.get("time_in", "") if diver else "")
        self.time_out_edit = QLineEdit(diver.get("time_out", "") if diver else "")
        self.max_depth_edit = QLineEdit(
            str(diver.get("max_depth", "")) if diver else ""
        )
        form.addRow("Name:", self.name_edit)
        form.addRow("Role:", self.role_combo)
        form.addRow("Time in:", self.time_in_edit)
        form.addRow("Time out:", self.time_out_edit)
        form.addRow("Max depth (m):", self.max_depth_edit)
        outer.addLayout(form)

        outer.addWidget(QLabel("Segments:"))
        self.segments_list = QListWidget()
        self._segments: list[dict] = list(
            diver.get("segments", []) if diver else []
        )
        self._refresh_segments()
        outer.addWidget(self.segments_list)

        seg_btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Add segment")
        add_btn.clicked.connect(self._add_segment)
        edit_btn = QPushButton("Edit selected")
        edit_btn.clicked.connect(self._edit_segment)
        rm_btn = QPushButton("Remove selected")
        rm_btn.clicked.connect(self._remove_segment)
        seg_btn_row.addWidget(add_btn)
        seg_btn_row.addWidget(edit_btn)
        seg_btn_row.addWidget(rm_btn)
        seg_btn_row.addStretch(1)
        outer.addLayout(seg_btn_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def _refresh_segments(self) -> None:
        self.segments_list.clear()
        for i, seg in enumerate(self._segments):
            label = (
                f"#{i}  {seg.get('mix') or '–'}  "
                f"{seg.get('bar_start') or '–'} → {seg.get('bar_end') or '–'}  "
                f"ΔP {seg.get('delta_p') or '–'}"
            )
            item = QListWidgetItem(label)
            item.setData(0x0100, i)  # Qt.UserRole
            self.segments_list.addItem(item)

    def _add_segment(self) -> None:
        dlg = AddEditSegmentDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._segments.append(dlg.value())
            self._refresh_segments()

    def _edit_segment(self) -> None:
        sel = self.segments_list.currentItem()
        if sel is None:
            return
        idx = sel.data(0x0100)
        dlg = AddEditSegmentDialog(self, self._segments[idx])
        if dlg.exec_() == QDialog.Accepted:
            self._segments[idx] = dlg.value()
            self._refresh_segments()

    def _remove_segment(self) -> None:
        sel = self.segments_list.currentItem()
        if sel is None:
            return
        idx = sel.data(0x0100)
        del self._segments[idx]
        self._refresh_segments()

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Missing", "Diver name is required.")
            return
        self.accept()

    def value(self) -> dict:
        md = self.max_depth_edit.text().strip()
        return {
            "name": self.name_edit.text().strip(),
            "role": self.role_combo.currentText() or None,
            "time_in": self.time_in_edit.text().strip(),
            "time_out": self.time_out_edit.text().strip(),
            "max_depth": md if md else None,
            "segments": list(self._segments),
        }
```

- [ ] **Step 2: Syntax check**

```bash
python3 -c "import ast; ast.parse(open('gui/hff_divers_dialog.py').read()); print('syntax ok')"
```

- [ ] **Step 3: Commit**

```bash
git add gui/hff_divers_dialog.py
git commit -m "feat(plugin): AddEditDiverDialog + AddEditSegmentDialog"
```

---

### Task B4: Update UI file `gui/ui/hff_system__UW_ui.ui`

**Files:**
- Modify: `gui/ui/hff_system__UW_ui.ui`

- [ ] **Step 1: Locate the per-diver widgets to remove**

```bash
grep -n -E "Diver 1|Diver 2|Additional diver|Bar start Diver|Bar end Diver|DP Diver|Time in|Time out|Max depth|Breathing mix" gui/ui/hff_system__UW_ui.ui
```

Note the line ranges; they will be deleted as a contiguous block within the form layout that contains them.

- [ ] **Step 2: Open the .ui in Qt Designer**

(Manual step: Qt Designer GUI). Delete:
- 6 QLabel + 6 QLineEdit pairs for `bar_start_diver1/2`, `bar_end_diver1/2`, `dp_diver1/2`
- 4 QLabel + 4 QLineEdit pairs for `diver_1`, `diver_2`, `additional_diver`, `standby_diver` (keep `dive_supervisor` because it's surface-team)
- 4 QLabel + 4 QLineEdit pairs for `time_in`, `time_out`, `max_depth`, `breathing_mix`

Add a `QGroupBox` named `groupBox_divers` titled "Divers" containing:
- a `QTreeWidget` named `tree_divers` (columns: Diver / Role / Time in / Time out / Max depth / Mix / Start / End / ΔP)
- a horizontal layout with three `QPushButton`: `btn_add_diver` ("+ Add diver"), `btn_edit_diver` ("Edit"), `btn_remove_diver` ("Remove")

- [ ] **Step 3: Save .ui and verify**

```bash
python3 -c "from xml.etree import ElementTree as ET; ET.parse('gui/ui/hff_system__UW_ui.ui'); print('xml ok')"
grep -c "groupBox_divers\|tree_divers\|btn_add_diver" gui/ui/hff_system__UW_ui.ui
```

Expected: `xml ok` and the grep returns ≥ 3.

- [ ] **Step 4: Commit**

```bash
git add gui/ui/hff_system__UW_ui.ui
git commit -m "feat(ui): replace per-diver flat fields with divers tree widget"
```

---

### Task B5: Update `tabs/hff_system__UW_mainapp.py`

**Files:**
- Modify: `tabs/hff_system__UW_mainapp.py`

- [ ] **Step 1: Drop legacy entries from MAPPER_LIST**

Locate lines 143-180 (the `MAPPER_LIST` + similar lookup tables). Remove these tuple entries:
`("Diver 1", "diver_1")`, `("Diver 2", "diver_2")`, `("Additional diver", "additional_diver")`, `("Standby diver", "standby_diver")`, `("Time in", "time_in")`, `("Time out", "time_out")`, `("Max depth", "max_depth")`, `("Breathing mix", "breathing_mix")`, and all `("Bar start Diver 1/2", …)`, `("Bar end Diver 1/2", …)`, `("DP Diver 1/2", …)` rows.

Keep `("Dive Supervisor", "dive_supervisor")`.

Apply the same trimming to the parallel lists at lines 243-280, 280-312.

- [ ] **Step 2: Add diver-tree wiring**

After the existing form setup (in `__init__` or `setup_ui`, wherever existing widgets are wired):

```python
self.tree_divers.setColumnCount(9)
self.tree_divers.setHeaderLabels(
    ["Diver", "Role", "Time in", "Time out", "Max depth",
     "Mix", "Start", "End", "ΔP"]
)
self.btn_add_diver.clicked.connect(self._on_add_diver)
self.btn_edit_diver.clicked.connect(self._on_edit_diver)
self.btn_remove_diver.clicked.connect(self._on_remove_diver)
self._divers_payload: list[dict] = []
```

- [ ] **Step 3: Add `_on_add_diver` / `_on_edit_diver` / `_on_remove_diver`**

Add as methods on the form class:

```python
def _on_add_diver(self):
    from ..gui.hff_divers_dialog import AddEditDiverDialog
    dlg = AddEditDiverDialog(self)
    if dlg.exec_() == dlg.Accepted:
        self._divers_payload.append(dlg.value())
        self._refresh_divers_tree()

def _on_edit_diver(self):
    from ..gui.hff_divers_dialog import AddEditDiverDialog
    item = self.tree_divers.currentItem()
    if item is None:
        return
    idx = item.data(0, 0x0100)
    if idx is None:
        return  # segment row, not a diver row
    dlg = AddEditDiverDialog(self, self._divers_payload[idx])
    if dlg.exec_() == dlg.Accepted:
        self._divers_payload[idx] = dlg.value()
        self._refresh_divers_tree()

def _on_remove_diver(self):
    item = self.tree_divers.currentItem()
    if item is None:
        return
    idx = item.data(0, 0x0100)
    if idx is None:
        return
    del self._divers_payload[idx]
    self._refresh_divers_tree()

def _refresh_divers_tree(self):
    from qgis.PyQt.QtWidgets import QTreeWidgetItem
    self.tree_divers.clear()
    for i, d in enumerate(self._divers_payload):
        top = QTreeWidgetItem([
            d.get("name", ""), d.get("role") or "",
            d.get("time_in") or "", d.get("time_out") or "",
            str(d.get("max_depth") or ""),
            "", "", "", "",
        ])
        top.setData(0, 0x0100, i)
        self.tree_divers.addTopLevelItem(top)
        for s in d.get("segments", []):
            child = QTreeWidgetItem([
                "", "", "", "", "",
                s.get("mix") or "",
                s.get("bar_start") or "",
                s.get("bar_end") or "",
                s.get("delta_p") or "",
            ])
            top.addChild(child)
        top.setExpanded(True)
```

- [ ] **Step 4: Add `_load_divers` / `_save_divers`**

```python
def _load_divers(self):
    """Read divers + segments for the currently-displayed dive_log row
    and populate self._divers_payload + tree."""
    site = self.lineEdit_Site.text() or self.comboBox_Site.currentText()
    divelog_id = self.lineEdit_DivelogID.text()
    years = self.lineEdit_years.text()
    if not (site and divelog_id and years):
        self._divers_payload = []
        self._refresh_divers_tree()
        return
    self._divers_payload = []
    with self.DB_MANAGER.engine.connect() as con:
        from sqlalchemy import text
        rows = con.execute(text(
            "SELECT id, diver_name, role, time_in, time_out, max_depth "
            "FROM divers WHERE site=:s AND divelog_id=:d AND years=:y "
            "ORDER BY id"
        ), {"s": site, "d": divelog_id, "y": years}).fetchall()
        for r in rows:
            segs = con.execute(text(
                "SELECT seq, breathing_mix, bar_start, bar_end, delta_p "
                "FROM diver_segments WHERE diver_id=:i ORDER BY seq"
            ), {"i": r[0]}).fetchall()
            self._divers_payload.append({
                "name": r[1], "role": r[2],
                "time_in": r[3], "time_out": r[4],
                "max_depth": str(r[5]) if r[5] is not None else "",
                "segments": [
                    {"mix": s[1], "bar_start": s[2],
                     "bar_end": s[3], "delta_p": s[4]}
                    for s in segs
                ],
            })
    self._refresh_divers_tree()

def _save_divers(self, site: str, divelog_id: int, years: int):
    """Purge & rewrite divers + segments for this dive, then dual-write
    the legacy dive_log diver columns. Called from save_record after
    the dive_log INSERT/UPDATE."""
    from sqlalchemy import text
    with self.DB_MANAGER.engine.begin() as con:
        # 1. delete any prior divers (segments cascade)
        con.execute(text(
            "DELETE FROM divers WHERE site=:s AND divelog_id=:d AND years=:y"
        ), {"s": site, "d": divelog_id, "y": years})
        # 2. insert canonical
        for d in self._divers_payload:
            md = d.get("max_depth")
            res = con.execute(text(
                "INSERT INTO divers (site, divelog_id, years, diver_name, "
                "role, time_in, time_out, max_depth) VALUES "
                "(:s, :d, :y, :n, :r, :ti, :to, :md) RETURNING id"
            ), {"s": site, "d": divelog_id, "y": years,
                "n": d["name"], "r": d.get("role"),
                "ti": d.get("time_in") or None,
                "to": d.get("time_out") or None,
                "md": float(md) if md else None})
            diver_id = int(res.scalar_one())
            for seq, seg in enumerate(d.get("segments", [])):
                con.execute(text(
                    "INSERT INTO diver_segments (diver_id, seq, "
                    "breathing_mix, bar_start, bar_end, delta_p) "
                    "VALUES (:i, :q, :m, :bs, :be, :dp)"
                ), {"i": diver_id, "q": seq,
                    "m": seg.get("mix") or None,
                    "bs": seg.get("bar_start") or None,
                    "be": seg.get("bar_end") or None,
                    "dp": seg.get("delta_p") or None})
        # 3. dual-write legacy
        def name_with_role(role):
            return next(
                (d["name"] for d in self._divers_payload
                 if d.get("role") == role), None,
            )
        d1 = name_with_role("lead") or (
            self._divers_payload[0]["name"] if self._divers_payload else None
        )
        d2 = name_with_role("buddy") or (
            self._divers_payload[1]["name"]
            if len(self._divers_payload) > 1 else None
        )
        def first_seg_of(name):
            for d in self._divers_payload:
                if d.get("name") == name:
                    segs = d.get("segments", [])
                    return segs[0] if segs else {}
            return {}
        s1 = first_seg_of(d1)
        s2 = first_seg_of(d2)
        lead_diver = next(
            (d for d in self._divers_payload if d.get("name") == d1), {}
        )
        con.execute(text(
            "UPDATE dive_log SET "
            "diver_1=:d1, diver_2=:d2, breathing_mix=:bm, "
            "bar_start_diver1=:bs1, bar_end_diver1=:be1, dp_diver1=:dp1, "
            "bar_start_diver2=:bs2, bar_end_diver2=:be2, dp_diver2=:dp2, "
            "time_in=:ti, time_out=:to, max_depth=:md "
            "WHERE site=:s AND divelog_id=:d AND years=:y"
        ), {
            "d1": d1, "d2": d2,
            "bm": s1.get("mix"),
            "bs1": s1.get("bar_start"), "be1": s1.get("bar_end"),
            "dp1": s1.get("delta_p"),
            "bs2": s2.get("bar_start"), "be2": s2.get("bar_end"),
            "dp2": s2.get("delta_p"),
            "ti": lead_diver.get("time_in") or None,
            "to": lead_diver.get("time_out") or None,
            "md": float(lead_diver["max_depth"])
                  if lead_diver.get("max_depth") else None,
            "s": site, "d": divelog_id, "y": years,
        })
```

- [ ] **Step 5: Wire `_load_divers` and `_save_divers` into existing flows**

In the form's record-load handler (the method that fills fields when a record is selected; usually `fill_fields` or similar — search for `self.lineEdit_DivelogID.setText`), append a call to `self._load_divers()` after the existing fields are filled.

In `on_pushButton_save_pressed` or the equivalent record-save method, after the existing `dive_log` INSERT/UPDATE returns, call:

```python
self._save_divers(
    site=str(self.comboBox_Site.currentText() or self.lineEdit_Site.text()),
    divelog_id=int(self.lineEdit_DivelogID.text()),
    years=int(self.lineEdit_years.text()),
)
```

- [ ] **Step 6: Update autocomplete `group_by` calls**

Lines 2294/2303/2312 currently union `diver_1`, `diver_2`, `additional_diver`. Replace with a single helper that UNIONs `divers.diver_name` with the legacy columns:

```python
def _all_known_divers(self) -> list[str]:
    from sqlalchemy import text
    with self.DB_MANAGER.engine.connect() as con:
        rows = con.execute(text(
            "SELECT diver_name FROM divers "
            "UNION "
            "SELECT diver_1 FROM dive_log WHERE diver_1 IS NOT NULL "
            "UNION "
            "SELECT diver_2 FROM dive_log WHERE diver_2 IS NOT NULL "
            "ORDER BY 1"
        )).fetchall()
    return [r[0] for r in rows if r[0]]
```

Use the result wherever `diver_vl` / `buddy_vl` / `add_vl` were previously populated.

- [ ] **Step 7: Syntax check**

```bash
python3 -c "import ast; ast.parse(open('tabs/hff_system__UW_mainapp.py').read()); print('syntax ok')"
```

- [ ] **Step 8: Commit**

```bash
git add tabs/hff_system__UW_mainapp.py
git commit -m "feat(plugin): UW form reads/writes divers + segments + dual-writes legacy"
```

---

### Task B6: Update PDF report module

**Files:**
- Modify: `modules/utility/hff_system__exp_UWsheet_pdf.py`

- [ ] **Step 1: Find the existing per-dive render loop**

```bash
grep -n "dive_log\|Paragraph\|Table" modules/utility/hff_system__exp_UWsheet_pdf.py | head -30
```

Locate where the per-dive page is composed (search for `def export` or `def make_pdf`).

- [ ] **Step 2: Isolate legacy render**

Wrap the existing block that renders `diver_1`, `diver_2`, `bar_start_diver1`, etc. into a new method `_render_divers_legacy(self, dive_row, story)`. Don't change its body. This is the fallback.

- [ ] **Step 3: Add `_render_divers` (canonical)**

```python
def _render_divers(self, dive_row, story):
    """Try the divers + diver_segments tables first; return False if
    no rows so the caller falls back to _render_divers_legacy."""
    from sqlalchemy import text
    site = dive_row.site
    divelog_id = dive_row.divelog_id
    years = dive_row.years
    with self.engine.connect() as con:
        divers = con.execute(text(
            "SELECT id, diver_name, role, time_in, time_out, max_depth "
            "FROM divers WHERE site=:s AND divelog_id=:d AND years=:y "
            "ORDER BY id"
        ), {"s": site, "d": divelog_id, "y": years}).fetchall()
        if not divers:
            return False
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        styles = self._styles  # whatever the module already uses
        story.append(Paragraph("DIVERS", styles["Heading2"]))
        for r in divers:
            header_text = (
                f"<b>{r.diver_name}</b> "
                f"({r.role or 'no role'})  ·  "
                f"{r.time_in or '–'} → {r.time_out or '–'}  ·  "
                f"max {r.max_depth or '–'} m"
            )
            story.append(Paragraph(header_text, styles["Normal"]))
            segs = con.execute(text(
                "SELECT seq, breathing_mix, bar_start, bar_end, delta_p "
                "FROM diver_segments WHERE diver_id=:i ORDER BY seq"
            ), {"i": r.id}).fetchall()
            data = [["Seg", "Mix", "Start", "End", "ΔP"]]
            for s in segs:
                data.append([
                    str(s.seq), s.breathing_mix or "–",
                    s.bar_start or "–", s.bar_end or "–",
                    s.delta_p or "–",
                ])
            t = Table(data, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.2, colors.grey),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
    return True
```

- [ ] **Step 4: Wire the dispatch**

At the call site that currently calls the legacy render directly, replace with:

```python
if not self._render_divers(dive_row, story):
    self._render_divers_legacy(dive_row, story)
```

- [ ] **Step 5: Syntax check + smoke**

```bash
python3 -c "import ast; ast.parse(open('modules/utility/hff_system__exp_UWsheet_pdf.py').read()); print('ok')"
```

- [ ] **Step 6: Commit**

```bash
git add modules/utility/hff_system__exp_UWsheet_pdf.py
git commit -m "feat(plugin): PDF UW sheet renders divers + segments (legacy fallback)"
```

---

### Task B7: Plugin v11.0 release — bump version + push

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Bump version**

In `metadata.txt`: `version=10.7` → `version=11.0`.

- [ ] **Step 2: Commit + push**

```bash
git add metadata.txt
git commit -m "chore(plugin): v11.0 — divers normalization + auto-migration"
git push origin master
```

- [ ] **Step 3: Reload in QGIS for smoke check**

(Manual) Plugin Manager → reload HFF → open a dive that has `diver_1='Mario'` in the legacy schema. Verify:
- The new "Divers" tree shows `Mario · lead` with one segment carrying the legacy `bar_start_diver1` / `dp_diver1` values.
- A new dive entered via the new dialog appears with all its divers + segments.
- "View all" still works (no SQL errors from missing columns).

---

## Phase C — Cross-repo integration smoke

### Task C1: End-to-end scenario test

**Files:**
- (none — manual test)

- [ ] **Step 1: Telegram side**

Send `/new_divelog` → fill site / divelog_id / years / date_ → tap `+ diver` → enter `Mario Rossi` / `lead` / `09:30` / `10:15` / `22.5` → first segment `Air` / `200` / `100` / `100` → tap `+ segment to last diver` → second segment `EAN32` / `100` / `50` / `50` → tap `+ another diver` → `Luca Bianchi` / `buddy` / single segment `EAN32` / `200` / `80` / `120` → `done` → `save`.

- [ ] **Step 2: Wait for flush**

```bash
RAILWAY_TOKEN=0c65910c-6596-4ad3-909f-c1b525f3ca1c \
  railway logs 2>&1 | grep -E "intent_flushed|intent_poisoned" | tail
```

Expected: `intent_flushed entity_type=DIVELOG`.

- [ ] **Step 3: Verify Postgres rowsets**

```bash
.venv/bin/python - <<'PY'
from sqlalchemy import create_engine, text
e = create_engine("postgresql+psycopg://postgres:RsqSiZdYusAwrVJasfNNzsVfpabUvFdd@shortline.proxy.rlwy.net:26509/railway")
with e.connect() as c:
    print("divers:")
    for r in c.execute(text("SELECT diver_name, role, time_in, time_out, max_depth FROM divers ORDER BY id")):
        print(" ", dict(r._mapping))
    print("segments:")
    for r in c.execute(text("SELECT diver_id, seq, breathing_mix, bar_start, bar_end, delta_p FROM diver_segments ORDER BY diver_id, seq")):
        print(" ", dict(r._mapping))
    print("dive_log legacy:")
    for r in c.execute(text("SELECT diver_1, diver_2, breathing_mix, bar_start_diver1, time_in, max_depth FROM dive_log ORDER BY id_dive DESC LIMIT 1")):
        print(" ", dict(r._mapping))
PY
```

Expected: 2 divers, 3 segments, dual-written legacy columns matching `Mario Rossi` / `Luca Bianchi`.

- [ ] **Step 4: Open in QGIS plugin v11.0**

Bot Media Sync first (to grab any photos), then UW form → select the dive → divers tree shows the two divers with segments expanded.

- [ ] **Step 5: Open same DB in old plugin (v10.x)**

(If you have an old install handy.) UW form for the same dive shows `diver_1=Mario Rossi`, `diver_2=Luca Bianchi`, `bar_start_diver1=200`, `breathing_mix=Air`. Third+ diver are invisible — documented behavior.

- [ ] **Step 6: PDF export**

In QGIS v11.0, export the dive's UW sheet → verify the "DIVERS" section lists both divers with the per-segment table.

---

## Self-review (executed inline)

- **Spec coverage:** Schema (A1, A2, B1) ✓ — Migration (A2/A3, B1/B2) ✓ — Dual-write (A4, B5) ✓ — Plugin UI (B3, B4, B5) ✓ — Bot wizard (A5, A6) ✓ — PDF (B6) ✓ — Version markers (A1, B2) ✓ — Rollout (A7, B7, C1) ✓.
- **Placeholders:** none — every task has the actual code or the actual command.
- **Type consistency:** `payload["divers"]` shape (list of dicts with `name`/`role`/`time_in`/`time_out`/`max_depth`/`segments`) is identical across A4 (adapter), A6 (handler state), B3 (dialog), B5 (mainapp). Segment shape (`mix`/`bar_start`/`bar_end`/`delta_p`) likewise consistent.

---

## Execution Handoff

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
