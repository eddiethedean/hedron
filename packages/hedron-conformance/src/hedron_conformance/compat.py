"""Schema / contract compatibility policy for the portable conformance kit."""

from __future__ import annotations

from dataclasses import dataclass

from hedron_conformance.schema import CONTRACT_VERSION, FIXTURE_VERSION

# Major contract id is everything before the last ``-N`` segment when present.
# ``hedron-portable-1`` → family ``hedron-portable``, major ``1``.
_SUPPORTED_CONTRACT_FAMILIES = frozenset({"hedron-portable"})
_SUPPORTED_CONTRACT_MAJORS = frozenset({1})
_SUPPORTED_FIXTURE_MAJORS = frozenset({1})


@dataclass(frozen=True, slots=True)
class CompatibilityDecision:
    ok: bool
    code: str
    message: str


def _split_contract(version: str) -> tuple[str, int] | None:
    text = version.strip()
    if not text:
        return None
    if "-" not in text:
        return None
    family, _, major_s = text.rpartition("-")
    if not family or not major_s.isdigit():
        return None
    return family, int(major_s)


def _fixture_major(version: str) -> int | None:
    text = version.strip()
    if not text:
        return None
    head = text.split(".", 1)[0]
    if not head.isdigit():
        return None
    return int(head)


def check_contract_version(version: str) -> CompatibilityDecision:
    """Return whether a fixture ``contract_version`` is acceptable to this runner."""
    parsed = _split_contract(version)
    if parsed is None:
        return CompatibilityDecision(
            ok=False,
            code="CONF-COMPAT-CONTRACT-MALFORMED",
            message=f"malformed contract_version {version!r}; expected family-N like {CONTRACT_VERSION!r}",
        )
    family, major = parsed
    if family not in _SUPPORTED_CONTRACT_FAMILIES:
        return CompatibilityDecision(
            ok=False,
            code="CONF-COMPAT-CONTRACT-FAMILY",
            message=f"unsupported contract family {family!r}; supported={sorted(_SUPPORTED_CONTRACT_FAMILIES)}",
        )
    if major not in _SUPPORTED_CONTRACT_MAJORS:
        return CompatibilityDecision(
            ok=False,
            code="CONF-COMPAT-CONTRACT-MAJOR",
            message=(
                f"unsupported contract major {major} for {family}; "
                f"supported majors={sorted(_SUPPORTED_CONTRACT_MAJORS)}; "
                f"runner contract={CONTRACT_VERSION}"
            ),
        )
    return CompatibilityDecision(
        ok=True,
        code="CONF-COMPAT-OK",
        message=f"contract_version {version} accepted (runner={CONTRACT_VERSION})",
    )


def check_fixture_version(version: str) -> CompatibilityDecision:
    """Return whether a fixture ``fixture_version`` major is acceptable."""
    major = _fixture_major(version)
    if major is None:
        return CompatibilityDecision(
            ok=False,
            code="CONF-COMPAT-FIXTURE-MALFORMED",
            message=f"malformed fixture_version {version!r}; expected semver-like {FIXTURE_VERSION!r}",
        )
    if major not in _SUPPORTED_FIXTURE_MAJORS:
        return CompatibilityDecision(
            ok=False,
            code="CONF-COMPAT-FIXTURE-MAJOR",
            message=(
                f"unsupported fixture major {major}; "
                f"supported majors={sorted(_SUPPORTED_FIXTURE_MAJORS)}; "
                f"runner fixture={FIXTURE_VERSION}"
            ),
        )
    return CompatibilityDecision(
        ok=True,
        code="CONF-COMPAT-OK",
        message=f"fixture_version {version} accepted (runner={FIXTURE_VERSION})",
    )


def compatibility_policy_dict() -> dict[str, object]:
    """Machine-readable policy for third-party runtime authors."""
    return {
        "runner_contract_version": CONTRACT_VERSION,
        "runner_fixture_version": FIXTURE_VERSION,
        "supported_contract_families": sorted(_SUPPORTED_CONTRACT_FAMILIES),
        "supported_contract_majors": sorted(_SUPPORTED_CONTRACT_MAJORS),
        "supported_fixture_majors": sorted(_SUPPORTED_FIXTURE_MAJORS),
        "forward": "Same family + same major is accepted; newer majors refuse with CONF-COMPAT-*.",
        "backward": "Older majors in the same family refuse; re-publish fixtures against the runner major.",
    }
