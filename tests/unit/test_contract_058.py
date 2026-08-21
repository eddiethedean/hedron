"""CONTRACT-058 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import codes


def test_contract_058_packet_files_exist() -> None:
    root = Path("docs/acceptance")
    for name in (
        "release-gate-0.58.toml",
        "progressive-authoring-inventory-058.toml",
        "styling-authoring-inventory-058.toml",
        "progressive-lowering-058.toml",
        "styling-lowering-058.toml",
        "feature-explanation-058.toml",
        "design-system-schema-058.toml",
        "style-recipe-catalog-058.toml",
        "progressive-tracking-058.toml",
        "RELEASE_0_58.md",
        "upgrade-fixtures-058.md",
    ):
        assert (root / name).is_file(), name
    assert Path("docs/implementation/PROGRESSIVE_AUTHORING_058.md").is_file()
    assert Path("docs/rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md").is_file()


def test_inventories_list_frozen_symbols() -> None:
    progressive = tomllib.loads(
        Path("docs/acceptance/progressive-authoring-inventory-058.toml").read_text(encoding="utf-8")
    )
    styling = tomllib.loads(
        Path("docs/acceptance/styling-authoring-inventory-058.toml").read_text(encoding="utf-8")
    )
    progressive_names = {row["name"] for row in progressive["symbol"]}
    styling_names = {row["name"] for row in styling["symbol"]}
    for name in (
        "Hedron.screen",
        "Hedron.form_command",
        "DataWorkspace.with_screen",
        "TaskFlow",
        "DashboardWorkspace",
        "SessionAuthFlow",
        "UploadFlow",
    ):
        assert name in progressive_names, name
    for name in ("DesignSystem", "StyleRecipe.control", "StyleScope"):
        assert name in styling_names, name


def test_rfc_0085_accepted_markers() -> None:
    rfc = Path("docs/rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md").read_text(encoding="utf-8")
    decisions = Path("docs/DECISIONS.md").read_text(encoding="utf-8")
    assert "**Status:** Accepted" in rfc
    assert "| D-101 | Accepted |" in decisions
    assert "| D-102 | Accepted |" in decisions
    assert "| D-105 | Accepted |" in decisions


def test_diagnostic_codes_present() -> None:
    for attr, value in (
        ("HED_SCREEN_0001", "HED-SCREEN-0001"),
        ("HED_FORMCMD_0001", "HED-FORMCMD-0001"),
        ("HED_FEATURE_0001", "HED-FEATURE-0001"),
        ("HED_BRAND_0001", "HED-BRAND-0001"),
        ("HED_RECIPE_0001", "HED-RECIPE-0001"),
        ("HED_STYLE_SCOPE_0001", "HED-STYLE-SCOPE-0001"),
        ("HED_DESIGN_0001", "HED-DESIGN-0001"),
    ):
        assert getattr(codes, attr) == value
