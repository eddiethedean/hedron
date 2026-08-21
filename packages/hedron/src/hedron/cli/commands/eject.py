"""CLI command: eject component contract and CSS."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from hedron.cli.commands.inspect import _accessibility_contract_for
from hedron.cli.discovery import _find_component, _load_app, _registry_empty_hint


def _assert_project_write_path(path: Path, *, cwd: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(cwd)
    except ValueError as exc:
        raise ValueError(f"Refusing to eject outside the project root: {resolved}") from exc
    cursor = resolved
    while True:
        if cursor.exists() and cursor.is_symlink():
            raise ValueError(f"Refusing to write through symlink: {cursor}")
        if cursor == cwd or cursor.parent == cursor:
            break
        cursor = cursor.parent
    return resolved


def _cmd_eject(args: argparse.Namespace) -> int:
    target = str(args.component or "")
    if target == "features" or target.startswith("features:"):
        return _cmd_eject_feature(args)
    _load_app(args.app)
    from hedron.config import load_hedron_settings
    from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders

    settings = load_hedron_settings(Path.cwd())
    discovered = discover_component_folders(settings.resolved_roots(base=Path.cwd()))
    apply_discovery_to_registry(discovered)

    meta = _find_component(args.component)
    if meta is None:
        _registry_empty_hint(app=args.app, what="components")
        print(f"Component {args.component!r} not found", file=sys.stderr)
        return 1
    # Never trust registry ``folder_path`` as a write root (same policy as Explorer reads).
    cwd = Path.cwd().resolve()
    if args.out:
        try:
            out_dir = _assert_project_write_path(Path(args.out), cwd=cwd)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    else:
        out_dir = cwd / "components" / meta.name
        try:
            _assert_project_write_path(out_dir, cwd=cwd)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    contract = _accessibility_contract_for(meta)
    contract_path = out_dir / "accessibility_contract.json"
    if contract_path.exists() and not args.force:
        print(f"Refusing to overwrite {contract_path} (use --force)", file=sys.stderr)
        return 1
    contract_path.write_text(
        json.dumps(contract.as_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    written.append(str(contract_path))
    if meta.styles_path and Path(meta.styles_path).is_file():
        dest = out_dir / "styles.css"
        if dest.exists() and not args.force:
            print(f"Refusing to overwrite {dest} (use --force)", file=sys.stderr)
            return 1
        shutil.copy2(meta.styles_path, dest)
        written.append(str(dest))
    elif meta.styles_path is None:
        dest = out_dir / "styles.css"
        if not dest.exists() or args.force:
            dest.write_text(
                f"/* Ejected styles for {meta.logical_id} */\n.root {{\n  display: block;\n}}\n",
                encoding="utf-8",
            )
            written.append(str(dest))
    if not written:
        print(
            f"Nothing written for {meta.logical_id!r} "
            "(sources missing and starter files already present; use --force).",
            file=sys.stderr,
        )
        return 1
    print(json.dumps({"component": meta.logical_id, "written": written}, indent=2))
    return 0


def _cmd_eject_feature(args: argparse.Namespace) -> int:
    from hedron.features import eject_feature
    from hedron_core.bundles import FeatureConflictError, eject_source, included_bundles

    target = str(args.component or "")
    logical_id = target.split(":", 1)[1] if ":" in target else ""
    app = _load_app(getattr(args, "app", None))
    app_id = str(getattr(app, "hedron_app_id", "") or "") if app is not None else ""
    if not logical_id:
        bundles = included_bundles(app_id=app_id or None)
        if not bundles:
            print("No FeatureBundles included", file=sys.stderr)
            return 1
        logical_id = bundles[0].logical_id
    cwd = Path.cwd().resolve()
    try:
        out_dir = (
            _assert_project_write_path(Path(args.out), cwd=cwd)
            if args.out
            else _assert_project_write_path(cwd / "ejected" / logical_id, cwd=cwd)
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    surface = getattr(args, "surface", None)
    overwrite = bool(getattr(args, "force", False))
    if app is not None:
        try:
            source = eject_feature(
                app,
                logical_id,
                surface=surface,
                output=out_dir,
                overwrite=overwrite,
            )
        except FeatureConflictError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        written = [str(out_dir / "explicit.py"), str(out_dir / "source_map.json")]
        print(
            json.dumps(
                {"feature": logical_id, "surface": surface or "*", "written": written},
                indent=2,
            )
        )
        return 0
    dest = out_dir / "explicit.py"
    if dest.exists() and not overwrite:
        print(f"Refusing to overwrite {dest} (use --overwrite)", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    matches = [
        item for item in included_bundles(app_id=app_id or None) if item.logical_id == logical_id
    ]
    if not matches:
        print(f"FeatureBundle {logical_id!r} not found", file=sys.stderr)
        return 1
    source = eject_source(matches[0])
    if surface is not None:
        source = (
            f"{source}\n"
            f"# Selected surface: {surface!r}\n"
            f"# Remaining surfaces were omitted from this ejection selection.\n"
        )
    dest.write_text(source, encoding="utf-8")
    print(
        json.dumps(
            {"feature": logical_id, "surface": surface or "*", "written": [str(dest)]},
            indent=2,
        )
    )
    return 0
