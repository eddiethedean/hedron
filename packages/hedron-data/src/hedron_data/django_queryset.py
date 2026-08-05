"""Bounded Django QuerySet DataSource (D-046)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from hedron_data.sources import (
    ColumnSchema,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

__all__ = ["DjangoQuerySetDataSource", "QueryBudgetExceeded", "QueryDiagnostics"]


class QueryBudgetExceeded(RuntimeError):
    """Raised when a fetch exceeds the configured query-count budget."""


class QueryDiagnostics:
    """Mutable query-count diagnostics for the current fetch/apply."""

    __slots__ = ("query_count", "budget")

    def __init__(self, *, budget: int = 25) -> None:
        self.query_count = 0
        self.budget = budget

    def record(self, n: int = 1) -> None:
        self.query_count += n
        if self.query_count > self.budget:
            raise QueryBudgetExceeded(f"Query budget exceeded: {self.query_count} > {self.budget}")


class DjangoQuerySetDataSource:
    """``DataEditorSource`` backed by an application-supplied authorized QuerySet.

    The constructor never discovers models or calls ``.objects.all()``. Tenant/auth
    scoping must already be applied on ``base_queryset`` and cannot be removed by
    client refinements.
    """

    def __init__(
        self,
        base_queryset: Any,
        *,
        key_field: str = "pk",
        schema: Sequence[ColumnSchema] = (),
        allowlisted_sort_fields: frozenset[str] | None = None,
        allowlisted_filter_fields: frozenset[str] | None = None,
        search_fields: Sequence[str] = (),
        max_page_size: int = 100,
        query_budget: int = 25,
        row_mapper: Callable[[Any], dict[str, Any]] | None = None,
        apply_changes: Callable[[DataChanges[dict[str, Any]]], DataSaveResult[dict[str, Any]]]
        | None = None,
        transaction_owner: str = "application",
    ) -> None:
        type_name = type(base_queryset).__name__
        if not type_name.endswith("QuerySet"):
            raise TypeError(
                "DjangoQuerySetDataSource requires an application-supplied QuerySet; "
                f"got {type_name!r}"
            )
        self._base = base_queryset
        self._key_field = key_field
        self._schema = tuple(schema)
        # Deny-by-default: omitted allowlists mean no client sort/filter refinements.
        self._sort_allow = (
            frozenset() if allowlisted_sort_fields is None else allowlisted_sort_fields
        )
        self._filter_allow = (
            frozenset() if allowlisted_filter_fields is None else allowlisted_filter_fields
        )
        self._search_fields = tuple(search_fields)
        self._max_page_size = max_page_size
        self._query_budget = query_budget
        self._row_mapper = row_mapper or self._default_mapper
        self._apply_changes = apply_changes
        self.transaction_owner = transaction_owner
        self.last_diagnostics = QueryDiagnostics(budget=query_budget)

    def _default_mapper(self, obj: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self._schema:
            for col in self._schema:
                data[col.name] = getattr(obj, col.name, None)
        else:
            data[self._key_field] = getattr(obj, self._key_field, getattr(obj, "pk", None))
            # Prefer model_to_dict when available without importing django at module import
            # for non-Django environments that only construct the class.
            try:
                from django.forms.models import model_to_dict

                data.update(model_to_dict(obj))
            except Exception:  # noqa: BLE001
                for field in getattr(obj, "_meta", None).fields if hasattr(obj, "_meta") else ():
                    data[field.name] = getattr(obj, field.name, None)
        data.setdefault(self._key_field, getattr(obj, "pk", data.get(self._key_field)))
        return data

    def describe_schema(self) -> tuple[ColumnSchema, ...]:
        """Return schema without evaluating the QuerySet."""
        return self._schema

    def fetch(self, query: DataQuery) -> DataPage[dict[str, Any]]:
        q = DataQuery(
            offset=query.offset,
            limit=query.limit,
            cursor=query.cursor,
            sort=query.sort,
            filters=query.filters,
            projection=query.projection,
            search=query.search,
            locale=query.locale,
            allowlisted_sort_fields=self._sort_allow,
            allowlisted_filter_fields=self._filter_allow,
        ).validated(max_page_size=self._max_page_size)

        diag = QueryDiagnostics(budget=self._query_budget)
        self.last_diagnostics = diag
        qs = self._base
        diag.record()  # base identity / clone

        for field_name, expected in q.filters.items():
            qs = qs.filter(**{field_name: expected})
            diag.record()

        if q.search and self._search_fields:
            from django.db.models import Q

            clause = Q()
            for field_name in self._search_fields:
                clause |= Q(**{f"{field_name}__icontains": q.search})
            qs = qs.filter(clause)
            diag.record()

        order_by: list[str] = []
        for field_name, direction in q.sort:
            order_by.append(field_name if direction == "asc" else f"-{field_name}")
        if order_by:
            qs = qs.order_by(*order_by)
            diag.record()
        elif not qs.query.order_by:
            # Deterministic pagination requires stable ordering.
            qs = qs.order_by(self._key_field if self._key_field != "pk" else "pk")
            diag.record()

        total = qs.count()
        diag.record()
        page_qs = qs[q.offset : q.offset + q.limit]
        diag.record()
        rows = [self._row_mapper(obj) for obj in page_qs]
        if q.projection:
            rows = [{k: r.get(k) for k in q.projection} for r in rows]
        next_offset = q.offset + q.limit if q.offset + q.limit < total else None
        return DataPage(
            rows=rows,
            schema=self._schema,
            total=total,
            next_offset=next_offset,
            version=None,
        )

    def apply(self, changes: DataChanges[dict[str, Any]]) -> DataSaveResult[dict[str, Any]]:
        if self._apply_changes is None:
            return DataSaveResult(
                ok=False,
                field_errors=(
                    FieldError(
                        row_key="*",
                        field=None,
                        message=(
                            "Mutations require an application-supplied apply_changes "
                            f"callback (transaction_owner={self.transaction_owner!r})"
                        ),
                    ),
                ),
            )
        return self._apply_changes(changes)
