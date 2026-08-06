"""Phase 0.17 notebook preview helper (NOTEBOOK-017)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from hedron_notebook import NotebookPreview, __version__, start_preview


@dataclass
class _FakeServer:
    port: int = 8765
    started: bool = field(default=False, init=False)
    shut_down: bool = field(default=False, init=False)

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.shut_down = True


def test_package_version_and_exports() -> None:
    assert __version__ == "0.1.0"
    assert callable(start_preview)
    assert NotebookPreview is not None


def test_localhost_preview_token_and_url() -> None:
    server = _FakeServer(port=9123)
    preview = start_preview(
        object(),
        host="127.0.0.1",
        server=server,
        token="test-token-abc",
        root_path="/proxy",
    )
    try:
        assert server.started
        assert preview.hosted_warning is False
        assert preview.port == 9123
        assert preview.token == "test-token-abc"
        assert "hedron_preview_token=test-token-abc" in preview.url
        assert preview.url.startswith("http://127.0.0.1:9123/proxy/?")
        assert preview.external_url() == preview.url
        html = preview.iframe_html(width="80%", height="400")
        assert 'src="http://127.0.0.1:9123/proxy/?hedron_preview_token=test-token-abc"' in html
        assert 'width="80%"' in html
        assert 'height="400"' in html
        assert "sandbox=" in html
    finally:
        preview.shutdown()
    assert server.shut_down


def test_random_token_when_not_provided() -> None:
    server = _FakeServer()
    preview = start_preview(object(), server=server)
    try:
        assert len(preview.token) >= 16
        assert preview.token in preview.url
        assert preview.hosted_warning is False
    finally:
        preview.shutdown()


def test_hosted_warning_for_non_loopback() -> None:
    server = _FakeServer()
    with pytest.warns(UserWarning, match="non-loopback"):
        preview = start_preview(object(), host="0.0.0.0", server=server)
    try:
        assert preview.hosted_warning is True
    finally:
        preview.shutdown()


def test_shutdown_is_idempotent() -> None:
    server = _FakeServer()
    preview = start_preview(object(), server=server)
    preview.shutdown()
    preview.shutdown()
    assert server.shut_down
