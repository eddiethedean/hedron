from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Download:
    identifier: str


def download(identifier: str) -> Download:
    if not isinstance(identifier, str) or not identifier:
        raise ValueError("download identifier must be a non-empty string")
    return Download(identifier)
