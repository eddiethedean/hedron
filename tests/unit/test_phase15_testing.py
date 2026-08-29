"""Phase 0.15 AppScenario / mark / fixture foundation tests."""

from __future__ import annotations

import pytest

from hedron import Card, Heading, Hedron, Page, Text
from hedron.testing import (
    AppScenario,
    AuthPrincipal,
    OidcCallbackStub,
    UploadFixture,
    as_adapter,
    assert_non_200_fragment,
    fastapi_fixture,
    find_all_marks,
    find_mark,
    fragment_client,
    redact_secrets_for_failure,
    render_html,
)
from hedron_core.builtins._base import mark_data
from hedron_core.testing.adapters import AdapterResponse


def test_mark_data_emits_hedron_mark_key() -> None:
    assert mark_data("submit") == {"hedron-mark": "submit"}
    assert mark_data(None) == {}
    assert mark_data("") == {}


def test_card_mark_renders_data_attribute() -> None:
    html = render_html(Card(Text("Hello"), title="T", mark="greeting-card"))
    assert 'data-hedron-mark="greeting-card"' in html
    found = find_mark(html, mark="greeting-card")
    assert found.tag == "article"
    assert "Hello" in found.html
    assert find_all_marks(html, mark="greeting-card")
    assert find_all_marks(html, mark="missing") == []


def test_app_scenario_find_on_last_response() -> None:
    html = '<div data-hedron-mark="a">one</div><span data-hedron-mark="b">two</span>'

    def get(path: str, *, headers=None, cookies=None) -> AdapterResponse:
        return AdapterResponse(200, html, {}, dict(cookies or {}))

    def post(path: str, *, data=None, headers=None, cookies=None) -> AdapterResponse:
        return AdapterResponse(200, html, {}, dict(cookies or {}))

    scenario = AppScenario.from_callables(get, post)
    scenario.get("/")
    assert scenario.find(mark="a").tag == "div"
    assert [el.mark for el in scenario.find_all()] == ["a", "b"]


def test_app_scenario_retains_cookies_across_requests() -> None:
    seen: list[dict[str, str]] = []

    def get(path: str, *, headers=None, cookies=None) -> AdapterResponse:
        jar = dict(cookies or {})
        seen.append(jar)
        return AdapterResponse(200, "ok", {}, {"session": "abc"} if "session" not in jar else {})

    def post(path: str, *, data=None, headers=None, cookies=None) -> AdapterResponse:
        return AdapterResponse(200, "posted", {}, {})

    scenario = AppScenario.from_callables(get, post)
    scenario.navigate("/")
    scenario.fragment_get("/frag", target="#main")
    assert seen[0] == {}
    assert seen[1].get("session") == "abc"
    assert scenario.cookies["session"] == "abc"


def test_fragment_methods_set_htmx_headers() -> None:
    captured: list[dict[str, str]] = []

    def get(path: str, *, headers=None, cookies=None) -> AdapterResponse:
        captured.append(dict(headers or {}))
        return AdapterResponse(200, "<div>frag</div>", {}, {})

    def post(path: str, *, data=None, headers=None, cookies=None) -> AdapterResponse:
        captured.append(dict(headers or {}))
        return AdapterResponse(200, "<div>saved</div>", {}, {})

    scenario = AppScenario.from_callables(get, post)
    scenario.fragment_get("/x", target="#panel")
    scenario.fragment_post("/y", data={"a": "1"}, target="#panel")
    assert captured[0]["HX-Request"] == "true"
    assert captured[0]["HX-Target"] == "#panel"
    assert captured[1]["HX-Request"] == "true"
    assert captured[1]["HX-Target"] == "#panel"


def test_fixture_validation_and_redaction() -> None:
    principal = AuthPrincipal(subject="user-1", roles=("admin",), claims={"email": "a@b.c"})
    assert principal.subject == "user-1"
    with pytest.raises(ValueError):
        AuthPrincipal(subject="")
    stub = OidcCallbackStub(state="st", code="secret-code")
    redacted = redact_secrets_for_failure(stub)
    assert redacted["code"] == "[redacted]"
    assert redacted["state"] == "st"


def test_upload_fixture_rejects_mutable_bytearray_content() -> None:
    with pytest.raises(ValueError, match="content must be bytes"):
        UploadFixture(
            filename="sample.txt",
            content_type="text/plain",
            content=bytearray(b"mutable"),  # type: ignore[arg-type]
        )


def test_assert_non_200_fragment() -> None:
    response = AdapterResponse(422, "<div class='error'>invalid</div>", {})
    assert_non_200_fragment(response, status_code=422, contains="invalid")
    with pytest.raises(AssertionError):
        assert_non_200_fragment(response, status_code=400)
    with pytest.raises(AssertionError):
        assert_non_200_fragment(
            AdapterResponse(422, "<html><body>x</body></html>", {}),
            status_code=422,
        )


def test_fastapi_app_scenario_smoke() -> None:
    app = Hedron(
        title="phase15",
        security="standard",
        session_secret="phase15-secret",
        explorer="off",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Heading("Home", level=1), Card(Text("Marked"), mark="home-card"), title="Home")

    fixture = fastapi_fixture(app)
    scenario = AppScenario(fixture)
    response = scenario.navigate("/")
    assert response.status_code == 200
    scenario.assert_page_document()
    found = scenario.find(mark="home-card")
    assert found.tag == "article"
    assert "Marked" in found.html

    client = fragment_client(app, target="#main")
    assert client.headers["HX-Request"] == "true"
    assert client.headers["HX-Target"] == "#main"
    wrapped = as_adapter(fragment_client(app))
    assert wrapped.name == "fastapi"
    again = AppScenario.from_fixture(wrapped)
    page = again.get("/")
    assert page.status_code == 200
    assert "Home" in page.body
