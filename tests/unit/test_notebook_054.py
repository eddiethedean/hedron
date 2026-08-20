"""NOTEBOOK-054 evidence: display handles, static fallbacks, multi-view sessions."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from hedron_conformance.authoring_loop import HED_NOTEBOOK_TOKEN, HED_NOTEBOOK_TOPOLOGY
from hedron_notebook import (
    DISPLAY_SNAPSHOT_SCHEMA,
    DisplayHandle,
    NotebookSession,
    NotebookTokenError,
    NotebookTopologyError,
    StaleDisplayHandleError,
    preview_handle,
    start_preview,
)

ROOT = Path(__file__).resolve().parents[2]

DISPLAY_OPS = ("update", "snapshot", "open_in_browser", "close")


@dataclass
class _FakeServer:
    port: int = 8765
    started: bool = field(default=False, init=False)
    shut_down: bool = field(default=False, init=False)

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.shut_down = True


def test_notebook_054_packet_bound() -> None:
    gate = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "release-gate-0.54.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["NOTEBOOK-054"]["command"] == "python scripts/check_notebook_054.py"
    assert rows["NOTEBOOK-054"]["owner"] == "hedron-notebook"
    locks = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "authoring-sim-notebook-054.toml").read_text(
            encoding="utf-8"
        )
    )
    assert sorted(locks["notebook"]["display_ops"]) == sorted(DISPLAY_OPS)
    assert locks["notebook"]["multi_view"] is True
    assert locks["notebook"]["public_hosting"] is False


def test_failure_codes_match_shared_schema() -> None:
    assert NotebookTopologyError.code == HED_NOTEBOOK_TOPOLOGY
    assert NotebookTokenError.code == HED_NOTEBOOK_TOKEN


def test_display_handle_supports_every_declared_operation() -> None:
    handle = DisplayHandle(handle_id="view-1", title="Run report")
    for op in DISPLAY_OPS:
        assert callable(getattr(handle, op)), op
    assert callable(handle.dispose)


def test_display_handle_update_snapshot_and_close() -> None:
    handle = DisplayHandle(handle_id="report", title="Run report")
    assert handle.revision == 0
    handle.update("<p>Queued</p>")
    handle.update("<p>Running</p>")
    assert handle.revision == 2
    assert handle.closed is False

    snapshot = handle.snapshot()
    assert snapshot["schema_version"] == DISPLAY_SNAPSHOT_SCHEMA
    assert snapshot["handle_id"] == "report"
    assert snapshot["title"] == "Run report"
    assert snapshot["revision"] == 2
    assert snapshot["closed"] is False
    assert snapshot["url"] is None
    assert "Running" in snapshot["html"]
    assert snapshot["text"] == "Running"
    assert "Run report" in snapshot["image"]
    assert json.loads(json.dumps(snapshot)) == snapshot

    handle.close()
    assert handle.closed is True
    assert handle.snapshot()["closed"] is True
    with pytest.raises(StaleDisplayHandleError):
        handle.update("<p>Done</p>")


def test_static_fallbacks_render_html_text_and_image_placeholder() -> None:
    handle = DisplayHandle(handle_id="fallbacks", title="Job log")
    handle.update("<div><p>Step 1 &amp; 2</p>\n  <p>Step 3</p></div>")
    assert handle.as_html().startswith("<div>")
    assert handle.as_text() == "Step 1 & 2 Step 3"
    assert handle.as_image_placeholder() == "[hedron notebook view: Job log (live, revision 1)]"
    handle.close()
    assert "closed" in handle.as_image_placeholder()


def test_non_string_content_is_escaped_and_rich_repr_is_reused() -> None:
    class _Rich:
        def _repr_html_(self) -> str:
            return "<b>rich</b>"

    escaped = DisplayHandle(handle_id="escape")
    escaped.update("<script>alert(1)</script>")
    assert "<script>" in escaped.as_html()  # explicit HTML stays verbatim

    unsafe = DisplayHandle(handle_id="unsafe")
    unsafe.update(["<script>alert(1)</script>"])
    assert "&lt;script&gt;" in unsafe.as_html()
    assert "<script>" not in unsafe.as_html()

    rich = DisplayHandle(handle_id="rich")
    rich.update(_Rich())
    assert rich.as_html() == "<b>rich</b>"


def test_notebook_session_holds_multiple_views() -> None:
    session = NotebookSession("authoring-loop")
    catalog = session.display("<p>catalog</p>", handle_id="catalog", title="Catalog")
    workflow = session.display("<p>workflow</p>", handle_id="workflow", title="Workflow")

    assert session.handles == (catalog, workflow)
    assert session.get("workflow") is workflow
    with pytest.raises(KeyError):
        session.get("missing")
    with pytest.raises(ValueError, match="already holds"):
        session.display("<p>dup</p>", handle_id="catalog")

    snapshot = session.snapshot()
    assert snapshot["session_id"] == "authoring-loop"
    assert [row["handle_id"] for row in snapshot["handles"]] == ["catalog", "workflow"]
    assert json.loads(json.dumps(snapshot)) == snapshot


def test_notebook_session_is_bounded() -> None:
    session = NotebookSession("bounded", max_handles=2)
    session.display(handle_id="a")
    session.display(handle_id="b")
    with pytest.raises(ValueError, match="maximum of 2 handles"):
        session.display(handle_id="c")
    with pytest.raises(ValueError, match="max_handles"):
        NotebookSession("invalid", max_handles=0)


def test_preview_handle_wraps_a_running_preview() -> None:
    server = _FakeServer(port=9101)
    preview = start_preview(object(), server=server, token="handle-token-1")
    session = NotebookSession("preview-session")
    session.add_cleanup(preview.shutdown)
    handle = session.add(preview_handle(preview))

    assert handle.handle_id == "preview"
    assert handle.url is not None
    assert "<iframe" in handle.as_html()
    session.close()
    assert handle.closed is True
    assert server.shut_down is True
