"""Spreadsheet import/export beyond CSV (xlsx/ods) with formula sandbox."""

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
    "excel_col",
]


def _strip_formula_evasion_prefix(value: str) -> str:
    """Drop leading BOM, ASCII controls, and Unicode whitespace used to evade checks."""
    index = 0
    length = len(value)
    while index < length:
        char = value[index]
        code = ord(char)
        if char == "\ufeff" or code < 32 or code == 127 or char.isspace():
            index += 1
            continue
        break
    return value[index:]


# ASCII formula prefixes plus common fullwidth lookalikes used to bypass filters.
_DANGEROUS_FORMULA_PREFIXES = frozenset(
    {
        "=",
        "+",
        "-",
        "@",
        "\uff1d",  # fullwidth equals
        "\uff0b",  # fullwidth plus
        "\uff0d",  # fullwidth hyphen-minus
        "\uff20",  # fullwidth commercial at
    }
)


def _reject_or_sanitize(value: str, *, formula_policy: str) -> str:
    # Classic spreadsheet/CSV injection prefixes, after stripping evasion padding.
    normalized = _strip_formula_evasion_prefix(value)
    dangerous = bool(normalized) and normalized[:1] in _DANGEROUS_FORMULA_PREFIXES
    if dangerous:
        if formula_policy == "reject":
            raise error(
                "HED-DATA-0040",
                title="Spreadsheet formula rejected",
                explanation="Imported cells must not contain formulas under reject policy.",
                remediation="Strip formulas before import or use formula_policy='sanitize'.",
            )
        if formula_policy == "sanitize":
            # Prefix the neutralized residual so Excel/ODS treat it as text.
            return "'" + normalized
        raise ValueError(f"Unknown formula_policy {formula_policy!r}")
    return value


def excel_col(index: int) -> str:
    """Convert 0-based column index to Excel letters (A, B, ... Z, AA, ...)."""
    if index < 0:
        raise ValueError("column index must be >= 0")
    n = index + 1
    letters: list[str] = []
    while n:
        n, rem = divmod(n - 1, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))


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
        sheet_rows = [names] + [
            [
                _reject_or_sanitize(str(row.get(name, "")), formula_policy="sanitize")
                for name in names
            ]
            for row in rows
        ]
        row_xml = []
        for r_idx, values in enumerate(sheet_rows, start=1):
            cells = []
            for c_idx, value in enumerate(values):
                col = excel_col(c_idx)
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
    """Minimal OpenDocument Spreadsheet (content.xml + mimetype)."""
    names = [c.name if isinstance(c, ColumnSchema) else str(c) for c in columns]
    ns = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    }

    def cell_xml(value: object) -> str:
        text = _reject_or_sanitize(
            str(value if value is not None else ""), formula_policy="sanitize"
        )
        esc = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        return (
            f'<table:table-cell office:value-type="string">'
            f"<text:p>{esc}</text:p></table:table-cell>"
        )

    row_xml: list[str] = []
    header = "".join(cell_xml(name) for name in names)
    row_xml.append(f"<table:table-row>{header}</table:table-row>")
    for row in rows:
        body = "".join(cell_xml(row.get(name, "")) for name in names)
        row_xml.append(f"<table:table-row>{body}</table:table-row>")
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns["office"]}" '
        f'xmlns:table="{ns["table"]}" xmlns:text="{ns["text"]}">'
        "<office:body><office:spreadsheet>"
        f'<table:table table:name="Sheet1">{"".join(row_xml)}</table:table>'
        "</office:spreadsheet></office:body></office:document-content>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content)
    return buf.getvalue()


def import_rows_ods(
    data: bytes,
    *,
    formula_policy: str = "reject",
) -> list[dict[str, JsonValue]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        if "content.xml" in names:
            root = ET.fromstring(zf.read("content.xml"))
            text_ns = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
            table_ns = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
            matrix: list[list[str]] = []
            for row in root.findall(f".//{{{table_ns}}}table-row"):
                values: list[str] = []
                for cell in row.findall(f"{{{table_ns}}}table-cell"):
                    p = cell.find(f"{{{text_ns}}}p")
                    values.append(
                        _reject_or_sanitize(
                            p.text or "" if p is not None else "",
                            formula_policy=formula_policy,
                        )
                    )
                matrix.append(values)
            if not matrix:
                return []
            headers = [h or f"col_{i}" for i, h in enumerate(matrix[0])]
            return [
                {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                for row in matrix[1:]
            ]
        # Legacy hedron CSV-in-zip ODS from earlier 0.12 drafts.
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
