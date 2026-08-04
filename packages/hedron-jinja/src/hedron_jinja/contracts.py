"""Typed template contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

from hedron_core import Model, RenderMode

ViewT = TypeVar("ViewT", bound=Model)


class TemplateSource(StrEnum):
    APPLICATION = "application"
    PACKAGE = "package"


@dataclass(frozen=True, slots=True)
class TemplateSpec(Generic[ViewT]):
    name: str
    view_type: type[ViewT] | None = None
    mode: RenderMode = RenderMode.FRAGMENT
    source: TemplateSource = TemplateSource.APPLICATION
    logical_id: str | None = None

    def __post_init__(self) -> None:
        _validate_template_name(self.name)
        if self.logical_id is None:
            object.__setattr__(self, "logical_id", f"{self.source.value}:{self.name}")


def _validate_template_name(name: str) -> None:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ValueError(f"invalid canonical template name: {name!r}")
    segments = name.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ValueError(f"invalid canonical template name: {name!r}")
