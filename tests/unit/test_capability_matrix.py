"""Capability matrix unit tests for phase 0.7A."""

from __future__ import annotations

from hedron_core.adapter import CapabilityClass, capability_matrix
from hedron_core.htmx_contract import htmx_context_from_headers
from hedron_core.interaction import InteractionResult, interaction_headers


def test_capability_matrix_labels_portable_and_host() -> None:
    matrix = capability_matrix()
    adapters = {row.adapter: row for row in matrix}
    assert set(adapters) == {"fastapi", "flask", "django"}
    for row in matrix:
        assert row.stability == "supported"
        classes = {c.classification for c in row.capabilities}
        assert CapabilityClass.PORTABLE in classes
    django = adapters["django"]
    forms = next(c for c in django.capabilities if c.name == "django_forms")
    assert forms.supported is True
    qs = next(c for c in django.capabilities if c.name == "queryset_datasource")
    assert qs.supported is True
    flask = adapters["flask"]
    assert any(c.name == "blueprint_init_app" and c.supported for c in flask.capabilities)


def test_portable_interaction_headers_no_framework_types() -> None:
    result = InteractionResult(redirect="/ok", cache="no-store")
    headers = interaction_headers(result)
    assert headers["HX-Redirect"] == "/ok"
    assert headers["Cache-Control"] == "private, no-store"


def test_htmx_context_from_headers() -> None:
    ctx = htmx_context_from_headers({"HX-Request": "true", "HX-Target": "#main"})
    assert ctx.is_htmx is True
    assert ctx.target == "#main"
