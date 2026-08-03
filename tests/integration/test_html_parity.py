"""Offline vs FastAPI HTML parity for phase 0.2."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, Page, Stack, Text, render
from hedron_core import RenderMode, reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def _core_body(html: str) -> str:
    """Normalize to comparable body content without HTMX injection noise."""
    text = html
    if "<body>" in text and "</body>" in text:
        text = text.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    # Drop injected HTMX script if present.
    text = text.replace('<script src="/hedron-static/htmx.min.js" defer></script>', "")
    start = text.find('<meta name="htmx-config" ')
    if start >= 0:
        end = text.find(">", start)
        text = text[:start] + text[end + 1 :]
    return "".join(text.split())


def test_same_core_html_offline_and_via_fastapi() -> None:
    tree = Page(Stack(Text("parity-check"), Text("second")), title="Parity")
    offline = render(tree, mode=RenderMode.PAGE).html

    app = Hedron(
        title="parity",
        security="standard",
        explorer="off",
        session_secret="test-secret",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Stack(Text("parity-check"), Text("second")), title="Parity")

    client = TestClient(app)
    online = client.get("/").text
    assert _core_body(offline) == _core_body(online)
    assert "parity-check" in online
    assert "second" in online
