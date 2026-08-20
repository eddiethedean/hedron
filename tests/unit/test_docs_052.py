"""DOCS-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

PACKET_FILES = (
    Path("docs/acceptance/release-gate-0.52.toml"),
    Path("docs/acceptance/conformance-capability-inventory-052.toml"),
    Path("docs/acceptance/conformance-profile-052.toml"),
    Path("docs/acceptance/posit-lifecycle-052.toml"),
    Path("docs/acceptance/RELEASE_0_52.md"),
    Path("docs/acceptance/upgrade-fixtures-052.md"),
    Path("docs/implementation/CONFORMANCE_052.md"),
    Path("docs/implementation/POSIT_LIFECYCLE_052.md"),
    Path("docs/api/CONFORMANCE.md"),
    Path("docs/api/POSIT_LIFECYCLE.md"),
    Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md"),
)


def test_docs_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DOCS-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_packet_files_and_rfc_markers() -> None:
    for path in PACKET_FILES:
        assert path.is_file(), path
    rfc = Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").read_text(
        encoding="utf-8"
    )
    assert "Conformance authority" in rfc
    assert "hedron-portable-1" in rfc
    assert "**Status:** Accepted" in rfc
    impl = Path("docs/implementation/CONFORMANCE_052.md").read_text(encoding="utf-8")
    assert "Stage 1 Implemented" in impl
    api = Path("docs/api/CONFORMANCE.md").read_text(encoding="utf-8")
    assert "load_profile_registry" in api
    assert "compile_suite" in api
    assert "build_result_envelope" in api
    assert "SandboxPolicy" in api
