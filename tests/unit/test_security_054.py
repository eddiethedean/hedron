"""SECURITY-054 evidence: token/path redaction, escaping, and iframe policy."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from hedron_conformance.authoring_loop import HED_NOTEBOOK_TOKEN
from hedron_notebook import (
    PREVIEW_TOKEN_HEADER,
    PREVIEW_TOKEN_QUERY,
    REDACTED,
    DisplayHandle,
    NotebookSession,
    NotebookTokenError,
    PreviewTokenGate,
    preview_handle,
    redact_text,
    start_preview,
    wrap_preview_app,
)

ROOT = Path(__file__).resolve().parents[2]

SECRET = "s3cret-preview-token-value"


@dataclass
class _FakeServer:
    port: int = 8765
    started: bool = field(default=False, init=False)
    shut_down: bool = field(default=False, init=False)

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.shut_down = True


def test_security_054_packet_bound() -> None:
    gate = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "release-gate-0.54.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SECURITY-054"]["command"] == "python scripts/check_security_054.py"
    locks = tomllib.loads(
        (ROOT / "docs" / "acceptance" / "authoring-sim-notebook-054.toml").read_text(
            encoding="utf-8"
        )
    )
    security = locks["security"]
    assert security["redact_tokens_and_paths"] is True
    assert security["output_escaping"] is True
    assert security["iframe_policy"] is True
    assert security["non_loopback_default"] == "rejected"


def test_redact_text_removes_tokens_and_local_paths() -> None:
    text = (
        f"http://127.0.0.1:9000/?{PREVIEW_TOKEN_QUERY}={SECRET} "
        f"{PREVIEW_TOKEN_HEADER}: {SECRET} "
        "loaded from /Users/author/notebooks/report.ipynb and C:\\Users\\author\\app.py"
    )
    redacted = redact_text(text)
    assert SECRET not in redacted
    assert "/Users/author" not in redacted
    assert "C:\\Users" not in redacted
    assert redacted.count(REDACTED) == 4


def test_handle_snapshot_redacts_token_from_url_and_html() -> None:
    handle = DisplayHandle(
        handle_id="preview",
        title="Preview",
        url=f"http://127.0.0.1:9000/?{PREVIEW_TOKEN_QUERY}={SECRET}",
    )
    handle.update(f'<iframe src="http://127.0.0.1:9000/?{PREVIEW_TOKEN_QUERY}={SECRET}"></iframe>')

    snapshot = handle.snapshot()
    serialized = json.dumps(snapshot)
    assert SECRET not in serialized
    assert REDACTED in snapshot["url"]
    assert REDACTED in snapshot["html"]
    # The live handle still knows the real URL so open_in_browser keeps working.
    assert handle.url is not None
    assert SECRET in handle.url


def test_session_snapshot_of_a_real_preview_leaks_no_token() -> None:
    server = _FakeServer(port=9333)
    preview = start_preview(object(), server=server, token=SECRET)
    session = NotebookSession("secure")
    session.add_cleanup(preview.shutdown)
    session.add(preview_handle(preview))
    try:
        serialized = json.dumps(session.snapshot())
        assert SECRET not in serialized
        assert REDACTED in serialized
    finally:
        session.close()
    assert server.shut_down is True


def test_saved_output_escapes_untrusted_content() -> None:
    handle = DisplayHandle(handle_id="escaped")
    handle.update({"label": "<img src=x onerror=alert(1)>"})
    html = handle.as_html()
    assert "<img" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert handle.as_text() == "{'label': '<img src=x onerror=alert(1)>'}"


def test_iframe_policy_keeps_sandbox_and_title() -> None:
    server = _FakeServer(port=9444)
    preview = start_preview(object(), server=server, token=SECRET)
    try:
        html = preview.iframe_html()
        assert 'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"' in html
        assert 'title="Hedron notebook preview"' in html
        handle = preview_handle(preview)
        assert "sandbox=" in handle.as_html()
        assert SECRET not in handle.as_html()
    finally:
        preview.shutdown()


def test_empty_token_is_a_typed_token_failure() -> None:
    with pytest.raises(NotebookTokenError) as excinfo:
        start_preview(object(), server=_FakeServer(), token="")
    assert excinfo.value.code == HED_NOTEBOOK_TOKEN
    assert "non-empty" in str(excinfo.value)

    with pytest.raises(NotebookTokenError) as gate_error:
        wrap_preview_app(object(), "")
    assert gate_error.value.code == HED_NOTEBOOK_TOKEN
    assert isinstance(PreviewTokenGate(object(), SECRET), PreviewTokenGate)
