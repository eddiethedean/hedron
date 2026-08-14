"""Public contracts for third-party Hedron element authors."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedron_core.diagnostics import error

AUTHOR_SURFACES = (
    "element_metadata",
    "events",
    "lifecycle",
    "fallback",
    "assets",
    "a11y",
    "diagnostics",
)

REQUIRED_ELEMENT_META_KEYS = (
    "tag_name",
    "abi_version",
    "module_asset_id",
    "logical_id",
    "events",
    "lifecycle",
    "fallback",
    "a11y_contract",
    "attributes",
)

REQUIRED_DIAGNOSTICS_PREFIX_GUIDANCE = (
    "Use a distribution-owned HED-<PLUGIN>- diagnostic prefix; "
    "do not claim Hedron's built-in HED-ELEMENT- codes."
)

__all__ = [
    "AUTHOR_SURFACES",
    "REQUIRED_DIAGNOSTICS_PREFIX_GUIDANCE",
    "REQUIRED_ELEMENT_META_KEYS",
    "diagnostics_prefix_guidance",
    "packaging_checklist",
    "validate_element_author_meta",
]


def validate_element_author_meta(meta: dict[str, Any]) -> dict[str, Any]:
    """Validate the minimum portable element-author metadata contract."""
    missing = [key for key in REQUIRED_ELEMENT_META_KEYS if key not in meta]
    if missing:
        raise error(
            "HED-ELEMENT-AUTHOR-0001",
            title="Incomplete element author metadata",
            explanation=f"Required metadata keys are missing: {', '.join(missing)}.",
            remediation="Declare every required author metadata surface before registration.",
        )
    if not isinstance(meta["a11y_contract"], Mapping):
        raise error(
            "HED-ELEMENT-AUTHOR-0002",
            title="Invalid accessibility contract",
            explanation="a11y_contract must be a mapping (an empty mapping is allowed).",
            remediation="Set a11y_contract to a JSON-compatible mapping.",
        )
    tag_name = meta["tag_name"]
    if not isinstance(tag_name, str) or "-" not in tag_name:
        raise error(
            "HED-ELEMENT-AUTHOR-0002",
            title="Invalid authored element tag",
            explanation=f"tag_name {tag_name!r} must be a hyphenated custom-element name.",
            remediation="Use a distribution-owned tag such as ext-example.",
        )
    return dict(meta)


def packaging_checklist() -> list[str]:
    """Return the required files and public-API packaging rules."""
    return [
        "pyproject.toml with hedron-core and hedron-elements compatibility pins",
        "hedron.plugins entry point",
        "src/<package>/plugin.py using PluginContext and public hedron_core exports only",
        "src/<package>/static/<tag>.mjs",
        "src/<package>/static/<tag>.css",
        "tests/test_element.py",
        "examples/README.md",
        "no private registry imports or private Hedron APIs",
    ]


def diagnostics_prefix_guidance() -> str:
    """Return the required diagnostic namespace guidance for plugins."""
    return REQUIRED_DIAGNOSTICS_PREFIX_GUIDANCE
