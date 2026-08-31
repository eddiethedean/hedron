"""Cross-CLI parity for the shared Workbench command services."""

from __future__ import annotations

import json

import pytest

from fastapi_workbench import cli as workbench_cli
from fastapi_workbench.cli_support import (
    cookie_path_matches_mount,
    report_checks_ok,
    resolve_check,
)
from hedron_posit import cli as posit_cli


def test_check_commands_share_common_resolution_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    for key in (
        "RS_SERVER_URL",
        "FASTAPI_WORKBENCH",
        "FASTAPI_WORKBENCH_MODE",
        "HEDRON_POSIT_PRODUCT",
        "POSIT_PRODUCT",
        "RSTUDIO_PRODUCT",
    ):
        monkeypatch.delenv(key, raising=False)

    assert workbench_cli.main(["check", "--mode", "off", "--format", "json"]) == 0
    generic = json.loads(capsys.readouterr().out)
    assert posit_cli.main(["check", "--mode", "off", "--format", "json"]) == 0
    posit = json.loads(capsys.readouterr().out)

    for key in (
        "mode",
        "bind",
        "external_origin",
        "browser_mount",
        "cookie_mount",
        "source",
        "discovered",
        "workers",
    ):
        assert posit[key] == generic[key]
    assert posit["posit_status"]["product"] == "inactive"


def test_both_cli_compatibility_aliases_use_shared_cookie_parser() -> None:
    header = 'session=x; Path="/s/a/p/1/"; HttpOnly'
    assert workbench_cli._cookie_path_matches_mount is cookie_path_matches_mount  # pyright: ignore[reportPrivateUsage]
    assert posit_cli._cookie_path_matches_mount is cookie_path_matches_mount  # pyright: ignore[reportPrivateUsage]
    assert cookie_path_matches_mount(header, "/s/a/p/1") is True
    assert cookie_path_matches_mount("session=x; HttpOnly", "/s/a/p/1") is False


def test_shared_resolver_binds_before_discovery_and_closes_socket() -> None:
    events: list[object] = []

    class Socket:
        def getsockname(self) -> tuple[str, int]:
            events.append("getsockname")
            return ("127.0.0.1", 43210)

        def close(self) -> None:
            events.append("close")

    result = resolve_check(
        host="127.0.0.1",
        port=0,
        discover=True,
        discovery_available=True,
        explicit_mount=lambda _port: False,
        bind=lambda host, port: events.append(("bind", host, port)) or Socket(),
        discover_url=lambda port: events.append(("discover", port)) or "/s/a/p/1",
        resolve=lambda port, raw: events.append(("resolve", port, raw)) or "resolved",
    )

    assert result.value == "resolved"
    assert events == [
        ("bind", "127.0.0.1", 0),
        "getsockname",
        ("discover", 43210),
        ("resolve", 43210, "/s/a/p/1"),
        "close",
    ]


def test_shared_exit_evaluation_rejects_any_nested_false() -> None:
    assert report_checks_ok({"checks": {"safe": True, "probe": {"reachable": True}}})
    assert not report_checks_ok(
        {"checks": {"safe": True, "probe": {"new_future_invariant": False}}}
    )
