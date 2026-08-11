"""NATIVE-028: HEDRON_NATIVE_DISABLE fallback + escape parity."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from hedron_native import (
    escape_attr,
    escape_attr_python,
    escape_text,
    escape_text_python,
    native_disabled_by_env,
)

_SAMPLES = (
    "",
    "plain",
    "<script>alert(1)</script>",
    'a"b\'c',
    "nul\x00byte",
    "café <tag>&",
    "<" * 50 + "&" * 50,
)


def test_escape_parity_with_python_reference() -> None:
    for sample in _SAMPLES:
        assert escape_text(sample) == escape_text_python(sample)
        assert escape_attr(sample) == escape_attr_python(sample)


def test_native_disabled_by_env_reads_live_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEDRON_NATIVE_DISABLE", raising=False)
    assert native_disabled_by_env() is False
    monkeypatch.setenv("HEDRON_NATIVE_DISABLE", "1")
    assert native_disabled_by_env() is True


def test_hedron_native_disable_subprocess_forces_python_path() -> None:
    code = (
        "from hedron_native import ("
        "escape_text, escape_text_python, native_available, native_disabled_by_env);"
        "assert native_disabled_by_env() is True;"
        "assert native_available() is False;"
        "assert escape_text('<script>') == escape_text_python('<script>');"
        "print('ok')"
    )
    env = {**os.environ, "HEDRON_NATIVE_DISABLE": "1"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    assert "ok" in proc.stdout
