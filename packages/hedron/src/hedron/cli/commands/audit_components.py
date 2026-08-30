"""CLI command: capability and package audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from hedron.cli.discovery import apply_project_discovery as _apply_project_discovery
from hedron.cli.discovery import load_app as _load_app
from hedron_core.registry import get_registry
from hedron_core.typing_aliases import JsonObject, PluginMetaDict


def _cmd_audit_components(args: argparse.Namespace) -> int:
    _load_app(args.app)
    base = Path(getattr(args, "project", None) or Path.cwd()).resolve()
    _apply_project_discovery(base)
    from hedron_core.plugins import get_diagnostic_owners, get_explorer_panels

    registry = get_registry()
    rows: list[JsonObject] = []
    for c in registry.components():
        rows.append(
            {
                "logical_id": c.logical_id,
                "name": c.name,
                "distribution": c.distribution,
                "module": c.module,
                "capabilities": {
                    "styles": bool(c.styles_path),
                    "browser_js": bool(c.browser_modules),
                    "assets": bool(c.asset_roots),
                },
            }
        )
    plugin_rows: list[JsonObject] = []
    try:
        from importlib.metadata import entry_points

        from hedron.plugins import ENTRY_POINT_GROUP

        eps = entry_points()
        discovered = (
            list(eps.select(group=ENTRY_POINT_GROUP))
            if hasattr(eps, "select")
            else list(eps.get(ENTRY_POINT_GROUP, []))  # type: ignore[arg-type]
        )
        for ep in discovered:
            try:
                target = ep.load()
                meta = getattr(target, "PLUGIN_META", None)
                if meta is not None:
                    plugin_rows.append(cast(JsonObject, cast(PluginMetaDict, meta.to_dict())))
                else:
                    plugin_rows.append({"name": ep.name, "version": "unknown"})
            except Exception as exc:  # noqa: BLE001
                plugin_rows.append({"name": ep.name, "error": str(exc)})
    except Exception:  # noqa: BLE001
        plugin_rows = []
    payload: JsonObject = cast(
        JsonObject,
        {
            "components": rows,
            "plugins": plugin_rows,
            "explorer_panels": [p.to_dict() for p in get_explorer_panels()],
            "diagnostic_owners": dict(get_diagnostic_owners()),
        },
    )
    print(json.dumps(payload, indent=2))
    return 0


cmd_audit_components = _cmd_audit_components
