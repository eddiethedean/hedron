"""REVIEW-026 adversarial trust-boundary suite."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from hedron import Form, Hedron, Hx, Page, Text, TextInput
from hedron_core.rendering import RenderMode, render


def test_renderer_escapes_untrusted_text() -> None:
    tree = Text("<script>alert(1)</script>")
    html = render(tree, mode=RenderMode.FRAGMENT).html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_default_hedron_all_excludes_live_transports() -> None:
    import hedron

    banned = {
        "job_status_sse_response",
        "SseResponse",
        "WebSocketChannel",
        "StreamingResponse",
        "EventSourceResponse",
    }
    assert banned.isdisjoint(set(hedron.__all__))


def test_experimental_namespace_exists_separately() -> None:
    import hedron.experimental as experimental

    assert hasattr(experimental, "__all__") or hasattr(experimental, "job_status_sse_response")


def test_csrf_required_on_standard_mutating_form() -> None:
    app = Hedron(
        title="rev026",
        security="standard",
        explorer="off",
        session_secret="test-secret-rev026",
    )

    @app.page("/")
    def home() -> Page:
        return Page(
            Form(
                TextInput(name="title"),
                hx=Hx(post="/save"),
            ),
            title="Home",
        )

    @app.action("/save")
    def save() -> Text:
        return Text("ok")

    client = TestClient(app)
    # Missing CSRF should not succeed as a clean 200 HTML success for standard profile.
    response = client.post("/save", data={"title": "x"})
    assert response.status_code in {400, 403, 422, 401}


def test_production_explorer_development_forced_off(monkeypatch: pytest.MonkeyPatch) -> None:
    import warnings

    from hedron_core.production_gate import RISK_ACCEPTANCE_ENV

    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="explorer-development"):
        Hedron(
            title="rev026",
            security="standard",
            explorer="development",
            session_secret="test-secret-rev026-prod-ok-32chars!",
            production=True,
        )
    monkeypatch.setenv(RISK_ACCEPTANCE_ENV, "explorer-development")
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        app = Hedron(
            title="rev026",
            security="standard",
            explorer="development",
            session_secret="test-secret-rev026-prod-ok-32chars!",
            production=True,
        )
    assert app.hedron_explorer_mode == "off"
