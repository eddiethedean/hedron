"""Django forms bridge tests (phase 0.11)."""

from __future__ import annotations

from django import forms
from django.test import RequestFactory

from hedron_core.rendering import render
from hedron_django.forms import csrf_hidden_input, form_to_nodes, validation_interaction


class SampleForm(forms.Form):
    name = forms.CharField(max_length=40, label="Name")
    bio = forms.CharField(widget=forms.Textarea, required=False)
    role = forms.ChoiceField(choices=[("a", "Admin"), ("m", "Member")])
    active = forms.BooleanField(required=False)


def test_form_to_nodes_renders_controls() -> None:
    form = SampleForm(data={"name": "", "role": "x"})
    assert not form.is_valid()
    nodes = form_to_nodes(form, request=None, include_csrf=False)
    html = render(nodes).html
    assert 'name="name"' in html
    assert "bio" in html
    assert "role" in html


def test_validation_interaction() -> None:
    form = SampleForm(data={})
    assert not form.is_valid()
    result = validation_interaction(form)
    html = render(result.content).html
    assert "name" in html.lower() or "error" in html.lower() or "required" in html.lower()


def test_csrf_hidden_with_request() -> None:
    request = RequestFactory().get("/")
    token_html = csrf_hidden_input(request)
    assert "csrfmiddlewaretoken" in token_html.value
