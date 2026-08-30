"""Evidence gate integrity: Verified rows need real commands + ci_job attestation."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

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


def test_current_patch_package_metadata_passes() -> None:
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
    # The workspace may be preparing a patch that is not on PyPI yet.
    assert gate.check_packages(str(release["development_version"])) == []


def test_github_release_requires_successful_pypi_publish() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "steps.pypi.outcome == 'success'" in workflow
    assert "steps.pypi.outputs.publish_failed != '1'" in workflow
    assert "steps.pypi.outcome == 'failure' || steps.pypi.outputs.publish_failed == '1'" in workflow


def test_built_quickstart_is_verified_before_pypi_upload() -> None:
    """Immutable uploads must not be the first exercise of the release verifier."""
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    prepublish = workflow.index("      - name: Verify built quick start before publication")
    upload = workflow.index("      - name: Publish to PyPI", prepublish)
    assert prepublish < upload
    assert '"${{ steps.ref.outputs.version }}" --dist-dir dist --attempts 1' in workflow


def test_edron_has_an_independent_release_path() -> None:
    general = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    edron = (ROOT / ".github" / "workflows" / "edron-release.yml").read_text(encoding="utf-8")

    assert general.count('echo "Skipping Edron; publish it only from edron-v* tags"') == 2
    assert '"edron-v*.*.*"' in edron
    assert "workflow_dispatch:" in edron
    assert "RELEASE_REF:" in edron
    assert "needs: [test, dependency_bounds, browser]" in edron
    assert ".venv/bin/python scripts/check_edron_10_release.py" in edron
    assert "Preflight published Stable dependencies from PyPI" in edron
    assert "tests/unit/test_edron_runtime.py" in edron
    assert "tests/unit/test_edron_phase02.py" in edron
    assert "id-token: write" in edron
    publisher = re.search(r"pypa/gh-action-pypi-publish@([^\s]+)", edron)
    assert publisher is not None
    assert re.fullmatch(r"[0-9a-f]{40}", publisher.group(1))


def test_v1_branch_has_one_stable_required_ci_context() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "branches: [main, v1.0]" in workflow
    assert "name: CI required" in workflow
    assert "needs:\n      [changes, test, dependency-bounds" in workflow
