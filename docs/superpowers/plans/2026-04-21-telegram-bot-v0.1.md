# HFF Telegram Bot v0.1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v0.1 of `hff-telegram-bot`: a working vertical slice for the SITE entity — a Telegram user can register a sqlite DB, run `/new_site`, attach photos, and see the record + media land in the HFF sqlite target after a successful flush.

**Architecture:** Single Python process (aiogram 3.x + asyncio). Bot-side state in a local SQLite (`state.db`). Target HFF DB (sqlite for v0.1) written via SQLAlchemy through the plugin's existing schema modules (imported as a git submodule). Async sync worker drains queued intents every 30 s. Idempotency via a single `bot_flushed_intents` table in the target DB.

**Tech Stack:** Python 3.11, `aiogram 3.x`, `SQLAlchemy 2.x`, `pydantic-settings`, `cryptography` (Fernet), `structlog`, `opencv-python-headless`, `pytest` / `pytest-asyncio` / `aiogram-tests`.

**Reference spec:** `docs/superpowers/specs/2026-04-21-telegram-bot-design.md`

**Out of scope for v0.1 (deferred to later releases):**
- DIVELOG / ARTEFACT / ANCHOR / POTTERY / SHIPWRECK entities
- Postgres target DBs (sqlite only in v0.1)
- `/invite`, `/revoke`, `/edit <id>`, `/retry <id>` commands
- Health-check loop and bulk-retry on DB recovery
- Metrics dashboard
- MTProto large-file support
- Nightly garbage collection
- site_cache offline fallback (v0.1 assumes target DB is reachable at wizard start OR accepts free-text site name)

---

### Task 1: Initialize the `hff-telegram-bot` repo

**Files:**
- Create: `hff-telegram-bot/pyproject.toml`
- Create: `hff-telegram-bot/.gitignore`
- Create: `hff-telegram-bot/README.md` (stub)
- Create: `hff-telegram-bot/bot/__init__.py`
- Create: `hff-telegram-bot/tests/__init__.py`

- [ ] **Step 1: Create the directory and initialise git**

```bash
cd ~/dev
mkdir hff-telegram-bot && cd hff-telegram-bot
git init -b main
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "hff-telegram-bot"
version = "0.1.0"
description = "Telegram bot for HFF-Survey data entry with offline queue"
requires-python = ">=3.11"
dependencies = [
  "aiogram>=3.4,<4",
  "sqlalchemy>=2.0,<3",
  "pydantic>=2.6",
  "pydantic-settings>=2.2",
  "cryptography>=42",
  "structlog>=24",
  "opencv-python-headless>=4.9",
  "pillow>=10",
  "python-slugify>=8",
]

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "pytest-asyncio>=0.23",
  "pytest-cov>=4",
  "aiogram-tests>=1.1",
  "ruff>=0.3",
  "mypy>=1.9",
]

[tool.hatch.build.targets.wheel]
packages = ["bot"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "-ra --strict-markers --cov=bot --cov-report=term-missing"
testpaths = ["tests"]

[tool.mypy]
strict = true
python_version = "3.11"
```

- [ ] **Step 3: Write `.gitignore`**

```gitignore
__pycache__/
*.pyc
.venv/
.env
.env.*
!.env.example
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
*.db
*.sqlite
*.sqlite-journal
media/
logs/
```

- [ ] **Step 4: Create stub `bot/__init__.py` and `tests/__init__.py`**

```python
# bot/__init__.py
"""HFF Telegram Bot."""
__version__ = "0.1.0"
```

```python
# tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .gitignore bot/__init__.py tests/__init__.py README.md
git commit -m "chore: initialise hff-telegram-bot repo scaffolding"
```

---

### Task 2: Configuration via `pydantic-settings`

**Files:**
- Create: `hff-telegram-bot/bot/config.py`
- Create: `hff-telegram-bot/.env.example`
- Create: `hff-telegram-bot/tests/unit/test_config.py`

- [ ] **Step 1: Write `.env.example`**

```env
BOT_TOKEN=
BOOT_ADMIN_CHAT_ID=
STATE_DB_PATH=./state.db
MEDIA_BASE_PATH=./media
LOG_LEVEL=INFO
LOG_PATH=./logs/bot.log
FERNET_KEY=
SYNC_INTERVAL_SECONDS=30
```

- [ ] **Step 2: Write the failing test**

```python
# tests/unit/test_config.py
import os
from pathlib import Path
from bot.config import Settings

def test_settings_load_from_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BOT_TOKEN", "123:abc")
    monkeypatch.setenv("BOOT_ADMIN_CHAT_ID", "42")
    monkeypatch.setenv("STATE_DB_PATH", str(tmp_path / "state.db"))
    monkeypatch.setenv("MEDIA_BASE_PATH", str(tmp_path / "media"))
    monkeypatch.setenv("FERNET_KEY", "dGVzdGtleXNob3VsZGJlMzJieXRlc2xvbmcxMjM0NQ==")
    monkeypatch.setenv("SYNC_INTERVAL_SECONDS", "15")

    s = Settings()

    assert s.bot_token == "123:abc"
    assert s.boot_admin_chat_id == 42
    assert s.sync_interval_seconds == 15
    assert s.state_db_path == tmp_path / "state.db"

def test_settings_requires_bot_token(monkeypatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Settings()
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/unit/test_config.py -v
```
Expected: FAIL (`ModuleNotFoundError: No module named 'bot.config'`).

- [ ] **Step 4: Implement `bot/config.py`**

```python
# bot/config.py
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(...)
    boot_admin_chat_id: int = Field(...)
    state_db_path: Path = Field(default=Path("./state.db"))
    media_base_path: Path = Field(default=Path("./media"))
    log_level: str = Field(default="INFO")
    log_path: Path = Field(default=Path("./logs/bot.log"))
    fernet_key: str = Field(...)
    sync_interval_seconds: int = Field(default=30)
```

- [ ] **Step 5: Run test again, must pass**

```bash
pytest tests/unit/test_config.py -v
```
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add bot/config.py tests/unit/test_config.py .env.example
git commit -m "feat: add Settings loaded from .env via pydantic-settings"
```

---

### Task 3: Fernet key helper + encryption utilities

**Files:**
- Create: `hff-telegram-bot/bot/store/__init__.py`
- Create: `hff-telegram-bot/bot/store/crypto.py`
- Create: `hff-telegram-bot/tests/unit/test_crypto.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_crypto.py
from cryptography.fernet import Fernet
from bot.store.crypto import Cryptor

def test_roundtrip_json() -> None:
    key = Fernet.generate_key().decode()
    c = Cryptor(key)
    payload = {"host": "localhost", "port": 5432, "password": "s3cret"}
    blob = c.encrypt_json(payload)
    assert isinstance(blob, bytes)
    assert c.decrypt_json(blob) == payload

def test_wrong_key_fails() -> None:
    import pytest
    from cryptography.fernet import InvalidToken
    blob = Cryptor(Fernet.generate_key().decode()).encrypt_json({"x": 1})
    with pytest.raises(InvalidToken):
        Cryptor(Fernet.generate_key().decode()).decrypt_json(blob)
```

- [ ] **Step 2: Run test — expect fail**

```bash
pytest tests/unit/test_crypto.py -v
```
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Create `bot/store/__init__.py`** (empty file) and `bot/store/crypto.py`

```python
# bot/store/crypto.py
import json
from cryptography.fernet import Fernet

class Cryptor:
    def __init__(self, key: str) -> None:
        self._f = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt_json(self, obj: dict) -> bytes:
        return self._f.encrypt(json.dumps(obj, sort_keys=True).encode("utf-8"))

    def decrypt_json(self, blob: bytes) -> dict:
        return json.loads(self._f.decrypt(blob).decode("utf-8"))
```

- [ ] **Step 4: Run test, expect pass**

- [ ] **Step 5: Commit**

```bash
git add bot/store/__init__.py bot/store/crypto.py tests/unit/test_crypto.py
git commit -m "feat: Cryptor for Fernet-encrypted JSON blobs"
```

---

### Task 4: `state.db` schema + initialization

**Files:**
- Create: `hff-telegram-bot/bot/store/schema.sql`
- Create: `hff-telegram-bot/bot/store/db.py`
- Create: `hff-telegram-bot/tests/unit/test_state_db.py`

- [ ] **Step 1: Write `schema.sql`**

```sql
-- bot/store/schema.sql
CREATE TABLE IF NOT EXISTS users (
    chat_id          INTEGER PRIMARY KEY,
    display_name     TEXT NOT NULL,
    role             TEXT NOT NULL CHECK(role IN ('admin','editor')),
    active_db_alias  TEXT,
    created_at       TEXT NOT NULL,
    created_by       INTEGER
);

CREATE TABLE IF NOT EXISTS db_registry (
    alias            TEXT PRIMARY KEY,
    server_type      TEXT NOT NULL CHECK(server_type IN ('sqlite','postgres')),
    conn_params_enc  BLOB NOT NULL,
    media_base_path  TEXT NOT NULL,
    created_by       INTEGER NOT NULL,
    created_at       TEXT NOT NULL,
    last_health_ok   TEXT,
    last_health_err  TEXT
);

CREATE TABLE IF NOT EXISTS pending_intents (
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

CREATE TABLE IF NOT EXISTS media_spool (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_id        INTEGER NOT NULL REFERENCES pending_intents(id) ON DELETE CASCADE,
    telegram_file_id TEXT NOT NULL,
    local_path       TEXT NOT NULL,
    original_name    TEXT,
    mediatype        TEXT NOT NULL CHECK(mediatype IN ('image','video')),
    filetype         TEXT NOT NULL,
    sha256           TEXT NOT NULL,
    final_media_id   INTEGER,
    final_filepath   TEXT
);

CREATE TABLE IF NOT EXISTS site_cache (
    alias            TEXT NOT NULL,
    sito             TEXT NOT NULL,
    last_refreshed   TEXT NOT NULL,
    PRIMARY KEY (alias, sito)
);

CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_intents(status, db_alias);
CREATE INDEX IF NOT EXISTS idx_spool_intent ON media_spool(intent_id);
```

- [ ] **Step 2: Write the failing test**

```python
# tests/unit/test_state_db.py
from pathlib import Path
import sqlite3
from bot.store.db import init_state_db

def test_init_creates_all_tables(tmp_path: Path) -> None:
    db = tmp_path / "state.db"
    init_state_db(db)
    con = sqlite3.connect(db)
    names = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )}
    con.close()
    assert names == {"users", "db_registry", "pending_intents",
                     "media_spool", "site_cache"}

def test_init_is_idempotent(tmp_path: Path) -> None:
    db = tmp_path / "state.db"
    init_state_db(db)
    init_state_db(db)  # must not raise
```

- [ ] **Step 3: Run test, expect fail**

- [ ] **Step 4: Implement `bot/store/db.py`**

```python
# bot/store/db.py
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def init_state_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    con = sqlite3.connect(path)
    try:
        con.executescript(schema_sql)
        con.commit()
    finally:
        con.close()

def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con
```

- [ ] **Step 5: Run test, expect pass. Commit.**

```bash
git add bot/store/schema.sql bot/store/db.py tests/unit/test_state_db.py
git commit -m "feat: state.db schema + idempotent initializer"
```

---

### Task 5: `user_store` with bootstrap admin

**Files:**
- Create: `hff-telegram-bot/bot/store/user_store.py`
- Create: `hff-telegram-bot/tests/unit/test_user_store.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_user_store.py
from pathlib import Path
import pytest
from bot.store.db import init_state_db
from bot.store.user_store import UserStore, Role, UserNotFound

@pytest.fixture
def store(tmp_path: Path) -> UserStore:
    db = tmp_path / "state.db"
    init_state_db(db)
    return UserStore(db)

def test_bootstrap_admin_first_time(store: UserStore) -> None:
    user = store.bootstrap_admin(chat_id=42, display_name="Enzo")
    assert user.chat_id == 42
    assert user.role == Role.ADMIN

def test_bootstrap_admin_idempotent(store: UserStore) -> None:
    a = store.bootstrap_admin(chat_id=42, display_name="Enzo")
    b = store.bootstrap_admin(chat_id=42, display_name="Enzo")
    assert a.chat_id == b.chat_id
    assert store.count() == 1

def test_get_unknown_raises(store: UserStore) -> None:
    with pytest.raises(UserNotFound):
        store.get(999)

def test_set_active_db(store: UserStore) -> None:
    store.bootstrap_admin(42, "Enzo")
    store.set_active_db(42, "tabarjah-2025")
    assert store.get(42).active_db_alias == "tabarjah-2025"
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/store/user_store.py`**

```python
# bot/store/user_store.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from bot.store.db import connect

class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"

class UserNotFound(Exception):
    pass

@dataclass(frozen=True)
class User:
    chat_id: int
    display_name: str
    role: Role
    active_db_alias: str | None
    created_at: str
    created_by: int | None

class UserStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def bootstrap_admin(self, chat_id: int, display_name: str) -> User:
        with connect(self._db_path) as con:
            existing = con.execute(
                "SELECT * FROM users WHERE chat_id = ?", (chat_id,)
            ).fetchone()
            if existing:
                return self._row_to_user(existing)
            con.execute(
                "INSERT INTO users (chat_id, display_name, role, created_at) "
                "VALUES (?, ?, ?, ?)",
                (chat_id, display_name, Role.ADMIN.value, self._now()),
            )
            con.commit()
        return self.get(chat_id)

    def get(self, chat_id: int) -> User:
        with connect(self._db_path) as con:
            row = con.execute(
                "SELECT * FROM users WHERE chat_id = ?", (chat_id,)
            ).fetchone()
        if not row:
            raise UserNotFound(chat_id)
        return self._row_to_user(row)

    def set_active_db(self, chat_id: int, alias: str) -> None:
        with connect(self._db_path) as con:
            con.execute(
                "UPDATE users SET active_db_alias = ? WHERE chat_id = ?",
                (alias, chat_id),
            )
            con.commit()

    def count(self) -> int:
        with connect(self._db_path) as con:
            return con.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    @staticmethod
    def _row_to_user(row) -> User:
        return User(
            chat_id=row["chat_id"],
            display_name=row["display_name"],
            role=Role(row["role"]),
            active_db_alias=row["active_db_alias"],
            created_at=row["created_at"],
            created_by=row["created_by"],
        )
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
git add bot/store/user_store.py tests/unit/test_user_store.py
git commit -m "feat: UserStore with idempotent bootstrap_admin"
```

---

### Task 6: `registry` for registered DBs

**Files:**
- Create: `hff-telegram-bot/bot/store/registry.py`
- Create: `hff-telegram-bot/tests/unit/test_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_registry.py
from pathlib import Path
import pytest
from cryptography.fernet import Fernet
from bot.store.db import init_state_db
from bot.store.crypto import Cryptor
from bot.store.registry import Registry, RegistryEntry, AliasExists, UnknownAlias

@pytest.fixture
def reg(tmp_path: Path) -> Registry:
    db = tmp_path / "state.db"
    init_state_db(db)
    return Registry(db, Cryptor(Fernet.generate_key().decode()),
                    media_root=tmp_path / "media")

def test_add_sqlite_roundtrip(reg: Registry, tmp_path: Path) -> None:
    sqlite_file = tmp_path / "hff.sqlite"
    sqlite_file.touch()
    reg.add_sqlite(alias="tabarjah-2025", sqlite_path=sqlite_file, created_by=42)
    entry = reg.get("tabarjah-2025")
    assert entry.server_type == "sqlite"
    assert entry.conn_params["sqlite_path"] == str(sqlite_file)
    assert entry.media_base_path.name == "tabarjah-2025"

def test_add_duplicate_alias_raises(reg: Registry, tmp_path: Path) -> None:
    sqlite_file = tmp_path / "hff.sqlite"; sqlite_file.touch()
    reg.add_sqlite("a1", sqlite_file, created_by=1)
    with pytest.raises(AliasExists):
        reg.add_sqlite("a1", sqlite_file, created_by=1)

def test_list_returns_all(reg: Registry, tmp_path: Path) -> None:
    for n in ("a1", "a2", "a3"):
        f = tmp_path / f"{n}.sqlite"; f.touch()
        reg.add_sqlite(n, f, created_by=1)
    assert sorted(e.alias for e in reg.list_all()) == ["a1", "a2", "a3"]

def test_get_unknown_raises(reg: Registry) -> None:
    with pytest.raises(UnknownAlias):
        reg.get("nope")

def test_remove(reg: Registry, tmp_path: Path) -> None:
    f = tmp_path / "x.sqlite"; f.touch()
    reg.add_sqlite("x", f, created_by=1)
    reg.remove("x")
    with pytest.raises(UnknownAlias):
        reg.get("x")
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/store/registry.py`**

```python
# bot/store/registry.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from bot.store.db import connect
from bot.store.crypto import Cryptor

class AliasExists(Exception): ...
class UnknownAlias(Exception): ...

@dataclass(frozen=True)
class RegistryEntry:
    alias: str
    server_type: str
    conn_params: dict
    media_base_path: Path
    created_by: int
    created_at: str
    last_health_ok: str | None
    last_health_err: str | None

class Registry:
    def __init__(self, db_path: Path, cryptor: Cryptor, media_root: Path) -> None:
        self._db_path = db_path
        self._cryptor = cryptor
        self._media_root = media_root

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_sqlite(self, alias: str, sqlite_path: Path, created_by: int) -> None:
        self._add(alias, "sqlite", {"sqlite_path": str(sqlite_path)}, created_by)

    def _add(self, alias: str, server_type: str, conn_params: dict, created_by: int) -> None:
        media_path = self._media_root / alias
        media_path.mkdir(parents=True, exist_ok=True)
        enc = self._cryptor.encrypt_json(conn_params)
        with connect(self._db_path) as con:
            try:
                con.execute(
                    "INSERT INTO db_registry "
                    "(alias, server_type, conn_params_enc, media_base_path, created_by, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (alias, server_type, enc, str(media_path), created_by, self._now()),
                )
                con.commit()
            except Exception as e:
                if "UNIQUE" in str(e):
                    raise AliasExists(alias) from e
                raise

    def get(self, alias: str) -> RegistryEntry:
        with connect(self._db_path) as con:
            row = con.execute(
                "SELECT * FROM db_registry WHERE alias = ?", (alias,)
            ).fetchone()
        if not row:
            raise UnknownAlias(alias)
        return self._row_to_entry(row)

    def list_all(self) -> list[RegistryEntry]:
        with connect(self._db_path) as con:
            rows = con.execute("SELECT * FROM db_registry ORDER BY alias").fetchall()
        return [self._row_to_entry(r) for r in rows]

    def remove(self, alias: str) -> None:
        with connect(self._db_path) as con:
            cur = con.execute("DELETE FROM db_registry WHERE alias = ?", (alias,))
            con.commit()
        if cur.rowcount == 0:
            raise UnknownAlias(alias)

    def _row_to_entry(self, row) -> RegistryEntry:
        return RegistryEntry(
            alias=row["alias"],
            server_type=row["server_type"],
            conn_params=self._cryptor.decrypt_json(row["conn_params_enc"]),
            media_base_path=Path(row["media_base_path"]),
            created_by=row["created_by"],
            created_at=row["created_at"],
            last_health_ok=row["last_health_ok"],
            last_health_err=row["last_health_err"],
        )
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
git add bot/store/registry.py tests/unit/test_registry.py
git commit -m "feat: Registry for encrypted DB-target storage (sqlite only in v0.1)"
```

---

### Task 7: `intent_store` with optimistic lock

**Files:**
- Create: `hff-telegram-bot/bot/store/intent_store.py`
- Create: `hff-telegram-bot/tests/unit/test_intent_store.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_intent_store.py
from pathlib import Path
import pytest
from bot.store.db import init_state_db
from bot.store.intent_store import IntentStore, IntentStatus, EntityType

@pytest.fixture
def store(tmp_path: Path) -> IntentStore:
    db = tmp_path / "state.db"
    init_state_db(db)
    return IntentStore(db)

def test_enqueue_returns_intent_with_pending_status(store: IntentStore) -> None:
    intent = store.enqueue(user_chat_id=42, db_alias="a1",
                            entity_type=EntityType.SITE,
                            payload={"sito": "Alice B", "nazione": "LB"})
    assert intent.status == IntentStatus.PENDING
    assert intent.retry_count == 0
    assert intent.idempotency_key  # UUID populated

def test_claim_pending_marks_as_flushing(store: IntentStore) -> None:
    intent = store.enqueue(42, "a1", EntityType.SITE, {"sito": "X", "nazione": "LB"})
    claimed = store.claim_pending(intent.id)
    assert claimed is not None
    assert claimed.status == IntentStatus.FLUSHING

def test_claim_pending_returns_none_if_already_claimed(store: IntentStore) -> None:
    intent = store.enqueue(42, "a1", EntityType.SITE, {"sito": "X", "nazione": "LB"})
    assert store.claim_pending(intent.id) is not None
    assert store.claim_pending(intent.id) is None  # lock held

def test_mark_flushed_records_entity_id(store: IntentStore) -> None:
    intent = store.enqueue(42, "a1", EntityType.SITE, {"sito": "X", "nazione": "LB"})
    store.claim_pending(intent.id)
    store.mark_flushed(intent.id, target_entity_id=777)
    after = store.get(intent.id)
    assert after.status == IntentStatus.FLUSHED
    assert after.target_entity_id == 777

def test_mark_failed_increments_retry(store: IntentStore) -> None:
    intent = store.enqueue(42, "a1", EntityType.SITE, {"sito": "X", "nazione": "LB"})
    store.claim_pending(intent.id)
    store.mark_failed(intent.id, error="conn refused")
    after = store.get(intent.id)
    assert after.status == IntentStatus.FAILED
    assert after.retry_count == 1
    assert after.last_error == "conn refused"

def test_list_pending_due_excludes_failed_within_backoff(store: IntentStore) -> None:
    # All freshly pending intents are due
    i1 = store.enqueue(42, "a1", EntityType.SITE, {"sito": "A", "nazione": "LB"})
    i2 = store.enqueue(42, "a1", EntityType.SITE, {"sito": "B", "nazione": "LB"})
    due = store.list_pending_due()
    assert {d.id for d in due} == {i1.id, i2.id}
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/store/intent_store.py`**

```python
# bot/store/intent_store.py
from __future__ import annotations
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from bot.store.db import connect

class EntityType(str, Enum):
    SITE = "SITE"
    SHIPWRECK = "SHIPWRECK"
    DIVELOG = "DIVELOG"
    ARTEFACT = "ARTEFACT"
    ANCHOR = "ANCHOR"
    POTTERY = "POTTERY"

class IntentStatus(str, Enum):
    PENDING = "pending"
    FLUSHING = "flushing"
    FLUSHED = "flushed"
    FAILED = "failed"
    POISON = "poison"
    DISCARDED = "discarded"

@dataclass(frozen=True)
class Intent:
    id: int
    idempotency_key: str
    user_chat_id: int
    db_alias: str
    entity_type: EntityType
    payload: dict
    status: IntentStatus
    retry_count: int
    last_error: str | None
    created_at: str
    flushed_at: str | None
    target_entity_id: int | None

class IntentStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def enqueue(self, user_chat_id: int, db_alias: str,
                entity_type: EntityType, payload: dict) -> Intent:
        with connect(self._db_path) as con:
            cur = con.execute(
                "INSERT INTO pending_intents "
                "(idempotency_key, user_chat_id, db_alias, entity_type, payload_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), user_chat_id, db_alias,
                 entity_type.value, json.dumps(payload), self._now()),
            )
            con.commit()
            new_id = cur.lastrowid
        return self.get(new_id)

    def get(self, intent_id: int) -> Intent:
        with connect(self._db_path) as con:
            row = con.execute(
                "SELECT * FROM pending_intents WHERE id = ?", (intent_id,)
            ).fetchone()
        if not row:
            raise KeyError(intent_id)
        return self._row_to_intent(row)

    def claim_pending(self, intent_id: int) -> Intent | None:
        """Optimistic lock: returns intent only if it was pending and got claimed."""
        with connect(self._db_path) as con:
            cur = con.execute(
                "UPDATE pending_intents SET status = 'flushing' "
                "WHERE id = ? AND status = 'pending'",
                (intent_id,),
            )
            con.commit()
            if cur.rowcount == 0:
                return None
        return self.get(intent_id)

    def mark_flushed(self, intent_id: int, target_entity_id: int) -> None:
        with connect(self._db_path) as con:
            con.execute(
                "UPDATE pending_intents SET status = 'flushed', "
                "flushed_at = ?, target_entity_id = ? WHERE id = ?",
                (self._now(), target_entity_id, intent_id),
            )
            con.commit()

    def mark_failed(self, intent_id: int, error: str) -> None:
        with connect(self._db_path) as con:
            con.execute(
                "UPDATE pending_intents SET status = 'failed', "
                "retry_count = retry_count + 1, last_error = ? WHERE id = ?",
                (error, intent_id),
            )
            con.commit()

    def mark_poison(self, intent_id: int, error: str) -> None:
        with connect(self._db_path) as con:
            con.execute(
                "UPDATE pending_intents SET status = 'poison', "
                "last_error = ? WHERE id = ?",
                (error, intent_id),
            )
            con.commit()

    def list_pending_due(self) -> list[Intent]:
        """v0.1: no backoff — returns all pending intents. Extend in v0.5."""
        with connect(self._db_path) as con:
            rows = con.execute(
                "SELECT * FROM pending_intents WHERE status = 'pending' "
                "ORDER BY id ASC"
            ).fetchall()
        return [self._row_to_intent(r) for r in rows]

    def list_by_user(self, user_chat_id: int, limit: int = 10) -> list[Intent]:
        with connect(self._db_path) as con:
            rows = con.execute(
                "SELECT * FROM pending_intents WHERE user_chat_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (user_chat_id, limit),
            ).fetchall()
        return [self._row_to_intent(r) for r in rows]

    def discard(self, intent_id: int) -> None:
        with connect(self._db_path) as con:
            con.execute(
                "UPDATE pending_intents SET status = 'discarded' "
                "WHERE id = ? AND status IN ('pending', 'failed', 'poison')",
                (intent_id,),
            )
            con.commit()

    @staticmethod
    def _row_to_intent(row) -> Intent:
        return Intent(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            user_chat_id=row["user_chat_id"],
            db_alias=row["db_alias"],
            entity_type=EntityType(row["entity_type"]),
            payload=json.loads(row["payload_json"]),
            status=IntentStatus(row["status"]),
            retry_count=row["retry_count"],
            last_error=row["last_error"],
            created_at=row["created_at"],
            flushed_at=row["flushed_at"],
            target_entity_id=row["target_entity_id"],
        )
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
git add bot/store/intent_store.py tests/unit/test_intent_store.py
git commit -m "feat: IntentStore with CRUD + optimistic lock for flusher"
```

---

### Task 8: Media spool with sha256 dedupe

**Files:**
- Create: `hff-telegram-bot/bot/media/__init__.py`
- Create: `hff-telegram-bot/bot/media/spool.py`
- Create: `hff-telegram-bot/tests/unit/test_spool.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_spool.py
from pathlib import Path
import pytest
from bot.store.db import init_state_db
from bot.store.intent_store import IntentStore, EntityType
from bot.media.spool import MediaSpool, Mediatype

@pytest.fixture
def spool_setup(tmp_path: Path):
    db = tmp_path / "state.db"
    init_state_db(db)
    intents = IntentStore(db)
    intent = intents.enqueue(42, "a1", EntityType.SITE, {"sito": "A", "nazione": "LB"})
    spool = MediaSpool(db_path=db, spool_root=tmp_path / "spool")
    return intent, spool

def test_store_bytes_returns_path_and_dedupes(spool_setup) -> None:
    intent, spool = spool_setup
    content = b"fake-jpeg-bytes"
    row1 = spool.store(intent_id=intent.id, telegram_file_id="tg1",
                        content=content, filetype="jpg", mediatype=Mediatype.IMAGE,
                        original_name="A1")
    row2 = spool.store(intent_id=intent.id, telegram_file_id="tg1",
                        content=content, filetype="jpg", mediatype=Mediatype.IMAGE,
                        original_name="A1")
    # Same sha256 + same intent → same row returned
    assert row1.id == row2.id
    assert Path(row1.local_path).exists()

def test_store_different_content_creates_new_row(spool_setup) -> None:
    intent, spool = spool_setup
    a = spool.store(intent.id, "tg1", b"aaa", "jpg", Mediatype.IMAGE, "A1")
    b = spool.store(intent.id, "tg2", b"bbb", "jpg", Mediatype.IMAGE, "A2")
    assert a.id != b.id

def test_list_for_intent(spool_setup) -> None:
    intent, spool = spool_setup
    spool.store(intent.id, "tg1", b"aaa", "jpg", Mediatype.IMAGE, "A1")
    spool.store(intent.id, "tg2", b"bbb", "jpg", Mediatype.IMAGE, "A2")
    rows = spool.list_for_intent(intent.id)
    assert len(rows) == 2
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/media/__init__.py` (empty) and `bot/media/spool.py`**

```python
# bot/media/spool.py
from __future__ import annotations
import hashlib
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from bot.store.db import connect

class Mediatype(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

@dataclass(frozen=True)
class SpoolRow:
    id: int
    intent_id: int
    telegram_file_id: str
    local_path: str
    original_name: str | None
    mediatype: Mediatype
    filetype: str
    sha256: str
    final_media_id: int | None
    final_filepath: str | None

class MediaSpool:
    def __init__(self, db_path: Path, spool_root: Path) -> None:
        self._db_path = db_path
        self._spool_root = spool_root
        self._spool_root.mkdir(parents=True, exist_ok=True)

    def store(self, intent_id: int, telegram_file_id: str, content: bytes,
              filetype: str, mediatype: Mediatype, original_name: str) -> SpoolRow:
        sha = hashlib.sha256(content).hexdigest()
        with connect(self._db_path) as con:
            existing = con.execute(
                "SELECT * FROM media_spool WHERE intent_id = ? AND sha256 = ?",
                (intent_id, sha),
            ).fetchone()
            if existing:
                return self._row_to_spool(existing)
            local = self._spool_root / f"{uuid.uuid4().hex}.{filetype}"
            local.write_bytes(content)
            cur = con.execute(
                "INSERT INTO media_spool "
                "(intent_id, telegram_file_id, local_path, original_name, "
                " mediatype, filetype, sha256) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (intent_id, telegram_file_id, str(local), original_name,
                 mediatype.value, filetype, sha),
            )
            con.commit()
            return self._get_by_id(cur.lastrowid)

    def list_for_intent(self, intent_id: int) -> list[SpoolRow]:
        with connect(self._db_path) as con:
            rows = con.execute(
                "SELECT * FROM media_spool WHERE intent_id = ? ORDER BY id",
                (intent_id,),
            ).fetchall()
        return [self._row_to_spool(r) for r in rows]

    def _get_by_id(self, id_: int) -> SpoolRow:
        with connect(self._db_path) as con:
            row = con.execute(
                "SELECT * FROM media_spool WHERE id = ?", (id_,)
            ).fetchone()
        return self._row_to_spool(row)

    def update_finalized(self, spool_id: int, final_media_id: int, final_filepath: str) -> None:
        with connect(self._db_path) as con:
            con.execute(
                "UPDATE media_spool SET final_media_id = ?, final_filepath = ? "
                "WHERE id = ?",
                (final_media_id, final_filepath, spool_id),
            )
            con.commit()

    def delete_local_file(self, spool_id: int) -> None:
        row = self._get_by_id(spool_id)
        Path(row.local_path).unlink(missing_ok=True)

    @staticmethod
    def _row_to_spool(row) -> SpoolRow:
        return SpoolRow(
            id=row["id"], intent_id=row["intent_id"],
            telegram_file_id=row["telegram_file_id"], local_path=row["local_path"],
            original_name=row["original_name"], mediatype=Mediatype(row["mediatype"]),
            filetype=row["filetype"], sha256=row["sha256"],
            final_media_id=row["final_media_id"], final_filepath=row["final_filepath"],
        )
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
git add bot/media/__init__.py bot/media/spool.py tests/unit/test_spool.py
git commit -m "feat: MediaSpool with sha256 dedupe per intent"
```

---

### Task 9: Media finalization (thumbnail + resize) — `media/ops.py`

**Files:**
- Create: `hff-telegram-bot/bot/media/ops.py`
- Create: `hff-telegram-bot/tests/unit/test_media_ops.py`
- Create: `hff-telegram-bot/tests/fixtures/sample.jpg` (see Step 1)

- [ ] **Step 1: Create a sample image fixture**

```bash
mkdir -p tests/fixtures
python -c "
import cv2, numpy as np
img = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
cv2.imwrite('tests/fixtures/sample.jpg', img)
"
```

- [ ] **Step 2: Write the failing test**

```python
# tests/unit/test_media_ops.py
from pathlib import Path
import cv2
import pytest
from bot.media.ops import finalize_image, slugify_site, FinalizedMedia

SAMPLE = Path(__file__).parent.parent / "fixtures" / "sample.jpg"

def test_slugify_site() -> None:
    assert slugify_site("Alice B Wreck") == "alice-b-wreck"
    assert slugify_site("Cement Wreck  ") == "cement-wreck"
    assert slugify_site("Site/With\\Bad:Chars") == "site-with-bad-chars"

def test_finalize_image_creates_thumb_and_resize(tmp_path: Path) -> None:
    alias_base = tmp_path / "a1"
    result = finalize_image(
        source=SAMPLE,
        alias_base=alias_base,
        site_slug="alice-b-wreck",
        id_media=123,
        original_name="A1",
        filetype="jpg",
    )
    assert isinstance(result, FinalizedMedia)
    assert result.id_media == 123
    thumb = alias_base / "alice-b-wreck" / "thumbnail" / "123_A1_thumb.png"
    resize = alias_base / "alice-b-wreck" / "image_resize" / "123_A1.png"
    assert thumb.exists()
    assert resize.exists()
    # thumb must be 100x100
    t = cv2.imread(str(thumb))
    assert t.shape[:2] == (100, 100)
    # Paths returned are relative to alias_base
    assert result.thumb_relpath == "alice-b-wreck/thumbnail/123_A1_thumb.png"
    assert result.resize_relpath == "alice-b-wreck/image_resize/123_A1.png"
```

- [ ] **Step 3: Run, expect fail.**

- [ ] **Step 4: Implement `bot/media/ops.py`**

```python
# bot/media/ops.py
from __future__ import annotations
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np

@dataclass(frozen=True)
class FinalizedMedia:
    id_media: int
    thumb_relpath: str
    resize_relpath: str

def slugify_site(name: str) -> str:
    lowered = name.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")

def _resize_15x10_300dpi(img: np.ndarray) -> np.ndarray:
    dpi = 300
    cm_to_inch = 0.393701
    w_px = int(15 * cm_to_inch * dpi)
    h_px = int(10 * cm_to_inch * dpi)
    resized = cv2.resize(img, (w_px, h_px), interpolation=cv2.INTER_AREA)
    bg = np.full((h_px, w_px, 3), 255, dtype=np.uint8)
    y = (h_px - resized.shape[0]) // 2
    x = (w_px - resized.shape[1]) // 2
    bg[y:y + resized.shape[0], x:x + resized.shape[1]] = resized
    return bg

def finalize_image(source: Path, alias_base: Path, site_slug: str,
                   id_media: int, original_name: str, filetype: str) -> FinalizedMedia:
    thumb_name = f"{id_media}_{original_name}_thumb.png"
    resize_name = f"{id_media}_{original_name}.png"
    thumb_dir = alias_base / site_slug / "thumbnail"
    resize_dir = alias_base / site_slug / "image_resize"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    resize_dir.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(source))
    if img is None:
        raise ValueError(f"Could not decode image at {source}")
    cv2.imwrite(str(thumb_dir / thumb_name),
                cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA))
    cv2.imwrite(str(resize_dir / resize_name),
                _resize_15x10_300dpi(img),
                [cv2.IMWRITE_PNG_COMPRESSION, 0])
    return FinalizedMedia(
        id_media=id_media,
        thumb_relpath=f"{site_slug}/thumbnail/{thumb_name}",
        resize_relpath=f"{site_slug}/image_resize/{resize_name}",
    )

def finalize_video(source: Path, alias_base: Path, site_slug: str,
                   id_media: int, original_name: str, filetype: str) -> FinalizedMedia:
    thumb_name = f"{id_media}_{original_name}_video.png"
    resize_name = f"{id_media}_{original_name}.{filetype}"
    thumb_dir = alias_base / site_slug / "thumbnail"
    resize_dir = alias_base / site_slug / "image_resize"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    resize_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(source))
    try:
        ret, frame = cap.read()
        while ret and frame is not None and frame.mean() < 1:
            ret, frame = cap.read()
        if frame is None:
            raise ValueError(f"Could not read any frame from {source}")
        cv2.imwrite(str(thumb_dir / thumb_name), cv2.resize(frame, (100, 100)))
    finally:
        cap.release()
    shutil.copy2(source, resize_dir / resize_name)
    return FinalizedMedia(
        id_media=id_media,
        thumb_relpath=f"{site_slug}/thumbnail/{thumb_name}",
        resize_relpath=f"{site_slug}/image_resize/{resize_name}",
    )
```

- [ ] **Step 5: Run, expect pass. Commit.**

```bash
git add bot/media/__init__.py bot/media/ops.py tests/unit/test_media_ops.py tests/fixtures/sample.jpg
git commit -m "feat: media ops (slugify, thumbnail, 15x10@300dpi resize)"
```

---

### Task 10: Add HFF plugin as git submodule

**Files:**
- Create: `hff-telegram-bot/bot/hff_models/` (submodule mount point)
- Modify: `hff-telegram-bot/.gitmodules`

- [ ] **Step 1: Add submodule**

```bash
git submodule add https://github.com/enzococca/HFF.git bot/hff_models_src
git submodule update --init --recursive
```

- [ ] **Step 2: Create a thin re-export module that exposes just what the bot needs**

Create `bot/hff_models/__init__.py`:

```python
# bot/hff_models/__init__.py
"""Thin re-export of HFF plugin schema modules for use inside the bot.

We only need the structures/ and entities/ subpackages. The submodule lives
in bot/hff_models_src/ (the whole plugin repo); we surface the relevant
subset here so bot code has a clean import path.
"""
import sys
from pathlib import Path

_src = Path(__file__).parent.parent / "hff_models_src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from modules.db.structures import Site_table, UW_table, ANC_table, \
    ART_table, POTTERY_table, Shipwreck_table, Media_table, \
    Media_thumb_table, Media_to_Entity_table  # noqa: E402,F401
from modules.db.entities import SITE, UW, ANC, ART, POTTERY, SHIPWRECK  # noqa: E402,F401
```

- [ ] **Step 3: Commit**

```bash
git add .gitmodules bot/hff_models_src bot/hff_models/__init__.py
git commit -m "chore: add HFF plugin as submodule + schema re-exports"
```

---

### Task 11: Target-DB connector + `bot_flushed_intents` management

**Files:**
- Create: `hff-telegram-bot/bot/sync/__init__.py`
- Create: `hff-telegram-bot/bot/sync/target_db.py`
- Create: `hff-telegram-bot/tests/unit/test_target_db.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_target_db.py
from pathlib import Path
import sqlite3
import pytest
from bot.sync.target_db import connect_target, ensure_flushed_intents_table, \
    check_idempotency

def _make_empty_hff_sqlite(path: Path) -> None:
    """Creates an empty file; bot_flushed_intents must be created by ensure_..."""
    sqlite3.connect(path).close()

def test_ensure_creates_table(tmp_path: Path) -> None:
    f = tmp_path / "hff.sqlite"
    _make_empty_hff_sqlite(f)
    engine = connect_target({"sqlite_path": str(f)})
    ensure_flushed_intents_table(engine)
    with engine.connect() as con:
        names = {r[0] for r in con.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    assert "bot_flushed_intents" in names

def test_check_idempotency_returns_none_when_absent(tmp_path: Path) -> None:
    f = tmp_path / "hff.sqlite"
    _make_empty_hff_sqlite(f)
    engine = connect_target({"sqlite_path": str(f)})
    ensure_flushed_intents_table(engine)
    assert check_idempotency(engine, "non-existent-key") is None

def test_check_idempotency_returns_entity_id(tmp_path: Path) -> None:
    f = tmp_path / "hff.sqlite"
    _make_empty_hff_sqlite(f)
    engine = connect_target({"sqlite_path": str(f)})
    ensure_flushed_intents_table(engine)
    with engine.begin() as con:
        con.exec_driver_sql(
            "INSERT INTO bot_flushed_intents (idempotency_key, entity_type, "
            "entity_id, flushed_at) VALUES ('k1', 'SITE', 123, '2026-04-21')"
        )
    assert check_idempotency(engine, "k1") == ("SITE", 123)
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/sync/__init__.py` (empty) and `bot/sync/target_db.py`**

```python
# bot/sync/target_db.py
from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

def connect_target(conn_params: dict) -> Engine:
    if "sqlite_path" in conn_params:
        return create_engine(f"sqlite:///{conn_params['sqlite_path']}", future=True)
    raise ValueError(f"Unsupported conn_params: {conn_params}")

def ensure_flushed_intents_table(engine: Engine) -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS bot_flushed_intents (
        idempotency_key  TEXT PRIMARY KEY,
        entity_type      TEXT NOT NULL,
        entity_id        INTEGER NOT NULL,
        flushed_at       TEXT NOT NULL
    )
    """
    with engine.begin() as con:
        con.execute(text(sql))

def check_idempotency(engine: Engine, key: str) -> tuple[str, int] | None:
    with engine.connect() as con:
        row = con.execute(
            text("SELECT entity_type, entity_id FROM bot_flushed_intents "
                 "WHERE idempotency_key = :k"),
            {"k": key},
        ).fetchone()
    return (row[0], row[1]) if row else None
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
git add bot/sync/__init__.py bot/sync/target_db.py tests/unit/test_target_db.py
git commit -m "feat: target_db connector + bot_flushed_intents idempotency check"
```

---

### Task 12: SITE adapter

**Files:**
- Create: `hff-telegram-bot/bot/sync/adapters/__init__.py`
- Create: `hff-telegram-bot/bot/sync/adapters/base.py`
- Create: `hff-telegram-bot/bot/sync/adapters/site.py`
- Create: `hff-telegram-bot/tests/integration/__init__.py`
- Create: `hff-telegram-bot/tests/integration/test_site_adapter.py`

- [ ] **Step 1: Write the failing integration test**

```python
# tests/integration/test_site_adapter.py
from datetime import datetime, timezone
from pathlib import Path
import cv2
import numpy as np
import pytest
from sqlalchemy import text
from bot.hff_models import Site_table, Media_table, Media_thumb_table, \
    Media_to_Entity_table  # noqa: F401  # trigger create_all
from bot.media.spool import SpoolRow, Mediatype
from bot.sync.target_db import connect_target, ensure_flushed_intents_table
from bot.sync.adapters.site import SiteAdapter

SAMPLE = Path(__file__).parent.parent / "fixtures" / "sample.jpg"

def _prep_blank_hff(path: Path) -> None:
    """Import Site_table etc. to trigger metadata.create_all on this new sqlite."""
    from sqlalchemy import create_engine
    # The hff_models modules call metadata.create_all(engine) at import time
    # using a Connection() config. We can't easily reuse that here — instead we
    # piggyback by letting SQLAlchemy reflect-then-create through a fresh engine.
    eng = create_engine(f"sqlite:///{path}")
    # Re-run create_all via each module's own metadata
    from modules.db.structures.Site_table import SITE_table
    # NOTE: The plugin structures instantiate their own engine tied to Connection();
    # for the test we just manually issue the CREATE TABLE via the plugin's
    # db_structure routine if available, or copy the minimum DDL inline below.
    eng.dispose()
    # Inline DDL for the three tables needed in v0.1:
    import sqlite3
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE site_table (
        id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT,
        nazione TEXT,
        regione TEXT,
        comune TEXT,
        descrizione TEXT,
        provincia TEXT,
        sito_path TEXT DEFAULT '',
        find_check INTEGER DEFAULT 0,
        photo_material TEXT DEFAULT '[[]]',
        damage TEXT DEFAULT '',
        country TEXT DEFAULT ''
    );
    CREATE TABLE media_table (
        id_media INTEGER PRIMARY KEY AUTOINCREMENT,
        mediatype TEXT, filename TEXT, filetype TEXT,
        filepath TEXT, descrizione TEXT, tags TEXT
    );
    CREATE TABLE media_thumb_table (
        id_media_thumb INTEGER PRIMARY KEY AUTOINCREMENT,
        id_media INTEGER, mediatype TEXT,
        media_filename TEXT, media_thumb_filename TEXT,
        filetype TEXT, filepath TEXT, path_resize TEXT,
        CONSTRAINT uq UNIQUE (media_thumb_filename)
    );
    CREATE TABLE media_to_entity_table (
        id_mediatoentity INTEGER PRIMARY KEY AUTOINCREMENT,
        id_entity INTEGER, entity_type TEXT, table_name TEXT,
        id_media INTEGER, filepath TEXT, media_name TEXT,
        CONSTRAINT uq UNIQUE (id_entity, entity_type, id_media)
    );
    """)
    con.commit(); con.close()

def test_flush_site_with_one_photo(tmp_path: Path) -> None:
    hff = tmp_path / "hff.sqlite"
    _prep_blank_hff(hff)
    engine = connect_target({"sqlite_path": str(hff)})
    ensure_flushed_intents_table(engine)

    spool_file = tmp_path / "pic.jpg"
    img = cv2.imread(str(SAMPLE))
    cv2.imwrite(str(spool_file), img)

    media_spool = [SpoolRow(
        id=1, intent_id=1, telegram_file_id="tg1", local_path=str(spool_file),
        original_name="view1", mediatype=Mediatype.IMAGE, filetype="jpg",
        sha256="x" * 64, final_media_id=None, final_filepath=None,
    )]
    adapter = SiteAdapter(engine=engine, alias_base=tmp_path / "a1",
                           idempotency_key="key-1")
    id_sito = adapter.flush(
        payload={"sito": "Alice B Wreck", "nazione": "LB"},
        media_spool=media_spool,
    )

    with engine.connect() as con:
        row = con.execute(
            text("SELECT id_sito, sito, nazione FROM site_table WHERE id_sito=:i"),
            {"i": id_sito}).fetchone()
        assert row.sito == "Alice B Wreck"
        assert row.nazione == "LB"

        media_count = con.execute(text("SELECT COUNT(*) FROM media_table")).scalar()
        thumb_count = con.execute(text("SELECT COUNT(*) FROM media_thumb_table")).scalar()
        link_count = con.execute(text(
            "SELECT COUNT(*) FROM media_to_entity_table WHERE entity_type='SITE'"
        )).scalar()
        assert (media_count, thumb_count, link_count) == (1, 1, 1)

        idem = con.execute(text(
            "SELECT entity_id FROM bot_flushed_intents WHERE idempotency_key='key-1'"
        )).fetchone()
        assert idem.entity_id == id_sito

    thumb = tmp_path / "a1" / "alice-b-wreck" / "thumbnail" / "1_view1_thumb.png"
    resize = tmp_path / "a1" / "alice-b-wreck" / "image_resize" / "1_view1.png"
    assert thumb.exists() and resize.exists()

def test_flush_is_idempotent(tmp_path: Path) -> None:
    hff = tmp_path / "hff.sqlite"
    _prep_blank_hff(hff)
    engine = connect_target({"sqlite_path": str(hff)})
    ensure_flushed_intents_table(engine)
    adapter = SiteAdapter(engine=engine, alias_base=tmp_path / "a1",
                           idempotency_key="same-key")
    a = adapter.flush({"sito": "X", "nazione": "LB"}, media_spool=[])
    b = adapter.flush({"sito": "X", "nazione": "LB"}, media_spool=[])
    assert a == b
    with engine.connect() as con:
        count = con.execute(text("SELECT COUNT(*) FROM site_table")).scalar()
    assert count == 1
```

- [ ] **Step 2: Run, expect fail (module not found).**

- [ ] **Step 3: Implement `bot/sync/adapters/__init__.py` (empty) and `bot/sync/adapters/base.py`**

```python
# bot/sync/adapters/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from sqlalchemy.engine import Engine
from bot.media.spool import SpoolRow
from bot.sync.target_db import check_idempotency

class BaseAdapter(ABC):
    def __init__(self, engine: Engine, alias_base: Path, idempotency_key: str) -> None:
        self.engine = engine
        self.alias_base = alias_base
        self.idempotency_key = idempotency_key

    def flush(self, payload: dict, media_spool: list[SpoolRow]) -> int:
        existing = check_idempotency(self.engine, self.idempotency_key)
        if existing is not None:
            return existing[1]
        return self._do_flush(payload, media_spool)

    @abstractmethod
    def _do_flush(self, payload: dict, media_spool: list[SpoolRow]) -> int: ...
```

- [ ] **Step 4: Implement `bot/sync/adapters/site.py`**

```python
# bot/sync/adapters/site.py
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import text
from bot.media.ops import finalize_image, finalize_video, slugify_site
from bot.media.spool import SpoolRow, Mediatype
from bot.sync.adapters.base import BaseAdapter

ENTITY_TYPE = "SITE"
TABLE_NAME = "site_table"
MEDIA_ENTITY_CODE = "SITE"

class SiteAdapter(BaseAdapter):
    def _do_flush(self, payload: dict, media_spool: list[SpoolRow]) -> int:
        sito = payload["sito"]
        nazione = payload["nazione"]
        slug = slugify_site(sito)
        with self.engine.begin() as con:
            result = con.execute(
                text("INSERT INTO site_table (sito, nazione, regione, comune, "
                     "descrizione, provincia) VALUES (:sito, :nazione, :reg, "
                     ":com, :descr, :prov)"),
                {"sito": sito, "nazione": nazione,
                 "reg": payload.get("regione", ""),
                 "com": payload.get("comune", ""),
                 "descr": payload.get("descrizione", ""),
                 "prov": payload.get("provincia", "")},
            )
            id_sito = result.lastrowid
            for spool in media_spool:
                next_id = con.execute(
                    text("SELECT COALESCE(MAX(id_media), 0) FROM media_table")
                ).scalar() + 1
                source = Path(spool.local_path)
                if spool.mediatype == Mediatype.IMAGE:
                    fin = finalize_image(source=source, alias_base=self.alias_base,
                                          site_slug=slug, id_media=next_id,
                                          original_name=spool.original_name or "media",
                                          filetype=spool.filetype)
                else:
                    fin = finalize_video(source=source, alias_base=self.alias_base,
                                          site_slug=slug, id_media=next_id,
                                          original_name=spool.original_name or "media",
                                          filetype=spool.filetype)
                con.execute(
                    text("INSERT INTO media_table (id_media, mediatype, filename, "
                         "filetype, filepath, descrizione, tags) VALUES "
                         "(:id, :mt, :fn, :ft, :fp, :d, :tg)"),
                    {"id": next_id, "mt": spool.mediatype.value,
                     "fn": spool.original_name or "media",
                     "ft": spool.filetype, "fp": fin.resize_relpath,
                     "d": "Insert description", "tg": "['image']"},
                )
                con.execute(
                    text("INSERT INTO media_thumb_table (id_media, mediatype, "
                         "media_filename, media_thumb_filename, filetype, "
                         "filepath, path_resize) VALUES "
                         "(:idm, :mt, :fn, :tn, :ft, :fp, :pr)"),
                    {"idm": next_id, "mt": spool.mediatype.value,
                     "fn": spool.original_name or "media",
                     "tn": fin.thumb_relpath.rsplit("/", 1)[1],
                     "ft": spool.filetype, "fp": fin.thumb_relpath,
                     "pr": fin.resize_relpath},
                )
                con.execute(
                    text("INSERT INTO media_to_entity_table (id_entity, entity_type, "
                         "table_name, id_media, filepath, media_name) VALUES "
                         "(:ie, :et, :tn, :idm, :fp, :mn)"),
                    {"ie": id_sito, "et": MEDIA_ENTITY_CODE, "tn": TABLE_NAME,
                     "idm": next_id, "fp": fin.resize_relpath,
                     "mn": spool.original_name or "media"},
                )
                # Note: spool rows updated by the caller (flusher) after commit
            con.execute(
                text("INSERT INTO bot_flushed_intents (idempotency_key, entity_type, "
                     "entity_id, flushed_at) VALUES (:k, :et, :eid, :ts)"),
                {"k": self.idempotency_key, "et": ENTITY_TYPE,
                 "eid": id_sito, "ts": datetime.now(timezone.utc).isoformat()},
            )
        return id_sito
```

- [ ] **Step 5: Run integration test, expect pass. Commit.**

```bash
pytest tests/integration/test_site_adapter.py -v
git add bot/sync/adapters/__init__.py bot/sync/adapters/base.py \
        bot/sync/adapters/site.py tests/integration/__init__.py \
        tests/integration/test_site_adapter.py
git commit -m "feat: SITE adapter with media, idempotency, atomic transaction"
```

---

### Task 13: Flusher — orchestration + error classification

**Files:**
- Create: `hff-telegram-bot/bot/sync/flusher.py`
- Create: `hff-telegram-bot/tests/integration/test_flusher.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/integration/test_flusher.py
from pathlib import Path
import cv2, sqlite3, pytest
from cryptography.fernet import Fernet
from sqlalchemy import text
from bot.store.db import init_state_db
from bot.store.crypto import Cryptor
from bot.store.registry import Registry
from bot.store.intent_store import IntentStore, EntityType, IntentStatus
from bot.media.spool import MediaSpool, Mediatype
from bot.sync.flusher import Flusher
from tests.integration.test_site_adapter import _prep_blank_hff

SAMPLE = Path(__file__).parent.parent / "fixtures" / "sample.jpg"

@pytest.fixture
def setup(tmp_path):
    state = tmp_path / "state.db"
    init_state_db(state)
    cryptor = Cryptor(Fernet.generate_key().decode())
    registry = Registry(state, cryptor, media_root=tmp_path / "media")
    intents = IntentStore(state)
    spool = MediaSpool(state, tmp_path / "spool")
    hff = tmp_path / "hff.sqlite"
    _prep_blank_hff(hff)
    registry.add_sqlite("a1", hff, created_by=42)
    return state, registry, intents, spool, hff, tmp_path / "media"

def test_flusher_flushes_pending_intent(setup):
    state, registry, intents, spool, hff, media_root = setup
    intent = intents.enqueue(42, "a1", EntityType.SITE,
                              {"sito": "Alice B", "nazione": "LB"})
    img_bytes = SAMPLE.read_bytes()
    spool.store(intent.id, "tg1", img_bytes, "jpg", Mediatype.IMAGE, "v1")

    flusher = Flusher(registry, intents, spool)
    flusher.flush_one(intent.id)

    after = intents.get(intent.id)
    assert after.status == IntentStatus.FLUSHED
    assert after.target_entity_id is not None

    from bot.sync.target_db import connect_target
    engine = connect_target({"sqlite_path": str(hff)})
    with engine.connect() as con:
        n = con.execute(text("SELECT COUNT(*) FROM site_table")).scalar()
    assert n == 1

def test_flusher_marks_failed_on_recoverable_error(setup, monkeypatch):
    state, registry, intents, spool, hff, media_root = setup
    intent = intents.enqueue(42, "a1", EntityType.SITE,
                              {"sito": "X", "nazione": "LB"})
    hff.unlink()  # simulate DB unreachable

    flusher = Flusher(registry, intents, spool)
    flusher.flush_one(intent.id)

    after = intents.get(intent.id)
    assert after.status in (IntentStatus.FAILED, IntentStatus.POISON)
    assert after.retry_count >= 1 or after.status == IntentStatus.POISON
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/sync/flusher.py`**

```python
# bot/sync/flusher.py
from __future__ import annotations
import socket
import traceback
import structlog
from sqlalchemy.exc import (OperationalError, IntegrityError, DataError,
                             ProgrammingError, DBAPIError)
from bot.store.intent_store import IntentStore, Intent, EntityType
from bot.store.registry import Registry
from bot.media.spool import MediaSpool
from bot.sync.target_db import connect_target, ensure_flushed_intents_table
from bot.sync.adapters.site import SiteAdapter

log = structlog.get_logger()

RECOVERABLE = (OperationalError, TimeoutError, socket.gaierror)
FATAL = (IntegrityError, DataError, ProgrammingError)

ADAPTERS = {EntityType.SITE: SiteAdapter}

class Flusher:
    def __init__(self, registry: Registry, intents: IntentStore, spool: MediaSpool) -> None:
        self.registry = registry
        self.intents = intents
        self.spool = spool

    def flush_one(self, intent_id: int) -> None:
        claimed = self.intents.claim_pending(intent_id)
        if claimed is None:
            return
        try:
            entry = self.registry.get(claimed.db_alias)
            engine = connect_target(entry.conn_params)
            ensure_flushed_intents_table(engine)
            adapter_cls = ADAPTERS.get(claimed.entity_type)
            if adapter_cls is None:
                self.intents.mark_poison(
                    claimed.id,
                    f"No adapter registered for {claimed.entity_type.value}")
                return
            adapter = adapter_cls(engine=engine, alias_base=entry.media_base_path,
                                   idempotency_key=claimed.idempotency_key)
            spool_rows = self.spool.list_for_intent(claimed.id)
            entity_id = adapter.flush(claimed.payload, spool_rows)
            for s in spool_rows:
                self.spool.delete_local_file(s.id)
            self.intents.mark_flushed(claimed.id, target_entity_id=entity_id)
            log.info("intent_flushed", intent_id=claimed.id, entity_id=entity_id,
                     alias=claimed.db_alias)
        except RECOVERABLE as e:
            self.intents.mark_failed(claimed.id, error=str(e))
            log.warning("intent_failed_recoverable", intent_id=claimed.id, error=str(e))
        except FATAL as e:
            self.intents.mark_poison(claimed.id, error=str(e))
            log.error("intent_poisoned_fatal", intent_id=claimed.id, error=str(e))
        except Exception as e:
            self.intents.mark_poison(
                claimed.id,
                error=f"UNEXPECTED: {e}\n{traceback.format_exc()}")
            log.error("intent_poisoned_unexpected", intent_id=claimed.id, error=str(e))
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
pytest tests/integration/test_flusher.py -v
git add bot/sync/flusher.py tests/integration/test_flusher.py
git commit -m "feat: Flusher with error classification (recoverable/fatal/unexpected)"
```

---

### Task 14: Scheduler — periodic drain task

**Files:**
- Create: `hff-telegram-bot/bot/sync/scheduler.py`
- Create: `hff-telegram-bot/tests/unit/test_scheduler.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_scheduler.py
import asyncio
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from bot.store.db import init_state_db
from bot.store.intent_store import IntentStore, EntityType
from bot.sync.scheduler import Scheduler

@pytest.mark.asyncio
async def test_scheduler_calls_flusher_for_pending_intents(tmp_path: Path) -> None:
    state = tmp_path / "state.db"
    init_state_db(state)
    intents = IntentStore(state)
    flusher = MagicMock()
    intents.enqueue(42, "a1", EntityType.SITE, {"sito": "A", "nazione": "LB"})
    intents.enqueue(42, "a1", EntityType.SITE, {"sito": "B", "nazione": "LB"})

    scheduler = Scheduler(intents=intents, flusher=flusher, interval_seconds=0.01)
    task = asyncio.create_task(scheduler.run())
    await asyncio.sleep(0.05)
    scheduler.stop()
    await task

    assert flusher.flush_one.call_count >= 2
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement `bot/sync/scheduler.py`**

```python
# bot/sync/scheduler.py
from __future__ import annotations
import asyncio
import structlog
from bot.store.intent_store import IntentStore

log = structlog.get_logger()

class Scheduler:
    def __init__(self, intents: IntentStore, flusher, interval_seconds: float) -> None:
        self.intents = intents
        self.flusher = flusher
        self.interval_seconds = interval_seconds
        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    async def run(self) -> None:
        log.info("scheduler_started", interval=self.interval_seconds)
        while not self._stop.is_set():
            try:
                for intent in self.intents.list_pending_due():
                    self.flusher.flush_one(intent.id)
            except Exception as e:
                log.error("scheduler_tick_error", error=str(e))
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                pass
        log.info("scheduler_stopped")
```

- [ ] **Step 4: Run, expect pass. Commit.**

```bash
git add bot/sync/scheduler.py tests/unit/test_scheduler.py
git commit -m "feat: async Scheduler draining pending intents every N seconds"
```

---

### Task 15: Aiogram bootstrap + auth middleware + `/start`

**Files:**
- Create: `hff-telegram-bot/bot/main.py`
- Create: `hff-telegram-bot/bot/handlers/__init__.py`
- Create: `hff-telegram-bot/bot/handlers/common.py`
- Create: `hff-telegram-bot/bot/handlers/middleware.py`
- Create: `hff-telegram-bot/tests/unit/test_handlers_common.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_handlers_common.py
import pytest
from pathlib import Path
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE
from bot.store.db import init_state_db
from bot.store.user_store import UserStore, Role
from bot.handlers.common import start_handler

@pytest.mark.asyncio
async def test_start_bootstraps_admin_for_boot_chat_id(tmp_path: Path) -> None:
    state = tmp_path / "state.db"; init_state_db(state)
    users = UserStore(state)
    req = MessageHandler(start_handler, state=None,
                          dp_kwargs={"users": users, "boot_admin_chat_id": 42})
    MESSAGE["from"]["id"] = 42; MESSAGE["chat"]["id"] = 42
    MESSAGE["text"] = "/start"
    calls = await req.query(message=MESSAGE)
    assert users.get(42).role == Role.ADMIN
    # Check a reply was sent
    assert calls.send_message.count > 0
    assert "Welcome" in calls.send_message.fetchone().text
```

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Create `bot/handlers/__init__.py` (empty) and `bot/handlers/middleware.py`**

```python
# bot/handlers/middleware.py
from __future__ import annotations
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.store.user_store import UserStore, UserNotFound, Role

class AuthMiddleware(BaseMiddleware):
    """Attach `user` to handler data if the caller is in the allowlist.

    For unauthorized callers (chat_id not in users table), forwards the update
    anyway so /start can handle bootstrap. All other handlers check data["user"].
    """
    def __init__(self, users: UserStore) -> None:
        self.users = users

    async def __call__(self, handler, event: TelegramObject, data: dict):
        chat_id = None
        if hasattr(event, "from_user") and event.from_user:
            chat_id = event.from_user.id
        try:
            data["user"] = self.users.get(chat_id) if chat_id else None
        except UserNotFound:
            data["user"] = None
        return await handler(event, data)

def require_role(role: Role):
    """Decorator: handler skipped if user is not at least `role`."""
    def deco(handler):
        async def wrapper(event, **data):
            user = data.get("user")
            if user is None:
                await event.answer("You are not authorized. Ask an admin to /invite you.")
                return
            if role == Role.ADMIN and user.role != Role.ADMIN:
                await event.answer("This command is admin-only.")
                return
            return await handler(event, **data)
        return wrapper
    return deco
```

- [ ] **Step 4: Create `bot/handlers/common.py`**

```python
# bot/handlers/common.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.store.user_store import UserStore, UserNotFound

router = Router(name="common")

async def start_handler(message: Message, users: UserStore,
                         boot_admin_chat_id: int) -> None:
    chat_id = message.from_user.id
    name = message.from_user.full_name or str(chat_id)
    # Bootstrap admin on first /start from BOOT_ADMIN_CHAT_ID
    if chat_id == boot_admin_chat_id:
        users.bootstrap_admin(chat_id=chat_id, display_name=name)
    try:
        user = users.get(chat_id)
    except UserNotFound:
        await message.answer(
            f"This bot is locked to an allowlist.\n"
            f"Ask an admin to /invite you with your chat_id: {chat_id}"
        )
        return
    await message.answer(
        f"Welcome {user.display_name}. Active DB: {user.active_db_alias or '(none)'}.\n"
        f"Commands: /new_site /list_dbs /use /status"
    )

router.message.register(start_handler, Command("start"))
```

- [ ] **Step 5: Create `bot/main.py` (minimal, just enough to wire things)**

```python
# bot/main.py
from __future__ import annotations
import asyncio
import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import Settings
from bot.store.db import init_state_db
from bot.store.user_store import UserStore
from bot.store.crypto import Cryptor
from bot.store.registry import Registry
from bot.store.intent_store import IntentStore
from bot.media.spool import MediaSpool
from bot.sync.flusher import Flusher
from bot.sync.scheduler import Scheduler
from bot.handlers.middleware import AuthMiddleware
from bot.handlers import common

log = structlog.get_logger()

async def main() -> None:
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    settings = Settings()
    init_state_db(settings.state_db_path)
    users = UserStore(settings.state_db_path)
    cryptor = Cryptor(settings.fernet_key)
    registry = Registry(settings.state_db_path, cryptor,
                         media_root=settings.media_base_path)
    intents = IntentStore(settings.state_db_path)
    spool = MediaSpool(settings.state_db_path, settings.media_base_path / "_spool")
    flusher = Flusher(registry, intents, spool)
    scheduler = Scheduler(intents, flusher, settings.sync_interval_seconds)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(AuthMiddleware(users))
    dp["users"] = users
    dp["registry"] = registry
    dp["intents"] = intents
    dp["spool"] = spool
    dp["boot_admin_chat_id"] = settings.boot_admin_chat_id

    dp.include_router(common.router)

    scheduler_task = asyncio.create_task(scheduler.run())
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.stop()
        await scheduler_task
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 6: Run tests, expect pass. Commit.**

```bash
pytest tests/unit/test_handlers_common.py -v
git add bot/main.py bot/handlers/ tests/unit/test_handlers_common.py
git commit -m "feat: aiogram bootstrap + AuthMiddleware + /start with admin bootstrap"
```

---

### Task 16: `/add_db`, `/list_dbs`, `/use`, `/remove_db`

**Files:**
- Create: `hff-telegram-bot/bot/handlers/admin.py`
- Create: `hff-telegram-bot/tests/unit/test_handlers_admin.py`

- [ ] **Step 1: Write the failing test for each command**

```python
# tests/unit/test_handlers_admin.py
import pytest
from pathlib import Path
from bot.store.db import init_state_db
from bot.store.user_store import UserStore, Role
from bot.store.crypto import Cryptor
from bot.store.registry import Registry
from cryptography.fernet import Fernet

@pytest.fixture
def services(tmp_path: Path):
    state = tmp_path / "state.db"; init_state_db(state)
    users = UserStore(state); users.bootstrap_admin(42, "Enzo")
    cryptor = Cryptor(Fernet.generate_key().decode())
    registry = Registry(state, cryptor, media_root=tmp_path / "media")
    return users, registry, tmp_path

def test_list_dbs_empty_returns_message(services) -> None:
    users, registry, _ = services
    from bot.handlers.admin import format_db_list
    out = format_db_list(registry, active_alias=None)
    assert "no registered" in out.lower()

def test_list_dbs_marks_active(services) -> None:
    users, registry, tmp = services
    f = tmp / "a.sqlite"; f.touch()
    registry.add_sqlite("a1", f, created_by=42)
    from bot.handlers.admin import format_db_list
    out = format_db_list(registry, active_alias="a1")
    assert "a1" in out and "← active" in out
```

- [ ] **Step 2: Implement `bot/handlers/admin.py`** (this file is larger — split into sub-steps; keeping the test above first gives us a fast feedback loop)

```python
# bot/handlers/admin.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from pathlib import Path
from bot.store.registry import Registry, AliasExists, UnknownAlias
from bot.store.user_store import UserStore, Role
from bot.handlers.middleware import require_role

router = Router(name="admin")

class AddDbFsm(StatesGroup):
    waiting_file = State()
    waiting_alias = State()

@router.message(Command("add_db"))
@require_role(Role.ADMIN)
async def cmd_add_db(message: Message, state: FSMContext, **_) -> None:
    await state.set_state(AddDbFsm.waiting_file)
    await message.answer(
        "Send the .sqlite file as a document (drag-and-drop). v0.1 supports "
        "sqlite only; postgres comes in v0.2."
    )

@router.message(AddDbFsm.waiting_file, F.document)
async def receive_sqlite(message: Message, state: FSMContext,
                           registry: Registry, **_) -> None:
    doc = message.document
    if not doc.file_name.endswith((".sqlite", ".db")):
        await message.answer("Expected a .sqlite or .db file.")
        return
    # Download the file to media_root/_uploads/<alias-will-be>/<filename>
    tmp_dir = registry._media_root / "_uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    dst = tmp_dir / doc.file_name
    await message.bot.download(doc, destination=dst)
    await state.update_data(sqlite_path=str(dst))
    await state.set_state(AddDbFsm.waiting_alias)
    await message.answer("Alias for this DB? (a-z 0-9 - _, short)")

@router.message(AddDbFsm.waiting_alias)
async def receive_alias(message: Message, state: FSMContext, registry: Registry,
                         user, **_) -> None:
    alias = message.text.strip()
    if not alias.replace("-", "").replace("_", "").isalnum() or len(alias) > 40:
        await message.answer("Invalid alias. Use a-z 0-9 - _, max 40 chars.")
        return
    data = await state.get_data()
    try:
        registry.add_sqlite(alias=alias, sqlite_path=Path(data["sqlite_path"]),
                              created_by=user.chat_id)
    except AliasExists:
        await message.answer(f"Alias '{alias}' already exists.")
        await state.clear()
        return
    await state.clear()
    await message.answer(f"Registered '{alias}'. Run /use {alias} to make it active.")

def format_db_list(registry: Registry, active_alias: str | None) -> str:
    entries = registry.list_all()
    if not entries:
        return "No registered DBs. Use /add_db (admin only)."
    lines = []
    for e in entries:
        marker = " ← active" if e.alias == active_alias else ""
        lines.append(f"• {e.alias} ({e.server_type}){marker}")
    return "\n".join(lines)

@router.message(Command("list_dbs"))
async def cmd_list_dbs(message: Message, registry: Registry, user, **_) -> None:
    if user is None:
        await message.answer("Unauthorized.")
        return
    await message.answer(format_db_list(registry, active_alias=user.active_db_alias))

@router.message(Command("use"))
async def cmd_use(message: Message, command: CommandObject, users: UserStore,
                    registry: Registry, user, **_) -> None:
    if user is None:
        await message.answer("Unauthorized.")
        return
    alias = (command.args or "").strip()
    if not alias:
        await message.answer("Usage: /use <alias>")
        return
    try:
        registry.get(alias)
    except UnknownAlias:
        await message.answer(f"Unknown alias '{alias}'.")
        return
    users.set_active_db(user.chat_id, alias)
    await message.answer(f"Active DB set to {alias}.")

@router.message(Command("remove_db"))
@require_role(Role.ADMIN)
async def cmd_remove_db(message: Message, command: CommandObject,
                          registry: Registry, **_) -> None:
    alias = (command.args or "").strip()
    if not alias:
        await message.answer("Usage: /remove_db <alias>")
        return
    try:
        registry.remove(alias)
    except UnknownAlias:
        await message.answer(f"Unknown alias '{alias}'.")
        return
    await message.answer(f"Removed '{alias}'.")
```

- [ ] **Step 3: Wire into `bot/main.py`**

Modify `bot/main.py` to `dp.include_router(admin.router)` after `common.router`.

- [ ] **Step 4: Run tests (`test_handlers_admin.py`), expect pass. Commit.**

```bash
pytest tests/unit/test_handlers_admin.py -v
git add bot/handlers/admin.py bot/main.py tests/unit/test_handlers_admin.py
git commit -m "feat: /add_db /list_dbs /use /remove_db (sqlite only for v0.1)"
```

---

### Task 17: SITE wizard FSM

**Files:**
- Create: `hff-telegram-bot/bot/fsm/__init__.py`
- Create: `hff-telegram-bot/bot/fsm/states.py`
- Create: `hff-telegram-bot/bot/keyboards/__init__.py`
- Create: `hff-telegram-bot/bot/keyboards/actions.py`
- Create: `hff-telegram-bot/bot/handlers/entities/__init__.py`
- Create: `hff-telegram-bot/bot/handlers/entities/site.py`
- Create: `hff-telegram-bot/tests/unit/test_site_wizard.py`

- [ ] **Step 1: Write `bot/fsm/states.py`**

```python
# bot/fsm/states.py
from aiogram.fsm.state import State, StatesGroup

class SiteWizard(StatesGroup):
    waiting_sito = State()
    waiting_nazione = State()
    action_menu = State()
    waiting_optional_value = State()
    waiting_photo = State()
    waiting_photo_name = State()
```

- [ ] **Step 2: Write `bot/keyboards/actions.py`**

```python
# bot/keyboards/actions.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def site_action_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏ regione", callback_data="site:edit:regione"),
         InlineKeyboardButton(text="✏ comune", callback_data="site:edit:comune"),
         InlineKeyboardButton(text="✏ provincia", callback_data="site:edit:provincia")],
        [InlineKeyboardButton(text="✏ descrizione", callback_data="site:edit:descrizione")],
        [InlineKeyboardButton(text="📸 photo", callback_data="site:photo")],
        [InlineKeyboardButton(text="✅ save", callback_data="site:save"),
         InlineKeyboardButton(text="❌ cancel", callback_data="site:cancel")],
    ])
```

- [ ] **Step 3: Write `bot/handlers/entities/site.py`**

```python
# bot/handlers/entities/site.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType
from bot.fsm.states import SiteWizard
from bot.keyboards.actions import site_action_menu
from bot.media.spool import MediaSpool, Mediatype
from bot.store.intent_store import IntentStore, EntityType

router = Router(name="site_wizard")

@router.message(Command("new_site"))
async def cmd_new_site(message: Message, state: FSMContext, user, **_) -> None:
    if user is None:
        await message.answer("Unauthorized.")
        return
    if user.active_db_alias is None:
        await message.answer("Set an active DB first: /list_dbs then /use <alias>")
        return
    await state.set_state(SiteWizard.waiting_sito)
    await state.update_data(payload={}, alias=user.active_db_alias, intent_id=None)
    await message.answer(f"New site on {user.active_db_alias}. Site name (sito)?")

@router.message(SiteWizard.waiting_sito)
async def receive_sito(message: Message, state: FSMContext, **_) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Please type the site name.")
        return
    data = await state.get_data()
    data["payload"]["sito"] = message.text.strip()
    await state.update_data(**data)
    await state.set_state(SiteWizard.waiting_nazione)
    await message.answer("Country (nazione)?")

@router.message(SiteWizard.waiting_nazione)
async def receive_nazione(message: Message, state: FSMContext,
                            intents: IntentStore, user, **_) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Please type the country.")
        return
    data = await state.get_data()
    data["payload"]["nazione"] = message.text.strip()
    # Create the intent so we can attach media to it; payload is finalized at save
    intent = intents.enqueue(
        user_chat_id=user.chat_id, db_alias=data["alias"],
        entity_type=EntityType.SITE, payload=data["payload"])
    data["intent_id"] = intent.id
    await state.update_data(**data)
    await state.set_state(SiteWizard.action_menu)
    await message.answer(
        f"Core fields captured (intent #{intent.id}). Pick more or save:",
        reply_markup=site_action_menu())

@router.callback_query(F.data == "site:cancel", SiteWizard.action_menu)
async def cb_cancel(cb: CallbackQuery, state: FSMContext,
                      intents: IntentStore, **_) -> None:
    data = await state.get_data()
    if data.get("intent_id"):
        intents.discard(data["intent_id"])
    await state.clear()
    await cb.message.edit_text("Cancelled.")
    await cb.answer()

@router.callback_query(F.data == "site:save", SiteWizard.action_menu)
async def cb_save(cb: CallbackQuery, state: FSMContext, **_) -> None:
    # Intent is already enqueued; sync worker picks it up.
    data = await state.get_data()
    await state.clear()
    await cb.message.edit_text(
        f"✅ Intent #{data['intent_id']} queued. Flushing to {data['alias']}…")
    await cb.answer()

@router.callback_query(F.data.startswith("site:edit:"), SiteWizard.action_menu)
async def cb_edit(cb: CallbackQuery, state: FSMContext, **_) -> None:
    field = cb.data.split(":", 2)[2]
    await state.update_data(editing_field=field)
    await state.set_state(SiteWizard.waiting_optional_value)
    await cb.message.answer(f"Type new value for '{field}' (or 'skip'):")
    await cb.answer()

@router.message(SiteWizard.waiting_optional_value)
async def receive_optional(message: Message, state: FSMContext,
                              intents: IntentStore, **_) -> None:
    data = await state.get_data()
    field = data["editing_field"]
    val = (message.text or "").strip()
    if val.lower() != "skip":
        data["payload"][field] = val
        # Intent payload is stored as JSON; update by replacing the intent row payload
        # via direct SQL (kept simple in v0.1 — IntentStore.update_payload helper)
        # To avoid API bloat, we re-enqueue and discard the old one:
        old_id = data["intent_id"]
        new_intent = intents.enqueue(
            user_chat_id=message.from_user.id, db_alias=data["alias"],
            entity_type=EntityType.SITE, payload=data["payload"])
        intents.discard(old_id)
        data["intent_id"] = new_intent.id
    await state.update_data(**data)
    await state.set_state(SiteWizard.action_menu)
    await message.answer(f"Updated. Pick more or save (intent #{data['intent_id']}):",
                           reply_markup=site_action_menu())

@router.callback_query(F.data == "site:photo", SiteWizard.action_menu)
async def cb_photo_ask(cb: CallbackQuery, state: FSMContext, **_) -> None:
    await state.set_state(SiteWizard.waiting_photo)
    await cb.message.answer("Send the photo.")
    await cb.answer()

@router.message(SiteWizard.waiting_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext, **_) -> None:
    # Store largest thumbnail
    await state.update_data(pending_photo_file_id=message.photo[-1].file_id)
    await state.set_state(SiteWizard.waiting_photo_name)
    await message.answer("Name for this photo (short, no extension)?")

@router.message(SiteWizard.waiting_photo_name)
async def receive_photo_name(message: Message, state: FSMContext,
                               spool: MediaSpool, bot_obj: object = None, **_) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Type a name or 'cancel'.")
        return
    data = await state.get_data()
    file_info = await message.bot.get_file(data["pending_photo_file_id"])
    buf = await message.bot.download_file(file_info.file_path)
    spool.store(intent_id=data["intent_id"],
                 telegram_file_id=data["pending_photo_file_id"],
                 content=buf.read(), filetype="jpg", mediatype=Mediatype.IMAGE,
                 original_name=name)
    await state.set_state(SiteWizard.action_menu)
    await message.answer(f"Photo '{name}' attached. More?",
                           reply_markup=site_action_menu())
```

- [ ] **Step 4: Write smoke test for the wizard**

```python
# tests/unit/test_site_wizard.py
import pytest
from pathlib import Path
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

from bot.store.db import init_state_db
from bot.store.user_store import UserStore
from bot.store.crypto import Cryptor
from bot.store.registry import Registry
from bot.store.intent_store import IntentStore, IntentStatus
from bot.media.spool import MediaSpool
from cryptography.fernet import Fernet
from bot.handlers.entities.site import cmd_new_site

@pytest.mark.asyncio
async def test_new_site_requires_active_db(tmp_path: Path) -> None:
    state_db = tmp_path / "state.db"; init_state_db(state_db)
    users = UserStore(state_db); users.bootstrap_admin(42, "Enzo")
    user = users.get(42)  # active_db_alias is None
    req = MessageHandler(cmd_new_site, state=None, dp_kwargs={"user": user})
    MESSAGE["from"]["id"] = 42; MESSAGE["chat"]["id"] = 42
    MESSAGE["text"] = "/new_site"
    calls = await req.query(message=MESSAGE)
    assert "active DB" in calls.send_message.fetchone().text
```

- [ ] **Step 5: Register wizard router in `bot/main.py`**

Add `from bot.handlers.entities import site as site_entity` and `dp.include_router(site_entity.router)`.

- [ ] **Step 6: Run, expect pass. Commit.**

```bash
pytest tests/unit/test_site_wizard.py -v
git add bot/fsm/ bot/keyboards/ bot/handlers/entities/ tests/unit/test_site_wizard.py bot/main.py
git commit -m "feat: SITE wizard (FSM: sito → nazione → action menu → save/photo/edit)"
```

---

### Task 18: `/status`, `/show`, `/discard`

**Files:**
- Modify: `hff-telegram-bot/bot/handlers/common.py`
- Create: `hff-telegram-bot/tests/unit/test_status_handlers.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_status_handlers.py
from pathlib import Path
import pytest
from bot.store.db import init_state_db
from bot.store.intent_store import IntentStore, EntityType, IntentStatus
from bot.handlers.common import format_user_status

def test_format_status_with_intents(tmp_path: Path) -> None:
    db = tmp_path / "state.db"; init_state_db(db)
    intents = IntentStore(db)
    i1 = intents.enqueue(42, "a1", EntityType.SITE, {"sito": "A", "nazione": "LB"})
    intents.claim_pending(i1.id)
    intents.mark_flushed(i1.id, target_entity_id=100)
    i2 = intents.enqueue(42, "a1", EntityType.SITE, {"sito": "B", "nazione": "LB"})

    out = format_user_status(intents, user_chat_id=42)
    assert "#" in out
    assert "flushed" in out.lower() or "✅" in out
    assert "pending" in out.lower() or "⏳" in out
```

- [ ] **Step 2: Extend `bot/handlers/common.py`**

```python
# Append to bot/handlers/common.py

from aiogram.filters import CommandObject  # noqa: E402
from bot.store.intent_store import IntentStore, IntentStatus  # noqa: E402

STATUS_EMOJI = {
    IntentStatus.PENDING: "⏳",
    IntentStatus.FLUSHING: "🔄",
    IntentStatus.FLUSHED: "✅",
    IntentStatus.FAILED: "⚠",
    IntentStatus.POISON: "❌",
    IntentStatus.DISCARDED: "🗑",
}

def format_user_status(intents: IntentStore, user_chat_id: int) -> str:
    rows = intents.list_by_user(user_chat_id, limit=10)
    if not rows:
        return "No intents yet."
    out = []
    for r in rows:
        emoji = STATUS_EMOJI[r.status]
        out.append(f"#{r.id} {emoji} {r.status.value:<8} {r.entity_type.value:<8} "
                   f"{r.db_alias}  {r.last_error or ''}")
    return "\n".join(out)

async def status_handler(message, intents: IntentStore, user, **_) -> None:
    if user is None:
        await message.answer("Unauthorized.")
        return
    await message.answer("```\n" + format_user_status(intents, user.chat_id) + "\n```",
                          parse_mode="Markdown")

async def show_handler(message, command: CommandObject, intents: IntentStore,
                        user, **_) -> None:
    if user is None:
        await message.answer("Unauthorized.")
        return
    if not command.args:
        await message.answer("Usage: /show <intent_id>")
        return
    intent = intents.get(int(command.args))
    if intent.user_chat_id != user.chat_id and user.role.value != "admin":
        await message.answer("Not your intent.")
        return
    lines = [f"#{intent.id}  {intent.status.value}  {intent.entity_type.value}",
             f"alias: {intent.db_alias}",
             f"payload: {intent.payload}",
             f"error: {intent.last_error}",
             f"entity_id: {intent.target_entity_id}"]
    await message.answer("```\n" + "\n".join(lines) + "\n```", parse_mode="Markdown")

async def discard_handler(message, command: CommandObject, intents: IntentStore,
                            user, **_) -> None:
    if user is None:
        await message.answer("Unauthorized.")
        return
    if not command.args:
        await message.answer("Usage: /discard <intent_id>")
        return
    intents.discard(int(command.args))
    await message.answer(f"Intent #{command.args} discarded.")

router.message.register(status_handler, Command("status"))
router.message.register(show_handler, Command("show"))
router.message.register(discard_handler, Command("discard"))
```

- [ ] **Step 3: Run, expect pass. Commit.**

```bash
pytest tests/unit/test_status_handlers.py -v
git add bot/handlers/common.py tests/unit/test_status_handlers.py
git commit -m "feat: /status /show /discard commands"
```

---

### Task 19: End-to-end integration test

**Files:**
- Create: `hff-telegram-bot/tests/integration/test_end_to_end.py`

- [ ] **Step 1: Write the e2e test**

```python
# tests/integration/test_end_to_end.py
import asyncio, time
from pathlib import Path
import cv2, pytest
from cryptography.fernet import Fernet
from sqlalchemy import text
from bot.store.db import init_state_db
from bot.store.user_store import UserStore
from bot.store.crypto import Cryptor
from bot.store.registry import Registry
from bot.store.intent_store import IntentStore, EntityType, IntentStatus
from bot.media.spool import MediaSpool, Mediatype
from bot.sync.flusher import Flusher
from bot.sync.scheduler import Scheduler
from bot.sync.target_db import connect_target
from tests.integration.test_site_adapter import _prep_blank_hff

SAMPLE = Path(__file__).parent.parent / "fixtures" / "sample.jpg"

@pytest.mark.asyncio
async def test_new_site_queue_to_flushed_with_media(tmp_path: Path) -> None:
    state = tmp_path / "state.db"; init_state_db(state)
    cryptor = Cryptor(Fernet.generate_key().decode())
    media_root = tmp_path / "media"
    registry = Registry(state, cryptor, media_root=media_root)
    intents = IntentStore(state)
    spool = MediaSpool(state, media_root / "_spool")
    users = UserStore(state); users.bootstrap_admin(42, "Enzo")

    hff = tmp_path / "hff.sqlite"; _prep_blank_hff(hff)
    registry.add_sqlite("a1", hff, created_by=42)

    # Simulate wizard outcome: enqueue intent + attach photo
    intent = intents.enqueue(42, "a1", EntityType.SITE,
                              {"sito": "Alice B", "nazione": "LB"})
    spool.store(intent.id, "tg1", SAMPLE.read_bytes(), "jpg",
                 Mediatype.IMAGE, "view1")

    # Start scheduler (fast)
    flusher = Flusher(registry, intents, spool)
    scheduler = Scheduler(intents, flusher, interval_seconds=0.05)
    t = asyncio.create_task(scheduler.run())
    for _ in range(40):
        await asyncio.sleep(0.05)
        if intents.get(intent.id).status == IntentStatus.FLUSHED:
            break
    scheduler.stop(); await t

    assert intents.get(intent.id).status == IntentStatus.FLUSHED
    engine = connect_target({"sqlite_path": str(hff)})
    with engine.connect() as con:
        n_site = con.execute(text("SELECT COUNT(*) FROM site_table")).scalar()
        n_mte  = con.execute(text("SELECT COUNT(*) FROM media_to_entity_table "
                                     "WHERE entity_type='SITE'")).scalar()
    assert (n_site, n_mte) == (1, 1)

    thumb = media_root / "a1" / "alice-b" / "thumbnail" / "1_view1_thumb.png"
    resize = media_root / "a1" / "alice-b" / "image_resize" / "1_view1.png"
    assert thumb.exists() and resize.exists()

    # Spool file removed
    assert not any((media_root / "_spool").glob("*.jpg"))
```

- [ ] **Step 2: Run, expect pass. Commit.**

```bash
pytest tests/integration/test_end_to_end.py -v
git add tests/integration/test_end_to_end.py
git commit -m "test: end-to-end SITE intent → flushed + media on disk + DB rows"
```

---

### Task 20: Crash-recovery idempotency test

**Files:**
- Create: `hff-telegram-bot/tests/integration/test_crash_recovery.py`

- [ ] **Step 1: Write the test**

```python
# tests/integration/test_crash_recovery.py
from pathlib import Path
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import text
from bot.store.db import init_state_db
from bot.store.crypto import Cryptor
from bot.store.registry import Registry
from bot.store.intent_store import IntentStore, EntityType, IntentStatus
from bot.media.spool import MediaSpool
from bot.sync.flusher import Flusher
from bot.sync.target_db import connect_target
from tests.integration.test_site_adapter import _prep_blank_hff

def test_double_flush_same_intent_produces_single_row(tmp_path: Path) -> None:
    state = tmp_path / "state.db"; init_state_db(state)
    cryptor = Cryptor(Fernet.generate_key().decode())
    registry = Registry(state, cryptor, media_root=tmp_path / "media")
    intents = IntentStore(state)
    spool = MediaSpool(state, tmp_path / "spool")
    hff = tmp_path / "hff.sqlite"; _prep_blank_hff(hff)
    registry.add_sqlite("a1", hff, created_by=42)

    intent = intents.enqueue(42, "a1", EntityType.SITE,
                              {"sito": "A", "nazione": "LB"})
    flusher = Flusher(registry, intents, spool)
    flusher.flush_one(intent.id)
    # Now simulate "bot restart" — reset intent status to pending, re-run flush
    with __import__("sqlite3").connect(state) as con:
        con.execute("UPDATE pending_intents SET status='pending' WHERE id=?",
                     (intent.id,))
    flusher.flush_one(intent.id)

    engine = connect_target({"sqlite_path": str(hff)})
    with engine.connect() as con:
        n = con.execute(text("SELECT COUNT(*) FROM site_table")).scalar()
        mte = con.execute(text(
            "SELECT COUNT(*) FROM bot_flushed_intents WHERE idempotency_key=:k"),
            {"k": intent.idempotency_key}).scalar()
    assert n == 1  # no duplicate site row
    assert mte == 1
```

- [ ] **Step 2: Run, expect pass. Commit.**

```bash
pytest tests/integration/test_crash_recovery.py -v
git add tests/integration/test_crash_recovery.py
git commit -m "test: crash-recovery — double flush stays idempotent"
```

---

### Task 21: Systemd unit, README, tag v0.1.0

**Files:**
- Create: `hff-telegram-bot/deploy/hff-bot.service`
- Create: `hff-telegram-bot/deploy/rsync-sync.sh.example`
- Modify: `hff-telegram-bot/README.md` (full content)

- [ ] **Step 1: Create `deploy/hff-bot.service`**

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
ReadWritePaths=/var/hff-bot /opt/hff-telegram-bot
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 2: Create `deploy/rsync-sync.sh.example`**

```bash
#!/usr/bin/env bash
# Mirror the bot's media folder for a specific alias down to the laptop's
# HFF plugin THUMB_PATH base. Schedule with cron, e.g. every 5 min.
# Usage: ./rsync-sync.sh <alias> <laptop-thumb-base>
set -euo pipefail
ALIAS="${1:?alias required}"
LAPTOP_BASE="${2:?laptop THUMB_PATH base required}"
SSH_TARGET="${BOT_SSH_TARGET:-hffbot@bot.example.com}"
rsync -av --delete \
  "${SSH_TARGET}:/var/hff-bot/media/${ALIAS}/" \
  "${LAPTOP_BASE}/"
```

- [ ] **Step 3: Write a full `README.md`**

```markdown
# hff-telegram-bot

Telegram bot for HFF-Survey field data entry. Queues writes locally when the
target HFF database is unreachable and replays them via an async sync worker.

## Quick start (dev)

    python -m venv .venv && source .venv/bin/activate
    pip install -e '.[dev]'
    cp .env.example .env
    # Fill BOT_TOKEN, BOOT_ADMIN_CHAT_ID, FERNET_KEY
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    python -m bot.main

## v0.1 scope

- Entity: SITE only
- Target DB: SQLite only
- Commands: `/start /add_db /list_dbs /use /remove_db /new_site /status /show /discard`
- Single-admin (bootstrapped from BOOT_ADMIN_CHAT_ID). No /invite yet.

## Architecture

See `docs/design.md` (mirrored from the plugin's
`docs/superpowers/specs/2026-04-21-telegram-bot-design.md`).

## Deployment

    sudo useradd --system --home /var/hff-bot hffbot
    sudo mkdir -p /var/hff-bot/{logs,media}
    sudo chown -R hffbot:hffbot /var/hff-bot
    sudo cp deploy/hff-bot.service /etc/systemd/system/
    sudo systemctl enable --now hff-bot

On the laptop running the QGIS plugin, schedule `deploy/rsync-sync.sh.example`
to mirror `<base>/<alias>/` down to a local folder, then set `THUMB_PATH` and
`THUMB_RESIZE` in `~/HFF/HFF_DB_folder/config.cfg` to point at that folder.

## Testing

    pytest
```

- [ ] **Step 4: Tag**

```bash
git add deploy/ README.md
git commit -m "docs: README + systemd unit + rsync example for v0.1"
git tag -a v0.1.0 -m "v0.1.0 — SITE vertical slice"
```

- [ ] **Step 5: Final test sweep**

```bash
pytest --cov=bot --cov-report=term-missing
ruff check bot tests
mypy bot
```

Expected: all green; coverage ≥ 80 % on `bot/` excluding `bot/main.py`.

---

## Self-review

### Spec coverage
Checked each spec section (2-11) against tasks:

| Spec section | Covered by task(s) |
|---|---|
| 2 core decisions | Tasks 1-21 collectively |
| 2.1 glossary | Task 9 (slugify), 12 (SITE adapter) |
| 2.2 site dependency | Out of scope for v0.1 (only SITE entity, so no cross-dep); deferred to DIVELOG plan |
| 3 architecture | Tasks 4 (state.db), 11-13 (target_db + adapters + flusher), 14 (scheduler), 15 (aiogram) |
| 4 bot-side data model | Tasks 4 (schema), 5-8 (stores) |
| 5 user flows | Tasks 15 (/start), 16 (/add_db + DB mgmt), 17 (/new_site), 18 (/status et al.) |
| 6 media handling | Tasks 8 (spool), 9 (ops), 12 (adapter wiring) |
| 7 error handling | Task 13 (flusher classification); retry backoff simplified for v0.1 (no backoff — listed under out-of-scope) |
| 8 repo layout | Task 1 scaffolding + progressive file creation |
| 9 testing | TDD in every task + task 19 (e2e) + task 20 (crash recovery) |
| 10 release plan | This plan IS 0.1; subsequent versions each get their own plan |
| 11 out-of-scope | Explicitly listed at the top of this plan |

### Placeholder scan
- No "TBD", "TODO", "similar to Task N".
- Every code step has complete runnable code.
- Every test has an explicit assertion set.

### Type consistency
- `EntityType` / `IntentStatus` / `Mediatype` / `Role` enums defined in their respective stores and used consistently.
- `FinalizedMedia.thumb_relpath` / `.resize_relpath` referenced identically in adapter and tests.
- `RegistryEntry.conn_params` and `.media_base_path` accessed with same names everywhere.

All checks pass.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-21-telegram-bot-v0.1.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
