# Changelog

All notable changes to **Blend Version Manager** are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [1.4.4] — 2026-06-07
Bug fixes.

### Fixed
- **Handlers broke on Blender 3.6+ / 4.2:** `save_post` / `load_post` handlers
  declared a single parameter, but Blender now passes an extra filepath argument,
  causing a `TypeError` that silently disabled **auto-version on save** and the
  **auto-refresh when opening a file**. Handlers now accept `*args`.
- **Selection no longer jumps:** editing a note, pinning, boosting or deleting kept
  resetting the highlighted row to the top; the current selection is now preserved
  across list rebuilds.
- **`Default note` preference now works:** it was never applied — it's now used when
  you save a version with the note field left empty.

## [1.4.3] — 2026-06-07
UI: two-line version rows.

### Changed
- Each version row is now **two lines** — line 1: version number + milestone and
  auto/pin badges; line 2: the timestamp. Stacks vertically so nothing is cut off
  in a narrow sidebar.

## [1.4.2] — 2026-06-07
UI: notes moved out of the list.

### Changed
- The version row now shows only the **version number + date** (and badges) —
  the note was removed from the line for a cleaner, professional list.
- Selecting a version shows its **note prominently at the top of the Details
  panel**, with an inline edit button; the note is always shown ("(no note)"
  when empty).

## [1.4.1] — 2026-06-07
UI: narrow-panel readability.

### Changed
- Version rows are decluttered so the **name/note uses the full width**; the
  timestamp was removed from the row (it cut off names in a narrow sidebar).
- Trailing badges (milestone ★, auto 🕐, pin 📌) are drawn only when they apply.
- The **Details** panel is now open by default and shows the full date, size,
  Blender version and **full filename on its own line**, with label/value splits
  that stay readable when the panel is made narrow.

## [1.4.0] — 2026-06-07
Maintenance release — version bump, no functional changes.

## [1.3.0] — 2026-06-07
Version Boost (semantic milestones). Backward compatible.

### Added
- **Boost** action: promote any saved version to a named semantic milestone
  (Major / Minor / Patch → `1.0.0`, `1.1.0`, `1.1.1`), layered on top of the
  incremental `v001/v002` numbering. The dialog previews the resulting version.
- Boosted versions are **auto-pinned** (protected from pruning) and show a ★ badge
  in the list, with milestone + optional name surfaced in the Details panel.
- New manifest fields `milestone` and `label` on version records; helpers
  `parse_milestone` / `bump_milestone` / `next_milestone` in storage.

## [1.2.0] — 2026-06-07
Automatic versioning. Backward compatible.

### Added
- **Auto-version on save** via a `save_post` handler, with throttle modes in
  Preferences: *Off* (default), *Every save*, *Every Nth save*, *Time interval*.
- Inline **Auto** control in the panel's New Version box for one-click enable.
- **Auto-prune after auto-version** option (reuses the keep-N limit; pins protected).
- Auto-versions are tagged `[auto-save]` with a clock badge in the list and a
  `kind` field in the manifest, so they're distinguishable from manual checkpoints.

### Notes
- Auto-versioning copies the file Blender just wrote (no extra save), and the
  add-on's own internal saves are suspended so manual actions never double-version.

## [1.1.0] — 2026-06-07
Advanced UI and management upgrade. Backward compatible with 1.0.0 manifests.

### Added
- **Add-on Preferences** page: safety-snapshot toggle, confirm-destructive toggle,
  auto-keep limit, compression, and a default note.
- **Professional version browser**: custom multi-column `UIList` with a current-version
  marker, note, date and pin badge, plus a native list + side-button column layout.
- **Search, filter and sort** header (text search, pinned-only, newest/oldest,
  pinned-on-top).
- Collapsible **Details** and **Maintenance** sub-panels (metadata grid, open folder,
  prune, settings shortcut) and a header stats line (version count + total size).
- New operators: **delete**, **edit note**, **pin/unpin**, **prune** (keeps newest N
  unpinned, protects pins), and **open versions folder**.
- Per-version **size** and **pinned** metadata, plus a tracked **current** version pointer.

### Changed
- `versions.json` is now a structured state dict (`{schema, current, versions[]}`).
  Legacy bare-list manifests from 1.0.0 are still read automatically.

## [1.0.0] — 2026-06-07
Initial release.

### Added
- Save numbered versions with a note, browse them in the 3D viewport sidebar,
  restore (with an automatic safety snapshot) and open versions read-only.
- Stored as incremental `.blend` copies + a `versions.json` sidecar in
  `.blendversions/<file>/`.
