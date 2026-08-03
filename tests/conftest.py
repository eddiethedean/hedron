"""Shared test fixtures."""

from __future__ import annotations

import pytest

from hedron_core import reset_registry_for_tests


@pytest.fixture(autouse=True)
def _reset_hedron_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield
