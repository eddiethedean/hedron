"""INVENTORY-051 extras disposition honesty."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import __version__ as core_version
from hedron_core.plugin_loader import load_plugins
from hedron_core.plugins import get_feature_manifests, reset_explorer_panels_for_tests
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_extras.descriptor import extras_features, sandbox_feature
from hedron_extras.plugin import register as extras_register


class _EP:
    def __init__(self, name: str = "hedron_extras", target: object | None = None) -> None:
        self.name = name
        self._target = target if target is not None else extras_register

    def load(self) -> object:
        return self._target


def setup_function() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()


def test_inventory_lock_matches_runtime() -> None:
    data = tomllib.loads(
        Path("docs/acceptance/extras-capability-inventory-051.toml").read_text(encoding="utf-8")
    )
    rows = {row["id"]: row for row in data["capability"]}
    assert rows["EXTRAS-SANDBOX-001"]["maturity"] == "experimental"
    assert rows["EXTRAS-SANDBOX-001"]["supported_hedron_extras"] is False
    assert rows["EXTRAS-XUI-001"]["graduate_in_051"] is False
    load_plugins(enabled=["hedron_extras"], hedron_version=core_version, entry_points=[_EP()])
    names = {f.name for f in get_feature_manifests(plugin="hedron_extras")}
    assert names == {f.name for f in extras_features()}
    assert "sandbox" not in names
    assert "BrowserPythonSandbox" not in {m.name for m in get_registry().components()}
    assert sandbox_feature().maturity == "experimental"
