# HFF Telegram Bot — Design Spec

**Date:** 2026-04-21
**Status:** Draft, awaiting review
**Author:** Enzo Cocca (with Claude)
**Target repo:** `hff-telegram-bot` (new, separate from QGIS plugin)

## 1. Goal

Build a Telegram bot that lets a small team of archaeologists insert HFF records (Site, Shipwreck, Divelog, Artefact, Anchor, Pottery) and attach media (photos/videos) from their phone. The bot keeps working when the target HFF database is unreachable by queueing writes locally and flushing them when the DB comes back.

## 2. Core decisions (locked)

| Decision | Choice |
|---|---|
| Deployment model | Bot always online on a VPS; target DB may be intermittently unreachable; writes are queued locally in SQLite and replayed via a background async task |
| DB target selection | Multi-DB registry maintained **from inside the bot** with commands; user picks the active DB per session with `/use <alias>` |
| Auth / roles | Allowlist by `chat_id`. Two roles: `admin` (manages DBs and users) and `editor` (data entry only) |
| Media storage layout | `<base>/<db_alias>/<site_slug>/{thumbnail,image_resize}/`, naming convention identical to the plugin: `{id_media}_{name}_thumb.png` and `{id_media}_{name}.{ext}` |
| Media backing | Bot-side filesystem only. Bridge to the plugin on the user's laptop is a **deploy detail** (rsync / sshfs / nginx+URL). README documents rsync as the default |
| Originals retention | **Not retained**: only `thumbnail/` and `image_resize/` are kept (matches current plugin convention) |
| Data entry UX | Wizard per entity: **only core fields are asked upfront** (minimum required to satisfy DB constraints); everything else is opt-in via an action menu with inline buttons `[✏ field]` `[📸 photo]` `[🎥 video]` `[✅ save]` `[❌ cancel]` |
| Idempotency | Bot creates a `bot_flushed_intents(idempotency_key, entity_type, entity_id, flushed_at)` table **in the target DB on first flush** (not by altering HFF tables). Flusher checks this table before insert |
| Entities MVP scope | SITE → DIVELOG → ARTEFACT/ANCHOR/POTTERY → SHIPWRECK (in this order) |

## 2.1 Glossary

- **alias** — short identifier of a registered target DB, `[a-z0-9_-]+`, e.g. `tabarjah-2025`. Unique across the bot.
- **site_slug** — filesystem-safe rendering of the `site_table.sito` value (SITE entity) or the `site` column (DIVELOG/ARTEFACT/ANCHOR/POTTERY). Slugified with `re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')`. Used only as a subfolder name under `<base>/<alias>/`; the actual `site` column value stored in HFF tables keeps the human-readable form.
- **intent** — one queued write operation (one HFF row + zero-to-many media). The unit of idempotency.
- **spool** — binary media files saved on the bot's disk **before** flush, under `<base>/_spool/<uuid>.<ext>`. Deleted after finalization.
- **core fields** — the minimum set a wizard asks upfront to satisfy DB `NOT NULL` and `UNIQUE` constraints. Everything else is optional via the action menu.

## 2.2 Cross-entity dependency: `site`

DIVELOG, ARTEFACT, ANCHOR, and POTTERY all carry a `site` column whose value is expected to match an existing `site_table.sito`. The wizard for those entities fetches the list of known sites:

- **Online path**: query the active alias's `site_table` at wizard start.
- **Offline path**: the bot keeps a per-alias cache `site_cache(alias, sito, last_refreshed)` in `state.db`, refreshed on every successful health-check. If the DB is unreachable and the cache is empty for this alias, the wizard lets the user type a site name freely (validated later at flush time; if it doesn't match on flush, the intent goes to `poison` with a clear message).

## 3. Architecture

Single Python process (aiogram 3.x + asyncio) with 5 isolated layers:

```
┌────────────────────────────────────────────────────────┐
│                    Telegram layer                      │
│  handlers/  routers per entity                         │
│  fsm/       stateful wizards per entity                │
│  keyboards/ inline keyboards (enum values, action menu)│
└─────────────────────┬──────────────────────────────────┘
                      │ dispatch intent
                      ▼
┌────────────────────────────────────────────────────────┐
│                    Intent queue                        │
│  state.db (bot-side SQLite):                           │
│    users, db_registry, pending_intents, media_spool    │
│  store/intent_store.py  CRUD append/update/list        │
└─────────────────────┬──────────────────────────────────┘
                      │ asyncio.create_task
                      ▼
┌────────────────────────────────────────────────────────┐
│                    Sync worker                         │
│  sync/scheduler.py  every 30 s scan pending_intents    │
│  sync/flusher.py    resolve id_entity, rename media,   │
│                     insert into HFF tables,            │
│                     commit with idempotency_key        │
└─────────┬────────────────────────┬─────────────────────┘
          │                        │
          ▼                        ▼
┌──────────────────────┐  ┌──────────────────────────────┐
│   Target DB layer    │  │   Media storage              │
│  db_registry:        │  │  <base>/<db_alias>/          │
│   sqlite/postgres    │  │    <site_slug>/              │
│   adapter, conn pool │  │      thumbnail/              │
│   per registered DB  │  │      image_resize/           │
└──────────────────────┘  └──────────────────────────────┘
```

### Design principles

- **Telegram layer never touches the target DB directly.** It only writes intents into the queue. This keeps the bot responsive even when the DB is down.
- **Idempotency key per intent** (UUID v4 assigned at queue insert). The flusher checks `bot_flushed_intents` in the target DB before every insert. If the key is already there, mark the intent `flushed` and skip — covers "bot crashed mid-flush" cleanly.
- **One alias = one media namespace.** Files under `<base>/tabarjah-2025/...` never mix with `<base>/lucy-2026/...`.
- **Sync worker lives inside the bot process** (separate asyncio task). No Redis, no Celery, no second service. The queue is a plain SQLite file — inspectable with `sqlite3 state.db` during debugging.

## 4. Bot-side data model (`state.db`)

```sql
CREATE TABLE users (
    chat_id          INTEGER PRIMARY KEY,
    display_name     TEXT NOT NULL,
    role             TEXT NOT NULL CHECK(role IN ('admin','editor')),
    active_db_alias  TEXT,
    created_at       TEXT NOT NULL,
    created_by       INTEGER
);

CREATE TABLE db_registry (
    alias            TEXT PRIMARY KEY,            -- e.g. 'tabarjah-2025'
    server_type      TEXT NOT NULL CHECK(server_type IN ('sqlite','postgres')),
    conn_params_enc  BLOB NOT NULL,               -- Fernet-encrypted JSON
    media_base_path  TEXT NOT NULL,               -- <base>/<alias>/
    created_by       INTEGER NOT NULL,
    created_at       TEXT NOT NULL,
    last_health_ok   TEXT,
    last_health_err  TEXT
);

CREATE TABLE pending_intents (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    idempotency_key  TEXT NOT NULL UNIQUE,
    user_chat_id     INTEGER NOT NULL,
    db_alias         TEXT NOT NULL,
    entity_type      TEXT NOT NULL CHECK(entity_type IN (
                       'SITE','SHIPWRECK','DIVELOG','ARTEFACT','ANCHOR','POTTERY')),
    payload_json     TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'pending'
                       CHECK(status IN ('pending','flushing','flushed',
                                        'failed','poison','discarded')),
    retry_count      INTEGER NOT NULL DEFAULT 0,
    last_error       TEXT,
    created_at       TEXT NOT NULL,
    flushed_at       TEXT,
    target_entity_id INTEGER
);

CREATE TABLE media_spool (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id        INTEGER NOT NULL REFERENCES pending_intents(id) ON DELETE CASCADE,
    telegram_file_id TEXT NOT NULL,
    local_path       TEXT NOT NULL,               -- <base>/_spool/<uuid>.<ext>
    original_name    TEXT,
    mediatype        TEXT NOT NULL CHECK(mediatype IN ('image','video')),
    filetype         TEXT NOT NULL,
    sha256           TEXT NOT NULL,
    final_media_id   INTEGER,
    final_filepath   TEXT
);

CREATE TABLE site_cache (
    alias            TEXT NOT NULL,
    sito             TEXT NOT NULL,               -- value of site_table.sito
    last_refreshed   TEXT NOT NULL,
    PRIMARY KEY (alias, sito)
);

CREATE INDEX idx_pending_status ON pending_intents(status, db_alias);
CREATE INDEX idx_spool_intent ON media_spool(intent_id);
```

### Target DB side: idempotency tracking table

Created by the flusher on first write to any registered DB:

```sql
CREATE TABLE IF NOT EXISTS bot_flushed_intents (
    idempotency_key  TEXT PRIMARY KEY,
    entity_type      TEXT NOT NULL,
    entity_id        INTEGER NOT NULL,
    flushed_at       TEXT NOT NULL
);
```

This is the **only** new object the bot adds to the HFF schema. The plugin ignores it entirely.

### Entity → HFF table mapping

| `entity_type` | HFF table         | `media_to_entity_table.entity_type` |
|---------------|-------------------|-------------------------------------|
| `SITE`        | `site_table`      | `SITE`                              |
| `SHIPWRECK`   | `shipwreck_table` | `SHIPWRECK`                         |
| `DIVELOG`     | `dive_log`        | `DOC`                               |
| `ARTEFACT`    | `artefact_log`    | `ARTEFACT`                          |
| `ANCHOR`      | `anchor_table`    | `ANCHOR`                            |
| `POTTERY`     | `pottery_table`   | `POTTERY`                           |

One adapter module per `entity_type` under `bot/sync/adapters/`. Each adapter:
1. Inserts the entity row (lets DB AUTOINCREMENT assign the primary key, then reads it back).
2. Finalizes each associated media spool row (generates thumbnail + resize, renames to convention, moves into `<base>/<alias>/<site_slug>/{thumbnail,image_resize}/`).
3. Inserts `media_table`, `media_thumb_table`, `media_to_entity_table` rows using the new entity id.
4. Inserts `bot_flushed_intents(idempotency_key, entity_type, entity_id, now())`.
5. All 4 steps wrapped in a single transaction. `COMMIT` or `ROLLBACK`.

## 5. User flows

### 5.1 Onboarding

- `.env` has `BOOT_ADMIN_CHAT_ID=<your chat_id>`. On first `/start` from that chat_id, the user is inserted into `users` as `admin`. Env var is then cosmetic.
- Other users: `/start` on an unauthorized chat responds with "ask an admin to `/invite <your chat_id>`".

### 5.2 Registering DBs (admin only)

```
/add_db
Bot: [SQLite file] [Postgres URL]
Admin: [tap SQLite file]
Bot:   "Send the .sqlite as a document, max 2 GB."
Admin: [uploads file]
Bot:   "Alias for this DB (a-z 0-9 - _)?"
Admin: "tabarjah-2025"
Bot:   "Registered. Health-check OK (78 dive_log rows, 12 sites).
        Run /use tabarjah-2025 to make it active."
```

Postgres path: prompts for host/port/user/password/dbname, tests connection, encrypts with Fernet, stores in `db_registry.conn_params_enc`. Fernet key lives in `.env` (`FERNET_KEY=`).

### 5.3 Switching active DB

```
/list_dbs
• tabarjah-2025 (sqlite)  ← active
• lucy-2026 (sqlite)
• hff-main (postgres)     ⚠ last sync failed 3 h ago

/use lucy-2026
Active DB set to lucy-2026.
```

`active_db_alias` is persisted on `users` — survives bot restarts.

### 5.4 Data entry wizard (example: DIVELOG)

```
/new_divelog
Bot: "New divelog on lucy-2026. Site?  [Alice B] [Cement] [Smashed] [➕ new]"
User: [tap Alice B]
Bot: "Divelog ID?"
User: "90"
Bot: "Year?"
User: "2026"
Bot: "Date (dd-mm-yyyy)?"
User: "21-04-2026"
Bot: "Core fields captured. Pick more fields or save:
     [✏ task] [✏ result] [✏ divers] [✏ depth/visibility/current]
     [📸 photo] [🎥 video] [✅ save] [❌ cancel]"
User: [📸 photo]
Bot: "Send the photo."
User: [sends photo]
Bot: "Name (file reference in DB)?"
User: "GOPR1001"
Bot: "Tag?  [DOC photolog] [PE photo-end]"
User: [DOC photolog]
Bot: "Added. Keep editing or save?  [✏ …] [📸] [🎥] [✅]"
User: [✅ save]
Bot: "✅ Divelog queued (intent #142). 1 photo attached. Flushing…"
[sync worker, ≤ 30 s later]
Bot: "✅ #142 flushed to lucy-2026. id_dive = 90. id_media = 631."
```

**Required fields per entity** (everything else is optional via menu):

| Entity     | Required core                             | UNIQUE constraint the core must satisfy         |
|------------|-------------------------------------------|-------------------------------------------------|
| SITE       | `sito`, `nazione`                         | `sito` (via `id_sito` AUTOINCREMENT PK)         |
| SHIPWRECK  | `code_id`, `name_vessel`, `area`          | `code_id`                                       |
| DIVELOG    | `site`, `divelog_id`, `years`, `date_`    | `(site, divelog_id, years)`                     |
| ARTEFACT   | `site`, `artefact_id`, `years`            | `(site, artefact_id, years)`                    |
| ANCHOR     | `site`, `anchors_id`, `years`             | `anchors_id`                                    |
| POTTERY    | `site`, `pottery_id`, `years`             | `(site, pottery_id, years)`                     |

If a user submits core fields that violate a UNIQUE constraint, the flush raises `IntegrityError` (FATAL) → intent goes to `poison` with the message `"UNIQUE constraint failed: ..."`. The user can `/edit <id>` to change the conflicting value and resubmit as a new intent.

### 5.5 Queue inspection

```
/status
Your intents:
#142 ✅ flushed  divelog  lucy-2026  2 m ago
#143 ⏳ pending  artefact lucy-2026  now
#141 ❌ failed   divelog  lucy-2026  'IntegrityError: divelog_id=77 exists'
     → /retry 141 or /discard 141
```

### 5.6 Admin commands

- `/invite <chat_id> <display name> [admin|editor]`
- `/revoke <chat_id>`
- `/add_db` / `/remove_db <alias>` / `/health_check <alias>`
- `/poison` — lists intents in `poison` state across the whole bot
- `/metrics` — daily counters

## 6. Media handling end-to-end

### 6.1 Acquisition
1. `bot.get_file(message.photo[-1].file_id)` downloads the binary.
2. Saved to `<base>/_spool/<uuid4>.<ext>`.
3. SHA-256 computed. If `media_spool` already has this sha256 linked to the current `intent_id`, dedupe (ignore).
4. Wizard prompts for a user-chosen name, stored in `media_spool.original_name`.
5. Wizard prompts for tag. Options depend on `entity_type`:
   - DIVELOG: `[DOC photolog]` / `[PE photo-end]`
   - others: automatic tag matching the entity

File size cap: 20 MB via the standard Bot API. MTProto fallback via `telethon` is documented as a post-MVP opt-in (`ENABLE_LARGE_FILES=true`).

### 6.2 Finalization at flush (per spool row)

```python
# bot/media/ops.py
def finalize(spool_row, alias_base, site_slug, session):
    max_id = session.query(func.max(MEDIA.id_media)).scalar() or 0
    id_media = max_id + 1
    fname = spool_row.original_name
    ext = spool_row.filetype
    mt = spool_row.mediatype  # 'image' | 'video'
    thumb_suffix = '_thumb.png' if mt == 'image' else '_video.png'
    resize_ext   = 'png' if mt == 'image' else ext

    name_thumb  = f"{id_media}_{fname}{thumb_suffix}"
    name_resize = f"{id_media}_{fname}.{resize_ext}"

    thumb_dir  = Path(alias_base) / site_slug / 'thumbnail'
    resize_dir = Path(alias_base) / site_slug / 'image_resize'
    thumb_dir.mkdir(parents=True, exist_ok=True)
    resize_dir.mkdir(parents=True, exist_ok=True)

    if mt == 'image':
        img = cv2.imread(spool_row.local_path)
        cv2.imwrite(str(thumb_dir / name_thumb),
                    cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA))
        cv2.imwrite(str(resize_dir / name_resize),
                    _resize_15x10_300dpi(img),
                    [cv2.IMWRITE_PNG_COMPRESSION, 0])
    else:  # video
        cap = cv2.VideoCapture(spool_row.local_path)
        ret, frame = cap.read()
        while ret and frame.mean() < 1:
            ret, frame = cap.read()
        cv2.imwrite(str(thumb_dir / name_thumb), cv2.resize(frame, (100, 100)))
        shutil.copy2(spool_row.local_path, resize_dir / name_resize)
        cap.release()

    Path(spool_row.local_path).unlink(missing_ok=True)
    spool_row.final_media_id = id_media
    spool_row.final_filepath = f'{site_slug}/image_resize/{name_resize}'
    return id_media, name_thumb, name_resize
```

Paths written to the HFF DB are **relative to `THUMB_PATH` / `THUMB_RESIZE`**. Example:

- `media_thumb_table.filepath`    = `<site_slug>/thumbnail/<name_thumb>`
- `media_thumb_table.path_resize` = `<site_slug>/image_resize/<name_resize>`
- `media_to_entity_table.filepath` = `<site_slug>/image_resize/<name_resize>`

Plugin display code already does `QIcon(thumb_path_str + filepath)`; it handles relative suffixes transparently as long as `THUMB_PATH` points to the alias base. **v10.5 of the plugin** will add a small README note on pointing `THUMB_PATH` at the mirrored `<alias>` root.

### 6.3 Plugin access to bot-stored media

Deploy detail, three documented options in README (in order of simplicity):

| Strategy | When to choose |
|----------|---------------|
| `rsync` periodic (cron on laptop pulls `bot:<base>/<alias>/` → `laptop:<THUMB_PATH>/..`) | Single operator on a stable laptop |
| `sshfs` mount of `<base>` on the laptop, `THUMB_PATH` points to the mount | Desk workstation, reliable network |
| nginx read-only serve of `<base>` + future plugin support for HTTPS `filepath` | Distributed team (post-MVP plugin change) |

MVP README ships an example cron + `rsync-sync.sh`.

### 6.4 Garbage collection
Nightly asyncio task:
- Removes files in `_spool/` older than 7 days without a linked `intent_id` (i.e. discarded intents whose spool cleanup failed).
- Rotates `logs/bot.log` entries older than 30 days.
- Never touches finalized media under `<alias>/<site_slug>/...`.

## 7. Error handling, retry, observability

### 7.1 Intent state machine

```
pending ──► flushing ──► flushed          (happy)
   │           │
   │           └──► failed ──► (backoff retry) ──► pending
   │                   │
   │                   └──► (retry_count ≥ 5) ──► poison
   │
   └──► discarded  (user /discard)
```

- `flushing` is taken with an optimistic lock: `UPDATE pending_intents SET status='flushing' WHERE id=? AND status='pending'`. If 0 rows affected, another worker got it — skip.
- Backoff schedule (seconds): `[30, 60, 300, 900, 3600]` for `retry_count` 1..5.

### 7.2 Error classification

```python
RECOVERABLE = (OperationalError, TimeoutError, DisconnectionError, socket.gaierror)
FATAL       = (IntegrityError, DataError, ProgrammingError)

try:
    adapter.flush(...)
except RECOVERABLE as e:
    intent.status = 'failed'
    intent.retry_count += 1
    intent.last_error = str(e)
    schedule_retry(intent, BACKOFF[intent.retry_count])
except FATAL as e:
    intent.status = 'poison'
    intent.last_error = str(e)
    notify_admin(...)
except Exception as e:
    intent.status = 'poison'
    intent.last_error = f'UNEXPECTED: {e}\n{traceback.format_exc()}'
    notify_admin(...)
```

Rule: **never `except: pass` anywhere**. Every failure is logged and either retried or surfaced via `/status` / admin DM.

### 7.3 User notifications

- ✅ Flushed: ACK message to the owning chat with new entity id.
- ❌ Failed with retry pending: silent (avoid spam during multi-hour outages).
- ❌ Poison: DM to the user with actionable next steps; DM to admins as well (`ADMIN_NOTIFY_POISON=true`).

### 7.4 Health checks

- Every 5 minutes, per registered DB: `SELECT 1` (postgres) or `PRAGMA quick_check` (sqlite).
- Result stored in `db_registry.last_health_ok` / `last_health_err`.
- On KO → admin DM once.
- On KO → OK transition → bulk-retry all `failed` intents on that alias.

### 7.5 Logging & metrics

- Structured JSON logs via `structlog` to `/var/hff-bot/logs/bot.log` (daily rotation).
- SQLite-backed daily counters (`metrics_daily` table in `state.db`): intents created / flushed / failed / poisoned, average pending→flushed latency.
- `/metrics` command (admin only) prints last 7 days.

### 7.6 Recovery commands

- `/status` — your last 10 intents with their state.
- `/show <id>` — full intent details (payload, error, spool media).
- `/retry <id>` — force-reset a `failed` or `poison` intent back to `pending`.
- `/discard <id>` — mark `discarded`, delete associated spool files.
- `/edit <id>` — only for `pending`/`failed`: re-opens the wizard pre-filled with current payload; saving produces a **new intent** with a fresh idempotency key.

## 8. Stack and repo layout

**New repo:** `hff-telegram-bot` (separate from the QGIS plugin).
**Rationale:** different lifecycle, different deploy target (VPS vs QGIS user machine), different test harness. The bot imports HFF schema objects via a git submodule pointing at the plugin repo (`bot/hff_models/ → plugin/modules/db/`), so schema stays single-source.

```
hff-telegram-bot/
├── bot/
│   ├── main.py
│   ├── config.py
│   ├── handlers/{common,admin,dbselect}.py
│   ├── handlers/entities/{site,shipwreck,divelog,artefact,anchor,pottery}.py
│   ├── fsm/{states,context}.py
│   ├── keyboards/{actions,enums}.py
│   ├── store/{schema.sql,intent_store,user_store,registry}.py
│   ├── sync/{scheduler,flusher,health}.py
│   ├── sync/adapters/{base,site,shipwreck,divelog,artefact,anchor,pottery}.py
│   ├── media/{ops,spool}.py
│   └── hff_models/            # submodule → plugin/modules/db
├── tests/
│   ├── unit/
│   └── integration/
├── deploy/
│   ├── hff-bot.service
│   ├── nginx-media.conf.example
│   └── rsync-sync.sh.example
├── .env.example
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

### Stack

- Python 3.11+ (match plugin)
- `aiogram` 3.x
- `SQLAlchemy` 2.x (match plugin)
- `pydantic-settings` for config from `.env`
- `cryptography.Fernet` for conn-params encryption
- `structlog` for JSON logs
- `opencv-python-headless` + `Pillow` fallback
- `pytest` + `pytest-asyncio` + `aiogram_tests`
- `ruff` + `mypy --strict` in CI

### `.env.example`

```env
BOT_TOKEN=
BOOT_ADMIN_CHAT_ID=
STATE_DB_PATH=/var/hff-bot/state.db
MEDIA_BASE_PATH=/var/hff-bot/media
LOG_LEVEL=INFO
LOG_PATH=/var/hff-bot/logs/bot.log
FERNET_KEY=
SYNC_INTERVAL_SECONDS=30
HEALTH_CHECK_INTERVAL_SECONDS=300
ENABLE_LARGE_FILES=false
ADMIN_NOTIFY_POISON=true
```

### `deploy/hff-bot.service`

```ini
[Unit]
Description=HFF Telegram Bot
After=network.target

[Service]
Type=simple
User=hffbot
Group=hffbot
WorkingDirectory=/opt/hff-telegram-bot
Environment="PATH=/opt/hff-telegram-bot/.venv/bin"
EnvironmentFile=/opt/hff-telegram-bot/.env
ExecStart=/opt/hff-telegram-bot/.venv/bin/python -m bot.main
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/hff-bot/logs/stdout.log
StandardError=append:/var/hff-bot/logs/stderr.log

NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/var/hff-bot
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## 9. Testing strategy

### Unit tests (target ≥ 85 % coverage on non-Telegram code)

- `store/intent_store` — CRUD, status transitions, optimistic lock correctness.
- `media/ops` — thumbnail + resize pixel-compared against fixtures generated by the plugin's `Media_utility` (regression guard).
- `sync/adapters/<entity>` — given a blank fixture SQLite of the HFF schema, running the adapter populates the entity table + `media_table` + `media_thumb_table` + `media_to_entity_table` + `bot_flushed_intents` with the expected rows.
- `idempotency` — running flush twice with the same key must produce exactly one row in each target table.
- `store/registry` — encrypt/decrypt round-trip for Postgres connection params.

### Integration tests

- **Full happy path**: mock Telegram wizard → intent enqueued → flusher drains → target SQLite file + filesystem media verified.
- **Crash recovery**: start a flush, SIGKILL the worker mid-transaction, restart the bot, verify the intent is re-picked and flushes exactly once (no duplicates, no orphan media files).
- **DB down scenario**: remove the target SQLite file → issue 5 inserts → put file back → next health-check flips to OK → all 5 intents drain in bulk-retry.

### Manual test plan (`tests/manual.md`)

- Bootstrap admin → `/invite` an editor.
- Register a sqlite DB and a postgres DB.
- Create: 1 site with 3 photos, 1 divelog referencing the site, 1 artefact with 1 photo + 1 video.
- Shut down the bot mid-wizard → restart → verify the wizard resumes from the last captured step (FSM persistence on restart).
- Power off the target DB host → make 5 inserts → power on → verify bulk-retry completes all 5 without manual intervention.

## 10. Release plan

| Version | Scope |
|---------|-------|
| 0.1 alpha | SITE end-to-end (wizard → queue → flush → plugin displays) |
| 0.2 | + DIVELOG (most complex entity; confirms the "core + action menu" pattern) |
| 0.3 | + ARTEFACT + ANCHOR + POTTERY |
| 0.4 | + SHIPWRECK |
| 0.5 | hardening: metrics, `/edit` wizard, bulk-retry on health recovery |
| 1.0 | docs, deploy automation, manual QA sign-off |

Update flow on the VPS:
```
cd /opt/hff-telegram-bot
git pull
.venv/bin/pip install -e .
systemctl restart hff-bot
```

## 11. Out of scope (explicitly)

- No web dashboard. Admin does everything from Telegram.
- No Telegram Mini App (HTML form). Reconsidered if wizard UX proves insufficient after 0.3.
- No multi-language UI in MVP. All bot messages in English.
- No automatic reconciliation across multiple DBs (e.g. "copy record from lucy-2026 to hff-main"). Can be a separate tool later.
- No on-device (laptop) sync component; the plugin-side mirroring is a deploy concern, not a bot feature.
