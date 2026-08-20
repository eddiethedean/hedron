"""CI-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import run_kit, to_junit, to_sarif


def test_ci_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["CI-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_junit_xml_contains_testsuite() -> None:
    report = run_kit()
    xml = to_junit(report)
    assert "<testsuite" in xml
    assert 'name="hedron-conformance"' in xml
    assert report.results[0].fixture_id in xml


def test_sarif_document_shape() -> None:
    report = run_kit()
    doc = to_sarif(report)
    assert doc["version"] == "2.1.0"
    assert doc["runs"][0]["tool"]["driver"]["name"] == "hedron-conformance"
    assert doc["runs"][0]["properties"]["ok"] is True
    assert isinstance(doc["runs"][0]["results"], list)
