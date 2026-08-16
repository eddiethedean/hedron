"""Language-neutral Hedron conformance-test kit."""

from __future__ import annotations

from hedron_conformance.author import (
    AuthorKitDiagnostic,
    author_kit_dir,
    author_kit_summary,
    intentional_failure_examples,
    validate_author_manifest,
)
from hedron_conformance.compat import (
    CompatibilityDecision,
    check_contract_version,
    check_fixture_version,
    compatibility_policy_dict,
)
from hedron_conformance.element_abi import load_element_abi_fixtures
from hedron_conformance.normalize import normalize_html
from hedron_conformance.runner import CapabilityResult, FixtureResult, run_kit
from hedron_conformance.schema import (
    CONTRACT_VERSION,
    FIXTURE_VERSION,
    Capability,
    ConformanceFixture,
    ExpectedOutcome,
    FixtureInput,
    load_bundled_fixtures,
)

__version__ = "0.45.0"

__all__ = [
    "CONTRACT_VERSION",
    "FIXTURE_VERSION",
    "AuthorKitDiagnostic",
    "Capability",
    "CapabilityResult",
    "CompatibilityDecision",
    "ConformanceFixture",
    "ExpectedOutcome",
    "FixtureInput",
    "FixtureResult",
    "__version__",
    "author_kit_dir",
    "author_kit_summary",
    "check_contract_version",
    "check_fixture_version",
    "compatibility_policy_dict",
    "intentional_failure_examples",
    "load_bundled_fixtures",
    "load_element_abi_fixtures",
    "normalize_html",
    "run_kit",
    "validate_author_manifest",
]
