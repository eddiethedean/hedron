"""ECOSYSTEM-050 Flask/Django stay off; one public third-party provider."""

from __future__ import annotations

import inspect

from tests.unit._helpers_050 import reset_050

from hedron_core.plugins import ExplorerProvider, get_explorer_providers, register_explorer_provider
from hedron_django import apps as django_apps
from hedron_flask import blueprint as flask_blueprint


def setup_function() -> None:
    reset_050()


def test_flask_django_explorer_mode_off() -> None:
    assert 'explorer_mode="off"' in inspect.getsource(flask_blueprint)
    assert 'explorer_mode="off"' in inspect.getsource(django_apps)


def test_third_party_provider_without_private_imports() -> None:
    register_explorer_provider(
        ExplorerProvider(panel_id="community-panel", title="Community", plugin="community")
    )
    assert get_explorer_providers()[0].plugin == "community"
    import hedron_core.plugins.explorer as explorer_mod

    source = inspect.getsource(explorer_mod)
    assert "from fastapi" not in source
    assert "import fastapi" not in source
