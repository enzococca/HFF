# Design — Webapp data viewer + bot edit existing records

**Date:** 2026-04-26
**Scope:** extend the existing FastAPI webapp (`bot/webapp/server.py`) into a mobile-first browser/editor for all 6 HFF entities + Divers + Media; add bot slash commands to edit existing records.
**Repos affected:** `hff-telegram-bot`
**Driver:** team members without QGIS need (a) a way to consult HFF data from the field on a phone, (b) lightweight CRUD to fix typos / fill descriptions / update task notes without going through QGIS, and (c) an analytical dashboard summarising the project. The bot today only creates records; existing records can only be edited via QGIS plugin — we close that gap with a shared edit service used by both webapp HTTP routes and bot slash commands.

## Goals

1. Mobile-first read browser for Site, Divelog, Anchor, Artefact, Pottery, Shipwreck, Divers, Media records — with search, filters, pagination, and per-record detail.
2. Field-level edit for the same 7 entities, gated by an explicit allowlist per entity.
3. Mini analytical dashboard with KPI tiles and 6 charts on the same page.
4. Per-user DB selection via a dropdown — the user picks any alias they have access to (no fallback to bot's `/use`).
5. Telegram Mini App auth for the webapp (initData HMAC); existing `Bearer MEDIA_TOKEN` stays for the media-file endpoints.
6. Bot `/edit_<entity>` slash commands that share business logic with the webapp via a single `EditService`.
7. Audit trail of every edit, written to `bot_audit_log` on the target DB.

## Non-goals

- Delete records. Out of scope; only edit existing.
- Add records via webapp. The bot wizards already cover this; the webapp keeps `/new_site` (existing) but does not add new wizards.
- Spatial / geometry editing. Out of scope.
- Real-time multi-user collaboration. Last-write-wins, audit log captures history.
- Webapp i18n. English-only first cut, matching the rest of the codebase.
- Web charts beyond Chart.js — no D3, no Plotly. KISS.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Telegram Mini App (mobile-first, theme-aware Jinja2)   │
│                       │ initData HMAC                   │
│                       ▼                                  │
│  bot/webapp/server.py                                    │
│   - existing routes (/health, /media/*, /new_site)      │
│   - new entity routes (list / detail / edit / save)     │
│   - /dashboard + /dashboard/data (JSON for Chart.js)    │
│   - /switch_db (POST sets signed cookie)                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  bot/sync/edit_service.py    (NEW — shared)             │
│   - EditService.update_site/divelog/anchor/...           │
│   - column allowlist per entity                          │
│   - audit log write                                      │
│   ↑                          ↑                           │
│   used by webapp POST        used by bot /edit_* handlers│
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  bot/sync/query_service.py   (NEW — read helpers)        │
│   - list_<entity>(alias, filters, page, search)          │
│   - get_<entity>(alias, pk)                              │
│   - dashboard_metrics(alias)                             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Target DBs (sqlite + postgres) via existing             │
│  bot/store/registry.py + bot/sync/target_db.py           │
└─────────────────────────────────────────────────────────┘
```

**Connection caching**: a module-level dict in `query_service` caches one SQLAlchemy `Engine` per alias for the process lifetime. `pool_pre_ping=True` so dead connections recycle on first use. Switching DB in webapp is `O(1)` after the first request to a new alias.

**No new tables on `state.db`**: auth + alias data already in `users` + `db_registry`.

## Auth flow

```
1. Browser opens /sites?initData=<...>
   (Telegram WebApp injects initData via query string; verified via HMAC).
2. Server verifies HMAC against BOT_TOKEN. If invalid → 403.
3. Extracts chat_id from parsed initData. Looks up via UserStore.get(chat_id).
4. If user not in allowlist → 403.
5. Selected alias from signed cookie `hff_alias` (default: user.active_db_alias).
6. Renders page.
```

Session = stateless. Initdata is short-lived (~24h) and re-injected by Telegram on every navigation; signed cookie holds only the chosen alias.

`/switch_db` POST endpoint: validates the user has access to the alias, sets the signed cookie, redirects back to the page.

## Data layer

### `bot/sync/edit_service.py`

```python
class EditService:
    def __init__(self, registry: Registry):
        self._registry = registry

    SITE_EDITABLE     = {...}  # 26 cols, see appendix A
    DIVELOG_EDITABLE  = {...}  # 23 cols
    ANCHOR_EDITABLE   = {...}  # 60 cols
    ARTEFACT_EDITABLE = {...}  # 27 cols
    POTTERY_EDITABLE  = {...}  # 38 cols
    SHIPWRECK_EDITABLE = {...} # 41 cols
    MEDIA_EDITABLE    = {"filename", "filetype", "descrizione", "tags"}
    DIVERS_EDITABLE   = {"diver_name", "role", "time_in", "time_out",
                         "max_depth"}
    DIVER_SEGMENTS_EDITABLE = {"breathing_mix", "bar_start", "bar_end",
                               "delta_p"}

    def update_site(self, alias, id_sito, fields, user_chat_id) -> tuple[int, str|None]:
        return self._update("site_table", "id_sito",
                            alias, id_sito, fields,
                            self.SITE_EDITABLE, user_chat_id)

    # … same shape for each entity …

    def _update(self, table, pk_col, alias, pk_value, fields,
                editable, user_chat_id):
        # 1. Filter `fields` to keys ∈ editable (silent drop).
        # 2. Open engine via registry.
        # 3. Read OLD values (for audit).
        # 4. UPDATE table SET col = :val, … WHERE pk = :pk.
        # 5. INSERT into bot_audit_log row per (col, old, new).
        # 6. Return (rowcount, None) on success; (0, msg) on failure.
```

The audit log is created idempotently the first time `EditService` runs against a given alias:

```sql
CREATE TABLE IF NOT EXISTS bot_audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,  -- SERIAL on Postgres
    component     TEXT NOT NULL,        -- 'site_table' / 'dive_log' / …
    pk            TEXT NOT NULL,        -- str(id) of the changed row
    field         TEXT NOT NULL,
    old_value     TEXT,
    new_value     TEXT,
    user_chat_id  INTEGER NOT NULL,
    applied_at    TEXT NOT NULL,
    source        TEXT NOT NULL         -- 'webapp' | 'bot'
);
CREATE INDEX IF NOT EXISTS idx_audit_table_pk
    ON bot_audit_log(component, pk);
CREATE INDEX IF NOT EXISTS idx_audit_user
    ON bot_audit_log(user_chat_id, applied_at);
```

### `bot/sync/query_service.py`

```python
class QueryService:
    def __init__(self, registry: Registry):
        self._registry = registry

    def list_sites(self, alias, *, search=None, country=None,
                   limit=20, offset=0) -> list[dict]:
        ...

    def get_site(self, alias, id_sito) -> dict | None:
        ...

    def list_divelogs(self, alias, *, search=None, site=None,
                      year=None, limit=20, offset=0) -> list[dict]:
        ...

    def get_divelog(self, alias, id_dive) -> dict | None:
        # Returns dive_log row PLUS list of divers + their segments.
        ...

    # … same shape for each entity …

    def dashboard_metrics(self, alias) -> dict:
        # 7 GROUP BY queries returning the structure consumed by
        # /dashboard/data — see appendix B.
        ...
```

All queries use `text()` with parameterized binds. No SQL string interpolation. SQLite + Postgres parity via the same patterns introduced in `bot/sync/divers_schema.py`.

## Webapp routes

| URL | Method | Handler |
|-----|--------|---------|
| `/` | GET | redirect to `/sites` |
| `/sites` | GET | list + filters + search |
| `/sites/{id_sito}` | GET | detail (read-only) |
| `/sites/{id_sito}/edit` | GET | edit form |
| `/sites/{id_sito}` | POST | save edit |
| `/divelogs` | GET | list |
| `/divelogs/{id_dive}` | GET | detail (incl. divers + segments) |
| `/divelogs/{id_dive}/edit` | GET | edit form |
| `/divelogs/{id_dive}` | POST | save edit |
| `/anchors` | GET | list |
| `/anchors/{id_anc}` | GET / POST / `/edit` | detail / edit |
| `/artefacts` | GET / detail / edit | |
| `/potteries` | GET / detail / edit | |
| `/shipwrecks` | GET / detail / edit | |
| `/divers/{id}` | GET / POST / `/edit` | edit a divers row |
| `/diver_segments/{id}` | GET / POST / `/edit` | edit a segment row |
| `/media_records` | GET | list (paginated by alias subtree) |
| `/media_records/{id_media}` | GET / POST / `/edit` | edit metadata |
| `/dashboard` | GET | renders chart skeleton |
| `/dashboard/data` | GET | JSON metrics |
| `/switch_db` | POST | sets `hff_alias` signed cookie |
| existing `/health`, `/new_site`, `/media/list`, `/media/{path}` | unchanged | |

All entity templates share three Jinja2 base templates (`entity_list.html`, `entity_detail.html`, `entity_edit.html`) parameterised by a context dict — the per-entity columns, label translations, and edit-allowlist.

## UI / UX

### Layout chrome

```
┌─ HFF · <Page name>   [☰] [▼ alias-name] ────┐
│   <page-specific content>                   │
│                                              │
│ Sites · Divelogs · Dashboard ───────────────┘
└─────────────────────────────────────────────┘
```

- Header: page title, hamburger drawer toggle, DB alias dropdown.
- Drawer (slide from left): Sites, Divelogs, Anchors, Artefacts, Potteries, Shipwrecks, Media, Divers, Dashboard, Settings.
- Bottom nav (sticky, 3 tabs): the most-used three — Sites, Divelogs, Dashboard.

### Site list

- Search field: full-text against `name_site`, `location_`, `village`, `antique_name`.
- Filters: country (distinct values), year (parsed from `date_start`).
- Each list row shows: name, country · year-range · count of divelogs at this site. Tap → detail.
- Pagination: 20 per page, "Load more" button appends.

### Site detail

- All read-only field rows.
- Media grid (3-col thumbnails, lazy-load, opens `/media/{path}` on tap with the user's bearer token from the signed cookie).
- "Divelogs at this site" list (≤ 20 rows, link to each).
- Floating "Edit" button → `/sites/{id}/edit`.

### Site edit

- HTML form with one input per `SITE_EDITABLE` column.
- Pre-populated.
- POST → `EditService.update_site` → flash "Saved" on success, redirect to detail.
- Validation errors inline.

### Divelog list / detail / edit

- Same pattern, with the divelog detail showing the **Divers** section (rows from `divers` joined with `diver_segments`) and the photo + video tables (the same table widgets the QGIS plugin uses).
- The edit form lets you mutate divelog dive-level fields. To edit divers / segments, the detail page links to per-row edit forms (`/divers/{id}/edit`, `/diver_segments/{id}/edit`).

### Other entities

Same three-template pattern (list / detail / edit). Per-entity context dict declares:
- `columns_in_list` — 3-5 columns shown in the list row.
- `searchable` — list of columns the search field hits.
- `filters` — list of `(column, label, distinct-values)` tuples for filter dropdowns.
- `editable` — the allowlist set.
- `field_labels` — display label per column.

### Dashboard

`/dashboard` HTML with 6 chart `<canvas>` + KPI tile row:

| Chart | Data source |
|-------|-------------|
| KPI tiles | `SELECT COUNT(*)` on each entity table |
| Sites by country | `GROUP BY country` |
| Divelogs per year | `GROUP BY years` |
| Top 10 divers | `divers GROUP BY diver_name ORDER BY COUNT DESC LIMIT 10` |
| Artefacts by material | `artefact_log GROUP BY material` |
| Anchors by typology | `anchor_table GROUP BY typology` |
| Pottery by period | `pottery_table GROUP BY period` |

`/dashboard/data` returns JSON; the page-side JS uses Chart.js (loaded from CDN, no bundle). Empty buckets → "No <entity> in this database yet." stub.

### Mobile-first CSS

Extends existing `static/style.css`:
- Container max-width 100% on mobile, 720px on tablets.
- Drawer overlay for hamburger menu.
- Bottom nav fixed; padding-bottom on body so content doesn't hide behind it.
- Tap targets ≥ 44 px (Apple HIG minimum).

## Bot edit flow

### Slash commands

| Command | Resolves on |
|---------|-------------|
| `/edit_site <name|id_sito>` | `name_site` ILIKE / `id_sito` |
| `/edit_divelog <id_dive>` | PK |
| `/edit_anchor <anchors_id>` | natural key |
| `/edit_artefact <artefact_id>` | natural key |
| `/edit_pottery <artefact_id>` | natural key |
| `/edit_shipwreck <code_id>` | natural key |
| `/edit_diver <name>` | `divers.diver_name` ILIKE |

### FSM

```
EditWizard:
    waiting_query        # got /edit_<entity>, waiting for the search term
    choose_match         # multiple results; user taps inline button
    field_menu           # record found, top fields shown as inline buttons
    waiting_value        # user tapped a field, expects new value
```

### Field menus

Each entity has a curated `TOP_FIELDS` list (6-8 most-edited columns) shown as inline keyboard. A "▸ more fields" button reveals additional pages, paginated 6 per page. "✓ done" exits the FSM.

### Update granularity

**Incremental**: each `waiting_value` reply commits to DB immediately via `EditService.update_<entity>` and writes audit log. Rationale: fits the bot's commit-per-message philosophy (mirrors `/new_*` wizard behaviour); no risk of losing partial edits if the user abandons; concurrency-safe because each write is a separate transaction.

The user can re-edit a field they got wrong by picking it again from the menu.

### Permissions

First cut: any allowlisted user can edit any record. The audit log captures who. Future tightening (admin-only or owner-only) can plug into `EditService` without touching wizards.

## Testing

**Unit (`tests/unit/test_edit_service.py`)**:
- `update_site` allowlist filters out junk keys.
- Concurrent edits to different fields don't clobber each other.
- Audit log row written per field change.
- Idempotent `bot_audit_log` table creation.

**Integration (`tests/integration/test_webapp_routes.py`, extends existing `test_postgres_target.py`-style)**:
- Each list endpoint returns expected rows after seeding test fixtures.
- Each edit POST succeeds and reflects in subsequent GET.
- Auth: missing initData → 403; bad HMAC → 403; non-allowlisted user → 403.
- Switch DB: cookie set / read.
- Dashboard JSON shape stable.

**Manual smoke**:
- Open Mini App from Telegram on phone.
- Browse 7 entity lists.
- Edit one record per entity; confirm change in QGIS.
- Run `/edit_site Tabarja` from Telegram, change country, confirm change in webapp.
- Open `/dashboard` and confirm 6 charts render.

**Existing test suite**: 262 tests stay green. New tests bring the total to ~290.

## Code organisation

```
bot/
├── sync/
│   ├── edit_service.py          # NEW — shared edit/audit logic
│   ├── query_service.py         # NEW — read helpers + dashboard_metrics
│   ├── divers_schema.py         # existing (gets a sibling for audit_log)
│   ├── audit_schema.py          # NEW — bot_audit_log idempotent migration
│   └── …
├── handlers/
│   └── edit_record.py           # NEW — /edit_* slash commands + FSM
├── fsm/
│   └── states.py                # extended with EditWizard
├── webapp/
│   ├── server.py                # existing — extended with new routes
│   ├── routes/                  # NEW — one file per entity bundle
│   │   ├── __init__.py
│   │   ├── sites.py
│   │   ├── divelogs.py
│   │   ├── anchors.py
│   │   ├── artefacts.py
│   │   ├── potteries.py
│   │   ├── shipwrecks.py
│   │   ├── divers.py
│   │   ├── media_records.py
│   │   ├── dashboard.py
│   │   └── auth.py              # signed cookie + initData verification
│   ├── templates/
│   │   ├── _base.html           # NEW — chrome (header, drawer, nav)
│   │   ├── entity_list.html     # NEW — generic list
│   │   ├── entity_detail.html   # NEW — generic detail
│   │   ├── entity_edit.html     # NEW — generic edit
│   │   ├── dashboard.html       # NEW
│   │   └── new_site.html        # existing
│   └── static/
│       ├── style.css            # extended
│       ├── charts.js            # NEW — Chart.js helpers
│       └── app.js               # NEW — drawer, db switcher, listloads
└── tests/
    ├── unit/test_edit_service.py
    ├── unit/test_query_service.py
    └── integration/test_webapp_routes.py
```

## Rollout

1. Land `EditService` + `QueryService` + `bot_audit_log` migration. Tests green.
2. Land webapp routes for Site only (read + edit + detail) + DB switcher + auth scaffolding. Smoke-test from phone.
3. Replicate the route bundle for the remaining 6 entities (one PR per pair).
4. Land `/dashboard` + `/dashboard/data`.
5. Land bot `/edit_*` slash commands + EditWizard FSM. Smoke-test from Telegram.
6. Bot version bump 2.0.0 → 2.1.0; release notes call out the audit-log column on every target DB.

## Open questions

None — every scope decision in this spec was confirmed by the user during the brainstorming round on 2026-04-26.

---

## Appendix A — Editable column allowlists

(Verbatim from each entity's plugin schema, filtered to the columns that are safe to mutate via casual UI. PK, FK, and counter columns are excluded.)

**SITE_EDITABLE** (26): `location_, mouhafasat, casa, village, antique_name, definition, name_site, country, area, type_class, supervisor, soil_type, topographic_setting, visibility, condition_state, features, disturbance, orientation, length_, width_, depth_, height_, material, dating, description, interpretation`

**DIVELOG_EDITABLE** (23): `site, divelog_id, years, date_, area_id, task, result, dive_supervisor, standby_diver, uw_temperature, uw_visibility, uw_current_, wind, max_depth, surface_interval, comments_, bottom_time, camera, time_in, time_out, layer, biblio, storage_`

**ANCHOR_EDITABLE** (60): `site, divelog_id, anchors_id, stone_type, anchor_type, anchor_shape, type_hole, inscription, petrography, weight, origin, comparison, typology, recovered, photographed, conservation_completed, years, date_, depth, tool_markings, description_i, petrography_r, ll, rl, ml, tw, bw, mw, rtt, ltt, rtb, ltb, tt, bt, td, rd, ld, tde, rde, lde, tfl, rfl, lfl, tfr, rfr, lfr, tfb, rfb, lfb, tft, rft, lft, area, bd, bde, bfl, bfr, bfb, bft, qty, biblio, storage_`

**ARTEFACT_EDITABLE** (27): `divelog_id, artefact_id, material, treatment, description, recovered, list, photographed, conservation_completed, years, date_, obj, shape, depth, tool_markings, lmin, lmax, wmin, wmax, tmin, tmax, biblio, storage_, box, washed, site, area`

**POTTERY_EDITABLE** (38): `divelog_id, site, date_, artefact_id, photographed, drawing, retrieved, inclusions, percent_inclusion, specific_part, form, typology, provenance, munsell_clay, surf_treatment, conservation, depth, storage_, period, state, samples, washed, dm, dr, db, th, ph, bh, thickmin, thickmax, years, box, biblio, description, area, munsell_surf, category, wheel_made, qty`

**SHIPWRECK_EDITABLE** (41): `code_id, name_vessel, yard, area, category, confidence, propulsion, material, nationality, type, owner, purpose, builder, cause, divers, wreck, composition, inclination, depth_max_min, depth_quality, latitude, position_quality_1, longitude, consulties, l, w, d, t, cl, cw, cd, nickname, date_built, date_lost, description, history, list, name, status, biblio, storage_`

**MEDIA_EDITABLE** (4): `filename, filetype, descrizione, tags`

**DIVERS_EDITABLE** (5): `diver_name, role, time_in, time_out, max_depth`

**DIVER_SEGMENTS_EDITABLE** (4): `breathing_mix, bar_start, bar_end, delta_p`

## Appendix B — `/dashboard/data` JSON shape

```json
{
  "kpis": {
    "sites": <int>, "divelogs": <int>, "anchors": <int>,
    "artefacts": <int>, "potteries": <int>, "shipwrecks": <int>,
    "divers": <int>
  },
  "sites_by_country": [{"country": "<str>", "count": <int>}, …],
  "divelogs_per_year": [{"year": <int>, "count": <int>}, …],
  "top_divers": [{"name": "<str>", "count": <int>}, …],
  "artefacts_by_material": [{"material": "<str>", "count": <int>}, …],
  "anchors_by_typology": [{"typology": "<str>", "count": <int>}, …],
  "pottery_by_period": [{"period": "<str>", "count": <int>}, …]
}
```
