"""DIFF-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import admit_fixtures, run_kit


def test_diff_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DIFF-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_python_reference_self_consistent() -> None:
    fixtures = admit_fixtures("core-render", include_subdirectories=False)
    first = run_kit(fixtures)
    second = run_kit(fixtures)
    assert first.ok and second.ok
    assert [(r.fixture_id, r.passed) for r in first.results] == [
        (r.fixture_id, r.passed) for r in second.results
    ]


def test_node_java_bins_optional_present() -> None:
    # Optional differential consumers; assert packaging seams exist (execution optional).
    assert Path("packages/hedron-runtime-node/bin/run-conformance.mjs").is_file()
    assert Path("packages/hedron-runtime-java/scripts/run-conformance.sh").is_file()
