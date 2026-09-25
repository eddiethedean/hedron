"""Typed access to values stored dynamically by ``argparse.Namespace``."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Protocol, cast

from hedron_core.typing_support import dynamic_attribute


class _Command(Protocol):
    def __call__(self, args: argparse.Namespace, /) -> int: ...


def string_argument(
    args: argparse.Namespace,
    name: str,
    default: str | None = None,
) -> str | None:
    value = dynamic_attribute(args, name, default)
    if value is None or isinstance(value, str):
        return value
    raise TypeError(f"argument {name!r} must be a string")


def boolean_argument(args: argparse.Namespace, name: str, default: bool = False) -> bool:
    value = dynamic_attribute(args, name, default)
    if isinstance(value, bool):
        return value
    raise TypeError(f"argument {name!r} must be a boolean")


def float_argument(args: argparse.Namespace, name: str, default: float) -> float:
    value = dynamic_attribute(args, name, default)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    raise TypeError(f"argument {name!r} must be numeric")


def path_argument(args: argparse.Namespace, name: str) -> str | Path | None:
    value = dynamic_attribute(args, name)
    if value is None or isinstance(value, (str, Path)):
        return value
    raise TypeError(f"argument {name!r} must be a path")


def run_command(args: argparse.Namespace) -> int:
    command = dynamic_attribute(args, "func")
    if not callable(command):
        raise TypeError("parsed command has no callable handler")
    return cast(_Command, command)(args)
