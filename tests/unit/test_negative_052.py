"""NEGATIVE-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import compile_suite, load_bundled_fixtures, run_kit


def test_negative_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["NEGATIVE-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_negative_boundary_fixtures_loaded() -> None:
    fixtures = load_bundled_fixtures()
    negatives = [fx for fx in fixtures if fx.negative]
    ids = {fx.id for fx in negatives}
    assert "neg-boundary-empty-escape" in ids
    assert "neg-adversarial-nul-attr" in ids
    assert "neg-expect-error-diagnostic" in ids
    assert Path(
        "packages/hedron-conformance/src/hedron_conformance/fixtures/negative_boundary_052.json"
    ).is_file()


def test_negative_fixtures_compile_and_run() -> None:
    negatives = [fx for fx in load_bundled_fixtures() if fx.id.startswith("neg-")]
    assert negatives
    compiled = compile_suite(negatives)
    assert compiled.ok, compiled.errors
    report = run_kit(negatives)
    assert report.ok, report.failures()
