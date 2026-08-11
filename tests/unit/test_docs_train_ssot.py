"""Regression tests for metadata-driven release documentation validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_docs_train_ssot as ssot  # noqa: E402


def failures(text: str) -> list[str]:
    return ssot.check_text(Path("fixture.md"), text)


def test_current_train_claim_accepts_release_metadata() -> None:
    assert not failures("Current train: 0.28.x; last published v0.28.1.")


def test_current_train_claim_rejects_any_stale_minor_without_a_version_blacklist() -> None:
    assert failures("The current published train is 0.25.x.")
    assert failures("The living train is 0.24.")


def test_living_version_before_train_is_checked() -> None:
    assert failures("Capability readiness is Supported on the living **0.27** train.")
    assert not failures("Capability readiness is Supported on the living **0.28** train.")
    assert failures("Ship on the living 0.27 train.")
    assert not failures(f"Ship on the living {ssot.FACTS.train} train.")


def test_soft_wrapped_living_claim_is_checked() -> None:
    wrapped = "Capability readiness is Supported on the living **0.27**\ntrain."
    assert failures(wrapped)
    ok = "Capability readiness is Supported on the living **0.28**\ntrain."
    assert not failures(ok)


def test_last_version_claim_without_published_keyword() -> None:
    assert failures("| Version | **0.28.x** / last **v0.27.0** |")
    assert not failures("| Version | **0.28.x** / last **v0.28.1** |")


def test_previous_train_is_allowed_only_when_explicitly_historical_or_supported() -> None:
    prev = ssot.FACTS.previous_train
    assert not failures(f"The previous {prev}.x train receives best-effort security triage.")
    assert failures(f"The current train is {prev}.x.")


def test_install_commands_require_the_canonical_bounded_pin() -> None:
    assert not failures(f'pip install "hedron{ssot.FACTS.pin}"')
    assert failures('pip install "hedron>=0.26.0"')
    assert failures("uv add hedron")


def test_satellite_floors_come_from_release_metadata() -> None:
    floor = f">={ssot.FACTS.satellite_minimum},<{ssot.FACTS.satellite_maximum}"
    assert ssot._has_compatible_satellite_floor(f'pip install "hedron-charts[matplotlib]{floor}"')
    assert ssot._has_compatible_satellite_floor(f'uv add "hedron-sample-kit{floor}"')
    assert not ssot._has_compatible_satellite_floor(
        f'pip install "hedron-charts>=0.1.5,<{ssot.FACTS.satellite_maximum}"'
    )


def test_unbounded_fixed_charts_floor_is_rejected() -> None:
    floor = ssot.FACTS.satellite_minimum
    assert ssot.UNBOUNDED_CHARTS_PKG.search(f"hedron-charts>={floor}")
    assert not ssot.UNBOUNDED_CHARTS_PKG.search(
        f"hedron-charts>={floor},<{ssot.FACTS.satellite_maximum}"
    )


def test_metadata_matches_workspace_and_changelog() -> None:
    assert not ssot.check_metadata()
