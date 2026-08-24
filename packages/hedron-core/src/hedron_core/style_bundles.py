# ruff: noqa: E501

"""Deterministic, dependency-ordered style bundles for phase 0.63.

The complete ``hedron-default.css`` remains the compatibility asset.  This module
adds a smaller, explicit bundle surface for applications that want to opt into a
known component set without taking ownership of the entire stylesheet.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from hedron_core.rendering import AssetRef
from hedron_core.theme import Theme, default_theme, emit_theme_css

__all__ = [
    "STYLE_BUNDLE_COMPONENTS",
    "StyleBundle",
    "compile_style_bundle",
    "compare_style_bundle_sizes",
    "style_bundle_asset_refs",
    "style_bundle_manifest",
]

STYLE_BUNDLE_COMPONENTS = (
    "app-shell",
    "button",
    "card",
    "chart",
    "dialog",
    "form",
    "popover",
    "surface",
)


@dataclass(frozen=True, slots=True)
class StyleBundle:
    """A local CSS bundle and its explicit dependency metadata."""

    logical_id: str
    href: str
    dependencies: tuple[str, ...]
    components: tuple[str, ...]
    css: str

    @property
    def byte_size(self) -> int:
        return len(self.css.encode("utf-8"))

    @property
    def digest(self) -> str:
        return "sha256-" + hashlib.sha256(self.css.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "logical_id": self.logical_id,
            "href": self.href,
            "dependencies": list(self.dependencies),
            "components": list(self.components),
            "byte_size": self.byte_size,
            "digest": self.digest,
        }


_BASE_CSS = """@layer reset, tokens, base, components, utilities, overrides;
@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  html { min-width: 20rem; text-size-adjust: 100%; }
  body { margin: 0; }
  button, input, select, textarea { font: inherit; }
}
@layer base {
  :where(button, a, input, select, textarea, [tabindex]):focus-visible {
    outline: var(--hedron-focus-ring, 3px solid var(--hedron-color-focus, #2563eb));
    outline-offset: 2px;
  }
  :where([aria-busy="true"], .hedron-is-busy) { cursor: progress; }
  :where([aria-invalid="true"], .hedron-has-error) {
    border-color: var(--hedron-color-danger, #c73939);
  }
}
"""

_ACCESSIBILITY_CSS = """@layer utilities {
  @media (forced-colors: active) {
    :where(.hedron-button, .hedron-card, .hedron-surface, .hedron-dialog, .hedron-popover) {
      forced-color-adjust: auto;
      border-color: ButtonText;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    :where(*, *::before, *::after) {
      animation-duration: 0ms !important;
      transition-duration: 0ms !important;
      scroll-behavior: auto !important;
    }
  }
  @media (prefers-reduced-transparency: reduce) {
    :where(.hedron-surface--translucent, .hedron-surface--glass,
      .hedron-card--translucent, .hedron-card--glass, .hedron-dialog--glass,
      .hedron-popover--glass) {
      background: var(--hedron-color-surface, Canvas);
      backdrop-filter: none;
    }
  }
  @media print {
    :where(.hedron-surface--translucent, .hedron-surface--glass,
      .hedron-card--translucent, .hedron-card--glass, .hedron-dialog--glass,
      .hedron-popover--glass) {
      background: var(--hedron-color-surface, #fff);
      box-shadow: none;
      backdrop-filter: none;
    }
  }
}
"""

_COMPONENT_CSS: Mapping[str, str] = {
    "app-shell": """@layer components {
  .hedron-app-shell { min-block-size: 100dvh; background: var(--hedron-color-bg, #f6f8fb); color: var(--hedron-color-fg, #172033); }
  .hedron-app-shell-nav { background: var(--hedron-color-surface, #fff); border-inline-end: 1px solid var(--hedron-color-border, #dce2eb); }
}
""",
    "button": """@layer components {
  .hedron-button, button.hedron-button { border: 1px solid var(--hedron-color-accent, #2563eb); border-radius: var(--hedron-shape-radius, .8rem); background: var(--hedron-color-accent, #2563eb); color: var(--hedron-color-on-accent, #fff); padding: .55rem .85rem; }
  .hedron-button:hover { background: var(--hedron-color-accent-hover, var(--hedron-color-accent, #2563eb)); }
  .hedron-button:disabled, .hedron-button[aria-disabled="true"] { opacity: .6; cursor: not-allowed; }
  .hedron-button[aria-busy="true"] { cursor: progress; }
}
""",
    "card": """@layer components {
  .hedron-card { background: var(--hedron-color-surface, #fff); color: var(--hedron-color-fg, #172033); border: 1px solid var(--hedron-color-border, #dce2eb); border-radius: var(--hedron-shape-radius, .8rem); box-shadow: var(--hedron-elevation-raised, none); }
  .hedron-card[aria-busy="true"] { opacity: .75; }
  .hedron-card[aria-invalid="true"], .hedron-card[data-state="error"] { border-color: var(--hedron-color-danger, #c73939); }
}
""",
    "chart": """@layer components {
  .hedron-chart { color: var(--hedron-chart-label, var(--hedron-color-fg, #172033)); background: var(--hedron-chart-surface, var(--hedron-color-surface, #fff)); }
  .hedron-chart [data-hedron-mark]:focus-visible { outline: 2px solid var(--hedron-chart-focus, var(--hedron-color-focus, #2563eb)); outline-offset: 2px; }
}
""",
    "dialog": """@layer components {
  .hedron-dialog { background: var(--hedron-color-surface, #fff); color: var(--hedron-color-fg, #172033); border: 1px solid var(--hedron-color-border, #dce2eb); border-radius: var(--hedron-shape-radius, .8rem); box-shadow: var(--hedron-overlay-shadow); }
  .hedron-dialog[aria-busy="true"] { cursor: progress; }
}
""",
    "form": """@layer components {
  .hedron-form-field { display: grid; gap: .35rem; }
  .hedron-form-field[aria-invalid="true"] input, .hedron-form-field[aria-invalid="true"] select, .hedron-form-field[aria-invalid="true"] textarea { border-color: var(--hedron-color-danger, #c73939); }
  .hedron-form-field:has(:disabled) { opacity: .72; }
}
""",
    "popover": """@layer components {
  .hedron-popover { background: var(--hedron-color-surface, #fff); color: var(--hedron-color-fg, #172033); border: 1px solid var(--hedron-color-border, #dce2eb); border-radius: var(--hedron-shape-radius, .8rem); box-shadow: var(--hedron-overlay-shadow); }
}
""",
    "surface": """@layer components {
  .hedron-surface { background: var(--hedron-color-surface, #fff); color: var(--hedron-color-fg, #172033); border: 1px solid var(--hedron-color-border, #dce2eb); border-radius: var(--hedron-shape-radius, .8rem); }
  :where(.hedron-surface--translucent, .hedron-card--translucent) { background: color-mix(in srgb, var(--hedron-surface-color, var(--hedron-color-surface, #fff)) var(--hedron-surface-opacity, 78%), transparent); backdrop-filter: blur(var(--hedron-surface-blur, 8px)); }
  :where(.hedron-surface--glass, .hedron-card--glass, .hedron-dialog--glass, .hedron-popover--glass) { background: color-mix(in srgb, var(--hedron-surface-color, var(--hedron-color-surface, #fff)) var(--hedron-glass-opacity, 72%), transparent); border-color: var(--hedron-glass-border, var(--hedron-color-border, #dce2eb)); box-shadow: var(--hedron-glass-shadow, var(--hedron-elevation-raised, none)); backdrop-filter: blur(var(--hedron-glass-blur, 14px)); }
}
""",
}


def _complete_stylesheet() -> str:
    path = Path(str(resources.files("hedron_core").joinpath("static/hedron-default.css")))
    return path.read_text(encoding="utf-8")


def _normalize_components(components: Iterable[str] | None) -> tuple[str, ...]:
    if components is None:
        return STYLE_BUNDLE_COMPONENTS
    selected = tuple(sorted(set(str(item) for item in components)))
    unknown = set(selected) - set(STYLE_BUNDLE_COMPONENTS)
    if unknown:
        raise ValueError(f"unknown style bundle components: {', '.join(sorted(unknown))}")
    return selected


def compile_style_bundle(
    *,
    theme: Theme | None = None,
    components: Iterable[str] | None = None,
    complete: bool = False,
) -> StyleBundle:
    """Compile a deterministic complete or component-scoped CSS bundle."""
    selected = _normalize_components(components)
    resolved_theme = theme or default_theme()
    if complete:
        css = _complete_stylesheet() + emit_theme_css(resolved_theme)
        logical_id = "hedron:styles:complete"
        dependencies = ("hedron:styles:tokens", "hedron:styles:base", "hedron:styles:a11y")
        bundle_components = STYLE_BUNDLE_COMPONENTS
    else:
        parts = [
            "@layer reset, tokens, base, components, utilities, overrides;\n",
            emit_theme_css(resolved_theme),
            _BASE_CSS,
            _ACCESSIBILITY_CSS,
        ]
        parts.extend(_COMPONENT_CSS[name] for name in selected)
        css = "".join(parts)
        suffix = "-".join(selected) if selected else "base"
        logical_id = f"hedron:styles:{suffix}"
        dependencies = ("hedron:styles:tokens", "hedron:styles:base", "hedron:styles:a11y")
        bundle_components = selected
    href = f"/hedron-static/bundles/{logical_id.rsplit(':', 1)[-1]}.css"
    return StyleBundle(logical_id, href, dependencies, tuple(bundle_components), css)


def style_bundle_manifest(*, theme: Theme | None = None) -> tuple[dict[str, object], ...]:
    """Return a stable manifest containing complete and scoped bundle facts."""
    complete = compile_style_bundle(theme=theme, complete=True)
    rows = [complete.to_dict()]
    for component in STYLE_BUNDLE_COMPONENTS:
        rows.append(compile_style_bundle(theme=theme, components=(component,)).to_dict())
    return tuple(rows)


def style_bundle_asset_refs(
    components: Iterable[str] | None = None,
    *,
    static_prefix: str = "/hedron-static",
) -> tuple[AssetRef, ...]:
    """Return local dependency-ordered AssetRefs for a selected bundle."""
    selected = _normalize_components(components)
    prefix = static_prefix.rstrip("/")
    refs = [
        AssetRef(kind="css", href=f"{prefix}/bundles/tokens.css"),
        AssetRef(kind="css", href=f"{prefix}/bundles/base.css"),
        AssetRef(kind="css", href=f"{prefix}/bundles/a11y.css"),
    ]
    refs.extend(
        AssetRef(kind="css", href=f"{prefix}/bundles/{component}.css") for component in selected
    )
    return tuple(refs)


def compare_style_bundle_sizes(*, theme: Theme | None = None) -> dict[str, int | bool]:
    """Compare the selected component bundle with the compatibility stylesheet."""
    complete = compile_style_bundle(theme=theme, complete=True)
    selected = compile_style_bundle(theme=theme, components=("button",))
    return {
        "complete_bytes": complete.byte_size,
        "selected_bytes": selected.byte_size,
        "selected_is_smaller": selected.byte_size < complete.byte_size,
    }
