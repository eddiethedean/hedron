"""UPGRADE-055 evidence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron.cli.commands.upgrade_report import _cmd_upgrade_report
from hedron.workflow import build_upgrade_report


def test_issue_547_offline_upgrade_report_json() -> None:
    report = build_upgrade_report(from_version="0.54.0", to_version="0.55.0")
    data = report.to_dict()
    assert data["offline"] is True
    assert data["schema_version"] == "hedron-upgrade-report-1"
    assert any(f["kind"] == "heuristic" for f in data["findings"])
    assert report.exit_code() == 0

    bad = build_upgrade_report(from_version="9.0", to_version="0.55.0")
    assert bad.exit_code() == 2


def test_upgrade_report_cli_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"app_id": "demo", "migration_status": "legacy"}),
        encoding="utf-8",
    )
    ns = type(
        "NS",
        (),
        {
            "from_version": "0.54.0",
            "to_version": "0.55.0",
            "baseline": None,
            "manifest": str(manifest),
            "out": str(out),
            "allow_definite": True,
        },
    )()
    with pytest.raises(SystemExit) as exc:
        _cmd_upgrade_report(ns)
    assert exc.value.code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["offline"] is True
    assert any(f["code"] == "HED-UPGRADE-1001" for f in payload["findings"])
