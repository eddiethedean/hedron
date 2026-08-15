"""CLI command: inspect a component."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from hedron.cli.discovery import _find_component, _load_app, _registry_empty_hint
from hedron_core.typing_aliases import JsonObject


def _accessibility_contract_for(meta: object) -> Any:
    """Prefer curated reviewed contracts; fall back to an unreviewed stub."""
    from hedron_core.a11y import (
        AccessibilityContractCatalog,
        default_contract,
        seed_reviewed_contracts,
    )

    name = str(getattr(meta, "name", "") or "")
    package = getattr(meta, "distribution", None)
    pkg = package if isinstance(package, str) else "hedron-core"
    notes = str(getattr(meta, "accessibility_notes", None) or "")
    catalog = AccessibilityContractCatalog(package=pkg)
    seed_reviewed_contracts(catalog, package=pkg)
    catalog.ensure_registry(package=pkg)
    existing = catalog.contracts.get(name)
    if existing is not None:
        return existing
    return default_contract(name, package=pkg, notes=notes)


def _cmd_inspect(args: argparse.Namespace) -> int:
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
    contract = _accessibility_contract_for(meta)
    payload: JsonObject = {
        "logical_id": meta.logical_id,
        "name": meta.name,
        "module": meta.module,
        "distribution": meta.distribution,
        "props_model": meta.props_model,
        "slots": dict(meta.slots),
        "styles_path": meta.styles_path,
        "style_symbols": dict(meta.style_symbols),
        "browser_modules": list(meta.browser_modules),
        "folder_path": meta.folder_path,
        "accessibility_notes": meta.accessibility_notes,
        "accessibility_contract": contract.as_dict(),
        "accessibility_props_alongside_ordinary": True,
        "repair_guidance": {
            "reversible": True,
            "author_reviewed": True,
            "default_on": True,
        },
    }
    if meta.styles_path and Path(meta.styles_path).is_file():
        payload["styles"] = Path(meta.styles_path).read_text(encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0
