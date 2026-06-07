"""Pure file/metadata helpers for the version manager.

No ``bpy`` dependency, so it can be unit-checked outside Blender. The on-disk
state is a single ``versions.json`` holding a small dict::

    {"schema": 1, "current": <int>, "versions": [ {record}, ... ]}

Each record: version, filename, timestamp, note, blender_version, size, pinned.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

VERSIONS_DIRNAME = ".blendversions"
MANIFEST_NAME = "versions.json"
SCHEMA = 1


def version_dir(blend_path):
    """Folder that holds the versions + manifest for a given .blend file."""
    p = Path(blend_path)
    return p.parent / VERSIONS_DIRNAME / p.stem


def manifest_path(blend_path):
    return version_dir(blend_path) / MANIFEST_NAME


def _empty_state():
    return {"schema": SCHEMA, "current": 0, "versions": []}


def load_state(blend_path):
    """Return the full state dict; tolerant of missing/corrupt/legacy files."""
    mp = manifest_path(blend_path)
    if not mp.exists():
        return _empty_state()
    try:
        with open(mp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _empty_state()

    # Legacy format was a bare list of records.
    if isinstance(data, list):
        return {"schema": SCHEMA, "current": 0, "versions": data}
    if isinstance(data, dict):
        return {
            "schema": data.get("schema", SCHEMA),
            "current": int(data.get("current", 0)),
            "versions": data.get("versions", []),
        }
    return _empty_state()


def save_state(blend_path, state):
    """Atomically persist the state dict (write temp, then replace)."""
    vd = version_dir(blend_path)
    vd.mkdir(parents=True, exist_ok=True)
    state["schema"] = SCHEMA
    mp = manifest_path(blend_path)
    tmp = mp.with_name(mp.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    tmp.replace(mp)


def next_version_number(versions):
    if not versions:
        return 1
    return max(int(r.get("version", 0)) for r in versions) + 1


def version_filename(blend_path, number):
    return "{}_v{:03d}.blend".format(Path(blend_path).stem, number)


def next_version_path(blend_path, versions):
    number = next_version_number(versions)
    return version_dir(blend_path) / version_filename(blend_path, number)


def make_record(number, filename, note, blender_version, size=0, pinned=False):
    return {
        "version": int(number),
        "filename": filename,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "note": note or "",
        "blender_version": blender_version,
        "size": int(size),
        "pinned": bool(pinned),
    }


def find_record(versions, number):
    for rec in versions:
        if int(rec.get("version", -1)) == int(number):
            return rec
    return None


def copy_file(src, dst):
    """Plain binary copy (used for restore/snapshot of an existing file)."""
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dst_path))


def total_size(versions):
    return sum(int(r.get("size", 0)) for r in versions)


def human_size(num):
    """Human-readable byte size, e.g. 34.5 MB."""
    num = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024.0 or unit == "TB":
            return "{:.0f} {}".format(num, unit) if unit == "B" else "{:.1f} {}".format(num, unit)
        num /= 1024.0


def short_timestamp(iso):
    """'2026-06-07T15:10:42' -> '2026-06-07 15:10'."""
    if not iso:
        return ""
    return iso.replace("T", " ")[:16]


def parse_milestone(text):
    """'1.2.3' -> (1, 2, 3); returns None if not a valid semver-ish string."""
    if not text:
        return None
    try:
        parts = [int(x) for x in str(text).split(".")]
    except (ValueError, AttributeError):
        return None
    if not parts:
        return None
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def format_milestone(triple):
    return "{}.{}.{}".format(*triple)


def highest_milestone(versions):
    """Highest milestone among version records, as a triple (default 0,0,0)."""
    best = (0, 0, 0)
    for rec in versions:
        mv = parse_milestone(rec.get("milestone", ""))
        if mv and mv > best:
            best = mv
    return best


def bump_milestone(current, level):
    """Bump a (maj, min, patch) triple by 'MAJOR' | 'MINOR' | 'PATCH'."""
    maj, minr, pat = current
    if level == 'MAJOR':
        return (maj + 1, 0, 0)
    if level == 'MINOR':
        return (maj, minr + 1, 0)
    return (maj, minr, pat + 1)


def next_milestone(versions, level):
    """Next milestone string for a boost at the given level."""
    return format_milestone(bump_milestone(highest_milestone(versions), level))


def prune_candidates(versions, keep):
    """Return version numbers to delete: oldest unpinned beyond ``keep`` newest.

    Pinned versions are never candidates and do not consume a keep slot.
    keep <= 0 means 'unlimited' -> nothing pruned.
    """
    if keep is None or keep <= 0:
        return []
    unpinned = sorted(
        (r for r in versions if not r.get("pinned")),
        key=lambda r: int(r.get("version", 0)),
        reverse=True,
    )
    return [int(r.get("version", 0)) for r in unpinned[keep:]]
