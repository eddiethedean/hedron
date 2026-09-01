"""Bounded data inspection and inert schema projection tests for hedron-core."""

from __future__ import annotations

from collections.abc import Iterator, Mapping

import pytest
from pydantic import BaseModel

from hedron_core.auto.inspect import inspect_data
from hedron_core.diagnostics import HedronError
from hedron_core.schema_sanitizer import projections_from_model, sanitize_json_schema
from hedron_core.type_schema import MAX_SCHEMA_DEPTH


class _Source:
    def inspect_rows(self, *, max_rows: int) -> list[Mapping[str, object]]:
        assert max_rows == 200
        return [{"created_at": "2026-01-01", "lat": 1.0, "kind": "a"}]


class _BrokenSource:
    def inspect_rows(self, *, max_rows: int) -> list[Mapping[str, object]]:
        del max_rows
        raise RuntimeError("offline")


def test_inspect_data_source_reports_shape_cardinality_and_semantics() -> None:
    report = inspect_data(_Source())
    assert report.row_count == 1
    assert report.columns == ("created_at", "lat", "kind")
    assert report.cardinality == {"created_at": 1, "lat": 1, "kind": 1}
    assert report.datetime_columns == ("created_at",)
    assert report.geospatial_columns == ("lat",)
    assert report.bounded is True


def test_inspect_data_source_failure_is_bounded_and_explained() -> None:
    report = inspect_data(_BrokenSource())
    assert report.row_count is None
    assert report.notes == ("datasource inspect skipped: offline",)


def test_inspect_row_and_column_mappings() -> None:
    row = inspect_data({"id": 1, "name": "one"})
    columns = inspect_data({"id": [1, 2], "name": ["one", "two"]})
    assert row.row_count == 1
    assert row.columns == ("id", "name")
    assert columns.row_count == 2
    assert columns.cardinality == {"id": 2, "name": 2}


def test_inspect_column_mapping_enforces_lengths_bounds_and_column_cap() -> None:
    with pytest.raises(HedronError, match="lengths mismatch"):
        inspect_data({"id": [1], "name": ["one", "two"]})

    wide = {f"c{index:02d}": list(range(205)) for index in range(55)}
    report = inspect_data(wide)
    assert report.row_count == 200
    assert len(report.columns) == 50
    assert report.notes == ("truncated rows to 200",)


class _Model:
    def __init__(self, value: int) -> None:
        self.value = value

    def model_dump(self) -> Mapping[str, object]:
        return {"value": self.value}


def test_inspect_sequence_supports_mappings_models_and_truncation() -> None:
    rows: list[object] = [{"id": 1}, _Model(2), "ignored"] + [{"id": i} for i in range(205)]
    report = inspect_data(rows)
    assert report.row_count == 199
    assert report.columns == ("id", "value")
    assert report.notes == ("truncated rows to 200",)


class _LazyRows:
    hedron_lazy = True

    def __iter__(self) -> Iterator[object]:
        return iter(())


def test_inspect_refuses_lazy_iterables_without_collecting() -> None:
    with pytest.raises(HedronError, match="Implicit lazy collection refused"):
        inspect_data(_LazyRows())


class _Columnar:
    columns = ("id", "date")

    def __init__(self, mode: str) -> None:
        self.mode = mode

    def __iter__(self) -> Iterator[object]:
        return iter(())

    def head(self, limit: int) -> _Columnar:
        assert limit == 200
        return self

    def to_dicts(self) -> object:
        if self.mode == "polars":
            return [{1: "one", "date": "today"}]
        return None

    def to_dict(self, *args: object) -> object:
        if self.mode == "fallback" and args:
            raise TypeError("no orient")
        if self.mode in {"pandas", "fallback"}:
            return [{"id": 1}]
        return None


@pytest.mark.parametrize("mode", ["polars", "pandas", "fallback"])
def test_inspect_duck_typed_columnar_tables(mode: str) -> None:
    report = inspect_data(_Columnar(mode))
    assert report.row_count == 1
    assert report.columns


def test_inspect_unrecognized_iterable_is_not_consumed() -> None:
    report = inspect_data(iter([{"would": "consume"}]))
    assert report.row_count is None
    assert report.notes == ("unrecognized iterable list_iterator",)


def test_schema_sanitizer_handles_nested_schema_families_and_inert_scalars() -> None:
    schema = sanitize_json_schema(
        {
            "type": "object",
            "hedron": {"secret": True},
            "properties": {
                "choice": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                "metadata": {"additionalProperties": {"type": "boolean"}},
            },
            "dependentSchemas": {"choice": {"required": ["metadata"]}},
            "prefixItems": [{"type": "string"}, 7, object()],
            "$defs": {"Primitive": "kept", "Odd": object()},
            "description": object(),
            "examples": ["removed"],
        }
    )
    assert "hedron" not in schema
    assert "examples" not in schema
    assert schema["properties"]["choice"]["oneOf"][1] == {"type": "integer"}
    assert schema["prefixItems"][1] == 7
    assert isinstance(schema["prefixItems"][2], str)
    assert schema["$defs"]["Primitive"] == "kept"


@pytest.mark.parametrize(
    "schema",
    [
        {"properties": {"bad": lambda: None}},
        {"anyOf": [lambda: None]},
        {"description": lambda: None},
    ],
)
def test_schema_sanitizer_rejects_executable_values(schema: dict[str, object]) -> None:
    with pytest.raises(HedronError, match="Executable JSON Schema hook refused"):
        sanitize_json_schema(schema)


def test_schema_sanitizer_enforces_depth_and_deep_ref_limits() -> None:
    with pytest.raises(HedronError, match="depth exceeded"):
        sanitize_json_schema({"type": "object"}, depth=MAX_SCHEMA_DEPTH + 1)
    with pytest.raises(HedronError, match="Unsupported schema recursion"):
        sanitize_json_schema({"$ref": "#/$defs/Node"}, depth=9)


def test_schema_projection_handles_absent_and_non_model_types() -> None:
    class NoSchema:
        pass

    class InvalidSchema:
        @classmethod
        def model_json_schema(cls) -> object:
            return []

    assert projections_from_model(None) == ({}, {}, (), (), ())
    assert projections_from_model(NoSchema, sensitive=("token",), computed=("total",)) == (
        {},
        {},
        (),
        ("token",),
        ("total",),
    )
    assert projections_from_model(InvalidSchema) == ({}, {}, (), (), ())


def test_schema_projection_removes_top_level_and_nested_sensitive_fields() -> None:
    class Credentials(BaseModel):
        username: str
        token: str

    class Envelope(BaseModel):
        credentials: Credentials
        request_secret: str
        display_name: str
        computed_total: int

    input_schema, output_schema, shared, write_only, read_only = projections_from_model(
        Envelope,
        sensitive=("request_secret", "Credentials.token"),
        computed=("computed_total",),
    )

    assert write_only == ("request_secret",)
    assert read_only == ("computed_total",)
    assert shared == ("credentials", "display_name")
    assert "computed_total" not in input_schema["properties"]
    assert "request_secret" not in output_schema["properties"]
    assert "token" not in output_schema["$defs"]["Credentials"]["properties"]
    assert "token" in input_schema["$defs"]["Credentials"]["properties"]
