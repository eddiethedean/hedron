"""Fixture compiler — reject contradictory suites before any runtime runs."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from hedron_conformance.compat import check_contract_version, check_fixture_version
from hedron_conformance.schema import Capability, ConformanceFixture


@dataclass
class CompileReport:
    """Result of compiling (validating) a fixture suite."""

    ok: bool
    errors: list[str] = field(default_factory=list)
    fixture_count: int = 0
    fixture_ids: list[str] = field(default_factory=list)


def compile_suite(fixtures: Sequence[ConformanceFixture]) -> CompileReport:
    """Validate fixtures; fail closed on contradictory or unknown fields."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    known_capabilities = {c.value for c in Capability}

    for index, fixture in enumerate(fixtures):
        prefix = f"fixtures[{index}] id={fixture.id!r}"

        if fixture.id in seen_ids:
            errors.append(f"{prefix}: duplicate fixture id")
        else:
            seen_ids.add(fixture.id)

        if not fixture.id.strip():
            errors.append(f"{prefix}: empty fixture id")

        cap_value = (
            fixture.capability.value
            if isinstance(fixture.capability, Capability)
            else str(fixture.capability)
        )
        if cap_value not in known_capabilities:
            errors.append(f"{prefix}: unknown capability {cap_value!r}")

        contract = check_contract_version(fixture.contract_version)
        if not contract.ok:
            errors.append(
                f"{prefix}: contract_version rejected ({contract.code}: {contract.message})"
            )

        fixture_ver = check_fixture_version(fixture.fixture_version)
        if not fixture_ver.ok:
            errors.append(
                f"{prefix}: fixture_version rejected ({fixture_ver.code}: {fixture_ver.message})"
            )

        errors.extend(_contradiction_errors(prefix, fixture))

    return CompileReport(
        ok=not errors,
        errors=errors,
        fixture_count=len(fixtures),
        fixture_ids=[fx.id for fx in fixtures],
    )


def _contradiction_errors(prefix: str, fixture: ConformanceFixture) -> list[str]:
    errors: list[str] = []
    inp = fixture.input
    expected = fixture.expected

    if inp.expect_error and expected.html is not None:
        errors.append(
            f"{prefix}: contradictory expectations — expect_error True with html expected"
        )
    if inp.expect_error and expected.escaped_text is not None:
        errors.append(
            f"{prefix}: contradictory expectations — expect_error True with escaped_text expected"
        )
    if inp.expect_error and expected.escaped_attr is not None:
        errors.append(
            f"{prefix}: contradictory expectations — expect_error True with escaped_attr expected"
        )
    if inp.expect_error and expected.a11y_ok is True:
        errors.append(f"{prefix}: contradictory expectations — expect_error True with a11y_ok True")
    if inp.expect_error and expected.diagnostic_code is None and expected.error_code is None:
        errors.append(
            f"{prefix}: expect_error True requires diagnostic_code or error_code in expected"
        )
    if not inp.expect_error and expected.error_code is not None and expected.html is not None:
        errors.append(
            f"{prefix}: contradictory expectations — error_code with html success payload"
        )
    return errors


__all__ = ["CompileReport", "compile_suite"]
