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
    for bad in ("=1", "+1", "-1", "@1", "\t1"):
        with pytest.raises(HedronError):
            import_rows_ods(_ods_with_cell(bad), formula_policy="reject")
        assert _reject_or_sanitize(bad, formula_policy="sanitize").startswith("'")
