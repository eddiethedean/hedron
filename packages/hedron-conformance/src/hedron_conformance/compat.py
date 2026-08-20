"""Schema / contract compatibility policy for the portable conformance kit."""

from __future__ import annotations

from dataclasses import dataclass

from hedron_conformance.schema import CONTRACT_VERSION, FIXTURE_VERSION

# Major contract id is everything before the last ``-N`` segment when present.
# ``hedron-portable-1`` → family ``hedron-portable``, major ``1``.
_SUPPORTED_CONTRACT_FAMILIES = frozenset({"hedron-portable"})
_SUPPORTED_CONTRACT_MAJORS = frozenset({1})
_SUPPORTED_FIXTURE_MAJORS = frozenset({1})

# COMPAT-052: current/previous negotiation matrix (extend, do not replace seed).
CURRENT_CONTRACT_VERSION = CONTRACT_VERSION
# No prior portable major exists yet; previous equals current until a negotiated successor.
PREVIOUS_CONTRACT_VERSION = CONTRACT_VERSION
NEGOTIABLE_CONTRACT_VERSIONS = frozenset({CURRENT_CONTRACT_VERSION, PREVIOUS_CONTRACT_VERSION})


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
            message=(
                f"malformed contract_version {version!r}; "
                f"expected family-N like {CONTRACT_VERSION!r}"
            ),
        )
    family, major = parsed
    if family not in _SUPPORTED_CONTRACT_FAMILIES:
        return CompatibilityDecision(
            ok=False,
            code="CONF-COMPAT-CONTRACT-FAMILY",
            message=(
                f"unsupported contract family {family!r}; "
                f"supported={sorted(_SUPPORTED_CONTRACT_FAMILIES)}"
            ),
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
            message=(
                f"malformed fixture_version {version!r}; expected semver-like {FIXTURE_VERSION!r}"
            ),
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


def negotiate_protocol(requested: str) -> CompatibilityDecision:
    """Negotiate a requested contract version against current/previous (COMPAT-052).

    Forward-unknown majors fail closed. The seed ``hedron-portable-1`` is never
    silently replaced — successors must appear in the negotiable set first.
    """
    text = requested.strip()
    if text in NEGOTIABLE_CONTRACT_VERSIONS:
        return CompatibilityDecision(
            ok=True,
            code="CONF-COMPAT-NEGOTIATE-OK",
            message=(
                f"negotiated {text} "
                f"(current={CURRENT_CONTRACT_VERSION}, previous={PREVIOUS_CONTRACT_VERSION})"
            ),
        )
    # Still accept same-family same-major via the existing checker (fail-closed otherwise).
    base = check_contract_version(text)
    if base.ok:
        return CompatibilityDecision(
            ok=True,
            code="CONF-COMPAT-NEGOTIATE-OK",
            message=base.message,
        )
    return CompatibilityDecision(
        ok=False,
        code="CONF-COMPAT-NEGOTIATE-REFUSED",
        message=(
            f"protocol negotiation refused for {requested!r}; "
            f"negotiable={sorted(NEGOTIABLE_CONTRACT_VERSIONS)}; {base.message}"
        ),
    )


def protocol_matrix() -> dict[str, object]:
    """Current/previous protocol matrix for COMPAT-052 evidence."""
    return {
        "current": CURRENT_CONTRACT_VERSION,
        "previous": PREVIOUS_CONTRACT_VERSION,
        "negotiable": sorted(NEGOTIABLE_CONTRACT_VERSIONS),
        "replace_seed_without_negotiation": False,
        "forward_unknown": "fail-closed",
    }


def compatibility_policy_dict() -> dict[str, object]:
    """Machine-readable policy for third-party runtime authors."""
    return {
        "runner_contract_version": CONTRACT_VERSION,
        "runner_fixture_version": FIXTURE_VERSION,
        "supported_contract_families": sorted(_SUPPORTED_CONTRACT_FAMILIES),
        "supported_contract_majors": sorted(_SUPPORTED_CONTRACT_MAJORS),
        "supported_fixture_majors": sorted(_SUPPORTED_FIXTURE_MAJORS),
        "current_contract_version": CURRENT_CONTRACT_VERSION,
        "previous_contract_version": PREVIOUS_CONTRACT_VERSION,
        "negotiable_contract_versions": sorted(NEGOTIABLE_CONTRACT_VERSIONS),
        "forward": (
            "Same family + same major is accepted; newer majors refuse with CONF-COMPAT-*."
        ),
        "backward": (
            "Older majors in the same family refuse; re-publish fixtures against the runner major."
        ),
        "negotiation": (
            "Call negotiate_protocol(requested); successors require explicit negotiable admission."
        ),
    }
