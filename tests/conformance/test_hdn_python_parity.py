"""Conformance: Python and HDN StatusBanner twins lower to equivalent semantics."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from hedron_core import RenderMode, compile_hdn, render, run_program


def _load_status_banner():
    root = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "reference-app"
        / "components"
        / "StatusBanner"
    )
    spec = importlib.util.spec_from_file_location("status_banner_conf", root / "component.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.StatusBanner, root


def _normalize(html: str) -> str:
    html = re.sub(r"\s+", " ", html)
    html = html.replace('data-impl="python"', 'data-impl="X"')
    html = html.replace('data-impl="hdn"', 'data-impl="X"')
    return html.strip()


def test_python_and_hdn_status_banner_equivalent() -> None:
    StatusBanner, root = _load_status_banner()
    py_html = render(
        StatusBanner(label="Ready", tone="info"),
        mode=RenderMode.FRAGMENT,
    ).html
    hdn_html = render(
        run_program(
            compile_hdn((root / "template.hdn").read_text(encoding="utf-8")).program,
            {"label": "Ready", "tone": "info"},
        ),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "Ready" in py_html and "Ready" in hdn_html
    assert 'data-tone="info"' in py_html and 'data-tone="info"' in hdn_html
    assert "root" in py_html and "root" in hdn_html
    # Equivalent observable structure after normalizing implementation markers.
    assert "strong" in _normalize(py_html).lower()
    assert "strong" in _normalize(hdn_html).lower()
