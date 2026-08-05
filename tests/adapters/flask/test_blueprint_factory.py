"""Flask Blueprint / application-factory tests (phase 0.11)."""

from __future__ import annotations

from flask import Flask

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_flask import HedronBlueprint, HedronFlask


def create_factory_app() -> Flask:
    hedron = HedronFlask()
    ui = HedronBlueprint("ui", __name__)

    @ui.page("/")
    def home():
        return Page(Heading("Factory Home", level=1), title="Factory")

    @ui.component("/fragment")
    def fragment():
        return InteractionResult(content=Text("Blueprint fragment"), explanation="bp")

    @ui.action("/do", methods=["POST"])
    def do_action():
        return InteractionResult(content=Text("Done"), explanation="action")

    app = Flask(__name__)
    app.secret_key = "test"
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app


def test_init_app_stores_extension() -> None:
    app = create_factory_app()
    assert "hedron" in app.extensions
    assert isinstance(app.extensions["hedron"], HedronFlask)


def test_blueprint_page_renders() -> None:
    client = create_factory_app().test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Factory Home" in response.get_data(as_text=True)
    assert "<html" in response.get_data(as_text=True)


def test_blueprint_component_fragment() -> None:
    client = create_factory_app().test_client()
    response = client.get("/fragment", headers={"HX-Request": "true"})
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Blueprint fragment" in body


def test_constructor_compat_still_works() -> None:
    hedron = HedronFlask(__name__)
    assert hedron.flask is not None
    assert hedron.flask.extensions["hedron"] is hedron


def test_csrf_cookie_seeded_on_get() -> None:
    client = create_factory_app().test_client()
    response = client.get("/")
    assert "hedron_csrf" in response.headers.get("Set-Cookie", "")
