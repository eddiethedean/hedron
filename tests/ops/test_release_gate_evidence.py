"""Evidence gate integrity: Verified rows need real commands + ci_job attestation."""

from __future__ import annotations

import hashlib
import re
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_release_gate as gate  # noqa: E402


def test_validate_verified_requires_ci_job_and_existing_script() -> None:
    errors = gate._validate_verified_command(
        "DEMO",
        "python scripts/check_stable_tier_023.py",
        "test",
    )
    assert errors == []

    missing_job = gate._validate_verified_command(
        "DEMO",
        "python scripts/check_stable_tier_023.py",
        "",
    )
    assert any("ci_job" in e for e in missing_job)

    missing_script = gate._validate_verified_command(
        "DEMO",
        "python scripts/does_not_exist_023.py",
        "test",
    )
    assert any("missing path" in e for e in missing_script)


def test_suite_command_attested_by_ci_job() -> None:
    errors = gate._validate_verified_command(
        "REGRESS",
        "bash scripts/ci_checks.sh test --python 3.12",
        "test",
    )
    assert errors == []


def test_ssot_command_classification() -> None:
    assert gate._is_executable_ssot_command("python scripts/check_stable_tier_023.py")
    assert not gate._is_executable_ssot_command("python scripts/verify_pkg_23.py")
    assert not gate._is_executable_ssot_command("bash scripts/ci_checks.sh test")
    assert not gate._is_executable_ssot_command("python -m pytest -q")


def test_release_gate_0_23_manifest_passes_strict_checks() -> None:
    manifest = ROOT / "docs" / "acceptance" / "release-gate-0.23.toml"
    errors = gate.check_evidence_manifest(manifest)
    assert errors == [], errors
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    verified = [r for r in data["evidence"] if r.get("state") == "Verified"]
    assert verified
    assert all(str(r.get("ci_job", "")).strip() for r in verified)
    assert any(gate._is_executable_ssot_command(str(r["command"])) for r in verified)


def test_release_gate_0_67_plan_is_selected_and_well_formed() -> None:
    manifest = ROOT / "docs" / "acceptance" / "release-gate-0.67.toml"
    assert gate.evidence_manifest_for("0.67.0") == manifest
    assert gate.check_evidence_manifest_lenient(manifest) == []


def test_release_gate_1_2_candidate_is_selected_without_historical_fallback() -> None:
    manifest = ROOT / "docs" / "acceptance" / "release-gate-1.2.toml"
    assert gate.evidence_manifest_for("1.2.0") == manifest
    assert gate.check_evidence_manifest_lenient(manifest) == []


def test_release_gate_1_3_candidate_is_selected_and_inventory_is_fixed() -> None:
    manifest = ROOT / "docs" / "acceptance" / "release-gate-1.3.toml"
    assert gate.evidence_manifest_for("1.3.0") == manifest
    assert gate.check_evidence_manifest_lenient(manifest) == []
    errors = gate.check_evidence_manifest(manifest)
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    states = {row["id"]: row["state"] for row in data["evidence"]}
    assert states["FREEZE-130"] == "Verified"
    assert states["RELEASE-130"] == "Planned"
    assert not any("predecessor evidence must be satisfied" in error for error in errors)
    assert not any(
        "predecessor_record must confirm v1.2.0 publication" in error for error in errors
    )
    assert not any("FREEZE-130: state 'Planned'" in error for error in errors)
    assert any("RELEASE-130: state 'Planned'" in error for error in errors)
    assert any("every required phase 1.3 gate must be Verified" in error for error in errors)
    assert not any("planning contract freeze_satisfied must be true" in error for error in errors)
    assert any("release_approval.approved must be true" in error for error in errors)


def test_release_gate_1_3_rejects_inventory_and_target_drift(tmp_path: Path) -> None:
    source = (ROOT / "docs" / "acceptance" / "release-gate-1.3.toml").read_text(encoding="utf-8")
    source = source.replace('target = "v1.3.0"', 'target = "v1.3.1"')
    source = source.replace('id = "RELEASE-130"', 'id = "OTHER-130"')
    manifest = tmp_path / "release-gate-1.3.toml"
    manifest.write_text(source, encoding="utf-8")
    errors = gate.check_evidence_manifest_lenient(manifest)
    assert any("gate order mismatch" in error for error in errors)
    assert any("target must be v1.3.0" in error for error in errors)


def test_release_gate_1_3_binds_evidence_to_sha256(tmp_path: Path) -> None:
    evidence_root = tmp_path / "acceptance"
    evidence_root.mkdir()
    evidence = evidence_root / "evidence.json"
    evidence.write_text('{"result":"pass"}\n', encoding="utf-8")
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()

    assert gate._bound_record_errors(evidence_root, "evidence.json", digest, "TEST-130") == []
    evidence.write_text('{"result":"stale"}\n', encoding="utf-8")
    assert gate._bound_record_errors(evidence_root, "evidence.json", digest, "TEST-130") == [
        "TEST-130: retained evidence SHA-256 does not match"
    ]


def test_release_gate_1_3_source_commit_allows_only_evidence_followup(monkeypatch) -> None:
    source = "d" * 40
    changed = (
        "docs/acceptance/RELEASE_1_3.md\n"
        "docs/acceptance/release-gate-1.3.toml\n"
        "docs/acceptance/evidence-130/browser-linux.json\n"
    )

    def fake_run(command, **_kwargs):
        assert command == ["git", "merge-base", "--is-ancestor", source, "HEAD"]
        return SimpleNamespace(returncode=0)

    def fake_check_output(command, **_kwargs):
        if command[:3] == ["git", "diff", "--name-only"]:
            if command[3] == f"{source}..HEAD":
                return changed
            return ""
        if command[:2] == ["git", "status"]:
            return ""
        raise AssertionError(command)

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    monkeypatch.setattr(gate.subprocess, "check_output", fake_check_output)

    assert gate._phase_130_source_revision_errors(source) == []

    changed += "packages/hedron/src/hedron/app.py\n"
    assert gate._phase_130_source_revision_errors(source) == [
        "phase 1.3 source revision predates non-evidence changes: packages/hedron/src/hedron/app.py"
    ]


def test_release_gate_1_3_rejects_symlinked_evidence(tmp_path: Path) -> None:
    evidence_root = tmp_path / "acceptance"
    evidence_root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}\n", encoding="utf-8")
    (evidence_root / "evidence.json").symlink_to(outside)

    errors = gate._bound_record_errors(
        evidence_root,
        "evidence.json",
        hashlib.sha256(outside.read_bytes()).hexdigest(),
        "TEST-130",
    )

    assert errors == ["TEST-130: evidence path must not traverse symlinks"]


def test_release_gate_1_2_rejects_deferred_required_gates(tmp_path: Path) -> None:
    lines = [
        'phase = "1.2"',
        'target = "v1.2.0"',
        "support_policy_amendment_accepted = true",
        "stage_1_entry_satisfied = true",
        "release_cut_satisfied = false",
        "",
    ]
    for gate_id in gate.PHASE_120_EVIDENCE_IDS:
        lines.extend(
            [
                "[[evidence]]",
                f'id = "{gate_id}"',
                'state = "Deferred"',
                'owner = "release"',
                'rationale = "Required evidence is still pending."',
                'destination = "Complete before publication."',
                "",
            ]
        )
    manifest = tmp_path / "release-gate-1.2.toml"
    manifest.write_text("\n".join(lines), encoding="utf-8")

    errors = gate.check_evidence_manifest(manifest)
    assert any("release_cut_satisfied must be true" in error for error in errors)
    assert any("every required phase 1.2 gate must be Verified" in error for error in errors)


def test_current_patch_package_metadata_passes() -> None:
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
    # The workspace may be preparing a patch that is not on PyPI yet.
    assert gate.check_packages(str(release["development_version"])) == []


def test_github_release_requires_successful_pypi_publish() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "continue-on-error: true" not in workflow
    assert "steps.pypi.outcome == 'success'" in workflow
    assert "steps.verify_quickstart.outcome == 'success'" in workflow
    assert "--check-url https://pypi.org/simple/" in workflow
    assert 'if [ "$name" = "hedron-native" ]' in workflow


def test_release_workflow_uses_metadata_version_with_release_namespace() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert '      - "release-*"' in workflow
    assert "Resolve release version from checked-out metadata" in workflow
    assert "startsWith(github.ref, 'refs/tags/release-')" in workflow
    assert "Using legacy version tag for manual recovery" in workflow


def test_release_reuses_ci_and_keeps_live_services_out_of_publication() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "scripts/check_release_ci.sh" in workflow
    assert "actions: read" in workflow
    assert "  realconnect:" not in workflow
    assert "  realwb:" not in workflow
    assert "  publish_only_typing:" not in workflow


def test_ci_checks_package_versions_in_the_change_job() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    changes = workflow[workflow.index("  changes:") : workflow.index("  coverage:")]
    assert "scripts/check_changed_package_versions.py" in changes
    assert "  package_versions:" not in workflow


def test_built_quickstart_is_verified_before_pypi_upload() -> None:
    """Immutable uploads must not be the first exercise of the release verifier."""
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    prepublish = workflow.index("      - name: Verify built quick start before publication")
    upload = workflow.index("      - name: Publish to PyPI", prepublish)
    assert prepublish < upload
    assert '"${{ steps.version.outputs.version }}" --dist-dir dist --attempts 1' in workflow


def test_workbench_artifacts_are_verified_before_pypi_upload() -> None:
    """The release must reject stale immutable PyPI versions for all packages."""
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    prepublish = workflow.index("      - name: Verify all package wheels and immutable PyPI parity")
    upload = workflow.index("      - name: Publish to PyPI", prepublish)
    build = workflow.index("      - name: Build all workspace packages")
    assert build < prepublish
    assert prepublish < upload
    assert "scripts/check_workbench_release_artifacts.py" in workflow[prepublish:upload]
    assert "scripts/release_publish_order.py" in workflow


def test_120_release_requires_exact_approved_candidate_artifacts() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    prepublish = workflow.index("Verify exact approved 1.2.0 candidate artifacts")
    upload = workflow.index("name: Publish to PyPI", prepublish)
    release_steps = workflow[prepublish:upload]

    assert "steps.version.outputs.version == '1.2.0'" in release_steps
    assert "docs/acceptance/evidence-120/python-artifacts.json" in release_steps
    assert "--expected-artifact-count 44 --exact-set" in release_steps


def test_release_rehearsal_does_not_restore_the_retired_120_fallback_path() -> None:
    assert not (ROOT / ".github/workflows/release-artifacts-1.2.yml").exists()
    assert not (ROOT / "scripts/check_python_310_candidate.py").exists()
    workflow = (ROOT / ".github/workflows/release-artifacts-1.3.yml").read_text(encoding="utf-8")
    assert "check_python_310_candidate.py" not in workflow
    assert "uv python install 3.10" not in workflow
    assert "workflow_dispatch:" in workflow
    assert "uv publish" not in workflow

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "release-artifact-rehearsal:" not in ci
    assert "release-artifacts-1.3.yml" not in ci


def test_workbench_dependency_is_published_before_hedron_posit() -> None:
    publish_order = tomllib.loads(
        (ROOT / "release" / "publish-order.toml").read_text(encoding="utf-8")
    )["order"]
    assert publish_order.index("fastapi-workbench") < publish_order.index("hedron-posit")


def test_edron_is_published_by_main_and_retains_recovery_path() -> None:
    general = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    edron = (ROOT / ".github" / "workflows" / "edron-release.yml").read_text(encoding="utf-8")
    publish_order = tomllib.loads(
        (ROOT / "release" / "publish-order.toml").read_text(encoding="utf-8")
    )

    assert "Skipping Edron; publish it only from edron-v* tags" not in general
    assert "Skipping edron-sim; publish it only from the Edron release workflow" not in general
    assert "edron" in publish_order["order"]
    assert "edron-sim" in publish_order["order"]
    assert "edron" not in publish_order["excluded"]
    assert "edron-sim" not in publish_order["excluded"]
    assert '"edron-v*.*.*"' in edron
    assert "workflow_dispatch:" in edron
    assert "RELEASE_REF:" in edron
    assert "fetch-depth: 0" in edron[edron.index("  publish:") :]
    assert "scripts/check_release_ci.sh" in edron
    assert ".venv/bin/python scripts/check_edron_10_release.py" in edron
    assert "Recover Edron and edron-sim publication" in edron
    assert "secrets.PYPI_API_TOKEN" in edron
    assert "--check-url https://pypi.org/simple/" in edron
    assert "uv sync --no-install-project" in edron
    assert "uv run --no-sync python" in edron
    assert "Preflight published Stable dependencies from PyPI" in edron
    assert "id-token: write" in edron
    publisher = re.search(r"pypa/gh-action-pypi-publish@([^\s]+)", edron)
    assert publisher is not None
    assert re.fullmatch(r"[0-9a-f]{40}", publisher.group(1))


def test_v1_branch_has_one_stable_required_ci_context() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "branches: [main, v1.0]" in workflow
    assert "name: CI required" in workflow
    assert (
        "needs: [changes, coverage, test, dependency-bounds, quality, browser, packaging]"
        in workflow
    )


def test_local_release_gate_accepts_both_license_spelling_aliases() -> None:
    checks = (ROOT / "scripts" / "ci_checks.sh").read_text(encoding="utf-8")

    assert "! secret_available PWB_LICENSE && ! secret_available PWB_LICENCE" in checks
    assert "! secret_available CONNECT_LICENSE && ! secret_available CONNECT_LICENCE" in checks
