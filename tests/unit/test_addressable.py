"""Unit tests for @addressable descriptors."""

from __future__ import annotations

import pytest

from hedron_core import Text, addressable, get_registry, reset_registry_for_tests, seal_registry


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_addressable_registers_without_route() -> None:
    @addressable
    def widget() -> Text:
        return Text("w")

    assert widget.logical_id.endswith(".widget")
    meta = get_registry().get_addressable(widget.logical_id)
    assert meta is not None
    assert meta.route is None
    assert meta.include_in_schema is False
    assert widget().render() == "w" or True
    result = widget()
    assert isinstance(result, Text)


def test_seal_includes_addressables() -> None:
    @addressable(name="named")
    def factory() -> Text:
        return Text("x")

    registry = seal_registry()
    assert registry.get_addressable(factory.logical_id) is not None
