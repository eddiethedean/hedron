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
    if args.component == "interactions":
        return _cmd_inspect_interactions(args)
    if args.component == "features":
        return _cmd_inspect_features(args)
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


def _set_inspect_provenance(payload: JsonObject, *, mode: str) -> None:
    previous = payload.get("provenance")
    merged: JsonObject = dict(previous) if isinstance(previous, dict) else {}
    merged["mode"] = mode
    merged["unknown"] = False
    payload["provenance"] = merged


def _cmd_inspect_interactions(args: argparse.Namespace) -> int:
    from hedron.interactions import (
        app_interactions,
        inspect_interactions_static,
    )
    from hedron_core.catalog import compile_interaction_catalog

    as_json = bool(getattr(args, "json", False))
    manifest = getattr(args, "manifest", None)
    static_root = getattr(args, "static", None)
    if manifest:
        payload = inspect_interactions_static(Path("."), manifest=Path(manifest))
    elif static_root:
        payload = inspect_interactions_static(Path(static_root))
    elif getattr(args, "app", None):
        app = _load_app(args.app)
        catalog = app_interactions(app) if app is not None else compile_interaction_catalog()
        payload = catalog.to_manifest(profile="development").as_mapping()
        _set_inspect_provenance(payload, mode="trusted-app")
    else:
        catalog = compile_interaction_catalog()
        payload = catalog.to_manifest(profile="development").as_mapping()
        _set_inspect_provenance(payload, mode="process-registry")
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    entries = payload.get("entries") or []
    provenance = payload.get("provenance")
    mode = provenance.get("mode") if isinstance(provenance, dict) else None
    print(
        f"interactions  fingerprint="
        f"{payload.get('fingerprint') or payload.get('catalog_fingerprint')}"
    )
    print(f"mode={mode} unknown={payload.get('unknown', False)}")
    if not isinstance(entries, list):
        return 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        print(
            f"  {entry.get('logical_id')}  kind={entry.get('kind')}  "
            f"descriptor={entry.get('descriptor_fingerprint')}  "
            f"type={entry.get('type_schema_fingerprint') or 'absent'}"
        )
    return 0


def _cmd_inspect_features(args: argparse.Namespace) -> int:
    from hedron_core.bundles import included_bundles

    app_id = None
    if getattr(args, "app", None):
        app = _load_app(args.app)
        app_id = str(getattr(app, "hedron_app_id", "") or "") or None
    bundles = included_bundles(app_id=app_id)
    payload: JsonObject = {
        "features": [
            {
                "logical_id": item.logical_id,
                "provider": item.provider,
                "provider_version": item.provider_version,
                "views": [getattr(view, "logical_id", str(view)) for view in item.views],
                "commands": [
                    getattr(command, "logical_id", str(command)) for command in item.commands
                ],
                "projections": [proj.namespace for proj in item.projections],
                "dependencies": list(item.dependencies),
                "limitations": list(item.limitations),
            }
            for item in bundles
        ]
    }
    if bool(getattr(args, "json", False)):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(f"features  count={len(bundles)}")
    for item in bundles:
        print(f"  {item.logical_id}  provider={item.provider}  version={item.provider_version}")
    return 0
