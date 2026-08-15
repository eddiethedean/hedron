"""SUPPLY-042: wheel/npm identity, license, SBOM, rollback notes."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NPM = ROOT / "packages" / "hedron-elements" / "npm"
STATIC = ROOT / "packages" / "hedron-elements" / "src" / "hedron_elements" / "static"
SUPPLY = ROOT / "docs" / "acceptance" / "fleet-supply-042"

SUPPORTED_MODULES = (
    "hedron-example.mjs",
    "hedron-field-text.mjs",
    "hedron-field-choice.mjs",
    "hedron-field-file.mjs",
    "hedron-disclosure.mjs",
    "hedron-dialog.mjs",
    "hedron-action-async.mjs",
)


def test_npm_mirror_is_modules_and_types_only() -> None:
    package = json.loads((NPM / "package.json").read_text(encoding="utf-8"))
    assert package["name"] == "@hedron/elements"
    assert "react" not in package.get("dependencies", {})
    assert "react" not in package.get("peerDependencies", {})
    assert "react" not in package.get("devDependencies", {})


def test_supported_tag_modules_match_wheel_and_npm() -> None:
    for name in SUPPORTED_MODULES:
        wheel = (STATIC / name).read_bytes()
        mirror = (NPM / "modules" / name).read_bytes()
        assert wheel == mirror, name
        stub = NPM / "modules" / name.replace(".mjs", ".d.ts")
        assert stub.is_file(), f"missing typed stub for {name}"


def test_supply_packet_artifacts_exist() -> None:
    required_headings = {
        "LICENSE_INVENTORY.md": ("license", "hedron-elements"),
        "SBOM_NOTES.md": ("sbom", "hedron-elements"),
        "OFFLINE_INSTALL.md": ("offline", "cdn refusal"),
        "ROLLBACK.md": ("rollback", "hedron-elements"),
    }
    for name, needles in required_headings.items():
        path = SUPPLY / name
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8").lower()
        for needle in needles:
            assert needle in text, f"{name} missing {needle!r}"
