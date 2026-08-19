"""REGRESS-039: locked 27-issue remediation evidence."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from hedron.builtins.media import download_all_zip, media_file_response
from hedron_charts.optional_adapters import GreatTablesAdapter, ThreeJsAdapter
from hedron_core.diagnostics import HedronError
from hedron_core.visualization import ChartAccessibility, VisualizationLimits
from hedron_data.advanced import evaluate_formula, rows_to_tree
from hedron_data.memory import InMemoryDataSource
from hedron_data.normalize import normalize_rows
from hedron_data.sources import CellUpdate, DataChanges, DataQuery
from hedron_data.spreadsheet import export_rows_xlsx, import_rows_xlsx


def _acc() -> ChartAccessibility:
    return ChartAccessibility(title="t", description="d")


def test_073_great_tables_list_respects_payload_limits() -> None:
    adapter = GreatTablesAdapter()
    huge = [{"col": "x" * 1000} for _ in range(5000)]
    with pytest.raises((ValueError, HedronError)):
        adapter.compile(
            huge,
            accessibility=_acc(),
            limits=VisualizationLimits(max_payload_bytes=1024),
        )


def test_194_threejs_rejects_path_traversal() -> None:
    adapter = ThreeJsAdapter()
    with pytest.raises(ValueError, match="traversal"):
        adapter.compile({"model_url": "../secret/model.gltf", "bytes": 10}, accessibility=_acc())


def test_188_189_normalize_rows_column_and_empty() -> None:
    assert normalize_rows({}) == []
    rows = normalize_rows({"a": [1, 2], "b": [3, 4]})
    assert rows == [{"a": 1, "b": 3}, {"a": 2, "b": 4}]
    with pytest.raises(HedronError):
        normalize_rows({"a": [1], "b": [1, 2]})


def test_115_116_117_190_memory_source() -> None:
    with pytest.raises(HedronError):
        InMemoryDataSource([{"id": "1"}, {"id": "1"}], writable_fields=frozenset({"name"}))
    src = InMemoryDataSource(
        [{"id": "1", "v": 1}, {"id": "2", "v": "b"}, {"id": "3", "v": None}],
        writable_fields=frozenset({"v"}),
        allowlisted_sort_fields=frozenset({"v"}),
    )
    page = src.fetch(DataQuery(sort=(("v", "asc"),), limit=10))
    assert len(page.rows) == 3
    with pytest.raises((HedronError, ValueError)):
        src.fetch(DataQuery(sort=(("v", "sideways"),), limit=10))
    # Hard max page size caps rather than accepting unbounded limits
    capped = DataQuery(limit=10_000).validated()
    assert capped.limit <= 500
    result = src.apply(
        DataChanges(
            updates=(CellUpdate(row_key="missing", field="v", value=1, row_version="1"),),
            dataset_version=src._dataset_version,
        )
    )
    assert result.ok is False


def test_113_multifield_batch_conflict() -> None:
    src = InMemoryDataSource(
        [{"id": "1", "a": "x", "b": "y"}],
        writable_fields=frozenset({"a", "b"}),
        version="1",
    )
    ok = src.apply(
        DataChanges(
            updates=(CellUpdate(row_key="1", field="a", value="x2", row_version="1"),),
            dataset_version="1",
        )
    )
    assert ok.ok
    stale = src.apply(
        DataChanges(
            updates=(
                CellUpdate(row_key="1", field="a", value="bad", row_version="1"),
                CellUpdate(row_key="1", field="b", value="bad", row_version="1"),
            ),
            dataset_version="1",
        )
    )
    assert stale.ok is False
    assert stale.conflicts
    page = src.fetch(DataQuery(limit=10))
    assert page.rows[0]["a"] == "x2"
    assert page.rows[0]["b"] == "y"


def test_176_spreadsheet_strips_controls() -> None:
    data = export_rows_xlsx([{"id": "1", "note": "ok\x00bad"}], ["id", "note"])
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert "\x00" not in sheet
    assert "okbad" in sheet or "ok" in sheet


def test_248_import_rejects_incomplete_xlsx() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/workbook.xml", "<x/>")
    with pytest.raises((HedronError, KeyError, ValueError, zipfile.BadZipFile)):
        import_rows_xlsx(buf.getvalue())


def test_191_formula_invisible_prefix() -> None:
    from hedron_data.spreadsheet import _reject_or_sanitize

    assert _reject_or_sanitize("\u200b=1+1", formula_policy="sanitize").startswith("'")


def test_193_rows_to_tree_duplicate_ids() -> None:
    with pytest.raises((ValueError, HedronError)):
        rows_to_tree(
            [
                {"id": "a", "parent": None},
                {"id": "a", "parent": None},
            ],
            id_field="id",
            parent_field="parent",
        )


def test_247_formula_column_en_not_scientific() -> None:
    out = evaluate_formula("[a]*10", {"a": 2})
    assert out == 20
    out2 = evaluate_formula("[ae3]", {"ae3": 7})
    assert out2 == 7


def test_104_221_media_zip_and_range(tmp_path: Path) -> None:
    root = tmp_path
    (root / "a").mkdir()
    (root / "b").mkdir()
    (root / "a" / "file.txt").write_bytes(b"aaa")
    (root / "b" / "file.txt").write_bytes(b"bbb")
    resp = download_all_zip(
        [root / "a" / "file.txt", root / "b" / "file.txt"],
        root=root,
        authorized=True,
        max_total_bytes=1000,
    )
    assert resp.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(resp.body))
    names = set(zf.namelist())
    assert "a/file.txt" in names
    assert "b/file.txt" in names

    big = root / "big.bin"
    big.write_bytes(b"x" * 200_000)
    ranged = media_file_response(
        big,
        root=root,
        filename="big.bin",
        authorized=True,
        range_header="bytes=0-1023",
        max_range_bytes=50_000,
    )
    assert ranged.status_code == 206
    # Prove range path uses StreamingResponse (chunked), not a full buffered body.
    assert ranged.__class__.__name__ == "StreamingResponse"
    assert ranged.headers.get("content-length") == "1024"
    assert ranged.headers.get("content-range", "").startswith("bytes 0-1023/")
