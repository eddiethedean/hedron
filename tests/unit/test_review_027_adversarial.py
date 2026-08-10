"""REVIEW-027 adversarial satellite trust-boundary suite."""

from __future__ import annotations

import importlib

import pytest
from starlette.testclient import TestClient

from hedron import Hedron, Page, Text
from hedron_core.diagnostics import HedronError
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    resolve_fragment_region,
)
from hedron_core.rendering import RenderMode, render
from hedron_jinja.source import parse_hdj_source


def test_renderer_escapes_untrusted_text() -> None:
    html = render(Text("<script>alert(1)</script>"), mode=RenderMode.FRAGMENT).html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_fragment_region_fail_closed() -> None:
    policy = InteractionPolicy(declared_regions=(FragmentRegion(id="ok", selector="#ok"),))
    with pytest.raises(FragmentRegionError):
        resolve_fragment_region(policy, "#evil")


def test_hdj_rejects_missing_prologue() -> None:
    with pytest.raises(HedronError):
        parse_hdj_source("bad.hdj", "<p>no prologue</p>")


def test_extras_default_excludes_landmines() -> None:
    extras = importlib.import_module("hedron_extras")
    banned = {"TerminalView", "Joystick", "DeviceBridge", "CodeEditor"}
    assert banned.isdisjoint(set(extras.__all__))


def test_flask_and_django_modules_avoid_fastapi_imports() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for pkg in ("hedron-flask", "hedron-django"):
        for path in (root / "packages" / pkg / "src").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert "from fastapi" not in text
            assert "import fastapi" not in text


def test_csrf_still_required_on_fastapi_standard_action() -> None:
    app = Hedron(
        title="rev027",
        security="standard",
        explorer="off",
        session_secret="test-secret-rev027",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.action("/save")
    def save() -> Text:
        return Text("ok")

    client = TestClient(app)
    response = client.post("/save", data={"title": "x"})
    assert response.status_code in {400, 403, 422, 401}
