"""SUPPLY-040 in-repo @hedron/elements mirror identity."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NPM = ROOT / "packages" / "hedron-elements" / "npm"
STATIC = ROOT / "packages" / "hedron-elements" / "src" / "hedron_elements" / "static"


def test_npm_package_is_modules_and_types_only() -> None:
    package = json.loads((NPM / "package.json").read_text(encoding="utf-8"))
    assert package["name"] == "@hedron/elements"
    assert "react" not in package.get("dependencies", {})
    assert "react" not in package.get("peerDependencies", {})
    assert (NPM / "modules" / "hedron-bridge.mjs").is_file()
    assert (NPM / "modules" / "hedron-bridge.d.ts").is_file()
    assert (NPM / "modules" / "hedron-example.mjs").is_file()
    assert (NPM / "modules" / "hedron-example.d.ts").is_file()


def test_wheel_static_and_npm_modules_content_identity() -> None:
    for name in ("hedron-bridge.mjs", "hedron-example.mjs"):
        wheel = (STATIC / name).read_bytes()
        mirror = (NPM / "modules" / name).read_bytes()
        assert wheel == mirror
