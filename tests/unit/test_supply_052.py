"""SUPPLY-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_supply_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SUPPLY-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_runtime_license_files() -> None:
    assert Path("packages/hedron-runtime-node/LICENSE").is_file()
    assert Path("packages/hedron-runtime-java/LICENSE").is_file()
    assert Path("packages/hedron-conformance/LICENSE").is_file()
    for path in (
        Path("packages/hedron-runtime-node/LICENSE"),
        Path("packages/hedron-runtime-java/LICENSE"),
        Path("packages/hedron-conformance/LICENSE"),
    ):
        text = path.read_text(encoding="utf-8")
        assert "MIT" in text or "Permission is hereby granted" in text
