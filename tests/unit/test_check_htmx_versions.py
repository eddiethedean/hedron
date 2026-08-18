from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_htmx_versions.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_htmx_versions", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_reads_every_authoritative_htmx_pin() -> None:
    module = _load_module()
    pins = (module.read_core_pin(), *module.read_extension_pins())
    assert {(pin.package, pin.version) for pin in pins} == {
        ("htmx.org", "2.0.10"),
        ("htmx-ext-head-support", "2.0.2"),
        ("htmx-ext-preload", "2.1.2"),
        ("htmx-ext-sse", "2.2.4"),
    }


def test_npm_latest_reads_stable_dist_tag() -> None:
    module = _load_module()
    requested = []

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    def open_url(request, *, timeout):
        requested.append((request.full_url, request.headers["Accept"], timeout))
        return Response(
            json.dumps({"dist-tags": {"latest": "2.3.4", "next": "3.0.0-beta.1"}}).encode()
        )

    assert module.npm_latest("htmx-ext-sse", open_url=open_url) == "2.3.4"
    assert requested == [
        (
            "https://registry.npmjs.org/htmx-ext-sse",
            "application/vnd.npm.install-v1+json",
            20,
        )
    ]


def test_outdated_message_names_required_upgrade() -> None:
    module = _load_module()
    pin = module.AssetPin("htmx.org", "2.0.10", module.CORE_PIN_SOURCE)
    outdated, errors = module.check_pins((pin,), latest_for=lambda _package: "2.0.11")
    assert errors == []
    assert outdated == [
        "htmx.org: pinned 2.0.10, latest stable 2.0.11. "
        "Upgrade the pin and vendored asset in scripts/asset_audit.py to 2.0.11."
    ]


def test_current_pin_passes_and_lookup_failure_is_actionable() -> None:
    module = _load_module()
    pin = module.AssetPin("htmx-ext-sse", "2.2.2", module.EXTENSION_PIN_SOURCE)
    assert module.check_pins((pin,), latest_for=lambda _package: "2.2.2") == ([], [])

    def unavailable(_package):
        raise TimeoutError("registry timed out")

    outdated, errors = module.check_pins((pin,), latest_for=unavailable)
    assert outdated == []
    assert errors == ["htmx-ext-sse: could not query npm stable version: registry timed out"]
