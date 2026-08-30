"""CLI: offline application upgrade compatibility report."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from hedron.workflow import WorkflowManifest, build_upgrade_report, load_baseline


def _load_manifest(path: str | None) -> WorkflowManifest | None:
    if not path:
        return None
    decoded: object = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        raise SystemExit("manifest must be a JSON object")
    data = cast(dict[str, object], decoded)

    def string_tuple(key: str) -> tuple[str, ...]:
        value = data.get(key, ())
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise ValueError(f"manifest {key!r} must be an array")
        if not all(isinstance(item, str) for item in cast(Sequence[object], value)):
            raise ValueError(f"manifest {key!r} must contain only strings")
        return tuple(cast(Sequence[str], value))

    def mapping(key: str) -> dict[str, object]:
        value = data.get(key, {})
        if not isinstance(value, Mapping):
            raise ValueError(f"manifest {key!r} must be an object")
        return {str(name): item for name, item in cast(Mapping[object, object], value).items()}

    action_safety_values = mapping("action_safety")
    if not all(isinstance(value, str) for value in action_safety_values.values()):
        raise ValueError("manifest 'action_safety' values must be strings")
    return WorkflowManifest(
        app_id=str(data.get("app_id") or "app"),
        layout_regions=string_tuple("layout_regions"),
        capabilities=string_tuple("capabilities"),
        action_safety=cast(dict[str, str], action_safety_values),
        upload_requirements=mapping("upload_requirements"),
        security_headers=mapping("security_headers"),
        migration_status=str(data.get("migration_status") or "legacy"),
    )


def _cmd_upgrade_report(args: argparse.Namespace) -> None:
    try:
        baseline = load_baseline(Path(args.baseline)) if args.baseline else None
        manifest = _load_manifest(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"upgrade-report: {exc}\n")
        raise SystemExit(1) from exc
    report = build_upgrade_report(
        from_version=args.from_version,
        to_version=args.to_version,
        baseline=baseline,
        manifest=manifest,
    )
    payload = report.to_dict()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    raise SystemExit(report.exit_code(fail_on_definite=not args.allow_definite))


cmd_upgrade_report = _cmd_upgrade_report
