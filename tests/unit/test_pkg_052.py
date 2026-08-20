"""PKG-052 evidence."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path


def _living_tip() -> str:
    release = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["release"]
    return str(release["published_version"])


def test_pkg_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PKG-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_conformance_package_structure() -> None:
    tip = _living_tip()
    root = Path("packages/hedron-conformance")
    assert (root / "pyproject.toml").is_file()
    assert (root / "src" / "hedron_conformance" / "profiles.py").is_file()
    assert (root / "src" / "hedron_conformance" / "compile.py").is_file()
    assert (root / "src" / "hedron_conformance" / "report.py").is_file()
    assert (root / "src" / "hedron_conformance" / "sandbox.py").is_file()
    meta = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert meta["project"]["version"] == tip


def test_node_java_versions_bumped() -> None:
    tip = _living_tip()
    node = json.loads(Path("packages/hedron-runtime-node/package.json").read_text(encoding="utf-8"))
    assert node["version"] == tip
    pom = Path("packages/hedron-runtime-java/pom.xml").read_text(encoding="utf-8")
    assert f"<version>{tip}</version>" in pom
