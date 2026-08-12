"""CONF-031 unit coverage: compatibility policy and author kit."""

from __future__ import annotations

from hedron_conformance import (
    author_kit_summary,
    check_contract_version,
    check_fixture_version,
    compatibility_policy_dict,
    intentional_failure_examples,
    validate_author_manifest,
)


def test_compat_accepts_runner_versions() -> None:
    assert check_contract_version("hedron-portable-1").ok
    assert check_fixture_version("1.0.0").ok


def test_compat_refuses_unknown_major() -> None:
    bad = check_contract_version("hedron-portable-99")
    assert not bad.ok
    assert bad.code.startswith("CONF-COMPAT-")


def test_author_kit_summary_and_failures() -> None:
    summary = author_kit_summary()
    assert summary["readme_present"] is True
    assert summary["template_present"] is True
    policy = compatibility_policy_dict()
    assert "hedron-portable" in policy["supported_contract_families"]
    failures = intentional_failure_examples()
    assert any(not item.ok for item in failures)
    results = validate_author_manifest("hedron-portable-1", "1.0.0")
    assert all(item.ok for item in results)
