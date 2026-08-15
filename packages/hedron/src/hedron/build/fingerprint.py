"""Relink fingerprinted ES modules after copy-fingerprint."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron.build.rewrite import _rewrite_module_imports
from hedron_core.assets import fingerprint_bytes


def _relink_fingerprinted_modules(
    assets_dir: Path,
    entries: list[Any],
    *,
    basename_by_path: dict[str, str],
) -> list[Any]:
    """After copy-fingerprint, rewrite relative imports and re-emit changed modules."""
    from hedron_core.manifests import AssetEntry

    # Bound iterations: longest import chain cannot exceed module count.
    for _ in range(max(len(basename_by_path), 1) + 2):
        changed = False
        basename_map = {basename_by_path[path]: path for path in list(basename_by_path)}
        for index, entry in enumerate(list(entries)):
            if not isinstance(entry, AssetEntry) or entry.kind != "module":
                continue
            if not entry.path.endswith((".mjs", ".js")):
                continue
            dest = assets_dir / entry.path
            if not dest.is_file():
                continue
            text = dest.read_text(encoding="utf-8")
            rewritten = _rewrite_module_imports(text, basename_map)
            if rewritten == text:
                continue
            original_basename = basename_by_path.get(entry.path, Path(entry.path).name)
            stem = Path(original_basename).stem
            suffix = Path(original_basename).suffix or ".mjs"
            old_path = entry.path
            dest.unlink(missing_ok=True)
            new_entry = fingerprint_bytes(
                rewritten.encode("utf-8"),
                output_dir=assets_dir,
                logical_id=entry.logical_id,
                kind=entry.kind,
                filename_prefix=stem,
                suffix=suffix,
                content_type=entry.content_type or "text/javascript",
                attributes=dict(entry.attributes),
            )
            entries[index] = new_entry
            basename_by_path.pop(old_path, None)
            basename_by_path[new_entry.path] = original_basename
            changed = True
        if not changed:
            break
    return entries
