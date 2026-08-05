"""Spreadsheet import/export beyond CSV (xlsx/ods) with formula sandbox."""

# ruff: noqa: E501

from __future__ import annotations

import csv
import io
import zipfile
from collections.abc import Mapping, Sequence
from xml.etree import ElementTree as ET

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue
from hedron_data.sources import ColumnSchema

__all__ = [
    "export_rows_ods",
    "export_rows_xlsx",
    "import_rows_ods",
    "import_rows_xlsx",
]


def _reject_or_sanitize(value: str, *, formula_policy: str) -> str:
    if value.startswith("="):
        if formula_policy == "reject":
            raise error(
                "HED-DATA-0040",
                title="Spreadsheet formula rejected",
                explanation="Imported cells must not contain formulas under reject policy.",
                remediation="Strip formulas before import or use formula_policy='sanitize'.",
            )
        if formula_policy == "sanitize":
            return value.lstrip("=")
        raise ValueError(f"Unknown formula_policy {formula_policy!r}")
    return value


def export_rows_xlsx(
    rows: Sequence[Mapping[str, JsonValue]],
    columns: Sequence[ColumnSchema] | Sequence[str],
) -> bytes:
    names = [c.name if isinstance(c, ColumnSchema) else str(c) for c in columns]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>
""",
        )
        zf.writestr(
            "xl/workbook.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets>
</workbook>
""",
        )
        sheet_rows = [names] + [[str(row.get(name, "")) for name in names] for row in rows]
        row_xml = []
        for r_idx, values in enumerate(sheet_rows, start=1):
            cells = []
            for c_idx, value in enumerate(values):
                col = chr(ord("A") + c_idx)
                ref = f"{col}{r_idx}"
                esc = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{esc}</t></is></c>')
            row_xml.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
        zf.writestr(
            "xl/worksheets/sheet1.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"<sheetData>{''.join(row_xml)}</sheetData></worksheet>",
        )
    return buf.getvalue()


def import_rows_xlsx(
    data: bytes,
    *,
    formula_policy: str = "reject",
) -> list[dict[str, JsonValue]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        path = next(
            (n for n in zf.namelist() if "worksheets/sheet" in n and n.endswith(".xml")), None
        )
        if path is None:
            raise error(
                "HED-DATA-0041",
                title="xlsx worksheet missing",
                explanation="No worksheet XML found in archive.",
                remediation="Export a simple Sheet1 workbook.",
            )
        root = ET.fromstring(zf.read(path))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    matrix: list[list[str]] = []
    for row in root.findall(".//m:sheetData/m:row", ns):
        values: list[str] = []
        for cell in row.findall("m:c", ns):
            inline = cell.find("m:is/m:t", ns)
            formula = cell.find("m:f", ns)
            if formula is not None and formula.text:
                values.append(
                    _reject_or_sanitize(f"={formula.text}", formula_policy=formula_policy)
                )
            elif inline is not None and inline.text is not None:
                values.append(_reject_or_sanitize(inline.text, formula_policy=formula_policy))
            else:
                v = cell.find("m:v", ns)
                values.append(
                    _reject_or_sanitize(
                        v.text or "" if v is not None else "", formula_policy=formula_policy
                    )
                )
        matrix.append(values)
    if not matrix:
        return []
    headers = [h or f"col_{i}" for i, h in enumerate(matrix[0])]
    out: list[dict[str, JsonValue]] = []
    for row in matrix[1:]:
        item: dict[str, JsonValue] = {
            headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))
        }
        out.append(item)
    return out


def export_rows_ods(
    rows: Sequence[Mapping[str, JsonValue]],
    columns: Sequence[ColumnSchema] | Sequence[str],
) -> bytes:
    """Minimal ODS-compatible zip with a CSV content stream for portability."""
    names = [c.name if isinstance(c, ColumnSchema) else str(c) for c in columns]
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(names)
    for row in rows:
        writer.writerow([row.get(name, "") for name in names])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.csv", text.getvalue())
    return buf.getvalue()


def import_rows_ods(
    data: bytes,
    *,
    formula_policy: str = "reject",
) -> list[dict[str, JsonValue]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        raw = zf.read("content.csv").decode("utf-8")
    reader = csv.DictReader(io.StringIO(raw))
    out: list[dict[str, JsonValue]] = []
    for row in reader:
        cleaned: dict[str, JsonValue] = {
            str(key): _reject_or_sanitize(str(value), formula_policy=formula_policy)
            for key, value in row.items()
            if key is not None
        }
        out.append(cleaned)
    return out
