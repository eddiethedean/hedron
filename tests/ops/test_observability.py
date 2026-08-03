"""Observability redaction corpus."""

from __future__ import annotations

from hedron.ops import redacted_log_extra


def test_nested_redaction() -> None:
    payload = redacted_log_extra({"outer": {"api_key": "x", "ok": 1}})
    assert payload["outer"]["api_key"] == "[redacted]"
    assert payload["outer"]["ok"] == 1
