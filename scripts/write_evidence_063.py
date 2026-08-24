"""Generate deterministic local evidence projections for the phase 0.63 packet."""

from __future__ import annotations

import json
from pathlib import Path

from hedron import (
    build_state_matrix,
    component_contract_manifest,
    element_metadata_manifest,
    package_identity_manifest,
    theme_contract_report,
)
from hedron.migrate.react import analyze_react_source
from hedron.phase063_checks import analyze_project
from hedron_core import (
    ActionTrace,
    compare_style_bundle_sizes,
    compile_style_bundle,
    default_theme,
    encode_interaction_trace,
    profile_interaction_trace,
    react_island_recipe,
    resolve_visualization_theme,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "acceptance" / "evidence-063"


def _write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stylesheet = (
        ROOT / "packages/hedron-core/src/hedron_core/static/hedron-default.css"
    ).read_text(encoding="utf-8")
    theme_report = theme_contract_report(default_theme(), css=stylesheet)
    _write(
        "theme-contract.json",
        {
            "schema": theme_report["schema"],
            "digest": theme_report["digest"],
            "theme": {
                "schema": theme_report["theme"]["schema"],
                "name": theme_report["theme"]["name"],
                "fingerprint": theme_report["theme"]["fingerprint"],
                "modes": theme_report["theme"]["modes"],
                "variants": theme_report["theme"]["variants"],
                "accessibility_modes": theme_report["theme"]["accessibility_modes"],
                "token_count": len(theme_report["theme"]["tokens"]),
                "derived_token_count": len(theme_report["theme"]["derived"]),
                "recipe_count": len(theme_report["theme"]["recipes"]),
            },
            "stylesheet": theme_report["stylesheet"],
            "conformance": {
                "schema": theme_report["conformance"]["schema"],
                "ok": theme_report["conformance"]["ok"],
                "fingerprint": theme_report["conformance"]["fingerprint"],
                "inventory_digest": theme_report["conformance"]["inventory_digest"],
            },
        },
    )
    component_manifest = component_contract_manifest()
    _write(
        "component-manifest.json",
        {
            "schema": component_manifest["schema"],
            "version": component_manifest["version"],
            "digest": component_manifest["digest"],
            "component_count": len(component_manifest["components"]),
            "logical_ids": [item["logical_id"] for item in component_manifest["components"]],
        },
    )
    metadata = element_metadata_manifest()
    _write(
        "element-metadata.json",
        {
            "schema": metadata["schema"],
            "version": metadata["version"],
            "digest": metadata["digest"],
            "element_count": len(metadata["elements"]),
            "logical_ids": [item["logical_id"] for item in metadata["elements"]],
        },
    )
    identity = package_identity_manifest()
    _write(
        "package-identity.json",
        {
            "schema": identity["schema"],
            "runtime": identity["runtime"],
            "distributions": identity["distributions"],
            "component_manifest_digest": identity["component_manifest_digest"],
            "metadata_digest": identity["metadata_digest"],
            "digest": identity["digest"],
            "components": identity["components"],
        },
    )
    accessibility_modes = (
        "none",
        "forced-colors",
        "high-contrast",
        "reduced-motion",
        "reduced-transparency",
        "print",
    )
    state_matrix = build_state_matrix(accessibility_modes=accessibility_modes)
    _write(
        "state-matrix.json",
        {
            "schema": state_matrix.to_dict()["schema"],
            "version": 1,
            "count": len(state_matrix.entries),
            "digest": state_matrix.digest,
            "sample": [entry.to_dict() for entry in state_matrix.entries[:3]],
            "tail": [entry.to_dict() for entry in state_matrix.entries[-3:]],
        },
    )
    trace = ActionTrace().append("pending", facts={"component": "Button", "action": "save"})
    _write("interaction-profile.json", profile_interaction_trace(encode_interaction_trace(trace)))
    _write("react-migration.json", analyze_react_source(ROOT / "tests/fixtures/phase063/react"))
    _write("interaction-checks.json", analyze_project(ROOT / "tests/fixtures/phase063/project"))
    _write(
        "style-bundles.json",
        {
            "schema": "hedron.style-bundles/1",
            "manifest": [
                compile_style_bundle(components=(component,)).to_dict()
                for component in (
                    "app-shell",
                    "button",
                    "card",
                    "chart",
                    "dialog",
                    "form",
                    "popover",
                    "surface",
                )
            ],
            "comparison": compare_style_bundle_sizes(),
        },
    )
    _write("visualization-theme.json", resolve_visualization_theme(default_theme()).to_dict())
    _write("react-island.json", react_island_recipe().to_dict())
    _write(
        "runtime-baseline.json",
        {
            "schema": "hedron.phase063-baseline/1",
            "theme_css_bytes": len(stylesheet.encode("utf-8")),
            "component_manifest_entries": len(component_contract_manifest()["components"]),
            "element_metadata_entries": len(element_metadata_manifest()["elements"]),
            "state_matrix_cases": len(state_matrix.entries),
            "runtime": "python-no-node",
        },
    )


if __name__ == "__main__":
    main()
