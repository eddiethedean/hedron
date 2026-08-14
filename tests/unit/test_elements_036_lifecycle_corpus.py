"""LIFECYCLE-036 unit corpus: 100 SSR re-instances (always-on)."""

from __future__ import annotations

from hedron_core.rendering import render
from hedron_elements.example import Example


def test_one_hundred_ssr_instances() -> None:
    for i in range(100):
        html = render(Example(status=f"S{i}")).html
        assert "hedron-example" in html
        assert f"S{i}" in html
        assert html.count("<hedron-example") == 1
