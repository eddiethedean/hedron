"""Prove the core test environment does not install web frameworks."""

from __future__ import annotations

import importlib.util


def test_no_fastapi_flask_django() -> None:
    assert importlib.util.find_spec("fastapi") is None
    assert importlib.util.find_spec("flask") is None
    assert importlib.util.find_spec("django") is None
