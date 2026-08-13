#!/usr/bin/env python3
import sys
sys.path[:0] = ["packages/hedron-data/src", "packages/hedron-charts/src", "packages/hedron-core/src"]

from hedron_data.memory import InMemoryDataSource
from hedron_charts.limits import redact_rows
from hedron_data.advanced import rows_to_tree

print("=== InMemoryDataSource KeyError on missing key_field ===")
try:
    InMemoryDataSource([{"name": "Alice"}], key_field="id")
except KeyError as e:
    print(f"KeyError: {e}")

print("\n=== redact_rows false positive ===")
rows = [{"secretary": "bob", "password": "x", "notes": "ok"}]
print(f"in:  {rows[0]}")
print(f"out: {redact_rows(rows)[0]}")

print("\n=== rows_to_tree duplicate id silent overwrite ===")
tree = rows_to_tree([
    {"id": "1", "parent_id": None, "label": "first"},
    {"id": "1", "parent_id": None, "label": "second"},
])
print(f"surviving label: {tree[0].data['label']!r} (expected 'first' or error, got 'second')")

print("\n=== normalize_rows empty dict -> [{}] ===")
from hedron_data.normalize import normalize_rows
print(f"normalize_rows({{}}) = {normalize_rows({})!r}")
