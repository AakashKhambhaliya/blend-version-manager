"""Automatic versioning driven by Blender's ``save_post`` handler.

After every real save, this copies the just-written .blend into a new version
slot (subject to the throttle in Preferences). It never calls a Blender save
itself (it copies the file that is already on disk), so it cannot recurse — and
our own internal saves in operators.py are additionally wrapped in ``suspend()``
as belt-and-braces.
"""

import time

import bpy
from bpy.app.handlers import persistent

from . import storage
from .prefs import get_prefs

# Re-entrancy guard: True while the add-on performs its own internal saves.
_suspended = False
# Process-lifetime throttle state, keyed by .blend path.
_last_auto = {}
_save_counter = {}


class suspend:
    """Context manager that suppresses auto-versioning for internal saves."""

    def __enter__(self):
        global _suspended
        self._prev = _suspended
        _suspended = True
        return self

    def __exit__(self, *exc):
        global _suspended
        _suspended = self._prev
        return False


def reset_state():
    _last_auto.clear()
    _save_counter.clear()


def _should_version(path, prefs):
    """Apply the throttle rules; return True if a version should be made now."""
    mode = prefs.auto_mode
    if mode == 'OFF':
        return False

    if mode == 'NTH':
        count = _save_counter.get(path, 0) + 1
        _save_counter[path] = count
        return count % max(prefs.auto_every_n, 1) == 0

    if mode == 'INTERVAL':
        min_sec = max(prefs.auto_min_minutes, 0.0) * 60.0
        if min_sec > 0.0 and (time.time() - _last_auto.get(path, 0.0)) < min_sec:
            return False
        return True

    # 'EVERY'
    return True


def _make_auto_version(context, path, prefs):
    state = storage.load_state(path)
    versions = state["versions"]
    number = storage.next_version_number(versions)
    target = storage.next_version_path(path, versions)
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        storage.copy_file(path, target)  # copy the file Blender just saved
    except OSError:
        return

    size = target.stat().st_size if target.exists() else 0
    rec = storage.make_record(number, target.name, "[auto-save]",
                              bpy.app.version_string, size=size)
    rec["kind"] = "auto"
    versions.append(rec)
    state["current"] = number

    # Optional cleanup so auto-versions don't accumulate forever.
    if prefs.auto_prune and prefs.keep_max > 0:
        doomed = set(storage.prune_candidates(versions, prefs.keep_max))
        if doomed:
            vd = storage.version_dir(path)
            for r in list(versions):
                if int(r.get("version", -1)) in doomed:
                    f = vd / r.get("filename", "")
                    try:
                        if f.exists():
                            f.unlink()
                    except OSError:
                        pass
            state["versions"] = [r for r in versions
                                 if int(r.get("version", -1)) not in doomed]

    storage.save_state(path, state)
    _last_auto[path] = time.time()

    # Repopulate the UI list directly (avoids invoking an operator in a handler).
    try:
        from . import operators
        operators._populate(context)
    except Exception:
        pass


@persistent
def on_save_post(_dummy):
    if _suspended or bpy.app.background:
        return
    path = bpy.data.filepath
    if not path:
        return
    try:
        context = bpy.context
        prefs = get_prefs(context)
    except (KeyError, AttributeError):
        return
    if _should_version(path, prefs):
        _make_auto_version(context, path, prefs)
