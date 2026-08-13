#!/usr/bin/env python3
"""Standalone repro: formula policy bypass via invisible Unicode."""

import sys
sys.path[:0] = [
    "packages/hedron-data/src",
    "packages/hedron-core/src",
]

from hedron_data.spreadsheet import _reject_or_sanitize, export_rows_ods, import_rows_ods
from hedron_core.diagnostics import HedronError

BYPASS_PAYLOADS = [
    ("\u200b=SUM(1,1)", "zero-width space (U+200B)"),
    ("\u202e=cmd|calc", "RTL override (U+202E)"),
    ("\u2060=HYPERLINK()", "word joiner (U+2060)"),
]

for payload, label in BYPASS_PAYLOADS:
    print(f"--- {label} ---")
    print(f"  repr: {payload!r}")
    try:
        _reject_or_sanitize(payload, formula_policy="reject")
        print("  reject policy: NOT REJECTED (BUG)")
    except HedronError:
        print("  reject policy: rejected OK")

    sanitized = _reject_or_sanitize(payload, formula_policy="sanitize")
    if sanitized.startswith("'"):
        print(f"  sanitize policy: prefixed OK -> {sanitized!r}")
    else:
        print(f"  sanitize policy: NOT NEUTRALIZED -> {sanitized!r} (BUG)")

print("\nExport/import path with ZWSP formula:")
from io import BytesIO
import zipfile

ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
cell = "\u200b=1+1"
content = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    f'<office:document-content xmlns:office="{ns_office}" '
    f'xmlns:table="{ns_table}" xmlns:text="{ns_text}">'
    "<office:body><office:spreadsheet>"
    '<table:table table:name="Sheet1">'
    "<table:table-row>"
    f'<table:table-cell><text:p>val</text:p></table:table-cell>'
    "</table:table-row>"
    "<table:table-row>"
    f'<table:table-cell><text:p>{cell}</text:p></table:table-cell>'
    "</table:table-row>"
    "</table:table></office:spreadsheet></office:body></office:document-content>"
)
buf = BytesIO()
with zipfile.ZipFile(buf, "w") as zf:
    zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
    zf.writestr("content.xml", content)
try:
    import_rows_ods(buf.getvalue(), formula_policy="reject")
    print("  ODS import with ZWSP formula: NOT REJECTED (BUG)")
except HedronError as e:
    print(f"  ODS import rejected: {e.diagnostic.code}")
