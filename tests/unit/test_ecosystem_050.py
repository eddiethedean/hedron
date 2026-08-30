"""ECOSYSTEM-050 Flask/Django stay off; one public third-party provider."""

from __future__ import annotations

import subprocess
import sys

from tests.unit._helpers_050 import reset_050

from hedron_core.plugins import ExplorerProvider, get_explorer_providers, register_explorer_provider


def setup_function() -> None:
    reset_050()


def test_adapters_import_without_loading_explorer() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import hedron_flask.blueprint; import hedron_django.apps; "
                "assert 'hedron_explorer' not in sys.modules"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_third_party_provider_without_private_imports() -> None:
    register_explorer_provider(
        ExplorerProvider(panel_id="community-panel", title="Community", plugin="community")
    )
    assert get_explorer_providers()[0].plugin == "community"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import hedron_core.plugins.explorer; "
                "assert 'fastapi' not in sys.modules"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
