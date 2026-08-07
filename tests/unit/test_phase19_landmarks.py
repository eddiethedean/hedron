"""Phase 0.19 LANDMARK-019: real landmark types and safe attrs."""

from __future__ import annotations

import pytest

from hedron_core import Footer, Header, Main, Nav, Section, Text, render
from hedron_core.builtins.landmarks import LandmarkProps


@pytest.mark.a11y
def test_landmarks_are_real_types_not_factories() -> None:
    assert Header.__name__ == "Header"
    assert Main.__name__ == "Main"
    assert Nav.__name__ == "Nav"
    assert Header.__qualname__ == "Header"
    assert isinstance(Header(Text("h")), Header)
    assert LandmarkProps is not None


@pytest.mark.a11y
def test_landmark_safe_attrs_render() -> None:
    html = render(
        Main(
            Header(Text("Top"), id="site-header", lang="en", aria={"label": "Site"}),
            Nav(Text("Menu"), class_="nav", dir="ltr"),
            Section(Text("Body"), title="Section"),
            Footer(Text("Bottom"), data={"hedron-footer": "true"}),
            id="main",
        )
    ).html
    assert '<main id="main">' in html
    assert 'id="site-header"' in html
    assert 'lang="en"' in html
    assert 'aria-label="Site"' in html
    assert 'class="nav"' in html
    assert 'dir="ltr"' in html
    assert 'title="Section"' in html
    assert "data-hedron-footer=" in html


@pytest.mark.a11y
def test_landmark_rejects_unknown_attrs() -> None:
    with pytest.raises(TypeError, match="Unsupported landmark"):
        Main(Text("x"), onclick="alert(1)")  # type: ignore[call-arg]


@pytest.mark.a11y
def test_landmark_rejects_hostile_roles() -> None:
    with pytest.raises(TypeError, match=r"role='presentation' is not allowed on landmark"):
        Main(Text("x"), role="presentation")
    with pytest.raises(TypeError, match=r"role='none' is not allowed on landmark"):
        Nav(Text("x"), role="none")
    with pytest.raises(TypeError, match=r"role='button' is not allowed on landmark"):
        Main(Text("x"), role="button")
