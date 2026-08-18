"""HEADLESS-050 CLI shares explorer services; SARIF stays diagnostics_to_sarif."""

from __future__ import annotations

import inspect

from hedron.cli.commands import check as check_mod
from hedron.cli.commands import graph as graph_mod
from hedron.cli.commands import inspect as inspect_mod
from hedron.cli.commands import routes as routes_mod
from hedron_core.diagnostics import diagnostics_to_sarif
from hedron_explorer.services.catalog import graph_json


def test_graph_json_names_inverse_consumers_divergence() -> None:
    payload = graph_json()
    assert "inverse_consumers" not in payload
    assert payload["divergence"]["cli_only"] == ["inverse_consumers"]


def test_cli_commands_call_explorer_services() -> None:
    assert "hedron_explorer.services.catalog" in inspect.getsource(graph_mod)
    assert "hedron_explorer.services.catalog" in inspect.getsource(inspect_mod)
    assert "hedron_explorer.services.catalog" in inspect.getsource(routes_mod)
    assert "hedron_explorer.services" in inspect.getsource(check_mod)
    assert "skipped (not installed)" in inspect.getsource(graph_mod)
    assert "diagnostics_to_sarif" in inspect.getsource(check_mod)


def test_sarif_writer_is_core_function() -> None:
    assert diagnostics_to_sarif.__module__ == "hedron_core.diagnostics"
