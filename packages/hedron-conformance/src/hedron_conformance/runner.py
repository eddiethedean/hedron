"""Capability-level conformance runner."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from hedron_conformance.normalize import (
    normalize_diagnostic_code,
    normalize_html,
    normalize_identity,
)
from hedron_conformance.reference import evaluate_fixture
from hedron_conformance.schema import (
    Capability,
    ConformanceFixture,
    ExpectedOutcome,
    load_bundled_fixtures,
)

Evaluator = Callable[[ConformanceFixture], ExpectedOutcome]


@dataclass(frozen=True)
class FixtureResult:
    fixture_id: str
    contract_version: str
    capability: Capability
    passed: bool
    detail: str = ""


@dataclass
class CapabilityResult:
    capability: Capability
    passed: int = 0
    failed: int = 0
    results: list[FixtureResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.failed == 0


@dataclass
class KitReport:
    results: list[FixtureResult]
    by_capability: dict[Capability, CapabilityResult]

    @property
    def ok(self) -> bool:
        return all(r.passed for r in self.results)

    def failures(self) -> list[FixtureResult]:
        return [r for r in self.results if not r.passed]


def _compare(expected: ExpectedOutcome, actual: ExpectedOutcome) -> str | None:
    if expected.html is not None and normalize_html(actual.html or "") != normalize_html(
        expected.html
    ):
        return f"html mismatch: expected={expected.html!r} actual={actual.html!r}"
    if expected.escaped_text is not None and actual.escaped_text != expected.escaped_text:
        return (
            f"escaped_text mismatch: expected={expected.escaped_text!r} "
            f"actual={actual.escaped_text!r}"
        )
    if expected.escaped_attr is not None and actual.escaped_attr != expected.escaped_attr:
        return (
            f"escaped_attr mismatch: expected={expected.escaped_attr!r} "
            f"actual={actual.escaped_attr!r}"
        )
    if expected.identity is not None and normalize_identity(
        actual.identity or ""
    ) != normalize_identity(expected.identity):
        return f"identity mismatch: expected={expected.identity!r} actual={actual.identity!r}"
    if expected.diagnostic_code is not None and normalize_diagnostic_code(
        actual.diagnostic_code or ""
    ) != normalize_diagnostic_code(expected.diagnostic_code):
        return (
            f"diagnostic_code mismatch: expected={expected.diagnostic_code!r} "
            f"actual={actual.diagnostic_code!r}"
        )
    if (
        expected.artifact_version is not None
        and actual.artifact_version != expected.artifact_version
    ):
        return (
            f"artifact_version mismatch: expected={expected.artifact_version!r} "
            f"actual={actual.artifact_version!r}"
        )
    if expected.a11y_ok is not None and actual.a11y_ok != expected.a11y_ok:
        return f"a11y_ok mismatch: expected={expected.a11y_ok!r} actual={actual.a11y_ok!r}"
    if expected.error_code is not None and actual.error_code != expected.error_code:
        return f"error_code mismatch: expected={expected.error_code!r} actual={actual.error_code!r}"
    return None


def run_kit(
    fixtures: Sequence[ConformanceFixture] | None = None,
    *,
    evaluator: Evaluator | None = None,
) -> KitReport:
    items = list(fixtures) if fixtures is not None else load_bundled_fixtures()
    eval_fn = evaluator or evaluate_fixture
    results: list[FixtureResult] = []
    by_cap: dict[Capability, CapabilityResult] = {}
    for fixture in items:
        cap_result = by_cap.setdefault(
            fixture.capability, CapabilityResult(capability=fixture.capability)
        )
        try:
            actual = eval_fn(fixture)
            detail = _compare(fixture.expected, actual)
            passed = detail is None
            if not passed:
                detail = (
                    f"fixture={fixture.id} contract={fixture.contract_version} "
                    f"capability={fixture.capability.value}: {detail}"
                )
            else:
                detail = ""
        except Exception as exc:  # noqa: BLE001 — runner must surface evaluator failures
            passed = False
            detail = (
                f"fixture={fixture.id} contract={fixture.contract_version} "
                f"capability={fixture.capability.value}: evaluator error: {exc}"
            )
        fr = FixtureResult(
            fixture_id=fixture.id,
            contract_version=fixture.contract_version,
            capability=fixture.capability,
            passed=passed,
            detail=detail,
        )
        results.append(fr)
        cap_result.results.append(fr)
        if passed:
            cap_result.passed += 1
        else:
            cap_result.failed += 1
    return KitReport(results=results, by_capability=by_cap)
