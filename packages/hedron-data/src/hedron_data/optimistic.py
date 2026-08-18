"""Typed OptimisticMutation contract (phase 0.39 / OPTIMISTIC-039).

First proven inventory: bounded DataEditor / collection cell edits only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from hedron_core.security import contains_dangerous_scheme
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "DENY_BY_DEFAULT_RISKS",
    "OptimisticMutation",
    "OptimisticMutationState",
    "OptimisticPatch",
    "OptimisticRiskClass",
    "assert_optimism_allowed",
    "new_idempotency_key",
]


class OptimisticMutationState(StrEnum):
    CANONICAL = "canonical"
    PROPOSED = "proposed"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"
    CONFLICTED = "conflicted"
    REFETCHED = "refetched"


OptimisticRiskClass = Literal[
    "collection_edit",
    "authentication",
    "authorization",
    "irreversible_destruction",
    "payment",
    "secret",
    "file_publication",
    "cross_tenant",
]

DENY_BY_DEFAULT_RISKS: frozenset[str] = frozenset(
    {
        "authentication",
        "authorization",
        "irreversible_destruction",
        "payment",
        "secret",
        "file_publication",
        "cross_tenant",
    }
)


@dataclass(frozen=True, slots=True)
class OptimisticPatch:
    """Typed forward patch for a single field (allowlisted keys only)."""

    row_key: str
    field: str
    value: JsonValue
    previous: JsonValue | None = None

    def to_json_dict(self) -> dict[str, JsonValue]:
        return {
            "row_key": self.row_key,
            "field": self.field,
            "value": self.value,
            "previous": self.previous,
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> OptimisticPatch:
        return cls(
            row_key=str(raw["row_key"]),
            field=str(raw["field"]),
            value=raw.get("value"),  # type: ignore[arg-type]
            previous=raw.get("previous"),  # type: ignore[arg-type]
        )


def new_idempotency_key() -> str:
    return str(uuid4())


def assert_optimism_allowed(risk_class: str) -> None:
    if risk_class in DENY_BY_DEFAULT_RISKS:
        raise ValueError(
            f"OptimisticMutation deny-by-default for risk class {risk_class!r}; "
            "use server-confirmed mutation instead."
        )


@dataclass(slots=True)
class OptimisticMutation:
    """Explicit optimistic mutation with revision + idempotency + state machine."""

    action_id: str
    base_revision: str | int | None
    patches: tuple[OptimisticPatch, ...]
    idempotency_key: str = field(default_factory=new_idempotency_key)
    risk_class: OptimisticRiskClass = "collection_edit"
    refetch: bool = False
    state: OptimisticMutationState = OptimisticMutationState.CANONICAL
    allowed_fields: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        assert_optimism_allowed(self.risk_class)
        if not self.idempotency_key:
            raise ValueError("OptimisticMutation requires an idempotency_key")
        if not self.patches and not self.refetch:
            raise ValueError("OptimisticMutation requires patches or refetch=True")
        for patch in self.patches:
            if self.allowed_fields and patch.field not in self.allowed_fields:
                raise ValueError(f"field {patch.field!r} is not on the typed allowlist")
            if patch.field.startswith("__") or patch.field in {"constructor", "prototype"}:
                raise ValueError(f"forbidden patch field {patch.field!r}")
            if isinstance(patch.value, str) and (
                "<" in patch.value or contains_dangerous_scheme(patch.value)
            ):
                raise ValueError("Optimistic patches cannot contain HTML or executable URLs")

    def propose(self) -> OptimisticMutation:
        if self.state not in {
            OptimisticMutationState.CANONICAL,
            OptimisticMutationState.ROLLED_BACK,
            OptimisticMutationState.REFETCHED,
        }:
            raise ValueError(f"cannot propose from state {self.state}")
        self.state = OptimisticMutationState.PROPOSED
        return self

    def submit(self) -> OptimisticMutation:
        if self.state != OptimisticMutationState.PROPOSED:
            raise ValueError(f"cannot submit from state {self.state}")
        self.state = OptimisticMutationState.SUBMITTED
        return self

    def confirm(self, *, server_revision: str | int | None = None) -> OptimisticMutation:
        if self.state != OptimisticMutationState.SUBMITTED:
            raise ValueError(f"cannot confirm from state {self.state}")
        self.state = OptimisticMutationState.CONFIRMED
        if server_revision is not None:
            self.base_revision = server_revision
        return self

    def reject(self) -> OptimisticMutation:
        if self.state not in {
            OptimisticMutationState.PROPOSED,
            OptimisticMutationState.SUBMITTED,
        }:
            raise ValueError(f"cannot reject from state {self.state}")
        self.state = OptimisticMutationState.REJECTED
        return self

    def rollback(self) -> OptimisticMutation:
        if self.state not in {
            OptimisticMutationState.REJECTED,
            OptimisticMutationState.PROPOSED,
            OptimisticMutationState.SUBMITTED,
        }:
            raise ValueError(f"cannot rollback from state {self.state}")
        self.state = OptimisticMutationState.ROLLED_BACK
        return self

    def conflict(self) -> OptimisticMutation:
        if self.state not in {
            OptimisticMutationState.PROPOSED,
            OptimisticMutationState.SUBMITTED,
        }:
            raise ValueError(f"cannot conflict from state {self.state}")
        self.state = OptimisticMutationState.CONFLICTED
        return self

    def resolve_with_refetch(self, *, server_revision: str | int | None) -> OptimisticMutation:
        if self.state != OptimisticMutationState.CONFLICTED:
            raise ValueError(f"cannot refetch-resolve from state {self.state}")
        self.state = OptimisticMutationState.REFETCHED
        if server_revision is not None:
            self.base_revision = server_revision
        return self

    def to_json_dict(self) -> dict[str, JsonValue]:
        return {
            "action_id": self.action_id,
            "base_revision": self.base_revision,
            "idempotency_key": self.idempotency_key,
            "risk_class": self.risk_class,
            "refetch": self.refetch,
            "state": str(self.state),
            "patches": [p.to_json_dict() for p in self.patches],
        }

    @classmethod
    def from_cell_edits(
        cls,
        *,
        action_id: str,
        base_revision: str | int | None,
        patches: Sequence[OptimisticPatch | Mapping[str, object]],
        allowed_fields: frozenset[str] | None = None,
        idempotency_key: str | None = None,
    ) -> OptimisticMutation:
        built = tuple(
            p if isinstance(p, OptimisticPatch) else OptimisticPatch.from_mapping(p)
            for p in patches
        )
        return cls(
            action_id=action_id,
            base_revision=base_revision,
            patches=built,
            idempotency_key=idempotency_key or new_idempotency_key(),
            risk_class="collection_edit",
            allowed_fields=allowed_fields or frozenset(),
        )
