"""AUTHOR-045: Jinja helpers bind to live handles; manifests are not executable."""

from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel
from tests.unit._helpers_045 import make_app, reset_045

from hedron import FormBody, Text
from hedron_core.diagnostics import HedronError
from hedron_jinja.handles import catalog_command_form, catalog_view, coerce_interaction_target
from hedron_jinja.type_authoring import refuse_annotation_evaluation


def setup_function() -> None:
    reset_045()


def test_view_helper_uses_fragment_bind() -> None:
    app = make_app()

    @app.refreshable("/items/{item_id}")
    def item(item_id: str):
        return Text(item_id)

    bound = catalog_view(item, item_id="n1")
    assert bound.logical_id == item.logical_id
    assert "n1" in bound.path


def test_command_form_uses_action_handle_form() -> None:
    app = make_app()

    class Payload(BaseModel):
        title: str = "hi"

    @app.command(fallback="/")
    def add(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    node = catalog_command_form(add)
    from hedron_core.rendering import render

    html = render(node).html
    assert "<form" in html
    assert add.path in html or add.logical_id in html


def test_manifest_dict_is_not_executable() -> None:
    with pytest.raises(HedronError):
        coerce_interaction_target({"logical_id": "forged", "path": "/x"})


def test_annotation_evaluation_remains_refused() -> None:
    with pytest.raises(HedronError):
        refuse_annotation_evaluation(detail="typing.get_type_hints")
