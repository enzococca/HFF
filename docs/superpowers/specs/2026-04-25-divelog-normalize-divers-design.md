# Design — Normalize divelog into divers + diver_segments

**Date:** 2026-04-25
**Scope:** schema migration + plugin UI + bot wizard + PDF report
**Repos affected:** `HFF` (QGIS plugin), `hff-telegram-bot`
**Driver:** the existing `dive_log` row encodes diver information in
hardcoded slots (`diver_1`, `diver_2`, `additional_diver`,
`bar_start_diver1/2`, `bar_end_diver1/2`, `dp_diver1/2`,
`breathing_mix`, `time_in/out`, `max_depth`). This caps a dive at two
"first-class" divers, ties per-diver gas / pressure data to two slots,
and cannot represent a diver who switches breathing mix mid-dive.

## Goals

1. Allow N (≥0) divers per dive, each with their own time_in / time_out
   / max_depth.
2. Allow each diver to have multiple **segments** (mix changes) within
   the same dive, each with its own breathing_mix / bar_start / bar_end
   / delta_p.
3. Survive in mixed-version environments: old plugin installs must keep
   working without forced upgrade.
4. Auto-migrate existing `dive_log` rows the first time a new
   plugin / bot connects to a target DB (SQLite or Postgres).
5. New PDF reports render the multi-diver data; old reports still work
   as a fallback when no `divers` rows exist for a dive.

## Non-goals

- Migrate or surface `additional_diver` in the new UI. The legacy text
  column stays in `dive_log` for the old plugin to read; the new plugin
  ignores it.
- Restructure `dive_log` itself. Every legacy column stays — the old
  plugin keeps writing/reading them as before.
- Track per-segment time/depth profiles. Segments capture only mix +
  pressure + ΔP, not depth/time samples.

## Schema (target DB — SQLite + Postgres)

Two new tables plus a versioning table. Existing tables untouched.

```sql
CREATE TABLE divers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- SERIAL on Postgres
    site        TEXT     NOT NULL,
    divelog_id  INTEGER  NOT NULL,
    years       INTEGER  NOT NULL,
    diver_name  TEXT     NOT NULL,
    role        TEXT,                          -- 'lead' | 'buddy' | 'additional'
    time_in     TEXT,
    time_out    TEXT,
    max_depth   NUMERIC(5,2),
    FOREIGN KEY (site, divelog_id, years)
        REFERENCES dive_log(site, divelog_id, years),
    UNIQUE(site, divelog_id, years, diver_name)
);
CREATE INDEX idx_divers_dive ON divers(site, divelog_id, years);

CREATE TABLE diver_segments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    diver_id      INTEGER NOT NULL,
    seq           INTEGER NOT NULL,           -- 0, 1, 2 …
    breathing_mix TEXT,
    bar_start     TEXT,
    bar_end       TEXT,
    delta_p       TEXT,
    FOREIGN KEY (diver_id) REFERENCES divers(id) ON DELETE CASCADE,
    UNIQUE(diver_id, seq)
);
CREATE INDEX idx_segments_diver ON diver_segments(diver_id, seq);

CREATE TABLE hff_schema_version (
    component  TEXT PRIMARY KEY,               -- e.g. 'divers'
    version    INTEGER NOT NULL,
    applied_at TEXT NOT NULL                   -- ISO 8601
);
```

The `(site, divelog_id, years)` composite FK works because `dive_log`
already declares
`UNIQUE(divelog_id, years, site) AS DIVELOG_id_unico`. SQLite enforces
composite FKs when `PRAGMA foreign_keys = ON`; both stores already set
that pragma at connection time.

`role` is intentionally free-form (no `CHECK` constraint). Validation
lives at the app layer — schema-level validation would punish migrations
that surface unexpected legacy values.

## Auto-migration

Triggered every time a plugin or the bot connects to a target DB.
Gated by the version table so a fully-migrated DB pays only the cost of
a single `SELECT version FROM hff_schema_version`.

```python
def ensure_divers_schema(engine) -> None:
    if not _table_exists(engine, "hff_schema_version"):
        _create_version_table(engine)            # idempotent CREATE IF NOT EXISTS
    current = _read_version(engine, "divers")    # 0 if row absent
    target = 1
    if current >= target:
        return
    with engine.begin() as con:
        _create_divers_table(con)                # CREATE IF NOT EXISTS
        _create_diver_segments_table(con)
        _migrate_dive_log_to_divers(con)
        _write_version(con, "divers", target, datetime.now(UTC).isoformat())
```

`_migrate_dive_log_to_divers` is itself idempotent (the
`UNIQUE(site, divelog_id, years, diver_name)` index makes
re-running safe), but the version gate avoids the full table scan on
every connect:

```
for row in dive_log:
    site, divelog_id, years = row.site, row.divelog_id, row.years

    if row.diver_1:
        divers_id = INSERT INTO divers (
            site, divelog_id, years,
            diver_name = row.diver_1,
            role       = 'lead',
            time_in    = row.time_in,
            time_out   = row.time_out,
            max_depth  = row.max_depth,
        ) ON CONFLICT (site, divelog_id, years, diver_name) DO NOTHING
          RETURNING id
        if divers_id is not None:
            INSERT INTO diver_segments (
                diver_id      = divers_id,
                seq           = 0,
                breathing_mix = row.breathing_mix,
                bar_start     = row.bar_start_diver1,
                bar_end       = row.bar_end_diver1,
                delta_p       = row.dp_diver1,
            )

    # diver_2 — analog with role='buddy' and *_diver2 fields
    # additional_diver — ignored (per Non-goals)
```

**On-demand migration**: when the new plugin opens a single dive whose
`divers` rowset is empty but whose `dive_log.diver_1` is non-null (case:
old plugin wrote a new row after the global migration ran), the same
function is called scoped to that single `(site, divelog_id, years)`.
Cost: at most two INSERTs.

## Dual-write (new plugin / bot → DB)

When the new plugin or the bot saves a dive, three writes happen in
the same transaction:

1. UPSERT `dive_log` (canonical for dive-level fields, including the
   columns that are still meaningful: `task`, `result`, `dive_supervisor`,
   `surface_interval`, `bottom_time`, weather, etc.).
2. INSERT into `divers` and `diver_segments` (canonical for per-diver
   data).
3. UPDATE `dive_log` legacy diver columns (`diver_1`, `diver_2`,
   `bar_start_diver1/2`, `bar_end_diver1/2`, `dp_diver1/2`,
   `breathing_mix`, `time_in`, `time_out`, `max_depth`) so the **old
   plugin** sees the first two divers' first-segment data when it opens
   the same DB.

**Ordering rules** for picking "diver_1" vs "diver_2":
- diver_1 = the diver whose `role='lead'`, else the first inserted
  (lowest `divers.id`).
- diver_2 = the diver whose `role='buddy'`, else the second inserted.
- If only one diver exists, all `*_diver2` legacy columns are set to
  NULL.
- Divers beyond the second are **invisible to the old plugin**. This
  is documented to the user.

**Read path** (new plugin / bot adapter): always from `divers` +
`diver_segments`. The legacy diver columns are never read by new code.

## Plugin UI

`gui/ui/hff_system__UW_ui.ui` loses every field listed under
*Goals → driver* above. They are replaced by one `QGroupBox` "Divers"
containing a `QTreeWidget`:

- outer level = one row per diver, label
  `"<name> · <role> · <time_in> → <time_out> · max <max_depth> m"`
- inner level (expandable) = one row per segment,
  `"seg <seq> │ <mix> │ <bar_start> → <bar_end> │ ΔP <delta_p>"`
- buttons under the tree: **+ Add diver**, **Edit selected**,
  **Remove selected**

"+ Add diver" / "Edit selected" open a small modal `QDialog` with a
`QFormLayout` (name, role combo, time_in, time_out, max_depth) plus a
mini-list of segments with its own add/edit dialog.

`tabs/hff_system__UW_mainapp.py` changes:

- The `MAPPER_LIST` tuples (current lines ~143-180) drop the per-diver
  flat entries and gain one synthetic `("Divers", "_divers_widget")`
  for the routing logic.
- `save_record` writes in the order described in *Dual-write* above.
- Reads at form open: `SELECT * FROM divers WHERE site=? AND
  divelog_id=? AND years=?` joined with `diver_segments`. If empty
  and `dive_log.diver_1` is non-null, the on-demand migration runs for
  that one dive and the read repeats.
- Autocomplete on the diver-name field unions
  `SELECT DISTINCT diver_name FROM divers` with
  `SELECT DISTINCT diver_1 FROM dive_log` so old data is still
  suggested.

## Bot wizard

`bot/handlers/entities/divelog.py` and `bot/fsm/states.py` extend
`DivelogWizard` with the new states:

```
waiting_diver_name        → ciclo per diver
waiting_diver_role
waiting_diver_time_in
waiting_diver_time_out
waiting_diver_max_depth
waiting_segment_mix       → ciclo per segment dentro un diver
waiting_segment_bar_start
waiting_segment_bar_end
waiting_segment_delta_p
divers_menu               → bottoni inline: +seg / +diver / done
```

In the action menu of `/new_divelog` a button **+ Add diver** enters
the loop. After `delta_p` the bot lands at the
inline `divers_menu`:

```
✓ Diver Mario Rossi (lead) added with 1 segment.
[ + Add segment to Mario ]   [ + Add another diver ]   [ Done ]
```

`Done` returns to the divelog action menu (where the existing **save**
button lives — same `cb_save` that promotes DRAFT → PENDING per v1.5).

State accumulates the divers in `data["divers"]`:

```python
data["divers"] = [
    {"name": "Mario Rossi", "role": "lead",
     "time_in": "09:30", "time_out": "10:15", "max_depth": "22.5",
     "segments": [
         {"mix": "Air",   "bar_start": "200", "bar_end": "100", "delta_p": "100"},
         {"mix": "EAN32", "bar_start": "100", "bar_end": "50",  "delta_p": "50"},
     ]},
    ...
]
```

`bot/sync/adapters/divelog.py` consumes `payload["divers"]`:

1. INSERT into `dive_log` returning `id_dive` (as today).
2. For each diver dict: INSERT into `divers` returning `id`, then
   INSERT each segment into `diver_segments` with the right
   `diver_id`+`seq`.
3. UPDATE `dive_log` legacy columns (dual-write rules above).

All in one transaction. Idempotency via `bot_flushed_intents` is
unchanged: a retry finds the row and short-circuits.

## PDF report

`modules/utility/hff_system__exp_UWsheet_pdf.py` adds a "Divers"
section after the existing dive-level fields. For each diver row from
the new tables:

```
DIVERS
═══════════════════════════════════════════════════════════════════
<name> (<role>)               <time_in> → <time_out>     max <max> m
   Seg 0 │ <mix> │ <start> → <end> │ ΔP <delta_p>
   Seg 1 │ ...
```

Layout: one ReportLab `Table` for the diver header, one nested
`Table` for the segment list. Falls through to the existing legacy
render when `divers` returns 0 rows for the dive — so PDFs of dives
that have never been opened by the new plugin (and so never migrated
on-demand) still render with the old layout.

## Code organization

**Plugin (`HFF` repo)**:
- `modules/db/hff_divers_migration.py` (new) — `ensure_divers_schema()`,
  `_migrate_dive_log_to_divers()`, version table helpers. Imported
  from `hff_system__conn_strings.Connection.conn_str()` so every
  connection performs the gate check.
- `gui/ui/hff_system__UW_ui.ui` — surgical removal of legacy diver
  widgets, addition of the `QGroupBox` + `QTreeWidget` + buttons.
- `tabs/hff_system__UW_mainapp.py` — adapt MAPPER_LIST, save_record,
  read-on-open, autocomplete unions.
- `gui/hff_divers_dialog.py` (new) — small modal dialog for
  add/edit-diver and add/edit-segment.
- `modules/utility/hff_system__exp_UWsheet_pdf.py` — new diver
  rendering, legacy fallback isolated as `_render_divers_legacy()`.
- `metadata.txt` version → 11.0 (major because of UI removal).

**Bot (`hff-telegram-bot` repo)**:
- `bot/sync/divers_schema.py` (new) — same `ensure_divers_schema()`,
  reused metadata/Table objects appended to `bot/sync/schema.py`'s
  `MetaData`.
- `bot/sync/schema.py` — append `divers` and `diver_segments` Tables;
  `ensure_hff_schema()` calls `ensure_divers_schema()` after
  `metadata.create_all`.
- `bot/sync/adapters/divelog.py` — accept `payload["divers"]`, expand
  into `divers` + `diver_segments` inserts plus dual-write UPDATE on
  `dive_log` legacy columns.
- `bot/fsm/states.py` — new `DivelogWizard` states.
- `bot/handlers/entities/divelog.py` — diver/segment loops + buttons.
- `pyproject.toml` version → 2.0.0 (major because of payload schema
  break).

## Testing

**Plugin**: opening a fresh DB → migration runs → `divers` table
populated from existing `dive_log` rows. Manual smoke test: open a
dive with `diver_1='Mario'` and `dp_diver1='100'` in QGIS, verify the
new tree shows `Mario · lead` with `seg 0 ΔP 100`.

**Bot**: extend `tests/integration/test_divelog_adapter.py` to feed a
payload with `divers=[{...}, {...}]` and assert the resulting
`divers`+`diver_segments` rowsets and the dual-written legacy columns
match. Postgres testcontainer covers the FK + unique behavior.

**Mixed plugin versions**: scripted scenario — new plugin writes a
dive with 3 divers; open the same DB with old plugin code, verify it
shows the first two divers with their first-segment data, and that
the third diver is silently absent (documented behavior).

## Rollout

1. Land plugin v11.0 + bot v2.0.0 simultaneously (commit pair).
2. Push migration first (it's idempotent), let users open a few dives
   to verify the on-demand path before announcing.
3. Document the "third+ diver invisible to old plugin" caveat in the
   plugin's release notes.
4. After all team members are on plugin v11.0+, plan a v12 that drops
   the legacy `dive_log` diver columns and the dual-write code path.
   That migration is one-way and gated behind a separate version bump.

## Open questions

None blocking — every decision in this spec was confirmed by the user
during the brainstorming round on 2026-04-25.
