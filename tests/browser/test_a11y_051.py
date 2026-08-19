"""A11Y-051 extras semantics and password toggle."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import Hedron, Page, TextInput
from hedron_extras.editors import Typeahead


def test_password_and_typeahead_semantics() -> None:
    app = Hedron(title="A11y051", security="standard", session_secret="a11y-051")

    @app.page("/")
    def home():
        return Page(
            TextInput("pw", type="password"),
            Typeahead("q", ["one"], empty_message="No matches"),
            title="A11y",
        )

    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Show password" in page.text
        assert 'role="combobox"' in page.text
        assert "hedron-extras-typeahead" in page.text
