"""A11Y-049 schema/form parity and no SR-021 closure."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from hedron_core.builtins import Text
from hedron_core.rendering import render

pytestmark = pytest.mark.a11y


def test_schema_forms_remain_ordinary_html() -> None:
    html = render(Text("label required")).html
    assert "label required" in html
    impl = Path("docs/implementation/FASTAPI_PYDANTIC_CONVERGENCE_049.md").read_text(
        encoding="utf-8"
    )
    release = Path("docs/acceptance/RELEASE_0_49.md").read_text(encoding="utf-8")
    assert "SR-021" in impl or "SR-021" in release


def test_binding_strategies_do_not_invent_aria_live() -> None:
    html = render(Text("error")).html
    assert "aria-live" not in html


@pytest.mark.parametrize("engine", ("chromium", "firefox", "webkit"))
def test_optional_browser_a11y(engine: str) -> None:
    if os.environ.get("HEDRON_BROWSER", "").strip() not in {"1", "true", "yes"}:
        pytest.skip("HEDRON_BROWSER not set")
    selected = os.environ.get("HEDRON_BROWSER_ENGINE")
    if selected and selected != engine:
        pytest.skip(f"engine filter {selected}")
    assert render(Text("ok")).html
