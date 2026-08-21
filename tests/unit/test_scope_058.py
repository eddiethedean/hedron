"""SCOPE-058 evidence."""

from __future__ import annotations

import pytest

from hedron import StyleScope, Text
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import RenderContext, RenderMode, render


def test_style_scope_emits_data_hedron_markers() -> None:
    html = render(
        StyleScope(Text("scoped"), theme="default", color_mode="dark", density="compact"),
        context=RenderContext.standalone(),
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-style-scope="true"' in html
    assert 'data-hedron-theme="default"' in html
    assert 'data-hedron-color-mode="dark"' in html
    assert 'data-hedron-density="compact"' in html


def test_style_scope_rejects_invalid_density() -> None:
    with pytest.raises(HedronError):
        StyleScope(Text("x"), density="ultra")  # type: ignore[arg-type]
