"""Portable adapter harness scenarios (phase 0.11)."""

from __future__ import annotations

from fastapi import FastAPI
from flask import Flask

from hedron import Hedron, Page, Heading, Text
from hedron.testing.adapters import (
    assert_fragment_body,
    assert_page_document,
    fastapi_fixture,
    flask_fixture,
)
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask


def _fastapi_app() -> FastAPI:
    app = Hedron(title="harness")

    @app.page("/")
    def home() -> Page:
        return Page(Heading("FastAPI Home", level=1), title="Home")

    @app.component("/fragment")
    def fragment() -> InteractionResult:
        return InteractionResult(content=Text("FastAPI fragment"), explanation="harness")

    return app


def _flask_app() -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui", __name__)

    @ui.page("/")
    def home():
        return Page(Heading("Flask Home", level=1), title="Home")

    @ui.component("/fragment")
    def fragment():
        return InteractionResult(content=Text("Flask fragment"), explanation="harness")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


def test_portable_page_fastapi() -> None:
    fixture = fastapi_fixture(_fastapi_app())
    response = fixture.get("/")
    assert_page_document(response)
    assert "FastAPI Home" in response.body


def test_portable_fragment_fastapi() -> None:
    fixture = fastapi_fixture(_fastapi_app())
    response = fixture.get("/fragment", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="FastAPI fragment")


def test_portable_page_flask() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/")
    assert_page_document(response)
    assert "Flask Home" in response.body


def test_portable_fragment_flask() -> None:
    fixture = flask_fixture(_flask_app())
    response = fixture.get("/fragment", headers={"HX-Request": "true"})
    assert_fragment_body(response, contains="Flask fragment")
