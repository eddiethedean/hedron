"""Cascade layer helpers."""

from __future__ import annotations

CASCADE_LAYERS: tuple[str, ...] = (
    "reset",
    "tokens",
    "base",
    "components",
    "utilities",
    "overrides",
)


def wrap_in_layer(css: str, layer: str) -> str:
    if layer not in CASCADE_LAYERS:
        raise ValueError(f"Unknown cascade layer: {layer}")
    body = css.strip()
    if not body:
        return f"@layer {layer} {{}}\n"
    return f"@layer {layer} {{\n{body}\n}}\n"
