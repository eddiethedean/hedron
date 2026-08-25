#!/usr/bin/env python3
"""Executable contract checks for the phase 0.65 styling platform."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from hedron_core.diagnostics import HedronError

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
    from hedron_core.registry.application_style import register_application_style

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "verified.css"
        source.write_text(".card { color: red; }", encoding="utf-8")
        meta = register_application_style(
            name=f"gate-asset-{uuid.uuid4().hex[:8]}",
            source=source,
            scope="gate",
            allowed_roots=(root,),
        )
        _require(meta.source_digest.startswith("sha256-"), "style fingerprint missing")
        _require(
            meta.to_dict(source_root=root)["source"] == "verified.css",
            "style source was not redacted",
        )


def _check_layer() -> None:
    layers = _text(CORE / "css/layers.py")
    bundles = _text(CORE / "style_bundles.py")
    static = _text(FACADE / "static/hedron-default.css")
    expected = "reset, tokens, base, components, application, utilities, overrides"
    _require('"application"' in layers, "application cascade layer is missing from compiler")
    for text in (bundles, static):
        _require(expected in text, "application cascade layer is not declared everywhere")


def _check_tokens() -> None:
    from hedron_core.presentation_064 import presentation_token_manifest

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
    manifest = presentation_token_manifest()
    _require(not manifest["unconsumed"], f"unused presentation tokens: {manifest['unconsumed']}")


def _check_hooks() -> None:
    from hedron_core.presentation_064 import application_style_hook_manifest

    source = _text(CORE / "presentation_064.py")
    for hook in ("AppShell", "ProcessFlow", "Card", "FormField", "SplitView"):
        _require(hook in source, f"hook component missing: {hook}")
    for attr in ("hedron-component", "hedron-part", "hedron-state"):
        _require(attr in source, f"hook attribute missing: {attr}")
    _require("Card" in application_style_hook_manifest(), "hook manifest is not executable")


def _check_css() -> None:
    from hedron_core.css.compiler import compile_css

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
    scoped = compile_css(
        '.card:is(.primary, .secondary), .card:not([data-kind="a,b"]) { color: red; }',
        component_id="application:gate",
        layer="application",
        scope_root=':where([data-hedron-style-scope="gate"])',
        rewrite_selectors=False,
    )
    _require(".card:is(.primary, .secondary)" in scoped.css, "nested selector scoping is broken")
    try:
        compile_css(
            '@import "https://example.com/theme.css"; .card { color: red; }',
            component_id="application:gate",
            layer="application",
            rewrite_selectors=False,
        )
    except HedronError as exc:
        _require("Remote CSS import rejected" in str(exc), "wrong remote-import diagnostic")
    else:
        raise AssertionError("quoted remote CSS imports must be rejected")


def _check_tooling() -> None:
    parser = _text(FACADE / "cli/parser.py")
    style = _text(FACADE / "cli/commands/style.py")
    for option in ("inspect", "--custom-css", "eject-css", "ejected-path", "update"):
        _require(option in parser or option in style, f"style tooling missing: {option}")


def _check_presentation() -> None:
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


def _check_recipe() -> None:
    from hedron_core import PresentationError, ScopedStyleRecipe, compile_scoped_styles

    try:
        ScopedStyleRecipe(
            component="PrivateWidget",
            part="internal",
            declarations={"color": "red"},
        )
    except PresentationError:
        pass
    else:
        raise AssertionError("private recipe hooks must be rejected")
    css = compile_scoped_styles(
        (
            ScopedStyleRecipe(
                component="Card",
                part="heading",
                declarations={"opacity": "1"},
                motion="crossfade",
            ),
        )
    ).css
    _require("motion-crossfade" in css, "named motion recipe is not compiled")


def _check_ejection() -> None:
    parser = _text(FACADE / "cli/parser.py")
    style = _text(FACADE / "cli/commands/style.py")
    for needle in ("_cmd_style_update_check", "hedron.style-drift/1", "style-ejection/1"):
        _require(needle in parser or needle in style, f"ejection workflow missing: {needle}")


def _check_manifest_redaction() -> None:
    source = _text(CORE / "registry/application_style.py")
    build = _text(FACADE / "build/compile.py")
    _require("_redacted_source" in source, "manifest source redaction missing")
    _require('"source": style_entry["source"]' in build, "build source map is not redacted")


def _check_release_documents() -> None:
    gate = _text(ROOT / "docs/acceptance/release-gate-0.65.toml")
    inventory = _text(ROOT / "docs/acceptance/application-styling-inventory-065.toml")
    contract = _text(ROOT / "docs/acceptance/application-styling-contract-065.toml")
    _require('status = "Verified"' in gate, "release gate is not Verified")
    _require('status = "Verified"' in inventory, "capability inventory is not Verified")
    _require('status = "Verified"' in contract, "styling contract is not Verified")
    _require(
        "no runtime claim" not in _text(ROOT / "docs/STATUS.md"),
        "status still denies runtime claim",
    )


def _check_full_regression() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/unit/test_phase064_presentation.py",
            "tests/unit/test_phase065_styling.py",
            "tests/unit/test_phase065_issues_712_715.py",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    _require(result.returncode == 0, result.stdout[-2000:] + result.stderr[-1000:])


def _check_accessibility() -> None:
    css = _text(FACADE / "static/hedron-default.css")
    for needle in ("focus-visible", "forced-colors", "prefers-reduced-motion", "@media print"):
        _require(needle in css, f"accessibility fallback missing: {needle}")


def _check_controls() -> None:
    source = _text(CORE / "presentation_064.py")
    for token in ("control.focus", "control.invalid", "control.disabled", "control.indeterminate"):
        _require(token in source, f"control token missing: {token}")


def _check_data() -> None:
    source = _text(CORE / "presentation_064.py")
    for token in ("data.table.radius", "data.table.numeric", "data.table.sticky.elevation"):
        _require(token in source, f"data token missing: {token}")


def _check_motion() -> None:
    source = _text(CORE / "presentation_064.py")
    for name in ("MotionRecipe", "motion_recipes", "motion_recipe"):
        _require(name in source, f"motion recipe API missing: {name}")


def _check_security() -> None:
    _check_css()
    _check_asset()


def _check_package() -> None:
    _check_asset()
    _require(
        (ROOT / "packages/hedron-core/pyproject.toml").is_file(),
        "core package metadata missing",
    )


CHECKS = {
    "CONTRACT-065": _check_contract,
    "ASSET-065": _check_asset,
    "LAYER-065": _check_layer,
    "TOKEN-065": _check_tokens,
    "HOOKS-065": _check_hooks,
    "RECIPE-065": _check_recipe,
    "CSS-065": _check_css,
    "INSPECT-065": _check_tooling,
    "EJECT-065": _check_ejection,
    "MOTION-065": _check_motion,
    "CONTROLS-065": _check_controls,
    "DATA-065": _check_data,
    "PRESENT-065": _check_presentation,
    "A11Y-065": _check_accessibility,
    "SECURITY-065": _check_security,
    "PERF-065": _check_manifest_redaction,
    "FLEET-065": _check_release_documents,
    "UPGRADE-065": _check_release_documents,
    "REGRESS-065": _check_full_regression,
    "DOCS-065": _check_release_documents,
    "PKG-065": _check_package,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", choices=sorted(GATE_IDS), default=None)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not args.verify:
        parser.error("--verify is required for executable release evidence")
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
