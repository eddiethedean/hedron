"""TOPOLOGY-054 evidence: non-loopback rejection and printed handoff disposition."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from hedron_conformance.authoring_loop import HED_NOTEBOOK_TOPOLOGY
from hedron_notebook import (
    LOOPBACK_HOSTS,
    DisplayHandle,
    NotebookTokenError,
    NotebookTopologyError,
    handoff_disposition,
    is_loopback_host,
    require_loopback_host,
    start_preview,
    start_server_handoff,
)

ROOT = Path(__file__).resolve().parents[2]

NON_LOOPBACK_HOSTS = ("0.0.0.0", "192.168.1.10", "10.0.0.5", "example.com", "::")


@dataclass
class _FakeServer:
    port: int = 8765
    started: bool = field(default=False, init=False)
    shut_down: bool = field(default=False, init=False)

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.shut_down = True


def test_topology_054_packet_bound() -> None:
    gate = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "release-gate-0.54.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["TOPOLOGY-054"]["command"] == "python scripts/check_topology_054.py"
    locks = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "authoring-sim-notebook-054.toml").read_text(
            encoding="utf-8"
        )
    )
    assert locks["topology"]["print_disposition"] is True
    assert locks["topology"]["silent_public_promotion"] is False
    assert locks["notebook"]["handoff_to_real_server"] == "opt_in_explicit_disposition"


def test_loopback_classification() -> None:
    for host in LOOPBACK_HOSTS:
        assert is_loopback_host(host) is True
    assert is_loopback_host("127.0.0.2") is True
    assert is_loopback_host("[::1]") is True
    for host in NON_LOOPBACK_HOSTS:
        assert is_loopback_host(host) is False


def test_non_loopback_preview_is_rejected_with_the_topology_code() -> None:
    for host in NON_LOOPBACK_HOSTS:
        with pytest.raises(NotebookTopologyError) as excinfo:
            start_preview(object(), host=host, server=_FakeServer())
        assert excinfo.value.code == HED_NOTEBOOK_TOPOLOGY
        assert excinfo.value.host == host
        assert "refuses non-loopback" in str(excinfo.value)


def test_require_loopback_host_returns_supported_hosts() -> None:
    assert require_loopback_host("127.0.0.1") == "127.0.0.1"
    assert require_loopback_host("localhost", surface="handoff") == "localhost"
    with pytest.raises(NotebookTopologyError, match="handoff refuses non-loopback"):
        require_loopback_host("0.0.0.0", surface="handoff")


def test_handoff_disposition_states_the_full_topology() -> None:
    text = handoff_disposition(host="127.0.0.1", port=8000, app_label="ReportsApp")
    assert "127.0.0.1:8000" in text
    assert "interface: loopback" in text
    assert "token gate: required" in text
    assert "public hosting: refused by default" in text
    assert "promotion: never automatic" in text
    assert HED_NOTEBOOK_TOPOLOGY in text
    assert "ReportsApp" in text


def test_start_server_handoff_prints_disposition_and_binds_nothing() -> None:
    printed: list[str] = []
    disposition = start_server_handoff(object(), port=8001, printer=printed.append)
    assert printed == [disposition]
    assert "0.0.0.0" not in disposition
    assert "interface: loopback" in disposition


def test_start_server_handoff_refuses_public_and_untokenized_topologies() -> None:
    with pytest.raises(NotebookTopologyError) as public:
        start_server_handoff(object(), allow_public=True, printer=lambda _: None)
    assert public.value.code == HED_NOTEBOOK_TOPOLOGY

    with pytest.raises(NotebookTokenError):
        start_server_handoff(object(), token_gated=False, printer=lambda _: None)

    with pytest.raises(NotebookTopologyError):
        start_server_handoff(object(), host="0.0.0.0", printer=lambda _: None)


def test_browser_open_refuses_non_loopback_urls() -> None:
    opened: list[str] = []
    local = DisplayHandle(handle_id="local", url="http://127.0.0.1:9000/?x=1")
    assert local.open_in_browser(opener=opened.append) == "http://127.0.0.1:9000/?x=1"
    assert opened == ["http://127.0.0.1:9000/?x=1"]

    remote = DisplayHandle(handle_id="remote", url="http://example.com/preview")
    with pytest.raises(NotebookTopologyError) as excinfo:
        remote.open_in_browser(opener=opened.append)
    assert excinfo.value.code == HED_NOTEBOOK_TOPOLOGY
    assert opened == ["http://127.0.0.1:9000/?x=1"]

    static = DisplayHandle(handle_id="static")
    with pytest.raises(ValueError, match="no URL to open"):
        static.open_in_browser(opener=opened.append)
