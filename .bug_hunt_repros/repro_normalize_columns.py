#!/usr/bin/env python3
"""Standalone repro: normalize_rows column-oriented dict bugs."""

import sys

sys.path[:0] = [
    "packages/hedron-data/src",
    "packages/hedron-core/src",
]

from hedron_data.normalize import normalize_rows

print("Case 1: empty column first -> silent data loss")
r1 = normalize_rows({"a": [], "b": [1, 2]})
print(f"  input={{'a': [], 'b': [1, 2]}}")
print(f"  output={r1!r}")
assert r1 == [], f"unexpected: {r1!r}"

print("\nCase 2: empty column second -> IndexError")
try:
    normalize_rows({"b": [1, 2], "a": []})
    print("  ERROR: no exception raised")
    sys.exit(1)
except IndexError as e:
    print(f"  IndexError: {e}")

print("\nCase 3: length mismatch -> IndexError")
try:
    normalize_rows({"a": [1, 2], "b": [10]})
    sys.exit(1)
except IndexError as e:
    print(f"  IndexError: {e}")

print("\nAll cases confirm inconsistent column-oriented dict handling.")
