# Blend Version Manager

[![Latest release](https://img.shields.io/github/v/release/AakashKhambhaliya/blend-version-manager)](https://github.com/AakashKhambhaliya/blend-version-manager/releases/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A **Blender 4.2+** add-on to **save, browse and restore versions** of your `.blend`
file — without leaving Blender or renaming files by hand.

---

## ⬇ Install (two easy ways)

### A) Download ZIP (simplest)
1. Click the green **Code ▸ Download ZIP** button above (or
   [download it here](https://github.com/AakashKhambhaliya/blend-version-manager/archive/refs/heads/main.zip)).
2. In Blender: **Edit ▸ Preferences ▸ Add-ons ▸ ⌄ (top-right) ▸ Install from Disk…**
   → pick the downloaded zip.
3. Enable **Blend Version Manager**, then open the **Versions** tab in the 3D viewport
   sidebar (press `N`).

### B) Release zip (recommended for the latest stable build)
1. **[⬇ Download the latest release](https://github.com/AakashKhambhaliya/blend-version-manager/releases/latest)** → `blend_version_manager-x.y.z.zip`.
2. Install the same way (or just **drag-and-drop the zip into Blender**).

> This add-on is a **combined add-on + extension**: the *Download ZIP* installs it as a
> classic add-on, while the *Release* zip installs as a Blender 4.2 extension. Either works.

---

## Features
- **Save versions with notes** — numbered copies (`myfile_v001.blend`, `v002`, …) you can
  annotate; browse / **Restore** / **Open** from the sidebar.
- **Auto-version on save** — throttled (every save / every Nth / time interval), optional auto-prune.
- **Boost to milestones** — promote a version to a semantic release (`1.0.0`, `1.1.0`, …);
  boosted versions are auto-pinned.
- **Manage** — pin, edit-note, delete, prune; full add-on preferences.
- **Clean UI** — two-line, narrow-panel-friendly version list with a details panel.

Versions and a small `versions.json` (timestamps + notes) live next to your file in
`.blendversions/<file>/`.

## Usage
1. Save your file once (`File ▸ Save As`).
2. In the **Versions** panel, optionally type a note and click **Save Version**.
3. Select any version → **Restore**, **Open**, **Boost**, pin, edit its note, etc.

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0).
