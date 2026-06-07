"""Add-on preferences (Edit > Preferences > Add-ons > Blend Version Manager)."""

from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import AddonPreferences


def get_prefs(context):
    """Return this add-on's preferences. ``__package__`` is the add-on id."""
    return context.preferences.addons[__package__].preferences


class BVM_Preferences(AddonPreferences):
    bl_idname = __package__

    auto_snapshot_on_restore: BoolProperty(
        name="Safety snapshot before restore",
        description="Save a snapshot of the current file before it is overwritten by a restore",
        default=True,
    )
    confirm_destructive: BoolProperty(
        name="Confirm destructive actions",
        description="Ask before restoring or deleting a version",
        default=True,
    )
    keep_max: IntProperty(
        name="Auto-keep limit",
        description="When pruning, keep this many newest unpinned versions (0 = unlimited)",
        default=0,
        min=0,
        soft_max=100,
    )
    default_note: StringProperty(
        name="Default note",
        description="Used as the note when you save a version with the note field left empty",
        default="",
    )
    compress: BoolProperty(
        name="Compress version files",
        description="Write version copies compressed (smaller files, slightly slower)",
        default=True,
    )

    # --- Auto-versioning ---
    auto_mode: EnumProperty(
        name="Auto-version on save",
        description="Automatically create a version each time you save the file",
        items=(
            ('OFF', "Off", "Never version automatically", 'X', 0),
            ('EVERY', "Every save", "Version on every save", 'FILE_TICK', 1),
            ('NTH', "Every Nth save", "Version on every Nth save", 'LINENUMBERS_ON', 2),
            ('INTERVAL', "Time interval", "At most one auto-version per N minutes", 'TIME', 3),
        ),
        default='OFF',
    )
    auto_every_n: IntProperty(
        name="Every N saves",
        description="Create an auto-version on every Nth save",
        default=3,
        min=1,
        soft_max=20,
    )
    auto_min_minutes: FloatProperty(
        name="Min interval (min)",
        description="Minimum minutes between auto-versions",
        default=5.0,
        min=0.0,
        soft_max=120.0,
    )
    auto_prune: BoolProperty(
        name="Auto-prune after auto-version",
        description="After each auto-version, prune to the auto-keep limit "
                    "(pinned versions are always kept)",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column(heading="Behaviour")
        col.prop(self, "auto_snapshot_on_restore")
        col.prop(self, "confirm_destructive")
        col.prop(self, "compress")

        col = layout.column()
        col.prop(self, "keep_max")
        col.prop(self, "default_note")

        box = layout.box()
        box.label(text="Auto-versioning", icon='TIME')
        box.prop(self, "auto_mode")
        if self.auto_mode == 'NTH':
            box.prop(self, "auto_every_n")
        elif self.auto_mode == 'INTERVAL':
            box.prop(self, "auto_min_minutes")
        if self.auto_mode != 'OFF':
            box.prop(self, "auto_prune")
