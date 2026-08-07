"""Phase 0.19 PE-019: progressive-enhancement forms/mutations without HTMX."""

from __future__ import annotations

import re

import pytest
from fastapi import Form as FastAPIForm
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient

from hedron import Form, Hedron, InteractionResult, Page, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request
from hedron_core import FragmentRegion, reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def _build_app() -> Hedron:
    app = Hedron(title="pe", security="standard", explorer="off", session_secret="test-secret")
    status = FragmentRegion(id="status", selector="#status")

    @app.page("/", fragment_regions=[status])
    def home(request: Request) -> Page:
        token = csrf_token_for_request(request, request.app.state.hedron_security)
        msg = request.query_params.get("msg", "idle")
        return Page(
            Form(
                html.input(type="hidden", name="csrf_token", value=token),
                TextInput("name", value="", required=True),
                SubmitButton("Save"),
                action="/save",
                method="post",
                **{
                    "hx-post": "/save",
                    "hx-target": "#status",
                    "hx-swap": "innerHTML",
                },
            ),
            html.div(Text(msg), id="status"),
            title="PE",
        )

    @app.component("/save", fragment_regions=[status], methods=["POST"])
    def save(
        request: Request,
        name: str = FastAPIForm(""),
        csrf_token: str = FastAPIForm(""),
    ) -> InteractionResult | RedirectResponse:
        _ = csrf_token
        if request.headers.get("hx-request") == "true":
            return InteractionResult(content=Text(f"saved:{name}"), region_id="status")
        # Classic no-JS POST → redirect to full Page (progressive enhancement).
        return RedirectResponse(url=f"/?msg=ok:{name}", status_code=303)

    return app


def test_no_hx_request_mutation_redirects_to_full_page() -> None:
    client = TestClient(_build_app())
    get = client.get("/")
    assert get.status_code == 200
    match = re.search(r'name="csrf_token" value="([^"]+)"', get.text)
    assert match is not None
    token = match.group(1)
    post = client.post("/save", data={"name": "Ada", "csrf_token": token}, follow_redirects=False)
    assert post.status_code == 303
    assert "ok:Ada" in post.headers.get("location", "")
    follow = client.get(post.headers["location"])
    assert follow.status_code == 200
    assert "<!DOCTYPE html>" in follow.text or "<html" in follow.text.lower()
    assert "ok:Ada" in follow.text


def test_hx_request_mutation_returns_fragment() -> None:
    client = TestClient(_build_app())
    get = client.get("/")
    match = re.search(r'name="csrf_token" value="([^"]+)"', get.text)
    assert match is not None
    token = match.group(1)
    post = client.post(
        "/save",
        data={"name": "Ada", "csrf_token": token},
        headers={"HX-Request": "true", "HX-Target": "#status"},
    )
    assert post.status_code == 200
    assert "<!DOCTYPE" not in post.text
    assert "saved:Ada" in post.text
