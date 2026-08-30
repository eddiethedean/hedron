"""Versioned conformance profile registry (PROFILE-052).

Profiles extend ``hedron-portable-1``. Subdirectory corpora are admitted only
when a profile explicitly lists them — never as the default authority.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, cast

from hedron_conformance.schema import (
    CONTRACT_VERSION,
    Capability,
    ConformanceFixture,
    fixtures_dir,
    load_bundled_fixtures,
)

_LOG = logging.getLogger("hedron_conformance.profiles")

PROFILE_IDS = (
    "core-render",
    "interaction",
    "manifest",
    "element",
    "package",
)

# Opt-in subdirectory corpora from conformance-profile-052.toml.
SUBDIRECTORY_CORPORA = frozenset(
    {
        "type_authoring_044",
        "updates_043",
        "element_abi",
    }
)


@dataclass(frozen=True, slots=True)
class Profile:
    """A versioned profile admitting a capability subset and optional corpora."""

    id: str
    summary: str
    capabilities: frozenset[Capability]
    admit_subdirectories: frozenset[str]
    contract_version: str = CONTRACT_VERSION
    state: str = "Implemented"


@dataclass(frozen=True, slots=True)
class ProfileRegistry:
    """Versioned registry matching the 0.52 profile lock."""

    schema_version: int
    phase: str
    seed_contract_version: str
    profiles: tuple[Profile, ...]

    def get(self, profile_id: str) -> Profile:
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile
        raise KeyError(f"unknown profile_id {profile_id!r}")

    def ids(self) -> tuple[str, ...]:
        return tuple(p.id for p in self.profiles)


def _builtin_profiles() -> tuple[Profile, ...]:
    return (
        Profile(
            id="core-render",
            summary="Core HTML/normalize render vectors under the portable subset.",
            capabilities=frozenset(
                {
                    Capability.RENDERING,
                    Capability.ESCAPING,
                    Capability.IDENTITY,
                    Capability.ACCESSIBILITY,
                }
            ),
            admit_subdirectories=frozenset(),
        ),
        Profile(
            id="interaction",
            summary="Interaction and event vectors admitted by the portable subset.",
            capabilities=frozenset(
                {
                    Capability.DIAGNOSTICS,
                    Capability.ADVERSARIAL,
                }
            ),
            admit_subdirectories=frozenset({"updates_043"}),
        ),
        Profile(
            id="manifest",
            summary="Package/manifest negotiation and capability declaration vectors.",
            capabilities=frozenset(
                {
                    Capability.ARTIFACT_VERSION,
                    Capability.DIAGNOSTICS,
                }
            ),
            admit_subdirectories=frozenset(),
        ),
        Profile(
            id="element",
            summary="Element ABI portable vectors (opt-in subdirectory until admitted).",
            capabilities=frozenset(
                {
                    Capability.RENDERING,
                    Capability.IDENTITY,
                    Capability.ESCAPING,
                }
            ),
            admit_subdirectories=frozenset({"element_abi"}),
        ),
        Profile(
            id="package",
            summary="External package author-kit declared-capability vectors.",
            capabilities=frozenset(
                {
                    Capability.ARTIFACT_VERSION,
                    Capability.DIAGNOSTICS,
                }
            ),
            admit_subdirectories=frozenset({"type_authoring_044"}),
        ),
    )


def load_profile_registry() -> ProfileRegistry:
    """Return the versioned 0.52 profile registry (extends hedron-portable-1)."""
    profiles = _builtin_profiles()
    assert tuple(p.id for p in profiles) == PROFILE_IDS
    for profile in profiles:
        unknown = profile.admit_subdirectories - SUBDIRECTORY_CORPORA
        if unknown:
            raise RuntimeError(f"profile {profile.id} admits unknown corpora: {sorted(unknown)}")
    return ProfileRegistry(
        schema_version=1,
        phase="0.52",
        seed_contract_version=CONTRACT_VERSION,
        profiles=profiles,
    )


def admit_fixtures(
    profile_id: str,
    *,
    fixtures: Iterable[ConformanceFixture] | None = None,
    include_subdirectories: bool = True,
) -> list[ConformanceFixture]:
    """Return fixtures admitted by ``profile_id``.

    Default corpus is top-level bundled fixtures filtered by profile
    capabilities. Subdirectory corpora are included only when the profile
    explicitly admits them and ``include_subdirectories`` is True.
    """
    registry = load_profile_registry()
    profile = registry.get(profile_id)
    source = list(fixtures) if fixtures is not None else load_bundled_fixtures()
    admitted = [fx for fx in source if fx.capability in profile.capabilities]
    if include_subdirectories and profile.admit_subdirectories:
        admitted.extend(
            fx
            for fx in _load_subdirectory_markers(profile.admit_subdirectories)
            if fx.capability in profile.capabilities
        )
    return admitted


def _load_subdirectory_markers(names: frozenset[str]) -> list[ConformanceFixture]:
    """Load portable ConformanceFixture rows from admitted subdirectory JSON.

    Non-ConformanceFixture corpora (e.g. element_abi inventory JSON) are skipped
    rather than failing closed — they remain opt-in markers for the profile.
    Capability filtering is applied by ``admit_fixtures``.
    """
    directory = fixtures_dir()
    out: list[ConformanceFixture] = []
    for name in sorted(names):
        sub = directory / name
        if not sub.is_dir():
            continue
        for path in sorted(sub.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            items = cast(list[Any], data) if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict) or "capability" not in item or "id" not in item:
                    continue
                try:
                    out.append(ConformanceFixture.model_validate(item))
                except Exception:  # noqa: BLE001 — skip non-portable shapes
                    _LOG.debug(
                        "skipping non-portable conformance fixture in %s",
                        path,
                        exc_info=True,
                    )
                    continue
    return out


def suite_digest(fixtures: Iterable[ConformanceFixture]) -> str:
    """Deterministic SHA-256 digest over a fixture suite (id + capability + versions)."""
    rows: list[str] = []
    for fx in sorted(fixtures, key=lambda f: f.id):
        rows.append(
            f"{fx.id}\t{fx.capability.value}\t{fx.contract_version}\t{fx.fixture_version}\t"
            f"{int(fx.negative)}"
        )
    payload = "\n".join(rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def profile_suite_digest(profile_id: str) -> str:
    """Digest for the fixtures admitted by ``profile_id``."""
    return suite_digest(admit_fixtures(profile_id))


def suite_digests() -> dict[str, str]:
    """Map every registered profile id to its suite digest."""
    registry = load_profile_registry()
    return {profile_id: profile_suite_digest(profile_id) for profile_id in registry.ids()}


__all__ = [
    "PROFILE_IDS",
    "SUBDIRECTORY_CORPORA",
    "Profile",
    "ProfileRegistry",
    "admit_fixtures",
    "load_profile_registry",
    "profile_suite_digest",
    "suite_digest",
    "suite_digests",
]
