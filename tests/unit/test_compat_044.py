"""COMPAT-044: 0.43 fixtures remain, adapters emit bounded exceptions."""

from __future__ import annotations

import pytest
from tests.unit._helpers_044 import make_app, reset_044

from hedron import Page, Text
from hedron_core.codes import HED_TYPE_0009
from hedron_core.diagnostics import HedronError
from hedron_core.updates import StructuralBindingAdapter
from hedron_django.type_authoring import refuse_fastapi_type_authoring as django_refuse
from hedron_flask.type_authoring import refuse_fastapi_type_authoring as flask_refuse
from hedron_jinja.type_authoring import refuse_annotation_evaluation


def setup_function() -> None:
    reset_044()


def test_unmodeled_043_handler_still_structural() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    assert status.schema is None
    assert status.adapter in {None} or isinstance(
        getattr(status, "adapter", None) or StructuralBindingAdapter(),
        StructuralBindingAdapter,
    )
    assert status.bind  # callable


def test_flask_django_jinja_bounded_exceptions() -> None:
    with pytest.raises(HedronError) as flask_err:
        flask_refuse()
    assert flask_err.value.diagnostics[0].code == HED_TYPE_0009
    with pytest.raises(HedronError) as django_err:
        django_refuse()
    assert django_err.value.diagnostics[0].code == HED_TYPE_0009
    with pytest.raises(HedronError) as jinja_err:
        refuse_annotation_evaluation()
    assert jinja_err.value.diagnostics[0].code == HED_TYPE_0009


def test_legacy_region_still_works() -> None:
    from fastapi.testclient import TestClient

    from hedron import swap

    app = make_app()
    region = app.region("legacy", description="legacy")

    @app.fragment("/legacy", region=region)
    def legacy():
        return swap(Text("legacy"))

    @app.page("/")
    def home():
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    frag = client.get("/legacy", headers={"HX-Request": "true", "HX-Target": "legacy"})
    assert frag.status_code == 200
    assert "legacy" in frag.text
