"""Strict recursive types for Python's TOML reader."""

from collections.abc import Callable
from typing import BinaryIO


class TOMLDecodeError(ValueError): ...


def load(
    fp: BinaryIO,
    /,
    *,
    parse_float: Callable[[str], object] = ...,
) -> dict[str, object]: ...


def loads(
    s: str,
    /,
    *,
    parse_float: Callable[[str], object] = ...,
) -> dict[str, object]: ...
