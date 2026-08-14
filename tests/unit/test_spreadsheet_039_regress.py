"""REGRESS-039 spreadsheet import/export fixes."""

from __future__ import annotations

import zipfile
from io import BytesIO

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.spreadsheet import (
    _reject_or_sanitize,
    export_rows_ods,
    export_rows_xlsx,
    import_rows_ods,
    import_rows_xlsx,
)


def _xlsx_sheet(sheet_xml: str, *, shared: str | None = None) -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>',
        )
        zf.writestr("xl/workbook.xml", '<?xml version="1.0"?><workbook/>')
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        if shared is not None:
            zf.writestr("xl/sharedStrings.xml", shared)
    return buf.getvalue()


def test_039_xlsx_sparse_cells_keep_column_alignment() -> None:
    sheet = """<?xml version="1.0"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1">
      <c r="A1" t="inlineStr"><is><t>A</t></is></c>
      <c r="B1" t="inlineStr"><is><t>B</t></is></c>
      <c r="C1" t="inlineStr"><is><t>C</t></is></c>
    </row>
    <row r="2">
      <c r="A2" t="inlineStr"><is><t>one</t></is></c>
      <c r="C2" t="inlineStr"><is><t>three</t></is></c>
    </row>
  </sheetData>
</worksheet>"""
    rows = import_rows_xlsx(_xlsx_sheet(sheet))
    assert rows == [{"A": "one", "B": "", "C": "three"}]


def test_039_xlsx_shared_strings_resolved() -> None:
    shared = """<?xml version="1.0"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="4" uniqueCount="4">
  <si><t>name</t></si><si><t>city</t></si><si><t>Alice</t></si><si><t>Paris</t></si>
</sst>"""
    sheet = """<?xml version="1.0"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>
    <row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>
  </sheetData>
</worksheet>"""
    rows = import_rows_xlsx(_xlsx_sheet(sheet, shared=shared))
    assert rows == [{"name": "Alice", "city": "Paris"}]


def test_039_xlsx_rich_text_inline_strings() -> None:
    sheet = """<?xml version="1.0"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="inlineStr"><is><t>name</t></is></c></row>
    <row r="2">
      <c r="A2" t="inlineStr"><is><r><rPr><b/></rPr><t>Hello</t></r></is></c>
    </row>
  </sheetData>
</worksheet>"""
    rows = import_rows_xlsx(_xlsx_sheet(sheet))
    assert rows == [{"name": "Hello"}]


def test_039_xlsx_ods_strip_xml_illegal_controls() -> None:
    blob = export_rows_xlsx([{"a": "hello\x00world"}], ["a"])
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        sheet = zf.read("xl/worksheets/sheet1.xml")
    assert b"\x00" not in sheet
    assert import_rows_xlsx(blob)[0]["a"] == "helloworld"
    ods = export_rows_ods([{"a": "hi\x00there"}], ["a"])
    with zipfile.ZipFile(BytesIO(ods)) as zf:
        content = zf.read("content.xml")
    assert b"\x00" not in content
    assert import_rows_ods(ods)[0]["a"] == "hithere"


def test_039_ods_repeated_columns() -> None:
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"

    def cell(text: str, *, repeat: int | None = None) -> str:
        rep = f' table:number-columns-repeated="{repeat}"' if repeat is not None else ""
        return (
            f'<table:table-cell{rep} office:value-type="string">'
            f"<text:p>{text}</text:p></table:table-cell>"
        )

    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}" '
        f'xmlns:table="{ns_table}" xmlns:text="{ns_text}">'
        "<office:body><office:spreadsheet><table:table table:name='Sheet1'>"
        f"<table:table-row>{cell('A')}{cell('B')}{cell('C')}{cell('D')}</table:table-row>"
        f"<table:table-row>{cell('one')}{cell('', repeat=2)}{cell('four')}</table:table-row>"
        "</table:table></office:spreadsheet></office:body></office:document-content>"
    )
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content)
    rows = import_rows_ods(buf.getvalue())
    assert rows == [{"A": "one", "B": "", "C": "", "D": "four"}]


def test_039_ods_formula_attribute_rejected() -> None:
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}" '
        f'xmlns:table="{ns_table}" xmlns:text="{ns_text}">'
        "<office:body><office:spreadsheet><table:table table:name='Sheet1'>"
        "<table:table-row>"
        '<table:table-cell office:value-type="string"><text:p>id</text:p></table:table-cell>'
        "</table:table-row>"
        "<table:table-row>"
        '<table:table-cell table:formula="of:=1+2" office:value-type="float">'
        "<text:p>3</text:p></table:table-cell>"
        "</table:table-row>"
        "</table:table></office:spreadsheet></office:body></office:document-content>"
    )
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content)
    with pytest.raises(HedronError, match="HED-DATA-0040"):
        import_rows_ods(buf.getvalue(), formula_policy="reject")


def test_039_formula_policy_strips_invisible_unicode() -> None:
    for ch in ("\u200b", "\u202e", "\u2060"):
        payload = f"{ch}=SUM(1,1)"
        with pytest.raises(HedronError, match="HED-DATA-0040"):
            _reject_or_sanitize(payload, formula_policy="reject")
        assert _reject_or_sanitize(payload, formula_policy="sanitize").startswith("'")


def test_039_import_enforces_decompression_bounds() -> None:
    # Force an absurd declared uncompressed size via ZipInfo.
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        info = zipfile.ZipInfo("xl/worksheets/sheet1.xml")
        payload = b'<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>'
        info.file_size = 50_000_000
        info.compress_size = 100
        # writestr overwrites sizes; inject via write after patching is unreliable,
        # so call import with a tiny max and a real member that exceeds it.
        zf.writestr("xl/worksheets/sheet1.xml", payload * 2000)
    with pytest.raises(HedronError, match="HED-DATA-0041"):
        import_rows_xlsx(buf.getvalue(), max_uncompressed_bytes=1024)
