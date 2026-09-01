"""REGRESS-039 data normalize / memory / query / formula / tree fixes."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.security import Secret
from hedron_data.advanced import evaluate_formula, rows_to_tree
from hedron_data.memory import InMemoryDataSource
from hedron_data.normalize import normalize_rows
from hedron_data.sources import CellUpdate, DataChanges, DataQuery


def test_039_normalize_rows_empty_dict() -> None:
    assert normalize_rows({}) == []


def test_039_normalize_rows_column_length_mismatch() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0005"):
        normalize_rows({"a": [1], "b": [1, 2]})
    with pytest.raises(HedronError, match="HED-DATA-0005"):
        normalize_rows({"a": [], "b": [1, 2]})
    assert normalize_rows({"a": [1, 2], "b": [3, 4]}) == [
        {"a": 1, "b": 3},
        {"a": 2, "b": 4},
    ]


def test_039_normalize_dataframe_respects_explicit_max_rows() -> None:
    pandas = pytest.importorskip("pandas")
    with pytest.raises(HedronError, match="HED-DATA-0004"):
        normalize_rows(pandas.DataFrame({"a": [1, 2]}), max_rows=1)


def test_039_inmemory_rejects_duplicate_and_missing_keys() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0011"):
        InMemoryDataSource([{"id": "1", "value": "first"}, {"id": "1", "value": "second"}])
    with pytest.raises(HedronError, match="HED-DATA-0010"):
        InMemoryDataSource(rows=[{"name": "alice"}], key_field="id")


def test_039_inmemory_sorts_mixed_json_types() -> None:
    source = InMemoryDataSource(
        [{"id": "1", "value": 1}, {"id": "2", "value": "2"}, {"id": "3", "value": None}],
        allowlisted_sort_fields=frozenset({"value"}),
    )
    page = source.fetch(DataQuery(sort=(("value", "asc"),)))
    assert [r["id"] for r in page.rows] == ["3", "1", "2"]


def test_oversized_formula_integer_fails_as_diagnostic() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("[huge]", {"huge": 10**1000})


def test_039_dataquery_validates_direction_and_max_page_size() -> None:
    with pytest.raises(ValueError, match="sort direction"):
        DataQuery(sort=(("x", "sideways"),)).validated()
    with pytest.raises(ValueError, match="max_page_size"):
        DataQuery(limit=10).validated(max_page_size=0)


@pytest.mark.parametrize("value", [1, True, b"needle", ["needle"]])
def test_dataquery_rejects_non_string_search(value: object) -> None:
    with pytest.raises(ValueError, match="search"):
        DataQuery(search=value).validated()  # type: ignore[arg-type]


def test_offset_only_memory_source_rejects_cursor() -> None:
    with pytest.raises(ValueError, match="cursor pagination"):
        InMemoryDataSource([{"id": "1"}]).fetch(DataQuery(cursor="opaque"))


@pytest.mark.parametrize("value", [0, -1, True, 1.5, float("nan"), float("inf"), "10"])
def test_normalize_rows_rejects_invalid_row_budget(value: object) -> None:
    with pytest.raises(ValueError, match="max_rows"):
        normalize_rows([], max_rows=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, True, 1.5, float("nan"), float("inf"), "10"])
def test_memory_source_rejects_invalid_row_budget(value: object) -> None:
    with pytest.raises(ValueError, match="max_rows"):
        InMemoryDataSource([], max_rows=value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "query",
    [
        DataQuery(sort=None),  # type: ignore[arg-type]
        DataQuery(sort="name"),  # type: ignore[arg-type]
        DataQuery(sort=((None, "asc"),)),  # type: ignore[arg-type]
        DataQuery(filters=None),  # type: ignore[arg-type]
        DataQuery(projection="name"),  # type: ignore[arg-type]
        DataQuery(projection=(None,)),  # type: ignore[arg-type]
    ],
)
def test_dataquery_rejects_malformed_collection_shapes(query: DataQuery) -> None:
    with pytest.raises(ValueError):
        query.validated()


def test_039_inmemory_multi_field_batch_same_row_version() -> None:
    source = InMemoryDataSource(
        [{"id": "1", "first": "Ada", "last": "Lovelace"}],
        writable_fields=frozenset({"first", "last"}),
        version="1",
    )
    result = source.apply(
        DataChanges(
            updates=(
                CellUpdate(row_key="1", field="first", value="Augusta", row_version="1"),
                CellUpdate(row_key="1", field="last", value="King", row_version="1"),
            )
        )
    )
    assert result.ok is True
    page = source.fetch(DataQuery())
    assert page.rows[0]["first"] == "Augusta"
    assert page.rows[0]["last"] == "King"
    assert source._row_versions["1"] == "2"  # one bump for the whole row


def test_open_bug_inmemory_fetch_and_nested_secret_are_isolated() -> None:
    source = InMemoryDataSource([{"id": "1", "payload": {"name": "Ada"}}])
    page = source.fetch(DataQuery())
    page.rows[0]["payload"]["name"] = "Eve"  # type: ignore[index]
    assert source.fetch(DataQuery()).rows[0]["payload"] == {"name": "Ada"}

    rows = normalize_rows([{"nested": {"token": Secret("secret")}}])
    assert rows == [{"nested": {"token": "***"}}]

    columns = normalize_rows(
        {
            "token": [Secret("column-secret")],
            "nested": [{"password": Secret("nested-column-secret")}],
        }
    )
    assert columns == [{"token": "***", "nested": {"password": "***"}}]


def test_039_rows_to_tree_rejects_duplicate_ids() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0034"):
        rows_to_tree(
            [
                {"id": "1", "label": "first", "parent_id": None},
                {"id": "1", "label": "second", "parent_id": None},
            ],
            id_field="id",
            parent_field="parent_id",
        )


def test_039_evaluate_formula_rejects_scientific_juxtaposition() -> None:
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("=[a]e3", {"a": 2})
    with pytest.raises(HedronError, match="HED-DATA-0032"):
        evaluate_formula("=[a]e+3", {"a": 2})
    assert evaluate_formula("=[a]*[b]", {"a": 2, "b": 3}) == 6.0
    assert evaluate_formula("=1e3", {}) == 1000.0
