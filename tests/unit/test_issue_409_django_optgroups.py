"""#409: Django forms bridge flattens optgroups."""

from __future__ import annotations

from django import forms

from hedron_core.rendering import render
from hedron_django.forms import form_to_nodes


class GroupedForm(forms.Form):
    tier = forms.ChoiceField(
        choices=[
            ("starter", "Starter"),
            ("Teams", [("pro", "Pro"), ("ent", "Enterprise")]),
        ]
    )


def test_form_to_nodes_flattens_optgroup_choices() -> None:
    html = render(form_to_nodes(GroupedForm(), request=None, include_csrf=False)).html
    assert 'value="pro"' in html
    assert 'value="ent"' in html
    assert "Teams" not in html or "Enterprise" in html
