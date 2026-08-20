"""DOCTOR-054 evidence: `hedron package doctor` for external package authors."""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest

from hedron.cli import main
from hedron.fleet import diagnose_installed_fleet
from hedron.package_doctor import HED_PACKAGE_DOCTOR, diagnose_package
from hedron_conformance.authoring_loop import (
    AUTHORING_LOOP_SCHEMA_VERSION,
    AuthoringLoopFixture,
    validate_fixture_schema,
)

SAMPLE_KIT = Path("packages/hedron-sample-kit")


def _write_package(root: Path, pyproject: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    return root


def test_doctor_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DOCTOR-054"]["owner"] == "hedron"
    assert Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md").is_file()


def test_sample_kit_passes_the_package_doctor() -> None:
    report = diagnose_package(SAMPLE_KIT)
    assert report["package_doctor"] is True
    assert report["read_only"] is True
    assert report["automatic_install"] is False
    assert report["ok"] is True, report["diagnostics"]
    assert report["package"]["name"] == "hedron-sample-kit"
    assert report["schema_version"] == AUTHORING_LOOP_SCHEMA_VERSION
    checks = report["checks"]
    assert set(checks) == {
        "assets",
        "docs_links",
        "entry_points",
        "feature_descriptors",
        "metadata",
        "publishable",
        "schema_fingerprints",
        "version_ranges",
    }
    assert all(check["ok"] for check in checks.values())
    plugins = checks["entry_points"]["hedron_plugins"]
    assert [row["name"] for row in plugins] == ["sample_kit"]
    assert checks["schema_fingerprints"]["consumers"]
    assert checks["feature_descriptors"]["present"] is True
    assert checks["assets"]["count"] > 0


def test_doctor_report_survives_the_shared_fixture_boundary() -> None:
    report = diagnose_package(SAMPLE_KIT)
    envelope = {
        "schema_version": AUTHORING_LOOP_SCHEMA_VERSION,
        "fixture_id": "hedron-package-doctor:sample-kit",
        "kind": "authoring_loop_fixture",
        "payload": report,
        "diagnostics": report["diagnostics"],
    }
    assert validate_fixture_schema(envelope) == []
    fixture = AuthoringLoopFixture.from_dict(envelope)
    assert fixture.payload["package_doctor"] is True


def test_missing_metadata_fails_with_package_doctor_codes(tmp_path: Path) -> None:
    root = _write_package(
        tmp_path / "broken",
        '[project]\nversion = "0.1.0"\ndependencies = ["requests"]\n',
    )
    report = diagnose_package(root)
    assert report["ok"] is False
    errors = [row for row in report["diagnostics"] if row["severity"] == "error"]
    assert errors
    for row in report["diagnostics"]:
        assert row["code"] == HED_PACKAGE_DOCTOR
        assert row["boundary"] == "package_doctor"
        assert row["details"]["check"]
    assert any("name" in row["message"] for row in errors)
    unbounded = [
        row
        for row in report["diagnostics"]
        if row["details"]["check"] == "version_ranges" and row["severity"] == "warning"
    ]
    assert any("upper bound" in row["message"] for row in unbounded)


def test_missing_pyproject_is_reported_not_raised(tmp_path: Path) -> None:
    report = diagnose_package(tmp_path)
    assert report["package_doctor"] is True
    assert report["ok"] is False
    assert report["diagnostics"][0]["code"] == HED_PACKAGE_DOCTOR


def test_doctor_never_imports_or_installs(tmp_path: Path) -> None:
    root = _write_package(
        tmp_path / "explosive",
        '[project]\nname = "explosive"\nversion = "0.1.0"\n',
    )
    package = root / "src" / "explosive"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        'raise RuntimeError("package doctor must not import the target")\n',
        encoding="utf-8",
    )

    def _blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("package doctor must not shell out")

    with (
        patch("subprocess.run", side_effect=_blocked),
        patch("subprocess.call", side_effect=_blocked),
        patch("subprocess.Popen", side_effect=_blocked),
    ):
        report = diagnose_package(root)
    assert "explosive" not in sys.modules
    blob = json.dumps(report).lower()
    assert "pip install" not in blob
    assert "uv add" not in blob


def test_fleet_is_not_the_package_doctor() -> None:
    assert diagnose_installed_fleet()["package_doctor"] is False


def test_hedron_package_doctor_cli(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exited:
        main(["package", "doctor", str(SAMPLE_KIT), "--format", "json"])
    assert exited.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["package_doctor"] is True
    assert payload["ok"] is True


def test_hedron_package_doctor_cli_fails_on_broken_package(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _write_package(tmp_path / "empty", "[project]\n")
    with pytest.raises(SystemExit) as exited:
        main(["package", "doctor", str(root), "--format", "human"])
    assert exited.value.code == 1
    out = capsys.readouterr().out
    assert "package_doctor=True ok=False" in out
    assert HED_PACKAGE_DOCTOR in out
