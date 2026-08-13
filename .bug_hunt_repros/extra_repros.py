#!/usr/bin/env python3
"""Additional edge-case repros."""

from hedron_core.diagnostics import HedronError
from hedron_data.advanced import evaluate_formula, pivot_rows, rows_to_tree
from hedron_data.collab import merge_changes
from hedron_data.normalize import normalize_rows
from hedron_data.sources import CellUpdate, DataChanges
from hedron_data.spreadsheet import export_rows_xlsx, import_rows_xlsx

print("=== A: column dict one empty column ===")
try:
    r = normalize_rows({"a": [], "b": [1, 2]})
    print(f"Result: {r!r}")
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")

print("\n=== B: rows_to_tree duplicate ids (silent overwrite) ===")
rows = [
    {"id": "1", "parent_id": None, "name": "first"},
    {"id": "1", "parent_id": None, "name": "second"},
]
tree = rows_to_tree(rows)
print(f"Tree nodes: {[(n.key, n.data.get('name')) for n in tree]}")

print("\n=== C: evaluate_formula division by zero ===")
try:
    r = evaluate_formula("=1/0", {"x": 1})
    print(f"Result: {r!r}")
except HedronError as e:
    print(f"HedronError: {e.diagnostic.code} — {e.diagnostic.explanation}")

print("\n=== D: evaluate_formula empty after strip ===")
try:
    evaluate_formula("=   ", {"x": 1})
except HedronError as e:
    print(f"Rejected: {e.diagnostic.code}")

print("\n=== E: pivot_rows empty input ===")
print(f"pivot_rows([]): {pivot_rows([], index='i', columns='c', values='v')!r}")

print("\n=== F: merge_changes conflicting deletes ===")
local = DataChanges(deletes=("1", "2"))
remote = DataChanges(deletes=("2", "3"))
result = merge_changes("1", local, remote)
print(f"ok={result.ok} merged deletes={result.accepted.deletes if result.accepted else None}")

print("\n=== G: xlsx roundtrip with ampersand/quote ===")
rows = [{"x": 'say "hello" & goodbye'}]
blob = export_rows_xlsx(rows, ["x"])
out = import_rows_xlsx(blob)
print(f"Roundtrip: {out[0]['x']!r}")

print("\n=== H: normalize generator refused ===")
try:
    normalize_rows(x for x in [{"a": 1}])
except HedronError as e:
    print(f"Refused lazy: {e.diagnostic.code}")
except Exception as e:
    print(f"Unexpected: {type(e).__name__}: {e}")

print("\n=== I: normalize empty list ===")
print(f"normalize_rows([]): {normalize_rows([])!r}")

print("\n=== J: normalize column dict all empty lists ===")
print(f"normalize_rows({{'a': [], 'b': []}}): {normalize_rows({'a': [], 'b': []})!r}")
