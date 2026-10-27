"""Stable compatibility import paths backed by the Python standard library."""

from __future__ import annotations

import tomllib as tomllib
from enum import StrEnum as StrEnum

__all__ = ["StrEnum", "tomllib"]
