"""#385: write-only Sensitive fields must leave output required."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel

from hedron import Sensitive
from hedron_core.schema_sanitizer import projections_from_model


def test_write_only_fields_are_omitted_from_output_required() -> None:
    class SecretModel(BaseModel):
        token: Annotated[str, Sensitive()]
        name: str = "ok"

    _inp, output, _shared, write_only, _ro = projections_from_model(
        SecretModel, sensitive=("token",)
    )
    assert write_only == ("token",)
    assert list(output["properties"]) == ["name"]
    assert "token" not in (output.get("required") or [])
