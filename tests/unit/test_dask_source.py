from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.dask_source import DaskDataSource
from hedron_data.sources import DataQuery


def test_dask_search_without_fields_fails_closed() -> None:
    dd = pytest.importorskip("dask.dataframe")
    pandas = pytest.importorskip("pandas")
    frame = dd.from_pandas(pandas.DataFrame({"name": ["Alice", "Bob"]}), npartitions=1)
    with pytest.raises(HedronError, match="HED-DATA-0012"):
        DaskDataSource(frame).fetch(DataQuery(search="Alice"))
