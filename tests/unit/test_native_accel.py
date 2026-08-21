"""ACCEL-RUST-014: native acceleration availability and correctness."""

from __future__ import annotations

import pytest

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


def test_native_available_respects_disable_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_NATIVE_DISABLE", "1")
    assert native_available() is False
    assert escape_text("<script>&") == escape_text_python("<script>&")
    monkeypatch.delenv("HEDRON_NATIVE_DISABLE", raising=False)
    # Clear disable: availability may be True or False depending on extension load,
    # but escapes must still match the Python reference implementation.
    _ = native_available()
    assert escape_text("a&b") == escape_text_python("a&b")
