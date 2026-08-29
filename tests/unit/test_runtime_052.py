"""RUNTIME-052 evidence."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from hedron_conformance import run_kit


def _runtime_versions() -> tuple[str, str]:
    runtimes = tomllib.loads(Path("docs/release.toml").read_text(encoding="utf-8"))["runtimes"]
    return str(runtimes["node_version"]), str(runtimes["java_version"])


def test_runtime_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["RUNTIME-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_python_kit_runs_bundled_corpus() -> None:
    report = run_kit()
    assert report.ok, [f.detail for f in report.failures()]
    assert report.results


def test_node_runtime_package_present() -> None:
    node_version, _java_version = _runtime_versions()
    root = Path("packages/hedron-runtime-node")
    data = json.loads((root / "package.json").read_text(encoding="utf-8"))
    assert data["version"] == node_version
    assert (root / "bin" / "run-conformance.mjs").is_file()
    assert (root / "lib" / "runtime.mjs").is_file()


def test_java_runtime_package_present() -> None:
    _node_version, java_version = _runtime_versions()
    root = Path("packages/hedron-runtime-java")
    pom = (root / "pom.xml").read_text(encoding="utf-8")
    assert f"<version>{java_version}</version>" in pom
    assert (root / "scripts" / "run-conformance.sh").is_file()
    assert (
        root / "src" / "main" / "java" / "io" / "hedron" / "runtime" / "ConformanceRuntime.java"
    ).is_file()
