"""ACCEL-RUST-014: native acceleration availability and correctness."""

from __future__ import annotations

from hedron_native import (
    escape_attr,
    escape_attr_python,
    escape_text,
    escape_text_python,
    native_available,
)


def test_native_escape_matches_python() -> None:
    samples = [
        "",
        "plain",
        "<script>&",
        "a\"b'c",
        "a\x00b",
        "<" * 1000 + "&" * 1000,
    ]
    for sample in samples:
        assert escape_text(sample) == escape_text_python(sample)
        assert escape_attr(sample) == escape_attr_python(sample)


def test_native_available_flag_is_bool() -> None:
    assert isinstance(native_available(), bool)
