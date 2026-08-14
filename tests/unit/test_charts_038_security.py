"""SECURITY-038 adversarial suite + remediations #75/#81/#201/#239."""

from __future__ import annotations

import pytest
from tests.unit.charts_038_helpers import sample_spec

from hedron_charts.compile import parse_chart_spec
from hedron_charts.limits import reject_active_svg, reject_callbacks
from hedron_core.active_markup import active_markup_reason
from hedron_core.diagnostics import HedronError


def test_html_event_handler_strings_rejected() -> None:
    with pytest.raises(HedronError) as ei:
        reject_callbacks({"formatter": "onclick=alert(1)"})
    assert ei.value.diagnostic.code == "HED-CHART-0004"


def test_nul_byte_does_not_bypass_svg_scan() -> None:
    payload = "<svg><scr\x00ipt>alert(1)</script></svg>"
    assert active_markup_reason(payload) is not None
    with pytest.raises(HedronError):
        reject_active_svg(payload)


def test_remote_css_import_rejected() -> None:
    payload = '<svg><style>@import url("https://evil.example/x.css");</style></svg>'
    assert active_markup_reason(payload) == "remote css import"


def test_smil_remote_href_mutation_rejected() -> None:
    payload = '<svg><set attributeName="href" to="https://evil.example/x" begin="0s" /></svg>'
    reason = active_markup_reason(payload)
    assert reason in {"SMIL remote href mutation", "remote href"}


def test_spec_pollution_and_callbacks() -> None:
    raw = sample_spec().to_json_dict()
    raw["composition"] = {"constructor": {"prototype": {}}}
    with pytest.raises(HedronError):
        parse_chart_spec(raw)
