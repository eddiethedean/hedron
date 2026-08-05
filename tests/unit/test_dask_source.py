import pytest

from hedron_data.dask_source import DaskDataSource, require_dask
from hedron_data.sources import DataQuery

pytest.importorskip("dask")
pytest.importorskip("pandas")


def test_dask_positional_paging() -> None:
    dd = require_dask()
    import pandas as pd

    frame = dd.from_pandas(
        pd.DataFrame({"id": [10, 20, 30, 40], "value": [1, 2, 3, 4]}).set_index("id"),
        npartitions=1,
    )
    src = DaskDataSource(frame)
    page = src.fetch(DataQuery(offset=1, limit=2))
    assert len(page.rows) == 2
    # Positional page after non-RangeIndex must not use label .loc semantics.
    values = [row["value"] if isinstance(row, dict) else row for row in page.rows]
    assert values == [2, 3]
    assert page.total == 4
