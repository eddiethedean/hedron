"""SCHEMA-049 TypeSchema v2 dual projections and v1 upgrade."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from tests.unit._helpers_049 import make_app, reset_049

from hedron import FormBody, Sensitive, Text, ViewParams
from hedron_core.diagnostics import HedronError
from hedron_core.schema_sanitizer import sanitize_json_schema
from hedron_core.type_schema import (
    TYPE_SCHEMA_VERSION,
    TypeSchema,
    type_schema_from_descriptor,
    upgrade_type_schema,
)
from hedron_core.updates import BaseHandleDescriptor


def setup_function() -> None:
    reset_049()


def test_new_schemas_are_v2_with_projections() -> None:
    app = make_app()

    class Params(BaseModel):
        q: str = ""

    @app.refreshable("/search")
    def search(params: Annotated[Params, ViewParams(source="query")]):
        return Text(params.q)

    schema = search.schema
    assert isinstance(schema, TypeSchema)
    assert schema.schema_version == TYPE_SCHEMA_VERSION == 2
    assert "defaults" not in schema.as_mapping()
    assert "examples" not in schema.input_projection
    loaded = type_schema_from_descriptor(search.descriptor)
    assert loaded is not None
    assert loaded.schema_version == 2


def test_v1_artifacts_still_load_and_upgrade() -> None:
    descriptor = BaseHandleDescriptor(logical_id="legacy")
    v1 = TypeSchema(schema_version=1, handler_kind="view")
    attached = descriptor
    from hedron_core.type_schema import attach_type_schema

    attached = attach_type_schema(descriptor, v1)
    loaded = type_schema_from_descriptor(attached)
    assert loaded is not None
    assert loaded.schema_version == 1
    upgraded = upgrade_type_schema(loaded)
    assert upgraded.schema_version == 2
    assert "values" not in upgraded.as_mapping()


def test_sanitizer_strips_secrets_and_callables() -> None:
    clean = sanitize_json_schema(
        {
            "type": "object",
            "examples": ["x"],
            "default": 1,
            "properties": {
                "name": {"type": "string", "example": "private"},
                "count": {"type": "integer", "minimum": 0},
            },
        }
    )
    assert "examples" not in clean
    assert "default" not in clean
    assert clean["properties"] == {
        "name": {"type": "string"},
        "count": {"type": "integer", "minimum": 0},
    }
    try:
        sanitize_json_schema({"type": (lambda: None)})
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0003"
    else:
        raise AssertionError("callable schema must fail closed")


def test_sanitizer_fail_closes_unknown_keys_and_homoglyphs() -> None:
    class Extra(BaseModel):
        model_config = {"json_schema_extra": {"secret": "p@ss", "examples": ["x"]}}
        v: str = "a"

    try:
        sanitize_json_schema(Extra.model_json_schema())
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0003"
    else:
        raise AssertionError("json_schema_extra secrets must fail closed")

    homoglyph = sanitize_json_schema({"type": "object", "ｄefault": "secret", "default": 1})
    assert "default" not in homoglyph
    assert "ｄefault" not in homoglyph
    try:
        sanitize_json_schema({"type": "object", "mystery": True})
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0003"
    else:
        raise AssertionError("unknown keywords must fail closed")


def test_sensitive_stays_write_only() -> None:
    app = make_app()

    class Payload(BaseModel):
        token: Annotated[str, Sensitive()]
        name: str = "ok"

    @app.command(fallback="/")
    def save(data: Annotated[Payload, FormBody()]):
        return Text(data.name)

    schema = save.schema
    assert schema is not None
    assert "token" in schema.write_only_fields or "token" in schema.sensitivity_flags
