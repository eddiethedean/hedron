"""FIXTURE-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    Capability,
    ConformanceFixture,
    ExpectedOutcome,
    FixtureInput,
    compile_suite,
    load_bundled_fixtures,
)


def test_fixture_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["FIXTURE-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_compile_bundled_corpus_ok() -> None:
    report = compile_suite(load_bundled_fixtures())
    assert report.ok, report.errors
    assert report.fixture_count >= 1
    assert len(report.fixture_ids) == report.fixture_count


def test_compile_rejects_duplicate_ids() -> None:
    base = load_bundled_fixtures()[0]
    report = compile_suite([base, base])
    assert not report.ok
    assert any("duplicate" in err for err in report.errors)


def test_compile_rejects_contradictory_expect_error_html() -> None:
    bad = ConformanceFixture(
        id="bad-contradiction",
        capability=Capability.DIAGNOSTICS,
        input=FixtureInput(kind="diagnostic", expect_error=True),
        expected=ExpectedOutcome(html="<p>nope</p>", diagnostic_code="HED-SEC-0002"),
    )
    report = compile_suite([bad])
    assert not report.ok
    assert any("contradictory" in err for err in report.errors)


def test_compile_rejects_unknown_contract_version() -> None:
    bad = ConformanceFixture(
        id="bad-contract",
        capability=Capability.ESCAPING,
        contract_version="hedron-portable-99",
        input=FixtureInput(kind="escape_text", text="a"),
        expected=ExpectedOutcome(escaped_text="a"),
    )
    report = compile_suite([bad])
    assert not report.ok
    assert any("contract_version" in err for err in report.errors)
