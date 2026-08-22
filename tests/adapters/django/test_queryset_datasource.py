"""Bounded Django QuerySet DataSource tests (phase 0.11 / D-046)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from hedron_core.diagnostics import HedronError
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


def test_deny_by_default_client_filters() -> None:
    base = FakeQuerySet([FakeObj(1, "Ada", "t1"), FakeObj(2, "Grace", "t1")])
    source = DjangoQuerySetDataSource(
        base,
        row_mapper=lambda o: {"pk": o.pk, "name": o.name},
    )
    try:
        source.fetch(DataQuery(limit=10, filters={"name": "Ada"}))
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_deny_by_default_client_sort() -> None:
    base = FakeQuerySet([FakeObj(1, "Ada", "t1")])
    source = DjangoQuerySetDataSource(
        base,
        row_mapper=lambda o: {"pk": o.pk, "name": o.name},
    )
    try:
        source.fetch(DataQuery(limit=10, sort=(("name", "asc"),)))
        raised = False
    except ValueError:
        raised = True
    assert raised


@pytest.fixture
def person_model():
    """Real Django model + table for QuerySet DataSource evidence."""
    from django.apps import apps
    from django.db import connection, models

    Person = None
    for model in apps.get_models():
        if getattr(model._meta, "db_table", None) == "hedron_test_person_qs":
            Person = model
            break
    if Person is None:

        class Person(models.Model):
            name = models.CharField(max_length=64)
            tenant_id = models.CharField(max_length=32)

            class Meta:
                app_label = "hedron_django"
                db_table = "hedron_test_person_qs"

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Person)

    Person.objects.all().delete()
    yield Person
    Person.objects.all().delete()


def test_orm_tenant_scope_cannot_widen(person_model) -> None:
    Person = person_model
    Person.objects.bulk_create(
        [
            Person(name="Ada", tenant_id="t1"),
            Person(name="Grace", tenant_id="t1"),
            Person(name="Alan", tenant_id="t2"),
        ]
    )
    scoped = Person.objects.filter(tenant_id="t1")
    source = DjangoQuerySetDataSource(
        scoped,
        key_field="pk",
        schema=(
            ColumnSchema(name="name", label="Name"),
            ColumnSchema(name="tenant_id", label="Tenant"),
        ),
        allowlisted_filter_fields=frozenset({"name", "tenant_id"}),
        allowlisted_sort_fields=frozenset({"name", "pk"}),
        search_fields=("name",),
    )
    page = source.fetch(DataQuery(limit=10))
    assert page.total == 2
    assert all(r["tenant_id"] == "t1" for r in page.rows)

    # Client filter on tenant_id can only narrow within the pre-scoped base.
    narrowed = source.fetch(DataQuery(limit=10, filters={"tenant_id": "t2"}))
    assert narrowed.total == 0
    assert narrowed.rows == []

    searched = source.fetch(DataQuery(limit=10, search="Ada"))
    assert searched.total == 1
    assert searched.rows[0]["name"] == "Ada"


def test_orm_deny_unallowlisted_filter(person_model) -> None:
    Person = person_model
    Person.objects.create(name="Ada", tenant_id="t1")
    source = DjangoQuerySetDataSource(
        Person.objects.filter(tenant_id="t1"),
        allowlisted_filter_fields=frozenset({"name"}),
    )
    with pytest.raises(ValueError):
        source.fetch(DataQuery(limit=10, filters={"tenant_id": "t2"}))


def test_orm_search_without_fields_fails_closed(person_model) -> None:
    Person = person_model
    Person.objects.create(name="Ada", tenant_id="t1")
    source = DjangoQuerySetDataSource(Person.objects.all())
    with pytest.raises(HedronError, match="HED-DATA-0012"):
        source.fetch(DataQuery(limit=10, search="Ada"))


def test_orm_max_page_size_and_projection(person_model) -> None:
    Person = person_model
    Person.objects.bulk_create([Person(name=f"n{i}", tenant_id="t1") for i in range(5)])
    source = DjangoQuerySetDataSource(
        Person.objects.filter(tenant_id="t1"),
        schema=(
            ColumnSchema(name="name", label="Name"),
            ColumnSchema(name="tenant_id", label="Tenant"),
        ),
        max_page_size=2,
        allowlisted_sort_fields=frozenset({"name", "pk"}),
    )
    page = source.fetch(DataQuery(limit=100, projection=("name",)))
    assert len(page.rows) == 2
    assert all(set(r.keys()) == {"name"} for r in page.rows)
