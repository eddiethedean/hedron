"""Spreadsheet import/export beyond CSV (xlsx/ods) with formula sandbox."""

from __future__ import annotations

import csv
import io
import re
import unicodedata
import zipfile
from collections.abc import Mapping, Sequence
from xml.etree import ElementTree as ET

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue
from hedron_data.sources import ColumnSchema

__all__ = [
    "DEFAULT_MAX_UNCOMPRESSED_BYTES",
    "export_rows_ods",
    "export_rows_xlsx",
    "import_rows_ods",
    "import_rows_xlsx",
    "excel_col",
]

DEFAULT_MAX_UNCOMPRESSED_BYTES = 16 * 1024 * 1024
_MAX_ZIP_MEMBERS = 256
_MAX_COMPRESSION_RATIO = 100
_MAX_COLUMN_REPEATS = 10_000
_MAX_ROW_REPEATS = 10_000
_MAX_EXPANDED_CELLS = 50_000
_MAX_XLSX_COLUMN_INDEX = 16_383  # XFD, the final column in XLSX
_MAX_XLSX_ROW_INDEX = 1_048_576
_CELL_REF = re.compile(r"^([A-Za-z]+)(\d+)$")
# XML 1.0 Char exclusions (plus DEL): controls other than TAB/LF/CR.
_XML_ILLEGAL = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def _strip_formula_evasion_prefix(value: str) -> str:
    """Drop leading BOM, controls, whitespace, and Cf format chars used to evade checks."""
    index = 0
    length = len(value)
    while index < length:
        char = value[index]
        code = ord(char)
        category = unicodedata.category(char)
        if (
            char == "\ufeff"
            or code < 32
            or code == 127
            or char.isspace()
            or category in {"Cf", "Cc", "Zl", "Zp", "Mn", "Me"}
        ):
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
        "|",
        "\uff1d",  # fullwidth equals
        "\uff0b",  # fullwidth plus
        "\uff0d",  # fullwidth hyphen-minus
        "\uff20",  # fullwidth commercial at
        "\uff5c",  # fullwidth vertical line
    }
)


def reject_or_sanitize(value: str, *, formula_policy: str) -> str:
    # Classic spreadsheet/CSV injection prefixes, after stripping evasion padding.
    normalized = _strip_formula_evasion_prefix(value)
    folded = unicodedata.normalize("NFKC", normalized) if normalized else ""
    dangerous = bool(folded) and folded[:1] in _DANGEROUS_FORMULA_PREFIXES
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


# Compatibility name retained for callers that used the pre-1.0 helper.
_reject_or_sanitize = reject_or_sanitize


def _xml_safe_text(value: str) -> str:
    """Strip XML 1.0 illegal control characters before embedding in worksheet XML (#176)."""
    return _XML_ILLEGAL.sub("", value)


def _escape_xml_text(value: str) -> str:
    safe = _xml_safe_text(value)
    return safe.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _validated_headers(values: Sequence[str]) -> list[str]:
    headers = [value or f"col_{index}" for index, value in enumerate(values)]
    seen: dict[str, int] = {}
    for index, header in enumerate(headers):
        key = str(header)
        if key in seen:
            raise error(
                "HED-DATA-0041",
                title="Duplicate spreadsheet header",
                explanation=(f"Header {header!r} at column {index} duplicates column {seen[key]}."),
                remediation="Rename duplicate headers before importing the worksheet.",
            )
        seen[key] = index
    return headers


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


def excel_col_index(letters: str) -> int:
    """Convert Excel column letters to 0-based index."""
    if not letters:
        raise ValueError("Invalid column letters ''")
    n = 0
    for ch in letters.upper():
        if not ("A" <= ch <= "Z"):
            raise ValueError(f"Invalid column letters {letters!r}")
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def _read_zip_member(
    zf: zipfile.ZipFile,
    path: str,
    *,
    max_uncompressed_bytes: int,
) -> bytes:
    """Read a zip member with uncompressed-size and compression-ratio bounds (#248)."""
    if max_uncompressed_bytes < 1:
        raise ValueError("max_uncompressed_bytes must be >= 1")
    try:
        info = zf.getinfo(path)
    except KeyError as exc:
        raise error(
            "HED-DATA-0041",
            title="Spreadsheet archive member missing",
            explanation=f"Required member {path!r} was not found.",
            remediation="Export a simple workbook with the expected parts.",
        ) from exc
    if info.file_size > max_uncompressed_bytes:
        raise error(
            "HED-DATA-0041",
            title="Spreadsheet member exceeds size budget",
            explanation=(
                f"Member {path!r} declares {info.file_size} uncompressed bytes; "
                f"max is {max_uncompressed_bytes}."
            ),
            remediation="Reduce workbook size or raise max_uncompressed_bytes explicitly.",
        )
    compress_size = info.compress_size or 1
    if info.file_size > 0 and (info.file_size / compress_size) > _MAX_COMPRESSION_RATIO:
        raise error(
            "HED-DATA-0041",
            title="Spreadsheet compression ratio rejected",
            explanation=(f"Member {path!r} compression ratio exceeds {_MAX_COMPRESSION_RATIO}:1."),
            remediation="Refuse zip-bomb style archives; re-export without extreme compression.",
        )
    payload = zf.read(path)
    if len(payload) > max_uncompressed_bytes:
        raise error(
            "HED-DATA-0041",
            title="Spreadsheet member exceeds size budget",
            explanation=(
                f"Member {path!r} inflated to {len(payload)} bytes; "
                f"max is {max_uncompressed_bytes}."
            ),
            remediation="Reduce workbook size or raise max_uncompressed_bytes explicitly.",
        )
    return payload


def _guard_zip_namelist(zf: zipfile.ZipFile) -> None:
    names = zf.namelist()
    if len(names) > _MAX_ZIP_MEMBERS:
        raise error(
            "HED-DATA-0041",
            title="Spreadsheet archive too complex",
            explanation=f"Archive has {len(names)} members; max is {_MAX_ZIP_MEMBERS}.",
            remediation="Export a simple single-sheet workbook.",
        )


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
        row_xml: list[str] = []
        for r_idx, values in enumerate(sheet_rows, start=1):
            cells: list[str] = []
            for c_idx, value in enumerate(values):
                col = excel_col(c_idx)
                ref = f"{col}{r_idx}"
                esc = _escape_xml_text(value)
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{esc}</t></is></c>')
            row_xml.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
        zf.writestr(
            "xl/worksheets/sheet1.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"<sheetData>{''.join(row_xml)}</sheetData></worksheet>",
        )
    return buf.getvalue()


def _parse_shared_strings(
    zf: zipfile.ZipFile,
    *,
    max_uncompressed_bytes: int,
) -> list[str]:
    names = set(zf.namelist())
    path = next((n for n in names if n.endswith("sharedStrings.xml")), None)
    if path is None:
        return []
    root = ET.fromstring(_read_zip_member(zf, path, max_uncompressed_bytes=max_uncompressed_bytes))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    strings: list[str] = []
    for si in root.findall("m:si", ns):
        parts = [t.text or "" for t in si.findall(".//m:t", ns)]
        strings.append("".join(parts))
    return strings


def _inline_string_text(cell: ET.Element, ns: dict[str, str]) -> str | None:
    """Collect inlineStr text from direct ``t`` and rich-text ``r/t`` runs (#241)."""
    inline = cell.find("m:is", ns)
    if inline is None:
        return None
    parts = [t.text or "" for t in inline.findall(".//m:t", ns)]
    return "".join(parts)


def _cell_column_index(cell: ET.Element, fallback: int) -> int:
    ref = cell.get("r")
    if not ref:
        if fallback > _MAX_XLSX_COLUMN_INDEX:
            raise error(
                "HED-DATA-0041",
                title="XLSX cell reference exceeds bounds",
                explanation="Implicit cell column is outside the XLSX worksheet limits.",
                remediation="Export a worksheet within the XLSX row and column limits.",
            )
        return fallback
    match = _CELL_REF.match(ref)
    if not match:
        raise error(
            "HED-DATA-0041",
            title="Invalid XLSX cell reference",
            explanation=f"Cannot parse cell reference {ref!r}.",
            remediation="Export a standards-compliant worksheet.",
        )
    letters, row_text = match.groups()
    if len(letters) > 3 or len(row_text) > 7:
        raise error(
            "HED-DATA-0041",
            title="XLSX cell reference exceeds bounds",
            explanation=f"Cell reference {ref!r} is outside the XLSX worksheet limits.",
            remediation="Export a worksheet within the XLSX row and column limits.",
        )
    column = excel_col_index(letters)
    row = int(row_text)
    if column > _MAX_XLSX_COLUMN_INDEX or row < 1 or row > _MAX_XLSX_ROW_INDEX:
        raise error(
            "HED-DATA-0041",
            title="XLSX cell reference exceeds bounds",
            explanation=f"Cell reference {ref!r} is outside the XLSX worksheet limits.",
            remediation="Export a worksheet within the XLSX row and column limits.",
        )
    return column


def import_rows_xlsx(
    data: bytes,
    *,
    formula_policy: str = "reject",
    max_uncompressed_bytes: int = DEFAULT_MAX_UNCOMPRESSED_BYTES,
) -> list[dict[str, JsonValue]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        _guard_zip_namelist(zf)
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
        shared = _parse_shared_strings(zf, max_uncompressed_bytes=max_uncompressed_bytes)
        root = ET.fromstring(
            _read_zip_member(zf, path, max_uncompressed_bytes=max_uncompressed_bytes)
        )
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    matrix: list[list[str]] = []
    expanded = 0
    for row in root.findall(".//m:sheetData/m:row", ns):
        by_col: dict[int, str] = {}
        next_dense = 0
        seen_refs: set[str] = set()
        seen_columns: set[int] = set()
        for cell in row.findall("m:c", ns):
            ref = cell.get("r")
            if ref:
                if ref in seen_refs:
                    raise error(
                        "HED-DATA-0041",
                        title="Duplicate XLSX cell reference",
                        explanation=f"Cell reference {ref!r} appears more than once.",
                        remediation="Export a standards-compliant worksheet.",
                    )
                seen_refs.add(ref)
            col_idx = _cell_column_index(cell, next_dense)
            if col_idx in seen_columns:
                raise error(
                    "HED-DATA-0041",
                    title="Duplicate XLSX cell column",
                    explanation=f"Worksheet row contains column {excel_col(col_idx)!r} twice.",
                    remediation="Export a standards-compliant worksheet without duplicate cells.",
                )
            seen_columns.add(col_idx)
            next_dense = col_idx + 1
            formula = cell.find("m:f", ns)
            cell_type = cell.get("t")
            if formula is not None and formula.text:
                text = _reject_or_sanitize(f"={formula.text}", formula_policy=formula_policy)
            elif cell_type == "inlineStr" or cell.find("m:is", ns) is not None:
                inline_text = _inline_string_text(cell, ns)
                text = _reject_or_sanitize(inline_text or "", formula_policy=formula_policy)
            elif cell_type == "s":
                v = cell.find("m:v", ns)
                raw = (v.text or "").strip() if v is not None else ""
                try:
                    index = int(raw)
                except ValueError as exc:
                    raise error(
                        "HED-DATA-0041",
                        title="Invalid shared-string index",
                        explanation=f"Shared-string index {raw!r} is not an integer.",
                        remediation="Repair the workbook sharedStrings table.",
                    ) from exc
                if index < 0 or index >= len(shared):
                    raise error(
                        "HED-DATA-0041",
                        title="Shared-string index out of range",
                        explanation=(
                            f"Index {index} is outside sharedStrings (size {len(shared)})."
                        ),
                        remediation="Repair the workbook sharedStrings table.",
                    )
                text = _reject_or_sanitize(shared[index], formula_policy=formula_policy)
            else:
                v = cell.find("m:v", ns)
                text = _reject_or_sanitize(
                    v.text or "" if v is not None else "", formula_policy=formula_policy
                )
            by_col[col_idx] = text
        if not by_col:
            expanded += 1
            if expanded > _MAX_EXPANDED_CELLS:
                raise error(
                    "HED-DATA-0041",
                    title="XLSX expanded cell budget exceeded",
                    explanation=f"Worksheet expands to more than {_MAX_EXPANDED_CELLS} cells.",
                    remediation="Reduce sparse worksheet dimensions before import.",
                )
            matrix.append([])
            continue
        width = max(by_col) + 1
        expanded += width
        if expanded > _MAX_EXPANDED_CELLS:
            raise error(
                "HED-DATA-0041",
                title="XLSX expanded cell budget exceeded",
                explanation=f"Worksheet expands to more than {_MAX_EXPANDED_CELLS} cells.",
                remediation="Reduce sparse worksheet dimensions before import.",
            )
        matrix.append([by_col.get(i, "") for i in range(width)])
    if not matrix:
        return []
    headers = _validated_headers(matrix[0])
    out: list[dict[str, JsonValue]] = []
    for row in matrix[1:]:
        if not row or not any(row):
            continue
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
        esc = _escape_xml_text(text).replace('"', "&quot;")
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


def _ods_repeat(attr: str | None, *, max_repeat: int, label: str) -> int:
    if attr is None or attr == "":
        return 1
    try:
        count = int(attr)
    except ValueError as exc:
        raise error(
            "HED-DATA-0041",
            title="Invalid ODS repetition attribute",
            explanation=f"{label} value {attr!r} is not an integer.",
            remediation="Export a standards-compliant ODS workbook.",
        ) from exc
    if count < 1 or count > max_repeat:
        raise error(
            "HED-DATA-0041",
            title="ODS repetition exceeds budget",
            explanation=f"{label}={count} exceeds allowed range 1..{max_repeat}.",
            remediation="Reduce repeated empty rows/columns or raise import budgets.",
        )
    return count


def _normalize_ods_formula(raw: str) -> str:
    text = raw.strip()
    if text.lower().startswith("of:"):
        text = text[3:]
    if not text.startswith("="):
        text = f"={text}"
    return text


def import_rows_ods(
    data: bytes,
    *,
    formula_policy: str = "reject",
    max_uncompressed_bytes: int = DEFAULT_MAX_UNCOMPRESSED_BYTES,
) -> list[dict[str, JsonValue]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        _guard_zip_namelist(zf)
        names = set(zf.namelist())
        if "content.xml" in names:
            root = ET.fromstring(
                _read_zip_member(zf, "content.xml", max_uncompressed_bytes=max_uncompressed_bytes)
            )
            text_ns = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
            table_ns = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
            matrix: list[list[str]] = []
            expanded = 0
            for row in root.findall(f".//{{{table_ns}}}table-row"):
                row_repeat = _ods_repeat(
                    row.get(f"{{{table_ns}}}number-rows-repeated"),
                    max_repeat=_MAX_ROW_REPEATS,
                    label="number-rows-repeated",
                )
                values: list[str] = []
                for cell in row.findall(f"{{{table_ns}}}table-cell"):
                    col_repeat = _ods_repeat(
                        cell.get(f"{{{table_ns}}}number-columns-repeated"),
                        max_repeat=_MAX_COLUMN_REPEATS,
                        label="number-columns-repeated",
                    )
                    formula_attr = cell.get(f"{{{table_ns}}}formula")
                    if formula_attr:
                        cell_text = _reject_or_sanitize(
                            _normalize_ods_formula(formula_attr),
                            formula_policy=formula_policy,
                        )
                    else:
                        p = cell.find(f"{{{text_ns}}}p")
                        cell_text = _reject_or_sanitize(
                            p.text or "" if p is not None else "",
                            formula_policy=formula_policy,
                        )
                    values.extend([cell_text] * col_repeat)
                added = row_repeat * max(len(values), 1)
                if expanded + added > _MAX_EXPANDED_CELLS:
                    raise error(
                        "HED-DATA-0041",
                        title="ODS expanded cell budget exceeded",
                        explanation=(
                            f"row_repeat × columns expands to {expanded + added} cells; "
                            f"max is {_MAX_EXPANDED_CELLS}."
                        ),
                        remediation="Reduce repeated empty rows/columns before import.",
                    )
                expanded += added
                for _ in range(row_repeat):
                    matrix.append(list(values))
            if not matrix:
                return []
            headers = _validated_headers(matrix[0])
            return [
                {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
                for row in matrix[1:]
                if row and any(row)
            ]
        # Legacy hedron CSV-in-zip ODS from earlier 0.12 drafts.
        raw = _read_zip_member(
            zf, "content.csv", max_uncompressed_bytes=max_uncompressed_bytes
        ).decode("utf-8")
    reader = csv.DictReader(io.StringIO(raw))
    if reader.fieldnames is not None:
        reader.fieldnames = _validated_headers([str(value or "") for value in reader.fieldnames])
    out: list[dict[str, JsonValue]] = []
    for row in reader:
        cleaned: dict[str, JsonValue] = {
            str(key): _reject_or_sanitize(str(value), formula_policy=formula_policy)
            for key, value in row.items()
            if key is not None
        }
        out.append(cleaned)
    return out
