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
    assert not failures("Current train: 0.26.x; last published v0.26.0.")


def test_current_train_claim_rejects_any_stale_minor_without_a_version_blacklist() -> None:
    assert failures("The current published train is 0.25.x.")
    assert failures("The living train is 0.24.")


def test_previous_train_is_allowed_only_when_explicitly_historical_or_supported() -> None:
    assert not failures("The previous 0.25.x train receives best-effort security triage.")
    assert failures("The current train is 0.25.x.")


def test_install_commands_require_the_canonical_bounded_pin() -> None:
    assert not failures('pip install "hedron>=0.26.0,<0.27"')
    assert failures('pip install "hedron>=0.26.0"')
    assert failures("uv add hedron")


def test_satellite_floors_come_from_release_metadata() -> None:
    assert ssot._has_compatible_satellite_floor(
        'pip install "hedron-charts[matplotlib]>=0.1.6,<0.2"'
    )
    assert ssot._has_compatible_satellite_floor('uv add "hedron-sample-kit>=0.1.6,<0.2"')
    assert not ssot._has_compatible_satellite_floor('pip install "hedron-charts>=0.1.5,<0.2"')


def test_unbounded_fixed_charts_floor_is_rejected() -> None:
    assert ssot.UNBOUNDED_CHARTS_PKG.search("hedron-charts>=0.1.6")
    assert not ssot.UNBOUNDED_CHARTS_PKG.search("hedron-charts>=0.1.6,<0.2")


def test_metadata_matches_workspace_and_changelog() -> None:
    assert not ssot.check_metadata()
