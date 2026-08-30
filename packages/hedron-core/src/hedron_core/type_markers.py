"""Framework-neutral annotation markers used by host adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["FormBody", "ViewParams"]


@dataclass(frozen=True, slots=True)
class ViewParams:
    source: Literal["path", "query", "path_query"] = "path_query"


@dataclass(frozen=True, slots=True)
class FormBody:
    encoding: Literal["urlencoded", "multipart", "auto"] = "auto"
