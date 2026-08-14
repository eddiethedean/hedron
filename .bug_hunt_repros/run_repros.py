#!/usr/bin/env python3
"""Minimal repro scripts for hedron-data / hedron-charts bug hunt."""

from __future__ import annotations

import io
import sys
import threading
import traceback
import zipfile
from xml.etree import ElementTree as ET

print("=" * 60)
print("BUG HUNT REPROS — hedron-data / hedron-charts")
print("=" * 60)

failures: list[tuple[str, str]] = []


def check(name: str, fn) -> None:
    print(f"\n--- {name} ---")
    try:
        fn()
        print("PASS (no bug)")
    except Exception as exc:
        msg = f"{type(exc).__name__}: {exc}"
        print(f"FAIL: {msg}")
        traceback.print_exc()
        failures.append((name, msg))


# ── hedron-data: normalize ──────────────────────────────────────────────

from hedron_data.normalize import normalize_rows


def repro_normalize_mismatched_column_lengths() -> None:
    """Column-oriented dict with unequal sequence lengths."""
    data = {"a": [1, 2], "b": [10]}
    result = normalize_rows(data)
    print(f"result={result!r}")
    if len(result) != 1 or result[0].get("b") is None:
        raise AssertionError(f"Expected silent truncation or error; got {result!r}")


def repro_normalize_empty_column_dict() -> None:
    result = normalize_rows({})
    print(f"result={result!r}")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def repro_normalize_mixed_column_types() -> None:
    """Dict with one column sequence and one scalar."""
    data = {"a": [1, 2], "b": "scalar"}
    try:
        result = normalize_rows(data)
        print(f"result={result!r}")
    except Exception as exc:
        print(f"Raised (expected?): {exc}")


def repro_normalize_unicode_keys() -> None:
    rows = [{"名前": "太郎", "emoji": "🎉"}]
    result = normalize_rows(rows)
    assert result[0]["名前"] == "太郎"
    assert result[0]["emoji"] == "🎉"


def repro_normalize_none_values() -> None:
    result = normalize_rows([{"a": None, "b": 1}])
    assert result[0]["a"] is None


# ── hedron-data: spreadsheet ────────────────────────────────────────────

from hedron_data.spreadsheet import (
    export_rows_ods,
    export_rows_xlsx,
    import_rows_ods,
    import_rows_xlsx,
    _reject_or_sanitize,
)


def repro_xlsx_empty_zip() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        pass
    try:
        import_rows_xlsx(buf.getvalue())
    except Exception as exc:
        print(f"Raised: {type(exc).__name__}: {exc}")


def repro_xlsx_invalid_bytes() -> None:
    try:
        import_rows_xlsx(b"not a zip")
    except Exception as exc:
        print(f"Raised: {type(exc).__name__}: {exc}")


def repro_xlsx_unicode_roundtrip() -> None:
    rows = [{"id": "1", "text": "café 日本語 🎉"}]
    blob = export_rows_xlsx(rows, ["id", "text"])
    out = import_rows_xlsx(blob)
    if out[0]["text"] != "café 日本語 🎉":
        raise AssertionError(f"Unicode corruption: {out[0]['text']!r}")


def repro_xlsx_xml_breakout() -> None:
    """Cell value containing XML-breaking sequences."""
    rows = [{"x": "]]>", "y": "a&b<c>d"}]
    blob = export_rows_xlsx(rows, ["x", "y"])
    # Must parse as valid XML
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        path = next(n for n in zf.namelist() if "sheet" in n and n.endswith(".xml"))
        xml = zf.read(path)
    ET.fromstring(xml)  # raises if malformed
    out = import_rows_xlsx(blob)
    print(f"imported={out!r}")


def repro_formula_bidi_override() -> None:
    """RTL override char before formula — evasion attempt."""
    payload = "\u202e=cmd"
    try:
        _reject_or_sanitize(payload, formula_policy="reject")
        print("NOT rejected — potential formula bypass")
    except Exception as exc:
        print(f"Rejected: {exc}")


def repro_formula_zero_width_space() -> None:
    payload = "\u200b=cmd"
    try:
        _reject_or_sanitize(payload, formula_policy="reject")
        print("NOT rejected — potential formula bypass")
    except Exception as exc:
        print(f"Rejected: {exc}")


def repro_ods_empty_content() -> None:
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}" '
        f'xmlns:table="{ns_table}">'
        "<office:body><office:spreadsheet>"
        '<table:table table:name="Sheet1"/>'
        "</office:spreadsheet></office:body></office:document-content>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content)
    result = import_rows_ods(buf.getvalue())
    print(f"result={result!r}")


def repro_xlsx_export_empty_rows() -> None:
    blob = export_rows_xlsx([], ["id", "name"])
    out = import_rows_xlsx(blob)
    print(f"out={out!r}")


# ── hedron-data: InMemoryDataSource ─────────────────────────────────────

from hedron_data.memory import InMemoryDataSource
from hedron_data.sources import CellUpdate, DataChanges, DataQuery


def repro_inmemory_missing_key_field() -> None:
    try:
        InMemoryDataSource([{"name": "A"}], key_field="id")
    except KeyError as exc:
        print(f"KeyError (crash): {exc}")
        raise


def repro_inmemory_empty() -> None:
    src = InMemoryDataSource([], key_field="id")
    page = src.fetch(DataQuery(limit=10))
    print(f"rows={page.rows!r} total={page.total}")


def repro_inmemory_sort_unicode() -> None:
    src = InMemoryDataSource(
        [{"id": "1", "name": "zebra"}, {"id": "2", "name": "äpfel"}, {"id": "3", "name": "Apple"}],
        key_field="id",
    )
    page = src.fetch(DataQuery(sort=(("name", "asc"),), limit=10))
    names = [r["name"] for r in page.rows]
    print(f"sorted names={names!r}")


def repro_inmemory_concurrent_same_row() -> None:
    """Two threads update same row — one should win, no crash."""
    src = InMemoryDataSource(
        [{"id": "1", "name": "A"}],
        writable_fields=frozenset({"name"}),
        version="1",
    )
    barrier = threading.Barrier(2)
    results: list[bool] = []

    def worker(val: str) -> None:
        barrier.wait(timeout=5)
        r = src.apply(DataChanges(updates=(CellUpdate(row_key="1", field="name", value=val),)))
        results.append(r.ok)

    threads = [
        threading.Thread(target=worker, args=("X",)),
        threading.Thread(target=worker, args=("Y",)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    page = src.fetch(DataQuery(limit=1))
    print(f"results={results} final={page.rows[0]['name']!r}")


# ── hedron-data: DataQuery ──────────────────────────────────────────────

from hedron_data.sources import DataQuery


def repro_dataquery_sort_without_allowlist() -> None:
    """Invalid sort direction without allowlist — issue #117 territory."""
    q = DataQuery(sort=(("name", "invalid"),))
    try:
        q.validated()
        print("NOT rejected — invalid sort accepted")
    except ValueError as exc:
        print(f"Rejected: {exc}")


def repro_dataquery_limit_zero() -> None:
    q = DataQuery(limit=0)
    try:
        q.validated()
        print("NOT rejected — limit=0 accepted")
    except ValueError as exc:
        print(f"Rejected: {exc}")


# ── hedron-charts: limits ───────────────────────────────────────────────

from hedron_charts.limits import reject_callbacks, reject_remote_urls, redact_rows
from hedron_core.diagnostics import HedronError


def repro_callbacks_onclick_in_formatter() -> None:
    spec = {
        "options": {"plugins": {"tooltip": {"callbacks": {"label": "function(ctx){return ctx}"}}}}
    }
    try:
        reject_callbacks(spec)
        print("NOT rejected — onclick/callback bypass (#75 territory)")
    except HedronError as exc:
        print(f"Rejected: {exc.diagnostic.code}")


def repro_callbacks_html_event_handler_string() -> None:
    spec = {"label": '<img src=x onerror="alert(1)">'}
    try:
        reject_callbacks(spec)
        print("NOT rejected — HTML event handler in string")
    except HedronError as exc:
        print(f"Rejected: {exc.diagnostic.code}")


def repro_remote_url_in_nested_data_value() -> None:
    spec = {"data": {"values": [{"url": "https://evil.com/x.png"}]}}
    try:
        reject_remote_urls(spec)
        print("NOT rejected — url in data values")
    except HedronError as exc:
        print(f"Rejected: {exc.diagnostic.code}")


def repro_remote_url_schema_field() -> None:
    spec = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json", "mark": "bar"}
    try:
        reject_remote_urls(spec)
        print("NOT rejected — $schema https URL")
    except HedronError as exc:
        print(f"Rejected: {exc.diagnostic.code}")


def repro_redact_partial_match() -> None:
    rows = [{"my_secret_key": "x", "secretary": "bob"}]
    out = redact_rows(rows)
    print(f"redacted={out!r}")
    if out[0].get("secretary") == "***":
        raise AssertionError("False positive redaction on 'secretary'")


# ── hedron-charts: optional adapters ────────────────────────────────────

from hedron_charts.optional_adapters import GreatTablesAdapter, downsample_plotly_body
from hedron_charts.host_render import extract_folium_payload
from hedron_core.visualization import ChartAccessibility, VisualizationLimits


def repro_great_tables_payload_bytes_mismatch() -> None:
    adapter = GreatTablesAdapter()
    rows = [{"a": 1}, {"a": 2}]
    acc = ChartAccessibility(title="t").validated()
    out = adapter.compile(rows, accessibility=acc, limits=VisualizationLimits(max_rows=100))
    body_parsed = out.body
    meta_rows = out.metadata.get("rows")
    print(
        f"payload_bytes={out.payload_bytes} body_len={len(str(body_parsed))} meta_rows={meta_rows}"
    )


def repro_downsample_empty() -> None:
    result = downsample_plotly_body({}, max_points=100)
    print(f"result={result!r}")


def repro_downsample_non_list_data() -> None:
    result = downsample_plotly_body({"data": "not a list"}, max_points=100)
    print(f"result={result!r}")


def repro_folium_empty_mapping() -> None:
    try:
        extract_folium_payload({})
    except Exception as exc:
        print(f"Raised: {type(exc).__name__}: {exc}")


def repro_folium_null_location() -> None:
    result = extract_folium_payload({"type": "folium", "center": None})
    print(f"result={result!r}")


# ── hedron-charts: components empty data ────────────────────────────────

from hedron_charts.components import LineChart, BarChart


def repro_linechart_empty_data() -> None:
    chart = LineChart([], x="x", y="y", title="Empty")
    node = chart.render()
    print(f"rendered empty line chart: {type(node).__name__}")


def repro_barchart_empty_data() -> None:
    chart = BarChart([], x="x", y="y", title="Empty")
    node = chart.render()
    print(f"rendered empty bar chart: {type(node).__name__}")


# Run all
REPROS = [
    ("normalize: mismatched column lengths", repro_normalize_mismatched_column_lengths),
    ("normalize: empty column dict", repro_normalize_empty_column_dict),
    ("normalize: mixed column types", repro_normalize_mixed_column_types),
    ("normalize: unicode", repro_normalize_unicode_keys),
    ("normalize: None values", repro_normalize_none_values),
    ("xlsx: empty zip", repro_xlsx_empty_zip),
    ("xlsx: invalid bytes", repro_xlsx_invalid_bytes),
    ("xlsx: unicode roundtrip", repro_xlsx_unicode_roundtrip),
    ("xlsx: XML breakout chars", repro_xlsx_xml_breakout),
    ("formula: bidi override prefix", repro_formula_bidi_override),
    ("formula: zero-width space prefix", repro_formula_zero_width_space),
    ("ods: empty spreadsheet", repro_ods_empty_content),
    ("xlsx: export empty rows", repro_xlsx_export_empty_rows),
    ("inmemory: missing key_field", repro_inmemory_missing_key_field),
    ("inmemory: empty source", repro_inmemory_empty),
    ("inmemory: sort unicode", repro_inmemory_sort_unicode),
    ("inmemory: concurrent same row", repro_inmemory_concurrent_same_row),
    ("dataquery: invalid sort no allowlist", repro_dataquery_sort_without_allowlist),
    ("dataquery: limit zero", repro_dataquery_limit_zero),
    ("charts: callback in nested formatter", repro_callbacks_onclick_in_formatter),
    ("charts: HTML event handler string", repro_callbacks_html_event_handler_string),
    ("charts: url in data values", repro_remote_url_in_nested_data_value),
    ("charts: $schema https URL", repro_remote_url_schema_field),
    ("charts: redact false positive", repro_redact_partial_match),
    ("charts: great-tables payload bytes", repro_great_tables_payload_bytes_mismatch),
    ("charts: downsample empty", repro_downsample_empty),
    ("charts: downsample bad data type", repro_downsample_non_list_data),
    ("charts: folium empty mapping", repro_folium_empty_mapping),
    ("charts: folium null center", repro_folium_null_location),
    ("charts: LineChart empty data", repro_linechart_empty_data),
    ("charts: BarChart empty data", repro_barchart_empty_data),
]

for name, fn in REPROS:
    check(name, fn)

print("\n" + "=" * 60)
print(f"SUMMARY: {len(failures)} failure(s)")
for name, msg in failures:
    print(f"  • {name}: {msg}")
if failures:
    sys.exit(1)
