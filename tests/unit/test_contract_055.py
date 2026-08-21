"""CONTRACT-055 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron.workflow import REASON_CODES, WorkflowBudget, WorkflowManifest


def test_contract_055_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.55.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["CONTRACT-055"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md").is_file()


def test_workflow_manifest_redacts_and_lists_reason_codes() -> None:
    manifest = WorkflowManifest(
        layout_regions=("master", "detail"),
        capabilities=("items.edit",),
        security_headers={"raw_csp": "secret", "mode": "standard"},
        budgets=WorkflowBudget(body_bytes=1024),
    )
    data = manifest.redacted_dict()
    assert "raw_csp" not in data["security_headers"]
    assert data["security_headers"]["mode"] == "standard"
    assert list(REASON_CODES) == data["reason_codes"]
