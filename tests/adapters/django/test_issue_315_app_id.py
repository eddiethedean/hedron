"""#315: Django compile_to_interaction must pass expected_app_id."""

from __future__ import annotations

from django.test import RequestFactory

from hedron_core.htmx.policy import FragmentRegion
from hedron_core.updates import PortableTarget, RefreshIntent, safe_dom_id
from hedron_django import HedronDjango


def _target(*, app_id: str) -> PortableTarget:
    logical = "status"
    dom = safe_dom_id(logical)
    return PortableTarget(
        logical_id=logical,
        dom_id=dom,
        path=f"/_hedron/views/{logical}",
        app_id=app_id,
        region=FragmentRegion(id=dom, selector=f"#{dom}"),
        bound=True,
        selector=f"#{dom}",
    )


def test_django_respond_rejects_foreign_app_id(django_client) -> None:
    del django_client
    ext = HedronDjango()
    intent = RefreshIntent(targets=(_target(app_id="foreign"),))
    request = RequestFactory().get("/")
    response = ext.respond(intent, request)
    assert response.status_code == 403
    assert b"HED-UPDATE-0003" in response.content


def test_django_respond_accepts_own_app_id(django_client) -> None:
    del django_client
    ext = HedronDjango()
    intent = RefreshIntent(targets=(_target(app_id=ext.hedron_app_id),))
    request = RequestFactory().get("/")
    response = ext.respond(intent, request)
    assert response.status_code == 200
