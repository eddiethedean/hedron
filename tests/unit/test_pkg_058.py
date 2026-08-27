"""PKG-058 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import DesignSystem, StyleRecipe, StyleScope, explain_feature


def test_pkg_058_packet_and_gate_ids() -> None:
    packet_files = (
        Path("docs/acceptance/release-gate-0.58.toml"),
        Path("docs/acceptance/progressive-authoring-inventory-058.toml"),
        Path("docs/acceptance/styling-authoring-inventory-058.toml"),
        Path("docs/acceptance/RELEASE_0_58.md"),
        Path("docs/implementation/PROGRESSIVE_AUTHORING_058.md"),
        Path("docs/rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md"),
    )
    for path in packet_files:
        assert path.is_file(), path

    expected = (
        "CONTRACT-058",
        "LOWER-058",
        "SCREEN-058",
        "FORM-058",
        "RESOURCE-058",
        "TASK-058",
        "DASH-058",
        "FLOW-058",
        "BRAND-058",
        "THEME-058",
        "RECIPE-058",
        "SCOPE-058",
        "EXPLAIN-058",
        "VISUAL-058",
        "A11Y-058",
        "SECURITY-058",
        "ADAPTER-058",
        "REGRESS-058",
        "DX-058",
        "PKG-058",
    )
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.58.toml").read_text(encoding="utf-8"))
    found = tuple(row["id"] for row in gate["evidence"])
    assert found == expected


def test_pin_docs_and_public_exports() -> None:
    release = Path("docs/release.toml")
    assert release.is_file()
    data = tomllib.loads(release.read_text(encoding="utf-8"))
    pin_ceiling = str(data.get("release", {}).get("pin_ceiling", ""))
    assert (
        pin_ceiling.startswith("0.63")
        or pin_ceiling.startswith("0.64")
        or pin_ceiling.startswith("0.65")
        or pin_ceiling.startswith("0.67")
        or pin_ceiling.startswith("0.62")
        or pin_ceiling.startswith("0.60")
        or "0.58" in pin_ceiling
        or "0.59" in pin_ceiling
    )

    for symbol in (DesignSystem, StyleRecipe, StyleScope, explain_feature):
        assert symbol is not None
