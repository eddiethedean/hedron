"""SCHEMA-044: TypeSchema extension, bounds, fingerprints."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from tests.unit._helpers_044 import make_app, reset_044

from hedron import Text, ViewParams
from hedron_core.type_schema import (
    TYPE_SCHEMA_NAMESPACE,
    TYPE_SCHEMA_VERSION,
    Sensitive,
    TypeSchema,
)
from hedron_core.updates import descriptor_fingerprint


def setup_function() -> None:
    reset_044()


def test_type_schema_attaches_under_hedron_type() -> None:
    app = make_app()

    class Params(BaseModel):
        item_id: str

    @app.refreshable("/items/{item_id}")
    def item(params: Annotated[Params, ViewParams()]):
        return Text(params.item_id)

    payload = item.descriptor.extensions[TYPE_SCHEMA_NAMESPACE]
    assert payload["schema_version"] == TYPE_SCHEMA_VERSION
    assert payload["handler_kind"] == "view"
    assert "ViewParams" in payload["boundary_sources"]
    assert payload["descriptor_fingerprint"] == descriptor_fingerprint(item.descriptor)
    assert "values" not in payload
    assert "defaults" not in payload
    schema = item.schema
    assert isinstance(schema, TypeSchema)
    assert schema.effect_knowledge in {"dynamic", "declared"}


def test_sensitive_marker_is_redacted_in_schema() -> None:
    from typing import Annotated as A

    from hedron import FormBody, Text

    app = make_app()

    class Payload(BaseModel):
        token: A[str, Sensitive()]
        public_id: str = "ok"

    @app.command(fallback="/")
    def secret_cmd(data: Annotated[Payload, FormBody()]):
        return Text(data.public_id)

    flags = secret_cmd.descriptor.extensions[TYPE_SCHEMA_NAMESPACE]["sensitivity_flags"]
    assert "token" in flags
    dumped = str(secret_cmd.descriptor.extensions[TYPE_SCHEMA_NAMESPACE])
    assert "hunter2" not in dumped
