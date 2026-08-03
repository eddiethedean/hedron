"""Cross-adapter URL reverse corpus."""

from __future__ import annotations

from flask import Flask

from hedron_core.adapter import UrlReverseRequest
from hedron_flask.routing import FlaskUrlReverser


def test_flask_url_reverse() -> None:
    app = Flask("rev")

    @app.route("/items/<item_id>", endpoint="item")
    def item_view(item_id: str) -> str:
        return item_id

    rev = FlaskUrlReverser(app)
    with app.test_request_context("/"):
        url = rev.reverse(
            UrlReverseRequest(name="item", kwargs={"item_id": "1"}, root_path="/app")
        )
    assert "/items/1" in url
    assert url.startswith("/app")


def test_django_url_reverse() -> None:
    import django
    from django.conf import settings
    from django.urls import clear_url_caches, set_urlconf

    from hedron_django.routing import DjangoUrlReverser

    if not settings.configured:
        settings.configure(
            ROOT_URLCONF="tests.adapters.django.urls",
            SECRET_KEY="test",
            ALLOWED_HOSTS=["*"],
            MIDDLEWARE=[],
            INSTALLED_APPS=["django.contrib.contenttypes"],
        )
        django.setup()
    else:
        set_urlconf("tests.adapters.django.urls")
        clear_url_caches()

    rev = DjangoUrlReverser()
    url = rev.reverse(UrlReverseRequest(name="home", root_path="/prefix"))
    assert url.startswith("/prefix")
