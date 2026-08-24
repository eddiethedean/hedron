"""Stable target, writer, and bounded state-transfer contracts (0.62)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from hedron_core.diagnostics import error

__all__ = [
    "IdentityRegistry",
    "IdentityTarget",
    "StateTransfer",
    "StateTransferPolicy",
]


@dataclass(frozen=True, slots=True)
class IdentityTarget:
    key: str
    target: str
    writer: str
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if not all((self.key, self.target, self.writer)):
            raise ValueError("identity key, target, and writer are required")
        if len(self.key) > 256 or len(self.target) > 512 or len(self.writer) > 256:
            raise ValueError("identity fields exceed their limits")


@dataclass(frozen=True, slots=True)
class StateTransferPolicy:
    max_fields: int = 64
    max_bytes: int = 32_768
    require_schema_match: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.max_fields <= 1024:
            raise ValueError("max_fields must be between 1 and 1024")
        if not 1 <= self.max_bytes <= 262_144:
            raise ValueError("max_bytes must be between 1 and 262144")


@dataclass(frozen=True, slots=True)
class StateTransfer:
    identity: IdentityTarget
    fields: Mapping[str, Any]
    revision: str | int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))


@dataclass(slots=True)
class IdentityRegistry:
    """Reject duplicate writers instead of applying last-writer-wins silently."""

    policy: StateTransferPolicy = field(default_factory=StateTransferPolicy)
    _targets: dict[str, IdentityTarget] = field(
        default_factory=lambda: dict[str, IdentityTarget](), init=False, repr=False
    )

    def register(self, identity: IdentityTarget) -> None:
        existing = self._targets.get(identity.key)
        if existing is not None and existing != identity:
            raise error(
                "HED-IDENTITY-0002",
                title="Duplicate state writer",
                explanation=f"Identity {identity.key!r} has more than one target or writer.",
                remediation="Use one stable writer for the identity or declare a new key.",
                context={
                    "key": identity.key,
                    "existing_writer": existing.writer,
                    "writer": identity.writer,
                },
            )
        self._targets[identity.key] = identity

    def require(self, key: str) -> IdentityTarget:
        try:
            return self._targets[key]
        except KeyError as exc:
            raise error(
                "HED-IDENTITY-0001",
                title="Unknown identity target",
                explanation=f"No declared target exists for identity {key!r}.",
                remediation="Declare the target before transferring state.",
                context={"key": key},
            ) from exc

    def transfer(
        self, transfer: StateTransfer, target: IdentityTarget | None = None
    ) -> StateTransfer:
        destination = target or self.require(transfer.identity.key)
        if (
            destination.key != transfer.identity.key
            or destination.target != transfer.identity.target
        ):
            raise error(
                "HED-IDENTITY-0003",
                title="State transfer target mismatch",
                explanation="A transfer cannot cross its declared identity target.",
                remediation="Use a schema-compatible transfer for the declared target.",
            )
        if (
            self.policy.require_schema_match
            and destination.schema_version != transfer.identity.schema_version
        ):
            raise error(
                "HED-IDENTITY-0004",
                title="State transfer schema mismatch",
                explanation="The source and destination identity schemas differ.",
                remediation="Migrate the state explicitly or reject the transfer.",
            )
        if destination.writer != transfer.identity.writer:
            raise error(
                "HED-IDENTITY-0002",
                title="State transfer writer mismatch",
                explanation="A different writer cannot take ownership of durable state implicitly.",
                remediation="Declare an explicit ownership handoff.",
            )
        if len(transfer.fields) > self.policy.max_fields:
            raise error(
                "HED-IDENTITY-0005",
                title="State transfer field limit exceeded",
                explanation="The transfer contains more fields than the policy permits.",
                remediation="Transfer only the bounded, declared presentation state.",
            )
        try:
            encoded = json.dumps(dict(transfer.fields), separators=(",", ":"), sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise error(
                "HED-IDENTITY-0006",
                title="State transfer is not JSON-compatible",
                explanation="Transfer fields must be bounded JSON-compatible values.",
                remediation="Remove callbacks, request objects, credentials, and binary values.",
            ) from exc
        if len(encoded.encode()) > self.policy.max_bytes:
            raise error(
                "HED-IDENTITY-0005",
                title="State transfer byte limit exceeded",
                explanation="The transfer exceeds the configured state ceiling.",
                remediation="Transfer a smaller, declared presentation state.",
            )
        return transfer
