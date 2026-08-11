"""INTERACTIVE-028: Experimental interactive defaults stay opt-in."""

from __future__ import annotations

import pytest

from hedron_charts.optional_adapters import EXPERIMENTAL_ADAPTER_NAMES, optional_adapters
from hedron_charts.plugin import PLUGIN_META, register
from hedron_core.auto import Auto, clear_renderers_for_tests, list_renderers
from hedron_core.diagnostics import HedronError
from hedron_core.plugins import PluginContext, reset_explorer_panels_for_tests


@pytest.fixture(autouse=True)
def _charts_renderers() -> None:
    clear_renderers_for_tests()
    reset_explorer_panels_for_tests()
    register(PluginContext(PLUGIN_META))
    yield
    clear_renderers_for_tests()
    reset_explorer_panels_for_tests()


def test_list_renderers_maturity_labels() -> None:
    by_name = {spec.name: spec for spec in list_renderers()}
    assert by_name["matplotlib"].maturity == "supported"
    assert by_name["plotly"].maturity == "experimental"
    assert by_name["altair"].maturity == "experimental"


def test_auto_as_plotly_still_resolves() -> None:
    class _PlotlyLike:
        __module__ = "plotly.graph_objs._figure"

    auto = Auto(_PlotlyLike(), as_="plotly")
    node = auto.resolve()
    assert type(node).__name__ == "PlotlyChart"
    assert auto.decision is not None
    assert auto.decision.selected == "plotly"


def test_auto_without_as_rejects_experimental_plotly() -> None:
    from hedron_core.auto import get_last_auto_decision

    class _PlotlyLike:
        __module__ = "plotly.graph_objs._figure"

    with pytest.raises(HedronError) as exc:
        Auto(_PlotlyLike()).resolve()
    assert exc.value.diagnostic.code == "HED-AUTO-0004"
    rem = (exc.value.diagnostic.remediation or "").lower()
    assert "as_=" in rem or "as_='" in rem or "plotly" in rem
    assert "install hedron-charts" not in rem
    decision = get_last_auto_decision()
    assert decision is not None
    assert decision.selected != "plotly"
    assert any(name == "plotly" and "experimental" in reason for name, reason in decision.rejected)


def test_auto_matplotlib_resolves_without_as() -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    try:
        node = Auto(fig).resolve()
    finally:
        plt.close(fig)
    assert type(node).__name__ == "MatplotlibChart"


def test_optional_adapter_names_are_experimental_subset() -> None:
    names = {adapter.name for adapter in optional_adapters()}
    assert names
    assert names <= set(EXPERIMENTAL_ADAPTER_NAMES)
