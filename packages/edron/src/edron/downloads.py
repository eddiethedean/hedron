from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class Download:
    identifier: str


def download(identifier: str) -> Download:
    raw_identifier: object = identifier
    if not isinstance(cast(Any, raw_identifier), str) or not raw_identifier:
        raise ValueError("download identifier must be a non-empty string")
    return Download(identifier)
