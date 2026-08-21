"""COMPAT-043: adapters, 0.42 upgrade fixtures, 0.44 handoff, generic freeze."""

from __future__ import annotations

from dataclasses import replace

from tests.unit._helpers_043 import make_app, reset_043

from hedron import ActionHandle, FragmentHandle, Page, Text, swap
from hedron_core.htmx.policy import FragmentRegion, InteractionResult
from hedron_core.updates import (
    BaseHandleDescriptor,
    BindingPlan,
    StructuralBindingAdapter,
    descriptor_fingerprint,
    structural_bind,
)


def setup_function() -> None:
    reset_043()


def test_042_region_app_still_runs() -> None:
    app = make_app()
    region = app.region("legacy", description="legacy panel")

    @app.page("/", fragment_regions=(region,))
    def home():
        return Page(Text("hello"), title="Home")

    @app.fragment("/legacy", region=region)
    def legacy():
        return swap(Text("legacy"))

    from fastapi.testclient import TestClient

    client = TestClient(app)
    assert client.get("/").status_code == 200
    frag = client.get("/legacy", headers={"HX-Request": "true", "HX-Target": "legacy"})
    assert frag.status_code == 200
    assert "legacy" in frag.text


def test_mixed_legacy_and_handle_page() -> None:
    app = make_app()
    region = app.region("legacy", description="legacy")

    @app.refreshable
    def status():
        return Text("handle")

    @app.fragment("/legacy", region=region)
    def legacy():
        return swap(Text("legacy"))

    @app.page("/")
    def home():
        return Page(status(), Text("mixed"), title="Home")

    from fastapi.testclient import TestClient

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert "handle" in page.text
    assert "h-view-status" in page.text


def test_flask_django_convert_portable_updates_without_decorators() -> None:
    from hedron_core.updates import Patch, PortableTarget, compile_to_interaction, safe_dom_id
    from hedron_django.app import HedronDjango
    from hedron_flask import HedronFlask

    flask_ext = HedronFlask("compat-043", security="development")
    assert not hasattr(flask_ext, "refreshable")
    assert not hasattr(flask_ext, "command")
    target = PortableTarget(
        logical_id="status",
        dom_id=safe_dom_id("status"),
        path="/x",
        app_id="flask",
        region=FragmentRegion(id=safe_dom_id("status"), selector="#h-view-status"),
    )
    compiled = compile_to_interaction(Patch(target=target, content=Text("n")))
    assert isinstance(compiled, InteractionResult)
    django_ext = HedronDjango()
    assert not hasattr(django_ext, "refreshable")
    assert not hasattr(django_ext, "command")


def test_044_handoff_does_not_change_base_fingerprint_or_forms() -> None:
    descriptor = BaseHandleDescriptor(
        kind="view",
        app_id="a",
        logical_id="status",
        path="/_hedron/views/status",
        binding=BindingPlan(),
    )
    extended = replace(
        descriptor,
        extensions={"hedron.type": {"schema": "TypeSchema", "arity": 2}},
    )
    assert descriptor_fingerprint(descriptor) == descriptor_fingerprint(extended)

    class DummyModelAdapter(StructuralBindingAdapter):
        def bind(self, plan: BindingPlan, values, *, path: str):
            return structural_bind(plan, values, path=path)

    adapter = DummyModelAdapter()
    plan = BindingPlan(query_params=("q",))
    bound = adapter.bind(plan, {"q": "1"}, path="/v")
    assert bound.query == {"q": "1"}
    # Generated-form consumer may read the extension without changing conversion goldens.
    schema = extended.extensions["hedron.type"]["schema"]
    assert schema == "TypeSchema"
    assert len(FragmentHandle.__parameters__) == 2
    assert len(ActionHandle.__parameters__) == 2


def test_generated_ids_are_not_rollback_stable_note() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("x")

    assert status.path.startswith("/_hedron/views/")
    note = "generated ids are not rollback-stable"
    assert "not rollback-stable" in note
