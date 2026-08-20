"""DOCS-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

PACKET_FILES = (
    Path("docs/acceptance/release-gate-0.53.toml"),
    Path("docs/acceptance/application-dx-inventory-053.toml"),
    Path("docs/acceptance/application-assets-053.toml"),
    Path("docs/acceptance/application-contracts-053.toml"),
    Path("docs/acceptance/application-tooling-053.toml"),
    Path("docs/acceptance/RELEASE_0_53.md"),
    Path("docs/acceptance/upgrade-fixtures-053.md"),
    Path("docs/implementation/APPLICATION_DX_053.md"),
    Path("docs/api/APPLICATION_DX.md"),
    Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md"),
)


def test_docs_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DOCS-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_packet_files_and_api_markers() -> None:
    for path in PACKET_FILES:
        assert path.is_file(), path
    rfc = Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").read_text(encoding="utf-8")
    assert "**Status:** Accepted" in rfc
    impl = Path("docs/implementation/APPLICATION_DX_053.md").read_text(encoding="utf-8")
    assert "Stage 1 Implemented" in impl
    api = Path("docs/api/APPLICATION_DX.md").read_text(encoding="utf-8")
    for marker in (
        "compile_application_asset_plan",
        "export_routes_document",
        "OperationWorkflow",
        "generate_interaction_tests",
        "run_visual_conformance",
        "discover_public_api",
        "diagnose_installed_fleet",
    ):
        assert marker in api, marker
    assert "Stage 1 Implemented" in api
