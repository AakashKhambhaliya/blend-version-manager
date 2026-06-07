"""Blend Version Manager — save, browse and restore versions of a .blend file.

Combined add-on + extension:
- ``blender_manifest.toml`` makes it a Blender 4.2+ *extension* (Releases zip).
- ``bl_info`` below makes it installable as a classic *legacy add-on* too, so
  GitHub's "Code > Download ZIP" can be installed directly. Blender ignores
  ``bl_info`` when the add-on is loaded as an extension.
"""

bl_info = {
    "name": "Blend Version Manager",
    "author": "AakashKhambhaliya",
    "version": (1, 4, 5),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar (N) > Versions",
    "description": "Save, browse and restore versions of your .blend file.",
    "category": "System",
    "doc_url": "https://github.com/AakashKhambhaliya/blend-version-manager",
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import PointerProperty

from . import props
from . import prefs
from . import operators
from . import panel
from . import autosave

_classes = (
    prefs.BVM_Preferences,
    props.BVM_VersionItem,
    props.BVM_Props,
    *operators.classes,
    *panel.classes,
)


@persistent
def _on_load_post(*_args):
    """Auto-refresh the version list whenever a .blend file is opened.

    Accepts ``*args`` because Blender 3.6+ passes a filepath argument to file
    handlers in addition to the legacy scene/dummy argument.
    """
    try:
        bpy.ops.bvm.refresh()
    except Exception:
        pass


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.bvm = PointerProperty(type=props.BVM_Props)
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)
    if autosave.on_save_post not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(autosave.on_save_post)


def unregister():
    if autosave.on_save_post in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(autosave.on_save_post)
    autosave.reset_state()
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    if hasattr(bpy.types.WindowManager, "bvm"):
        del bpy.types.WindowManager.bvm
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
