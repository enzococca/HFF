# Cross-Repo End-to-End Smoke Checklist

**Scope:** Verify divers/segments + media + edit-flow propagate correctly across the two repositories whenever either side ships a release.

**Repos:**
- Plugin — `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/HFF` (v11.0+)
- Bot — `~/hff-telegram-bot` (v2.1.1+)

**Shared state:** A target SQLite DB registered with the bot via `/add_db`, and opened in QGIS via the plugin's config dialog (or a direct PostgreSQL target shared by both).

---

## A. Plugin → Bot (data flows from QGIS into the bot's view)

1. **QGIS:** Open the plugin, create a site (e.g. "SmokeSite_<date>") with a sensible country/area.
2. **QGIS:** New Divelog form for that site. Year = current. Add 2 divers; for one of them add 2 segments (different breathing mix). Save.
3. **QGIS:** Re-open the divelog form for the same record — confirm both divers and all segments are loaded back from `divers` + `diver_segments` tables (not the legacy `dive_log.divers` text column).
4. **Bot (Telegram chat):** `/use <alias>` to activate the same DB. Then `/edit_divelog <divelog_id>` (the integer one shown in the form). Expect the field menu inline keyboard.
5. **Bot:** Tap "↳ all fields" or page through — confirm `bottom_time`, `max_depth`, `wind` are listed as editable.
6. **Webapp:** Open the chat menu button "📊 Data" → drawer (☰) → "🤿 Divelogs". Tap the divelog. Expect a "Divers" linked block listing both divers and the second one's two segments.

## B. Bot → Plugin (edits made via Telegram appear in QGIS)

1. **Bot:** `/edit_divelog <id>` → tap "wind" → reply `15kt`. Expect "✓ wind updated."
2. **QGIS:** Refresh the divelog form (close/reopen, or hit the reload button). The wind field should now read `15kt`.
3. **Webapp:** Open `/audit` (drawer → "📝 Audit log"). Most recent row: `dive_log #<id> · wind · ∅ → 15kt · source=bot`.

## C. Webapp → Bot (edits via Mini App land in the audit + DB)

1. **Webapp:** Open a Site detail. Tap "✏ Edit". Change `description` to `smoke-test`. Save.
2. **Webapp:** `/audit` shows new row `site_table #<id> · description · ... → smoke-test · source=webapp`.
3. **QGIS:** Reload the site form. Description shows `smoke-test`.

## D. Media link-back

1. **Bot (chat):** Send a photo with caption referencing the active divelog (or attach via the media wizard).
2. **Webapp:** Re-open the divelog detail. Expect a "Media" linked block under "Divers" with a thumbnail. Tap → opens the Media detail page with full image.
3. **QGIS:** Reload the form. The media list should include the new image.

## E. Negative paths (must not regress)

- `/sites?initData=garbage` → 403 (auth invariant).
- `/divelogs/9999999` → 404 (not 500).
- Webapp DB switcher with an alias not in registry → 400 "unknown alias".
- `/edit_divelog 9999999` → "No divelog matching '9999999'." (not a 500).

---

## Pass criteria

All steps above complete without manual intervention beyond what's described, and:
- No 500s in Railway logs (`railway logs --deployment | grep -i error`)
- Audit log captures every edit (one row per changed field, never per request)
- No `no such table` errors (auto-migration must catch legacy targets)

If any step regresses on a future release, this doc is the recipe to reproduce it before bisecting.
