import zipfile
from io import BytesIO

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.spreadsheet import (
    _reject_or_sanitize,
    excel_col,
    export_rows_ods,
    export_rows_xlsx,
    import_rows_ods,
    import_rows_xlsx,
)


def _ods_with_cell(text: str) -> bytes:
    """Build a minimal ODS whose first data cell is unsanitized ``text``."""
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    esc = (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}" '
        f'xmlns:table="{ns_table}" xmlns:text="{ns_text}">'
        "<office:body><office:spreadsheet>"
        '<table:table table:name="Sheet1">'
        "<table:table-row>"
        f'<table:table-cell office:value-type="string"><text:p>id</text:p></table:table-cell>'
        "</table:table-row>"
        "<table:table-row>"
        f'<table:table-cell office:value-type="string"><text:p>{esc}</text:p></table:table-cell>'
        "</table:table-row>"
        "</table:table></office:spreadsheet></office:body></office:document-content>"
    )
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content)
    return buf.getvalue()


def test_xlsx_roundtrip_and_formula_reject() -> None:
    rows = [{"id": "1", "name": "a"}]
    data = export_rows_xlsx(rows, ["id", "name"])
    out = import_rows_xlsx(data)
    assert out[0]["id"] == "1"
    assert excel_col(26) == "AA"
    wide = export_rows_xlsx([{"c": "x"}], [f"c{i}" for i in range(30)])
    assert wide

    # Export path sanitizes formulas so downloaded files are not executable.
    ods = export_rows_ods([{"id": "=1+1"}], ["id"])
    with zipfile.ZipFile(BytesIO(ods)) as zf:
        assert "content.xml" in zf.namelist()
        assert "'=1+1" in zf.read("content.xml").decode("utf-8")
    cleaned = import_rows_ods(ods, formula_policy="reject")
    assert str(cleaned[0]["id"]).startswith("'")

    # Import reject still fails closed on unsanitized spreadsheet payloads.
    for bad in ("=1", "+1", "-1", "@1", "\t=1"):
        with pytest.raises(HedronError):
            import_rows_ods(_ods_with_cell(bad), formula_policy="reject")
        assert _reject_or_sanitize(bad, formula_policy="sanitize").startswith("'")


_FORMULA_EVASION_CORPUS = (
    ' =HYPERLINK("http://evil","x")',
    "\x00=cmd",
    "\ufeff=CMD",
    "\xa0=cmd",
    "\n=cmd",
    "\uff1dcmd",  # fullwidth equals
    "\uff0b1",  # fullwidth plus
    "\uff0d1",  # fullwidth hyphen-minus
    "\uff20cmd",  # fullwidth at
)


def test_formula_policy_rejects_whitespace_control_and_fullwidth_prefixes() -> None:
    for payload in _FORMULA_EVASION_CORPUS:
        with pytest.raises(HedronError, match="HED-DATA-0040|formula"):
            _reject_or_sanitize(payload, formula_policy="reject")
        sanitized = _reject_or_sanitize(payload, formula_policy="sanitize")
        assert sanitized.startswith("'")
        assert not sanitized[1:].startswith((" ", "\n", "\x00", "\ufeff", "\xa0"))


def test_xlsx_export_import_rejects_spaced_formula_payload() -> None:
    blob = export_rows_xlsx(
        [{"name": ' =HYPERLINK("http://evil","x")'}],
        ["name"],
    )
    # Export sanitizes; re-import under reject must accept the neutralized cell.
    cleaned = import_rows_xlsx(blob, formula_policy="reject")
    assert str(cleaned[0]["name"]).startswith("'")

    with pytest.raises(HedronError):
        import_rows_ods(
            _ods_with_cell(' =HYPERLINK("http://evil","x")'),
            formula_policy="reject",
        )


def test_importers_skip_blank_separator_rows() -> None:
    xlsx = export_rows_xlsx([{"a": "x", "b": "y"}], ["a", "b"])
    with zipfile.ZipFile(BytesIO(xlsx), "r") as source:
        sheet = source.read("xl/worksheets/sheet1.xml").decode("utf-8")
        members = {item.filename: source.read(item) for item in source.infolist()}
    sheet = sheet.replace('</row><row r="2">', '</row><row r="2"/><row r="3">', 1)
    members["xl/worksheets/sheet1.xml"] = sheet.encode("utf-8")
    rebuilt = BytesIO()
    with zipfile.ZipFile(rebuilt, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, payload in members.items():
            target.writestr(name, payload)
    assert import_rows_xlsx(rebuilt.getvalue()) == [{"a": "x", "b": "y"}]

    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    ods_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}"'
        f' xmlns:table="{ns_table}" xmlns:text="{ns_text}">'
        '<office:body><office:spreadsheet><table:table table:name="Sheet1">'
        "<table:table-row><table:table-cell><text:p>a</text:p></table:table-cell></table:table-row>"
        "<table:table-row/>"
        "<table:table-row><table:table-cell><text:p>x</text:p></table:table-cell></table:table-row>"
        "</table:table></office:spreadsheet></office:body></office:document-content>"
    )
    ods = BytesIO()
    with zipfile.ZipFile(ods, "w", compression=zipfile.ZIP_DEFLATED) as target:
        target.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        target.writestr("content.xml", ods_xml)
    assert import_rows_ods(ods.getvalue()) == [{"a": "x"}]
