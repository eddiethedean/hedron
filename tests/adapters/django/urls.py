"""Test URLconf for hedron-django adapter tests."""

from __future__ import annotations

from django.http import HttpRequest
from django.urls import path

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderMode
from hedron_django import component_response, hedron_view, interaction_response


@hedron_view
def page_view(request: HttpRequest):
    return component_response(
        Page(Heading("Hello", level=1), title="Test"),
        request=request,
        mode=RenderMode.PAGE,
    )


@hedron_view
def fragment_view(request: HttpRequest):
    return component_response(Text("Fragment body"), request=request, mode=RenderMode.FRAGMENT)


@hedron_view
def interaction_view(request: HttpRequest):
    return interaction_response(
        InteractionResult(
            content=Text("Updated"),
            trigger="refreshed",
            explanation="test",
        ),
        request=request,
    )


urlpatterns = [
    path("", page_view, name="home"),
    path("page/", page_view, name="page"),
    path("fragment/", fragment_view, name="fragment"),
    path("interaction/", interaction_view, name="interaction"),
]
