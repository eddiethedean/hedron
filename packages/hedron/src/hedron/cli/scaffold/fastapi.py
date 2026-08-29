"""Scaffold for ``hedron new`` FastAPI apps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hedron.cli.discovery import scaffold_dep as _scaffold_dep


def _pyproject(*, name: str, extra_deps: list[str] | None = None) -> str:
    deps = [
        _scaffold_dep("hedron"),
        "uvicorn[standard]>=0.30",
        *(extra_deps or ()),
    ]
    dep_lines = ",\n".join(f'    "{dep}"' for dep in deps)
    return f'''[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
{dep_lines},
]

[tool.hedron]
component_roots = ["components"]
theme = "default"
explorer = "off"
'''


def _app_minimal() -> str:
    return """import os
from datetime import datetime, timezone

from hedron import CsrfField, Hedron, SafeUrl, Stack, Text, UrlPurpose, html

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    theme="default",
    session_secret=os.environ.get(
        # Convention only — Hedron does not load HEDRON_SESSION_SECRET itself.
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.action("/ping")
def ping():
    from hedron import refresh

    return refresh(status).toast("Refreshed")


@app.page("/")
def home():
    return Stack(
        Text("Hello from hedron new"),
        status(),
        html.form(
            html.button("Refresh status", type="submit"),
            method="get",
            action=SafeUrl.parse(status.path, purpose=UrlPurpose.FORM_ACTION),
        ),
        html.form(
            CsrfField(),
            html.button("Ping", type="submit"),
            method="post",
            action=SafeUrl.parse("/ping", purpose=UrlPurpose.FORM_ACTION),
        ),
    )
"""


def _app_crud() -> str:
    return """import os
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, Field

from hedron import CsrfField, DesignSystem, Hedron, Stack, Text, html
from hedron_data import DataWorkspace, DataWorkspacePolicy, InMemoryDataSource

design = DesignSystem.brand("scaffold", accent="#2563eb")

app = Hedron(
    title="Hedron CRUD",
    security="standard",
    explorer="off",
    theme=design,
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)


class Order(BaseModel):
    id: str
    customer: str = "acme"
    quantity: int = Field(gt=0, le=100)


class QuickNote(BaseModel):
    message: str = Field(min_length=1, max_length=200)


# In-memory only — replace with an authorized durable DataEditorSource in production.
_SOURCE = InMemoryDataSource(
    [{"id": "1", "customer": "acme", "quantity": 2}],
    key_field="id",
    writable_fields=frozenset({"customer", "quantity"}),
)

orders = DataWorkspace(
    name="orders",
    model=Order,
    source=_SOURCE,
    policy=DataWorkspacePolicy(
        can_read=lambda: True,
        can_create=lambda: True,
        can_edit=lambda: True,
    ),
).with_screen(path="/orders", title="Orders")
app.include(orders)


@app.action("/notes")
def add_note(message: Annotated[str, Form(min_length=1, max_length=200)]):
    return Text(message)


@app.page("/")
def home():
    return Stack(
        Text("CRUD scaffold — open /orders for the DataWorkspace screen."),
        Text("Production replacements: persistence, authorization, transactions."),
        html.form(
            CsrfField(),
            html.input(name="message", required=True),
            html.button("Save", type="submit"),
            method="post",
            action=SafeUrl.parse("/notes", purpose=UrlPurpose.FORM_ACTION),
        ),
    )
"""


def _app_dashboard() -> str:
    return """import os

from pydantic import BaseModel, Field

from hedron import DashboardWorkspace, DesignSystem, Hedron, Text

design = DesignSystem.brand("scaffold", accent="#0f766e")

app = Hedron(
    title="Hedron Dashboard",
    security="standard",
    explorer="off",
    theme=design,
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)


class Filters(BaseModel):
    region: str = "all"
    limit: int = Field(default=5, ge=1, le=50)


class DashData(BaseModel):
    region: str
    total: int


def load_dashboard(filters: Filters) -> DashData:
    # Synthetic loader — replace with authorized IO and caching policy in production.
    base = 42 if filters.region == "all" else 7
    return DashData(region=filters.region, total=base * filters.limit)


def summary_panel(data: DashData) -> object:
    return Text(f"{data.region}: {data.total}")


dashboard = DashboardWorkspace(
    name="sales",
    path="/sales",
    title="Sales",
    filters=Filters,
    load=load_dashboard,
    panels={"summary": summary_panel},
)
app.include(dashboard)


@app.page("/")
def home():
    return Text(
        "Dashboard scaffold — open /sales. "
        "Replace loader/cache/authorization for production."
    )
"""


def _app_task() -> str:
    return '''import os

from fastapi import Depends
from pydantic import BaseModel, Field

from hedron import DesignSystem, Hedron, JobScope, Stack, TaskFlow, Text
from hedron_core.jobs import InMemoryJobBackend, set_job_backend

design = DesignSystem.brand("scaffold", accent="#b45309")

app = Hedron(
    title="Hedron Task",
    security="standard",
    explorer="off",
    theme=design,
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)

# Development-only backend. Replace with a durable JobBackend, workers, and
# retention policy before production (see hedron production gates).
set_job_backend(InMemoryJobBackend())


class ReportRequest(BaseModel):
    label: str = Field(min_length=1, max_length=80)


def report_payload(data: ReportRequest) -> dict[str, object]:
    return {"label": data.label}


def current_job_scope() -> JobScope:
    return JobScope(auth_subject="dev", tenant_id="local")


def allow_dev() -> None:
    """Open development authorization — replace with real Depends authz."""
    return None


def report_result(result: object) -> object:
    return Text(str(result))


reports = TaskFlow(
    name="report",
    input_model=ReportRequest,
    job_type="build-report",
    payload=report_payload,
    scope=current_job_scope,
    authorize_submit=Depends(allow_dev),
    result=report_result,
)
app.include(reports)


@app.page("/")
def home():
    submit = reports.submit_command
    return Stack(
        Text("TaskFlow scaffold (InMemoryJobBackend — replace for production)."),
        submit.form() if submit is not None else Text("Submit surface pending include."),
    )
'''


_TEMPLATES = {
    "minimal": (_app_minimal, None),
    "crud": (_app_crud, [_scaffold_dep("hedron-data")]),
    "dashboard": (_app_dashboard, None),
    "task": (_app_task, None),
}


def scaffold_fastapi(args: argparse.Namespace, dest: Path) -> int:
    template = str(getattr(args, "template", None) or "minimal")
    if template not in _TEMPLATES:
        raise SystemExit(f"Unknown --template {template!r}")
    app_factory, extra_deps = _TEMPLATES[template]
    (dest / "pyproject.toml").write_text(
        _pyproject(name=args.name, extra_deps=extra_deps),
        encoding="utf-8",
    )
    (dest / "app.py").write_text(app_factory(), encoding="utf-8")
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "fastapi",
                "template": template,
                "files": ["pyproject.toml", "app.py", "components/"],
            },
            indent=2,
        )
    )
    return 0


_scaffold_fastapi = scaffold_fastapi
