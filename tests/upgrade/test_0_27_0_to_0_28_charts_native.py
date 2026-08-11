"""0.28 charts/native upgrade fixtures from Published v0.27.0 goldens."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from hedron_charts.optional_adapters import EXPERIMENTAL_ADAPTER_NAMES, optional_adapters
from hedron_charts.pins import RUNTIME_PINS
from hedron_native import escape_attr_python, escape_text_python

ROOT = Path(__file__).resolve().parents[2]
GOLDENS = Path(__file__).resolve().parent / "goldens_0_27_0"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-028.toml"


def _load(name: str) -> dict:
    return json.loads((GOLDENS / name).read_text(encoding="utf-8"))


def _inventory() -> dict:
    return tomllib.loads(INVENTORY.read_text(encoding="utf-8"))


def test_baseline_is_v0_27_0() -> None:
    for name in (
        "charts_static.json",
        "charts_interactive.json",
        "native_escape.json",
        "charts_supply.json",
    ):
        assert _load(name)["baseline"] == "v0.27.0"


def test_charts_static_keys_match_inventory() -> None:
    golden = _load("charts_static.json")
    inv = _inventory()["hedron-charts"]["supported"]
    assert golden["supported_keys"] == inv
    from hedron_charts import AreaChart, BarChart, LineChart, ScatterChart

    for name in golden["beginner_components"]:
        assert name in {
            LineChart.__name__,
            BarChart.__name__,
            AreaChart.__name__,
            ScatterChart.__name__,
        }
    assert golden["static_adapter"] == "matplotlib"
    assert "HED-CHART-0002" in golden["payload_budget_codes"]
    assert "HED-CHART-0003" in golden["payload_budget_codes"]


def test_charts_interactive_experimental_alignment() -> None:
    golden = _load("charts_interactive.json")
    inv = _inventory()["hedron-charts"]["experimental"]
    assert golden["experimental"] == inv
    assert golden["supported_auto_default"] == "matplotlib"
    assert set(golden["production_default_excluded"]) == {"plotly", "altair"}
    live_names = {adapter.name for adapter in optional_adapters()}
    assert live_names <= set(EXPERIMENTAL_ADAPTER_NAMES)
    assert live_names <= set(golden["experimental"])


def test_native_escape_samples_match_python_reference() -> None:
    golden = _load("native_escape.json")
    assert golden["disable_env"] == "HEDRON_NATIVE_DISABLE"
    for sample in golden["samples"]:
        raw = sample["input"]
        assert escape_text_python(raw) == sample["escape_text"]
        assert escape_attr_python(raw) == sample["escape_attr"]
    inv_supported = set(_inventory()["hedron-native"]["supported"])
    assert set(golden["supported_keys"]) <= inv_supported


def test_charts_supply_pins_and_docs() -> None:
    golden = _load("charts_supply.json")
    for key in golden["pin_keys"]:
        assert key in RUNTIME_PINS
    for rel in (
        golden["license_inventory_doc"],
        golden["offline_install_doc"],
        golden["sbom_script"],
    ):
        assert (ROOT / rel).is_file(), rel
    assert golden["matplotlib_maturity"] == "Supported"
    assert golden["cdn_unpinned_excluded"] is True
    assert "cdn_unpinned_chart_runtimes" in _inventory()["hedron-charts"]["excluded"]
