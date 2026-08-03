"""Conformance: Python and HDN StatusBanner twins lower to equivalent semantics."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from hedron_core import RenderMode, compile_css, compile_hdn, render, run_program


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
    return module.StatusBanner, root, module


def _normalize(html: str) -> str:
    html = re.sub(r"\s+", " ", html)
    html = html.replace('data-impl="python"', 'data-impl="X"')
    html = html.replace('data-impl="hdn"', 'data-impl="X"')
    return html.strip()


def test_python_and_hdn_status_banner_equivalent() -> None:
    StatusBanner, root, module = _load_status_banner()
    style_id = module.STYLE_COMPONENT_ID
    css = compile_css(
        (root / "styles.css").read_text(encoding="utf-8"),
        component_id=style_id,
        registered_roots=[root],
        component_dir=root,
    )
    scoped_root = css.manifest.symbols["root"]
    assert scoped_root.startswith("h-root-")
    assert module.styles.root == scoped_root

    py_html = render(
        StatusBanner(label="Ready", tone="info"),
        mode=RenderMode.FRAGMENT,
    ).html
    hdn_html = render(
        run_program(
            compile_hdn(
                (root / "template.hdn").read_text(encoding="utf-8"),
                style_symbols=css.manifest.symbols,
            ).program,
            {"label": "Ready", "tone": "info"},
        ),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "Ready" in py_html and "Ready" in hdn_html
    assert 'data-tone="info"' in py_html and 'data-tone="info"' in hdn_html
    assert scoped_root in py_html and scoped_root in hdn_html
    assert "strong" in _normalize(py_html).lower()
    assert "strong" in _normalize(hdn_html).lower()
