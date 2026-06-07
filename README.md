# Blend Version Manager

[![Latest release](https://img.shields.io/github/v/release/AakashKhambhaliya/blend-version-manager)](https://github.com/AakashKhambhaliya/blend-version-manager/releases/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A **Blender 4.2+** add-on (extension) to **save, browse and restore versions** of your
`.blend` file — without leaving Blender or renaming files by hand.

---

## ⬇ Download & Install

> [!IMPORTANT]
> **Do NOT use the green “Code ▸ Download ZIP” button.** GitHub wraps the files in an
> extra folder, so Blender can’t find the manifest and shows a *“missing manifest”* error.
> Use the **Releases** zip below — it’s packaged correctly and installs in one click.

**1. [⬇ Download the latest release](https://github.com/AakashKhambhaliya/blend-version-manager/releases/latest)** → grab `blend_version_manager-x.y.z.zip`.

**2. Install in Blender (4.2+):**
- **Edit ▸ Preferences ▸ Add-ons ▸ ⌄ (top-right) ▸ Install from Disk…** → pick the zip.
- *…or simply **drag-and-drop the zip into the Blender window**.*

**3.** Open the **Versions** tab in the 3D viewport sidebar (press `N`).

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

## Build the install zip yourself
The release zip is just the **contents** of the [`blend_version_manager/`](blend_version_manager)
folder (with `blender_manifest.toml` at the zip root):

```bash
cd blend_version_manager
zip -r ../blend_version_manager.zip . -x "__pycache__/*"
```

Then install that zip as described above.

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0). See the add-on manifest for details.
