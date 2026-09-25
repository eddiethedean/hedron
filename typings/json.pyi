from collections.abc import Callable
from typing import TextIO


class JSONDecodeError(ValueError):
    msg: str
    doc: str
    pos: int
    lineno: int
    colno: int


def dumps(
    obj: object,
    *,
    skipkeys: bool = ...,
    ensure_ascii: bool = ...,
    check_circular: bool = ...,
    allow_nan: bool = ...,
    cls: type[object] | None = ...,
    indent: int | str | None = ...,
    separators: tuple[str, str] | None = ...,
    default: Callable[[object], object] | None = ...,
    sort_keys: bool = ...,
    **kwargs: object,
) -> str: ...


def loads(
    s: str | bytes | bytearray,
    *,
    cls: type[object] | None = ...,
    object_hook: Callable[[dict[str, object]], object] | None = ...,
    parse_float: Callable[[str], object] | None = ...,
    parse_int: Callable[[str], object] | None = ...,
    parse_constant: Callable[[str], object] | None = ...,
    object_pairs_hook: Callable[[list[tuple[str, object]]], object] | None = ...,
    **kwargs: object,
) -> object: ...


def dump(
    obj: object,
    fp: TextIO,
    *,
    skipkeys: bool = ...,
    ensure_ascii: bool = ...,
    check_circular: bool = ...,
    allow_nan: bool = ...,
    cls: type[object] | None = ...,
    indent: int | str | None = ...,
    separators: tuple[str, str] | None = ...,
    default: Callable[[object], object] | None = ...,
    sort_keys: bool = ...,
    **kwargs: object,
) -> None: ...


def load(fp: TextIO, *, cls: type[object] | None = ..., **kwargs: object) -> object: ...
