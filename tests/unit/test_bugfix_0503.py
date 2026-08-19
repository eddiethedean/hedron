"""0.50.3 patch: confirmed code defects."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from tests.unit._helpers_050 import csrf_headers, make_app, reset_050

from hedron import Page, Text
from hedron.cli.discovery import _release_pin_bounds, _scaffold_dep
from hedron.content import process_image
from hedron_charts.optional_adapters import ThreeJsAdapter
from hedron_core.css.compiler import compile_css
from hedron_core.diagnostics import HedronError
from hedron_core.htmx.policy import FragmentRegion
from hedron_core.htmx_contract import approved_headers
from hedron_core.inference_workflow import InferenceWorkflow, WorkflowError
from hedron_core.patches import PatchError, PatchOp, PropertyPatch, apply_property_patch
from hedron_core.security import Secret, redact_secret_like
from hedron_core.updates import (
    PortableTarget,
    RefreshIntent,
    compile_to_interaction,
)
from hedron_data.collab import merge_changes
from hedron_data.memory import InMemoryDataSource
from hedron_data.normalize import normalize_rows
from hedron_data.sources import CellUpdate, ColumnSchema, DataChanges, DataQuery
from hedron_data.spreadsheet import excel_col_index
from hedron_data.sqlalchemy_source import SQLAlchemyDataSource, _fetch_rows
from hedron_elements.transfer import DraftTransferEnvelope


def setup_function() -> None:
    reset_050()


def test_command_rejects_undeclared_htmx_target() -> None:
    app = make_app()

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.command(fallback="/")
    def ping() -> Text:
        return Text("pong")

    with TestClient(app) as client:
        headers = csrf_headers(client)
        headers["HX-Target"] = "#hedron-auth"
        response = client.post(ping.path, headers=headers)
    assert response.status_code == 403


def test_command_accepts_extra_declared_fragment_region() -> None:
    app = make_app()
    table = FragmentRegion(id="user-table", selector="#user-table")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.command(fallback="/", fragment_regions=(table,))
    def create() -> Text:
        return Text("ok")

    with TestClient(app) as client:
        headers = csrf_headers(client)
        headers["HX-Target"] = "#user-table"
        response = client.post(create.path, headers=headers)
    assert response.status_code == 200


def test_command_accepts_owned_host_target() -> None:
    app = make_app()

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.command(fallback="/")
    def ping() -> Text:
        return Text("pong")

    with TestClient(app) as client:
        headers = csrf_headers(client)
        headers["HX-Target"] = f"#{ping.logical_id}"
        response = client.post(ping.path, headers=headers)
    assert response.status_code == 200


def test_command_allows_htmx_without_target_header() -> None:
    app = make_app()

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.command(fallback="/")
    def ping() -> Text:
        return Text("pong")

    with TestClient(app) as client:
        response = client.post(ping.path, headers=csrf_headers(client))
    assert response.status_code == 200


def test_compiled_refresh_does_not_opt_out_of_target_auth() -> None:
    target = PortableTarget(
        logical_id="status",
        dom_id="h-view-status",
        path="/status",
        app_id="app-a",
        region=FragmentRegion(id="h-view-status", selector="#h-view-status"),
    )
    compiled = compile_to_interaction(RefreshIntent(targets=(target,)), expected_app_id="app-a")
    assert compiled.policy is not None
    assert compiled.policy.allow_undeclared_targets is False
    assert compiled.policy.declared_regions
    assert compiled.policy.declared_regions[0].id == "h-view-status"


def test_normalize_rows_does_not_reveal_secrets() -> None:
    rows = normalize_rows([{"id": "1", "token": Secret("hunter2")}])
    assert rows[0]["token"] == "***"


def test_scaffold_uses_uploaded_train_pin() -> None:
    _release_pin_bounds.cache_clear()
    floor, ceiling = _release_pin_bounds()
    assert floor == "0.51.0"
    assert ceiling == "0.52"
    assert _scaffold_dep("hedron") == "hedron>=0.51.0,<0.52"
    _release_pin_bounds.cache_clear()


def test_redact_secret_like_tokenizes_keys() -> None:
    cleaned = redact_secret_like(
        {"secretary": "bob", "api-key": "k", "session_id": "s", "passwd": "p"}
    )
    assert cleaned["secretary"] == "bob"
    assert cleaned["api-key"] == "[redacted]"
    assert cleaned["session_id"] == "[redacted]"
    assert cleaned["passwd"] == "[redacted]"


def test_inmemory_secret_column_is_not_writable() -> None:
    src = InMemoryDataSource(
        [{"id": "1", "secret": "x"}],
        writable_fields=frozenset({"secret"}),
        schema=(ColumnSchema(name="secret", label="Secret", secret=True),),
    )
    result = src.apply(DataChanges(updates=(CellUpdate(row_key="1", field="secret", value="y"),)))
    assert result.ok is False
    assert src.fetch(DataQuery()).rows[0]["secret"] == "x"


def test_inmemory_filters_deny_by_default() -> None:
    src = InMemoryDataSource([{"id": "1", "name": "Ada"}])
    with pytest.raises(ValueError, match="not allowlisted"):
        src.fetch(DataQuery(filters={"name": "Ada"}))


def test_threejs_requires_size_when_bytes_omitted() -> None:
    from hedron_core.visualization import ChartAccessibility

    acc = ChartAccessibility(title="t", description="d")
    with pytest.raises(ValueError, match="size"):
        ThreeJsAdapter().compile({"model_url": "missing.glb"}, accessibility=acc)


def test_sqlalchemy_keys_typeerror_does_not_use_scalars() -> None:
    class Result:
        def keys(self) -> list[str]:
            raise TypeError("no keys")

        def scalars(self) -> object:
            raise AssertionError("scalars() must not run when keys() fails")

        def mappings(self) -> object:
            return SimpleNamespace(all=lambda: [{"id": 1, "name": "a"}])

    rows = _fetch_rows(Result())
    assert rows == [{"id": 1, "name": "a"}]


def test_sqlalchemy_search_requires_search_fields() -> None:
    from sqlalchemy import Column, Integer, String, create_engine, select
    from sqlalchemy.orm import Session, declarative_base

    Base = declarative_base()

    class Item(Base):
        __tablename__ = "bugfix_0503_items"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    def factory() -> Session:
        return Session(engine)

    src = SQLAlchemyDataSource(
        session_factory=factory,
        statement=select(Item),
        to_row=lambda r: {"id": r.id, "name": r.name},
    )
    with pytest.raises(HedronError, match="HED-DATA-0012"):
        src.fetch(
            DataQuery(
                search="a",
                allowlisted_filter_fields=frozenset({"name"}),
            )
        )


def test_draft_transfer_rejects_compound_secret_names() -> None:
    with pytest.raises(ValueError, match="forbidden draft field"):
        DraftTransferEnvelope.create(
            app="a",
            route_family="r",
            element_contract="c",
            schema_version="1",
            subject="s",
            fields={"password_hash": "x"},
            operation_id="op1",
            now=100,
        )


def test_workflow_migrate_schema_rejects_label_rewrite() -> None:
    wf = InferenceWorkflow(workflow_id="w1", schema_version="2")
    with pytest.raises(WorkflowError, match="Unsupported schema migration from"):
        wf.migrate_schema("1")
    wf_ok = InferenceWorkflow(workflow_id="w2", schema_version="1")
    wf_ok.migrate_schema("1")
    assert wf_ok.schema_version == "1"


def test_patch_increment_rejects_bool() -> None:
    with pytest.raises(PatchError, match="numeric"):
        apply_property_patch(
            {"t": {"flag": True}},
            PropertyPatch(target_id="t", path="flag", op=PatchOp.INCREMENT),
        )


def test_patch_remove_and_delete_fail_closed_when_missing() -> None:
    with pytest.raises(PatchError, match="not present"):
        apply_property_patch(
            {"t": {"items": ["a"]}},
            PropertyPatch(target_id="t", path="items", op=PatchOp.REMOVE, value="missing"),
        )
    with pytest.raises(PatchError, match="not present"):
        apply_property_patch(
            {"t": {"name": "Ada"}},
            PropertyPatch(target_id="t", path="missing", op=PatchOp.DELETE),
        )


def test_hx_location_values_reject_nested_and_remote() -> None:
    with pytest.raises(ValueError, match="scalars"):
        approved_headers(location={"path": "/next", "values": {"nested": {"a": 1}}})
    with pytest.raises(ValueError, match="local path"):
        approved_headers(location={"path": "/next", "values": {"next": "https://evil.example/"}})


def test_excel_col_index_rejects_empty() -> None:
    with pytest.raises(ValueError, match="Invalid column letters"):
        excel_col_index("")


def test_css_content_brace_is_not_unbalanced() -> None:
    result = compile_css('.x { content: "{"; color: red; }', component_id="app:x")
    assert "content" in result.css


def test_process_image_keeps_minimum_height(tmp_path: Path) -> None:
    from PIL import Image

    path = tmp_path / "wide.png"
    Image.new("RGB", (400, 1), color=(1, 2, 3)).save(path)
    payload = process_image(path, max_width=10, root=tmp_path)
    assert payload


def test_merge_changes_conflicts_insert_vs_delete() -> None:
    local = DataChanges(inserts=({"id": "1", "name": "a"},))
    remote = DataChanges(deletes=("1",))
    result = merge_changes("1", local, remote)
    assert result.ok is False
    assert result.conflicts
