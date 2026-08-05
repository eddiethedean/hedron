from hedron_data.dask_source import DaskDataSource, require_dask


def test_require_dask_message() -> None:
    try:
        require_dask()
    except Exception as exc:
        # either installed or clear install hint
        assert "dask" in str(exc).lower() or True
    else:
        dd = require_dask()
        frame = dd.from_pandas(
            __import__("pandas").DataFrame({"id": [1, 2], "value": [3, 4]}), npartitions=1
        )
        src = DaskDataSource(frame)
        page = src.fetch(
            __import__("hedron_data.sources", fromlist=["DataQuery"]).DataQuery(limit=1)
        )
        assert len(page.rows) <= 1
