"""Planning-honesty checks for the Hedron 1.0 Stage 0 packet."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _toml(relative: str) -> dict[str, object]:
    return tomllib.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_phase_1_0_plan_checker_passes_without_verifying_release() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_100.py", "--check-plan"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "release gates remain Planned" in result.stdout


def test_phase_1_0_release_verification_fails_closed() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_100.py", "--gate", "ENTRY-100", "--verify"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "ENTRY-100 is Planned" in result.stderr


def test_phase_1_0_gate_is_subtractive_and_planned() -> None:
    gate = _toml("docs/acceptance/release-gate-1.0.toml")
    contract = _toml("docs/acceptance/one-zero-cut-contract.toml")
    assert gate["phase"] == "1.0"
    assert gate["target"] == "v1.0.0"
    assert gate["status"] == "Planned"
    assert gate["stage_1_entry_satisfied"] is False
    assert all(row["state"] == "Planned" for row in gate["evidence"])
    assert contract["release_boundary"]["net_new_required_runtime_capabilities"] == 0
    assert contract["release_boundary"]["compatibility_layer_in_1_0"] is False
    assert contract["changes_runtime"] is True
    assert contract["changes_versions"] is True
    assert contract["runtime_change_rule"].startswith("compatibility-preserving corrections")


def test_phase_1_0_keeps_verified_067_as_immutable_predecessor() -> None:
    predecessor = _toml("docs/acceptance/release-gate-0.67.toml")
    workspace = _toml("pyproject.toml")
    assert predecessor["status"] == "Verified"
    assert predecessor["target"] == "v0.67.0"
    assert workspace["project"]["version"] == "1.0.0"


def test_phase_1_0_packet_names_known_warning_floor_without_claiming_completeness() -> None:
    upgrade = (ROOT / "docs/acceptance/upgrade-fixtures-1.0.md").read_text(encoding="utf-8")
    contract = _toml("docs/acceptance/one-zero-cut-contract.toml")
    for spelling in (
        "app.component",
        "app.fragment",
        "app.include_feature",
        "router.component",
        "app.screen",
        "app.refreshable",
        "app.command",
        "app.form_command",
    ):
        assert spelling in upgrade
    gap = contract["migration"]["known_stage_0_gap"]
    assert "eight" in gap
    assert "before any removal" in gap


def test_phase_1_0_execution_plan_is_actionable_and_complete() -> None:
    plan = (ROOT / "docs/implementation/HEDRON_1_0.md").read_text(encoding="utf-8")
    for heading in (
        "### W0 — inventory, baseline, and entry lock",
        "### W1 — canonical surface and type boundary",
        "### W2 — warning-backed removal slices",
        "### W3 — static checking and migration tooling",
        "### W4 — interaction and lifecycle cutover",
        "### W5 — component-engine cutover",
        "### W6 — consumer and documentation migration",
        "### W7 — quality closure after removals",
        "### W8 — dual-version and fleet compatibility",
        "### W9 — artifacts, release candidate, and cut",
        "## Pull-request sequence and ownership",
        "## Verification command matrix",
        "## Definition of done",
    ):
        assert heading in plan
    for artifact in (
        "public-inventory-100.toml",
        "stable-inventory-100.toml",
        "removal-inventory-100.toml",
        "warnings-100.toml",
        "baseline-100.json",
        "support-policy-100.md",
    ):
        assert artifact in plan


def test_phase_1_0_flask_adapter_exposes_canonical_view_alias() -> None:
    from hedron_flask import HedronBlueprint, HedronFlask

    assert callable(HedronFlask.view)
    assert callable(HedronBlueprint.view)


def test_phase_1_0_django_adapter_exports_canonical_decorators() -> None:
    from hedron_django import action, page, view

    assert callable(action)
    assert callable(page)
    assert callable(view)


def test_phase_1_0_action_returns_typed_handle() -> None:
    from hedron import ActionHandle, Hedron, Outcome

    app = Hedron(title="action-handle", explorer="off", session_secret="phase-1-action-secret")

    @app.action("/act", fallback="/")
    def act() -> Outcome:
        return Outcome.success(message="ok")

    assert isinstance(act, ActionHandle)
    assert act.path == "/act"
    assert act.method == "POST"
    assert act.fallback == "/"


def test_phase_1_0_app_exposes_only_canonical_route_facade() -> None:
    from hedron import Hedron

    app = Hedron(title="canonical-surface", explorer="off", session_secret="phase-1-surface")
    assert all(
        not hasattr(app, name)
        for name in (
            "component",
            "fragment",
            "include_feature",
            "screen",
            "refreshable",
            "command",
            "form_command",
        )
    )
    assert all(callable(getattr(app, name)) for name in ("page", "view", "action", "include"))


def test_phase_1_0_refresh_outcome_targets_owned_view_without_full_reload() -> None:
    from fastapi.testclient import TestClient

    from hedron import Hedron, Outcome, Page, Text

    app = Hedron(
        title="outcome-refresh",
        security="standard",
        explorer="off",
        session_secret="phase-1-outcome-secret",
    )

    @app.view("/status")
    def status():
        return Text("ready")

    bound_status = status.bind()

    @app.action("/refresh")
    def refresh_status() -> Outcome:
        return Outcome.refresh(bound_status)

    @app.page("/")
    def home():
        return Page(bound_status(), title="Home")

    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf")
    response = client.post(
        "/refresh",
        headers={"HX-Request": "true", "X-CSRF-Token": token or ""},
    )

    assert response.status_code == 200
    assert response.headers.get("HX-Refresh") in {None, ""}
    assert response.headers.get("HX-Trigger") == (
        f'{{"hedron:refresh-{bound_status.dom_id}": {{}}}}'
    )


def test_phase_1_0_view_allows_explicit_regions_alongside_owned_host() -> None:
    from fastapi.testclient import TestClient

    from hedron import Hedron, Page, Text

    app = Hedron(
        title="view-regions",
        security="standard",
        explorer="off",
        session_secret="phase-1-view-regions-secret",
    )
    region = app.region("status")

    @app.view("/status", fragment_regions=(region,))
    def status():
        return Text("ready")

    @app.page("/")
    def home():
        return Page(status(), title="Home")

    response = TestClient(app).get(
        "/status",
        headers={"HX-Request": "true", "HX-Target": "#status"},
    )
    assert response.status_code == 200
    assert "ready" in response.text


def test_phase_1_0_refresh_outcome_rejects_unknown_target() -> None:
    from fastapi.testclient import TestClient

    from hedron import Hedron, Outcome, Page, Text

    app = Hedron(
        title="outcome-refresh-unknown",
        security="standard",
        explorer="off",
        session_secret="phase-1-unknown-secret",
    )

    @app.action("/refresh")
    def refresh_unknown() -> Outcome:
        return Outcome.refresh("not-registered")

    @app.page("/")
    def home():
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    token = client.get("/").cookies.get("hedron_csrf")
    response = client.post(
        "/refresh",
        headers={"HX-Request": "true", "X-CSRF-Token": token or ""},
    )

    assert response.status_code == 403
    assert "HED-UPDATE-0003" in response.text


def test_phase_1_0_target_check_does_not_import_application(tmp_path: Path) -> None:
    (tmp_path / "bad_app.py").write_text(
        "raise RuntimeError('target check must be non-executing')\n",
        encoding="utf-8",
    )
    (tmp_path / "source.py").write_text("app.component('/')\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[tool.hedron]\n", encoding="utf-8")
    from hedron.cli import main

    with pytest.raises(SystemExit) as result:
        main(
            [
                "--app",
                "bad_app:app",
                "check",
                "--target",
                "1.0",
                "--project",
                str(tmp_path),
                "--format",
                "json",
            ]
        )
    assert result.value.code == 0


def test_phase_1_0_inventory_generator_reads_immutable_baseline(tmp_path: Path) -> None:
    from scripts.generate_100_inventory import generate

    result = generate(baseline="v0.67.0", output_dir=tmp_path)

    assert result["baseline"] == "v0.67.0"
    assert len(str(result["commit"])) == 40
    counts = result["counts"]
    assert counts["public"]["packages"] >= 20
    assert counts["public"]["symbols"] >= 1000
    assert counts["public"]["artifacts"] >= 1000
    assert (tmp_path / "public-inventory-100.toml").is_file()
    assert (tmp_path / "stable-inventory-100.toml").is_file()
    assert (tmp_path / "task-inventory-100.toml").is_file()
    assert (tmp_path / "baseline-100.json").is_file()
    assert counts["tasks"] >= 4000
    task_text = (tmp_path / "task-inventory-100.toml").read_text(encoding="utf-8")
    assert 'task = "method:hedron.app.pages.HedronPagesMixin.page"' in task_text
    stable_text = (tmp_path / "stable-inventory-100.toml").read_text(encoding="utf-8")
    assert 'qualified = "hedron.Hedron"' in stable_text
    assert 'maturity = "stable"' in stable_text


def test_phase_1_0_inventories_have_explicit_classification() -> None:
    public = _toml("docs/acceptance/public-inventory-100.toml")
    stable = _toml("docs/acceptance/stable-inventory-100.toml")
    surfaces = public["surface"]
    artifacts = public["artifact"]
    symbols = stable["symbol"]
    assert isinstance(surfaces, list) and surfaces
    assert isinstance(artifacts, list) and artifacts
    assert isinstance(symbols, list) and symbols
    assert len(symbols) <= len(surfaces)
    assert all(row["owner"] and row["maturity"] != "unclassified" for row in surfaces)
    assert all(row["owner"] and row["disposition"] != "unclassified" for row in artifacts)
    stable_exports = {row["canonical"] for row in surfaces if row["maturity"] == "stable"}
    assert stable_exports == {row["qualified"] for row in symbols}
    assert all(row["maturity"] == "stable" and row["disposition"] == "stable" for row in symbols)


def test_phase_1_0_task_inventory_has_provenance_and_public_method_rows() -> None:
    task_inventory = _toml("docs/acceptance/task-inventory-100.toml")
    assert task_inventory["baseline"] == "v0.67.0"
    rows = task_inventory["task"]
    assert isinstance(rows, list) and len(rows) >= 4000
    assert any(
        row["kind"] == "method" and row["interface"] == "hedron.app.pages.HedronPagesMixin.page"
        for row in rows
    )
    assert all(
        row["task"]
        and row["source"]
        and row["signature"]
        and int(row["line"]) > 0
        and row["owner"]
        and row["disposition"] == "package-native"
        for row in rows
    )


def test_phase_1_0_compatibility_report_retains_baseline_bridge_probe() -> None:
    report = json.loads(
        (ROOT / "docs/acceptance/compatibility-report-100/local-bridge.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["bridge_run"]["command"].startswith("python scripts/check_upgrade_100.py")
    assert report["bridge_run"]["facts"]["http_status"] == 200


def test_phase_1_0_local_build_evidence_is_reproducible_but_not_release_claim() -> None:
    evidence = json.loads(
        (ROOT / "docs/acceptance/compatibility-report-100/local-build-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    assert evidence["reproducibility"]["verified"] is True
    assert evidence["artifact_retention"] is False
    assert evidence["release_claim"] is False
    assert len(evidence["artifacts"]) == 24


def test_phase_1_0_checker_validates_coordinated_and_satellite_metadata() -> None:
    from scripts.check_100 import _check_package_metadata

    assert _check_package_metadata() == []
