"""Runnable result of the Streamlit sales-dashboard migration guide."""

from __future__ import annotations

import os
from typing import Annotated, Literal

from fastapi import Query

from hedron import (
    Form,
    FormField,
    Grid,
    Heading,
    Hedron,
    Metric,
    Model,
    Page,
    Select,
    Sidebar,
    Stack,
    SubmitButton,
    Table,
    cache_data,
    html,
)
from hedron_data import DataTable

Region = Literal["All", "North", "South"]


class SalesRow(Model):
    month: str
    region: str
    revenue: int
    orders: int


@cache_data(ttl=300, scope="public")
def load_sales() -> list[SalesRow]:
    """Return public sample data; real user-dependent data must not use public scope."""
    return [
        SalesRow(month="Jan", region="North", revenue=3200, orders=32),
        SalesRow(month="Feb", region="North", revenue=4100, orders=38),
        SalesRow(month="Mar", region="North", revenue=4600, orders=41),
        SalesRow(month="Jan", region="South", revenue=2800, orders=29),
        SalesRow(month="Feb", region="South", revenue=3600, orders=34),
        SalesRow(month="Mar", region="South", revenue=4300, orders=39),
    ]


app = Hedron(
    title="Sales dashboard",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "local-migration-demo-only"),
)


@app.page("/")
def dashboard(
    region: Annotated[Region, Query()] = "All",
    minimum: Annotated[int, Query(ge=0, le=5000)] = 0,
) -> Page:
    filtered = [
        row
        for row in load_sales()
        if (region == "All" or row.region == region) and row.revenue >= minimum
    ]

    by_month: dict[str, int] = {}
    for row in filtered:
        by_month[row.month] = by_month.get(row.month, 0) + row.revenue

    filters = Sidebar(
        Heading("Filters", level=2),
        Form(
            FormField(
                name="region",
                label="Region",
                control=Select(
                    "region",
                    [(value, value) for value in ("All", "North", "South")],
                    value=region,
                ),
            ),
            FormField(
                name="minimum",
                label="Minimum revenue",
                control=html.input(
                    type="range",
                    name="minimum",
                    min="0",
                    max="5000",
                    step="500",
                    value=str(minimum),
                ),
            ),
            SubmitButton("Apply filters"),
            action="/",
            method="get",
        ),
        label="Dashboard filters",
    )

    monthly_rows = [
        [month, f"${revenue:,}"] for month, revenue in by_month.items()
    ] or [["—", "No rows"]]

    content = Stack(
        Heading("Sales dashboard", level=1),
        Grid(
            Metric("Revenue", f"${sum(row.revenue for row in filtered):,}"),
            Metric("Orders", sum(row.orders for row in filtered)),
            columns=2,
        ),
        Heading("Revenue by month", level=2),
        Table(
            ["Month", "Revenue"],
            monthly_rows,
            caption="Monthly revenue for the selected filters.",
        ),
        DataTable(
            filtered,
            row_model=SalesRow,
            caption="Filtered sales",
            empty_message="No sales match these filters.",
        ),
    )

    return Page(Grid(filters, content, columns=2), title="Sales dashboard")
