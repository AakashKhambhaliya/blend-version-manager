"""Blend Version Manager — save, browse and restore versions of a .blend file.

Packaged as a Blender 4.2+ extension (metadata lives in blender_manifest.toml,
so there is intentionally no bl_info here).
"""

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
