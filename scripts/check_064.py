#!/usr/bin/env python3
"""Verify the bounded 0.64.0 presentation/lifecycle release slice.

This checker deliberately verifies only the contracts shipped in the 0.64.0
cut. Broader phase work remains explicitly Deferred in the release manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATES = {
    "CONTRACT-064": "contract",
    "THEME-064": "theme",
    "MANIFEST-064": "manifest",
    "TYPOGEOM-064": "typogeom",
    "RESPONSIVE-064": "responsive",
    "CUSTOM-064": "custom",
    "ASSET-064": "asset",
    "STATE-064": "state",
    "A11Y-064": "a11y",
    "INTEGRATE-064": "integrate",
    "CSP-064": "csp",
    "SECURITY-064": "security",
    "UPGRADE-064": "upgrade",
    "DOCS-064": "docs",
    "PKG-064": "pkg",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def check_contract() -> None:
    from hedron_core.htmx_064 import HEDRON_LIFECYCLE_SCHEMA, lifecycle_attributes
    from hedron_core.presentation_064 import PRESENTATION_SCHEMA

    assert PRESENTATION_SCHEMA == "hedron.presentation-contract/1"
    assert HEDRON_LIFECYCLE_SCHEMA == "hedron.htmx-lifecycle/1"
    attrs = lifecycle_attributes()
    assert attrs == {
        "data-hedron-announcement": "polite",
        "data-hedron-concurrency": "latest",
        "data-hedron-focus": "none",
        "data-hedron-state-host": "true",
    }


def check_theme() -> None:
    from hedron_core import default_theme, presentation_contract, presentation_tokens

    theme = default_theme().extend("release-064", tokens={"space.4": "1.125rem"})
    first = presentation_contract(theme).to_dict()
    second = presentation_contract(theme).to_dict()
    assert first == second
    assert first["tokens"]["space.4"] == "1.125rem"
    assert first["digest"]
    assert presentation_tokens(theme)["motion.standard"] == "150ms"


def check_manifest() -> None:
    from hedron_core import component_presentation_manifest

    manifest = component_presentation_manifest()
    expected = {"AppShell", "Card", "FormField", "SplitView", "ProcessFlow"}
    assert set(manifest["parts_and_states"]) == expected
    for entry in manifest["parts_and_states"].values():
        assert entry["parts"]
        assert entry["states"]
    assert manifest["digest"] == component_presentation_manifest()["digest"]


def check_typogeom() -> None:
    from hedron_core import presentation_tokens

    tokens = presentation_tokens()
    required = {
        "type.display.size",
        "type.heading.size",
        "type.body.size",
        "space.1",
        "space.6",
        "geometry.control-height",
        "geometry.hit-target",
        "geometry.radius-md",
    }
    assert required <= tokens.keys()
    assert all(value and "url(" not in value for value in tokens.values())


def check_responsive() -> None:
    from hedron_core import ResponsiveCondition, ScopedStyleRecipe, compile_scoped_styles

    recipe = ScopedStyleRecipe(
        component="ReleaseCard",
        part="body",
        declarations={"padding-inline": "var(--hedron-space-4)"},
        conditions=(
            ResponsiveCondition("viewport", "sm"),
            ResponsiveCondition("container", "md"),
            ResponsiveCondition("direction", "rtl"),
            ResponsiveCondition("writing-mode", "vertical-rl"),
            ResponsiveCondition("accessibility", "print"),
        ),
    )
    css = compile_scoped_styles((recipe,)).css
    for marker in (
        "@media (min-width: 40rem)",
        "@container (min-width: 40rem)",
        '[dir="rtl"]',
        '[style*="writing-mode: vertical-rl"]',
        "@media print",
    ):
        assert marker in css


def check_custom() -> None:
    from hedron_core import PresentationError, ScopedStyleRecipe, compile_scoped_styles

    recipe = ScopedStyleRecipe(
        component="ReleaseCard",
        part="body",
        states=("selected",),
        declarations={"color": "var(--hedron-color-accent)"},
        layer="overrides",
    )
    first = compile_scoped_styles((recipe,))
    second = compile_scoped_styles((recipe,))
    assert first.css == second.css
    assert first.digest == second.digest
    assert "@layer overrides" in first.css
    for value in ("url(https://example.test)", "red; } body {", "javascript:alert(1)"):
        try:
            ScopedStyleRecipe(component="ReleaseCard", part="body", declarations={"color": value})
        except PresentationError:
            pass
        else:
            fail(f"unsafe CSS value was accepted: {value}")


def check_asset() -> None:
    from hedron_core.htmx_extensions import known_extensions

    ext = next(item for item in known_extensions() if item.public_id == "hedron")
    path = ROOT / "packages" / "hedron" / "src" / "hedron" / "static" / "ext" / "hedron.js"
    assert path.is_file()
    digest = "sha256-" + hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == ext.digest
    text = path.read_text(encoding="utf-8").lower()
    assert 'defineextension("hedron"' in text
    assert not re.search(r"\b(eval|fetch|xmlhttprequest|websocket|function\s+constructor)\b", text)


def check_state() -> None:
    from hedron_core import (
        HedronLifecycleEvent,
        LifecycleFact,
        LifecycleState,
        transition_lifecycle,
    )

    pending = transition_lifecycle(
        LifecycleFact(LifecycleState.IDLE, generation=4, operation_id="release-4"),
        HedronLifecycleEvent.REQUEST,
        generation=5,
        operation_id="release-5",
    )
    assert pending.state is LifecycleState.PENDING
    assert (
        transition_lifecycle(pending, HedronLifecycleEvent.SUCCESS, generation=4).state
        is LifecycleState.STALE
    )
    assert (
        transition_lifecycle(pending, HedronLifecycleEvent.SUCCESS, generation=5).state
        is LifecycleState.SUCCESS
    )


def check_a11y() -> None:
    from hedron_core import lifecycle_attributes

    attrs = lifecycle_attributes(focus="validation", announcement="assertive")
    assert attrs["data-hedron-focus"] == "validation"
    assert attrs["data-hedron-announcement"] == "assertive"
    js = (ROOT / "packages/hedron/src/hedron/static/ext/hedron.js").read_text(encoding="utf-8")
    assert "aria-busy" in js
    assert "data-hedron-state" in js


def check_integrate() -> None:
    from hedron_core.htmx_extensions import compile_extension_plan, parse_htmx_extensions
    from hedron_core.page_assets import inject_htmx_extensions

    plan = compile_extension_plan(declaration=parse_htmx_extensions(("hedron",)))
    html = '<html><head><script src="/hedron-static/htmx.min.js"></script></head></html>'
    rendered = inject_htmx_extensions(html, plan=plan)
    assert 'hx-ext="hedron"' in rendered
    assert rendered.index("htmx.min.js") < rendered.index("/hedron-static/ext/hedron.js")


def check_csp() -> None:
    text = (
        ROOT / "packages/hedron/src/hedron/static/ext/hedron.js"
    ).read_text(encoding="utf-8").lower()
    for forbidden in (
        "eval(",
        "new function",
        "innerhtml",
        "document.write",
        "fetch(",
        "xmlhttprequest",
    ):
        assert forbidden not in text, forbidden


def check_security() -> None:
    check_custom()
    check_asset()


def check_upgrade() -> None:
    from hedron_core.htmx_extensions import ExtensionPlan
    from hedron_core.page_assets import inject_htmx_extensions

    html = '<html><head><script src="/hedron-static/htmx.min.js"></script></head></html>'
    plan = ExtensionPlan(ids=(), source="opt-out", inject=False)
    assert inject_htmx_extensions(html, plan=plan) == html


def check_docs() -> None:
    commands = [
        [sys.executable, str(ROOT / "scripts/check_docs_train_ssot.py")],
        [sys.executable, str(ROOT / "scripts/check_package_docs_inventory.py")],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


def check_pkg() -> None:
    release = tomllib.loads((ROOT / "docs/release.toml").read_text(encoding="utf-8"))["release"]
    assert release["development_version"] == "0.64.0"
    assert release["registry_status"] in {"deferred", "uploaded"}
    if release["registry_status"] == "uploaded":
        assert release["pypi_version"] == release["development_version"]
    package_files = [ROOT / "pyproject.toml", *sorted((ROOT / "packages").glob("*/pyproject.toml"))]
    coordinated = {
        "hedron",
        "hedron-core",
        "hedron-conformance",
        "hedron-data",
        "hedron-django",
        "hedron-elements",
        "hedron-explorer",
        "hedron-extras",
        "hedron-flask",
        "hedron-jinja",
        "hedron-posit",
        "hedron-workbench",
    }
    for path in package_files:
        project = tomllib.loads(path.read_text(encoding="utf-8")).get("project", {})
        if project.get("name") in coordinated:
            assert project.get("version") == "0.64.0", path


CHECKS = {
    "contract": check_contract,
    "theme": check_theme,
    "manifest": check_manifest,
    "typogeom": check_typogeom,
    "responsive": check_responsive,
    "custom": check_custom,
    "asset": check_asset,
    "state": check_state,
    "a11y": check_a11y,
    "integrate": check_integrate,
    "csp": check_csp,
    "security": check_security,
    "upgrade": check_upgrade,
    "docs": check_docs,
    "pkg": check_pkg,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", choices=sorted(GATES))
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    selected = [args.gate] if args.gate else list(GATES)
    for gate in selected:
        CHECKS[GATES[gate]]()
        print(f"ok: {gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
