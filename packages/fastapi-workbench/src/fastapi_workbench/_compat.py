"""Compatibility helpers for the oldest supported Python runtime."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum as StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Python 3.10 backport of the subset of :class:`enum.StrEnum` we use."""

        @staticmethod
        def _generate_next_value_(
            name: str,
            start: int,
            count: int,
            last_values: list[object],
        ) -> str:
            del start, count, last_values
            return name.lower()

        def __str__(self) -> str:
            return str.__str__(self)
