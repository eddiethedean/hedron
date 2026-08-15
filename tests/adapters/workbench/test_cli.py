"""DX-029 CLI check / dry-run (no listener)."""

from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from hedron_workbench.cli import main


def test_check_text() -> None:
    assert main(["check", "--format", "text", "--mode", "off"]) == 0


def test_check_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--format", "json", "--mount", "/s/demo/p/9"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["browser_mount"] == "/s/demo/p/9"
    assert payload["cookie_mount"] == "/s/demo/p/9"


def test_check_discover_binds_before_rserver_url(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """#137: ``check --discover`` must bind a listener and pass that port."""
    from hedron_posit import cli as posit_cli

    bound: list[int] = []
    real_bind = posit_cli.bind_loopback

    def tracking_bind(host: str, port: int):
        sock = real_bind(host, port)
        bound.append(int(sock.getsockname()[1]))
        return sock

    monkeypatch.setattr(posit_cli, "bind_loopback", tracking_bind)
    script = tmp_path / "fake-rserver-url"
    script.write_text(
        '#!/bin/sh\necho "https://wb.example/s/disc/p/$2"\n',
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("RS_SERVER_URL", "https://wb.example/s/x/")
    assert (
        main(
            [
                "check",
                "--discover",
                "--format",
                "json",
                "--rserver-url",
                str(script),
            ]
        )
        == 0
    )
    assert bound, "check --discover must bind a listener before rserver-url"
    payload = json.loads(capsys.readouterr().out)
    assert payload["browser_mount"] == f"/s/disc/p/{bound[0]}"
    assert payload["discovered"] is True


def test_dry_run_alias() -> None:
    assert main(["dry-run", "--mode", "off"]) == 0


def test_external_bind_requires_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--host", "0.0.0.0"]) == 1
    assert "HED-WB-0001" in capsys.readouterr().err
    assert main(["check", "--host", "0.0.0.0", "--allow-external-bind"]) == 0


def test_bad_worker_count_is_diagnostic(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--workers", "0"]) == 1
    assert "HED-WB-0001" in capsys.readouterr().err


def test_doctor_reports_topology_without_importing_app(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        main(
            [
                "doctor",
                "--format",
                "json",
                "--mode",
                "off",
                "--topology",
                "reverse-proxy",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["deployment"]["topology"] == "reverse-proxy"
    assert payload["checks"]["listener_host_safe"] is True
