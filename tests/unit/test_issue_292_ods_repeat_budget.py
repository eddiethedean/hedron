"""#292: ODS import must bound row_repeat × col_repeat expansion."""

from __future__ import annotations

import zipfile
from io import BytesIO

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.spreadsheet import import_rows_ods


def _ods_with_repeats(*, row_repeat: int, col_repeat: int) -> bytes:
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_table = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}" '
        f'xmlns:table="{ns_table}" xmlns:text="{ns_text}">'
        "<office:body><office:spreadsheet>"
        '<table:table table:name="Sheet1">'
        "<table:table-row>"
        '<table:table-cell office:value-type="string"><text:p>id</text:p></table:table-cell>'
        "</table:table-row>"
        f'<table:table-row table:number-rows-repeated="{row_repeat}">'
        f'<table:table-cell table:number-columns-repeated="{col_repeat}" '
        'office:value-type="string"><text:p>x</text:p></table:table-cell>'
        "</table:table-row>"
        "</table:table></office:spreadsheet></office:body></office:document-content>"
    )
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content)
    return buf.getvalue()


def test_ods_multiplicative_repeats_fail_closed() -> None:
    with pytest.raises(HedronError) as caught:
        import_rows_ods(_ods_with_repeats(row_repeat=10_000, col_repeat=10_000))
    assert caught.value.diagnostics[0].code == "HED-DATA-0041"
