# Blend Version Manager

A Blender 4.2+ add-on (extension) to **save, browse and restore versions** of your
`.blend` file — without leaving Blender or renaming files by hand.

## What it does
- **Save Version** — flushes the current file and stores a numbered copy
  (`myfile_v001.blend`, `v002`, …) together with an optional note.
- **Browse** — every version is listed (newest first) with its timestamp and note in
  the 3D viewport sidebar.
- **Restore** — replace the working file with any earlier version. A safety snapshot of
  the current state is saved automatically before the file is overwritten.
- **Open** — load a version directly without touching the working file.

Versions and a small `versions.json` (timestamps + notes) live next to your file:

```
project/
├── myfile.blend
└── .blendversions/myfile/
    ├── versions.json
    ├── myfile_v001.blend
    └── myfile_v002.blend
```

The add-on prefers Blender's native operators (`wm.save_mainfile`,
`wm.save_as_mainfile`, `wm.open_mainfile`) and only adds what Blender lacks: per-version
notes and an ordered history.

## Install
1. Zip the `blend_version_manager` folder (or use it directly).
2. In Blender: **Edit ▸ Preferences ▸ Get Extensions ▸ ⌄ ▸ Install from Disk…** and pick
   the zip.
3. Enable it. Open the **Versions** tab in the 3D viewport sidebar (press `N`).

## Usage
1. Save your file once (`File ▸ Save As`).
2. In the **Versions** panel, type a note and click **Save Version**.
3. Select any version and use **Restore** or **Open**.
