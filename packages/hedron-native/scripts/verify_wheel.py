#!/usr/bin/env python3
"""Exercise the installed native wheel and its forced pure-Python fallback."""

from __future__ import annotations

import os

import hedron_native

CASES = (
    "",
    "Hedron & <components> with \"quotes\" and 'apostrophes'",
    "NUL\x00 removed; unicode: λ / 東京",
    "<script>alert('x')</script> & data",
)


def main() -> None:
    if not hedron_native.native_available():
        raise RuntimeError("installed wheel did not load its native extension")
    for value in CASES:
        if hedron_native.escape_text(value) != hedron_native.escape_text_python(value):
            raise AssertionError(f"native text escape differs for {value!r}")
        if hedron_native.escape_attr(value) != hedron_native.escape_attr_python(value):
            raise AssertionError(f"native attribute escape differs for {value!r}")

    previous = os.environ.get("HEDRON_NATIVE_DISABLE")
    os.environ["HEDRON_NATIVE_DISABLE"] = "1"
    try:
        if hedron_native.native_available():
            raise AssertionError("native extension ignored HEDRON_NATIVE_DISABLE")
        for value in CASES:
            if hedron_native.escape_text(value) != hedron_native.escape_text_python(value):
                raise AssertionError(f"Python text fallback differs for {value!r}")
            if hedron_native.escape_attr(value) != hedron_native.escape_attr_python(value):
                raise AssertionError(f"Python attribute fallback differs for {value!r}")
    finally:
        if previous is None:
            os.environ.pop("HEDRON_NATIVE_DISABLE", None)
        else:
            os.environ["HEDRON_NATIVE_DISABLE"] = previous


if __name__ == "__main__":
    main()
