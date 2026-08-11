"""Evidence gate integrity: Verified rows need real commands + ci_job attestation."""

from __future__ import annotations

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


def test_current_patch_package_metadata_passes() -> None:
    assert gate.check_packages("0.28.1") == []


def test_github_release_requires_successful_pypi_publish() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "steps.pypi.outcome == 'success'" in workflow
    assert "steps.pypi.outputs.publish_failed != '1'" in workflow
    assert "steps.pypi.outcome == 'failure' || steps.pypi.outputs.publish_failed == '1'" in workflow
