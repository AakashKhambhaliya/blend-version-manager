"""Property definitions for the version manager.

State lives on ``WindowManager`` (session-scoped). It is rebuilt from
``versions.json`` on demand, so nothing is baked into the saved .blend file.
"""

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup


class BVM_VersionItem(PropertyGroup):
    """One row in the version list (mirrors a record in versions.json)."""

    version: IntProperty(name="Version")
    filename: StringProperty(name="File")
    timestamp: StringProperty(name="Saved")
    date_short: StringProperty(name="Date")
    note: StringProperty(name="Note")
    blender_version: StringProperty(name="Blender")
    # Stored as a float (double): a 32-bit IntProperty overflows and raises
    # OverflowError for .blend files larger than ~2.1 GB.
    size: FloatProperty(name="Size", default=0.0)
    pinned: BoolProperty(name="Pinned")
    kind: StringProperty(name="Kind", default="manual")
    milestone: StringProperty(name="Milestone")
    label: StringProperty(name="Label")


class BVM_Props(PropertyGroup):
    versions: CollectionProperty(type=BVM_VersionItem)
    active_index: IntProperty(name="Active Version", default=0)
    current_version: IntProperty(name="Current Version", default=0)

    new_note: StringProperty(
        name="Note",
        description="Description stored with the next saved version",
        default="",
    )
    search: StringProperty(
        name="Search",
        description="Filter versions by note text or number",
        default="",
        options={'TEXTEDIT_UPDATE'},
    )
    show_pinned_only: BoolProperty(
        name="Pinned only",
        description="Show only pinned versions",
        default=False,
    )
    sort_order: EnumProperty(
        name="Sort",
        description="Order versions are displayed in",
        items=(
            ('NEWEST', "Newest first", "Highest version number on top", 'SORT_DESC', 0),
            ('OLDEST', "Oldest first", "Lowest version number on top", 'SORT_ASC', 1),
        ),
        default='NEWEST',
    )
    pinned_first: BoolProperty(
        name="Pinned on top",
        description="Always list pinned versions before the rest",
        default=True,
    )
