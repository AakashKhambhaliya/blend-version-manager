"""Operators: save, refresh, restore, open, delete, edit note, pin, prune, folder.

Native Blender operators do the heavy lifting wherever one exists
(``wm.save_mainfile`` / ``wm.save_as_mainfile(copy=True)`` to write versions,
``wm.open_mainfile`` to load them, ``wm.path_open`` to reveal the folder).
Custom code is limited to the manifest and the safety-snapshot copy.
"""

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from . import autosave
from . import storage
from .prefs import get_prefs


def _ensure_saved(op):
    """Block actions until the working file has been saved at least once."""
    if not bpy.data.filepath:
        op.report({'ERROR'}, "Save the .blend file first (File > Save As), then create versions.")
        return False
    return True


def _active_item(wm):
    if 0 <= wm.active_index < len(wm.versions):
        return wm.versions[wm.active_index]
    return None


def _populate(context):
    """Rebuild the UI list from disk and refresh the 'current' marker."""
    wm = context.window_manager.bvm
    wm.versions.clear()
    wm.current_version = 0
    if not bpy.data.filepath:
        wm.active_index = 0
        return

    state = storage.load_state(bpy.data.filepath)
    wm.current_version = int(state.get("current", 0))
    for rec in sorted(state["versions"], key=lambda r: r.get("version", 0), reverse=True):
        item = wm.versions.add()
        item.version = int(rec.get("version", 0))
        item.filename = rec.get("filename", "")
        item.timestamp = rec.get("timestamp", "")
        item.date_short = storage.short_timestamp(rec.get("timestamp", ""))
        item.note = rec.get("note", "")
        item.blender_version = rec.get("blender_version", "")
        item.size = int(rec.get("size", 0))
        item.pinned = bool(rec.get("pinned", False))
        item.kind = rec.get("kind", "manual")
        item.milestone = rec.get("milestone", "")
        item.label = rec.get("label", "")
    wm.active_index = 0


class BVM_OT_save_version(Operator):
    bl_idname = "bvm.save_version"
    bl_label = "Save Version"
    bl_description = "Save the current file and store a numbered copy with a note"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def execute(self, context):
        if not _ensure_saved(self):
            return {'CANCELLED'}

        blend_path = bpy.data.filepath
        wm = context.window_manager.bvm
        prefs = get_prefs(context)

        with autosave.suspend():
            bpy.ops.wm.save_mainfile()

        state = storage.load_state(blend_path)
        versions = state["versions"]
        number = storage.next_version_number(versions)
        target = storage.next_version_path(blend_path, versions)
        target.parent.mkdir(parents=True, exist_ok=True)

        # copy=True keeps the working file as the active document.
        try:
            with autosave.suspend():
                bpy.ops.wm.save_as_mainfile(
                    filepath=str(target), copy=True, compress=prefs.compress)
        except RuntimeError as exc:
            self.report({'ERROR'}, "Could not write version: {}".format(exc))
            return {'CANCELLED'}

        size = target.stat().st_size if target.exists() else 0
        versions.append(storage.make_record(
            number, target.name, wm.new_note, bpy.app.version_string, size=size))
        state["current"] = number
        storage.save_state(blend_path, state)

        wm.new_note = ""
        _populate(context)
        self.report({'INFO'}, "Saved version v{:03d}".format(number))
        return {'FINISHED'}


class BVM_OT_refresh(Operator):
    bl_idname = "bvm.refresh"
    bl_label = "Refresh"
    bl_description = "Reload the version list from disk"
    bl_options = {'REGISTER'}

    def execute(self, context):
        _populate(context)
        return {'FINISHED'}


class BVM_OT_restore(Operator):
    bl_idname = "bvm.restore"
    bl_label = "Restore Selected Version"
    bl_description = ("Replace the working file with the selected version. "
                      "A safety snapshot of the current file is saved first")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def invoke(self, context, event):
        if get_prefs(context).confirm_destructive:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        if not _ensure_saved(self):
            return {'CANCELLED'}

        wm = context.window_manager.bvm
        prefs = get_prefs(context)
        item = _active_item(wm)
        if item is None:
            self.report({'ERROR'}, "No version selected.")
            return {'CANCELLED'}

        blend_path = bpy.data.filepath
        src = storage.version_dir(blend_path) / item.filename
        if not src.exists():
            self.report({'ERROR'}, "Version file missing: {}".format(item.filename))
            return {'CANCELLED'}

        state = storage.load_state(blend_path)
        versions = state["versions"]
        restored = item.version
        snap_number = 0

        if prefs.auto_snapshot_on_restore:
            with autosave.suspend():
                bpy.ops.wm.save_mainfile()
            snap_number = storage.next_version_number(versions)
            snap = storage.next_version_path(blend_path, versions)
            storage.copy_file(blend_path, snap)
            size = snap.stat().st_size if snap.exists() else 0
            versions.append(storage.make_record(
                snap_number, snap.name,
                "Auto-snapshot before restoring v{:03d}".format(restored),
                bpy.app.version_string, size=size))

        state["current"] = restored
        storage.save_state(blend_path, state)

        storage.copy_file(src, blend_path)
        bpy.ops.wm.open_mainfile(filepath=blend_path)

        if snap_number:
            self.report({'INFO'}, "Restored v{:03d} (snapshot saved as v{:03d})".format(
                restored, snap_number))
        else:
            self.report({'INFO'}, "Restored v{:03d}".format(restored))
        return {'FINISHED'}


class BVM_OT_open(Operator):
    bl_idname = "bvm.open"
    bl_label = "Open Selected Version"
    bl_description = ("Open the selected version file directly "
                      "(does not overwrite the working file)")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if not _ensure_saved(self):
            return {'CANCELLED'}

        wm = context.window_manager.bvm
        item = _active_item(wm)
        if item is None:
            self.report({'ERROR'}, "No version selected.")
            return {'CANCELLED'}

        src = storage.version_dir(bpy.data.filepath) / item.filename
        if not src.exists():
            self.report({'ERROR'}, "Version file missing: {}".format(item.filename))
            return {'CANCELLED'}

        bpy.ops.wm.open_mainfile(filepath=str(src))
        return {'FINISHED'}


class BVM_OT_delete(Operator):
    bl_idname = "bvm.delete"
    bl_label = "Delete Selected Version"
    bl_description = "Permanently delete the selected version file"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def invoke(self, context, event):
        if get_prefs(context).confirm_destructive:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        wm = context.window_manager.bvm
        item = _active_item(wm)
        if item is None:
            self.report({'ERROR'}, "No version selected.")
            return {'CANCELLED'}

        number = item.version
        blend_path = bpy.data.filepath
        state = storage.load_state(blend_path)
        rec = storage.find_record(state["versions"], number)
        if rec is None:
            self.report({'ERROR'}, "Version not found in manifest.")
            return {'CANCELLED'}

        vfile = storage.version_dir(blend_path) / rec.get("filename", "")
        try:
            if vfile.exists():
                vfile.unlink()
        except OSError as exc:
            self.report({'ERROR'}, "Could not delete file: {}".format(exc))
            return {'CANCELLED'}

        state["versions"] = [r for r in state["versions"]
                             if int(r.get("version", -1)) != number]
        if state.get("current") == number:
            state["current"] = 0
        storage.save_state(blend_path, state)

        _populate(context)
        self.report({'INFO'}, "Deleted v{:03d}".format(number))
        return {'FINISHED'}


class BVM_OT_edit_note(Operator):
    bl_idname = "bvm.edit_note"
    bl_label = "Edit Note"
    bl_description = "Edit the note of the selected version"
    bl_options = {'REGISTER'}

    note: StringProperty(name="Note")

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def invoke(self, context, event):
        item = _active_item(context.window_manager.bvm)
        self.note = item.note if item else ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "note", text="")

    def execute(self, context):
        wm = context.window_manager.bvm
        item = _active_item(wm)
        if item is None:
            return {'CANCELLED'}
        blend_path = bpy.data.filepath
        state = storage.load_state(blend_path)
        rec = storage.find_record(state["versions"], item.version)
        if rec is None:
            self.report({'ERROR'}, "Version not found.")
            return {'CANCELLED'}
        rec["note"] = self.note
        storage.save_state(blend_path, state)
        _populate(context)
        return {'FINISHED'}


class BVM_OT_toggle_pin(Operator):
    bl_idname = "bvm.toggle_pin"
    bl_label = "Pin / Unpin"
    bl_description = "Pin the selected version so it is protected from pruning"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def execute(self, context):
        wm = context.window_manager.bvm
        item = _active_item(wm)
        if item is None:
            return {'CANCELLED'}
        blend_path = bpy.data.filepath
        state = storage.load_state(blend_path)
        rec = storage.find_record(state["versions"], item.version)
        if rec is None:
            return {'CANCELLED'}
        rec["pinned"] = not rec.get("pinned", False)
        storage.save_state(blend_path, state)
        _populate(context)
        return {'FINISHED'}


class BVM_OT_boost(Operator):
    bl_idname = "bvm.boost"
    bl_label = "Boost to Milestone"
    bl_description = ("Promote the selected version to a named semantic milestone "
                      "(e.g. 1.0.0). Boosted versions are pinned automatically")
    bl_options = {'REGISTER'}

    level: EnumProperty(
        name="Level",
        description="Which part of the milestone version to increase",
        items=(
            ('MAJOR', "Major", "Big release: X+1.0.0", 'TRIA_UP_BAR', 0),
            ('MINOR', "Minor", "New feature: X.Y+1.0", 'TRIA_UP', 1),
            ('PATCH', "Patch", "Small fix: X.Y.Z+1", 'TRIA_RIGHT', 2),
        ),
        default='MINOR',
    )
    label: StringProperty(
        name="Name",
        description="Optional name for this milestone (e.g. 'First playblast')",
    )

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def _highest(self, context):
        best = (0, 0, 0)
        for it in context.window_manager.bvm.versions:
            mv = storage.parse_milestone(it.milestone)
            if mv and mv > best:
                best = mv
        return best

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        item = _active_item(context.window_manager.bvm)
        if item is not None:
            layout.label(text="Boosting v{:03d}".format(item.version), icon='FILE_BLEND')
        layout.prop(self, "level", expand=True)
        preview = storage.format_milestone(
            storage.bump_milestone(self._highest(context), self.level))
        layout.label(text="New milestone:  v{}".format(preview), icon='SOLO_ON')
        layout.prop(self, "label")

    def execute(self, context):
        if not _ensure_saved(self):
            return {'CANCELLED'}
        wm = context.window_manager.bvm
        item = _active_item(wm)
        if item is None:
            self.report({'ERROR'}, "No version selected.")
            return {'CANCELLED'}

        blend_path = bpy.data.filepath
        state = storage.load_state(blend_path)
        rec = storage.find_record(state["versions"], item.version)
        if rec is None:
            self.report({'ERROR'}, "Version not found.")
            return {'CANCELLED'}

        milestone = storage.next_milestone(state["versions"], self.level)
        rec["milestone"] = milestone
        rec["label"] = self.label
        rec["pinned"] = True  # milestones are protected from pruning
        storage.save_state(blend_path, state)

        _populate(context)
        self.report({'INFO'}, "Boosted v{:03d} to milestone v{}".format(
            item.version, milestone))
        return {'FINISHED'}


class BVM_OT_prune(Operator):
    bl_idname = "bvm.prune"
    bl_label = "Prune Old Versions"
    bl_description = ("Delete unpinned versions beyond the auto-keep limit "
                      "set in the add-on preferences")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath) and len(context.window_manager.bvm.versions) > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs.keep_max <= 0:
            self.report({'WARNING'},
                        "Set an Auto-keep limit in the add-on preferences first.")
            return {'CANCELLED'}

        blend_path = bpy.data.filepath
        state = storage.load_state(blend_path)
        doomed = set(storage.prune_candidates(state["versions"], prefs.keep_max))
        if not doomed:
            self.report({'INFO'}, "Nothing to prune.")
            return {'CANCELLED'}

        vd = storage.version_dir(blend_path)
        for rec in list(state["versions"]):
            if int(rec.get("version", -1)) in doomed:
                f = vd / rec.get("filename", "")
                try:
                    if f.exists():
                        f.unlink()
                except OSError:
                    pass
        state["versions"] = [r for r in state["versions"]
                             if int(r.get("version", -1)) not in doomed]
        storage.save_state(blend_path, state)

        _populate(context)
        self.report({'INFO'}, "Pruned {} version(s).".format(len(doomed)))
        return {'FINISHED'}


class BVM_OT_open_folder(Operator):
    bl_idname = "bvm.open_folder"
    bl_label = "Open Versions Folder"
    bl_description = "Reveal the versions folder in your system file browser"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def execute(self, context):
        vd = storage.version_dir(bpy.data.filepath)
        vd.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.path_open(filepath=str(vd))
        return {'FINISHED'}


classes = (
    BVM_OT_save_version,
    BVM_OT_refresh,
    BVM_OT_restore,
    BVM_OT_open,
    BVM_OT_delete,
    BVM_OT_edit_note,
    BVM_OT_toggle_pin,
    BVM_OT_boost,
    BVM_OT_prune,
    BVM_OT_open_folder,
)
