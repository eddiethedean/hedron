"""LIFECYCLE-054 evidence: repeated execution, stale handles, deterministic cleanup."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from hedron_notebook import (
    DisplayHandle,
    NotebookSession,
    StaleDisplayHandleError,
    preview_handle,
    start_preview,
)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class _FakeServer:
    port: int = 8765
    started: bool = field(default=False, init=False)
    shutdowns: int = field(default=0, init=False)

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.shutdowns += 1


def test_lifecycle_054_packet_bound() -> None:
    gate = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "release-gate-0.54.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["LIFECYCLE-054"]["command"] == "python scripts/check_lifecycle_054.py"
    assert rows["LIFECYCLE-054"]["owner"] == "hedron-notebook"


def test_repeated_cell_execution_updates_one_view_in_place() -> None:
    handle = DisplayHandle(handle_id="cell", title="Cell output")
    for step in range(5):
        handle.update(f"<p>step {step}</p>")
    assert handle.revision == 5
    assert handle.as_text() == "step 4"
    assert handle.closed is False


def test_close_is_idempotent_and_runs_the_hook_once() -> None:
    calls: list[str] = []
    handle = DisplayHandle(handle_id="hooked", _on_close=lambda: calls.append("closed"))
    handle.close()
    handle.close()
    handle.dispose()
    assert calls == ["closed"]


def test_stale_handle_refuses_update_and_open() -> None:
    handle = DisplayHandle(handle_id="stale", url="http://127.0.0.1:9000/")
    handle.close()
    with pytest.raises(StaleDisplayHandleError, match="closed"):
        handle.update("<p>late</p>")
    with pytest.raises(StaleDisplayHandleError, match="closed"):
        handle.open_in_browser(opener=lambda url: None)


def test_handle_context_manager_closes_on_exit() -> None:
    with DisplayHandle(handle_id="scoped") as handle:
        handle.update("<p>inside</p>")
        assert handle.closed is False
    assert handle.closed is True


def test_session_close_is_deterministic_lifo_and_idempotent() -> None:
    order: list[str] = []
    session = NotebookSession("cleanup")
    for name in ("first", "second", "third"):
        session.display(
            f"<p>{name}</p>",
            handle_id=name,
            on_close=lambda name=name: order.append(name),
        )

    session.add_cleanup(lambda: order.append("cleanup-a"))
    session.add_cleanup(lambda: order.append("cleanup-b"))
    session.close()
    session.close()

    assert session.closed_order == ("third", "second", "first")
    assert order == ["third", "second", "first", "cleanup-b", "cleanup-a"]
    assert all(handle.closed for handle in session.handles)


def test_closed_session_refuses_new_views() -> None:
    session = NotebookSession("closed")
    session.close()
    with pytest.raises(StaleDisplayHandleError, match="closed"):
        session.display("<p>late</p>")
    with pytest.raises(StaleDisplayHandleError, match="closed"):
        session.add(DisplayHandle(handle_id="late"))


def test_session_context_manager_shuts_down_preview_once() -> None:
    server = _FakeServer(port=9222)
    preview = start_preview(object(), server=server, token="lifecycle-token")
    with NotebookSession("with-preview") as session:
        session.add_cleanup(preview.shutdown)
        session.add(preview_handle(preview))
        assert server.started is True
    assert server.shutdowns == 1
    # NotebookPreview.shutdown stays idempotent for interrupted cells.
    preview.shutdown()
    assert server.shutdowns == 1


def test_restarted_session_reuses_handle_ids_without_leaking_state() -> None:
    first = NotebookSession("kernel")
    first.display("<p>before restart</p>", handle_id="main")
    first.close()

    second = NotebookSession("kernel")
    handle = second.display("<p>after restart</p>", handle_id="main")
    assert handle.revision == 1
    assert handle.as_text() == "after restart"
    assert handle.closed is False
