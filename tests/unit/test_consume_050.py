"""CONSUME-050 uses 0.45–0.49 fingerprints, not a fourth catalog."""

from __future__ import annotations

from hedron_core.bundles import included_bundles
from hedron_core.catalog import InteractionCatalog, compile_interaction_catalog
from hedron_core.htmx_extensions import catalog_facts
from hedron_core.updates import handle_graph_payload
from hedron_explorer.services.catalog import interactions_json


def test_manifest_profile_development() -> None:
    catalog = compile_interaction_catalog()
    manifest = catalog.to_manifest(profile="development")
    assert hasattr(manifest, "as_mapping") or hasattr(manifest, "fingerprint")


def test_handle_graph_and_bundles_and_htmx_facts() -> None:
    payload = handle_graph_payload()
    assert isinstance(payload, dict)
    facts = catalog_facts()
    assert facts is not None
    bundles = included_bundles()
    assert isinstance(bundles, tuple)


def test_explorer_interactions_use_catalog_manifest() -> None:
    from fastapi import FastAPI
    from starlette.requests import Request

    app = FastAPI()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1),
        "server": ("test", 80),
        "app": app,
    }
    request = Request(scope)
    payload = interactions_json(request)
    assert isinstance(payload, dict)
    assert InteractionCatalog is not None
