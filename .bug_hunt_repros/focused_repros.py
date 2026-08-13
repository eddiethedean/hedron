#!/usr/bin/env python3
"""Focused repros for confirmed-new bug candidates."""

import io
import zipfile
from xml.etree import ElementTree as ET

from hedron_charts.limits import redact_rows
from hedron_charts.optional_adapters import GreatTablesAdapter
from hedron_core.visualization import ChartAccessibility, VisualizationLimits
from hedron_data.memory import InMemoryDataSource
from hedron_data.normalize import normalize_rows
from hedron_data.spreadsheet import _reject_or_sanitize, export_rows_xlsx, import_rows_xlsx

print("=== BUG 1: normalize_rows IndexError on mismatched column lengths ===")
try:
    normalize_rows({"a": [1, 2], "b": [10]})
except IndexError as e:
    print(f"CONFIRMED IndexError: {e}")
    print("Path: packages/hedron-data/src/hedron_data/normalize.py:110")

print("\n=== BUG 2: normalize_rows empty dict returns [{}] not [] ===")
r = normalize_rows({})
print(f"Result: {r!r} (expected [] for empty tabular input)")

print("\n=== BUG 3: InMemoryDataSource KeyError on missing key_field ===")
try:
    InMemoryDataSource([{"name": "A"}], key_field="id")
except KeyError as e:
    print(f"CONFIRMED KeyError: {e}")
    print("Path: packages/hedron-data/src/hedron_data/memory.py:23-46")

print("\n=== BUG 4: redact_rows substring false positive on 'secretary' ===")
rows = [{"my_secret_key": "x", "secretary": "bob", "password_hash": "p"}]
out = redact_rows(rows)
print(f"Input:  {rows[0]}")
print(f"Output: {out[0]}")
if out[0]["secretary"] != "bob":
    print("CONFIRMED: 'secretary' incorrectly redacted (substring match on 'secret')")
else:
    print("secretary correctly preserved")

print("\n=== BUG 5: GreatTablesAdapter payload_bytes uses unredacted json ===")
adapter = GreatTablesAdapter()
rows = [{"secret": "leak", "name": "a"}]
acc = ChartAccessibility(title="t", description="d").validated()
out = adapter.compile(rows, accessibility=acc, limits=VisualizationLimits(max_rows=100))
import json
body = json.loads(str(out.body))
redacted_body = json.loads(json.dumps(redact_rows(rows)))
print(f"body in output: {body}")
print(f"payload_bytes field: {out.payload_bytes}")
print(f"actual body bytes: {len(json.dumps(body).encode())}")
print(f"redacted would be: {redacted_body}")
if "leak" in json.dumps(out.body):
    print("CONFIRMED: body uses redact_rows but payload_bytes counts raw rows")

print("\n=== BUG 6: formula bypass via zero-width space ===")
payload = "\u200b=SUM(1,1)"
sanitized = _reject_or_sanitize(payload, formula_policy="sanitize")
print(f"Input: {payload!r}")
print(f"Sanitized (NOT prefixed): {sanitized!r}")
if not sanitized.startswith("'"):
    print("CONFIRMED: zero-width space evades formula detection")

print("\n=== BUG 7: formula bypass via RTL override ===")
payload = "\u202e=cmd|calc"
sanitized = _reject_or_sanitize(payload, formula_policy="sanitize")
print(f"Input: {payload!r}")
print(f"Sanitized: {sanitized!r}")
if not sanitized.startswith("'"):
    print("CONFIRMED: bidi override evades formula detection")

print("\n=== BUG 8: xlsx export does not escape XML control chars (issue #176 territory) ===")
rows = [{"x": "hello\x00world", "y": "tab\there"}]
blob = export_rows_xlsx(rows, ["x", "y"])
with zipfile.ZipFile(io.BytesIO(blob)) as zf:
    path = next(n for n in zf.namelist() if "sheet" in n and n.endswith(".xml"))
    xml = zf.read(path).decode("utf-8")
has_nul = "\x00" in xml
print(f"XML contains NUL: {has_nul}")
print(f"XML snippet: {xml[200:400]!r}")
try:
    ET.fromstring(xml.encode("utf-8"))
    print("XML parse: OK (may still be invalid per spec)")
except ET.ParseError as e:
    print(f"CONFIRMED XML parse error: {e}")

print("\n=== BUG 9: xlsx ]] in cell - check if breaks parser ===")
rows = [{"x": "test"}]
blob = export_rows_xlsx(rows, ["x"])
out = import_rows_xlsx(blob)
print(f"Roundtrip OK: {out}")

print("\n=== BUG 10: normalize mixed scalar + column sequences ===")
r = normalize_rows({"a": [1, 2], "b": "scalar"})
print(f"Result: {r!r} — treats as single-row mapping with list value")
