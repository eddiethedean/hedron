"""DataEditor save works with Hedron double-submit CSRF and no csrf-token meta (#216)."""

from __future__ import annotations

from fastapi import Request
from fastapi.testclient import TestClient

from hedron import Hedron, Page, Text
from hedron.security.csrf import prepare_csrf_from_request, validate_csrf
from hedron.security.policy import SecurityPolicy
from hedron_data import (
    CellUpdate,
    Column,
    DataChanges,
    DataEditor,
    DataSaveResult,
    InMemoryDataSource,
)


def test_dataeditor_json_save_accepts_csrf_header_from_cookie_without_meta() -> None:
    """PAGE seeds hedron_csrf; editor must send it as X-CSRF-Token (no private meta)."""
    rows = [{"id": "1", "name": "Ada"}]
    source = InMemoryDataSource(rows, key_field="id")
    saves: list[DataChanges] = []

    def on_save(changes: DataChanges) -> DataSaveResult:
        saves.append(changes)
        return DataSaveResult(ok=True, accepted=changes, version="2")

    editor = DataEditor(
        source=source,
        columns=[
            Column(name="id", read_only=True),
            Column(name="name", writable=True),
        ],
        key_field="id",
        save_endpoint="/editor/save",
        on_save=on_save,
    )

    app = Hedron(title="editor-csrf", security="standard", explorer="off", session_secret="test")

    @app.page("/")
    def home() -> Page:
        # Intentionally no meta[name=csrf-token] — cookie-only path (#216).
        return Page(Text("editor"), editor, title="Editor")

    @app.post("/editor/save")
    async def save(request: Request) -> dict[str, object]:
        # Same CSRF path apps use for DataEditor JSON saves (reference-app pattern).
        policy = getattr(request.app.state, "hedron_security", SecurityPolicy.from_name("standard"))
        await prepare_csrf_from_request(request, policy)
        validate_csrf(request, policy)
        payload = await request.json()
        updates = tuple(
            CellUpdate(
                row_key=str(item["row_key"]),
                field=str(item["field"]),
                value=item.get("value"),
                row_version=(
                    str(item["row_version"]) if item.get("row_version") is not None else None
                ),
            )
            for item in payload.get("updates") or []
        )
        result = editor.apply_changes(DataChanges(updates=updates))
        return {"ok": result.ok, "version": result.version, "errors": []}

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert 'name="csrf-token"' not in page.text
    token = page.cookies.get("hedron_csrf")
    assert token

    denied = client.post(
        "/editor/save",
        json={
            "updates": [{"row_key": "1", "field": "name", "value": "Ada Lovelace"}],
            "inserts": [],
            "deletes": [],
            "dataset_version": "1",
        },
    )
    assert denied.status_code == 403

    # Mirror editor.js: cookie sent via credentials; header from readCsrfToken(cookie).
    ok = client.post(
        "/editor/save",
        json={
            "updates": [{"row_key": "1", "field": "name", "value": "Ada Lovelace"}],
            "inserts": [],
            "deletes": [],
            "dataset_version": "1",
        },
        headers={"X-CSRF-Token": token},
    )
    assert ok.status_code == 200
    body = ok.json()
    assert body["ok"] is True
    assert saves
    assert saves[0].updates[0].value == "Ada Lovelace"
