"""CATALOG-045: sealed InteractionCatalog from 0.43 descriptors and 0.44 TypeSchema."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from typing import Annotated

import pytest
from pydantic import BaseModel
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text, ViewParams
from hedron_core.catalog import (
    CatalogVersionError,
    compile_interaction_catalog,
    register_projection_provider,
    seal_interaction_catalog,
)
from hedron_core.codes import HED_CATALOG_0003, HED_CATALOG_0004
from hedron_core.type_schema import TYPE_SCHEMA_NAMESPACE, payload_fingerprint
from hedron_core.updates import descriptor_fingerprint


def setup_function() -> None:
    reset_045()


def test_unmodeled_entry_omits_type_fields() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    entry = catalog.require(status.logical_id)
    assert entry.kind == "view"
    assert entry.effect_state in {"dynamic", "observed"}
    assert entry.type_schema_version is None
    assert entry.type_schema_fingerprint is None
    assert entry.handler_fingerprint is None
    assert "hedron.type" not in status.descriptor.extensions
    payload = entry.as_mapping()
    assert "type_schema_fingerprint" not in payload
    assert "values" not in payload
    assert payload["descriptor_fingerprint"] == descriptor_fingerprint(status.descriptor)


def test_modeled_entry_indexes_type_schema_fingerprint() -> None:
    app = make_app()

    class Params(BaseModel):
        item_id: str

    @app.refreshable("/items/{item_id}")
    def item(params: Annotated[Params, ViewParams()]):
        return Text(params.item_id)

    catalog = app.interactions
    entry = catalog.require(item.logical_id)
    schema = item.descriptor.extensions[TYPE_SCHEMA_NAMESPACE]
    assert entry.type_schema_version == 1
    assert entry.type_schema_fingerprint == payload_fingerprint(schema)
    assert len(item.schema.stable_fingerprint()) == 32
    assert entry.descriptor_fingerprint == descriptor_fingerprint(item.descriptor)
    assert "values" not in schema
    assert entry.effect_state in {"dynamic", "declared"}
    assert "ViewParams" in entry.boundary_sources


def test_descriptor_fingerprint_excludes_effect_and_extensions() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    raw = descriptor_fingerprint(status.descriptor)
    encoded = json.dumps(
        {
            "v": status.descriptor.version,
            "kind": status.descriptor.kind,
            "app_id": status.descriptor.app_id,
            "logical_id": status.descriptor.logical_id,
            "name": status.descriptor.name,
            "path": status.descriptor.path,
            "method": status.descriptor.method,
            "host_tag": status.descriptor.host_tag,
            "swap": status.descriptor.swap,
            "fallback": status.descriptor.fallback,
            "include_in_schema": status.descriptor.include_in_schema,
            "binding": {
                "path_params": list(status.descriptor.binding.path_params),
                "query_params": list(status.descriptor.binding.query_params),
                "required": list(status.descriptor.binding.required),
            },
            "limits": dict(status.descriptor.limits),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    assert raw == hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:32]
    assert "effect" not in encoded
    assert "extensions" not in encoded


def test_seal_rejects_provider_mutation() -> None:
    make_app()
    seal_interaction_catalog()
    from hedron_core.catalog import SurfaceProjectionProvider

    with pytest.raises(CatalogVersionError) as caught:
        register_projection_provider(
            SurfaceProjectionProvider(
                namespace="example.test",
                provider="tests",
                provider_version="0",
                surface="none",
            )
        )
    assert caught.value.diagnostic.code == HED_CATALOG_0003


def test_require_missing_entry() -> None:
    make_app()
    catalog = compile_interaction_catalog()
    with pytest.raises(CatalogVersionError) as caught:
        catalog.require("missing.handler")
    assert caught.value.diagnostic.code == HED_CATALOG_0004


def test_determinism_across_hash_seeds() -> None:
    app = make_app()

    @app.refreshable
    def a_view():
        return Text("a")

    @app.command(fallback="/")
    def b_cmd():
        return Text("b")

    first = compile_interaction_catalog(app_id=app.hedron_app_id).fingerprint
    os.environ["PYTHONHASHSEED"] = "1"
    second = compile_interaction_catalog(app_id=app.hedron_app_id).fingerprint
    assert first == second
    assert [
        item.logical_id for item in compile_interaction_catalog(app_id=app.hedron_app_id).views()
    ] == [a_view.logical_id]


def test_concurrent_readers() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    errors: list[str] = []

    def reader() -> None:
        for _ in range(40):
            entry = catalog.require(status.logical_id)
            if entry.kind != "view":
                errors.append(entry.kind)

    threads = [threading.Thread(target=reader) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []


def test_lookup_does_not_import_optional_packages(monkeypatch: pytest.MonkeyPatch) -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    import builtins

    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name.startswith(("hedron_charts", "hedron_mcp", "hedron_data")):
            raise AssertionError(f"catalog lookup imported {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    assert catalog.require(status.logical_id).kind == "view"
    _ = catalog.views()
    _ = catalog.fingerprint
