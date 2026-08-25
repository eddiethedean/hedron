#!/usr/bin/env python3
"""Executable contract checks for the phase 0.65 styling platform."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "packages/hedron-core/src/hedron_core"
FACADE = ROOT / "packages/hedron/src/hedron"
GATE_IDS = {
    "CONTRACT-065",
    "ASSET-065",
    "LAYER-065",
    "TOKEN-065",
    "HOOKS-065",
    "RECIPE-065",
    "CSS-065",
    "INSPECT-065",
    "EJECT-065",
    "MOTION-065",
    "CONTROLS-065",
    "DATA-065",
    "PRESENT-065",
    "A11Y-065",
    "SECURITY-065",
    "PERF-065",
    "FLEET-065",
    "UPGRADE-065",
    "REGRESS-065",
    "DOCS-065",
    "PKG-065",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _check_contract() -> None:
    scope = _text(ROOT / "docs/acceptance/application-styling-scope-065.md")
    contract = _text(ROOT / "docs/acceptance/application-styling-contract-065.toml")
    rfc = _text(ROOT / "docs/rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md")
    for issue in ("#690", "#693", "#694", "#698", "#712", "#713", "#714", "#715"):
        _require(issue in scope and issue in rfc, f"missing issue disposition: {issue}")
    _require("style_manifest" in contract, "style manifest contract missing")
    _require("global_css_requires_opt_in = true" in contract, "global CSS policy missing")


def _check_asset() -> None:
    source = _text(CORE / "registry/application_style.py")
    builder = _text(CORE / "registry/builder.py")
    compile_source = _text(FACADE / "build/compile.py")
    for text, needle in (
        (source, "register_application_style"),
        (builder, "application_styles"),
        (compile_source, "ApplicationStyleManifest"),
        (compile_source, "fingerprint_file"),
    ):
        _require(needle in text, f"application style asset seam missing: {needle}")


def _check_layer() -> None:
    layers = _text(CORE / "css/layers.py")
    bundles = _text(CORE / "style_bundles.py")
    static = _text(FACADE / "static/hedron-default.css")
    expected = "reset, tokens, base, components, application, utilities, overrides"
    _require('"application"' in layers, "application cascade layer is missing from compiler")
    for text in (bundles, static):
        _require(expected in text, "application cascade layer is not declared everywhere")


def _check_tokens() -> None:
    source = _text(CORE / "presentation_064.py")
    motion_names = (
        "motion.instant",
        "motion.standard",
        "motion.emphasized",
        "motion.reveal",
        "motion.elevate",
        "motion.crossfade",
    )
    for name in motion_names:
        _require(f'"{name}"' in source, f"motion token missing: {name}")
    _require("data.table.border" in source, "data-view semantic token missing")
    _require("control.appearance" in source, "native control token missing")
    _require("presentation_token_manifest" in source, "presentation token manifest missing")


def _check_hooks() -> None:
    source = _text(CORE / "presentation_064.py")
    for hook in ("AppShell", "ProcessFlow", "Card", "FormField", "SplitView"):
        _require(hook in source, f"hook component missing: {hook}")
    for attr in ("hedron-component", "hedron-part", "hedron-state"):
        _require(attr in source, f"hook attribute missing: {attr}")


def _check_css() -> None:
    source = _text(CORE / "css/compiler.py")
    _require(
        "scope_root" in source and "allow_remote" in source,
        "CSS compiler policy seam missing",
    )
    _require("_scope_prelude" in source, "CSS scope rewrite missing")
    _require(
        "@layer application" in _text(FACADE / "static/hedron-default.css"),
        "application CSS layer missing",
    )


def _check_tooling() -> None:
    parser = _text(FACADE / "cli/parser.py")
    style = _text(FACADE / "cli/commands/style.py")
    for option in ("inspect", "--custom-css", "eject-css"):
        _require(option in parser or option in style, f"style tooling missing: {option}")


def _check_verticals() -> None:
    css = _text(FACADE / "static/hedron-default.css")
    for text in ("prefers-reduced-motion", "forced-colors", "@media print", "accent-color"):
        _require(text in css, f"required fallback missing: {text}")
    for text in ("data-hedron-row-state", "table.hedron-table", 'input[type="range"]'):
        _require(text in css, f"required issue slice missing: {text}")
    for text in ("hedron-ambient-layer", "hedron-shell-preset", "prefers-reduced-transparency"):
        _require(
            text in css
            or text in _text(CORE / "builtins" / "surfaces.py")
            or text in _text(CORE / "builtins" / "shell.py"),
            f"0.65 styling slice missing: {text}",
        )


def _check_docs() -> None:
    for relative in (
        "docs/implementation/EXECUTION_0_65.md",
        "docs/implementation/APPLICATION_STYLING_065.md",
        "docs/acceptance/RELEASE_0_65.md",
    ):
        _require((ROOT / relative).is_file(), f"missing release document: {relative}")


CHECKS = {
    "CONTRACT-065": _check_contract,
    "ASSET-065": _check_asset,
    "LAYER-065": _check_layer,
    "TOKEN-065": _check_tokens,
    "HOOKS-065": _check_hooks,
    "RECIPE-065": _check_tokens,
    "CSS-065": _check_css,
    "INSPECT-065": _check_tooling,
    "EJECT-065": _check_tooling,
    "MOTION-065": _check_verticals,
    "CONTROLS-065": _check_verticals,
    "DATA-065": _check_verticals,
    "PRESENT-065": _check_verticals,
    "A11Y-065": _check_verticals,
    "SECURITY-065": _check_css,
    "PERF-065": _check_asset,
    "FLEET-065": _check_docs,
    "UPGRADE-065": _check_docs,
    "REGRESS-065": _check_docs,
    "DOCS-065": _check_docs,
    "PKG-065": _check_asset,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", choices=sorted(GATE_IDS), default=None)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    selected = [args.gate] if args.gate else sorted(GATE_IDS)
    gate = "startup"
    try:
        for gate in selected:
            CHECKS[gate]()
            print(f"ok: {gate}")
    except (AssertionError, OSError, UnicodeDecodeError) as exc:
        print(f"not ready: {gate}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
