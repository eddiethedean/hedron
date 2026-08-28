#!/usr/bin/env python3
"""Executable contract checks for the phase 0.65 styling platform."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

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
    from hedron.cli.commands.style import (
        _application_style_drift,
        _cmd_style_eject_application,
    )
    from hedron_core.registry.application_style import register_application_style
    from hedron_core.registry.builder import (
        reset_registry_for_tests,
        restore_registry_builder,
        snapshot_registry_builder,
    )

    snapshot = snapshot_registry_builder()
    original_cwd = Path.cwd()
    reset_registry_for_tests()
    try:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            outside = root / "outside"
            project.mkdir()
            outside.mkdir()
            source = project / "app.css"
            source.write_text(".card { color: red; }", encoding="utf-8")
            register_application_style(
                name=f"gate-eject-{uuid.uuid4().hex[:8]}",
                source=source,
                scope="gate",
                allowed_roots=(project,),
            )
            os.chdir(project)
            output = io.StringIO()
            with patch("hedron.cli.commands.style._require_app", return_value=object()):
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    result = _cmd_style_eject_application(
                        argparse.Namespace(app="gate:app", output="ejected", overwrite=False)
                    )
                _require(result == 0, f"real ejection failed: {output.getvalue()}")

                ejected = project / "ejected"
                css = ejected / "application-styles.css"
                manifest = ejected / "source_map.json"
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                _require(payload.get("blocks"), "ejection block digests are missing")
                _require(payload.get("css_digest"), "ejection CSS digest is missing")
                _require(_application_style_drift(manifest)["clean"], "fresh ejection is not clean")
                css.write_text(
                    css.read_text(encoding="utf-8") + "/* edited */\n",
                    encoding="utf-8",
                )
                drift = _application_style_drift(manifest)
                _require(drift["ejected_changed"], "edited ejection was not detected")

                for unsafe_output in ("../outside", "linked"):
                    if unsafe_output == "linked":
                        (project / "linked").symlink_to(outside, target_is_directory=True)
                    output.seek(0)
                    output.truncate(0)
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                        result = _cmd_style_eject_application(
                            argparse.Namespace(
                                app="gate:app",
                                output=unsafe_output,
                                overwrite=True,
                            )
                        )
                    _require(result == 1, f"unsafe ejection was accepted: {unsafe_output}")
                _require(
                    not (outside / "application-styles.css").exists(),
                    "ejection escaped the project root",
                )
    finally:
        os.chdir(original_cwd)
        reset_registry_for_tests()
        restore_registry_builder(snapshot)


def _check_manifest_redaction() -> None:
    source = _text(CORE / "registry/application_style.py")
    build = _text(FACADE / "build/compile.py")
    _require("_redacted_source" in source, "manifest source redaction missing")
    _require('"source": style_entry["source"]' in build, "build source map is not redacted")


def _check_release_documents() -> None:
    from hedron_core.compat import tomllib

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
    parsed = tomllib.loads(gate)
    _require(parsed["predecessor_satisfied"] is True, "predecessor audit is not satisfied")
    _require(parsed["zero_deferred_at_cut"] is False, "deferred policy is misstated")
    _require(parsed.get("deferred_policy"), "deferred policy is undocumented")


def _check_fleet() -> None:
    from hedron_core.compat import tomllib

    inventory = tomllib.loads(
        _text(ROOT / "docs/acceptance/application-styling-inventory-065.toml")
    )
    capabilities = inventory.get("capability", [])
    _require(capabilities, "capability inventory is empty")
    for capability in capabilities:
        disposition = capability.get("disposition")
        expected_state = "Verified" if disposition == "Required" else "Planned"
        _require(
            capability.get("state") == expected_state,
            f"invalid capability state: {capability.get('id')}",
        )
        if disposition in {"Progressive", "Deferred"}:
            _require(
                capability.get("owner"),
                f"unowned progressive capability: {capability.get('id')}",
            )
            _require(
                capability.get("fallback"),
                f"progressive capability lacks fallback: {capability.get('id')}",
            )


def _check_upgrade() -> None:
    fixture = _text(ROOT / "docs/acceptance/application-styling-upgrade-fixtures-065.md")
    for needle in ("v0.64.1", "v0.65.0", "source_map.json", "application-styles.css"):
        _require(needle in fixture, f"upgrade fixture missing: {needle}")
    _require(
        "allowed_roots" in _text(FACADE / "app/hedron.py"),
        "package-root upgrade path missing",
    )


def _check_full_regression() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests",
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


def _check_performance() -> None:
    from hedron_core.css.compiler import compile_css

    stylesheet = ".card { color: red; } .card:hover { color: blue; }"
    started = time.perf_counter()
    for _ in range(100):
        compile_css(
            stylesheet,
            component_id="application:performance",
            layer="application",
            rewrite_selectors=False,
        )
    elapsed = time.perf_counter() - started
    _require(elapsed < 2.0, f"CSS compile regression exceeded 2s budget: {elapsed:.3f}s")


def _check_security() -> None:
    _check_css()
    _check_asset()
    _check_manifest_redaction()


def _check_package() -> None:
    with tempfile.TemporaryDirectory() as directory:
        requirements = {
            "hedron-core": {
                "hedron_core/static/hedron-default.css",
                "hedron_core/css/compiler.py",
            },
            "hedron": {
                "hedron/static/hedron-default.css",
                "hedron/cli/commands/style.py",
            },
        }
        for package, required_files in requirements.items():
            _require(
                (ROOT / f"packages/{package}/pyproject.toml").is_file(),
                f"{package} package metadata missing",
            )
            destination = Path(directory) / package
            destination.mkdir()
            result = subprocess.run(
                [
                    "uv",
                    "build",
                    "--package",
                    package,
                    "--wheel",
                    "--out-dir",
                    str(destination),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            _require(result.returncode == 0, result.stdout[-1000:] + result.stderr[-1000:])
            wheels = sorted(destination.glob("*.whl"))
            _require(wheels, f"{package} wheel was not produced")
            with zipfile.ZipFile(wheels[0]) as wheel:
                names = set(wheel.namelist())
            missing = sorted(required_files - names)
            _require(not missing, f"{package} wheel is missing files: {missing}")


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
    "PERF-065": _check_performance,
    "FLEET-065": _check_fleet,
    "UPGRADE-065": _check_upgrade,
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
