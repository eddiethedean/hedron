"""MORPH-048 explicit Deferred disposition; no Idiomorph admission."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from hedron_core import HedronError
from hedron_core.codes import HED_EXT_0003
from hedron_core.htmx_contract import safe_hx_swap
from hedron_core.htmx_extensions import MORPH_ADMITTED, parse_htmx_extensions
from hedron_sim.subset import UnsupportedSimFeatureError, require_supported_swap


def test_morph_is_not_admitted() -> None:
    assert MORPH_ADMITTED is False
    assert safe_hx_swap("morph") is False
    assert safe_hx_swap("morph:outerHTML") is False
    assert safe_hx_swap("innerHTML") is True
    with pytest.raises(HedronError) as exc:
        parse_htmx_extensions(["morph"])
    assert exc.value.diagnostic.code == HED_EXT_0003
    with pytest.raises(UnsupportedSimFeatureError):
        require_supported_swap("morphdom")
    asset = Path("packages/hedron-core/src/hedron_core/static/ext/idiomorph.js")
    assert not asset.is_file()


def test_gate_records_deferred_disposition() -> None:
    data = tomllib.loads(Path("docs/acceptance/release-gate-0.48.toml").read_text(encoding="utf-8"))
    morph = next(row for row in data["evidence"] if row["id"] == "MORPH-048")
    assert morph["state"] in {"Deferred", "Planned", "Verified"}
    if morph["state"] == "Deferred":
        assert morph.get("rationale")
        assert morph.get("destination")


def test_spike_matrix_documented() -> None:
    text = Path("docs/acceptance/htmx-morph-compat-048.toml").read_text(encoding="utf-8")
    for marker in (
        "forms_values_selection",
        "focus",
        "hx_preserve",
        "hedron-example",
        "hedron-chart",
        "hedron-map",
        "oob",
        "chromium",
        "firefox",
        "webkit",
    ):
        assert marker in text
