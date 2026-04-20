# UI Harmonization + Tutorial Browser Integration — Design

**Date:** 2026-04-20
**Status:** Draft

## Goal

Three related UI improvements for the HFF QGIS plugin:

1. Harmonize fonts across all `.ui` forms (currently 8 different families, 8 different sizes).
2. Harmonize icon sizes on buttons across all forms (currently 30×30, 10×10, 40×40, 25×25 mixed).
3. Integrate the existing tutorial browser into the **HFF Data Management** dockwidget's "Tutorials" tab, replacing the static "Installation" YouTube link.

## Non-goals

- No changes to form business logic.
- No changes to tutorial content (existing `.md` files in `docs/tutorials/{en,ar-lb}/` stay as-is).
- No new tutorial languages beyond the existing `en` and `ar-lb`.

## Current state

- **Fonts:** 8 families in use across 24 `.ui` files (Times New Roman 132×, Open Sans 102×, Calibri 98×, MS Shell Dlg 2 56×, Microsoft Sans Serif 22×, others). 8 point sizes from 8pt to 17pt.
- **Icons:** `iconSize` property varies: 30×30 (8), 10×10 (7), 40×40 (2); some outliers like 500×499 (likely preview QLabel — must be preserved).
- **Tutorials tab** (`gui/ui/hff_system__plugin.ui` line 213-242): contains a single `QLabel` (`label_8`) with hardcoded HTML. Only content is an "Installation" hyperlink to a YouTube video.
- **Tutorial viewer:** `tabs/Tutorial_viewer.py` already implements a full `TutorialViewerDialog` (QDialog) with language selector (en / ar-lb), search, markdown→HTML rendering, theme integration. Currently invoked via toolbar action `actionTutorial` (see `hff_system_Plugin.py:510`).

## Design

### 1. Font harmonization

- Python script parses each `.ui` file as XML (ElementTree, not regex) and removes every `<property name="font">...</property>` block.
- Widgets will inherit the QGIS application font → native look on macOS/Windows/Linux.
- Script is idempotent and outputs a summary of files changed.

### 2. Icon harmonization

- Same script (separate pass) normalizes geometry on buttons that carry an icon:
  - Targets: widgets of class `QToolButton` or `QPushButton` with an `icon` property set.
  - `iconSize` → 24×24 (Qt standard).
  - `minimumSize` / `maximumSize` → 32×32 if already constrained (preserve unconstrained buttons).
- Widgets without `icon` property are untouched (preserves form layout for text-only buttons, QLabels holding preview images, etc.).

### 3. Tutorial browser embedded in dockwidget

**Refactor `tabs/Tutorial_viewer.py`:**

- Extract `TutorialBrowserWidget(QWidget)` containing all current functionality (language combo, search, list, content browser, markdown renderer, theme integration).
- `TutorialViewerDialog(QDialog)` becomes a thin wrapper: layout contains a single `TutorialBrowserWidget` plus a "Close" button. Backwards-compatible with existing `runTutorial()` caller.

**Modify `hff_system_DockWidget.py`:**

- After `self.setupUi(self)`, locate the "Tutorials" tab widget by name.
- Remove `label_8` (the static HTML label with the Installation link).
- Set a `QVBoxLayout` on the tab and insert a `TutorialBrowserWidget` instance.

**Modify `gui/ui/hff_system__plugin.ui`:**

- Remove the `label_8` widget from the Tutorials tab to keep the `.ui` clean. The tab becomes an empty container; the dock widget populates it at runtime.

### Data flow

```
docs/tutorials/en/*.md          ┐
docs/tutorials/ar-lb/*.md       ┴──► TutorialBrowserWidget ──► HFF Data Management dock, "Tutorials" tab
                                                        └──► TutorialViewerDialog (existing menu action)
```

Single source of truth: `TutorialBrowserWidget` owns file discovery, parsing, and rendering. Both the embedded tab and the standalone dialog show identical content.

### Error handling

- Missing tutorial directory → widget shows "No tutorials found" placeholder (already present in existing code).
- Missing language directory → fallback to `en` (already present).
- Malformed markdown → best-effort render (existing behavior, no regression).

### Testing

Manual testing in QGIS on macOS:

1. Start QGIS, enable HFF plugin, open the HFF Data Management dock.
2. Click the "Tutorials" tab → verify tutorial list appears, first tutorial renders.
3. Switch language combo en ↔ ar-lb → verify list and content update.
4. Open any data entry form (Site, UW, Anchor, Artefact, Pottery, Shipwreck, EAMENA) → verify consistent native font and 24×24 icon sizes.
5. Click the toolbar "Tutorials" action → verify the standalone dialog still works identically.

No automated test suite exists in this project (per `CLAUDE.md`); manual verification is the standard.

## Implementation order

1. Write Python harmonization script (`scripts/harmonize_ui.py`) with font + icon passes, dry-run flag, commit-ready diff.
2. Run script, review diff, commit.
3. Refactor `Tutorial_viewer.py` → extract `TutorialBrowserWidget`; keep `TutorialViewerDialog` working.
4. Remove `label_8` from `hff_system__plugin.ui` (via manual edit).
5. Update `HffPluginDialog.__init__` to inject `TutorialBrowserWidget` into the Tutorials tab.
6. Manual test in QGIS, commit.

## Risks

- Stripping fonts from `.ui` may reveal layout issues if any form relied on a specific font metrics (e.g., field heights tuned for Times New Roman). Mitigation: visual check of each form after the change; rollback is a single `git revert`.
- QGIS plugin loader caches `.ui` files. A full QGIS restart is required after `.ui` edits.
