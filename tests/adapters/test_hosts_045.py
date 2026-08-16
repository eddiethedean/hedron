"""HOST-045: Flask/Django portable facts and machine-readable exceptions."""

from __future__ import annotations

import pytest

from hedron import Text
from hedron_core.codes import HED_PROJECTION_0005, HED_TYPE_0009
from hedron_core.diagnostics import HedronError
from hedron_django.catalog import (
    PORTABLE_FACT_KEYS as DJANGO_KEYS,
)
from hedron_django.catalog import (
    project_catalog_facts as django_facts,
)
from hedron_django.catalog import (
    refuse_live_host_authority as django_refuse,
)
from hedron_flask.catalog import PORTABLE_FACT_KEYS as FLASK_KEYS
from hedron_flask.catalog import (
    project_catalog_facts as flask_facts,
)
from hedron_flask.catalog import (
    refuse_live_host_authority as flask_refuse,
)
from tests.unit._helpers_045 import make_app, reset_045


def setup_function() -> None:
    reset_045()


def test_flask_and_django_project_the_same_portable_keys() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    flask_payload = flask_facts(status.logical_id, app_id=app.hedron_app_id)
    django_payload = django_facts(status.logical_id, app_id=app.hedron_app_id)
    assert FLASK_KEYS == DJANGO_KEYS
    for key in FLASK_KEYS:
        assert key in flask_payload
        assert flask_payload[key] == django_payload[key]
    assert flask_payload["disposition"] == "projection_adapter"
    assert flask_payload["host_exceptions"]["fastapi_di"] == "bounded_exception"
    assert flask_payload["kind"] == "view"


def test_flask_refuses_fastapi_type_schema_production() -> None:
    with pytest.raises(HedronError) as caught:
        flask_refuse(field="type_schema_production")
    assert caught.value.diagnostic.code == HED_TYPE_0009


def test_django_refuses_live_csrf_as_host_exception() -> None:
    with pytest.raises(HedronError) as caught:
        django_refuse(field="csrf")
    assert caught.value.diagnostic.code == HED_PROJECTION_0005
    assert caught.value.diagnostic.context["field"] == "csrf"
