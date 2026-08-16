"""Closed 0.44 annotation markers (FastAPI host)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from hedron_core.codes import HED_TYPE_0002, HED_TYPE_0005, HED_TYPE_0006
from hedron_core.diagnostics import error
from hedron_core.updates import MAX_PATCH_TARGETS, MAX_REFRESH_TARGETS

if TYPE_CHECKING:
    from hedron.handles import BoundFragment, FragmentHandle

CONTROL_KINDS = (
    "text",
    "textarea",
    "password",
    "number",
    "checkbox",
    "select",
    "radio",
    "date",
    "time",
    "datetime-local",
    "file",
    "email",
    "url",
)
SAFE_AUTOCOMPLETE = frozenset(
    {
        "off",
        "on",
        "name",
        "email",
        "username",
        "current-password",
        "new-password",
        "organization",
        "url",
        "tel",
    }
)

__all__ = [
    "CONTROL_KINDS",
    "Control",
    "FormBody",
    "Refreshes",
    "Updates",
    "ViewParams",
]


@dataclass(frozen=True, slots=True)
class ViewParams:
    source: Literal["path", "query", "path_query"] = "path_query"


@dataclass(frozen=True, slots=True)
class FormBody:
    encoding: Literal["urlencoded", "multipart", "auto"] = "auto"


@dataclass(frozen=True, slots=True)
class Control:
    kind: str | None = None
    label: str | None = None
    help: str | None = None
    autocomplete: str | None = None
    rows: int | None = None

    def __post_init__(self) -> None:
        if self.kind is not None and self.kind not in CONTROL_KINDS:
            raise error(
                HED_TYPE_0005,
                title="Unknown Control.kind",
                explanation=f"Control.kind {self.kind!r} is outside the closed inventory.",
                remediation=f"Use one of: {', '.join(CONTROL_KINDS)}.",
            )
        if self.autocomplete is not None and self.autocomplete not in SAFE_AUTOCOMPLETE:
            raise error(
                HED_TYPE_0005,
                title="Unsafe Control.autocomplete",
                explanation=f"autocomplete={self.autocomplete!r} is not an allowlisted token.",
                remediation="Use a documented autocomplete token such as 'email' or 'off'.",
            )
        if self.rows is not None and (self.rows < 1 or self.rows > 64):
            raise error(
                HED_TYPE_0005,
                title="Invalid Control.rows",
                explanation="rows must be between 1 and 64.",
                remediation="Pass a small positive integer or omit rows.",
            )
        if self.label is not None and ("<" in self.label or ">" in self.label):
            raise error(
                HED_TYPE_0005,
                title="Unsafe Control.label",
                explanation="Control labels must be plain text.",
                remediation="Remove HTML from the label.",
            )


def _logical_ids(targets: Sequence[object]) -> tuple[str, ...]:
    ids: list[str] = []
    seen: set[str] = set()
    for item in targets:
        logical = getattr(item, "logical_id", None)
        if not isinstance(logical, str) or not logical:
            raise error(
                HED_TYPE_0006,
                title="Unresolved effect target",
                explanation=f"{item!r} is not a registered handle.",
                remediation="Pass FragmentHandle or BoundFragment instances.",
            )
        if logical in seen:
            continue
        seen.add(logical)
        ids.append(logical)
    return tuple(ids)


@dataclass(frozen=True, slots=True)
class Refreshes:
    targets: tuple[Any, ...]
    target_ids: tuple[str, ...]

    def __init__(self, *targets: FragmentHandle[Any, Any] | BoundFragment[Any]) -> None:
        ids = _logical_ids(targets)
        if len(ids) > MAX_REFRESH_TARGETS:
            raise error(
                HED_TYPE_0006,
                title="Declared refresh target limit exceeded",
                explanation=f"Refreshes listed {len(ids)} targets; max is {MAX_REFRESH_TARGETS}.",
                remediation="Reduce declared fan-out.",
            )
        object.__setattr__(self, "targets", targets)
        object.__setattr__(self, "target_ids", ids)


@dataclass(frozen=True, slots=True)
class Updates:
    targets: tuple[Any, ...]
    target_ids: tuple[str, ...]

    def __init__(self, *targets: FragmentHandle[Any, Any] | BoundFragment[Any]) -> None:
        ids = _logical_ids(targets)
        if len(ids) > MAX_PATCH_TARGETS:
            raise error(
                HED_TYPE_0006,
                title="Declared patch target limit exceeded",
                explanation=f"Updates listed {len(ids)} targets; max is {MAX_PATCH_TARGETS}.",
                remediation="Reduce declared fan-out.",
            )
        object.__setattr__(self, "targets", targets)
        object.__setattr__(self, "target_ids", ids)


def raise_conflicting_markers(detail: str) -> None:
    raise error(
        HED_TYPE_0002,
        title="Conflicting type-authoring markers",
        explanation=detail,
        remediation="Attach exactly one Hedron source marker per parameter.",
    )
