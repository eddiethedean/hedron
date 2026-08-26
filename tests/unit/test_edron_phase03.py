"""PHASE-EDRON-03: explicit data editing and workspace ergonomics."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel
from starlette.testclient import TestClient

import edron as ed
from hedron_data import FieldError


def make_workspace(
    *, authorize: bool = True, required_principal: object | None = "user-1"
) -> tuple[ed.DataWorkspace, list[ed.AuditEvent]]:
    columns = (
        ed.Column("id", read_only=True, sortable=True, filterable=True),
        ed.Column("name", writable=True, sortable=True, filterable=True),
        ed.Column("tenant", hidden=True, read_only=True),
        ed.Column("secret", hidden=True, secret=True),
    )
    source = ed.DataSource.in_memory(
        [
            {"id": "1", "name": "Ada", "tenant": "a", "secret": "x"},
            {"id": "2", "name": "Grace", "tenant": "a", "secret": "y"},
        ],
        columns=columns,
        writable_fields=("name",),
        sort_fields=("id", "name"),
        filter_fields=("id", "name"),
        projection_fields=("id", "name"),
        search_fields=("name",),
    )
    audit: list[ed.AuditEvent] = []

    def authorize_edit(intent: ed.EditIntent, principal: object | None) -> bool:
        return authorize and principal == required_principal

    def validate_edit(intent: ed.EditIntent) -> tuple[FieldError, ...]:
        return (
            (FieldError("1", "name", "Name is required"),)
            if any(item.field == "name" and not item.value for item in intent.updates)
            else ()
        )

    workspace = ed.DataWorkspace(
        "people",
        source=source,
        columns=columns,
        edit=ed.EditPolicy(
            writable_fields=frozenset({"name"}),
            authorize=authorize_edit,
            validate=validate_edit,
            audit=audit.append,
        ),
    )
    return workspace, audit


def test_workspace_pages_sort_filters_search_and_bounds() -> None:
    workspace, _ = make_workspace()
    page = workspace.page(ed.PageRequest(limit=1, sort=(("name", "desc"),)))
    assert page.rows[0]["name"] == "Grace"
    assert page.total == 2
    assert page.next_offset == 1

    found = workspace.page(ed.PageRequest(search="ada"))
    assert [row["id"] for row in found.rows] == ["1"]
    filtered = workspace.page(ed.PageRequest(filters={"id": "2"}))
    assert [row["name"] for row in filtered.rows] == ["Grace"]

    with pytest.raises(ed.BindingError, match="allowlisted"):
        workspace.page(ed.PageRequest(sort=(("secret", "asc"),)))
    capped = workspace.page(ed.PageRequest(limit=10_000))
    assert len(capped.rows) == 2


def test_edit_is_authorized_validated_concurrent_and_audited() -> None:
    workspace, audit = make_workspace()
    denied = workspace.apply(
        ed.EditIntent(updates=(ed.CellEdit("1", "name", "Augusta", "1"),)),
        principal="intruder",
    )
    assert not denied.ok and denied.errors
    assert audit[-1].outcome == "rejected"

    invalid = workspace.apply(
        ed.EditIntent(updates=(ed.CellEdit("1", "name", "", "1"),)),
        principal="user-1",
    )
    assert not invalid.ok and invalid.errors[0].message == "Name is required"

    accepted = workspace.apply(
        ed.EditIntent(
            updates=(ed.CellEdit("1", "name", "Augusta", "1"),),
            reason="correction",
        ),
        principal="user-1",
    )
    assert accepted.ok
    assert audit[-1].outcome == "accepted"
    assert audit[-1].reason == "correction"
    assert not hasattr(audit[-1], "value")

    stale = workspace.apply(
        ed.EditIntent(updates=(ed.CellEdit("1", "name", "Stale", "1"),)),
        principal="user-1",
    )
    assert not stale.ok and stale.conflicts
    assert audit[-1].outcome == "conflict"


def test_forged_fields_inserts_and_deletes_fail_closed() -> None:
    workspace, _ = make_workspace()
    forged = workspace.apply(
        ed.EditIntent(updates=(ed.CellEdit("1", "secret", "leak"),)),
        principal="user-1",
    )
    assert not forged.ok and forged.errors[0].field == "secret"

    inserted = workspace.apply(
        ed.EditIntent(inserts=({"id": "3", "name": "Lin"},)), principal="user-1"
    )
    assert not inserted.ok and "Inserts" in inserted.errors[0].message
    deleted = workspace.apply(ed.EditIntent(deletes=("1",)), principal="user-1")
    assert not deleted.ok and "Deletes" in deleted.errors[0].message


def test_selection_and_csv_export_are_bounded_to_authorized_page() -> None:
    workspace, _ = make_workspace()
    page = workspace.page(selection=ed.DataSelection(("2",)))
    exported = workspace.export_csv(page)
    assert exported.row_count == 1
    assert exported.filename == "people.csv"
    text = exported.content.decode()
    assert "Grace" in text and "Ada" not in text
    assert "secret" not in text and "tenant" not in text

    with pytest.raises(ed.BindingError, match="outside the authorized page"):
        workspace.page(ed.PageRequest(limit=1), selection=ed.DataSelection(("2",)))


def test_page_facade_renders_native_table_editor_and_fallback() -> None:
    workspace, audit = make_workspace(required_principal=None)
    app = ed.App(title="Data", session_secret="test")
    app.data_workspace(workspace)
    assert app.native_surface(workspace) is not None
    assert app.explain()["data_workspaces"][0]["save_path"] == workspace.save_endpoint

    @app.page("/", title="People")
    class People(ed.Page):
        def render(self) -> None:
            self.data_workspace(workspace)

    @app.page("/edit", title="Edit")
    class Edit(ed.Page):
        def render(self) -> None:
            self.data_editor(workspace)

    client = TestClient(app.native)
    table = client.get("/")
    assert table.status_code == 200
    assert "hedron-data-table" in table.text
    editor = client.get("/edit")
    assert editor.status_code == 200
    assert "<hedron-data-editor" in editor.text
    assert "hedron-data-editor-fallback" in editor.text
    assert '"saveEndpoint":"/__edron/data/people/save"' in editor.text.replace("&quot;", '"')

    token = editor.cookies.get("hedron_csrf")
    assert token
    payload = {
        "updates": [{"row_key": "1", "field": "name", "value": "Augusta"}],
        "inserts": [],
        "deletes": [],
        "dataset_version": "1",
    }
    assert client.post(workspace.save_endpoint, json=payload).status_code == 403
    saved = client.post(
        workspace.save_endpoint,
        json=payload,
        headers={"X-CSRF-Token": token},
    )
    assert saved.status_code == 200
    assert saved.json()["ok"] is True
    assert audit[-1].outcome == "accepted"

    malformed = client.post(
        workspace.save_endpoint,
        json={"updates": "not-an-array"},
        headers={"X-CSRF-Token": token},
    )
    assert malformed.status_code == 422


def test_workspace_diagnostics_redact_shape_and_native_feature() -> None:
    workspace, _ = make_workspace()
    facts = workspace.diagnostics()
    assert facts["adapter"] == "memory"
    assert facts["writable"] == ["name"]
    assert "secret" not in facts["projectable"]

    class Person(BaseModel):
        id: str
        name: str
        tenant: str
        secret: str

    feature = workspace.native_feature(model=Person, can_read=lambda: True)
    assert feature.name == "people"
    assert feature.source is workspace.source.native


def test_edit_intent_and_source_contracts_are_bounded() -> None:
    with pytest.raises(ValueError, match="at least one"):
        ed.EditIntent()
    with pytest.raises(ValueError, match="limited"):
        ed.EditIntent(deletes=tuple(str(index) for index in range(501)))
    with pytest.raises(ValueError, match="limited"):
        ed.DataSelection(tuple(str(index) for index in range(501)))
    with pytest.raises(TypeError, match="fetch"):
        ed.DataSource(object())
    parsed = ed.EditIntent.from_mapping(
        {"updates": [{"row_key": "1", "field": "name", "value": "Ada"}]}
    )
    assert parsed.updates == (ed.CellEdit("1", "name", "Ada"),)

    class AwaitableSource:
        async def fetch(self, query: Any) -> Any:
            return None

        async def apply(self, changes: Any) -> Any:
            return None

    with pytest.raises(TypeError, match="async sources"):
        ed.DataSource(AwaitableSource()).fetch(__import__("hedron_data").DataQuery())


def test_dataframe_adapters_use_native_bounded_normalization() -> None:
    pandas = pytest.importorskip("pandas")
    columns = (ed.Column("id", read_only=True), ed.Column("name"))
    source = ed.DataSource.dataframe(
        pandas.DataFrame([{"id": "1", "name": "Ada"}]),
        columns=columns,
        projection_fields=("id", "name"),
    )
    workspace = ed.DataWorkspace("frame_people", source=source, columns=columns)
    assert workspace.page().rows == ({"id": "1", "name": "Ada"},)
    assert workspace.diagnostics()["adapter"] == "pandas"


@pytest.mark.parametrize("adapter", ["polars", "pyarrow"])
def test_columnar_dataframe_adapters(adapter: str) -> None:
    module = pytest.importorskip(adapter)
    frame = (
        module.DataFrame({"id": ["1"], "name": ["Ada"]})
        if adapter == "polars"
        else module.table({"id": ["1"], "name": ["Ada"]})
    )
    columns = (ed.Column("id", read_only=True), ed.Column("name"))
    source = ed.DataSource.dataframe(
        frame,
        columns=columns,
        projection_fields=("id", "name"),
    )
    workspace = ed.DataWorkspace(f"{adapter}_people", source=source, columns=columns)
    assert workspace.page().rows == ({"id": "1", "name": "Ada"},)
    assert workspace.diagnostics()["adapter"] == adapter


def test_sqlalchemy_adapter_keeps_sessions_application_owned() -> None:
    sqlalchemy = pytest.importorskip("sqlalchemy")
    from sqlalchemy.orm import sessionmaker

    metadata = sqlalchemy.MetaData()
    people = sqlalchemy.Table(
        "people",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
        sqlalchemy.Column("name", sqlalchemy.String),
    )
    engine = sqlalchemy.create_engine("sqlite://")
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(people.insert(), [{"id": "1", "name": "Ada"}])
    source = ed.DataSource.sqlalchemy(
        session_factory=sessionmaker(engine),
        statement=sqlalchemy.select(people.c.id, people.c.name),
        to_row=lambda row: dict(row),
        columns=(ed.Column("id", read_only=True), ed.Column("name")),
    )
    workspace = ed.DataWorkspace(
        "sql_people",
        source=source,
        columns=(ed.Column("id", read_only=True), ed.Column("name")),
    )
    assert workspace.page().rows == ({"id": "1", "name": "Ada"},)
    assert workspace.diagnostics()["adapter"] == "sqlalchemy"
