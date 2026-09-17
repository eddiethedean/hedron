"""Read-only Theme Lab data backed by the shared theme resolver."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from hedron_core.theme import (
    FOLIO_ACCENTS,
    builtin_themes,
    ensure_builtin_themes_registered,
    folio_theme,
)
from hedron_core.theme_contract import theme_contract_report
from hedron_core.theme_platform import (
    ThemeBuilder,
    conformance_report,
    diff_theme_specs,
    explain_theme_spec,
    validate_theme_spec,
)


def _theme_specs(accent: str) -> dict[str, Any]:
    """Resolve only registered built-ins; package code is never imported here."""
    ensure_builtin_themes_registered()
    return {
        theme.name: ThemeBuilder.from_theme(
            folio_theme(accent=accent) if theme.name == "folio" else theme
        ).build_spec()
        for theme in builtin_themes()
    }


def _selected_names(names: Iterable[str] | None, available: dict[str, Any]) -> list[str]:
    requested = tuple(
        dict.fromkeys(
            "classic" if name == "default" else str(name) for name in (names or ("folio", "aurora"))
        )
    )
    selected = [name for name in requested if name in available]
    return selected or ["folio"]


def theme_lab_report(
    *, left: str = "folio", right: str = "aurora", profile: str = "core", accent: str = "green"
) -> dict[str, Any]:
    """Return an exportable, deterministic report for the Explorer Theme Lab.

    The report contains no request-specific mutation and is safe to render as
    JSON or HTML.  Its exercise descriptions are intentionally declarative;
    the browser test harness remains the authority for computed behavior.
    """
    accent = accent if accent in FOLIO_ACCENTS else "green"
    available = _theme_specs(accent)
    left = "classic" if left == "default" else left if left in available else "folio"
    right = "classic" if right == "default" else right if right in available else "aurora"
    names = _selected_names((left, right), available)
    themes: list[dict[str, Any]] = []
    for name in names:
        spec = available[name]
        validation = validate_theme_spec(spec, profile=profile, strict=False)
        contract = theme_contract_report(spec)
        themes.append(
            {
                "name": name,
                "accent": accent if name == "folio" else None,
                "spec": explain_theme_spec(spec),
                "validation": validation.to_dict(),
                "conformance": conformance_report(spec, profile=profile),
                "resolution": contract["theme"],
                "component_manifest_digest": contract["component_manifest"]["digest"],
                "state_matrix": {
                    "count": contract["state_matrix"]["count"],
                    "digest": contract["state_matrix"]["digest"],
                },
                "modes": ["light", "dark", "more-contrast", "forced-colors"],
            }
        )

    left_spec = available[names[0]]
    right_spec = available[names[1]] if len(names) > 1 else left_spec
    warnings: list[dict[str, str]] = []
    for name in names:
        spec = available[name]
        for token, value in spec.tokens.items():
            if isinstance(value, str) and ("color(" in value or "var(" in value):
                warnings.append(
                    {
                        "theme": name,
                        "code": "THEME-LAB-FALLBACK",
                        "token": token,
                        "message": "Token requires a canonical sRGB fallback before packaging.",
                    }
                )

    return {
        "schema": "hedron.theme-lab/1",
        "read_only": True,
        "available_themes": sorted(available),
        "available_accents": list(FOLIO_ACCENTS),
        "selection": {
            "left": left,
            "right": right,
            "accent": accent,
        },
        "profile": profile,
        "themes": themes,
        "diff": diff_theme_specs(left_spec, right_spec),
        "warnings": warnings,
        "exercises": [
            {
                "id": "keyboard-focus",
                "label": "Keyboard and focus",
                "assertions": [
                    "tab reaches the picker and every interactive control",
                    "focus is visible",
                ],
            },
            {
                "id": "zoom-reflow",
                "label": "200% and 400% zoom",
                "assertions": [
                    "content reflows without horizontal loss",
                    "brand copy remains readable",
                ],
            },
            {
                "id": "state-modes",
                "label": "States and accessibility modes",
                "assertions": [
                    "light/dark are comparable",
                    "forced-colors and more-contrast retain focus and state cues",
                ],
            },
        ],
    }
