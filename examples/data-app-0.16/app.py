"""Phase 0.16 analysis workbench sample."""

from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

from hedron import Hedron, Page, Text
from hedron.testing import transform_plan_fixture
from hedron_core.rendering import RenderMode, render
from hedron_extras import (
    CallableActionForm,
    ChoiceCards,
    ChoiceOption,
    CodeEditor,
    DataExplorer,
    JSONEditor,
    Steps,
    TreeView,
)

app = FastAPI(title="Hedron 0.16 workbench sample")
hedron = Hedron(app)


def _page(*body: object) -> str:
    return render(Page(*body, title="0.16 workbench"), mode=RenderMode.DOCUMENT).html


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _page(
        Text("Hedron 0.16 analysis workbench"),
        Steps(["Explore", "Edit", "Export"], current=0),
        ChoiceCards(
            "mode",
            [
                ChoiceOption(value="table", label="Table"),
                ChoiceOption(value="json", label="JSON"),
            ],
            selected=["table"],
        ),
        TreeView(
            [
                {
                    "id": "datasets",
                    "label": "Datasets",
                    "children": [{"id": "demo", "label": "demo.csv", "children": []}],
                }
            ]
        ),
        DataExplorer(
            [{"field": "status", "label": "Status", "values": ["open", "closed"]}],
            max_rows=100,
        ),
        JSONEditor({"status": "open", "count": 3}, schema={"type": "object"}),
        CodeEditor("print('bounded submit only')", language="python"),
        CallableActionForm(
            "export_csv",
            [{"name": "limit", "label": "Limit", "kind": "int"}],
            title="Export",
        ),
    )


@app.post("/export", response_class=HTMLResponse)
async def export(
    request: Request,
    hedron_action: str = Form("export_csv"),
    limit: int = Form(10),
) -> str:
    # Ordinary HTTP path — no implicit callable execution.
    plan = transform_plan_fixture(limit=min(max(limit, 1), 100))
    return _page(
        Text(f"Authorized action={hedron_action} plan_rows={plan.max_rows}"),
        Text("Same domain action available without extras JS."),
    )
