"""CLI command: component dependency graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

from hedron.cli.discovery import apply_project_discovery as _apply_project_discovery
from hedron.cli.discovery import load_app as _load_app
from hedron_core.registry import get_registry
from hedron_core.typing_aliases import JsonObject


def _cmd_graph(args: argparse.Namespace) -> int:
    _load_app(args.app)
    base = Path(getattr(args, "project", None) or Path.cwd()).resolve()
    _apply_project_discovery(base)
    try:
        from hedron_explorer.services.catalog import graph_json

        explorer_payload: dict[str, Any] = graph_json()
        inverse: dict[str, list[str]] = {}
        raw_edges = explorer_payload.get("edges")
        edges_list = cast(list[object], raw_edges) if isinstance(raw_edges, list) else []
        for edge_value in edges_list:
            edge = cast(dict[str, object], edge_value) if isinstance(edge_value, dict) else None
            if edge is not None:
                inverse.setdefault(str(edge.get("to")), []).append(str(edge.get("from")))
        explorer_payload["inverse_consumers"] = inverse
        print(json.dumps(explorer_payload, indent=2))
        return 0
    except ImportError:
        print("hedron-explorer: skipped (not installed)", file=sys.stderr)
    registry = get_registry()
    nodes: list[JsonObject] = []
    edges: list[JsonObject] = []
    for c in registry.components():
        nodes.append({"id": c.logical_id, "name": c.name, "kind": "component"})
        for dep in c.browser_modules:
            edges.append({"from": c.logical_id, "to": dep, "kind": "browser_module"})
        if c.styles_path:
            edges.append({"from": c.logical_id, "to": c.styles_path, "kind": "styles"})
    inverse: dict[str, list[str]] = {}
    for edge in edges:
        inverse.setdefault(str(edge["to"]), []).append(str(edge["from"]))
    payload: JsonObject = cast(
        JsonObject,
        {"nodes": nodes, "edges": edges, "inverse_consumers": inverse},
    )
    print(json.dumps(payload, indent=2))
    return 0


cmd_graph = _cmd_graph
