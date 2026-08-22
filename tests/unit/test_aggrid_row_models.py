from pathlib import Path

import pytest

from hedron_data.aggrid import aggrid_column_defs, ensure_aggrid_assets, infinite_block_request
from hedron_data.sources import ColumnSchema, DataQuery

_ASSETS = Path(__file__).resolve().parents[2] / "packages/hedron-data/src/hedron_data/assets/aggrid"


def test_aggrid_client_and_infinite() -> None:
    defs = aggrid_column_defs([ColumnSchema(name="id", label="Id", display="text", writable=True)])
    assert defs[0]["field"] == "id"
    q = infinite_block_request(DataQuery(limit=25), block_size=50, start_row=100)
    assert q.offset == 100
    assert q.limit == 50

    with pytest.raises(ValueError, match="secret.*not allowlisted"):
        infinite_block_request(
            DataQuery(
                projection=("secret",),
                allowlisted_projection_fields=frozenset({"public"}),
            ),
            block_size=50,
            start_row=0,
        )

    meta = ensure_aggrid_assets(row_model="infinite")
    assert meta["rowModel"] == "infinite"
    assert meta["runtime"] == "hedron-data:aggrid.community.js"
    assert "hedron-data-selection" in meta["events"]
    community = _ASSETS / "ag-grid-community.min.js"
    host = _ASSETS / "host.js"
    assert community.is_file() and community.stat().st_size > 50_000
    text = host.read_text(encoding="utf-8")
    assert "rowModelType" in text
    assert "infinite" in text
    assert "hedron-data-edit" in text
    assert "fail(" in text


def test_aggrid_host_registers_htmx_lifecycle_and_disposes_grids() -> None:
    text = (_ASSETS / "host.js").read_text(encoding="utf-8")
    assert "function destroy(el)" in text
    assert "api.destroy" in text
    assert "delete el._hedronAgGridApi" in text
    assert "data-hedron-grid-mounted" in text
    assert "base.matches" in text
    assert 'document.addEventListener("htmx:beforeSwap", beforeSwap)' in text
    assert "htmx:oobBeforeSwap" in text
    assert "htmx:oobAfterSwap" in text
