"""REVIEW-028 adversarial trust-boundary suite for charts + native."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from hedron_charts.limits import reject_remote_urls
from hedron_charts.plugin import PLUGIN_META, register
from hedron_core import Text
from hedron_core.auto import Auto, clear_renderers_for_tests
from hedron_core.diagnostics import HedronError
from hedron_core.plugins import PluginContext, reset_explorer_panels_for_tests
from hedron_core.rendering import RenderMode, render


def test_cdn_remote_url_rejected_for_charts() -> None:
    with pytest.raises(HedronError) as exc:
        reject_remote_urls({"layout": {"images": [{"source": "https://cdn.example/x.png"}]}})
    assert exc.value.diagnostic.code == "HED-CHART-0005"


def test_interactive_auto_quarantines_plotly() -> None:
    clear_renderers_for_tests()
    reset_explorer_panels_for_tests()
    register(PluginContext(PLUGIN_META))
    try:

        class _PlotlyLike:
            __module__ = "plotly.graph_objs._figure"

        with pytest.raises(HedronError) as exc:
            Auto(_PlotlyLike()).resolve()
        assert exc.value.diagnostic.code in {"HED-AUTO-0001", "HED-AUTO-0004"}
    finally:
        clear_renderers_for_tests()
        reset_explorer_panels_for_tests()


def test_native_escape_of_script_tags() -> None:
    from hedron_native import escape_text, escape_text_python

    raw = "<script>alert(1)</script>"
    escaped = escape_text(raw)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped
    assert escaped == escape_text_python(raw)

    html = render(Text(raw), mode=RenderMode.FRAGMENT).html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_hedron_native_disable_subprocess() -> None:
    code = (
        "from hedron_native import native_available, native_disabled_by_env, "
        "escape_text, escape_text_python;"
        "assert native_disabled_by_env();"
        "assert not native_available();"
        "assert escape_text('<x>') == escape_text_python('<x>');"
        "print('ok')"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "HEDRON_NATIVE_DISABLE": "1"},
    )
    assert proc.returncode == 0, proc.stderr
    assert "ok" in proc.stdout
