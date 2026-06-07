"""UI: a professional version browser in the 3D viewport sidebar.

Layout follows Blender's native "list + side button column" idiom, with a
search/sort filter header, a current-version marker, pin badges and collapsible
sub-panels for details and maintenance.
"""

import bpy
from bpy.types import Panel, UIList

from . import storage
from .prefs import get_prefs


class BVM_UL_versions(UIList):
    """Two-line version row for narrow panels.

    Line 1: marker, version number, milestone badge and (auto/pin) badges.
    Line 2: the timestamp.
    The note is intentionally NOT shown here — select a version to read/edit its
    note (and full metadata) in the Details sub-panel below.
    """

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        wm = context.window_manager.bvm
        is_current = item.version == wm.current_version

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            col = layout.column(align=True)

            # Line 1: marker + version + milestone + trailing badges.
            top = col.row(align=True)
            top.label(text="", icon='RADIOBUT_ON' if is_current else 'RADIOBUT_OFF')
            top.label(text="v{:03d}".format(item.version))
            if item.milestone:
                ms = top.row(align=True)
                ms.label(text="v{}".format(item.milestone), icon='SOLO_ON')

            badges = top.row(align=True)
            badges.alignment = 'RIGHT'
            if item.kind == 'auto':
                badges.label(text="", icon='TIME')
            if item.pinned:
                badges.label(text="", icon='PINNED')

            # Line 2: timestamp, indented to align under the version label.
            bottom = col.row(align=True)
            bottom.label(text="", icon='BLANK1')
            bottom.label(text=item.date_short or "—")

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="v{:03d}".format(item.version))

    def draw_filter(self, context, layout):
        wm = context.window_manager.bvm
        row = layout.row(align=True)
        row.prop(wm, "search", text="", icon='VIEWZOOM')
        row.prop(wm, "show_pinned_only", text="", icon='PINNED', toggle=True)
        row = layout.row(align=True)
        row.prop(wm, "sort_order", expand=True)
        row.prop(wm, "pinned_first", text="", icon='SORTBYEXT', toggle=True)

    def filter_items(self, context, data, propname):
        wm = context.window_manager.bvm
        items = getattr(data, propname)
        flags = []
        order = []

        search = wm.search.lower().strip()
        show_pinned_only = wm.show_pinned_only
        for it in items:
            visible = True
            if show_pinned_only and not it.pinned:
                visible = False
            if visible and search:
                hay = "{} v{:03d} {}".format(it.note, it.version, it.blender_version).lower()
                visible = search in hay
            flags.append(self.bitflag_filter_item if visible else 0)

        idx = list(range(len(items)))
        idx.sort(key=lambda i: items[i].version,
                 reverse=(wm.sort_order == 'NEWEST'))
        if wm.pinned_first:
            idx.sort(key=lambda i: not items[i].pinned)  # stable: pinned first
        order = [0] * len(items)
        for pos, orig in enumerate(idx):
            order[orig] = pos

        return flags, order


def _selected(wm):
    if 0 <= wm.active_index < len(wm.versions):
        return wm.versions[wm.active_index]
    return None


class BVM_PT_panel(Panel):
    bl_label = "Version Manager"
    bl_idname = "BVM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Versions"

    def draw_header(self, context):
        self.layout.label(text="", icon='RECOVER_LAST')

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager.bvm

        if not bpy.data.filepath:
            box = layout.box()
            box.label(text="Unsaved file", icon='ERROR')
            box.label(text="Save the .blend first to start versioning.")
            return

        # Stats line.
        total = storage.total_size([{"size": v.size} for v in wm.versions])
        head = layout.row(align=True)
        head.label(text="{} version{}".format(len(wm.versions),
                                               "" if len(wm.versions) == 1 else "s"),
                   icon='DOCUMENTS')
        sub = head.row()
        sub.alignment = 'RIGHT'
        sub.label(text=storage.human_size(total))

        # New version block.
        box = layout.box()
        box.label(text="New Version", icon='FILE_NEW')
        box.prop(wm, "new_note", text="", icon='TEXT')
        box.operator("bvm.save_version", icon='FILE_TICK')

        prefs = get_prefs(context)
        auto = box.row(align=True)
        auto_on = prefs.auto_mode != 'OFF'
        auto.prop(prefs, "auto_mode", text="Auto",
                  icon='TIME' if auto_on else 'X')
        if prefs.auto_mode == 'NTH':
            auto.prop(prefs, "auto_every_n", text="N")
        elif prefs.auto_mode == 'INTERVAL':
            auto.prop(prefs, "auto_min_minutes", text="min")

        # List + native side-button column.
        layout.separator()
        row = layout.row()
        row.template_list("BVM_UL_versions", "", wm, "versions",
                          wm, "active_index", rows=8)

        col = row.column(align=True)
        col.operator("bvm.save_version", icon='ADD', text="")
        col.operator("bvm.delete", icon='REMOVE', text="")
        col.separator()
        col.operator("bvm.boost", icon='SOLO_ON', text="")
        col.operator("bvm.toggle_pin", icon='PINNED', text="")
        col.operator("bvm.edit_note", icon='GREASEPENCIL', text="")
        col.separator()
        col.operator("bvm.refresh", icon='FILE_REFRESH', text="")

        # Primary actions.
        actions = layout.row(align=True)
        actions.scale_y = 1.2
        actions.operator("bvm.restore", icon='RECOVER_LAST', text="Restore")
        actions.operator("bvm.open", icon='FILE_FOLDER', text="Open")


class BVM_PT_details(Panel):
    bl_label = "Details"
    bl_idname = "BVM_PT_details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Versions"
    bl_parent_id = "BVM_PT_panel"

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager.bvm
        item = _selected(wm)
        if item is None:
            layout.label(text="No version selected.", icon='INFO')
            return

        is_current = item.version == wm.current_version
        col = layout.column(align=True)
        title = col.row(align=True)
        title.label(text="v{:03d}".format(item.version), icon='FILE_BLEND')
        if is_current:
            badge = title.row()
            badge.alignment = 'RIGHT'
            badge.label(text="current", icon='RADIOBUT_ON')

        if item.milestone:
            ms = layout.box().row()
            ms.label(text="Milestone  v{}".format(item.milestone), icon='SOLO_ON')
            if item.label:
                ms.label(text=item.label)

        # Note — the prominent element of the details, with inline edit.
        note_box = layout.box()
        header = note_box.row(align=True)
        header.label(text="Note", icon='TEXT')
        header.operator("bvm.edit_note", text="", icon='GREASEPENCIL', emboss=False)
        note_box.label(text=item.note if item.note else "(no note)")

        # Short metadata: label/value pairs use split() so they stay readable
        # even in a narrow panel.
        for label, value in (
            ("Saved", storage.short_timestamp(item.timestamp) or "—"),
            ("Size", storage.human_size(item.size)),
            ("Blender", item.blender_version or "—"),
        ):
            split = layout.split(factor=0.34, align=True)
            split.label(text=label)
            split.label(text=value)

        # Filename can be long: give it its own full-width line.
        fcol = layout.column(align=True)
        fcol.label(text="File", icon='FILE_BLEND')
        fcol.label(text=item.filename or "—")

        row = layout.row(align=True)
        row.operator("bvm.edit_note", icon='GREASEPENCIL', text="Edit Note")
        row.operator("bvm.toggle_pin",
                     icon='PINNED' if item.pinned else 'UNPINNED',
                     text="Unpin" if item.pinned else "Pin")
        layout.operator("bvm.boost", icon='SOLO_ON',
                        text="Boost to Milestone")


class BVM_PT_maintenance(Panel):
    bl_label = "Maintenance"
    bl_idname = "BVM_PT_maintenance"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Versions"
    bl_parent_id = "BVM_PT_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("bvm.open_folder", icon='FILEBROWSER')
        col.operator("bvm.prune", icon='TRASH')
        col.operator("bvm.refresh", icon='FILE_REFRESH')
        layout.operator("preferences.addon_show",
                        text="Add-on Settings", icon='PREFERENCES').module = __package__


classes = (
    BVM_UL_versions,
    BVM_PT_panel,
    BVM_PT_details,
    BVM_PT_maintenance,
)
