"""CLI: offline application upgrade compatibility report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hedron.workflow import WorkflowManifest, build_upgrade_report, load_baseline


def _load_manifest(path: str | None) -> WorkflowManifest | None:
    if not path:
        return None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("manifest must be a JSON object")
    return WorkflowManifest(
        app_id=str(data.get("app_id") or "app"),
        layout_regions=tuple(data.get("layout_regions") or ()),
        capabilities=tuple(data.get("capabilities") or ()),
        action_safety=dict(data.get("action_safety") or {}),
        upload_requirements=dict(data.get("upload_requirements") or {}),
        security_headers=dict(data.get("security_headers") or {}),
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
