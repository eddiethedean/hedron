"""POSTURE-056 evidence."""

from __future__ import annotations

import json
from pathlib import Path

from hedron.cli.commands.security_check import (
    collect_posture,
    exit_code_for,
    report_to_sarif,
)


def test_posture_056_security_check_outputs(tmp_path: Path) -> None:
    suppressions = tmp_path / "suppressions.json"
    suppressions.write_text(
        json.dumps({"suppressions": [{"id": "SEC-056-DEV-EXPLORER", "expires": "2099-01-01"}]}),
        encoding="utf-8",
    )
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"fingerprints": []}), encoding="utf-8")
    report = collect_posture(
        project=Path(),
        policy_name="standard",
        suppressions_path=suppressions,
        baseline_path=baseline,
    )
    assert report.profile_version == "hedron-security-1"
    assert report.conformance_status in {"inventory_complete", "inventory_partial", "unknown"}
    payload = report.redacted_dict()
    assert "findings" in payload
    sarif = report_to_sarif(report)
    assert sarif["runs"][0]["tool"]["driver"]["name"] == "hedron-security-check"
    assert exit_code_for(report, strict=False) in {0, 2}
