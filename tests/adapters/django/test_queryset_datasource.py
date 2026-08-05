"""Bounded Django QuerySet DataSource tests (phase 0.11 / D-046)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hedron_data import ColumnSchema, DataQuery, DjangoQuerySetDataSource, QueryBudgetExceeded


@dataclass
class FakeObj:
    pk: int
    name: str
    tenant_id: str


class FakeQuerySet:
    """Minimal QuerySet-like object for unit tests without migrations."""

    def __init__(self, rows: list[FakeObj]) -> None:
        self._rows = list(rows)
        self.query = type("Q", (), {"order_by": ()})()

    def filter(self, **kwargs: Any) -> FakeQuerySet:
        items = self._rows
        for key, value in kwargs.items():
            if key.endswith("__icontains"):
                field = key[: -len("__icontains")]
                items = [r for r in items if value.lower() in str(getattr(r, field)).lower()]
            else:
                items = [r for r in items if getattr(r, key) == value]
        return FakeQuerySet(items)

    def order_by(self, *fields: str) -> FakeQuerySet:
        items = list(self._rows)
        for field in reversed(fields):
            desc = field.startswith("-")
            name = field[1:] if desc else field
            items.sort(key=lambda r: getattr(r, name), reverse=desc)
        qs = FakeQuerySet(items)
        qs.query = type("Q", (), {"order_by": fields})()
        return qs

    def count(self) -> int:
        return len(self._rows)

    def __getitem__(self, item: slice) -> list[FakeObj]:
        return self._rows[item]


def test_fetch_respects_tenant_scope() -> None:
    base = FakeQuerySet(
        [
            FakeObj(1, "Ada", "t1"),
            FakeObj(2, "Grace", "t1"),
            FakeObj(3, "Alan", "t2"),
        ]
    )
    scoped = base.filter(tenant_id="t1")
    source = DjangoQuerySetDataSource(
        scoped,
        key_field="pk",
        schema=(ColumnSchema(name="name", label="Name"),),
        allowlisted_filter_fields=frozenset({"name"}),
        allowlisted_sort_fields=frozenset({"name", "pk"}),
        row_mapper=lambda o: {"pk": o.pk, "name": o.name, "tenant_id": o.tenant_id},
    )
    page = source.fetch(DataQuery(limit=10))
    assert page.total == 2
    assert all(r["tenant_id"] == "t1" for r in page.rows)
    page2 = source.fetch(DataQuery(limit=10, filters={"name": "Ada"}))
    assert page2.total == 1
    assert page2.rows[0]["name"] == "Ada"


def test_query_budget() -> None:
    base = FakeQuerySet([FakeObj(i, f"n{i}", "t1") for i in range(5)])
    source = DjangoQuerySetDataSource(
        base,
        query_budget=1,
        row_mapper=lambda o: {"pk": o.pk, "name": o.name},
    )
    raised = False
    try:
        source.fetch(DataQuery(limit=5))
    except QueryBudgetExceeded:
        raised = True
    assert raised


def test_rejects_non_queryset() -> None:
    try:
        DjangoQuerySetDataSource([1, 2, 3])  # type: ignore[arg-type]
        raised = False
    except TypeError:
        raised = True
    assert raised


def test_schema_without_evaluation() -> None:
    base = FakeQuerySet([FakeObj(1, "Ada", "t1")])
    schema = (ColumnSchema(name="name", label="Name"),)
    source = DjangoQuerySetDataSource(base, schema=schema)
    assert source.describe_schema() == schema
