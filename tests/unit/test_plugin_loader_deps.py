"""Plugin dependency graph: cycle, missing dep, topo order, duplicate."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.plugin_loader import _topo_sort, load_plugins
from hedron_core.plugins import PluginContext, PluginMeta
from hedron_core.registry import reset_registry_for_tests


def _ep(name: str, fn: object) -> object:
    class EP:
        def __init__(self) -> None:
            self.name = name

        def load(self) -> object:
            return fn

    return EP()


def _meta(name: str, *, depends_on: tuple[str, ...] = ()) -> PluginMeta:
    return PluginMeta(
        name=name,
        version="0.42.0",
        distribution=name,
        hedron_version=">=0.57,<0.58",
        depends_on=depends_on,
    )


def test_topo_sort_orders_dependencies_first() -> None:
    order = _topo_sort({"a": ("b",), "b": (), "c": ("a",)})
    assert order.index("b") < order.index("a") < order.index("c")


def test_topo_sort_rejects_cycles() -> None:
    with pytest.raises(HedronError, match="HED-PLUGIN-CYCLE|Plugin dependency cycle"):
        _topo_sort({"a": ("b",), "b": ("a",)})


def test_topo_sort_rejects_missing_dependency() -> None:
    with pytest.raises(HedronError, match="HED-PLUGIN-MISSING|Missing plugin dependency"):
        _topo_sort({"a": ("missing",)})


def test_load_plugins_rejects_dependency_cycle() -> None:
    reset_registry_for_tests()

    def a(_ctx: PluginContext) -> None:
        return None

    def b(_ctx: PluginContext) -> None:
        return None

    a.PLUGIN_META = _meta("a", depends_on=("b",))  # type: ignore[attr-defined]
    b.PLUGIN_META = _meta("b", depends_on=("a",))  # type: ignore[attr-defined]

    with pytest.raises(HedronError, match="HED-PLUGIN-CYCLE|cycle"):
        load_plugins(entry_points=[_ep("a", a), _ep("b", b)])


def test_load_plugins_rejects_duplicate_plugin_name() -> None:
    reset_registry_for_tests()

    def one(_ctx: PluginContext) -> None:
        return None

    def two(_ctx: PluginContext) -> None:
        return None

    one.PLUGIN_META = _meta("dup")  # type: ignore[attr-defined]
    two.PLUGIN_META = _meta("dup")  # type: ignore[attr-defined]

    with pytest.raises(HedronError, match="HED-PLUGIN-DUPLICATE|Duplicate plugin"):
        load_plugins(entry_points=[_ep("one", one), _ep("two", two)])
