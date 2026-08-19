"""VISUAL-051 extras empty/error/disabled states."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hedron import Hedron, Page
from hedron_extras.composition import TreeView
from hedron_extras.editors import Typeahead


def test_empty_and_error_gallery_markup() -> None:
    app = Hedron(title="Visual051", security="standard", session_secret="visual-051")

    @app.page("/")
    def home():
        return Page(
            TreeView([], empty_message="No items"),
            TreeView([], error_message="offline"),
            Typeahead("q", [], empty_message="No matches"),
            title="Visual",
        )

    with TestClient(app) as client:
        page = client.get("/")
        assert "No items" in page.text
        assert "offline" in page.text
        assert "No matches" in page.text
        assert 'role="alert"' in page.text
