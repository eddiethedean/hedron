"""Python StatusBanner used as the reference twin of the HDN template."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from hedron_core import (
    Component,
    Field,
    Props,
    StyleSymbols,
    compile_css,
    html,
    styles_from_manifest,
)

_ROOT = Path(__file__).resolve().parent
# Stable style component id shared by the HDN twin and parity tests.
STYLE_COMPONENT_ID = "hedron-reference:StatusBanner"
_styles: StyleSymbols | None = None


def load_styles(symbols: Mapping[str, str] | None = None) -> StyleSymbols:
    """Bind style symbols from a manifest, or compile colocated CSS once."""
    global _styles
    if symbols is not None:
        _styles = styles_from_manifest(symbols, component_id=STYLE_COMPONENT_ID)
        return _styles
    if _styles is not None:
        return _styles
    result = compile_css(
        (_ROOT / "styles.css").read_text(encoding="utf-8"),
        component_id=STYLE_COMPONENT_ID,
        registered_roots=[_ROOT],
        component_dir=_ROOT,
    )
    _styles = styles_from_manifest(result.manifest.symbols, component_id=STYLE_COMPONENT_ID)
    return _styles


def __getattr__(name: str) -> Any:
    if name == "styles":
        return load_styles()
    raise AttributeError(name)


class StatusBannerProps(Props):
    label: str = Field(default="Ready")
    tone: str = Field(default="info")


class StatusBanner(Component[StatusBannerProps]):
    """Representative custom component implemented in Python."""

    props_type = StatusBannerProps
    distribution = "hedron-reference"
    logical_name = "StatusBanner"

    def __init__(self, label: str = "Ready", *, tone: str = "info", **kwargs: Any) -> None:
        super().__init__(StatusBannerProps(label=label, tone=tone, **kwargs))

    def render(self) -> Any:
        return html.div(
            html.strong(self.props.label),
            class_=load_styles().root,
            data={"tone": self.props.tone, "impl": "python"},
        )
