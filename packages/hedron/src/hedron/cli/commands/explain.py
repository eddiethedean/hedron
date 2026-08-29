"""CLI command: explain included features (``hedron explain features:ID``)."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import Any, cast

from hedron.cli.discovery import load_app as _load_app


def _cmd_explain(args: argparse.Namespace) -> int:
    target = str(getattr(args, "target", "") or "")
    if not target.startswith("features:"):
        print(
            f"hedron explain currently supports features:ID targets only (got {target!r})",
            file=sys.stderr,
        )
        return 2
    logical_id = target.split(":", 1)[1].strip()
    if not logical_id:
        print("hedron explain features:ID requires a non-empty feature id", file=sys.stderr)
        return 2
    app_path = getattr(args, "app", None)
    if not app_path:
        print("hedron explain requires --app module:attr", file=sys.stderr)
        return 2
    app = _load_app(app_path)
    if app is None:
        print(f"Could not load --app {app_path!r}", file=sys.stderr)
        return 1
    from hedron.features import explain_feature
    from hedron_core.bundles import FeatureConflictError

    try:
        payload = explain_feature(app, logical_id)
    except FeatureConflictError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    fmt = str(getattr(args, "format", "human") or "human")
    if fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        print(_format_human(payload))
    return 0


def _format_human(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    schema = payload.get("schema", "")
    logical_id = payload.get("logical_id", "")
    kind = payload.get("kind", "")
    lines.append(f"Feature {logical_id} ({kind})")
    if schema:
        lines.append(f"schema: {schema}")
    for key in ("surfaces", "routes", "effects", "security", "limitations", "source"):
        value = payload.get(key)
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            if not value:
                lines.append(f"{key}: (none)")
                continue
            lines.append(f"{key}:")
            for item in cast(Sequence[object], value):
                lines.append(f"  - {_short(item)}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for nested_key, nested_value in cast(dict[object, object], value).items():
                lines.append(f"  {nested_key}: {_short(nested_value)}")
        else:
            lines.append(f"{key}: {_short(value)}")
    return "\n".join(lines)


def _short(value: object) -> str:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value)
    return json.dumps(value, sort_keys=True, default=str)


cmd_explain = _cmd_explain
