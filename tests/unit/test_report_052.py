"""REPORT-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    build_result_envelope,
    load_bundled_fixtures,
    offline_bundle_manifest,
    run_kit,
    suite_digest,
    to_junit,
    to_sarif,
    verify_envelope_digest,
)


def test_report_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["REPORT-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_result_envelope_sha256_and_hmac() -> None:
    report = run_kit()
    digest = suite_digest(load_bundled_fixtures())
    envelope = build_result_envelope(report, manifest_digest=digest)
    assert envelope["ok"] is True
    assert envelope["provenance"]["algorithm"] == "sha256"
    assert verify_envelope_digest(envelope)

    keyed = build_result_envelope(report, manifest_digest=digest, key=b"test-key")
    assert keyed["provenance"]["algorithm"] == "hmac-sha256"
    assert verify_envelope_digest(keyed, key=b"test-key")
    assert not verify_envelope_digest(keyed, key=b"wrong")


def test_offline_bundle_manifest_deterministic() -> None:
    report = run_kit()
    digest = suite_digest(load_bundled_fixtures())
    envelope = build_result_envelope(report, manifest_digest=digest)
    junit = to_junit(report)
    sarif = to_sarif(report)
    first = offline_bundle_manifest(envelope=envelope, junit_xml=junit, sarif=sarif)
    second = offline_bundle_manifest(envelope=envelope, junit_xml=junit, sarif=sarif)
    assert first == second
    assert first["offline"] is True
    assert "junit.xml" in first["files"]
