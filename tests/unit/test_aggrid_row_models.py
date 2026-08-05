from hedron_data.aggrid import aggrid_column_defs, ensure_aggrid_assets, infinite_block_request
from hedron_data.sources import ColumnSchema, DataQuery


def test_aggrid_client_and_infinite() -> None:
    defs = aggrid_column_defs([ColumnSchema(name="id", label="Id", display="text", writable=True)])
    assert defs[0]["field"] == "id"
    q = infinite_block_request(DataQuery(limit=25), block_size=50, start_row=100)
    assert q.offset == 100
    assert q.limit == 50
    meta = ensure_aggrid_assets(row_model="infinite")
    assert meta["rowModel"] == "infinite"
