import zipfile
from io import BytesIO

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.spreadsheet import (
    excel_col,
    export_rows_ods,
    export_rows_xlsx,
    import_rows_ods,
    import_rows_xlsx,
)


def test_xlsx_roundtrip_and_formula_reject() -> None:
    rows = [{"id": "1", "name": "a"}]
    data = export_rows_xlsx(rows, ["id", "name"])
    out = import_rows_xlsx(data)
    assert out[0]["id"] == "1"
    assert excel_col(26) == "AA"
    wide = export_rows_xlsx([{"c": "x"}], [f"c{i}" for i in range(30)])
    assert wide

    ods = export_rows_ods([{"id": "=1+1"}], ["id"])
    with zipfile.ZipFile(BytesIO(ods)) as zf:
        assert "content.xml" in zf.namelist()
    with pytest.raises(HedronError):
        import_rows_ods(ods, formula_policy="reject")
    cleaned = import_rows_ods(ods, formula_policy="sanitize")
    assert str(cleaned[0]["id"]).startswith("'")

    for bad in ("=1", "+1", "-1", "@1", "\t1"):
        with pytest.raises(HedronError):
            import_rows_ods(export_rows_ods([{"id": bad}], ["id"]), formula_policy="reject")
