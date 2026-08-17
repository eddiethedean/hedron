"""SECURITY-049 strict content type, scopes non-authority, no new CSRF."""

from __future__ import annotations

from typing import Annotated

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from tests.unit._helpers_043 import csrf_headers
from tests.unit._helpers_049 import make_app, reset_049

from hedron import FormBody, Page, RequiresScopes, Text
from hedron.type_authoring.normalize import inspect_handler
from hedron.type_authoring.signature import reject_json_formbody


def setup_function() -> None:
    reset_049()


class Payload(BaseModel):
    title: str = "x"


def test_formbody_json_still_415() -> None:
    app = make_app(security="standard")

    @app.command("/save", fallback="/")
    def save(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    with TestClient(app) as client:
        headers = csrf_headers(client, htmx=False)
        response = client.post(
            save.path,
            content=b'{"title":"nope"}',
            headers={**headers, "Content-Type": "application/json"},
        )
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_strict_json_profile_and_scopes_are_declarations() -> None:
    compiled = inspect_handler(lambda: None, kind="command")

    class _Headers(dict):
        pass

    class _Request:
        headers = _Headers({"content-type": "text/plain"})

    try:
        reject_json_formbody(compiled, _Request(), strict_json=True)
    except HTTPException as exc:
        assert exc.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    else:
        raise AssertionError("expected 415")
    scopes = RequiresScopes("a", "b")
    assert scopes.grants_access() is False
    assert scopes.scopes == ("a", "b")
