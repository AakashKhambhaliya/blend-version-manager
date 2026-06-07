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

## Download & Install
1. **[⬇ Download the latest release](https://github.com/AakashKhambhaliya/blend-version-manager/releases/latest)**
   and grab the `blend_version_manager-*.zip` file.
2. In Blender (4.2+): **Edit ▸ Preferences ▸ Add-ons ▸ ⌄ (top-right) ▸ Install from Disk…**
   and pick the downloaded zip. *(On older 4.2 builds it's under **Get Extensions ▸ ⌄ ▸
   Install from Disk…**.)*
3. It enables automatically. Open the **Versions** tab in the 3D viewport sidebar (press `N`).

> Tip: you can also just **drag-and-drop the zip into the Blender window** to install it.

### Build the zip yourself
The release zip is simply the contents of the `blend_version_manager/` folder
(with `blender_manifest.toml` at the root). Zip those files and install as above.

## Usage
1. Save your file once (`File ▸ Save As`).
2. In the **Versions** panel, type a note and click **Save Version**.
3. Select any version and use **Restore** or **Open**.
