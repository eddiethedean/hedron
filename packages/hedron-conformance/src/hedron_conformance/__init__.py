"""Language-neutral Hedron conformance-test kit."""

from __future__ import annotations

from hedron_conformance.author import (
    AUTHOR_KIT_VERSION,
    AuthorKitDiagnostic,
    author_kit_dir,
    author_kit_summary,
    declared_capabilities,
    intentional_failure_examples,
    validate_author_manifest,
)
from hedron_conformance.compat import (
    CURRENT_CONTRACT_VERSION,
    PREVIOUS_CONTRACT_VERSION,
    CompatibilityDecision,
    check_contract_version,
    check_fixture_version,
    compatibility_policy_dict,
    negotiate_protocol,
    protocol_matrix,
)
from hedron_conformance.compile import CompileReport, compile_suite
from hedron_conformance.element_abi import load_element_abi_fixtures
from hedron_conformance.normalize import normalize_html
from hedron_conformance.profiles import (
    PROFILE_IDS,
    Profile,
    ProfileRegistry,
    admit_fixtures,
    load_profile_registry,
    profile_suite_digest,
    suite_digest,
    suite_digests,
)
from hedron_conformance.report import (
    build_result_envelope,
    offline_bundle_manifest,
    to_junit,
    to_sarif,
    verify_envelope_digest,
)
from hedron_conformance.runner import CapabilityResult, FixtureResult, KitReport, run_kit
from hedron_conformance.sandbox import (
    NO_NETWORK_MARKER,
    PROCESS_KILL_TIMEOUT_S,
    SandboxPolicy,
    SuitePathError,
    refuse_secret_env_capture,
    validate_suite_path,
)
from hedron_conformance.schema import (
    CONTRACT_VERSION,
    FIXTURE_VERSION,
    PROTOCOL_CURRENT,
    PROTOCOL_PREVIOUS,
    Capability,
    ConformanceFixture,
    ExpectedOutcome,
    FixtureInput,
    load_bundled_fixtures,
)

__version__ = "0.52.0"

__all__ = [
    "AUTHOR_KIT_VERSION",
    "CONTRACT_VERSION",
    "CURRENT_CONTRACT_VERSION",
    "FIXTURE_VERSION",
    "NO_NETWORK_MARKER",
    "PREVIOUS_CONTRACT_VERSION",
    "PROCESS_KILL_TIMEOUT_S",
    "PROFILE_IDS",
    "PROTOCOL_CURRENT",
    "PROTOCOL_PREVIOUS",
    "AuthorKitDiagnostic",
    "Capability",
    "CapabilityResult",
    "CompatibilityDecision",
    "CompileReport",
    "ConformanceFixture",
    "ExpectedOutcome",
    "FixtureInput",
    "FixtureResult",
    "KitReport",
    "Profile",
    "ProfileRegistry",
    "SandboxPolicy",
    "SuitePathError",
    "__version__",
    "admit_fixtures",
    "author_kit_dir",
    "author_kit_summary",
    "build_result_envelope",
    "check_contract_version",
    "check_fixture_version",
    "compatibility_policy_dict",
    "compile_suite",
    "declared_capabilities",
    "intentional_failure_examples",
    "load_bundled_fixtures",
    "load_element_abi_fixtures",
    "load_profile_registry",
    "negotiate_protocol",
    "normalize_html",
    "offline_bundle_manifest",
    "profile_suite_digest",
    "protocol_matrix",
    "refuse_secret_env_capture",
    "run_kit",
    "suite_digest",
    "suite_digests",
    "to_junit",
    "to_sarif",
    "validate_author_manifest",
    "validate_suite_path",
    "verify_envelope_digest",
]
