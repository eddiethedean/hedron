"""FLEET-053 evidence."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest

from hedron.cli import main
from hedron.fleet import (
    diagnose_installed_fleet,
    looks_like_secret_env,
    redact_env_mapping,
)


def test_fleet_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["FLEET-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_diagnose_installed_fleet_is_read_only_not_package_doctor() -> None:
    report = diagnose_installed_fleet()
    assert report["read_only"] is True
    assert report["package_doctor"] is False
    assert report["automatic_install"] is False
    assert report["environment"] is None  # never dump env by default
    dists = report["distributions"]
    assert dists["hedron"] is not None
    assert isinstance(report["selected_extras"], list)
    assert isinstance(report["plugins"], list)
    assert isinstance(report["assets"], list)
    assert isinstance(report["recommendations"], list)
    for rec in report["recommendations"]:
        assert "evidence" in rec and rec["evidence"]
        assert "message" in rec and rec["message"]
        lower = rec["message"].lower()
        if "auto-install" in lower:
            assert "no auto-install" in lower


def test_redact_env_mapping_redacts_secret_keys() -> None:
    assert looks_like_secret_env("HEDRON_API_KEY")
    assert looks_like_secret_env("SESSION_SECRET")
    assert not looks_like_secret_env("HEDRON_HOME")
    redacted = redact_env_mapping(
        {
            "HEDRON_HOME": "/tmp/hedron",
            "API_TOKEN": "super-secret",
            "DATABASE_PASSWORD": "pw",
            "PATH": "/usr/bin",
        }
    )
    assert redacted["HEDRON_HOME"] == "/tmp/hedron"
    assert redacted["PATH"] == "/usr/bin"
    assert redacted["API_TOKEN"] == "[redacted]"
    assert redacted["DATABASE_PASSWORD"] == "[redacted]"


def test_diagnose_never_calls_installer() -> None:
    """Fleet doctor must remain read-only — no pip/uv install side effects."""

    def _blocked_run(*_a, **_k):  # type: ignore[no-untyped-def]
        raise AssertionError("subprocess must not run during fleet diagnosis")

    with (
        patch("subprocess.run", side_effect=_blocked_run),
        patch("subprocess.call", side_effect=_blocked_run),
        patch("subprocess.Popen", side_effect=_blocked_run),
        patch("os.system", side_effect=_blocked_run),
    ):
        report = diagnose_installed_fleet()
    blob = json.dumps(report, default=str).lower()
    assert "pip install" not in blob
    assert "uv add" not in blob
    assert report["automatic_install"] is False


def test_plugins_snapshot_failure_still_returns_report(caplog: pytest.LogCaptureFixture) -> None:
    """Best-effort plugin collection must not fail the diagnosis (logs + continues)."""
    import logging

    with (
        patch(
            "hedron_core.plugins.get_explorer_panels",
            side_effect=RuntimeError("boom"),
        ),
        caplog.at_level(logging.DEBUG, logger="hedron.fleet"),
    ):
        report = diagnose_installed_fleet()
    assert isinstance(report["plugins"], list)
    assert report["read_only"] is True
    assert any("plugin registry snapshot failed" in r.message for r in caplog.records)


def test_hedron_fleet_cli_json(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exited:
        main(["fleet", "--format", "json"])
    assert exited.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["read_only"] is True
    assert payload["package_doctor"] is False
    assert payload["environment"] is None
