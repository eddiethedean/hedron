"""Language-neutral Hedron conformance-test kit."""

from __future__ import annotations

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

__version__ = "0.28.0"

__all__ = [
    "CONTRACT_VERSION",
    "FIXTURE_VERSION",
    "Capability",
    "CapabilityResult",
    "ConformanceFixture",
    "ExpectedOutcome",
    "FixtureInput",
    "FixtureResult",
    "__version__",
    "load_bundled_fixtures",
    "normalize_html",
    "run_kit",
]
