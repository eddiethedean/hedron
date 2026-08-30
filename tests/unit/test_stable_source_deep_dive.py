"""Regression coverage for the Stable-package source deep dive."""

from __future__ import annotations

import math

import pytest
from fastapi import HTTPException

import edron as ed
from edron.errors import BindingError
from edron.navigation import NavigationError
from hedron.security.policy import SecurityPolicy
from hedron.security.redirects import redirect_external
from hedron.sse import _poll_interval, _retry_ms
from hedron_charts import compile_chart
from hedron_charts.limits import redact_rows
from hedron_charts.spec import (
    AccessibilityDef as ChartAccessibilityDef,
)
from hedron_charts.spec import (
    ChartSpec,
    DataRef,
    Encoding,
    MarkDef,
    TransformDef,
)
from hedron_core.browser import BrowserStorage, StorageQuotaExceeded
from hedron_core.cache import InMemoryCacheBackend, use_cache_backend
from hedron_core.channel import ChannelBudget, PageSessionChannel, RegionUpdate
from hedron_core.diagnostics import HedronError
from hedron_core.jobs import InMemoryJobBackend
from hedron_core.security_context import SecurityContext, SecurityContextError
from hedron_core.visualization import ChartEvent, VisualizationLimits, validate_chart_event
from hedron_data import DataChanges, InMemoryDataSource
from hedron_data.events import GridCellEvent, validate_grid_event
from hedron_maps import MapPolicy, MapSpec, RasterTiles, StaticImage, compile_map
from hedron_maps.proxy import assert_ssrf_safe
from hedron_maps.spec import AccessibilityDef as MapAccessibilityDef


def _chart_spec(rows: tuple[dict[str, object], ...], **kwargs: object) -> ChartSpec:
    return ChartSpec(
        data=DataRef(rows=rows),
        marks=(MarkDef(type="point", encodings={"x": Encoding(field="x")}),),
        accessibility=ChartAccessibilityDef(title="Chart", description="Description"),
        **kwargs,
    )


def test_cache_rejected_replacement_preserves_existing_value() -> None:
    backend = InMemoryCacheBackend(max_entries=2, max_bytes=4)
    backend.set("key", "ok")

    with pytest.raises(ValueError, match="exceeds max_bytes"):
        backend.set("key", "too large")

    assert backend.lookup("key") == (True, "ok")

    circular: list[object] = []
    circular.append(circular)
    with pytest.raises(ValueError, match="cannot be bounded"):
        backend.set("circular", circular)


def test_security_context_rejects_forged_local_fingerprint_and_nonfinite_clock() -> None:
    with pytest.raises(SecurityContextError, match="tampered"):
        SecurityContext(application_id="app", fingerprint="forged")

    context = SecurityContext(application_id="app")
    with pytest.raises(SecurityContextError, match="finite"):
        context.to_authenticated("secret", now=math.nan)

    future = context.to_authenticated("secret", now=2_200_000_000)
    restored = SecurityContext.from_authenticated(
        future,
        secret="secret",
        expected_application_id="app",
        now=2_200_000_000,
    )
    assert restored == context


def test_in_memory_jobs_reject_nonfinite_json_payloads() -> None:
    with pytest.raises(ValueError, match="JSON-compatible"):
        InMemoryJobBackend().submit("report", {"value": math.nan})


def test_browser_storage_enforces_constructor_quotas_and_value_isolation() -> None:
    with pytest.raises(ValueError, match="max_entries"):
        BrowserStorage("prefs", max_entries=0)
    with pytest.raises(StorageQuotaExceeded, match="max_entries"):
        BrowserStorage("prefs", max_entries=1, initial={"a": 1, "b": 2})

    original: dict[str, object] = {"nested": [1]}
    store = BrowserStorage("prefs", consent_granted=True, initial={"value": original})
    original["nested"] = [1, 2, 3]
    loaded = store.get("value")
    assert loaded == {"nested": [1]}
    assert isinstance(loaded, dict)
    loaded["nested"] = []
    assert store.get("value") == {"nested": [1]}


def test_channel_and_visualization_budgets_reject_invalid_bounds() -> None:
    with pytest.raises(ValueError, match="max_messages"):
        ChannelBudget(max_messages=0)
    with pytest.raises(ValueError, match="max_rows"):
        VisualizationLimits(max_rows=0)

    channel = PageSessionChannel(
        "channel",
        frozenset({"main"}),
        budget=ChannelBudget(max_message_bytes=32),
    )
    with pytest.raises(ValueError, match="max_message_bytes"):
        channel.prepare_region_update(RegionUpdate("main", "x" * 33))


def test_event_payloads_reject_nonfinite_json() -> None:
    with pytest.raises(ValueError, match="finite JSON"):
        validate_chart_event(ChartEvent(kind="click", trace_id="t", payload={"x": math.nan}))
    with pytest.raises(ValueError, match="finite JSON"):
        validate_grid_event(GridCellEvent(row_key="1", payload={"x": math.nan}))


@pytest.mark.parametrize(
    "url",
    (" https://example.com", "https://example.com\t.evil.test", "https://example%2ecom"),
)
def test_external_redirect_rejects_noncanonical_hosts(url: str) -> None:
    with pytest.raises(HTTPException):
        redirect_external(url, policy=SecurityPolicy(allow_external_redirects=True))


def test_sse_polling_bounds_nonfinite_and_extreme_backend_values() -> None:
    assert _poll_interval(math.inf, retry_after=2) == 2.0
    assert _poll_interval(None, retry_after=10_000) == 60.0
    assert _retry_ms(math.nan) == 1000
    assert _retry_ms(10_000) == 60_000


def test_edron_cache_eviction_and_invalidate_all_use_owning_backends() -> None:
    calls = 0

    @ed.cache_data(scope="public", max_entries=1)
    def load(value: str) -> str:
        nonlocal calls
        calls += 1
        return value

    first = InMemoryCacheBackend()
    second = InMemoryCacheBackend()
    with use_cache_backend(first):
        assert load("first") == "first"
    with use_cache_backend(second):
        assert load("second") == "second"
    with use_cache_backend(first):
        assert load("first") == "first"
    assert calls == 2

    load.invalidate_all()
    with use_cache_backend(first):
        assert load("first") == "first"
    with use_cache_backend(second):
        assert load("second") == "second"
    assert calls == 4


def test_edron_workspace_does_not_treat_zero_limit_as_missing() -> None:
    columns = (ed.Column("id"),)
    workspace = ed.DataWorkspace(
        "items",
        source=ed.DataSource.in_memory(
            [{"id": "1"}],
            columns=columns,
            projection_fields=("id",),
        ),
        columns=columns,
    )
    with pytest.raises(BindingError, match="paging"):
        workspace.request_from({"limit": "0"})


def test_edron_layout_rejects_boolean_column_counts() -> None:
    with pytest.raises(NavigationError, match="boolean"):
        ed.layout("grid", columns=True)
    with pytest.raises(NavigationError, match="integers"):
        ed.layout("grid", columns={"mobile": False})


def test_data_capacity_rejection_does_not_emit_accepted_audit() -> None:
    audited: list[DataChanges[dict[str, object]]] = []
    source = InMemoryDataSource(
        [{"id": "1"}],
        max_rows=1,
        writable_fields=frozenset({"name"}),
        audit_hook=audited.append,  # type: ignore[arg-type]
    )
    result = source.apply(DataChanges(inserts=({"id": "2", "name": "new"},)))
    assert result.ok is False
    assert audited == []


def test_chart_plan_uses_recursive_exact_key_redaction() -> None:
    plan = compile_chart(
        _chart_spec(({"x": 1, "secretary": "Ada", "nested": {"token": "sensitive"}},))
    )
    assert plan.transformed_rows[0]["secretary"] == "Ada"
    assert plan.transformed_rows[0]["nested"] == {"token": "***"}
    assert redact_rows([{"items": ({"api-key": "credential"},)}]) == [
        {"items": [{"api-key": "***"}]}
    ]


def test_chart_compiler_enforces_payload_and_direct_model_guards() -> None:
    with pytest.raises(HedronError, match="payload limit"):
        compile_chart(_chart_spec(({"x": 1, "blob": "x" * 1_100_000},)))
    with pytest.raises(HedronError, match="Prototype-pollution"):
        compile_chart(_chart_spec(({"x": 1},), composition={"__proto__": {}}))
    with pytest.raises(HedronError, match="not valid JSON"):
        compile_chart(_chart_spec(({"x": math.nan},)))


def test_chart_numeric_strings_and_fold_expansion_remain_bounded() -> None:
    plan = compile_chart(_chart_spec(({"x": "NaN"},)))
    assert plan.domains["x"] == [0, 1]

    fields = [f"field_{index}" for index in range(65)]
    with pytest.raises(HedronError, match="Transform row limit"):
        compile_chart(
            _chart_spec(
                ({"x": 1},),
                transforms=(TransformDef(op="fold", params={"fields": fields}),),
            )
        )


def test_map_rejects_hostless_https_and_preserves_nondefault_proxy_port() -> None:
    spec = MapSpec(
        basemap=RasterTiles(url="https:/tiles/{z}/{x}/{y}", attribution="Tiles"),
        accessibility=MapAccessibilityDef(title="Map", description="Description"),
        policy=MapPolicy(),
    )
    with pytest.raises(HedronError, match="host missing"):
        compile_map(spec)

    policy = MapPolicy(
        remote_requests_permitted=True,
        allowed_origins=("https://example.com",),
    )
    with pytest.raises(HedronError, match="not allowed"):
        assert_ssrf_safe("https://example.com:80/tile", policy, resolve_dns=False)
    with pytest.raises(HedronError, match="Port 0"):
        assert_ssrf_safe("https://example.com:0/tile", policy, resolve_dns=False)


def test_map_rejects_nonfinite_values_before_plan_serialization() -> None:
    with pytest.raises(ValueError, match="bounds must be finite"):
        StaticImage(src="/map.png", bounds=(math.nan, 0, 1, 2))

    raw = {
        "accessibility": {"title": "Map", "description": "Description"},
        "layers": [
            {
                "kind": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": [],
                    "metadata": {"score": math.inf},
                },
            }
        ],
    }
    with pytest.raises(HedronError, match="not valid JSON"):
        compile_map(raw)
