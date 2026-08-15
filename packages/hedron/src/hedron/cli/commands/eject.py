"""CLI command: eject component contract and CSS."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from hedron.cli.commands.inspect import _accessibility_contract_for
from hedron.cli.discovery import _find_component, _load_app, _registry_empty_hint


def _cmd_eject(args: argparse.Namespace) -> int:
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
        out_dir = Path(args.out).expanduser().resolve()
        try:
            out_dir.relative_to(cwd)
        except ValueError:
            print(
                f"Refusing to eject outside the project root: {out_dir}",
                file=sys.stderr,
            )
            return 1
    else:
        out_dir = cwd / "components" / meta.name
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
