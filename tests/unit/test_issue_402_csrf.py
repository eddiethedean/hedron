"""#402: CSRF tokens_match must not raise on non-ASCII tokens."""

from __future__ import annotations

from hedron_core.csrf import tokens_match


def test_non_ascii_tokens_return_false() -> None:
    assert tokens_match("abc", "abé") is False
    assert tokens_match("café", "café") is True
    assert tokens_match("abc", "abcd") is False
