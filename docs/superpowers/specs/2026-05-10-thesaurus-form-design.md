# HFF Thesaurus form — design spec

**Status:** queued for v11.4. Issue #44 (Catnip19) immediate request shipped via baked defaults in v11.3 (`modules/utility/hff_combobox_defaults.py`).

## Problem

Free-text comboboxes in Pottery / Anchor / Artefact / Dive log / Shipwreck were
populated only from `DB_MANAGER.group_by(...)` distinct values. On a fresh DB
they appeared empty. v11.3 fixed the symptom by merging DB values with a
hard-coded default vocabulary in code. The vocabulary is **not user-editable**.

## Goal

Promote the hard-coded vocabularies to a real per-project, user-editable
thesaurus stored in `hff_system__thesaurus_sigle` (the table already exists in
the schema — see `modules/db/structures/Pyarchinit_thesaurus_sigle.py:45` —
but was never wired up).

## Reference

`pyarchinit/tabs/Thesaurus.py` (2920 lines) — too heavy. Port a stripped-down
version (~400 lines) tailored to HFF's narrower needs.

`pyarchinit/tabs/Inv_Materiali.py:1986-2000` — the consumption pattern
to mirror in HFF `charge_list()`:

```python
search_dict = {
    'lingua': lang,
    'nome_tabella': "'pottery_table'",
    'tipologia_sigla': "'form'"
}
rows = self.DB_MANAGER.query_bool(search_dict, 'HFF_THESAURUS_SIGLE')
values = [r.sigla_estesa for r in rows]
```

## Schema (already in DB, no migration needed)

```
hff_system__thesaurus_sigle
  id_thesaurus_sigle    INTEGER PK
  nome_tabella          TEXT       -- e.g. 'pottery_table'
  sigla                 VARCHAR(3) -- short code
  sigla_estesa          TEXT       -- displayed value (the dropdown item)
  descrizione           TEXT
  tipologia_sigla       TEXT       -- field name, e.g. 'form'
  lingua                TEXT       -- 'en', 'ar-lb', 'it'
```

## Deliverables

1. **`tabs/hff_system__Thesaurus.py`** (~400 lines)
   - QDialog loading `gui/ui/hff_system__Thesaurus_ui.ui`
   - One QTableWidget showing all rows for the currently filtered `(nome_tabella, lingua)`
   - Filter dropdowns: `nome_tabella`, `lingua` (the same values used in form
     `charge_list` calls — derived from `DEFAULTS` keys)
   - Buttons: Add / Delete / Save / Import CSV / Export CSV
   - Inline editing in the table; save commits all dirty rows
   - Multi-language: stored per `lingua`, displayed according to the active
     locale via `hff_i18n.HffI18n`

2. **`gui/ui/hff_system__Thesaurus_ui.ui`** — minimal Qt Designer form

3. **`modules/db/hff_db_structure.py`** — seed routine called on
   first-time DB creation, reading the v11.3 `DEFAULTS` dict and inserting
   one row per (table, field, value, 'en'). Idempotent — skip if already
   populated.

4. **Toolbar entry** in `hff_system_Plugin.py` →
   `runThesaurus()` opening the new dialog.

5. **`charge_list()` migration** — modify
   `modules/utility/hff_combobox_defaults.populate()` to additionally query
   the thesaurus and merge with DB-distinct + the in-code fallback list.
   No call-site changes needed (single helper, all forms benefit).

   ```python
   def populate(combo, db_values, table=None, field=None, ...):
       thes = _query_thesaurus(table, field, locale)  # NEW
       defaults = DEFAULTS.get((table, field), [])
       merged = sorted({v for v in (db_values + thes + defaults) if v})
       ...
   ```

## Out of scope (vs pyarchinit)

- No browse/find/new state machine
- No sort panel
- No AI-generated descriptions
- No nested categories / hierarchical sigla
- No `tipologia_sigla` decimal codes (`3.11`, `3.4`) — use field name directly

## Acceptance

- Open Thesaurus dialog → see 16 rows for Pottery → form, edit one,
  save → reopen Pottery form → new value appears in `comboBox_form`
- Delete a row → next reopen of the Pottery form does NOT show that
  value (unless it's still in `pottery_table.form` or in code defaults)
- Import a CSV with 50 entries for Anchor → typology → Anchor form's
  `comboBox_typology` shows them all + DB distinct + code defaults
- Switching locale to `ar-lb` → form combos show Arabic translations if
  present, otherwise fall back to English

## Estimated effort

- Thesaurus dialog + UI: 4-5 hours
- Seed routine + DB migration glue: 1-2 hours
- charge_list integration: 30 min (single helper edit)
- Toolbar entry + i18n: 1 hour
- Testing: 2 hours

**Total: ~1 working day.**
