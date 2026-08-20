"""PROFILE-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    PROFILE_IDS,
    admit_fixtures,
    load_profile_registry,
    profile_suite_digest,
    suite_digests,
)


def test_profile_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PROFILE-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_profile_registry_matches_lock() -> None:
    lock = tomllib.loads(
        Path("docs/acceptance/conformance-profile-052.toml").read_text(encoding="utf-8")
    )
    lock_ids = tuple(row["id"] for row in lock["profile"])
    registry = load_profile_registry()
    assert registry.ids() == lock_ids == PROFILE_IDS
    assert registry.seed_contract_version == "hedron-portable-1"
    assert lock["replace_seed_without_negotiation"] is False


def test_admit_fixtures_filters_by_capability() -> None:
    core = admit_fixtures("core-render", include_subdirectories=False)
    assert core
    assert all(
        fx.capability.value in {"rendering", "escaping", "identity", "accessibility"} for fx in core
    )
    element = load_profile_registry().get("element")
    assert "element_abi" in element.admit_subdirectories


def test_suite_digests_deterministic() -> None:
    first = suite_digests()
    second = suite_digests()
    assert first == second
    assert set(first) == set(PROFILE_IDS)
    assert len(profile_suite_digest("core-render")) == 64
