"""Test URLconf for hedron-django adapter tests."""

from __future__ import annotations

from django.http import HttpRequest
from django.urls import path
from django.views.decorators.http import require_http_methods

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_django import hedron_static_urlpatterns, hedron_view
from hedron_django.csrf import extract_csrf_from_post


@hedron_view
def page_view(request: HttpRequest):
    # Return a component (not a pre-built HttpResponse) so hedron_view seeds CSRF.
    return Page(Heading("Hello", level=1), title="Test")


@hedron_view
def fragment_view(request: HttpRequest):
    return Text("Fragment body")


@hedron_view
def interaction_view(request: HttpRequest):
    return InteractionResult(
        content=Text("Updated"),
        trigger="refreshed",
        explanation="test",
    )


@require_http_methods(["GET", "POST"])
@hedron_view
def action_view(request: HttpRequest):
    if request.method == "POST":
        # Middleware already validated CSRF; portable extract is for app-level checks.
        _ = extract_csrf_from_post(request)
        return InteractionResult(content=Text("saved"), explanation="action")
    return Page(Text("action-form"), title="Action")


urlpatterns = [
    *hedron_static_urlpatterns(),
    path("", page_view, name="home"),
    path("page/", page_view, name="page"),
    path("fragment/", fragment_view, name="fragment"),
    path("interaction/", interaction_view, name="interaction"),
    path("action/", action_view, name="action"),
]
