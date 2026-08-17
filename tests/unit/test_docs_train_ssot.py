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
    assert not failures(
        f"Current train: {ssot.FACTS.train_line}; last published v{ssot.FACTS.published_version}."
    )


def test_current_train_claim_rejects_any_stale_minor_without_a_version_blacklist() -> None:
    assert failures("The current published train is 0.25.x.")
    assert failures("The living train is 0.24.")


def test_living_version_before_train_is_checked() -> None:
    assert failures("Capability readiness is Supported on the living **0.27** train.")
    assert not failures(
        f"Capability readiness is Supported on the living **{ssot.FACTS.train}** train."
    )
    assert failures("Ship on the living 0.27 train.")
    assert not failures(f"Ship on the living {ssot.FACTS.train} train.")


def test_soft_wrapped_living_claim_is_checked() -> None:
    wrapped = "Capability readiness is Supported on the living **0.27**\ntrain."
    assert failures(wrapped)
    ok = f"Capability readiness is Supported on the living **{ssot.FACTS.train}**\ntrain."
    assert not failures(ok)


def test_soft_wrapped_last_published_claim_is_checked() -> None:
    assert failures("Status: last published\nPyPI/git = `v0.34.0`.")
    assert not failures(f"Status: last published\nPyPI/git = `v{ssot.FACTS.published_version}`.")


def test_current_tip_and_current_pin_claims_are_checked() -> None:
    assert failures("Install the current tip under **0.34.0** above.")
    assert failures("Prefer the living `hedron>=0.34.0,<0.35` train.")
    assert not failures(f"Prefer the current `hedron{ssot.FACTS.pin}` train.")


def test_last_version_claim_without_published_keyword() -> None:
    assert failures("| Version | **0.28.x** / last **v0.27.0** |")
    assert not failures(
        f"| Version | **{ssot.FACTS.train_line}** / last **v{ssot.FACTS.published_version}** |"
    )


def test_previous_train_is_allowed_only_when_explicitly_historical_or_supported() -> None:
    prev = ssot.FACTS.previous_train
    assert not failures(f"The previous {prev}.x train receives best-effort security triage.")
    assert failures(f"The current train is {prev}.x.")


def test_install_commands_require_the_canonical_bounded_pin() -> None:
    assert not failures(f'pip install "hedron{ssot.FACTS.pin}"')
    assert failures('pip install "hedron>=0.26.0"')
    assert failures("uv add hedron")
    if ssot.FACTS.registry_deferred:
        assert not failures(f'uvx --from "hedron{ssot.FACTS.pypi_pin}" hedron new demo')


def test_pypi_latest_claim_is_allowed_when_registry_is_deferred() -> None:
    if not ssot.FACTS.registry_deferred:
        return
    assert not failures(
        f"On PyPI today the latest is **{ssot.FACTS.pypi_version}** (tag/PyPI deferred)."
    )
    assert failures("The current published train is 0.25.x.")


def test_first_run_pages_must_disclose_deferred_pypi() -> None:
    if not ssot.FACTS.registry_deferred:
        return
    missing = ssot.check_first_run_registry_honesty(
        {path: "Train 0.46 without mentioning the index.\n" for path in ssot.FIRST_RUN_PATHS}
    )
    assert missing
    honest = (
        f"On PyPI today: {ssot.FACTS.pypi_version}. "
        "This repository is 0.46.0 (Git tag / PyPI deferred).\n"
    )
    ok = ssot.check_first_run_registry_honesty({path: honest for path in ssot.FIRST_RUN_PATHS})
    assert not ok


def test_historical_install_can_be_skipped_without_skipping_current_claims() -> None:
    text = 'pip install "hedron>=0.20.0,<0.21"'
    assert not ssot.check_text(Path("historical.md"), text, check_installs=False)
    assert ssot.check_text(
        Path("historical.md"),
        "The current train is 0.20.x.",
        check_installs=False,
    )


def test_satellite_floors_come_from_release_metadata() -> None:
    charts = ssot.FACTS.charts_pin
    sample = ssot.FACTS.sample_kit_pin
    assert ssot._has_compatible_satellite_floor(f'pip install "hedron-charts[matplotlib]{charts}"')
    assert ssot._has_compatible_satellite_floor(f'uv add "hedron-sample-kit{sample}"')
    assert not ssot._has_compatible_satellite_floor(
        f'pip install "hedron-charts>=0.1.5,<{ssot.FACTS.charts_maximum}"'
    )


def test_unbounded_fixed_charts_floor_is_rejected() -> None:
    floor = ssot.FACTS.charts_minimum
    assert ssot.UNBOUNDED_CHARTS_PKG.search(f"hedron-charts>={floor}")
    assert not ssot.UNBOUNDED_CHARTS_PKG.search(
        f"hedron-charts>={floor},<{ssot.FACTS.charts_maximum}"
    )


def test_metadata_matches_workspace_and_changelog() -> None:
    assert not ssot.check_metadata()


def test_security_policy_is_derived_from_release_metadata() -> None:
    facts = ssot.FACTS
    text = (
        f"Security fixes land on the **current published train** (`{facts.train_line}`).\n"
        "Best-effort triage for the immediately previous minor "
        f"(`{facts.previous_train}.x`).\n"
        f"| `{facts.train_line}` | Yes (current published train — pin `{facts.pin}`; "
        f"published `v{facts.published_version}`) |\n"
        f"| `{facts.previous_train}.x` | Best-effort security triage through "
        f"approximately {facts.previous_security_until}; upgrade to `{facts.train_line}` |\n"
    )
    assert not ssot.check_security_policy(Path("SECURITY.md"), text)


def test_security_policy_rejects_stale_support_rows() -> None:
    assert ssot.check_security_policy(
        Path("SECURITY.md"),
        "Security fixes land on 0.38; 0.35 receives best-effort triage.",
    )
