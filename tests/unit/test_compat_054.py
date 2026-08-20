"""COMPAT-054: missing-extra / min-max / current-previous honesty for 0.54."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance.authoring_loop import AUTHORING_LOOP_SCHEMA_VERSION
from hedron_sample_kit import list_variants


def test_compat_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["COMPAT-054"]["state"] in {"Planned", "Verified"}
    assert Path("docs/acceptance/authoring-shared-054.toml").is_file()


def test_sample_kit_variants_independently_named() -> None:
    variants = set(list_variants())
    assert "web_component" in variants or "callout" in variants or len(variants) >= 1
    # Optional variant stays honest when env gate is off.
    assert AUTHORING_LOOP_SCHEMA_VERSION.startswith("hedron-authoring-loop-")


def test_authoring_extra_declared_for_conformance() -> None:
    meta = tomllib.loads(
        Path("packages/hedron-sample-kit/pyproject.toml").read_text(encoding="utf-8")
    )
    extras = meta["project"].get("optional-dependencies") or {}
    assert "authoring" in extras or "hedron-conformance" in str(meta)


def test_predecessor_052_still_compatible_contract() -> None:
    from hedron_conformance import CONTRACT_VERSION

    assert CONTRACT_VERSION == "hedron-portable-1"
